"""ROUTE-VALID-003: F1 STEP-reference pixel-phase/resolution stress test.

This script deliberately has a narrow remit.  It reuses (never regenerates)
the 144 frozen Route-C masks from IMSTL-007 and creates 144 new masks each
for Route A (direct F1 STEP B-rep) and Route B (a controlled tessellation of
that same STEP).  No descriptor, Excel, y, model, or notebook is opened.

The historical F1 raw STL is slightly non-cubic.  Its retained Route-C masks
were made from the documented N40_BBOX_EXACT derivative.  Therefore Route A
and Route B receive the *same, one-time, raw-STL-bbox-derived axis-wise affine
N40 transform*.  The raw STEP/STL coordinate frames must agree before this is
allowed.  There is no ICP, rotation, or route-specific fit-to-bbox operation.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
import os
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.BRepBuilderAPI import BRepBuilderAPI_GTransform
from OCP.GCPnts import GCPnts_QuasiUniformDeflection
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.gp import gp_GTrsf, gp_Mat, gp_Trsf, gp_Vec, gp_XYZ


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
DELIVERABLE = ROOT / "URP4-1_DELIVERABLE"
SCRIPTS = LAB / "scripts"
TABLES = LAB / "reports" / "tables"

WORK_ID = "ROUTE-VALID-003_F1_STEP_REFERENCE_PIXEL_PHASE_AND_RESOLUTION_STRESS_TEST_NO_Y"
RUN_ID = os.environ.get("ROUTE_VALID_003_RUN_ID", "ROUTE-VALID-003-20260729-001")
SETTINGS = "IDX-URP4-1-GEOM-ROUTES / CFG-ROUTEVALID003-F1-COMMON-N40-Z9-P500-750-1000-1500-PHASE4 r1"
RUN = LAB / "runs" / "ROUTE-VALID-003" / RUN_ID
RESULT = LAB / "results" / "ROUTE-VALID-003" / RUN_ID

EXPECTED_SIZE_MM = 40.0
SLICE_COUNT = 801
SELECTED = (0, 1, 100, 200, 400, 600, 700, 799, 800)
BOUNDARY_INDICES = {0, 1, 799, 800}
RESOLUTIONS = (500, 750, 1000, 1500)
PHASES = {"P00": (0.0, 0.0), "P50X": (0.5, 0.0), "P50Y": (0.0, 0.5), "P50XY": (0.5, 0.5)}
COMMON_COORDINATE_TOLERANCE_MM = 1.0e-4
MIN_COMPONENT_AREA_MM2 = 0.0032

ELIGIBILITY = TABLES / "ROUTE-VALID-001-20260729-001_source_eligibility.csv"
PARITY = TABLES / "R09-20260715_stp_stl_metric_parity.csv"
N40_MANIFEST = TABLES / "R09-20260715_n40_canonical_processed_manifest.csv"
IMSTL007_RUN = LAB / "runs" / "I007" / "IMSTL-007-20260728-002"
IMSTL007_RESULT = LAB / "results" / "I007_F1" / "IMSTL-007-20260728-002"
IMSTL007_MEASUREMENTS = TABLES / "IMSTL-007-20260728-002_mask_measurements.csv"
IMSTL008_RESULT = LAB / "results" / "I008_F1" / "IMSTL-008-20260728-002"
RV001_RESULT = LAB / "results" / "ROUTE-VALID-001" / "ROUTE-VALID-001-20260729-001"
RV002_RESULT = LAB / "results" / "ROUTE-VALID-002" / "ROUTE-VALID-002-20260729-001"
SS7 = SCRIPTS / "STRICT_STEP_007_overlay_trace_execution.py"
PROTECTED_BASELINE = LAB / "results" / "HQ-BLUEPRINT-001" / "PROTECTED_ASSET_BASELINE.json"
ADAPTER_PROBE_RESULT = LAB / "results" / "ROUTE-VALID-003A" / "ROUTE-VALID-003A-20260729-001" / "PRODUCER_PACKET.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stable_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


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


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def packed_mask_sha256(mask: np.ndarray) -> str:
    packed = np.packbits(np.asarray(mask, dtype=np.uint8).reshape(-1), bitorder="big")
    return hashlib.sha256(packed.tobytes()).hexdigest()


def hash_check(path: Path, expected: str) -> dict[str, object]:
    exists = path.is_file()
    observed = sha256_file(path) if exists else ""
    return {
        "path": relative(path) if exists else str(path),
        "exists": exists,
        "expected_sha256": expected.lower(),
        "observed_sha256": observed,
        "hash_match": bool(exists and observed.lower() == expected.lower()),
        "size_bytes": path.stat().st_size if exists else "",
    }


def load_step_tools() -> Any:
    spec = importlib.util.spec_from_file_location("route_valid_003_ss7", SS7)
    if spec is None or spec.loader is None:
        raise RuntimeError("STRICT_STEP_007 helper module unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def filtered_topology(mask: np.ndarray, resolution: int) -> dict[str, int]:
    binary = np.asarray(mask, dtype=np.uint8)
    raw_count, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
    raw_components = int(raw_count - 1)
    min_pixels = max(1, int(math.ceil(MIN_COMPONENT_AREA_MM2 / ((EXPECTED_SIZE_MM / resolution) ** 2))))
    filtered = np.zeros_like(binary)
    kept = 0
    for label in range(1, raw_count):
        if int(stats[label, cv2.CC_STAT_AREA]) >= min_pixels:
            filtered[labels == label] = 1
            kept += 1
    inverse = (1 - filtered).astype(np.uint8)
    bg_count, bg_labels = cv2.connectedComponents(inverse, connectivity=8)
    border = set(np.unique(np.r_[bg_labels[0, :], bg_labels[-1, :], bg_labels[:, 0], bg_labels[:, -1]]).tolist())
    holes = sum(1 for label in range(1, bg_count) if label not in border)
    return {
        "component_count_raw": raw_components,
        "component_count_filtered": int(kept),
        "hole_count_filtered": int(holes),
        "min_component_pixels": min_pixels,
    }


def boundary_band(mask_a: np.ndarray, mask_b: np.ndarray, radius: int = 2) -> np.ndarray:
    a = np.asarray(mask_a, dtype=np.uint8)
    b = np.asarray(mask_b, dtype=np.uint8)
    kernel = np.ones((2 * radius + 1, 2 * radius + 1), dtype=np.uint8)
    union = np.maximum(a, b)
    boundary = cv2.morphologyEx(union, cv2.MORPH_GRADIENT, kernel)
    return boundary.astype(bool)


def compare_masks(reference: np.ndarray, candidate: np.ndarray, *, comparison_id: str, slice_index: int, resolution: int, phase_id: str) -> dict[str, object]:
    a, b = np.asarray(reference, dtype=bool), np.asarray(candidate, dtype=bool)
    inter = int(np.logical_and(a, b).sum())
    union = int(np.logical_or(a, b).sum())
    diff = np.logical_xor(a, b)
    diff_px = int(diff.sum())
    px_area = (EXPECTED_SIZE_MM / resolution) ** 2
    band = boundary_band(a, b)
    explained = 1.0 if diff_px == 0 else float(np.logical_and(diff, band).sum() / diff_px)
    ta, tb = filtered_topology(a, resolution), filtered_topology(b, resolution)
    topology_only = diff_px == 0 and (
        ta["component_count_filtered"] != tb["component_count_filtered"] or ta["hole_count_filtered"] != tb["hole_count_filtered"]
    )
    if diff_px == 0 and not topology_only:
        primary = "no_observed_mask_difference"
    elif topology_only:
        primary = "component_population_only"
    elif explained == 1.0:
        primary = "boundary_raster_discretization"
    else:
        primary = "interior_geometry_difference"
    return {
        "run_id": RUN_ID,
        "model_id": "F1",
        "comparison_id": comparison_id,
        "slice_index": slice_index,
        "slice_group": "boundary" if slice_index in BOUNDARY_INDICES else "interior",
        "resolution_px": resolution,
        "phase_id": phase_id,
        "mask_iou": inter / union if union else 1.0,
        "symmetric_difference_pixels": diff_px,
        "symmetric_difference_area_mm2": float(diff_px * px_area),
        "area_relative_delta": abs(int(a.sum()) - int(b.sum())) / max(int(a.sum()), 1),
        "reference_solid_pixels": int(a.sum()),
        "candidate_solid_pixels": int(b.sum()),
        "reference_area_mm2": float(a.sum() * px_area),
        "candidate_area_mm2": float(b.sum() * px_area),
        "boundary_band_explained_fraction": explained,
        "reference_component_count_raw": ta["component_count_raw"],
        "candidate_component_count_raw": tb["component_count_raw"],
        "reference_component_count_filtered": ta["component_count_filtered"],
        "candidate_component_count_filtered": tb["component_count_filtered"],
        "reference_hole_count_filtered": ta["hole_count_filtered"],
        "candidate_hole_count_filtered": tb["hole_count_filtered"],
        "primary_difference_classification": primary,
        "route_relationship": "same_source_representation_difference" if comparison_id == "A-B" and diff_px else ("paired_STL_route_difference" if comparison_id == "A-C" and diff_px else "none_observed"),
        "spatial_classification": "boundary_raster_discretization" if diff_px and explained == 1.0 else ("interior_geometry_difference" if diff_px else "none_observed"),
        "component_population_only": topology_only,
        "threshold_policy": "continuous metrics only; no new parity threshold",
    }


def build_output_manifest(root: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.name != "OUTPUT_MANIFEST.csv":
            rows.append({"relative_path": path.relative_to(root).as_posix(), "size_bytes": path.stat().st_size, "sha256": sha256_file(path)})
    return rows


def protected_file_audit() -> dict[str, bool]:
    baseline = json.loads(PROTECTED_BASELINE.read_text(encoding="utf-8"))
    return {
        asset["alias"] + "::" + asset["path"]: (
            (ROOT / asset["path"]).is_file() and sha256_file(ROOT / asset["path"]) == asset["before_sha256"]
        )
        for asset in baseline["assets"]
        if asset["asset_kind"] == "file"
    }


def common_contract_and_evidence() -> tuple[dict[str, object], list[dict[str, object]], dict[tuple[int, int, str], tuple[np.ndarray, dict[str, object]]]]:
    """Audit every immutable predecessor before creating any new A/B mask."""
    if str(DELIVERABLE) not in sys.path:
        sys.path.insert(0, str(DELIVERABLE))
    from urp4.descriptor_service.v0_1.geometry import geometry_bounds, load_binary_stl_vertices

    for required in (ELIGIBILITY, PARITY, N40_MANIFEST, IMSTL007_RUN / "CONTRACT.json", IMSTL007_RUN / "OUTPUT_MANIFEST.csv", IMSTL007_MEASUREMENTS, IMSTL007_RESULT / "INDEPENDENT_QA.json", IMSTL008_RESULT / "INDEPENDENT_QA.json", RV001_RESULT / "INDEPENDENT_QA.json", RV002_RESULT / "INDEPENDENT_QA.json", SS7, PROTECTED_BASELINE, ADAPTER_PROBE_RESULT):
        if not required.is_file():
            raise RuntimeError(f"missing required predecessor input: {required}")

    eligibility = {row["model_id"]: row for row in read_csv(ELIGIBILITY)}.get("F1")
    parity = {row["model_id"]: row for row in read_csv(PARITY)}.get("F1")
    n40 = {row["model_id"]: row for row in read_csv(N40_MANIFEST)}.get("F1")
    if eligibility is None or parity is None or n40 is None:
        raise RuntimeError("F1 missing eligibility, parity, or N40-manifest row")
    step = ROOT / parity["stp_path"]
    stl = ROOT / parity["stl_path"]
    processed = ROOT / n40["processed_file"]
    rows: list[dict[str, object]] = []
    for alias, path, expected in (("F1_original_STEP", step, parity["stp_sha256"]), ("F1_paired_imported_raw_STL", stl, parity["stl_sha256"]), ("F1_N40_processed_STL", processed, n40["processed_sha256"])):
        result = hash_check(path, expected)
        result.update({"evidence_alias": alias, "evidence_group": "source_geometry", "status": "confirmed" if result["hash_match"] else "unresolved"})
        rows.append(result)

    if not (eligibility["eligibility_status"] == "paired_confirmed" and eligibility["official_route_ac_eligibility"] == "eligible" and parity["parity_state"] == "confirmed_metric_parity"):
        raise RuntimeError("F1 is not an eligible confirmed STEP/STL source pair")
    if not all(bool(row["hash_match"]) for row in rows):
        raise RuntimeError("F1 source hash mismatch")
    if n40["source_sha256"].lower() != parity["stl_sha256"].lower():
        raise RuntimeError("N40 processed F1 does not lineage-match paired imported raw STL")

    tools = load_step_tools()
    ocp = tools._ocp_modules()
    step_shape = tools._read_step_shape(step, ocp)
    step_bbox = np.asarray(tools._shape_bbox(step_shape, ocp), dtype=float)
    raw_triangles = load_binary_stl_vertices(stl, expected_sha256=parity["stl_sha256"])
    stl_min, stl_max = geometry_bounds(raw_triangles)
    step_min, step_max = step_bbox[:3], step_bbox[3:]
    coordinate_residual = float(max(np.max(np.abs(step_min - stl_min)), np.max(np.abs(step_max - stl_max))))
    if coordinate_residual > COMMON_COORDINATE_TOLERANCE_MM:
        raise RuntimeError(f"F1 STEP/STL coordinate frames fail common-transform identity audit: {coordinate_residual} mm")
    scale = EXPECTED_SIZE_MM / (stl_max - stl_min)
    translation = -stl_min * scale
    rows.append({
        "evidence_alias": "F1_STEP_STL_raw_coordinate_frame",
        "evidence_group": "source_identity_crosswalk",
        "status": "confirmed",
        "step_bbox_min_mm": step_min.tolist(), "step_bbox_max_mm": step_max.tolist(),
        "stl_bbox_min_mm": stl_min.tolist(), "stl_bbox_max_mm": stl_max.tolist(),
        "max_bbox_coordinate_residual_mm": coordinate_residual,
        "identity_audit_tolerance_mm": COMMON_COORDINATE_TOLERANCE_MM,
        "common_transform": "axis-wise affine from paired raw STL bbox; applied identically to STEP Route A/B",
        "scale_xyz": scale.tolist(), "translation_xyz_mm": translation.tolist(),
        "route_specific_fit": False,
    })

    i007_contract = json.loads((IMSTL007_RUN / "CONTRACT.json").read_text(encoding="utf-8"))
    i007_phases = {str(key): tuple(float(value) for value in values) for key, values in dict(i007_contract["phases"]).items()}
    if tuple(i007_contract["selected_slice_indices"]) != SELECTED or tuple(i007_contract["resolutions_px"]) != RESOLUTIONS or i007_phases != PHASES:
        raise RuntimeError("IMSTL-007 selected-slice/resolution/phase contract mismatch")
    if i007_contract["source"]["sha256"].lower() != n40["processed_sha256"].lower():
        raise RuntimeError("IMSTL-007 Route C source differs from canonical F1 N40 derivative")
    i007_manifest = {row["relative_path"]: row for row in read_csv(IMSTL007_RUN / "OUTPUT_MANIFEST.csv")}
    i007_measurements = read_csv(IMSTL007_MEASUREMENTS)
    if len(i007_measurements) != 144 or len(i007_manifest) != 145:
        raise RuntimeError("IMSTL-007 frozen Route C manifest/measurement count mismatch")
    from urp4.geometry_io.v0_4.imported_winding import mask_packedbits_sha256
    c_masks: dict[tuple[int, int, str], tuple[np.ndarray, dict[str, object]]] = {}
    for row in i007_measurements:
        key = (int(row["slice_index"]), int(row["resolution_px"]), str(row["phase_id"]))
        path = ROOT / row["image_path"]
        rel_in_run = path.resolve().relative_to(IMSTL007_RUN.resolve()).as_posix()
        manifest = i007_manifest.get(rel_in_run)
        image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
        image_ok = image is not None
        mask = np.asarray(image > 0, dtype=bool) if image_ok else np.zeros((1, 1), dtype=bool)
        png_hash = sha256_file(path) if image_ok else ""
        packed_hash = mask_packedbits_sha256(mask) if image_ok else ""
        valid = bool(
            image_ok and manifest is not None and png_hash == manifest["sha256"] and packed_hash == row["mask_packedbits_sha256"]
            and int(mask.sum()) == int(row["solid_pixels"])
        )
        if not valid or key in c_masks:
            raise RuntimeError(f"IMSTL-007 frozen Route C identity mismatch: {key}")
        meta = {
            "run_id": RUN_ID, "model_id": "F1", "route": "C", "reused": True,
            "reused_from_run_id": "IMSTL-007-20260728-002", "reused_from_image_path": row["image_path"],
            "slice_index": key[0], "resolution_px": key[1], "phase_id": key[2], "z_mm": float(row["z_mm"]),
            "phase_x_pixel": float(row["phase_x_pixel"]), "phase_y_pixel": float(row["phase_y_pixel"]),
            "phase_x_mm": float(row["phase_x_mm"]), "phase_y_mm": float(row["phase_y_mm"]),
            "raster_bounds_mm": "[0,0] to [40,40]", "solid_pixels": int(mask.sum()), "area_mm2": float(row["area_mm2"]),
            "component_count_raw": int(row["component_count_raw"]), "component_count_filtered": int(row["component_count_filtered"]),
            "hole_count_filtered": int(row["hole_count_filtered"]),
            "mask_packedbits_sha256": packed_hash, "png_sha256": png_hash,
            "source_path": relative(processed), "source_sha256": n40["processed_sha256"],
            "config_hash": stable_hash(i007_contract), "runtime_s": "reused_no_recompute", "warning": "",
        }
        c_masks[key] = (mask, meta)
    if len(c_masks) != 144:
        raise RuntimeError("IMSTL-007 Route C did not provide exactly 144 unique masks")
    rows.append({"evidence_alias": "IMSTL007_frozen_route_C_144", "evidence_group": "frozen_mask_replay", "status": "confirmed", "measurement_rows": len(i007_measurements), "manifest_rows": len(i007_manifest), "reused_mask_count": len(c_masks), "source_hash": i007_contract["source"]["sha256"], "recompute_forbidden": True})
    for alias, path in (("IMSTL007_independent_QA", IMSTL007_RESULT / "INDEPENDENT_QA.json"), ("IMSTL008_independent_QA", IMSTL008_RESULT / "INDEPENDENT_QA.json"), ("ROUTE_VALID_001_independent_QA", RV001_RESULT / "INDEPENDENT_QA.json"), ("ROUTE_VALID_002_independent_QA", RV002_RESULT / "INDEPENDENT_QA.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        status = str(payload.get("status", payload.get("checks", {}).get("status", ""))).lower()
        accepted = status in {"passed", "pass"}
        if not accepted:
            raise RuntimeError(f"predecessor QA not accepted: {alias}")
        rows.append({"evidence_alias": alias, "evidence_group": "accepted_predecessor", "status": "confirmed", "path": relative(path), "sha256": sha256_file(path), "qa_status": status})
    adapter_probe = json.loads(ADAPTER_PROBE_RESULT.read_text(encoding="utf-8"))
    adapter_ok = (
        adapter_probe.get("status") == "completed"
        and int(adapter_probe.get("case_count", 0)) == 12
        and float(adapter_probe.get("min_iou", 0.0)) == 1.0
        and float(adapter_probe.get("max_area_delta", math.inf)) == 0.0
        and int(adapter_probe.get("max_odd_rows", -1)) == 0
    )
    if not adapter_ok:
        raise RuntimeError("direct-B-rep curve-raster adapter probe is not an exact accepted replay")
    rows.append({"evidence_alias": "ROUTE_VALID_003A_direct_BRep_curve_adapter", "evidence_group": "implementation_adapter_probe", "status": "confirmed", "path": relative(ADAPTER_PROBE_RESULT), "sha256": sha256_file(ADAPTER_PROBE_RESULT), "exact_classifier_cases": 12, "min_iou": adapter_probe["min_iou"], "max_area_delta": adapter_probe["max_area_delta"], "max_odd_rows": adapter_probe["max_odd_rows"]})

    z_values = np.linspace(0.0, EXPECTED_SIZE_MM, SLICE_COUNT)
    z_values[0] = np.nextafter(0.0, EXPECTED_SIZE_MM)
    z_values[-1] = np.nextafter(EXPECTED_SIZE_MM, 0.0)
    contract = {
        "work_id": WORK_ID, "run_id": RUN_ID, "settings_address": SETTINGS,
        "runtime": "KMK312 / Python 3.12.12", "model_id": "F1", "family": "F",
        "routes": {"A": "original STEP direct B-rep", "B": "controlled tessellation from same original STEP", "C": "reused frozen separately stored paired imported STL masks"},
        "analysis_domain_mm": [40.0, 40.0, 40.0], "axis": "z", "slice_count": SLICE_COUNT,
        "selected_slice_indices": list(SELECTED), "selected_z_mm": {str(index): float(z_values[index]) for index in SELECTED},
        "resolutions_px": list(RESOLUTIONS), "phases_pixel": PHASES,
        "pixel_center_convention": "same as IMSTL-007; phase is physical geometry/segment translation before unchanged raster", "raster_bounds_xy_mm": [[0.0, 0.0], [40.0, 40.0]],
        "common_transform": {"transform_id": "F1-RAW-STL-BBOX-AXISWISE-N40-COMMON-r1", "type": "axis-wise_affine", "basis": "paired raw imported STL bbox after confirmed STEP/STL coordinate-frame audit", "scale_xyz": scale.tolist(), "translation_xyz_mm": translation.tolist(), "identity_audit_max_residual_mm": coordinate_residual, "identity_audit_tolerance_mm": COMMON_COORDINATE_TOLERANCE_MM, "applied_to": ["Route A", "Route B"], "Route_C_status": "already N40 derivative from same raw STL transform", "forbidden": ["ICP", "rotation", "route-specific bbox fit", "independent alignment"]},
        "route_c_reuse": {"run_id": "IMSTL-007-20260728-002", "mask_count": 144, "mask_recompute": False, "source_sha256": n40["processed_sha256"]},
        "scope_locks": ["no F1 full STEP Z801", "no IMSTL-007 Route C recompute", "no IMSTL-008 recompute", "no other model", "no descriptor/excel/y/training/NB work"],
    }
    return contract, rows, c_masks


def common_affine_step(step_path: Path, *, scale: np.ndarray, translation: np.ndarray, tools: Any, ocp: Any) -> tuple[Any, dict[str, object]]:
    source = tools._read_step_shape(step_path, ocp)
    g = gp_GTrsf()
    g.SetVectorialPart(gp_Mat(float(scale[0]), 0.0, 0.0, 0.0, float(scale[1]), 0.0, 0.0, 0.0, float(scale[2])))
    g.SetTranslationPart(gp_XYZ(float(translation[0]), float(translation[1]), float(translation[2])))
    transformed = BRepBuilderAPI_GTransform(source, g, True).Shape()
    bbox = np.asarray(tools._shape_bbox(transformed, ocp), dtype=float)
    return transformed, {"step_common_affine_bbox_min_mm": bbox[:3].tolist(), "step_common_affine_bbox_max_mm": bbox[3:].tolist(), "step_common_affine_bbox_extent_mm": (bbox[3:] - bbox[:3]).tolist(), "step_common_affine_bbox_outside_N40_mm": float(max(np.max(np.maximum(-bbox[:3], 0.0)), np.max(np.maximum(bbox[3:] - EXPECTED_SIZE_MM, 0.0))))}


def sample_brep_section_curves(wires: list[Any], *, deflection_mm: float) -> tuple[np.ndarray, dict[str, object]]:
    """Sample exact B-rep section curves, not a 3-D controlled tessellation.

    The adapter was checked against 12 preserved slow BRepClassifier masks in
    ROUTE-VALID-003A before being allowed to calculate the full F1 grid.
    """
    pieces: list[np.ndarray] = []
    point_count = 0
    fallback_edges = 0
    for wire in wires:
        explorer = TopExp_Explorer(wire, TopAbs_EDGE)
        while explorer.More():
            curve = BRepAdaptor_Curve(TopoDS.Edge_s(explorer.Current()))
            sampler = GCPnts_QuasiUniformDeflection(curve, deflection_mm, curve.FirstParameter(), curve.LastParameter())
            if sampler.IsDone() and sampler.NbPoints() >= 2:
                points = np.asarray([(float(sampler.Value(index).X()), float(sampler.Value(index).Y())) for index in range(1, sampler.NbPoints() + 1)], dtype=float)
            else:
                fallback_edges += 1
                first, last = curve.Value(curve.FirstParameter()), curve.Value(curve.LastParameter())
                points = np.asarray([(float(first.X()), float(first.Y())), (float(last.X()), float(last.Y()))], dtype=float)
            point_count += len(points)
            if len(points) >= 2:
                pieces.append(np.column_stack((points[:-1], points[1:])))
            explorer.Next()
    segments = np.vstack(pieces) if pieces else np.empty((0, 4), dtype=float)
    return segments, {"curve_sample_point_count": int(point_count), "curve_sample_segment_count": int(len(segments)), "curve_sampling_fallback_edge_count": int(fallback_edges)}


def even_odd_pixel_center_raster(segments: np.ndarray, resolution: int) -> tuple[np.ndarray, dict[str, object]]:
    """Fill direct-B-rep section curves using an even-odd pixel-centre scanline."""
    mask = np.zeros((resolution, resolution), dtype=bool)
    segment = np.asarray(segments, dtype=float)
    if len(segment) == 0:
        return mask, {"odd_intersection_row_count": 0, "filled_interval_count": 0}
    pixel = EXPECTED_SIZE_MM / resolution
    x1, y1, x2, y2 = segment.T
    keep = np.abs(y2 - y1) > 1.0e-12
    x1, y1, x2, y2 = x1[keep], y1[keep], x2[keep], y2[keep]
    low, high = np.minimum(y1, y2), np.maximum(y1, y2)
    start = np.floor((EXPECTED_SIZE_MM - high) / pixel - 0.5).astype(int) + 1
    stop = np.floor((EXPECTED_SIZE_MM - low) / pixel - 0.5).astype(int)
    start = np.clip(start, 0, resolution - 1); stop = np.clip(stop, -1, resolution - 1)
    counts = np.maximum(0, stop - start + 1); valid = counts > 0
    start, counts, x1, y1, x2, y2 = start[valid], counts[valid], x1[valid], y1[valid], x2[valid], y2[valid]
    if not len(counts):
        return mask, {"odd_intersection_row_count": 0, "filled_interval_count": 0}
    offsets = np.repeat(np.cumsum(counts) - counts, counts)
    rows = np.repeat(start, counts) + (np.arange(int(counts.sum())) - offsets)
    segment_index = np.repeat(np.arange(len(counts)), counts)
    yy = EXPECTED_SIZE_MM - (rows + 0.5) * pixel
    xs = x1[segment_index] + (yy - y1[segment_index]) * (x2[segment_index] - x1[segment_index]) / (y2[segment_index] - y1[segment_index])
    order = np.lexsort((xs, rows)); rows, xs = rows[order], xs[order]
    starts = np.r_[0, np.flatnonzero(np.diff(rows)) + 1]; stops = np.r_[starts[1:], len(rows)]
    odd_rows = 0; interval_count = 0
    for left_index, right_index in zip(starts.tolist(), stops.tolist(), strict=True):
        row = int(rows[left_index]); intersections = np.sort(xs[left_index:right_index])
        if len(intersections) % 2:
            odd_rows += 1
            intersections = intersections[:-1]
        for left, right in zip(intersections[0::2], intersections[1::2], strict=True):
            c0 = max(0, min(resolution - 1, int(math.ceil(left / pixel - 0.5))))
            c1 = max(0, min(resolution - 1, int(math.floor(right / pixel - 0.5))))
            if c1 >= c0:
                mask[row, c0:c1 + 1] ^= True
                interval_count += 1
    return mask, {"odd_intersection_row_count": int(odd_rows), "filled_interval_count": int(interval_count)}


def direct_brep_mask(shape: Any, *, z_mm: float, resolution: int, phase_x_mm: float, phase_y_mm: float, tools: Any, sg: Any) -> tuple[np.ndarray, dict[str, object]]:
    started = time.perf_counter()
    if phase_x_mm or phase_y_mm:
        shift = gp_Trsf(); shift.SetTranslation(gp_Vec(phase_x_mm, phase_y_mm, 0.0))
        local = tools.BRepBuilderAPI_Transform(shape, shift, True).Shape()
    else:
        local = shape
    sg.Z_MM = z_mm
    edges = sg.section_edge_sequence([local])
    wires, _ = sg.connect_wires(edges)
    records = [sg.face_record(wire, index) for index, wire in enumerate(wires, start=1)]
    eligible = [record for record in records if record["eligible"] and record["face_build_done"]]
    pixel_size = EXPECTED_SIZE_MM / resolution
    segments, sampling = sample_brep_section_curves([wires[int(record["wire_index"]) - 1] for record in eligible], deflection_mm=pixel_size / 2.0)
    mask, raster = even_odd_pixel_center_raster(segments, resolution)
    return np.asarray(mask, dtype=bool), {"section_edge_count": int(edges.Length()), "wire_count": len(wires), "eligible_face_count": len(eligible), "quarantined_wire_count": len(records) - len(eligible), "no_heal_rule": "open/noneligible B-rep wires quarantined; no repair/fill/bridge", "direct_brep_rasterizer": "exact_section_curve_sampling_even_odd_pixel_center", "curve_deflection_mm": pixel_size / 2.0, "runtime_s": time.perf_counter() - started, **sampling, **raster}


def controlled_tess_mask(triangles: np.ndarray, *, z_mm: float, resolution: int, phase_x_mm: float, phase_y_mm: float, tools: Any) -> tuple[np.ndarray, dict[str, object]]:
    started = time.perf_counter()
    segments = np.asarray(tools.vectorized_segments(triangles, z_mm), dtype=float)
    if len(segments):
        segments = segments.copy()
        segments[:, [0, 2]] += phase_x_mm
        segments[:, [1, 3]] += phase_y_mm
    mask, diag = tools.rasterize_segments_scanline(segments, (0.0, 0.0), (EXPECTED_SIZE_MM, EXPECTED_SIZE_MM), resolution, resolution)
    return np.asarray(mask, dtype=bool), {"controlled_triangle_count": int(len(triangles)), "controlled_segment_count": int(len(segments)), "runtime_s": time.perf_counter() - started, **diag}


def mask_path(route: str, resolution: int, phase_id: str, slice_index: int) -> Path:
    return RUN / "masks" / f"Route_{route}" / f"P{resolution}" / phase_id / f"F1_z{slice_index:04d}.png"


def write_mask(path: Path, mask: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise RuntimeError(f"refuse to overwrite route mask: {path}")
    if not cv2.imwrite(str(path), np.asarray(mask, dtype=np.uint8) * 255):
        raise RuntimeError(f"cannot write {path}")


def metric_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    numeric = ("mask_iou", "symmetric_difference_pixels", "symmetric_difference_area_mm2", "area_relative_delta", "boundary_band_explained_fraction")
    groupings = {
        "overall": lambda r: (str(r["comparison_id"]),),
        "slice": lambda r: (str(r["comparison_id"]), int(r["slice_index"])),
        "resolution": lambda r: (str(r["comparison_id"]), int(r["resolution_px"])),
        "phase": lambda r: (str(r["comparison_id"]), str(r["phase_id"])),
        "slice_group": lambda r: (str(r["comparison_id"]), str(r["slice_group"])),
    }
    for grouping, key_fn in groupings.items():
        groups: dict[tuple[object, ...], list[dict[str, object]]] = defaultdict(list)
        for row in rows:
            groups[key_fn(row)].append(row)
        for key, group in sorted(groups.items(), key=lambda item: tuple(map(str, item[0]))):
            base: dict[str, object] = {"summary_group": grouping, "comparison_id": key[0], "group_key": "|".join(map(str, key[1:])), "case_count": len(group)}
            for field in numeric:
                values = np.asarray([float(row[field]) for row in group], dtype=float)
                base[field + "_min"] = float(values.min())
                base[field + "_median"] = float(np.median(values))
                base[field + "_max"] = float(values.max())
            base["all_boundary_explained_exact"] = all(float(row["boundary_band_explained_fraction"]) == 1.0 for row in group if int(row["symmetric_difference_pixels"]) > 0)
            out.append(base)
    return out


def worst_case_figures(masks: dict[tuple[int, int, str], dict[str, np.ndarray]], comparisons: list[dict[str, object]]) -> list[dict[str, object]]:
    figures: list[dict[str, object]] = []
    for comparison_id in ("A-B", "A-C"):
        ranked = sorted((row for row in comparisons if row["comparison_id"] == comparison_id), key=lambda row: (float(row["mask_iou"]), -int(row["symmetric_difference_pixels"]), int(row["slice_index"]), int(row["resolution_px"]), str(row["phase_id"])))[:6]
        for rank, row in enumerate(ranked, start=1):
            key = (int(row["slice_index"]), int(row["resolution_px"]), str(row["phase_id"]))
            bank = masks[key]
            a, b, c = bank["A"], bank["B"], bank["C"]
            left, right = (a, b) if comparison_id == "A-B" else (a, c)
            diff = np.logical_xor(left, right)
            def tile(mask: np.ndarray) -> np.ndarray:
                return np.repeat(np.repeat(mask.astype(np.uint8) * 255, 1, axis=0), 1, axis=1)
            diff_rgb = np.zeros((*diff.shape, 3), dtype=np.uint8)
            diff_rgb[np.logical_and(left, ~right)] = (0, 0, 255)
            diff_rgb[np.logical_and(~left, right)] = (255, 255, 0)
            panels = [cv2.cvtColor(tile(a), cv2.COLOR_GRAY2BGR), cv2.cvtColor(tile(b), cv2.COLOR_GRAY2BGR), cv2.cvtColor(tile(c), cv2.COLOR_GRAY2BGR), diff_rgb]
            target_h = 360
            panels = [cv2.resize(panel, (target_h, target_h), interpolation=cv2.INTER_NEAREST) for panel in panels]
            sheet = np.hstack(panels)
            labels = ("Route A", "Route B", "Route C reused", comparison_id + " diff")
            for idx, label in enumerate(labels):
                cv2.putText(sheet, label, (idx * target_h + 8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 1, cv2.LINE_AA)
            path = RESULT / "figures" / f"{comparison_id.replace('-', '')}_worst_{rank:02d}_z{key[0]:04d}_P{key[1]}_{key[2]}.png"
            path.parent.mkdir(parents=True, exist_ok=True)
            if not cv2.imwrite(str(path), sheet):
                raise RuntimeError(f"cannot write worst-case figure {path}")
            figures.append({"comparison_id": comparison_id, "rank": rank, "slice_index": key[0], "resolution_px": key[1], "phase_id": key[2], "mask_iou": row["mask_iou"], "symmetric_difference_pixels": row["symmetric_difference_pixels"], "primary_difference_classification": row["primary_difference_classification"], "figure_path": relative(path), "figure_sha256": sha256_file(path), "route_A_mask": relative(mask_path("A", key[1], key[2], key[0])), "route_B_mask": relative(mask_path("B", key[1], key[2], key[0])), "route_C_reused_mask": row["route_C_reused_mask_path"]})
    return figures


def main() -> None:
    if "kmk312" not in str(Path(sys.executable).resolve()).lower() or sys.version_info[:2] != (3, 12):
        raise RuntimeError("ROUTE-VALID-003 requires KMK312 Python 3.12.12")
    if RUN.exists() or RESULT.exists():
        raise RuntimeError(f"run/result already exists; refuse overwrite: {RUN_ID}")
    contract, evidence_rows, c_masks = common_contract_and_evidence()
    RUN.mkdir(parents=True)
    RESULT.mkdir(parents=True)
    write_json(RUN / "COMMON_RASTER_CONTRACT.json", contract)
    write_json(RESULT / "COMMON_RASTER_CONTRACT.json", contract)
    evidence_path = TABLES / f"{RUN_ID}_source_evidence_replay.csv"
    write_csv(evidence_path, evidence_rows)

    tools = load_step_tools()
    sg = tools.loadsg()
    ocp = tools._ocp_modules()
    parity = {row["model_id"]: row for row in read_csv(PARITY)}["F1"]
    step_path = ROOT / parity["stp_path"]
    raw_stl_path = ROOT / parity["stl_path"]
    # The single common transform derives from retained raw STL bounds, whose
    # coordinate frame was just checked against the original STEP.  It is not
    # fitted to any Route-A/B output.
    source_row = next(row for row in evidence_rows if row.get("evidence_alias") == "F1_STEP_STL_raw_coordinate_frame")
    scale = np.asarray(source_row["scale_xyz"], dtype=float)
    translation = np.asarray(source_row["translation_xyz_mm"], dtype=float)
    step_shape, step_meta = common_affine_step(step_path, scale=scale, translation=translation, tools=tools, ocp=ocp)
    mesh_cfg = tools.GeometryRouteConfig.from_values(input_paths=[str(step_path)], normalize_to_size_mm=None, tessellation_deflection_mm=0.1, tessellation_angle_rad=0.35, allow_stl_to_step_proxy=False)
    vertices, faces = tools._shape_to_arrays(step_shape, mesh_cfg, ocp)
    triangles = vertices[faces]
    z_values = np.linspace(0.0, EXPECTED_SIZE_MM, SLICE_COUNT)
    z_values[0] = np.nextafter(0.0, EXPECTED_SIZE_MM)
    z_values[-1] = np.nextafter(EXPECTED_SIZE_MM, 0.0)
    config_hash = stable_hash(contract)
    measurements: list[dict[str, object]] = []
    route_a_registry: list[dict[str, object]] = []
    route_b_registry: list[dict[str, object]] = []
    route_c_registry: list[dict[str, object]] = []
    masks: dict[tuple[int, int, str], dict[str, np.ndarray]] = {}
    started = time.perf_counter()
    for index in SELECTED:
        z_mm = float(z_values[index])
        for resolution in RESOLUTIONS:
            pixel_size = EXPECTED_SIZE_MM / resolution
            for phase_id, (phase_x, phase_y) in PHASES.items():
                key = (index, resolution, phase_id)
                phase_x_mm, phase_y_mm = phase_x * pixel_size, phase_y * pixel_size
                mask_a, meta_a = direct_brep_mask(step_shape, z_mm=z_mm, resolution=resolution, phase_x_mm=phase_x_mm, phase_y_mm=phase_y_mm, tools=tools, sg=sg)
                mask_b, meta_b = controlled_tess_mask(triangles, z_mm=z_mm, resolution=resolution, phase_x_mm=phase_x_mm, phase_y_mm=phase_y_mm, tools=tools)
                mask_c, meta_c = c_masks[key]
                path_a, path_b = mask_path("A", resolution, phase_id, index), mask_path("B", resolution, phase_id, index)
                write_mask(path_a, mask_a); write_mask(path_b, mask_b)
                topology_a, topology_b = filtered_topology(mask_a, resolution), filtered_topology(mask_b, resolution)
                for route, mask, meta, path, topology, registry in (("A", mask_a, meta_a, path_a, topology_a, route_a_registry), ("B", mask_b, meta_b, path_b, topology_b, route_b_registry)):
                    row = {
                        "run_id": RUN_ID, "model_id": "F1", "route": route, "source_path": relative(step_path), "source_sha256": parity["stp_sha256"],
                        "config_hash": config_hash, "slice_index": index, "z_mm": z_mm, "resolution_px": resolution, "phase_id": phase_id,
                        "phase_x_pixel": phase_x, "phase_y_pixel": phase_y, "phase_x_mm": phase_x_mm, "phase_y_mm": phase_y_mm,
                        "raster_bounds_mm": "[0,0] to [40,40]", "solid_pixels": int(mask.sum()), "area_mm2": float(mask.sum() * pixel_size**2),
                        "mask_packedbits_sha256": packed_mask_sha256(mask), "png_path": relative(path), "png_sha256": sha256_file(path),
                        "runtime_s": meta["runtime_s"], "warning": "", **topology, **step_meta, **meta,
                    }
                    registry.append(row); measurements.append(row)
                c_row = {**meta_c, "common_contract_hash": config_hash, "pixel_size_mm": pixel_size, "slice_group": "boundary" if index in BOUNDARY_INDICES else "interior"}
                route_c_registry.append(c_row); measurements.append(c_row)
                masks[key] = {"A": mask_a, "B": mask_b, "C": mask_c}
    if len(route_a_registry) != 144 or len(route_b_registry) != 144 or len(route_c_registry) != 144:
        raise RuntimeError("A/B/C registry count mismatch")
    comparisons: list[dict[str, object]] = []
    for (index, resolution, phase_id), bank in sorted(masks.items()):
        for comparison_id, candidate in (("A-B", bank["B"]), ("A-C", bank["C"])):
            row = compare_masks(bank["A"], candidate, comparison_id=comparison_id, slice_index=index, resolution=resolution, phase_id=phase_id)
            row["z_mm"] = float(z_values[index]); row["phase_x_pixel"] = PHASES[phase_id][0]; row["phase_y_pixel"] = PHASES[phase_id][1]
            row["phase_x_mm"] = PHASES[phase_id][0] * (EXPECTED_SIZE_MM / resolution); row["phase_y_mm"] = PHASES[phase_id][1] * (EXPECTED_SIZE_MM / resolution)
            row["route_A_mask_path"] = relative(mask_path("A", resolution, phase_id, index)); row["route_B_mask_path"] = relative(mask_path("B", resolution, phase_id, index)); row["route_C_reused_mask_path"] = route_c_registry[[ (r["slice_index"], r["resolution_px"], r["phase_id"]) for r in route_c_registry ].index((index,resolution,phase_id))]["reused_from_image_path"]
            comparisons.append(row)
    summaries = metric_summary(comparisons)
    figures = worst_case_figures(masks, comparisons)
    route_a_path = TABLES / f"{RUN_ID}_route_A_mask_registry.csv"; route_b_path = TABLES / f"{RUN_ID}_route_B_mask_registry.csv"; route_c_path = TABLES / f"{RUN_ID}_route_C_reused_mask_registry.csv"
    measurement_path = TABLES / f"{RUN_ID}_route_ABC_measurements.csv"; ab_path = TABLES / f"{RUN_ID}_A_B_144_comparisons.csv"; ac_path = TABLES / f"{RUN_ID}_A_C_144_comparisons.csv"; summary_path = TABLES / f"{RUN_ID}_resolution_phase_slice_summary.csv"; figure_path = TABLES / f"{RUN_ID}_worst_case_review_registry.csv"
    write_csv(route_a_path, route_a_registry); write_csv(route_b_path, route_b_registry); write_csv(route_c_path, route_c_registry); write_csv(measurement_path, measurements)
    write_csv(ab_path, [row for row in comparisons if row["comparison_id"] == "A-B"]); write_csv(ac_path, [row for row in comparisons if row["comparison_id"] == "A-C"]); write_csv(summary_path, summaries); write_csv(figure_path, figures)
    producer = {"work_id": WORK_ID, "run_id": RUN_ID, "status": "completed_pending_independent_QA", "runtime": "KMK312 / Python 3.12.12", "route_A_new_masks": len(route_a_registry), "route_B_new_masks": len(route_b_registry), "route_C_reused_masks": len(route_c_registry), "A_B_comparisons": sum(row["comparison_id"] == "A-B" for row in comparisons), "A_C_comparisons": sum(row["comparison_id"] == "A-C" for row in comparisons), "elapsed_s": time.perf_counter() - started, "protected_files_unchanged": all(protected_file_audit().values()), "scope": "selected 9 slices x 4 resolutions x 4 phases only; no full Z801/descriptors/y"}
    write_json(RESULT / "PRODUCER_PACKET.json", producer)
    report = f"""# ROUTE-VALID-003 F1 STEP-reference pixel-phase and resolution stress test

