from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Iterable, Mapping

from .models import FS4ContractError, FS4IntegrationPlan
from .registry import BASE_METHOD_FAMILIES, COORDINATOR_REFERENCE


BASE_IDS = tuple(item.method_family_id for item in BASE_METHOD_FAMILIES)


def validate_candidate_interface(rows: Iterable[Mapping[str, Any]]) -> dict[str, int]:
    data = [dict(row) for row in rows]
    if not data:
        raise FS4ContractError("candidate interface is empty")
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
    missing = required - set(data[0])
    if missing:
        raise FS4ContractError(f"candidate interface missing fields: {sorted(missing)}")
    ids = [str(row["candidate_id"]) for row in data]
    if len(ids) != len(set(ids)):
        raise FS4ContractError("candidate_id is not unique")
    blocks: dict[str, list[dict[str, Any]]] = defaultdict(list)
    eligible = 0
    for row in data:
        is_eligible = str(row["feature_selection_export_eligible"]).strip().lower() in {"true", "1"}
        pair_required = str(row["pair_integrity_required"]).strip().lower() in {"true", "1"}
        if is_eligible:
            eligible += 1
            if row["calculation_state"] != "calculated":
                raise FS4ContractError("uncalculated candidate cannot be export eligible")
            if row["selection_pool_status"] not in {"technical_sensitivity", "technical_sensitivity_paired"}:
                raise FS4ContractError("nontechnical candidate cannot be export eligible")
        if "zero-impute" in str(row["missingness_policy"]).lower() and "never" not in str(row["missingness_policy"]).lower():
            raise FS4ContractError("missingness policy appears to authorize zero imputation")
        if pair_required:
            block = str(row["candidate_block_id"]).strip()
            if not block:
                raise FS4ContractError("paired candidate lacks candidate_block_id")
            blocks[block].append(row)
    if any(len(members) != 2 for members in blocks.values()):
        raise FS4ContractError("directional pair block must have exactly two members")
    status_counts = Counter(str(row["selection_pool_status"]) for row in data)
    return {
        "registered": len(data),
        "eligible": eligible,
        "pair_blocks": len(blocks),
        "hold": status_counts.get("hold", 0),
        "rejected": status_counts.get("rejected", 0),
    }


def build_no_fit_plan(
    *,
    candidate_registry_version: str,
    candidate_matrix_id: str,
    dataset_manifest_id: str = "PENDING-DATASET-MANIFEST",
    target_policy_id: str = "YPOL-GM-v0.1",
) -> FS4IntegrationPlan:
    if candidate_registry_version != "XREG-v0.1":
        raise FS4ContractError("FS4 v0.2 requires XREG-v0.1")
    return FS4IntegrationPlan(
        contract_version="FS4-INTEGRATION-v0.2",
        candidate_registry_version=candidate_registry_version,
        candidate_matrix_id=candidate_matrix_id,
        dataset_manifest_id=dataset_manifest_id,
        target_policy_id=target_policy_id,
        base_method_family_ids=BASE_IDS,
        coordinator_reference_id=COORDINATOR_REFERENCE.method_family_id,
        outer_split_strategy="leave_one_family_out_or_predefined_grouped",
        inner_split_strategy="grouped_nested_cv_inside_outer_train_only",
        grouping_keys=("base_geometry_id", "replicate_id", "direction", "vf_sibling_group"),
        feature_selection_scope="inner_train_only",
        method_selection_scope="inner_train_only",
        ensemble_training_scope="inner_oof_only",
        max_feature_blocks=6,
        max_scalar_columns_after_pair_expansion=12,
        runtime_alias="KMK312",
        execution_mode="static_plan_only",
        model_fit_allowed=False,
        prediction_allowed=False,
        feature_promotion_allowed=False,
        inverse_design_claim_allowed=False,
        notes="Methods 1-4 are base competitors; method 5 is coordinator/reference only. A new live-hash authorization is required before any fit.",
    )


def validate_oof_merge_records(records: Iterable[Mapping[str, Any]]) -> dict[str, int]:
    data = [dict(row) for row in records]
    if not data:
        raise FS4ContractError("OOF merge records are empty")
    identities = set()
    coverage: dict[tuple[str, str], set[str]] = defaultdict(set)
    methods = set()
    for row in data:
        if row.get("prediction_scope") != "inner_oof" or bool(row.get("trained_on_row")):
            raise FS4ContractError("meta/merge training may consume inner-OOF predictions only")
        if row.get("outer_test_used"):
            raise FS4ContractError("outer-test data cannot train merge weights")
        for field in ("dataset_manifest_id", "target_policy_id", "outer_fold_id", "row_id", "method_family_id"):
            if not str(row.get(field, "")).strip():
                raise FS4ContractError(f"OOF merge record missing {field}")
        identities.add((row["dataset_manifest_id"], row["target_policy_id"], row["outer_fold_id"]))
        key = (str(row["outer_fold_id"]), str(row["row_id"]))
        method = str(row["method_family_id"])
        coverage[key].add(method)
        methods.add(method)
    if not methods.issubset(set(BASE_IDS)):
        raise FS4ContractError("coordinator or unknown method cannot masquerade as a base method")
    if any(method_set != methods for method_set in coverage.values()):
        raise FS4ContractError("incomplete inner-OOF base-method coverage")
    return {"identity_count": len(identities), "row_fold_count": len(coverage), "method_count": len(methods)}
