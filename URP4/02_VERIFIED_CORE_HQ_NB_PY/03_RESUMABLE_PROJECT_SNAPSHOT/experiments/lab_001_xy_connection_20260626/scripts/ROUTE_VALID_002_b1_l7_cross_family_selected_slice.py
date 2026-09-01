"""ROUTE-VALID-002: B1/L7 confirmed-pair A/B/C selected-slice validation.

Route A: original STEP direct B-rep section/raster.
Route B: controlled tessellation derived from the *same* STEP.
Route C: separately stored paired imported STL through the frozen oriented
non-zero winding primitives, with a documented N40 grid adapter only when
export micro-anisotropy makes the frozen stream's exact-square guard inapplicable.

This is a selected-slice, no-y route audit.  It does not calculate descriptors,
access Excel/LEGACY-PY/y, or alter a source/notebook/module.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import sys
import time
from pathlib import Path
from typing import Any

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
DELIVERABLE = ROOT / "URP4-1_DELIVERABLE"
SCRIPTS = LAB / "scripts"
TABLES = LAB / "reports" / "tables"
RESULT = LAB / "results" / "ROUTE-VALID-002" / "ROUTE-VALID-002-20260729-001"

WORK_ID = "ROUTE-VALID-002_B1_L7_CONFIRMED_PAIR_CROSS_FAMILY_SELECTED_SLICE_VALIDATION_NO_Y"
RUN_ID = "ROUTE-VALID-002-20260729-001"
SETTINGS = "IDX-URP4-1-GEOM-ROUTES / CFG-ROUTEVALID002-B1L7-N40-ZMID-P500P1000-PHASE00 r1"
TARGETS = ("B1", "L7")
RESOLUTIONS = (500, 1000)
SLICE_COUNT = 801
SELECTED_SLICE_INDEX = 400
EXPECTED_SIZE_MM = 40.0
PHASE = "PHASE-00"

ELIGIBILITY = TABLES / "ROUTE-VALID-001-20260729-001_source_eligibility.csv"
PARITY = TABLES / "R09-20260715_stp_stl_metric_parity.csv"
SS7 = SCRIPTS / "STRICT_STEP_007_overlay_trace_execution.py"
PROTECTED_BASELINE = LAB / "results" / "HQ-BLUEPRINT-001" / "PROTECTED_ASSET_BASELINE.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stable_hash(value: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    keys = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def hash_check(path_value: str, expected_hash: str) -> dict[str, object]:
    path = Path(path_value)
    exists = path.is_file()
    observed = sha256_file(path) if exists else ""
    return {
        "path": str(path),
        "exists": exists,
        "expected_sha256": expected_hash.lower(),
        "observed_sha256": observed,
        "hash_match": bool(exists and observed.lower() == expected_hash.lower()),
        "byte_size": path.stat().st_size if exists else "",
    }


def contract_replay() -> dict[str, dict[str, object]]:
    eligibility = {row["model_id"]: row for row in read_csv(ELIGIBILITY)}
    parity = {row["model_id"]: row for row in read_csv(PARITY)}
    out: dict[str, dict[str, object]] = {}
    for model_id in TARGETS:
        prior = eligibility.get(model_id)
        pair = parity.get(model_id)
        if prior is None or pair is None:
            out[model_id] = {"model_id": model_id, "contract_status": "blocked", "reason": "registry row missing"}
            continue
        step = hash_check(str(ROOT / pair["stp_path"]), pair["stp_sha256"])
        stl = hash_check(str(ROOT / pair["stl_path"]), pair["stl_sha256"])
        pass_status = (
            prior["eligibility_status"] == "paired_confirmed"
            and prior["official_route_ac_eligibility"] == "eligible"
            and pair["parity_state"] == "confirmed_metric_parity"
            and step["hash_match"]
            and stl["hash_match"]
        )
        out[model_id] = {
            "model_id": model_id,
            "contract_status": "passed" if pass_status else "blocked",
            "reason": "confirmed pair + registry SHA replay" if pass_status else "identity/status/hash prerequisite failed",
            "eligibility_status": prior["eligibility_status"],
            "official_route_ac_eligibility": prior["official_route_ac_eligibility"],
            "parity_state": pair["parity_state"],
            "stp_path": step["path"],
            "stp_expected_sha256": step["expected_sha256"],
            "stp_observed_sha256": step["observed_sha256"],
            "stp_hash_match": step["hash_match"],
            "stl_path": stl["path"],
            "stl_expected_sha256": stl["expected_sha256"],
            "stl_observed_sha256": stl["observed_sha256"],
            "stl_hash_match": stl["hash_match"],
            "pair_source_note": pair["note"],
            "normalized_domain": "N40 (transient in-memory only)",
            "axis": "z",
            "selected_position": "z-mid = normalized 20 mm",
            "pixel_phase": PHASE,
        }
    return out


def component_hole_counts(mask: np.ndarray) -> tuple[int, int]:
    binary = np.asarray(mask, dtype=np.uint8)
    count, _ = cv2.connectedComponents(binary, connectivity=8)
    components = int(count - 1)
    inverse = (1 - binary).astype(np.uint8)
    bg_count, labels = cv2.connectedComponents(inverse, connectivity=8)
    border_labels = set(np.unique(np.r_[labels[0, :], labels[-1, :], labels[:, 0], labels[:, -1]]).tolist())
    holes = sum(1 for label in range(1, bg_count) if label not in border_labels)
    return components, int(holes)


def route_measurement(mask: np.ndarray, *, model_id: str, route: str, resolution: int, runtime_s: float, extra: dict[str, object]) -> dict[str, object]:
    mask = np.asarray(mask, dtype=bool)
    px_area = (EXPECTED_SIZE_MM / resolution) ** 2
    components, holes = component_hole_counts(mask)
    return {
        "model_id": model_id,
        "route": route,
        "resolution_px": resolution,
        "axis": "z",
        "selected_position": "z-mid",
        "z_mm_normalized": 20.0,
        "pixel_phase": PHASE,
        "pixel_count": int(mask.sum()),
        "area_mm2": float(mask.sum() * px_area),
        "slice_area_profile_scope": "one_selected_zmid_point_not_full_profile",
        "slice_area_profile_mm2": float(mask.sum() * px_area),
        "component_count_diagnostic": components,
        "hole_count_diagnostic": holes,
        "runtime_s": runtime_s,
        **extra,
    }


def comparison(reference: np.ndarray, candidate: np.ndarray, *, model_id: str, comparison_id: str, resolution: int) -> dict[str, object]:
    reference, candidate = np.asarray(reference, dtype=bool), np.asarray(candidate, dtype=bool)
    inter = int(np.logical_and(reference, candidate).sum())
    union = int(np.logical_or(reference, candidate).sum())
    symmetric = int(np.logical_xor(reference, candidate).sum())
    px_area = (EXPECTED_SIZE_MM / resolution) ** 2
    ar, hr = component_hole_counts(reference)
    ac, hc = component_hole_counts(candidate)
    scope = (
        "same_source_STEP_representation_consistency_only_not_imported_STL_validation"
        if comparison_id == "A-B"
        else "confirmed_source_pair_STEP_vs_separately_stored_imported_STL_selected_slice_observation"
    )
    return {
        "model_id": model_id,
        "comparison_id": comparison_id,
        "resolution_px": resolution,
        "comparison_scope": scope,
        "mask_iou": inter / union if union else 1.0,
        "symmetric_difference_pixels": symmetric,
        "symmetric_difference_area_mm2": symmetric * px_area,
        "reference_pixel_count": int(reference.sum()),
        "candidate_pixel_count": int(candidate.sum()),
        "reference_area_mm2": float(reference.sum() * px_area),
        "candidate_area_mm2": float(candidate.sum() * px_area),
        "area_relative_delta": abs(int(reference.sum()) - int(candidate.sum())) / max(int(reference.sum()), 1),
        "reference_component_count_diagnostic": ar,
        "candidate_component_count_diagnostic": ac,
        "reference_hole_count_diagnostic": hr,
        "candidate_hole_count_diagnostic": hc,
        "threshold_policy": "continuous metrics only; no new pass/fail threshold",
    }


def load_step_tools() -> Any:
    spec = importlib.util.spec_from_file_location("route_valid_002_ss7", SS7)
    if spec is None or spec.loader is None:
        raise RuntimeError("STRICT_STEP_007 helper module unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def step_a_b_masks(step_path: Path, model_id: str, resolution: int, tools: Any, sg: Any, ocp: Any) -> tuple[np.ndarray, np.ndarray, dict[str, object], dict[str, object]]:
    """Produce Route A and B from exactly the same STEP and N40 coordinate cube."""
    start_a = time.perf_counter()
    shape = tools._read_step_shape(step_path, ocp)
    cfg = tools.GeometryRouteConfig.from_values(
        input_paths=[str(step_path)], normalize_to_size_mm=EXPECTED_SIZE_MM, allow_stl_to_step_proxy=False
    )
    normalized, scale, source_bbox = tools._normalize_shape(shape, cfg, ocp)
    bbox = tools._shape_bbox(normalized, ocp)
    transform = tools.gp_Trsf()
    transform.SetTranslation(tools.gp_Vec(-bbox[0], -bbox[1], -bbox[2]))
    local = tools.BRepBuilderAPI_Transform(normalized, transform, True).Shape()
    local_bbox = tools._shape_bbox(local, ocp)
    extents = np.array([local_bbox[3] - local_bbox[0], local_bbox[4] - local_bbox[1], local_bbox[5] - local_bbox[2]], dtype=float)
    if np.max(np.abs(extents - EXPECTED_SIZE_MM)) > 1.0e-8:
        raise RuntimeError(f"{model_id} STEP N40 local cube failed: {extents.tolist()}")
    sg.Z_MM = EXPECTED_SIZE_MM / 2.0
    edges = sg.section_edge_sequence([local])
    wires, _ = sg.connect_wires(edges)
    records = [sg.face_record(wire, index) for index, wire in enumerate(wires, start=1)]
    eligible_faces = [record for record in records if record["eligible"] and record["face_build_done"]]
    if not eligible_faces:
        raise RuntimeError(f"{model_id} Route A has no eligible closed B-rep faces")
    mask_a = tools.fmask(sg, eligible_faces, resolution)
    runtime_a = time.perf_counter() - start_a

    start_b = time.perf_counter()
    mesh_cfg = tools.GeometryRouteConfig.from_values(
        input_paths=[str(step_path)], normalize_to_size_mm=None, tessellation_deflection_mm=0.1,
        tessellation_angle_rad=0.35, allow_stl_to_step_proxy=False,
    )
    vertices, faces = tools._shape_to_arrays(local, mesh_cfg, ocp)
    triangles = vertices[faces]
    segments = tools.vectorized_segments(triangles, EXPECTED_SIZE_MM / 2.0)
    mask_b, _ = tools.rasterize_segments_scanline(
        segments, (0.0, 0.0), (EXPECTED_SIZE_MM, EXPECTED_SIZE_MM), resolution, resolution
    )
    runtime_b = time.perf_counter() - start_b
    shared = {
        "source_step_sha256": sha256_file(step_path),
        "source_bbox": source_bbox,
        "normalization_scale": scale,
        "local_analysis_bbox": local_bbox,
        "local_extent_mm": extents.tolist(),
        "section_edge_count": int(edges.Length()),
        "wire_count": len(wires),
        "eligible_face_count": len(eligible_faces),
        "quarantined_wire_count": len(records) - len(eligible_faces),
        "no_heal_rule": "open/noneligible B-rep wires are quarantined; no repair/fill/bridge",
    }
    return mask_a, mask_b.astype(bool), {**shared, "runtime_s": runtime_a}, {**shared, "runtime_s": runtime_b, "controlled_triangle_count": int(len(triangles)), "controlled_segment_count": int(len(segments))}


def imported_c_mask(stl_path: Path, expected_hash: str, model_id: str, resolution: int) -> tuple[np.ndarray, dict[str, object]]:
    if str(DELIVERABLE) not in sys.path:
        sys.path.insert(0, str(DELIVERABLE))
    from urp4.geometry_io.v0_4.imported_winding import (
        ImportedSTLWindingConfig,
        load_imported_stl_triangles,
        oriented_section_z,
        winding_raster,
    )

    config = ImportedSTLWindingConfig(
        pixel_resolution=resolution,
        slice_count=SLICE_COUNT,
        expected_size_mm=EXPECTED_SIZE_MM,
        normalization_mode="uniform_bbox_to_expected",
        axis="z",
        route_id=f"ROUTE-C-IMPORTED-STL-ORIENTED-NONZERO-{model_id}-P{resolution}-ZMID",
        algorithm_revision="ORIENTED_NONZERO_RAW/IMSTL-004/r1",
    )
    triangles, lower, upper, source_hash, normalization = load_imported_stl_triangles(
        stl_path, config, expected_sha256=expected_hash
    )
    extent = np.asarray(upper - lower, dtype=float)
    residual = float(np.max(np.abs(extent - EXPECTED_SIZE_MM)))
    xy_pitch_delta = float(abs(extent[0] - extent[1]))
    if residual > 1.0e-3:
        raise RuntimeError(f"{model_id} imported STL rejected: N40 bbox residual {residual} mm")
    # Use the explicit N40 pixel domain iff the module's bit-exact square pitch
    # precondition cannot be satisfied by the retained export bbox.  This is
    # recorded per output; it is not a global/default policy change.
    z_values = np.linspace(lower[2], upper[2], SLICE_COUNT)
    z_mm = float(z_values[SELECTED_SLICE_INDEX])
    start = time.perf_counter()
    segments, section_diag = oriented_section_z(triangles, z_mm)
    adapter_used = xy_pitch_delta > 1.0e-12
    lower_xy = np.array([0.0, 0.0], dtype=float) if adapter_used else lower[:2]
    upper_xy = np.array([EXPECTED_SIZE_MM, EXPECTED_SIZE_MM], dtype=float) if adapter_used else upper[:2]
    mask, raster_diag = winding_raster(segments, lower_xy=lower_xy, upper_xy=upper_xy, pixels=resolution)
    runtime = time.perf_counter() - start
    meta: dict[str, object] = {
        "source_stl_sha256": source_hash,
        "route_id": config.route_id,
        "algorithm_revision": config.algorithm_revision,
        "slice_index": SELECTED_SLICE_INDEX,
        "z_mm": z_mm,
        "source_bbox_extent_mm": normalization["source_bbox_extent_mm"],
        "analysis_bbox_extent_mm": normalization["analysis_bbox_extent_mm"],
        "analysis_uniform_scale": normalization["analysis_uniform_scale"],
        "bbox_residual_to_N40_mm": residual,
        "xy_extent_delta_mm": xy_pitch_delta,
        "explicit_n40_grid_adapter_used": adapter_used,
        "adapter_precondition": "analysis bbox residual <= 1e-3 mm and xy pitch delta > 1e-12 mm" if adapter_used else "not needed: analysis XY pitches are bit-exact square",
        "pixel_grid_rule": "explicit_normalized_N40_cube_xy_0_to_40mm" if adapter_used else "frozen_imported_winding_analysis_bbox_xy",
        "config_hash": stable_hash({
            "resolution": resolution, "slice_count": SLICE_COUNT, "expected_size_mm": EXPECTED_SIZE_MM,
            "axis": "z", "slice_index": SELECTED_SLICE_INDEX, "adapter_used": adapter_used,
        }),
        "runtime_s": runtime,
        **section_diag,
        **raster_diag,
    }
    return np.asarray(mask, dtype=bool), meta


def save_mask(model_id: str, route: str, resolution: int, mask: np.ndarray) -> dict[str, object]:
    path = RESULT / f"{model_id}_ZMID_P{resolution}_ROUTE_{route}.png"
    if not cv2.imwrite(str(path), np.asarray(mask, dtype=np.uint8) * 255):
        raise RuntimeError(f"cannot write {path}")
    return {"model_id": model_id, "route": route, "resolution_px": resolution, "path": str(path), "sha256": sha256_file(path)}


def protected_file_audit() -> dict[str, bool]:
    baseline = json.loads(PROTECTED_BASELINE.read_text(encoding="utf-8"))
    return {
        asset["alias"] + "::" + asset["path"]: (
            (ROOT / asset["path"]).is_file() and sha256_file(ROOT / asset["path"]) == asset["before_sha256"]
        )
        for asset in baseline["assets"] if asset["asset_kind"] == "file"
    }


def main() -> None:
    if "kmk312" not in str(Path(sys.executable).resolve()).lower() or sys.version_info[:2] != (3, 12):
        raise RuntimeError("ROUTE-VALID-002 requires KMK312 Python 3.12.12")
    for path in (ELIGIBILITY, PARITY, SS7, PROTECTED_BASELINE):
        if not path.is_file():
            raise RuntimeError(f"missing required predecessor input: {path}")
    RESULT.mkdir(parents=True, exist_ok=True)
    contracts = contract_replay()
    contract_rows = list(contracts.values())
    contract_path = TABLES / f"{RUN_ID}_B1_L7_source_contract.csv"
    write_csv(contract_path, contract_rows)
    blocked = [model_id for model_id, row in contracts.items() if row["contract_status"] != "passed"]
    if blocked:
        packet = {"work_id": WORK_ID, "run_id": RUN_ID, "status": "blocked_before_calculation", "blocked_models": blocked, "contract_table": str(contract_path)}
        (RESULT / "BLOCKED_PACKET.json").write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        raise RuntimeError(f"source contract blocked; no images calculated for {blocked}")

    tools = load_step_tools()
    sg = tools.loadsg()
    ocp = tools._ocp_modules()
    measurements: list[dict[str, object]] = []
    comparisons: list[dict[str, object]] = []
    images: list[dict[str, object]] = []
    status: dict[str, dict[str, str]] = {}
    for model_id in TARGETS:
        source = contracts[model_id]
        status[model_id] = {"route_ab": "not_started", "route_ac": "not_started"}
        for resolution in RESOLUTIONS:
            mask_a, mask_b, a_meta, b_meta = step_a_b_masks(Path(str(source["stp_path"])), model_id, resolution, tools, sg, ocp)
            status[model_id]["route_ab"] = "technical_complete"
            images.extend([save_mask(model_id, "A", resolution, mask_a), save_mask(model_id, "B", resolution, mask_b)])
            measurements.extend([
                route_measurement(mask_a, model_id=model_id, route="A", resolution=resolution, runtime_s=float(a_meta.pop("runtime_s")), extra=a_meta),
                route_measurement(mask_b, model_id=model_id, route="B", resolution=resolution, runtime_s=float(b_meta.pop("runtime_s")), extra=b_meta),
            ])
            comparisons.append(comparison(mask_a, mask_b, model_id=model_id, comparison_id="A-B", resolution=resolution))

            # Route C is permitted only after this model's A-B calculation completed.
            mask_c, c_meta = imported_c_mask(Path(str(source["stl_path"])), str(source["stl_expected_sha256"]), model_id, resolution)
            status[model_id]["route_ac"] = "technical_complete"
            images.append(save_mask(model_id, "C", resolution, mask_c))
            measurements.append(route_measurement(mask_c, model_id=model_id, route="C", resolution=resolution, runtime_s=float(c_meta.pop("runtime_s")), extra=c_meta))
            comparisons.append(comparison(mask_a, mask_c, model_id=model_id, comparison_id="A-C", resolution=resolution))

    measurement_path = TABLES / f"{RUN_ID}_route_ABC_measurements.csv"
    comparison_path = TABLES / f"{RUN_ID}_B1_L7_comparisons.csv"
    image_path = TABLES / f"{RUN_ID}_image_hash_registry.csv"
    write_csv(measurement_path, measurements)
    write_csv(comparison_path, comparisons)
    write_csv(image_path, images)
    protected = protected_file_audit()
    summary = {
        "work_id": WORK_ID,
        "run_id": RUN_ID,
        "settings": SETTINGS,
        "status": "completed_B1_L7_selected_slices_only",
        "scope_stop": "C1 not re-executed; B3/L1/F1/T17/STL-only models/full Z801/descriptor/y were not executed.",
        "runtime_executable": str(Path(sys.executable).resolve()),
        "source_contract_table": str(contract_path),
        "source_contract_sha256": sha256_file(contract_path),
        "measurement_table": str(measurement_path),
        "comparison_table": str(comparison_path),
        "image_registry": str(image_path),
        "status_by_model": status,
        "comparison_metrics": comparisons,
        "protected_file_hashes_unchanged": all(protected.values()),
        "protected_file_count": len(protected),
        "interpretation_guardrails": [
            "A-B is same-source STEP representation consistency only, not imported-STL validation.",
            "A-C is a confirmed-pair selected-slice observation only; no new threshold or production-route promotion is made.",
            "Area/mask results do not establish full slice profile, component-population, Angle/Curvature/full-descriptor, Excel/LEGACY-PY, y, training, or inverse-design parity.",
            "No result is generalized to B3/L1, F1, T17, or the 25 STL-only models.",
        ],
    }
    packet_path = RESULT / "ROUTE_VALID_002_PACKET.json"
    packet_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": summary["status"],
        "status_by_model": status,
        "comparison_rows": len(comparisons),
        "packet": str(packet_path),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
