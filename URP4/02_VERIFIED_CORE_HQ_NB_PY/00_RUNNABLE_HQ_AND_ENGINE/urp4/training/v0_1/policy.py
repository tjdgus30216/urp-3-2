"""Fail-closed feature routing, grouped evaluation, and OOF ensemble policy."""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from typing import Any, Iterable, Mapping

from .models import FeatureRoute, FoldAssignment, TrainingPlan, TrainingPolicyError
from .registry import feature_registry_by_id, method_registry_by_id


BARE_EXCEL_COLUMN = re.compile(r"^[A-Z]{1,3}$")
KNOWN_FAMILIES = {"B", "C", "L", "F", "T"}
BCL = {"B", "C", "L"}
FT = {"F", "T"}
ALLOWED_SPLITS = {"leave_one_family_out", "group_k_fold", "predefined_grouped", "fixture_only"}
ALLOWED_SELECTION_SCOPE = {"nested_within_outer_fold", "fixed_no_selection", "fixture_only"}


def _stable_id(prefix: str, value: Mapping[str, Any]) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return f"{prefix}::sha256-{hashlib.sha256(encoded).hexdigest()[:12]}"


def validate_semantic_id(value: str, field: str) -> None:
    if not value or BARE_EXCEL_COLUMN.fullmatch(value):
        raise TrainingPolicyError(f"{field} requires a source-scoped semantic ID, not bare Excel column {value!r}")
    if "::" not in value:
        raise TrainingPolicyError(f"{field} must include a source namespace using '::': {value!r}")


def route_features(
    *,
    method_id: str,
    model_families: Iterable[str],
    requested_blocks: Iterable[str],
    routing_mode: str,
) -> tuple[FeatureRoute, ...]:
    methods = method_registry_by_id()
    blocks = feature_registry_by_id()
    if method_id not in methods:
        raise TrainingPolicyError(f"unknown method_id: {method_id}")
    method = methods[method_id]
    families = tuple(sorted({str(value).upper() for value in model_families}))
    unknown = set(families) - KNOWN_FAMILIES
    if not families or unknown:
        raise TrainingPolicyError(f"unknown or empty model families: {sorted(unknown)}")
    requested = tuple(dict.fromkeys(str(value) for value in requested_blocks))
    if not requested:
        raise TrainingPolicyError("at least one feature block is required")
    missing = set(requested) - set(blocks)
    if missing:
        raise TrainingPolicyError(f"unknown feature blocks: {sorted(missing)}")
    if any(not blocks[item].direct_model_use for item in requested):
        raise TrainingPolicyError("metadata/output blocks cannot be direct model features")

    lattice_blocks = {"TRAIN-FEATURE-BASE-LATTICE", "TRAIN-FEATURE-ADDED-LATTICE"}.intersection(requested)
    contains_ft = bool(set(families).intersection(FT))
    contains_bcl = bool(set(families).intersection(BCL))
    if lattice_blocks and contains_ft:
        if routing_mode != "family_aware_partial" or not method.supports_family_partial_branch or not contains_bcl:
            raise TrainingPolicyError(
                "B/C/L-only lattice features cannot be applied or zero-imputed into F/T; use an approved family-aware partial branch"
            )
        bcl_blocks = tuple(requested)
        ft_blocks = tuple(item for item in requested if item not in lattice_blocks)
        if not ft_blocks:
            raise TrainingPolicyError("F/T partial branch has no valid all-family feature block")
        identity = {"method": method_id, "families": families, "blocks": requested, "mode": routing_mode}
        base = _stable_id("FEATURE-ROUTE", identity)
        return (
            FeatureRoute(base + "::BCL", method_id, routing_mode, "BCL", tuple(sorted(set(families).intersection(BCL))), bcl_blocks, (), (), "confirmed_policy", "B/C/L branch may consume lattice-only blocks."),
            FeatureRoute(base + "::FT", method_id, routing_mode, "FT", tuple(sorted(set(families).intersection(FT))), ft_blocks, tuple(sorted(lattice_blocks)), (), "confirmed_policy", "F/T branch excludes lattice-only blocks; no zero imputation."),
        )

    for block_id in requested:
        applicable = set(blocks[block_id].applicable_families)
        if not set(families).issubset(applicable):
            raise TrainingPolicyError(f"{block_id} is not applicable to all requested families")
    identity = {"method": method_id, "families": families, "blocks": requested, "mode": routing_mode}
    division = "BCL" if set(families).issubset(BCL) else "FT" if set(families).issubset(FT) else "ALL"
    return (
        FeatureRoute(_stable_id("FEATURE-ROUTE", identity), method_id, routing_mode, division, families, requested, (), (), "confirmed_policy", "No family-inapplicable feature was imputed."),
    )


