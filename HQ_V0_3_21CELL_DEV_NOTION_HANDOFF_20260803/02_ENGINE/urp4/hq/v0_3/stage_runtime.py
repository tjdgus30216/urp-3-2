"""Explicit, fail-closed stages for the 21-cell HQ development notebook.

The module deliberately reuses the submitted v0.1 geometry/pixel/descriptor
engines and the real v0.2 control validator.  It exposes their work in stages
instead of hiding the whole route behind a single notebook-cell ``run_hq``.
No y, feature selection, Training, XREG factory, forward prediction or inverse
design engine is invented here.
"""

from __future__ import annotations

import json
import hashlib
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from urp4.contracts.v0_1.canonical import sha256_file
from urp4.descriptor_service.v0_1 import Run139DescriptorService, Run139ExtractionPipeline
from urp4.descriptor_service.v0_1.config import ExtractionConfig
from urp4.geometry_io.v0_3.source_preflight import GeometrySourceRecord, inspect_source
from urp4.geometry_io.v0_4.imported_winding import ImportedSTLWindingConfig
from urp4.hq.v0_1.controller import FrozenRunConfig, URP4Controller, validate_and_freeze as validate_v01
from urp4.hq.v0_1.engine import _generated_geometry, _write_json, _write_output_manifest
from urp4.hq.v0_1.imported_pipeline import extract_imported_stl
from urp4.hq.v0_2 import HQV02Controller, validate_v02
from urp4.hq.v0_2.control import _read_frozen_tables
from urp4.hq.v0_2.direct_aggregation import compute_exploratory_direct


STAGE_DEFINITIONS: tuple[dict[str, str], ...] = (
    {"cell": "01", "title": "사용자 설정", "mode": "implemented_contract"},
    {"cell": "02", "title": "config freeze", "mode": "implemented"},
    {"cell": "03", "title": "stage / route 상태", "mode": "implemented"},
    {"cell": "04", "title": "source inventory", "mode": "implemented"},
    {"cell": "05", "title": "geometry generation / import", "mode": "implemented_for_stl"},
    {"cell": "06", "title": "normalization", "mode": "implemented_as_imported_winding_contract"},
    {"cell": "07", "title": "geometry QA", "mode": "implemented"},
    {"cell": "08", "title": "slicing", "mode": "implemented_for_stl"},
    {"cell": "09", "title": "pixel / component", "mode": "implemented_for_stl"},
    {"cell": "10", "title": "LEGACY descriptor", "mode": "implemented_direct_9_scalar"},
    {"cell": "11", "title": "XREG candidate factory", "mode": "fail_closed_factory_not_hq_api"},
    {"cell": "12", "title": "descriptor QA", "mode": "implemented"},
    {"cell": "13", "title": "full X export", "mode": "partial_direct9_xreg_fail_closed"},
    {"cell": "14", "title": "y intake", "mode": "fail_closed"},
    {"cell": "15", "title": "feature selection", "mode": "fail_closed"},
    {"cell": "16", "title": "Training 1–5", "mode": "fail_closed"},
    {"cell": "17", "title": "model / ensemble", "mode": "fail_closed"},
    {"cell": "18", "title": "forward chain", "mode": "fail_closed"},
    {"cell": "19", "title": "inverse chain", "mode": "fail_closed"},
    {"cell": "20", "title": "export / manifest", "mode": "implemented"},
    {"cell": "21", "title": "final gate", "mode": "implemented_nonproduction_gate"},
)


