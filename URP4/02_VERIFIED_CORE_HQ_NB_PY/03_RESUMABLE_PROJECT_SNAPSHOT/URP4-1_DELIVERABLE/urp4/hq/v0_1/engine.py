"""Production-shaped, fail-closed HQ execution engine."""

from __future__ import annotations

import json
import hashlib
from dataclasses import asdict, replace
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from urp4.contracts.v0_1.canonical import sha256_file
from urp4.descriptor_service.v0_1 import Run139DescriptorService, Run139ExtractionPipeline
from urp4.descriptor_service.v0_1.config import ExtractionConfig
from urp4.generators.lattice_typeab.v0_1 import GenerationConfig, build_type_a_request
from urp4.generators.lattice_typeab.v0_1.plugin import LatticeTypeABPlugin, package_code_sha256 as lattice_code_sha
from urp4.generators.tpms_multiwall.v0_1 import TPMSMultiwallPlugin, build_multiwall_candidate_registry, build_multiwall_request
from urp4.generators.tpms_multiwall.v0_1.plugin import package_code_sha256 as tpms_code_sha
from urp4.generators.voxel.v0_1 import VoxelPlugin, build_voxel_registry, build_voxel_request
from urp4.generators.voxel.v0_1.plugin import package_code_sha256 as voxel_code_sha
from urp4.geometry_io.v0_3.source_preflight import GeometrySourceRecord, inspect_source
from urp4.geometry_io.v0_4.imported_winding import ImportedSTLWindingConfig

from .controller import ROUTE_GENERATED, ROUTE_IMPORTED, ROUTE_STP, FrozenRunConfig, URP4Controller, validate_and_freeze
from .imported_pipeline import extract_imported_stl


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")


def _write_output_manifest(run_dir: Path) -> Path:
    rows = []
    for path in sorted(run_dir.rglob("*")):
        if not path.is_file() or path.name == "output_manifest.csv":
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append({"relative_path": path.relative_to(run_dir).as_posix(), "size_bytes": path.stat().st_size, "sha256": digest})
    target = run_dir / "output_manifest.csv"
    pd.DataFrame(rows).to_csv(target, index=False, encoding="utf-8-sig")
    return target


def _generated_geometry(controller: URP4Controller, frozen: FrozenRunConfig, run_dir: Path) -> tuple[Path, dict[str, Any]]:
    root = Path(frozen.root)
    output = run_dir / "geometry"
    output.mkdir(parents=True, exist_ok=True)
    family = controller.generator.family
    if family == "lattice_type_b":
        raise RuntimeError("Lattice Type B requires the identity-locked Variables.xlsx; HQ v0.1 fails closed")
    if family == "lattice_type_a":
        cfg = GenerationConfig(
            total_length_mm=controller.lattice.total_length_mm,
            cells_per_axis=int(frozen.derived["lattice_cells_per_axis"]),
        )
        request = build_type_a_request(
            config=cfg,
            target_vf=controller.generator.target_vf,
            random_seed=controller.generator.random_seed,
            model_id=controller.geometry.model_id,
            requested_formats=("stl",),
            code_sha256=lattice_code_sha(root),
            root=root,
        )
        outcome = LatticeTypeABPlugin(root).generate(request.document, output)
    elif family == "tpms":
        registry = build_multiwall_candidate_registry(seed=controller.generator.random_seed, grid_n=controller.tpms.grid_n)
        candidate = registry[controller.tpms.registry_index]
        candidate = replace(
            candidate,
            target_vf=controller.generator.target_vf,
            config=replace(candidate.config, size_mm=controller.geometry.expected_size_mm),
        )
        request = build_multiwall_request(candidate=candidate, requested_formats=("stl",), code_sha256=tpms_code_sha(root))
        outcome = TPMSMultiwallPlugin(root).generate(request.document, output)
    elif family == "voxel":
        registry = build_voxel_registry(
            seed=controller.generator.random_seed,
            grid_n=controller.voxel.grid_n,
            target_vf=controller.generator.target_vf,
            rows_per_mode=controller.voxel.rows_per_mode,
            size_mm=controller.geometry.expected_size_mm,
        )
        candidate = registry[controller.voxel.registry_index]
        request = build_voxel_request(candidate=candidate, requested_formats=("stl",), code_sha256=voxel_code_sha(root))
        outcome = VoxelPlugin(root).generate(request.document, output)
    else:
        raise ValueError(f"unsupported generator family: {family}")
    passed = [item for item in outcome.export_attempts if item.geometry_format == "stl" and item.status == "passed"]
    if not passed or not passed[0].path:
        raise RuntimeError("generator did not produce a passed STL artifact")
    # TPMS/Voxel plugins intentionally serialize artifact paths relative to the
    # deliverable root.  Resolving them against the caller's current working
    # directory made HQ execution depend on where Jupyter/Python was launched.
    serialized_path = Path(passed[0].path)
    path = (serialized_path if serialized_path.is_absolute() else root / serialized_path).resolve()
    return path, {
        "family": family,
        "request_object_id": outcome.request.object_id,
        "geometry_path": str(path),
        "geometry_sha256": sha256_file(path),
        "scientific_scope": "source-replay/conditional; not production-policy approval",
    }