- Run: `{RUN_ID}`
- Settings: `{SETTINGS}`
- Runtime: KMK312 / Python 3.12.12
- Scope: 9 selected z slices × 4 resolutions × 4 pixel phases; **A/B newly calculated, C reused from IMSTL-007**.
- Producer state: **completed pending independent QA**.

## Frozen evidence and transform

- F1 remains `paired_confirmed` / `confirmed_metric_parity` with raw STEP and separately stored STL hashes replayed.
- All 144 Route-C PNG and packed-mask identities replayed from `IMSTL-007-20260728-002`; none was regenerated.
- A/B used one shared raw-STL-bbox-derived axis-wise N40 transform only after raw STEP/STL coordinate frames agreed within `{COMMON_COORDINATE_TOLERANCE_MM}` mm.  No ICP, rotation, or route-specific bbox fitting was used.
- STEP common-transform bbox outside N40 (diagnostic): `{step_meta['step_common_affine_bbox_outside_N40_mm']:.9f}` mm.

## Producer counts

- Route A new masks: `{len(route_a_registry)}`
- Route B new masks: `{len(route_b_registry)}`
- Route C reused masks: `{len(route_c_registry)}`
- A–B comparisons: `{sum(row['comparison_id'] == 'A-B' for row in comparisons)}`
- A–C comparisons: `{sum(row['comparison_id'] == 'A-C' for row in comparisons)}`

This is a route/mask study only.  It does not establish descriptor, Angle, Curvature, Excel/LEGACY-PY, y, model-training, production-default, all-F, or all58 parity.
"""
    (RESULT / "REPORT.md").write_text(report, encoding="utf-8")
    write_csv(RUN / "OUTPUT_MANIFEST.csv", build_output_manifest(RUN))
    write_csv(RESULT / "OUTPUT_MANIFEST.csv", build_output_manifest(RESULT))
    print(json.dumps(producer, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