def freeze_hq_v03(controller: HQV02Controller, root: str | Path) -> dict[str, Any]:
    """Freeze a real v0.2 route or an explicit STEP/STP inventory-only route."""
    root_path = Path(root).resolve()
    base = controller.base
    # v0.2 correctly rejects STEP/STP descriptor extraction.  v0.3 keeps that
    # fail-closed boundary, but still admits a *read-only inventory contract*
    # so Cells 02–05 can communicate why the route stops.
    if base.geometry.source_type == "original_stp":
        source = _resolve(root_path, base.paths.input_geometry)
        if not source.is_file() or source.suffix.lower() not in {".stp", ".step"}:
            raise ValueError("original_step_stp inventory route requires an existing .stp or .step input_geometry")
        if base.workflow.feature_selection or base.workflow.training or base.workflow.run_batch:
            raise ValueError("STEP/STP inventory route cannot enable feature selection, training, or batch")
        identity = {
            "hq_version": "URP4-HQ-v0.3-step-inventory-only",
            "execution": asdict(controller.execution),
            "base": asdict(base),
            "route_id": "IMP-STP-PERSOLID-REFERENCE",
            "source_path": str(source),
            "source_sha256": sha256_file(source),
            "scientific_status": "external_reference_only_direct_descriptor_fail_closed",
        }
        digest = hashlib.sha256(json.dumps(identity, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
        return {**identity, "run_id": f"HQV03-{digest[:12]}", "config_sha256": digest}
    return validate_v02(controller, root_path)


def _resolve(root: Path, raw: str) -> Path:
    path = Path(raw).expanduser()
    return (path if path.is_absolute() else root / path).resolve()


@dataclass
class HQStageSession:
    """Stateful execution context used sequentially by notebook cells 02–21."""

    controller: HQV02Controller
    root: Path
    contract: dict[str, Any]
    run_dir: Path | None = None
    frozen_v01: FrozenRunConfig | None = None
    geometry_path: Path | None = None
    source_type: str | None = None
    preflight: dict[str, Any] | None = None
    extraction: Any | None = None
    tables: Any | None = None
    scalar_frame: pd.DataFrame | None = None
    records: dict[str, dict[str, Any]] = field(default_factory=dict)

    @classmethod
    def create(cls, controller: HQV02Controller, root: str | Path) -> "HQStageSession":
        root_path = Path(root).resolve()
        contract = freeze_hq_v03(controller, root_path)
        frozen = validate_v01(controller.base, root_path) if (
            controller.execution.execution_mode == "IMAGE_PIPELINE"
            and controller.execution.qualification_mode == "STRICT"
            and controller.base.geometry.source_type != "original_stp"
        ) else None
        session = cls(controller=controller, root=root_path, contract=contract, frozen_v01=frozen)
        session._record("02", "passed", "v0.2 validation contract frozen", contract)
        return session

    def _record(self, cell: str, status: str, note: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        value = {"cell": cell, "status": status, "note": note, "payload": payload or {}}
        self.records[cell] = value
        return value

    def stage_status(self) -> pd.DataFrame:
        rows = []
        for definition in STAGE_DEFINITIONS:
            state = self.records.get(definition["cell"], {})
            rows.append({**definition, "execution_status": state.get("status", "not_run"), "note": state.get("note", "")})
        return pd.DataFrame(rows)

    def stage_route_status(self) -> dict[str, Any]:
        """Record Cell 03 without starting a geometry or descriptor route."""
        payload = {
            "execution_mode": self.controller.execution.execution_mode,
            "qualification_mode": self.controller.execution.qualification_mode,
            "descriptor_lane": self.controller.execution.descriptor_lane,
            "source_type": self.controller.base.geometry.source_type,
            "route_id": self.contract.get("route_id"),
            "scientific_status": self.contract.get("scientific_status"),
        }
        return self._record("03", "passed", "route/status contract displayed; no calculation started", payload)

    def source_inventory(self) -> dict[str, Any]:
        execution = self.controller.execution
        base = self.controller.base
        if execution.execution_mode == "FROZEN_REPLAY":
            tables = _read_frozen_tables(_resolve(self.root, execution.frozen_table_root), execution.frozen_model_id)
            payload = {"route": "FROZEN_REPLAY", "model_id": tables.model_id, "table_root": str(_resolve(self.root, execution.frozen_table_root)), "image_or_geometry_accessed": False}
            return self._record("04", "passed", "three primitive tables available for replay", payload)
        if base.geometry.source_type == "original_stp":
            payload = {"source_type": "original_step_stp", "status": "blocked", "reason": "direct descriptor engine is not implemented"}
            return self._record("04", "blocked", "STEP/STP inventory only; direct descriptor is fail-closed", payload)
        if base.workflow.generate_geometry:
            return self._record("04", "passed", "generated STL will be created in Cell 05", {"source_type": "generated_stl", "family": base.generator.family})
        source = _resolve(self.root, base.paths.input_geometry)
        if not source.is_file():
            raise FileNotFoundError(f"input STL not found: {source}")
        payload = {"source_type": base.geometry.source_type, "path": str(source), "sha256": sha256_file(source), "bytes": source.stat().st_size}
        return self._record("04", "passed", "input STL inventory frozen", payload)

    def _begin_run(self) -> Path:
        if self.run_dir is not None:
            return self.run_dir
        base = self.controller.base
        output_root = _resolve(self.root, base.paths.output_root)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        target = output_root / f"HQV03-{self.contract['config_sha256'][:12]}_{stamp}"
        target.mkdir(parents=True, exist_ok=False)
        _write_json(target / "frozen_run_config.json", self.contract)
        self.run_dir = target
        return target

    def geometry_generation_or_import(self) -> dict[str, Any]:
        if self.controller.execution.execution_mode == "FROZEN_REPLAY":
            self._begin_run()
            return self._record("05", "not_applicable", "Frozen replay does not create or import geometry", {"run_dir": str(self.run_dir)})
        base = self.controller.base
        if base.geometry.source_type == "original_stp":
            return self._record("05", "blocked", "STEP/STP direct descriptor is fail-closed", {"source_type": "original_step_stp"})
        run_dir = self._begin_run()
        if base.workflow.generate_geometry:
            if self.frozen_v01 is None:
                raise RuntimeError("generated geometry stage currently requires STRICT validation")
            path, generation = _generated_geometry(base, self.frozen_v01, run_dir)
            self.geometry_path, self.source_type = path, "generated_stl"
            payload = {"geometry_path": str(path), **generation}
            _write_json(run_dir / "generation_manifest.json", payload)
            return self._record("05", "passed", "generated STL created by submitted v0.1 generator", payload)
        path = _resolve(self.root, base.paths.input_geometry)
        self.geometry_path, self.source_type = path, "imported_stl" if base.geometry.source_type == "imported_stl" else "generated_stl"
        payload = {"geometry_path": str(path), "sha256": sha256_file(path), "source_type": self.source_type}
        _write_json(run_dir / "input_geometry_manifest.json", payload)
        return self._record("05", "passed", "existing STL imported without mutation", payload)

    def normalization_contract(self) -> dict[str, Any]:
        base = self.controller.base
        if self.controller.execution.execution_mode == "FROZEN_REPLAY":
            return self._record("06", "not_applicable", "Frozen replay preserves prior primitive-table coordinates", {})
        if base.geometry.source_type == "original_stp":
            return self._record("06", "blocked", "STEP/STP route has no direct descriptor normalizer", {})
        if self.geometry_path is None:
            raise RuntimeError("run Cell 05 before Cell 06")
        if self.source_type == "imported_stl":
            payload = {"normalization_mode": "uniform_bbox_to_expected" if base.geometry.normalize_imported_stl else "require_expected_size", "target_mm": base.geometry.expected_size_mm, "implemented_by": "urp4.geometry_io.v0_4.imported_winding.ImportedSTLWindingConfig"}
            return self._record("06", "pending_execution_in_cell08", "normalization is executed by imported winding mask generation", payload)
        return self._record("06", "passed", "generated route uses its declared 40 mm source geometry", {"target_mm": base.geometry.expected_size_mm})

    def geometry_qa(self) -> dict[str, Any]:
        if self.controller.execution.execution_mode == "FROZEN_REPLAY":
            return self._record("07", "not_applicable", "Frozen replay has table-hash identity only", {})
        if self.geometry_path is None or self.source_type is None:
            raise RuntimeError("run Cell 05 before Cell 07")
        route = "GEN-STL-NATIVE-CONTROLLED" if self.source_type == "generated_stl" else "IMP-STL-ROBUST-DEV"
        self.preflight = inspect_source(GeometrySourceRecord.from_values(model_id=self.controller.base.geometry.model_id, pair_id=self.controller.base.geometry.model_id, source_type=self.source_type, path=self.geometry_path, geometry_revision=self.controller.base.geometry.geometry_revision, expected_route_id=route))
        _write_json(self._begin_run() / "geometry_preflight.json", self.preflight)
        if self.controller.base.import_control.reject_topology_risk and not bool(self.preflight.get("topology_clean")):
            raise RuntimeError("geometry topology risk rejected by controller policy")
        return self._record("07", "passed", "source preflight recorded", self.preflight)

    def slicing_pixel_component(self) -> dict[str, Any]:
        """Execute actual image/mask/pixel/component work; no descriptor aggregation."""
        base = self.controller.base
        if self.controller.execution.execution_mode == "FROZEN_REPLAY":
            self.tables = _read_frozen_tables(_resolve(self.root, self.controller.execution.frozen_table_root), self.controller.execution.frozen_model_id)
            self._record("08", "not_applicable", "Frozen replay creates no new slices", {"slice_rows": len(self.tables.slice_pixels)})
            return self._record("09", "passed", "primitive pixel/component tables loaded", {"slice_rows": len(self.tables.slice_pixels), "overlay_rows": len(self.tables.overlay_pixels), "component_rows": len(self.tables.overlay_components)})
        if self.geometry_path is None or self.source_type is None:
            raise RuntimeError("run Cells 05 and 07 before Cell 08")
        strict = self.controller.execution.qualification_mode == "STRICT"
        if strict and self.frozen_v01 is None:
            raise RuntimeError("STRICT route is missing v0.1 frozen contract")
        if strict:
            count, spacing, pixel, area = 801, 0.05, 1000, 0.0016
        else:
            derived = self.contract["derived"]
            count, spacing, pixel, area = int(derived["slice_count"]), float(derived["slice_spacing_mm"]), base.slicing.pixel_resolution, float(derived["area_per_pixel_mm2"])
        target = self._begin_run() / "descriptor"
        if self.source_type == "generated_stl":
            cfg = ExtractionConfig(axis="z", physical_size_mm=base.slicing.physical_size_mm, slice_count=count, slice_spacing_mm=spacing, pixel_width=pixel, pixel_height=pixel, area_per_pixel_mm2=area, length_per_pixel_mm=base.slicing.physical_size_mm / pixel, connectivity=base.slicing.connectivity, min_component_pixels=base.slicing.min_component_pixels)
            mode = "ARTIFACT-FULL" if base.artifacts.image_policy == "KEEP_ALL" else "STREAMING"
            self.extraction = Run139ExtractionPipeline(cfg).extract(model_id=base.geometry.model_id, geometry_path=self.geometry_path, output_dir=target, mode=mode, expected_geometry_sha256=sha256_file(self.geometry_path), overwrite=False)
        else:
            cfg = ImportedSTLWindingConfig(pixel_resolution=pixel, slice_count=count, expected_size_mm=base.geometry.expected_size_mm, normalization_mode="uniform_bbox_to_expected" if base.geometry.normalize_imported_stl else "require_expected_size")
            self.extraction = extract_imported_stl(model_id=base.geometry.model_id, geometry_path=self.geometry_path, output_dir=target, config=cfg, image_policy=base.artifacts.image_policy, min_component_pixels=base.slicing.min_component_pixels, connectivity=base.slicing.connectivity)
        self.tables = self.extraction.tables
        self._record("08", "passed", "actual image/mask slicing executed", {"slice_rows": len(self.tables.slice_pixels), "image_policy": base.artifacts.image_policy, "qualification": "strict" if strict else "exploratory_not_parity"})
        return self._record("09", "passed", "actual pixel and connected-component tables produced", {"overlay_rows": len(self.tables.overlay_pixels), "component_rows": len(self.tables.overlay_components), "qa_status": self.extraction.qa.get("status")})

    def legacy_descriptor(self) -> pd.DataFrame:
        if self.tables is None:
            raise RuntimeError("run Cell 09 before Cell 10")
        if self.controller.execution.execution_mode == "FROZEN_REPLAY" or self.controller.execution.qualification_mode == "STRICT":
            scalars = Run139DescriptorService().compute(self.tables)
        else:
            scalars = compute_exploratory_direct(self.tables, slice_count=int(self.contract["derived"]["slice_count"]), pixel_resolution=self.controller.base.slicing.pixel_resolution)
        self.scalar_frame = pd.DataFrame(item.to_row() for item in scalars)
        path = self._begin_run() / "descriptor_result.csv"
        self.scalar_frame.to_csv(path, index=False, encoding="utf-8-sig")
        self.scalar_frame.to_excel(self._begin_run() / "descriptor_result.xlsx", index=False)
        self._record("10", "passed", "direct LEGACY descriptor calculated", {"rows": len(self.scalar_frame), "formula_ids": sorted(self.scalar_frame.formula_id.unique().tolist()), "csv": str(path)})
        return self.scalar_frame

    def xreg_factory_status(self) -> dict[str, Any]:
        payload = {"status": "fail_closed", "reason": "XREG-v2.7 factory has no validated HQ execution API", "factory_reference": "experiments/lab_001_xy_connection_20260626/reports/tables/PRM149_xreg_v2_7_candidate_bank.csv", "implemented_fast_wave_reference": "urp4/descriptor_service/v0_4_fastxreg (separate candidate route, not imported into HQ)"}
        return self._record("11", "blocked", "XREG factory remains a separate, explicit lane", payload)

    def descriptor_qa(self) -> dict[str, Any]:
        if self.scalar_frame is None:
            raise RuntimeError("run Cell 10 before Cell 12")
        payload = {"direct_rows": len(self.scalar_frame), "finite": bool(pd.to_numeric(self.scalar_frame.value, errors="coerce").notna().all()), "image_qa": getattr(self.extraction, "qa", None), "qualification": self.contract.get("scientific_status")}
        return self._record("12", "passed", "direct descriptor QA recorded", payload)

    def full_x_export(self) -> dict[str, Any]:
        if self.scalar_frame is None:
            raise RuntimeError("run Cell 10 before Cell 13")
        direct = self._begin_run() / "x_direct_9.csv"
        self.scalar_frame.to_csv(direct, index=False, encoding="utf-8-sig")
        payload = {"legacy_direct_export": str(direct), "legacy_direct_rows": len(self.scalar_frame), "xreg_status": "blocked_no_hq_api", "not_a_full_xreg_export": True}
        _write_json(self._begin_run() / "full_x_export_status.json", payload)
        return self._record("13", "partial", "only the implemented direct-9 X lane is exported", payload)

    def fail_closed_stage(self, cell: str) -> dict[str, Any]:
        title = next(item["title"] for item in STAGE_DEFINITIONS if item["cell"] == cell)
        return self._record(cell, "blocked", f"{title} has no admitted HQ execution engine", {"status": "fail_closed", "y_accessed": False, "silent_surrogate": False})

    def export_manifest(self) -> dict[str, Any]:
        run_dir = self._begin_run()
        _write_json(run_dir / "stage_status.json", self.records)
        manifest = _write_output_manifest(run_dir)
        return self._record("20", "passed", "output manifest and stage status written", {"manifest": str(manifest)})

    def final_gate(self) -> dict[str, Any]:
        required = {"02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "20"}
        missing = sorted(required - set(self.records))
        payload = {"status": "development_execution_complete_not_production_release", "missing_prior_cells": missing, "implemented_direct_descriptor": self.records.get("10", {}).get("status") == "passed", "xreg_hq_api": "blocked", "y_training_inverse": "blocked", "scientific_release": False}
        _write_json(self._begin_run() / "final_gate.json", payload)
        return self._record("21", "passed" if not missing else "partial", "final gate preserves blocked scientific lanes", payload)
