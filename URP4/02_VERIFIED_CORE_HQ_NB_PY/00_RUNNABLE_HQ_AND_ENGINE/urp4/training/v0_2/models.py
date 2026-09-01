from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


class FS4ContractError(ValueError):
    """Raised when a four-method integration plan violates a frozen guard."""


@dataclass(frozen=True)
class MethodFamilyRole:
    method_family_id: str
    stage_id: str
    role: str
    source_aliases: tuple[str, ...]
    method_candidates: tuple[str, ...]
    applicable_domains: tuple[str, ...]
    feature_scope_policy: tuple[str, ...]
    family_partial_branch: bool
    may_enter_outer_comparison: bool
    may_train_meta_model: bool
    status: str
    notes: str = ""

    def to_row(self) -> dict[str, Any]:
        row = asdict(self)
        for field in (
            "source_aliases",
            "method_candidates",
            "applicable_domains",
            "feature_scope_policy",
        ):
            row[field] = "|".join(row[field])
        return row


@dataclass(frozen=True)
class FS4IntegrationPlan:
    contract_version: str
    candidate_registry_version: str
    candidate_matrix_id: str
    dataset_manifest_id: str
    target_policy_id: str
    base_method_family_ids: tuple[str, ...]
    coordinator_reference_id: str
    outer_split_strategy: str
    inner_split_strategy: str
    grouping_keys: tuple[str, ...]
    feature_selection_scope: str
    method_selection_scope: str
    ensemble_training_scope: str
    max_feature_blocks: int
    max_scalar_columns_after_pair_expansion: int
    runtime_alias: str
    execution_mode: str
    model_fit_allowed: bool
    prediction_allowed: bool
    feature_promotion_allowed: bool
    inverse_design_claim_allowed: bool
    notes: str = ""

    def to_row(self) -> dict[str, Any]:
        row = asdict(self)
        row["base_method_family_ids"] = "|".join(self.base_method_family_ids)
        row["grouping_keys"] = "|".join(self.grouping_keys)
        return row