def validate_split_contract(split: Mapping[str, Any]) -> dict[str, Any]:
    required = {"strategy", "grouped", "grouping_keys", "outer_cv", "inner_cv", "selection_scope", "random_seed"}
    missing = required - set(split)
    if missing:
        raise TrainingPolicyError(f"split contract missing fields: {sorted(missing)}")
    if split["strategy"] not in ALLOWED_SPLITS:
        raise TrainingPolicyError("random-row or unsupported split strategy is prohibited")
    if split["grouped"] is not True:
        raise TrainingPolicyError("training evaluation must be grouped")
    keys = [str(item) for item in split["grouping_keys"]]
    if "base_geometry_id" not in keys:
        raise TrainingPolicyError("grouping_keys must contain base_geometry_id")
    if split["selection_scope"] not in ALLOWED_SELECTION_SCOPE:
        raise TrainingPolicyError("feature/method selection must be nested within outer folds or fixed before evaluation")
    if not isinstance(split["random_seed"], int) or split["random_seed"] < 0:
        raise TrainingPolicyError("split random_seed must be a nonnegative integer")
    return dict(split)


def plan_outer_folds(rows: Iterable[Mapping[str, Any]], split: Mapping[str, Any]) -> tuple[FoldAssignment, ...]:
    contract = validate_split_contract(split)
    data = [dict(row) for row in rows]
    if not data:
        raise TrainingPolicyError("cannot plan folds for an empty row registry")
    for row in data:
        if not all(str(row.get(key, "")).strip() for key in ("row_id", "base_geometry_id", "family_id")):
            raise TrainingPolicyError("row registry requires row_id, base_geometry_id and family_id")
    if len({row["row_id"] for row in data}) != len(data):
        raise TrainingPolicyError("duplicate row_id in fold registry")
    group_family: dict[str, set[str]] = defaultdict(set)
    for row in data:
        group_family[str(row["base_geometry_id"])].add(str(row["family_id"]))
    if any(len(values) != 1 for values in group_family.values()):
        raise TrainingPolicyError("one base_geometry_id crosses family identities")

    strategy = contract["strategy"]
    assignments: list[FoldAssignment] = []
    if strategy == "leave_one_family_out":
        families = sorted({str(row["family_id"]) for row in data})
        if len(families) < 2:
            raise TrainingPolicyError("leave_one_family_out requires at least two families")
        for family in families:
            fold = f"LOFO::{family}"
            for row in data:
                assignments.append(FoldAssignment(str(row["row_id"]), str(row["base_geometry_id"]), str(row["family_id"]), fold, "test" if str(row["family_id"]) == family else "train"))
    elif strategy in {"group_k_fold", "fixture_only"}:
        groups = sorted(group_family)
        n_splits = min(max(2, int(contract.get("n_splits", 2))), len(groups))
        if len(groups) < 2:
            raise TrainingPolicyError("grouped split requires at least two base geometries")
        group_to_fold = {group: index % n_splits for index, group in enumerate(groups)}
        for fold_index in range(n_splits):
            fold = f"GROUP::{fold_index}"
            for row in data:
                role = "test" if group_to_fold[str(row["base_geometry_id"])] == fold_index else "train"
                assignments.append(FoldAssignment(str(row["row_id"]), str(row["base_geometry_id"]), str(row["family_id"]), fold, role))
    else:
        raise TrainingPolicyError("predefined_grouped requires an external frozen assignment registry")

    by_fold_group: dict[tuple[str, str], set[str]] = defaultdict(set)
    for item in assignments:
        by_fold_group[(item.outer_fold_id, item.base_geometry_id)].add(item.split_role)
    if any(len(roles) != 1 for roles in by_fold_group.values()):
        raise TrainingPolicyError("base geometry leaked across train/test within an outer fold")
    return tuple(assignments)


