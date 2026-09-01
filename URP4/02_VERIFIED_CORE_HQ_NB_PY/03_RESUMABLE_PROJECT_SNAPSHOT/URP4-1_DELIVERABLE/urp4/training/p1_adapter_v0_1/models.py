from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


class AdapterContractError(ValueError):
    """Raised when an FS4-P1 adapter request violates a frozen guard."""


@dataclass(frozen=True)
class RepresentativeAdapterSpec:
    pilot_recipe_id: str
    method_family_id: str
    representative_recipe: str
    source_aliases: tuple[str, ...]
    source_components: tuple[str, ...]
    compatibility_subset: tuple[str, ...]
    target_transforms: tuple[str, ...]
    inner_selection_rule: str
    family_route_policy: str
    missingness_policy: str
    conservative_fits_per_outer: int
    source_faithfulness: str
    status: str
    notes: str = ""

    def to_row(self) -> dict[str, Any]:
        row = asdict(self)
        for key in (
            "source_aliases",
            "source_components",
            "compatibility_subset",
            "target_transforms",
        ):
            row[key] = "|".join(row[key])
        return row


@dataclass(frozen=True)
class AdapterPlan:
    adapter_contract_version: str
    dataset_manifest_id: str
    pilot_recipe_id: str
    method_family_id: str
    representative_recipe: str
    outer_fold_id: str
    inner_fold_ids: tuple[str, ...]
    model_families: tuple[str, ...]
    common_candidate_ids: tuple[str, ...]
    bcl_specialist_candidate_ids: tuple[str, ...]
    selected_block_ids: tuple[str, ...]
    scalar_column_count: int
    feature_block_count: int
    branch_ids: tuple[str, ...]
    preprocessing_scope: str
    selection_scope: str
    missingness_policy: str
    conservative_estimator_fit_count: int
    execution_authorized: bool
    fit_allowed: bool
    prediction_allowed: bool
    target_values_read: int
    status: str
    notes: str = ""

    def to_row(self) -> dict[str, Any]:
        row = asdict(self)
        for key in (
            "inner_fold_ids",
            "model_families",
            "common_candidate_ids",
            "bcl_specialist_candidate_ids",
            "selected_block_ids",
            "branch_ids",
        ):
            row[key] = "|".join(row[key])
        return row
