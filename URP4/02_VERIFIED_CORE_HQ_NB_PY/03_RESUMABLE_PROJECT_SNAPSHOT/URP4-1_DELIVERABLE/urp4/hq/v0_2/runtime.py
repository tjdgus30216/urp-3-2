"""Fail-closed status runtime for the HQ v0.2 development blueprint."""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from dataclasses import asdict, fields
from datetime import datetime
from pathlib import Path
from typing import Any

from .models import BLUEPRINT_VERSION, STATUS_ONLY_MODE, BlueprintController


EXPECTED_PUBLIC_FIELDS = tuple(item.name for item in fields(BlueprintController))
ALLOWED_STAGE_STATES = {"READY", "EXPERIMENTAL", "LOCKED", "BLOCKED", "PLANNED"}
PROHIBITED_ENABLE_FLAGS = (
    "enable_generated_normalization",
    "enable_y_intake",
    "enable_feature_selection",
    "enable_training",
    "enable_ensemble",
    "enable_forward_performance",
    "enable_inverse_design",
)


def _sha256_json(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _assert_kmk312() -> None:
    executable = str(Path(sys.executable).resolve())
    if "kmk312" not in executable.lower() or sys.version_info[:2] != (3, 12):
        raise RuntimeError(f"HQ Blueprint must run in KMK312/Python 3.12; observed {executable} / {platform.python_version()}")


def validate_and_freeze_blueprint(controller: BlueprintController, root: str | Path) -> dict[str, Any]:
    """Validate the public contract and freeze a status-only run identity."""

    _assert_kmk312()
    root_path = Path(root).resolve()
    values = asdict(controller)
    if controller.execution_mode != STATUS_ONLY_MODE:
        raise ValueError("HQ Blueprint v0.2 permits only execution_mode='blueprint_status_only'")
    if controller.geometry_mode != "status_only":
        raise ValueError("Geometry import/generation execution is locked in Blueprint v0.2; use geometry_mode='status_only'")
    enabled = [name for name in PROHIBITED_ENABLE_FLAGS if bool(getattr(controller, name))]
    if enabled:
        raise ValueError(f"Blueprint status-only mode blocks unvalidated execution flags: {enabled}")
    if controller.batch_enabled:
        raise ValueError("Batch execution remains locked in Blueprint v0.2")
    if controller.input_file or controller.input_directory:
        raise ValueError("Status-only blueprint must not consume geometry paths")
    if controller.y_target:
        raise ValueError("Experimental y intake remains locked; y_target must be empty")
    if any(value != "LOCKED" for value in (controller.feature_selection_method, controller.training_method, controller.ensemble_policy)):
        raise ValueError("Feature selection, Training and ensemble policies must remain LOCKED")
    if controller.source_type not in {"generated_stl", "imported_stl", "original_stp"}:
        raise ValueError("Unsupported source_type")
    if not controller.normalize_all_analysis_geometry:
        raise ValueError("Project decision requires all analysis geometry to target 40×40×40 mm")
    if abs(controller.normalization_target_mm - 40.0) > 1.0e-12:
        raise ValueError("normalization_target_mm is frozen at 40.0 mm")
    if controller.normalization_method != "centered_uniform_bbox_to_40mm":
        raise ValueError("Only the documented centered uniform-scale candidate may appear in the blueprint")
    if controller.slicing_axis.lower() != "z":
        raise ValueError("Current qualified production default is z-axis slicing")
    if controller.pixel_resolution < 2 or controller.slice_count < 2 or controller.slice_spacing_mm <= 0:
        raise ValueError("Invalid slicing resolution/count/spacing")
    expected_span = controller.slice_spacing_mm * (controller.slice_count - 1)
    if abs(expected_span - controller.normalization_target_mm) > 1.0e-9:
        raise ValueError("slice_count and slice_spacing_mm must span the 40 mm analysis domain")
    if controller.connectivity not in {4, 8} or controller.min_component_pixels < 1:
        raise ValueError("Invalid connected-component contract")
    if controller.threshold_rule != "binary_nonzero_png_readback":
        raise ValueError("Only the traced binary PNG-readback threshold is admitted")
    if controller.candidate_registry_version != "XREG-v2.7-TECHNICAL":
        raise ValueError("Blueprint audit is frozen to XREG-v2.7-TECHNICAL")
    if not controller.output_directory.strip():
        raise ValueError("output_directory cannot be empty")

    derived = {
        "physical_size_mm": 40.0,
        "pixel_size_mm": 40.0 / controller.pixel_resolution,
        "area_per_pixel_mm2": (40.0 / controller.pixel_resolution) ** 2,
        "slice_span_mm": expected_span,
        "production_default": controller.pixel_resolution == 1000 and controller.slice_count == 801 and abs(controller.slice_spacing_mm - 0.05) <= 1.0e-12,
        "normalization_policy": "required_for_all_analysis_geometry",
        "generated_normalization_execution": "blocked_pending_HQ-GEOM-001",
        "y_training_inverse": "fail_closed_off",
    }
    identity = {"blueprint_version": BLUEPRINT_VERSION, "user_inputs": values, "derived": derived}
    digest = _sha256_json(identity)
    return {
        "blueprint_version": BLUEPRINT_VERSION,
        "run_id": f"HQBP-{digest[:12]}",
        "config_sha256": digest,
        "runtime_alias": "KMK312",
        "python_version": platform.python_version(),
        "root": str(root_path),
        "user_inputs": values,
        "derived": derived,
        "status": "blueprint_status_only",
    }


def write_frozen_blueprint(frozen: dict[str, Any], root: str | Path) -> Path:
    root_path = Path(root).resolve()
    out = root_path / frozen["user_inputs"]["output_directory"] / frozen["run_id"]
    out.mkdir(parents=True, exist_ok=True)
    payload = dict(frozen)
    payload["created_at_kst"] = "status-only deterministic checkpoint"
    path = out / "frozen_blueprint_config.json"
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if path.is_file() and path.read_text(encoding="utf-8") != rendered:
        raise FileExistsError(f"Frozen blueprint path exists with different content: {path}")
    if not path.is_file():
        path.write_text(rendered, encoding="utf-8")
    return path


def load_stage_registry(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_stage_registry(payload)
    return payload


def validate_stage_registry(payload: dict[str, Any]) -> None:
    stages = payload.get("stages", [])
    ids = [row.get("stage_id") for row in stages]
    expected = [f"HQ-CELL-{index:02d}" for index in range(22)]
    if ids != expected or len(set(ids)) != len(ids):
        raise ValueError("Stage registry must contain unique HQ-CELL-00..21 in order")
    required = {
        "stage_id", "stage_name", "purpose", "input_contract", "output_contract", "enabled", "execution_enabled",
        "status", "applicable_source_family", "implementation_module",
        "validation_evidence", "blocked_by", "related_work_id", "next_gate",
    }
    for row in stages:
        missing = required - set(row)
        if missing:
            raise ValueError(f"{row.get('stage_id')}: missing registry fields {sorted(missing)}")
        if row["status"] not in ALLOWED_STAGE_STATES:
            raise ValueError(f"{row['stage_id']}: unsupported status {row['status']}")
        if row["execution_enabled"]:
            raise ValueError(f"{row['stage_id']}: Blueprint v0.2 cannot enable scientific execution")
        if row["enabled"] and row["stage_id"] not in {"HQ-CELL-00", "HQ-CELL-01", "HQ-CELL-02", "HQ-CELL-03", "HQ-CELL-21"}:
            raise ValueError(f"{row['stage_id']}: only status/control/handoff stages may be enabled")


def stage_view(registry: dict[str, Any], stage_id: str) -> dict[str, Any]:
    matches = [row for row in registry["stages"] if row["stage_id"] == stage_id]
    if len(matches) != 1:
        raise KeyError(stage_id)
    return matches[0]