def validate_selection_records(records: Iterable[Mapping[str, Any]]) -> None:
    rows = [dict(row) for row in records]
    if not rows:
        raise TrainingPolicyError("selection audit records are required")
    for row in rows:
        if row.get("selection_scope") not in {"inner_train_only", "fixed_before_outer_cv"}:
            raise TrainingPolicyError("feature/method selection touched outer-test information")
        if bool(row.get("outer_test_used")):
            raise TrainingPolicyError("outer-test data cannot participate in selection")
        validate_semantic_id(str(row.get("candidate_id", "")), "candidate_id")


def validate_oof_ensemble_inputs(records: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    rows = [dict(row) for row in records]
    if not rows:
        raise TrainingPolicyError("OOF ensemble inputs are empty")
    for row in rows:
        if row.get("prediction_scope") != "outer_oof" or bool(row.get("trained_on_row")):
            raise TrainingPolicyError("ensemble may consume outer-OOF predictions only")
        for field in ("dataset_manifest_id", "target_id", "split_contract_id", "row_id", "outer_fold_id", "method_id"):
            if not str(row.get(field, "")):
                raise TrainingPolicyError(f"ensemble input missing {field}")
    identities = {(row["dataset_manifest_id"], row["target_id"], row["split_contract_id"]) for row in rows}
    if len(identities) != 1:
        raise TrainingPolicyError("ensemble inputs mix dataset, target or split identities")
    coverage: dict[tuple[str, str], set[str]] = defaultdict(set)
    methods = {str(row["method_id"]) for row in rows}
    for row in rows:
        coverage[(str(row["row_id"]), str(row["outer_fold_id"]))].add(str(row["method_id"]))
    if any(value != methods for value in coverage.values()):
        raise TrainingPolicyError("OOF ensemble base-method coverage is incomplete")
    return {"row_fold_count": len(coverage), "method_count": len(methods), "status": "confirmed_oof_contract"}


def build_training_plan(
    *,
    dataset_manifest_id: str,
    dataset_sha256: str,
    target_id: str,
    objective_direction: str,
    performance_domain: str,
    feature_ids: Iterable[str],
    feature_block_ids: Iterable[str],
    method_id: str,
    split_contract: Mapping[str, Any],
    runtime_alias: str = "KMK312",
    execution_mode: str = "static_plan_only",
    notes: str = "",
) -> TrainingPlan:
    if execution_mode != "static_plan_only":
        raise TrainingPolicyError("CINT-08 v0.1 prohibits model fit and prediction execution")
    validate_semantic_id(dataset_manifest_id, "dataset_manifest_id")
    validate_semantic_id(target_id, "target_id")
    features = tuple(dict.fromkeys(str(item) for item in feature_ids))
    if not features:
        raise TrainingPolicyError("feature_ids cannot be empty")
    for feature in features:
        validate_semantic_id(feature, "feature_id")
    if method_id not in method_registry_by_id():
        raise TrainingPolicyError(f"unknown method_id: {method_id}")
    blocks = tuple(dict.fromkeys(str(item) for item in feature_block_ids))
    unknown_blocks = set(blocks) - set(feature_registry_by_id())
    if unknown_blocks:
        raise TrainingPolicyError(f"unknown feature blocks: {sorted(unknown_blocks)}")
    split = validate_split_contract(split_contract)
    if objective_direction not in {"maximize", "minimize"}:
        raise TrainingPolicyError("objective_direction must be maximize or minimize")
    if not re.fullmatch(r"[0-9a-f]{64}", dataset_sha256):
        raise TrainingPolicyError("dataset_sha256 must be a full lowercase SHA-256")
    identity = {
        "dataset_manifest_id": dataset_manifest_id,
        "dataset_sha256": dataset_sha256,
        "target_id": target_id,
        "features": features,
        "method_id": method_id,
        "split": split,
    }
    return TrainingPlan(
        plan_id=_stable_id("TRAINING-PLAN", identity),
        dataset_manifest_id=dataset_manifest_id,
        dataset_sha256=dataset_sha256,
        target_id=target_id,
        objective_direction=objective_direction,
        performance_domain=performance_domain,
        feature_ids=features,
        feature_block_ids=blocks,
        method_id=method_id,
        split_contract=split,
        runtime_alias=runtime_alias,
        execution_mode=execution_mode,
        inverse_design_claim_authorized=False,
        scientific_status="fixture_only_no_fit",
        notes=notes,
    )

