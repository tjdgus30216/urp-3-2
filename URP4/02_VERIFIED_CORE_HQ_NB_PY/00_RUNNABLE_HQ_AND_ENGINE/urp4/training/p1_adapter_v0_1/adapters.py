from __future__ import annotations

import re
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping
from typing import Any

from .models import AdapterContractError, AdapterPlan
from .registry import ADAPTER_CONTRACT_VERSION, ALLOWED_OUTER_FOLDS, DATASET_OBJECT_ID, get_adapter_spec


_FAMILIES = frozenset("BCFLT")
_FORBIDDEN_KEYS = {
    "y",
    "y_values",
    "target",
    "target_values",
    "target_gm",
    "performance_y",
    "labels",
    "label_values",
    "predictions",
    "outer_test_scores",
}


def _reject_target_payload(value: Any, path: str = "request") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = str(key).strip().lower()
            if normalized in _FORBIDDEN_KEYS or normalized.endswith("_target_values") or normalized.endswith("_y_values"):
                raise AdapterContractError(f"target-bearing payload is prohibited at {path}.{key}")
            _reject_target_payload(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_target_payload(child, f"{path}[{index}]")


def _truthy(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def _applicable_families(raw: Any) -> frozenset[str]:
    text = str(raw).upper()
    tokens = set(re.findall(r"(?<![A-Z])([BCFLT])(?![A-Z])", text))
    if "ALL58" in text or "ALL_FAMILY" in text or tokens == _FAMILIES:
        return _FAMILIES
    if "BCL" in text:
        return frozenset("BCL")
    return frozenset(tokens)


def _validate_candidate_rows(rows: Iterable[Mapping[str, Any]]) -> tuple[list[dict[str, Any]], tuple[str, ...], tuple[str, ...]]:
    data = [dict(row) for row in rows]
    if not data:
        raise AdapterContractError("selected candidate rows are empty")
    required = {
        "candidate_id",
        "selection_pool_status",
        "feature_selection_export_eligible",
        "calculation_state",
        "candidate_block_id",
        "pair_integrity_required",
        "missingness_policy",
        "applicable_family_declared",
    }
    for row in data:
        missing = required - set(row)
        if missing:
            raise AdapterContractError(f"candidate row missing fields: {sorted(missing)}")
        if not _truthy(row["feature_selection_export_eligible"]):
            raise AdapterContractError(f"ineligible candidate selected: {row['candidate_id']}")
        if str(row["calculation_state"]) != "calculated":
            raise AdapterContractError(f"uncalculated candidate selected: {row['candidate_id']}")
        if str(row["selection_pool_status"]) not in {"technical_sensitivity", "technical_sensitivity_paired"}:
            raise AdapterContractError(f"nontechnical candidate selected: {row['candidate_id']}")
        policy = str(row["missingness_policy"]).lower()
        if "zero" in policy and "never" not in policy and "no zero" not in policy:
            raise AdapterContractError(f"zero-imputation authorization detected: {row['candidate_id']}")
    ids = [str(row["candidate_id"]) for row in data]
    if len(ids) != len(set(ids)):
        raise AdapterContractError("candidate_id is duplicated")

    pair_members: dict[str, list[str]] = defaultdict(list)
    block_ids: list[str] = []
    for row in data:
        block = str(row["candidate_block_id"]).strip()
        if _truthy(row["pair_integrity_required"]):
            if not block:
                raise AdapterContractError(f"paired candidate lacks block: {row['candidate_id']}")
            pair_members[block].append(str(row["candidate_id"]))
        block_ids.append(block or f"SCALAR::{row['candidate_id']}")
    broken = {block: members for block, members in pair_members.items() if len(members) != 2}
    if broken:
        raise AdapterContractError(f"directional pair selected incompletely: {broken}")
    return data, tuple(ids), tuple(dict.fromkeys(block_ids))


def compile_adapter_plan(request: Mapping[str, Any]) -> AdapterPlan:
    """Validate and compile one no-fit FS4-P1 representative plan.

    The adapter accepts candidate metadata only.  Target arrays, fitting and
    prediction are impossible by contract in this package version.
    """

    payload = dict(request)
    _reject_target_payload(payload)
    if payload.get("dataset_manifest_id") != DATASET_OBJECT_ID:
        raise AdapterContractError("dataset identity does not match the PRM-063 frozen object")
    if _truthy(payload.get("execution_authorized", False)):
        raise AdapterContractError("execution is not authorized by the no-fit adapter contract")

    spec = get_adapter_spec(pilot_recipe_id=str(payload.get("pilot_recipe_id", "")))
    if payload.get("method_family_id") != spec.method_family_id:
        raise AdapterContractError("method family and pilot recipe mismatch")
    if payload.get("representative_recipe") != spec.representative_recipe:
        raise AdapterContractError("representative recipe drift")

    outer_fold_id = str(payload.get("outer_fold_id", ""))
    if outer_fold_id not in ALLOWED_OUTER_FOLDS:
        raise AdapterContractError("outer fold is not one of the five PRM-063 folds")
    inner_fold_ids = tuple(str(item) for item in payload.get("inner_fold_ids", ()))
    expected_inner = tuple(f"{outer_fold_id}-IN-{index}" for index in range(1, 5))
    if inner_fold_ids != expected_inner:
        raise AdapterContractError("inner fold identity/order drift")

    families = tuple(dict.fromkeys(str(item).upper() for item in payload.get("model_families", ())))
    if not families or not set(families).issubset(_FAMILIES):
        raise AdapterContractError("invalid model family scope")

    rows, candidate_ids, block_ids = _validate_candidate_rows(payload.get("selected_candidate_rows", ()))
    if len(candidate_ids) > 12:
        raise AdapterContractError("more than 12 scalar columns selected")
    if len(block_ids) > 6:
        raise AdapterContractError("more than six feature blocks selected")

    common: list[str] = []
    specialist: list[str] = []
    for row in rows:
        candidate_id = str(row["candidate_id"])
        applicable = _applicable_families(row["applicable_family_declared"])
        if set(families).issubset(applicable):
            common.append(candidate_id)
        elif spec.method_family_id == "FS4-METHOD-04" and applicable == frozenset("BCL"):
            specialist.append(candidate_id)
        else:
            raise AdapterContractError(
                f"{candidate_id} is not applicable to {families}; only method 04 may route a BCL-only specialist"
            )
    if not common:
        raise AdapterContractError("every adapter needs at least one common all-requested-family feature")
    if specialist and not set(families).intersection(set("BCL")):
        raise AdapterContractError("BCL specialist has no applicable row in requested family scope")

    branches = ["all_family_common"]
    if specialist:
        branches.append("bcl_structural_specialist")
    fit_count = spec.conservative_fits_per_outer
    if fit_count * 5 > 4000:
        raise AdapterContractError("static estimator-fit ceiling exceeded")

    return AdapterPlan(
        adapter_contract_version=ADAPTER_CONTRACT_VERSION,
        dataset_manifest_id=DATASET_OBJECT_ID,
        pilot_recipe_id=spec.pilot_recipe_id,
        method_family_id=spec.method_family_id,
        representative_recipe=spec.representative_recipe,
        outer_fold_id=outer_fold_id,
        inner_fold_ids=inner_fold_ids,
        model_families=families,
        common_candidate_ids=tuple(common),
        bcl_specialist_candidate_ids=tuple(specialist),
        selected_block_ids=block_ids,
        scalar_column_count=len(candidate_ids),
        feature_block_count=len(block_ids),
        branch_ids=tuple(branches),
        preprocessing_scope="inner_train_fit_only",
        selection_scope="inner_train_or_complete_inner_oof_only_outer_test_sealed",
        missingness_policy=spec.missingness_policy,
        conservative_estimator_fit_count=fit_count,
        execution_authorized=False,
        fit_allowed=False,
        prediction_allowed=False,
        target_values_read=0,
        status="compiled_static_no_fit",
        notes="Compatibility plan only; it does not rank methods, select features, read target values or authorize execution.",
    )


def deny_execution(*_: Any, **__: Any) -> None:
    """Fail closed until a separate live-hash execution authorization exists."""

    raise AdapterContractError("FS4-P1 execution is locked; this package compiles no-fit plans only")