def run_hq(controller: URP4Controller, root: str | Path) -> dict[str, Any]:
    frozen = validate_and_freeze(controller, root)
    root_path = Path(frozen.root)
    output_root = Path(controller.paths.output_root)
    if not output_root.is_absolute():
        output_root = root_path / output_root
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    run_dir = output_root / f"{frozen.run_id}_{stamp}"
    run_dir.mkdir(parents=True, exist_ok=False)
    _write_json(run_dir / "frozen_run_config.json", frozen.to_dict())
    _write_json(run_dir / "run_manifest.json", {
        "run_id": frozen.run_id,
        "experiment_name": controller.paths.experiment_name,
        "config_sha256": frozen.config_sha256,
        "route_id": frozen.route_id,
        "runtime_alias": frozen.locked["runtime_alias"],
        "started_at_local": stamp,
        "execution_scope": {
            "generate": controller.workflow.generate_geometry,
            "import": controller.workflow.import_geometry,
            "descriptor": controller.workflow.extract_descriptors,
            "batch": controller.workflow.run_batch,
            "feature_selection": controller.workflow.feature_selection,
            "training": controller.workflow.training,
        },
    })
    status: dict[str, Any] = {
        "run_id": frozen.run_id,
        "config_sha256": frozen.config_sha256,
        "route_id": frozen.route_id,
        "run_dir": str(run_dir),
        "generation": None,
        "preflight": None,
        "descriptor": None,
        "training": {"enabled": False, "status": "locked_off_no_y_access"},
        "status": "running",
    }
    try:
        if controller.workflow.generate_geometry:
            geometry_path, generation = _generated_geometry(controller, frozen, run_dir)
            status["generation"] = generation
            source_type = "generated_stl"
        else:
            geometry_path = Path(frozen.user_inputs["paths"]["input_geometry"])
            source_type = controller.geometry.source_type
        preflight = inspect_source(GeometrySourceRecord.from_values(
            model_id=controller.geometry.model_id,
            pair_id=controller.geometry.model_id,
            source_type=source_type,
            path=geometry_path,
            geometry_revision=controller.geometry.geometry_revision,
            expected_route_id=(
                "GEN-STL-NATIVE-CONTROLLED" if source_type == "generated_stl"
                else "IMP-STL-ROBUST-DEV" if source_type == "imported_stl"
                else "IMP-STP-PERSOLID-REFERENCE"
            ),
        ))
        status["preflight"] = preflight
        _write_json(run_dir / "geometry_preflight.json", preflight)
        _write_json(run_dir / "input_geometry_manifest.json", {
            "model_id": controller.geometry.model_id,
            "source_type": source_type,
            "source_path": str(geometry_path),
            "source_sha256": sha256_file(geometry_path),
            "route_id": frozen.route_id,
            "geometry_revision": controller.geometry.geometry_revision,
        })
        if controller.import_control.reject_topology_risk and not bool(preflight["topology_clean"]):
            raise RuntimeError("geometry topology risk rejected by controller policy")

        if controller.workflow.extract_descriptors:
            descriptor_root = run_dir / "descriptor"
            if frozen.route_id == ROUTE_GENERATED:
                generated_mode = "ARTIFACT-FULL" if controller.artifacts.image_policy == "KEEP_ALL" else "STREAMING"
                extraction = Run139ExtractionPipeline(ExtractionConfig()).extract(
                    model_id=controller.geometry.model_id,
                    geometry_path=geometry_path,
                    output_dir=descriptor_root,
                    mode=generated_mode,
                    expected_geometry_sha256=sha256_file(geometry_path),
                    overwrite=False,
                )
                retention_note = (
                    "KEEP_ALL applied through ARTIFACT-FULL"
                    if controller.artifacts.image_policy == "KEEP_ALL"
                    else "STREAMING_TEMP_PNG applied"
                )
            elif frozen.route_id == ROUTE_IMPORTED:
                cfg = ImportedSTLWindingConfig(
                    pixel_resolution=int(frozen.user_inputs["slicing"]["pixel_resolution"]),
                    slice_count=int(frozen.derived["slice_count"]),
                    expected_size_mm=controller.geometry.expected_size_mm,
                    normalization_mode="uniform_bbox_to_expected" if controller.geometry.normalize_imported_stl else "require_expected_size",
                )
                extraction = extract_imported_stl(
                    model_id=controller.geometry.model_id,
                    geometry_path=geometry_path,
                    output_dir=descriptor_root,
                    config=cfg,
                    image_policy=controller.artifacts.image_policy,
                    min_component_pixels=controller.slicing.min_component_pixels,
                    connectivity=controller.slicing.connectivity,
                )
                retention_note = "imported-STL image policy applied directly"
            else:
                raise RuntimeError("STP descriptor extraction must fail closed in HQ v0.1")
            scalars = Run139DescriptorService().compute(extraction.tables)
            scalar_frame = pd.DataFrame([item.to_row() for item in scalars])
            scalar_csv = run_dir / "descriptor_result.csv"
            scalar_xlsx = run_dir / "descriptor_result.xlsx"
            scalar_frame.to_csv(scalar_csv, index=False, encoding="utf-8-sig")
            scalar_frame.to_excel(scalar_xlsx, index=False)
            status["descriptor"] = {
                "status": extraction.qa["status"],
                "row_count": len(scalar_frame),
                "formula_ids": sorted(scalar_frame["formula_id"].unique().tolist()),
                "csv": str(scalar_csv),
                "xlsx": str(scalar_xlsx),
                "qa": extraction.qa,
                "retention_note": retention_note,
            }
            _write_json(run_dir / "x_only_readiness.json", {
                "status": "ready_for_separate_x_only_QA",
                "descriptor_rows": len(scalar_frame),
                "feature_selection_performed": False,
                "y_accessed": False,
                "note": "This is an interface/readiness result, not feature promotion.",
            })
        _write_json(run_dir / "training_required_input_schema.json", {
            "required": ["semantic feature IDs", "official target_y ID", "family/group IDs", "source/crosswalk provenance"],
            "split_policy": "grouped/family-aware required",
            "method_ids": list(controller.training.method_ids),
            "grouped_split_required": controller.training.grouped_split_required,
            "execution_status": "locked_off_no_y_access",
        })
        status["status"] = "passed"
    except Exception as exc:
        status["status"] = "failed"
        status["failure_type"] = type(exc).__name__
        status["failure_reason"] = str(exc)
        status["output_manifest"] = str(run_dir / "output_manifest.csv")
        _write_json(run_dir / "run_status.json", status)
        _write_output_manifest(run_dir)
        raise
    status["output_manifest"] = str(run_dir / "output_manifest.csv")
    _write_json(run_dir / "run_status.json", status)
    _write_output_manifest(run_dir)
    return status
