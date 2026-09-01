from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


class ExecLayerContractError(RuntimeError):
    """Raised before computation when an executable-layer guard fails."""


@dataclass(frozen=True)
class ExecutionPermit:
    authorization_contract_id: str
    dataset_manifest_id: str
    adapter_contract_version: str
    executable_layer_version: str
    allowed_method_family_ids: tuple[str, ...]
    allowed_outer_fold_ids: tuple[str, ...]
    max_estimator_fits: int
    execution_authorized: bool
    permit_payload_sha256: str
    source_path: str
    source_file_sha256: str


@dataclass(frozen=True)
class ExecutionGraph:
    executable_layer_version: str
    pilot_recipe_id: str
    method_family_id: str
    representative_recipe: str
    estimator_class: str
    estimator_components: tuple[str, ...]
    preprocessing_components: tuple[str, ...]
    required_fit_metadata: tuple[str, ...]
    prediction_metadata: tuple[str, ...]
    common_feature_indices: tuple[int, ...]
    structural_feature_indices: tuple[int, ...]
    prospective_fits_per_outer: int
    permit_required: bool
    fit_called: int
    prediction_called: int
    status: str
    notes: str = ""

    def to_row(self) -> dict[str, Any]:
        row = asdict(self)
        for key in (
            "estimator_components",
            "preprocessing_components",
            "required_fit_metadata",
            "prediction_metadata",
            "common_feature_indices",
            "structural_feature_indices",
        ):
            row[key] = "|".join(map(str, row[key]))
        return row
