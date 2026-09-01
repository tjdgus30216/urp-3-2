"""Single-source controller for the URP4-1 HQ notebook.

Only values represented by :class:`URP4Controller` are user-editable.  This
module derives dependent values, validates route compatibility and freezes a
hash-addressed run contract before any geometry or image work begins.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from urp4.descriptor_service.v0_1.service import RUN139_BACKEND_ID
from urp4.geometry_io.v0_4.imported_winding import ImportedSTLWindingConfig


HQ_VERSION = "URP4-HQ-v0.1"
APPROVED_DESCRIPTOR_PROFILE = "P1000-Z801-DZ0.05-CC8M2-N40"
ROUTE_GENERATED = "GEN-STL-NATIVE-CONTROLLED"
ROUTE_IMPORTED = "IMP-STL-ORIENTED-NONZERO-SCREENING-L28"
ROUTE_STP = "IMP-STP-PERSOLID-REFERENCE"


@dataclass(frozen=True)
class WorkflowControl:
    import_geometry: bool = True
    generate_geometry: bool = False
    extract_descriptors: bool = True
    feature_selection: bool = False
    training: bool = False
    run_batch: bool = False


@dataclass(frozen=True)
class PathControl:
    input_geometry: str = ""
    input_directory: str = ""
    output_root: str = "outputs"
    experiment_name: str = "URP4-HQ"
    target_y: str = ""


@dataclass(frozen=True)
class GeometryControl:
    model_id: str = "MODEL-001"
    source_type: str = "imported_stl"  # generated_stl | imported_stl | original_stp
    geometry_revision: str = "user-input"
    expected_size_mm: float = 40.0
    normalize_imported_stl: bool = True


@dataclass(frozen=True)
class ImportControl:
    prefer_original_stp: bool = True
    allow_imported_stl: bool = True
    reject_topology_risk: bool = False


@dataclass(frozen=True)
class GeneratorControl:
    family: str = "lattice_type_a"  # lattice_type_a | lattice_type_b | tpms | voxel
    random_seed: int = 42
    target_vf: float = 0.30
    requested_format: str = "stl"


@dataclass(frozen=True)
class LatticeControl:
    total_length_mm: float = 40.0
    cell_definition_mode: str = "cells_per_axis"  # cells_per_axis | cell_size_mm
    cells_per_axis: int | None = 5
    cell_size_mm: float | None = None


@dataclass(frozen=True)
class TPMSControl:
    registry_index: int = 0
    grid_n: int = 40


@dataclass(frozen=True)
class VoxelControl:
    registry_index: int = 0
    grid_n: int = 40
    rows_per_mode: int = 1


@dataclass(frozen=True)
class SliceControl:
    axis: str = "z"
    physical_size_mm: float = 40.0
    definition_mode: str = "derive_count_from_spacing"
    slice_count: int | None = None
    slice_spacing_mm: float | None = 0.05
    pixel_resolution: int = 1000
    connectivity: int = 8
    min_component_pixels: int = 2
    threshold_rule: str = "binary_nonzero_png_readback"


@dataclass(frozen=True)
class DescriptorControl:
    point_enabled: bool = False
    surface_enabled: bool = False
    slice_enabled: bool = True
    lattice_enabled: bool = False
    candidate_enabled: bool = False


@dataclass(frozen=True)
class ArtifactControl:
    image_policy: str = "STREAMING_TEMP_PNG"  # STREAMING_TEMP_PNG | KEEP_ALL | KEEP_FLAGGED
    overwrite: bool = False
    export_component_tables: bool = True
    visual_review_export: bool = False


@dataclass(frozen=True)
class TrainingControl:
    method_ids: tuple[str, ...] = (
        "TRAIN-METHOD-01",
        "TRAIN-METHOD-02",
        "TRAIN-METHOD-03",
        "TRAIN-METHOD-04",
        "TRAIN-METHOD-05",
    )
    grouped_split_required: bool = True


@dataclass(frozen=True)
class URP4Controller:
    workflow: WorkflowControl = field(default_factory=WorkflowControl)
    paths: PathControl = field(default_factory=PathControl)
    geometry: GeometryControl = field(default_factory=GeometryControl)
    import_control: ImportControl = field(default_factory=ImportControl)
    generator: GeneratorControl = field(default_factory=GeneratorControl)
    lattice: LatticeControl = field(default_factory=LatticeControl)
    tpms: TPMSControl = field(default_factory=TPMSControl)
    voxel: VoxelControl = field(default_factory=VoxelControl)
    slicing: SliceControl = field(default_factory=SliceControl)
    descriptor: DescriptorControl = field(default_factory=DescriptorControl)
    artifacts: ArtifactControl = field(default_factory=ArtifactControl)
    training: TrainingControl = field(default_factory=TrainingControl)


@dataclass(frozen=True)
class FrozenRunConfig:
    hq_version: str
    run_id: str
    route_id: str
    root: str
    user_inputs: dict[str, Any]
    derived: dict[str, Any]
    locked: dict[str, Any]
    config_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _sha256(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def controller_from_dict(raw: dict[str, Any]) -> URP4Controller:
    """Build a typed controller from a JSON-compatible mapping."""

    return URP4Controller(
        workflow=WorkflowControl(**raw.get("workflow", {})),
        paths=PathControl(**raw.get("paths", {})),
        geometry=GeometryControl(**raw.get("geometry", {})),
        import_control=ImportControl(**raw.get("import_control", {})),
        generator=GeneratorControl(**raw.get("generator", {})),
        lattice=LatticeControl(**raw.get("lattice", {})),
        tpms=TPMSControl(**raw.get("tpms", {})),
        voxel=VoxelControl(**raw.get("voxel", {})),
        slicing=SliceControl(**raw.get("slicing", {})),
        descriptor=DescriptorControl(**raw.get("descriptor", {})),
        artifacts=ArtifactControl(**raw.get("artifacts", {})),
        training=TrainingControl(**raw.get("training", {})),
    )


def validate_and_freeze(controller: URP4Controller, root: str | Path) -> FrozenRunConfig:
    root_path = Path(root).resolve()
    values = asdict(controller)
    w, g, s = controller.workflow, controller.geometry, controller.slicing

    if w.import_geometry == w.generate_geometry:
        raise ValueError("Exactly one of import_geometry/generate_geometry must be True")
    if controller.paths.input_directory:
        raise ValueError("input_directory is reserved for locked batch execution in HQ v0.1")
    if w.run_batch:
        raise ValueError("Batch execution is an interface-only switch and remains locked in HQ v0.1")
    if w.feature_selection or w.training:
        if not controller.paths.target_y:
            raise ValueError("Feature selection/training requires an explicit target_y and remains locked in HQ v0.1")
        raise ValueError("Feature selection/training execution is intentionally locked in HQ v0.1")
    if s.axis.lower() != "z":
        raise ValueError("HQ v0.1 is qualified for z slicing only")
    if s.threshold_rule != "binary_nonzero_png_readback":
        raise ValueError("HQ v0.1 permits only binary_nonzero_png_readback thresholding")
    unsupported_scopes = {
        "point": controller.descriptor.point_enabled,
        "surface": controller.descriptor.surface_enabled,
        "lattice": controller.descriptor.lattice_enabled,
        "candidate": controller.descriptor.candidate_enabled,
    }
    requested_unsupported = [name for name, enabled in unsupported_scopes.items() if enabled]
    if requested_unsupported:
        raise ValueError(f"descriptor scopes not qualified in HQ v0.1: {requested_unsupported}")
    if w.extract_descriptors and not controller.descriptor.slice_enabled:
        raise ValueError("RUN_DESCRIPTOR_EXTRACTION requires slice_enabled=True in HQ v0.1")
    if not str(controller.paths.experiment_name).strip():
        raise ValueError("experiment_name cannot be empty")
    if not str(controller.paths.output_root).strip():
        raise ValueError("output_root cannot be empty")
    if not str(g.model_id).strip():
        raise ValueError("model_id cannot be empty")
    if not str(g.geometry_revision).strip():
        raise ValueError("geometry_revision cannot be empty")
    if controller.geometry.expected_size_mm <= 0:
        raise ValueError("expected_size_mm must be positive")
    if s.physical_size_mm <= 0:
        raise ValueError("physical_size_mm must be positive")
    if controller.generator.random_seed < 0:
        raise ValueError("random_seed must be non-negative")
    if not 0 < controller.generator.target_vf < 1:
        raise ValueError("target_vf must lie in (0, 1)")
    if controller.tpms.registry_index < 0 or controller.voxel.registry_index < 0:
        raise ValueError("generator registry_index must be non-negative")
    if controller.tpms.grid_n < 16 or controller.voxel.grid_n < 2:
        raise ValueError("TPMS grid_n must be >= 16 and Voxel grid_n must be >= 2")
    if controller.voxel.rows_per_mode < 1:
        raise ValueError("voxel rows_per_mode must be >= 1")
    if s.definition_mode == "derive_count_from_spacing":
        if s.slice_count is not None:
            raise ValueError("slice_count must be None when definition_mode=derive_count_from_spacing")
        if s.slice_spacing_mm is None or s.slice_spacing_mm <= 0:
            raise ValueError("positive slice_spacing_mm is required")
        slice_spacing = float(s.slice_spacing_mm)
        slice_count = int(round(s.physical_size_mm / slice_spacing)) + 1
    elif s.definition_mode == "derive_spacing_from_count":
        if s.slice_spacing_mm is not None:
            raise ValueError("slice_spacing_mm must be None when definition_mode=derive_spacing_from_count")
        if s.slice_count is None or s.slice_count < 2:
            raise ValueError("slice_count >= 2 is required")
        slice_count = int(s.slice_count)
        slice_spacing = float(s.physical_size_mm / (slice_count - 1))
    else:
        raise ValueError("unsupported slicing definition_mode")
    if s.pixel_resolution < 2:
        raise ValueError("pixel_resolution must be >= 2")
    pixel_size = float(s.physical_size_mm / s.pixel_resolution)
    area_per_pixel = pixel_size**2

    if controller.lattice.cell_definition_mode == "cells_per_axis":
        if controller.lattice.cell_size_mm is not None:
            raise ValueError("cell_size_mm must be None when cell_definition_mode=cells_per_axis")
        if not controller.lattice.cells_per_axis or controller.lattice.cells_per_axis < 1:
            raise ValueError("cells_per_axis must be >= 1")
        cells_per_axis = int(controller.lattice.cells_per_axis)
        cell_size = float(controller.lattice.total_length_mm / cells_per_axis)
    elif controller.lattice.cell_definition_mode == "cell_size_mm":
        if controller.lattice.cells_per_axis is not None:
            raise ValueError("cells_per_axis must be None when cell_definition_mode=cell_size_mm")
        if not controller.lattice.cell_size_mm or controller.lattice.cell_size_mm <= 0:
            raise ValueError("cell_size_mm must be positive")
        cell_size = float(controller.lattice.cell_size_mm)
        cells_per_axis = int(round(controller.lattice.total_length_mm / cell_size))
        if abs(cells_per_axis * cell_size - controller.lattice.total_length_mm) > 1.0e-9:
            raise ValueError("total_length_mm must be an integer multiple of cell_size_mm")
    else:
        raise ValueError("unsupported lattice cell_definition_mode")

    if controller.artifacts.image_policy not in {"STREAMING_TEMP_PNG", "KEEP_ALL", "KEEP_FLAGGED"}:
        raise ValueError("unsupported image_policy")
    if controller.artifacts.overwrite:
        raise ValueError("overwrite=True is not supported; HQ v0.1 always creates a new run directory")
    if not controller.artifacts.export_component_tables:
        raise ValueError("component-table export is mandatory for traceability in HQ v0.1")
    if controller.artifacts.visual_review_export:
        raise ValueError("automatic visual-review export is not qualified in HQ v0.1; use KEEP_ALL/KEEP_FLAGGED")
    if not controller.import_control.prefer_original_stp:
        raise ValueError("prefer_original_stp=False is not qualified; original STP remains the strict reference")
    if not controller.training.grouped_split_required:
        raise ValueError("grouped_split_required=False is forbidden by the future modeling contract")
    method_ids = tuple(str(item).strip() for item in controller.training.method_ids)
    if not method_ids or any(not item for item in method_ids) or len(set(method_ids)) != len(method_ids):
        raise ValueError("future training method_ids must be non-empty and unique")
    if w.import_geometry:
        source = Path(controller.paths.input_geometry).expanduser()
        if not source.is_absolute():
            source = root_path / source
        source = source.resolve()
        if not source.is_file():
            raise FileNotFoundError(f"input_geometry does not exist: {source}")
        suffix = source.suffix.lower()
        if g.source_type == "imported_stl" and suffix == ".stl":
            if not controller.import_control.allow_imported_stl:
                raise ValueError("imported STL is disabled by allow_imported_stl=False")
            route_id = ROUTE_IMPORTED
        elif g.source_type == "generated_stl" and suffix == ".stl":
            route_id = ROUTE_GENERATED
        elif g.source_type == "original_stp" and suffix in {".stp", ".step"}:
            route_id = ROUTE_STP
        else:
            raise ValueError(f"source_type/extension mismatch: {g.source_type}/{suffix}")
        values["paths"]["input_geometry"] = str(source)
    else:
        if controller.paths.input_geometry:
            raise ValueError("input_geometry must be empty when generate_geometry=True")
        if g.source_type != "generated_stl":
            raise ValueError("generate_geometry=True requires source_type=generated_stl")
        if controller.generator.family not in {"lattice_type_a", "lattice_type_b", "tpms", "voxel"}:
            raise ValueError("unsupported generator family")
        if controller.generator.family == "tpms" and not 0.45 <= controller.generator.target_vf <= 0.55:
            raise ValueError("TPMS target_vf is qualified only in the source-replay range 0.45..0.55 in HQ v0.1")
        if controller.generator.requested_format.lower() != "stl":
            raise ValueError("HQ v0.1 generated route requires STL; STEP export is not a silent fallback")
        route_id = ROUTE_GENERATED

    if w.extract_descriptors:
        if route_id == ROUTE_STP:
            raise ValueError("original STP is strict/reference in HQ v0.1; direct descriptor adapter is not yet qualified")
        if abs(g.expected_size_mm - 40.0) >= 1.0e-12:
            raise ValueError("descriptor extraction requires expected_size_mm=40.0")
        if abs(s.physical_size_mm - g.expected_size_mm) >= 1.0e-12:
            raise ValueError("slicing physical_size_mm must equal geometry expected_size_mm")
        if w.generate_geometry and controller.generator.family == "lattice_type_a" and abs(controller.lattice.total_length_mm - g.expected_size_mm) >= 1.0e-12:
            raise ValueError("generated Lattice total_length_mm must equal geometry expected_size_mm")
        if route_id == ROUTE_GENERATED and controller.artifacts.image_policy == "KEEP_FLAGGED":
            raise ValueError("KEEP_FLAGGED is not qualified for generated STL in HQ v0.1; use STREAMING_TEMP_PNG or KEEP_ALL")
        approved = (
            abs(s.physical_size_mm - 40.0) < 1.0e-12
            and slice_count == 801
            and abs(slice_spacing - 0.05) < 1.0e-12
            and s.pixel_resolution == 1000
            and s.connectivity == 8
            and s.min_component_pixels == 2
        )
        if not approved:
            raise ValueError(f"descriptor extraction requires approved profile {APPROVED_DESCRIPTOR_PROFILE}")

    derived = {
        "slice_count": slice_count,
        "slice_spacing_mm": slice_spacing,
        "pixel_size_mm": pixel_size,
        "area_per_pixel_mm2": area_per_pixel,
        "lattice_cells_per_axis": cells_per_axis,
        "lattice_cell_size_mm": cell_size,
    }
    imported_lock = ImportedSTLWindingConfig(
        pixel_resolution=s.pixel_resolution,
        slice_count=slice_count,
        expected_size_mm=g.expected_size_mm,
        normalization_mode="uniform_bbox_to_expected" if g.normalize_imported_stl else "require_expected_size",
    )
    locked = {
        "runtime_alias": "KMK312",
        "descriptor_backend_id": RUN139_BACKEND_ID,
        "descriptor_profile": APPROVED_DESCRIPTOR_PROFILE,
        "formula_ids": [f"XRV1-F{i:03d}" for i in range(1, 9)],
        "imported_stl_algorithm_revision": imported_lock.algorithm_revision,
        "imported_stl_route_id": imported_lock.route_id,
        "stl_to_step_default_fallback": False,
        "training_execution": "fail_closed_off",
        "batch_execution": "fail_closed_off",
        "supported_descriptor_scope": "slice_only",
    }
    identity = {"hq_version": HQ_VERSION, "route_id": route_id, "user_inputs": values, "derived": derived, "locked": locked}
    config_sha = _sha256(identity)
    return FrozenRunConfig(
        hq_version=HQ_VERSION,
        run_id=f"HQ-{config_sha[:12]}",
        route_id=route_id,
        root=str(root_path),
        user_inputs=values,
        derived=derived,
        locked=locked,
        config_sha256=config_sha,
    )
