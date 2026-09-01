"""Immutable objects for the CINT-08 no-fit training-engine boundary."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


class TrainingPolicyError(ValueError):
    """Raised when a training plan would create ambiguity or leakage."""


@dataclass(frozen=True)
class TrainingSourceSpec:
    alias_id: str
    relative_path: str
    sha256: str
    method_family: str
    source_role: str
    layout_id: str
    priority: str
    specialization_hint: str
    expected_cells: int
    expected_code_cells: int
    expected_markdown_cells: int
    expected_functions: int
    expected_classes: int
    output_columns: tuple[str, ...]
    authority_status: str = "professor_ta_delivery_read_only"
    execution_policy: str = "static_definition_audit_only"
    notes: str = ""

    def to_row(self) -> dict[str, Any]:
        row = asdict(self)
        row["output_columns"] = "|".join(self.output_columns)
        return row


@dataclass(frozen=True)
class MethodPluginSpec:
    method_id: str
    method_family: str
    stage_id: str
    short_meaning: str
    source_aliases: tuple[str, ...]
    candidate_components: tuple[str, ...]
    supported_layouts: tuple[str, ...]
    feature_scope_policy: tuple[str, ...]
    supports_family_partial_branch: bool
    supports_oof_ensemble: bool
    specialization_hint: str
    implementation_status: str
    scientific_status: str
    notes: str

    def to_row(self) -> dict[str, Any]:
        row = asdict(self)
        for key in ("source_aliases", "candidate_components", "supported_layouts", "feature_scope_policy"):
            row[key] = "|".join(row[key])
        return row


@dataclass(frozen=True)
class FeatureBlockSpec:
    block_id: str
    source_alias: str
    excel_range: str
    meaning: str
    applicable_families: tuple[str, ...]
    modeling_role: str
    missingness_policy: str
    direct_model_use: bool
    notes: str = ""

    def to_row(self) -> dict[str, Any]:
        row = asdict(self)
        row["applicable_families"] = "|".join(self.applicable_families)
        return row


@dataclass(frozen=True)
class NotebookAudit:
    alias_id: str
    relative_path: str
    expected_sha256: str
    observed_sha256: str
    size_bytes: int
    total_cells: int
    code_cells: int
    markdown_cells: int
    function_count: int
    class_count: int
    import_roots: tuple[str, ...]
    function_names_sha256: str
    output_columns: tuple[str, ...]
    source_identity_status: str
    structure_status: str
    execution_status: str = "not_executed_static_audit"

    def to_row(self) -> dict[str, Any]:
        row = asdict(self)
        row["import_roots"] = "|".join(self.import_roots)
        row["output_columns"] = "|".join(self.output_columns)
        return row


@dataclass(frozen=True)
class FeatureRoute:
    route_id: str
    method_id: str
    routing_mode: str
    division: str
    model_families: tuple[str, ...]
    included_blocks: tuple[str, ...]
    excluded_blocks: tuple[str, ...]
    imputed_blocks: tuple[str, ...]
    scientific_status: str
    notes: str

    def to_row(self) -> dict[str, Any]:
        row = asdict(self)
        for key in ("model_families", "included_blocks", "excluded_blocks", "imputed_blocks"):
            row[key] = "|".join(row[key])
        return row


@dataclass(frozen=True)
class FoldAssignment:
    row_id: str
    base_geometry_id: str
    family_id: str
    outer_fold_id: str
    split_role: str

    def to_row(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TrainingPlan:
    plan_id: str
    dataset_manifest_id: str
    dataset_sha256: str
    target_id: str
    objective_direction: str
    performance_domain: str
    feature_ids: tuple[str, ...]
    feature_block_ids: tuple[str, ...]
    method_id: str
    split_contract: dict[str, Any]
    runtime_alias: str
    execution_mode: str
    inverse_design_claim_authorized: bool
    scientific_status: str
    notes: str = ""

    def to_row(self) -> dict[str, Any]:
        row = asdict(self)
        row["feature_ids"] = "|".join(self.feature_ids)
        row["feature_block_ids"] = "|".join(self.feature_block_ids)
        return row

