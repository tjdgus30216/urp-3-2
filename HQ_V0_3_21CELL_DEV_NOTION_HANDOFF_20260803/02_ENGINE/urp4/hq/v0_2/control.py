"""Versioned HQ v0.2 control plane with no silent scientific promotion.

The submitted HQ v0.1 remains the strict P1000/Z801/N40 reference.  This
module reuses its engine exactly for strict runs and only labels a changed
slice/pixel configuration as ``EXPLORATORY_NOT_PARITY``.  Frozen replay reads
the table artifacts produced by a prior image-readback run; it never invents
pixels or accesses geometry.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, replace
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

import pandas as pd

from urp4.contracts.v0_1.canonical import sha256_file
from urp4.descriptor_service.v0_1 import Run139DescriptorService, Run139ExtractionPipeline
from urp4.descriptor_service.v0_1.config import ExtractionConfig
from urp4.descriptor_service.v0_1.models import PrimitiveTables
from urp4.geometry_io.v0_3.source_preflight import GeometrySourceRecord, inspect_source
from urp4.geometry_io.v0_4.imported_winding import ImportedSTLWindingConfig
from urp4.hq.v0_1 import run_hq as run_hq_v01
from urp4.hq.v0_1 import validate_and_freeze as validate_v01
from urp4.hq.v0_1.controller import ROUTE_GENERATED, ROUTE_IMPORTED, URP4Controller
from urp4.hq.v0_1.engine import _generated_geometry, _write_json, _write_output_manifest
from urp4.hq.v0_1.imported_pipeline import extract_imported_stl

from .direct_aggregation import compute_exploratory_direct


ExecutionMode = Literal["IMAGE_PIPELINE", "FROZEN_REPLAY"]
QualificationMode = Literal["STRICT", "EXPLORATORY"]
DescriptorLane = Literal["LEGACY_DIRECT", "XREG_CANDIDATE"]


@dataclass(frozen=True)
class ExecutionControl:
    """The additional controls exposed by HQ v0.2.

    ``STRICT`` is the submitted P1000/Z801/N40 reference profile.  Changing
    physical slicing values requires ``EXPLORATORY`` and results are tagged
    non-parity.  ``XREG_CANDIDATE`` is deliberately fail-closed: the current
    XREG bank is a separate, audited factory rather than an HQ engine API.
    """

    execution_mode: ExecutionMode = "IMAGE_PIPELINE"
    qualification_mode: QualificationMode = "STRICT"
    descriptor_lane: DescriptorLane = "LEGACY_DIRECT"
    frozen_table_root: str = ""
    frozen_model_id: str = ""


@dataclass(frozen=True)
class HQV02Controller:
    """A v0.1 controller plus versioned execution controls."""

    base: URP4Controller
    execution: ExecutionControl = ExecutionControl()


def _json_hash(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _resolve(root: Path, raw: str) -> Path:
    path = Path(raw).expanduser()
    return (path if path.is_absolute() else root / path).resolve()


def _derived_slice(base: URP4Controller) -> dict[str, float | int]:
    s = base.slicing
    if s.axis.lower() != "z":
        raise ValueError("HQ v0.2 supports z slicing only; other axes need their own validated route")
    if s.definition_mode == "derive_count_from_spacing":
        if s.slice_count is not None or s.slice_spacing_mm is None or s.slice_spacing_mm <= 0:
            raise ValueError("derive_count_from_spacing requires slice_count=None and positive slice_spacing_mm")
        count = int(round(s.physical_size_mm / s.slice_spacing_mm)) + 1
        spacing = float(s.slice_spacing_mm)
    elif s.definition_mode == "derive_spacing_from_count":
        if s.slice_spacing_mm is not None or s.slice_count is None or s.slice_count < 2:
            raise ValueError("derive_spacing_from_count requires slice_spacing_mm=None and slice_count>=2")
        count = int(s.slice_count)
        spacing = float(s.physical_size_mm / (count - 1))
    else:
        raise ValueError("unsupported slicing definition_mode")
    if s.pixel_resolution < 2 or s.connectivity not in {4, 8} or s.min_component_pixels < 1:
        raise ValueError("invalid pixel/component settings")
    pixel = float(s.physical_size_mm / s.pixel_resolution)
    return {
        "slice_count": count,
        "slice_spacing_mm": spacing,
        "pixel_size_mm": pixel,
        "area_per_pixel_mm2": pixel * pixel,
    }


def _table_root(path: Path) -> Path:
    return path / "tables" if (path / "tables").is_dir() else path


def _read_frozen_tables(root: Path, requested_model_id: str) -> PrimitiveTables:
    tables = _table_root(root)
    required = {
        "slice_pixels": tables / "slice_pixel_count_table.csv",
        "overlay_pixels": tables / "overlay_pixel_table.csv",
        "overlay_components": tables / "overlay_component_table.csv",
    }
    missing = [str(path) for path in required.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError("Frozen replay requires the three original primitive CSVs: " + "; ".join(missing))
    frames = {name: pd.read_csv(path, encoding="utf-8-sig") for name, path in required.items()}
    ids = set()
    for frame in frames.values():
        if "model_id" not in frame.columns:
            raise ValueError("Frozen replay table has no model_id column")
        ids.update(str(value) for value in frame["model_id"].dropna().unique())
    if len(ids) != 1:
        raise ValueError(f"Frozen replay requires one model per table root, observed model IDs: {sorted(ids)}")
    model_id = next(iter(ids))
    if requested_model_id and requested_model_id != model_id:
        raise ValueError(f"frozen_model_id mismatch: requested={requested_model_id}, observed={model_id}")
    return PrimitiveTables(model_id, frames["slice_pixels"], frames["overlay_pixels"], frames["overlay_components"])


def validate_v02(controller: HQV02Controller, root: str | Path) -> dict[str, Any]:
    """Validate controls and return a hash-addressed, JSON-safe run contract."""

    root_path = Path(root).resolve()
    base, execution = controller.base, controller.execution
    if execution.execution_mode not in {"IMAGE_PIPELINE", "FROZEN_REPLAY"}:
        raise ValueError("unsupported execution_mode")
    if execution.qualification_mode not in {"STRICT", "EXPLORATORY"}:
        raise ValueError("unsupported qualification_mode")
    if execution.descriptor_lane != "LEGACY_DIRECT":
        raise ValueError(
            "XREG_CANDIDATE is not an HQ v0.2 execution API yet. Use the audited XREG factory; do not silently substitute it."
        )
    if base.workflow.feature_selection or base.workflow.training or base.workflow.run_batch:
        raise ValueError("feature selection, training, and batch execution remain outside HQ v0.2")
    if not base.workflow.extract_descriptors:
        raise ValueError("HQ v0.2 currently requires extract_descriptors=True")
    if execution.execution_mode == "FROZEN_REPLAY":
        if not execution.frozen_table_root:
            raise ValueError("frozen_table_root is required for FROZEN_REPLAY")
        source = _resolve(root_path, execution.frozen_table_root)
        tables = _read_frozen_tables(source, execution.frozen_model_id)
        identity = {
            "hq_version": "URP4-HQ-v0.2",
            "execution": asdict(execution),
            "base": asdict(base),
            "frozen_table_root": str(source),
            "frozen_model_id": tables.model_id,
            "table_sha256": {
                name: sha256_file(_table_root(source) / filename)
                for name, filename in {
                    "slice_pixels": "slice_pixel_count_table.csv",
                    "overlay_pixels": "overlay_pixel_table.csv",
                    "overlay_components": "overlay_component_table.csv",
                }.items()
            },
            "scientific_status": "replay_only_no_new_image_or_pixel_calculation",
        }
        digest = _json_hash(identity)
        return {**identity, "route_id": "FROZEN-PIXEL-COMPONENT-REPLAY", "run_id": f"HQV02-{digest[:12]}", "config_sha256": digest}

    if execution.qualification_mode == "STRICT":
        frozen = validate_v01(base, root_path)
        identity = frozen.to_dict()
        identity.update({
            "hq_version": "URP4-HQ-v0.2-strict-delegates-v0.1",
            "execution": asdict(execution),
            "scientific_status": "strict_reference_delegated_to_submitted_v0_1",
        })
        return identity

    # Exploratory image execution uses the same pixel-readback engines, but no
    # result may be interpreted as legacy/Excel parity until a new gate exists.
    derived = _derived_slice(base)
    if base.slicing.threshold_rule != "binary_nonzero_png_readback":
        raise ValueError("only binary_nonzero_png_readback is implemented by the reused engine")
    if base.geometry.source_type == "original_stp":
        raise ValueError("direct STEP/STP descriptor extraction remains unimplemented; use it as a reference/preflight source")
    if base.geometry.source_type not in {"generated_stl", "imported_stl"}:
        raise ValueError("source_type must be generated_stl or imported_stl")
    if base.workflow.import_geometry == base.workflow.generate_geometry:
        raise ValueError("exactly one of import_geometry/generate_geometry must be true")
    if base.workflow.generate_geometry and base.geometry.source_type != "generated_stl":
        raise ValueError("generated geometry requires source_type=generated_stl")
    if base.workflow.import_geometry:
        source = _resolve(root_path, base.paths.input_geometry)
        if not source.is_file() or source.suffix.lower() != ".stl":
            raise ValueError("exploratory imported route requires an existing .stl input_geometry")
    if base.artifacts.image_policy not in {"STREAMING_TEMP_PNG", "KEEP_ALL", "KEEP_FLAGGED"}:
        raise ValueError("unsupported image_policy")
    if base.geometry.source_type == "generated_stl" and base.artifacts.image_policy == "KEEP_FLAGGED":
        raise ValueError("KEEP_FLAGGED is only implemented for imported STL")
    identity = {
        "hq_version": "URP4-HQ-v0.2",
        "execution": asdict(execution),
        "base": asdict(base),
        "derived": derived,
        "route_id": "GEN-STL-EXPLORATORY" if base.geometry.source_type == "generated_stl" else "IMP-STL-EXPLORATORY",
        "scientific_status": "exploratory_not_legacy_or_excel_parity",
    }
    digest = _json_hash(identity)
    return {**identity, "run_id": f"HQV02-{digest[:12]}", "config_sha256": digest}


def _run_directory(base: URP4Controller, root: Path, run_id: str) -> Path:
    output_root = _resolve(root, base.paths.output_root)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    target = output_root / f"{run_id}_{stamp}"
    target.mkdir(parents=True, exist_ok=False)
    return target


def _write_scalar_outputs(run_dir: Path, tables: PrimitiveTables, *, exploratory: dict[str, int] | None = None) -> dict[str, Any]:
    scalars = (
        compute_exploratory_direct(tables, slice_count=exploratory["slice_count"], pixel_resolution=exploratory["pixel_resolution"])
        if exploratory else Run139DescriptorService().compute(tables)
    )
    frame = pd.DataFrame([item.to_row() for item in scalars])
    csv_path = run_dir / "descriptor_result.csv"
    xlsx_path = run_dir / "descriptor_result.xlsx"
    frame.to_csv(csv_path, index=False, encoding="utf-8-sig")
    frame.to_excel(xlsx_path, index=False)
    return {"status": "passed", "row_count": len(frame), "csv": str(csv_path), "xlsx": str(xlsx_path), "formula_ids": sorted(frame["formula_id"].unique().tolist())}


def _run_frozen_replay(controller: HQV02Controller, root: Path, contract: dict[str, Any]) -> dict[str, Any]:
    run_dir = _run_directory(controller.base, root, contract["run_id"])
    tables = _read_frozen_tables(Path(contract["frozen_table_root"]), controller.execution.frozen_model_id)
    _write_json(run_dir / "frozen_run_config.json", contract)
    _write_json(run_dir / "frozen_replay_input_manifest.json", {
        "source_table_root": contract["frozen_table_root"], "model_id": tables.model_id,
        "table_sha256": contract["table_sha256"], "image_or_geometry_accessed": False,
    })
    descriptor = _write_scalar_outputs(run_dir, tables)
    status = {"status": "passed", "run_id": contract["run_id"], "route_id": contract["route_id"], "run_dir": str(run_dir), "descriptor": descriptor, "scientific_status": contract["scientific_status"]}
    _write_json(run_dir / "run_status.json", status)
    status["output_manifest"] = str(_write_output_manifest(run_dir))
    return status


def _run_exploratory(controller: HQV02Controller, root: Path, contract: dict[str, Any]) -> dict[str, Any]:
    base = controller.base
    run_dir = _run_directory(base, root, contract["run_id"])
    _write_json(run_dir / "frozen_run_config.json", contract)
    if base.workflow.generate_geometry:
        # Reuse the submitted geometry generator.  Descriptor extraction is
        # disabled only for its validation step; slicing below is real v0.2 work.
        generator_only = replace(base, workflow=replace(base.workflow, extract_descriptors=False))
        frozen = validate_v01(generator_only, root)
        geometry_path, generation = _generated_geometry(generator_only, frozen, run_dir)
        source_type = "generated_stl"
    else:
        geometry_path = _resolve(root, base.paths.input_geometry)
        generation = None
        source_type = "imported_stl"
    preflight = inspect_source(GeometrySourceRecord.from_values(
        model_id=base.geometry.model_id, pair_id=base.geometry.model_id, source_type=source_type,
        path=geometry_path, geometry_revision=base.geometry.geometry_revision,
        # Source preflight validates the physical source route.  The v0.2
        # exploratory label belongs to the *calculation configuration*, not
        # to a new geometry-source route.
        expected_route_id=("GEN-STL-NATIVE-CONTROLLED" if source_type == "generated_stl" else "IMP-STL-ROBUST-DEV"),
    ))
    _write_json(run_dir / "geometry_preflight.json", preflight)
    _write_json(run_dir / "input_geometry_manifest.json", {
        "model_id": base.geometry.model_id, "source_type": source_type, "source_path": str(geometry_path),
        "source_sha256": sha256_file(geometry_path), "route_id": contract["route_id"],
    })
    if base.import_control.reject_topology_risk and not bool(preflight.get("topology_clean")):
        raise RuntimeError("geometry topology risk rejected by controller policy")
    d = contract["derived"]
    descriptor_root = run_dir / "descriptor"
    if source_type == "generated_stl":
        cfg = ExtractionConfig(axis="z", physical_size_mm=base.slicing.physical_size_mm, slice_count=int(d["slice_count"]), slice_spacing_mm=float(d["slice_spacing_mm"]), pixel_width=base.slicing.pixel_resolution, pixel_height=base.slicing.pixel_resolution, area_per_pixel_mm2=float(d["area_per_pixel_mm2"]), length_per_pixel_mm=float(d["pixel_size_mm"]), connectivity=base.slicing.connectivity, min_component_pixels=base.slicing.min_component_pixels)
        extraction = Run139ExtractionPipeline(cfg).extract(model_id=base.geometry.model_id, geometry_path=geometry_path, output_dir=descriptor_root, mode="ARTIFACT-FULL" if base.artifacts.image_policy == "KEEP_ALL" else "STREAMING", expected_geometry_sha256=sha256_file(geometry_path), overwrite=False)
    else:
        cfg = ImportedSTLWindingConfig(pixel_resolution=base.slicing.pixel_resolution, slice_count=int(d["slice_count"]), expected_size_mm=base.geometry.expected_size_mm, normalization_mode="uniform_bbox_to_expected" if base.geometry.normalize_imported_stl else "require_expected_size")
        extraction = extract_imported_stl(model_id=base.geometry.model_id, geometry_path=geometry_path, output_dir=descriptor_root, config=cfg, image_policy=base.artifacts.image_policy, min_component_pixels=base.slicing.min_component_pixels, connectivity=base.slicing.connectivity)
    descriptor = _write_scalar_outputs(run_dir, extraction.tables, exploratory={"slice_count": int(d["slice_count"]), "pixel_resolution": base.slicing.pixel_resolution})
    descriptor["image_qa"] = extraction.qa
    status = {"status": "passed" if extraction.qa.get("status") == "passed" else "completed_with_exploratory_image_qa_warning", "run_id": contract["run_id"], "route_id": contract["route_id"], "run_dir": str(run_dir), "generation": generation, "preflight": preflight, "descriptor": descriptor, "scientific_status": contract["scientific_status"]}
    _write_json(run_dir / "run_status.json", status)
    status["output_manifest"] = str(_write_output_manifest(run_dir))
    return status


def run_hq_v02(controller: HQV02Controller, root: str | Path) -> dict[str, Any]:
    """Execute an actual v0.1 strict run, v0.2 exploratory run, or replay."""

    root_path = Path(root).resolve()
    contract = validate_v02(controller, root_path)
    if controller.execution.execution_mode == "FROZEN_REPLAY":
        return _run_frozen_replay(controller, root_path, contract)
    if controller.execution.qualification_mode == "STRICT":
        result = run_hq_v01(controller.base, root_path)
        result["hq_v02_contract"] = {"mode": "STRICT", "delegated_to": "URP4-HQ-v0.1", "config_sha256": contract["config_sha256"]}
        return result
    return _run_exploratory(controller, root_path, contract)
