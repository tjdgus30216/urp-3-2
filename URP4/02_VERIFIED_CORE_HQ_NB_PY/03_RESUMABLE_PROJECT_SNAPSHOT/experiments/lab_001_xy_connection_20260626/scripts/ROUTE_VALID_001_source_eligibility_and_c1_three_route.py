"""ROUTE-VALID-001: source eligibility + bounded C1 A/B/C selected-slice audit.

Scientific boundary
-------------------
Route A is the original STEP B-rep section.  Route B is a controlled
tessellation generated from *the same* STEP.  Route C is the separately
stored paired STL, processed with the frozen imported-STL winding route.

Therefore A--B is representation consistency only.  Only A--C is an
imported-STL geometry-preservation observation, and this script permits that
comparison solely when the source-pair registry says ``confirmed``.

This script does not access y, descriptors, Excel, models, or training.
It creates only a fresh, run-id scoped audit packet.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
DELIVERABLE = ROOT / "URP4-1_DELIVERABLE"
TABLES = LAB / "reports" / "tables"
RESULT = LAB / "results" / "ROUTE-VALID-001" / "ROUTE-VALID-001-20260729-001"

WORK_ID = "ROUTE-VALID-001_SOURCE_ELIGIBILITY_AND_THREE_ROUTE_SELECTED_SLICE_VALIDATION_NO_Y"
RUN_ID = "ROUTE-VALID-001-20260729-001"
SETTINGS = "IDX-URP4-1-GEOM-ROUTES / CFG-ROUTEVALID001-C1-ZMID-P1000 r1"
INVENTORY = TABLES / "STRICT_STEP_001_GEOMETRY_ROUTE_INVENTORY_20260724.csv"
PARITY = TABLES / "R09-20260715_stp_stl_metric_parity.csv"
STRICT018 = LAB / "results" / "STRICT-STEP-018" / "STRICT-STEP-018-20260729-001"
STRICT018_SCRIPT = LAB / "scripts" / "STRICT_STEP_018_c1_l1_area_screen.py"

RESOLUTION = 1000
SLICE_COUNT = 801
SELECTED_SLICE_INDEX = 400
EXPECTED_SIZE_MM = 40.0

STL_ONLY = {*(f"L{i}" for i in range(12, 21)), *(f"T{i}" for i in range(1, 17))}
ORIENTATION_HOLD = {"T17"}


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


def source_check(path_value: str, expected_sha: str) -> dict[str, object]:
    path = Path(path_value)
    exists = path.is_file()
    observed = sha256_file(path) if exists else ""
    return {
        "path": str(path),
        "exists": exists,
        "expected_sha256": expected_sha.lower(),
        "observed_sha256": observed,
        "hash_match": bool(exists and observed.lower() == expected_sha.lower()),
        "byte_size": path.stat().st_size if exists else "",
    }


def audit_eligibility() -> tuple[list[dict[str, object]], dict[str, dict[str, object]]]:
    inventory = {row["candidate_id"]: row for row in read_csv(INVENTORY)}
    parity = {row["model_id"]: row for row in read_csv(PARITY)}
    rows: list[dict[str, object]] = []
    lookup: dict[str, dict[str, object]] = {}

    for model_id in sorted(inventory):
        inv = inventory[model_id]
        par = parity.get(model_id)
        source = source_check(inv["source_geometry_path"], inv["source_sha256"])
        row: dict[str, object] = {
            "model_id": model_id,
            "inventory_geometry_route": inv["geometry_route"],
            "inventory_source_format": inv["source_geometry_format"],
            "inventory_source_path": inv["source_geometry_path"],
            "inventory_source_expected_sha256": inv["source_sha256"],
            "inventory_source_observed_sha256": source["observed_sha256"],
            "inventory_source_exists": source["exists"],
            "inventory_source_hash_match": source["hash_match"],
            "available_step_count": inv["available_step_count"],
            "available_stl_count": inv["available_stl_count"],
            "parity_state": par["parity_state"] if par else "not_registered",
            "stp_path": par["stp_path"] if par else "",
            "stp_expected_sha256": par["stp_sha256"] if par else "",
            "stl_path": par["stl_path"] if par else "",
            "stl_expected_sha256": par["stl_sha256"] if par else "",
            "stp_brep_status": par["stp_brep_status"] if par else "",
            "pair_note": par["note"] if par else "",
            "orientation_hold": model_id in ORIENTATION_HOLD,
            "official_route_ac_eligibility": "not_eligible",
            "eligibility_status": "",
            "eligibility_reason": "",
        }
        if model_id in STL_ONLY:
            row.update(
                eligibility_status="stl_only",
                eligibility_reason="No original STEP in inventory; STEP↔STL comparison is prohibited.",
            )
        elif not source["hash_match"]:
            row.update(
                eligibility_status="missing_or_hash_mismatch",
                eligibility_reason="Inventory source file is missing or its SHA-256 differs from inventory.",
            )
        elif par is None:
            row.update(
                eligibility_status="missing_or_hash_mismatch",
                eligibility_reason="No paired STEP/STL parity record exists; independent pair identity is unavailable.",
            )
        else:
            stp = source_check(str(ROOT / par["stp_path"]), par["stp_sha256"])
            stl = source_check(str(ROOT / par["stl_path"]), par["stl_sha256"])
            row.update(
                stp_exists=stp["exists"],
                stp_observed_sha256=stp["observed_sha256"],
                stp_hash_match=stp["hash_match"],
                stl_exists=stl["exists"],
                stl_observed_sha256=stl["observed_sha256"],
                stl_hash_match=stl["hash_match"],
                stl_byte_size=stl["byte_size"],
            )
            if not stp["hash_match"] or not stl["hash_match"]:
                row.update(
                    eligibility_status="missing_or_hash_mismatch",
                    eligibility_reason="Registered paired STEP or STL is missing or has a SHA-256 mismatch.",
                )
            elif par["parity_state"] == "confirmed_metric_parity":
                row.update(
                    eligibility_status="paired_confirmed",
                    eligibility_reason="Original STEP and separately stored STL both hash-match their parity registry; metric parity is confirmed.",
                    official_route_ac_eligibility="eligible" if model_id not in ORIENTATION_HOLD else "excluded_orientation_crosswalk",
                )
            elif par["parity_state"] == "likely_same_geometry_tessellation_or_orientation":
                row.update(
                    eligibility_status="paired_likely",
                    eligibility_reason="Both assets hash-match, but pair identity is only likely; sensitivity-only Route A–C permitted.",
                    official_route_ac_eligibility="sensitivity_only" if model_id not in ORIENTATION_HOLD else "excluded_orientation_crosswalk",
                )
            else:
                row.update(
                    eligibility_status="missing_or_hash_mismatch",
                    eligibility_reason=f"Unsupported/unknown parity state: {par['parity_state']}",
                )
        rows.append(row)
        lookup[model_id] = row
    return rows, lookup


def component_hole_counts(mask: np.ndarray) -> tuple[int, int]:
    binary = np.asarray(mask, dtype=np.uint8)
    count, _ = cv2.connectedComponents(binary, connectivity=8)
    components = int(count - 1)
    inverse = (1 - binary).astype(np.uint8)
    bg_count, labels = cv2.connectedComponents(inverse, connectivity=8)
    border_labels = set(np.unique(np.r_[labels[0, :], labels[-1, :], labels[:, 0], labels[:, -1]]).tolist())
    holes = sum(1 for label in range(1, bg_count) if label not in border_labels)
    return components, int(holes)


def metrics(reference: np.ndarray, candidate: np.ndarray) -> dict[str, object]:
    a, b = np.asarray(reference, dtype=bool), np.asarray(candidate, dtype=bool)
    intersection = int(np.logical_and(a, b).sum())
    union = int(np.logical_or(a, b).sum())
    symmetric = int(np.logical_xor(a, b).sum())
    pixel_area = (EXPECTED_SIZE_MM / RESOLUTION) ** 2
    ap, bp = int(a.sum()), int(b.sum())
    ac, hc = component_hole_counts(b)
    ar, hr = component_hole_counts(a)
    return {
        "mask_iou": intersection / union if union else 1.0,
        "symmetric_difference_pixels": symmetric,
        "symmetric_difference_area_mm2": symmetric * pixel_area,
        "reference_area_pixels": ap,
        "candidate_area_pixels": bp,
        "reference_area_mm2": ap * pixel_area,
        "candidate_area_mm2": bp * pixel_area,
        "area_relative_delta": abs(ap - bp) / max(ap, 1),
        "reference_component_count_diagnostic": ar,
        "candidate_component_count_diagnostic": ac,
        "reference_hole_count_diagnostic": hr,
        "candidate_hole_count_diagnostic": hc,
    }


def load_existing_step_masks() -> tuple[np.ndarray, np.ndarray, dict[str, object]]:
    brep_path = STRICT018 / "C1_ZMID_P1000_BREP.png"
    tess_path = STRICT018 / "C1_ZMID_P1000_TESS.png"
    if not brep_path.is_file() or not tess_path.is_file():
        raise RuntimeError("C1 Route A/B selected-slice artifacts are absent; Route C will not be started.")
    a = cv2.imread(str(brep_path), cv2.IMREAD_GRAYSCALE)
    b = cv2.imread(str(tess_path), cv2.IMREAD_GRAYSCALE)
    if a is None or b is None or a.shape != (RESOLUTION, RESOLUTION) or b.shape != a.shape:
        raise RuntimeError("C1 Route A/B masks are unreadable or not P1000; Route C will not be started.")
    return a > 0, b > 0, {
        "route_a_existing_mask_path": str(brep_path),
        "route_a_existing_mask_sha256": sha256_file(brep_path),
        "route_b_existing_mask_path": str(tess_path),
        "route_b_existing_mask_sha256": sha256_file(tess_path),
        "route_ab_execution_script": str(STRICT018_SCRIPT),
        "route_ab_execution_script_sha256": sha256_file(STRICT018_SCRIPT),
        "route_ab_interpretation": "same-original-STEP direct B-rep versus controlled tessellation representation consistency only",
    }


def route_c_mask(c1: dict[str, object]) -> tuple[np.ndarray, dict[str, object]]:
    if str(c1["eligibility_status"]) != "paired_confirmed" or str(c1["official_route_ac_eligibility"]) != "eligible":
        raise RuntimeError("C1 is not a confirmed and officially eligible STEP/STL pair.")
    if str(DELIVERABLE) not in sys.path:
        sys.path.insert(0, str(DELIVERABLE))
    from urp4.geometry_io.v0_4.imported_winding import (
        ImportedSTLWindingConfig,
        load_imported_stl_triangles,
        oriented_section_z,
        winding_raster,
    )

    config = ImportedSTLWindingConfig(
        pixel_resolution=RESOLUTION,
        slice_count=SLICE_COUNT,
        expected_size_mm=EXPECTED_SIZE_MM,
        normalization_mode="uniform_bbox_to_expected",
        axis="z",
        route_id="ROUTE-C-IMPORTED-STL-ORIENTED-NONZERO-C1-SELECTED-P1000-ZMID",
        algorithm_revision="ORIENTED_NONZERO_RAW/IMSTL-004/r1",
    )
    # The frozen stream currently passes the raw analysis bbox to a rasterizer
    # that demands *bit-exact* square pixel pitches.  C1's verified STL has a
    # harmless 1.27e-6 mm export-level anisotropy (30.00000095 vs 30 mm), so it
    # fails that guard after otherwise valid uniform N40 scaling.  The adapter
    # below does not change the STL or mesh.  It fixes the **analysis pixel
    # domain** to the explicit N40 cube [0,40]×[0,40], the same domain used by
    # Route A/B.  The raw bbox, scale, and maximum residual are retained as
    # provenance.  This is a bounded route-local grid-alignment experiment,
    # not an unrecorded change to the frozen imported-STL module.
    triangles, lower, upper, source_hash, normalization = load_imported_stl_triangles(
        str(c1["stl_path"]), config, expected_sha256=str(c1["stl_expected_sha256"])
    )
    extent = np.asarray(upper - lower, dtype=float)
    residual_mm = float(np.max(np.abs(extent - EXPECTED_SIZE_MM)))
    if residual_mm > 1.0e-3:
        raise RuntimeError(f"C1 grid-alignment adapter rejected: N40 bbox residual={residual_mm} mm")
    z_values = np.linspace(lower[2], upper[2], SLICE_COUNT)
    z_mm = float(z_values[SELECTED_SLICE_INDEX])
    start = time.perf_counter()
    segments, section_diag = oriented_section_z(triangles, z_mm)
    mask, raster_diag = winding_raster(
        segments,
        lower_xy=np.array([0.0, 0.0], dtype=float),
        upper_xy=np.array([EXPECTED_SIZE_MM, EXPECTED_SIZE_MM], dtype=float),
        pixels=RESOLUTION,
    )
    runtime = time.perf_counter() - start
    packet: dict[str, object] = {
        "slice_index": SELECTED_SLICE_INDEX,
        "z_mm": z_mm,
        "endpoint_adjusted": False,
        "source_geometry_sha256": source_hash,
        "route_id": config.route_id,
        "algorithm_revision": config.algorithm_revision,
        **normalization,
        **section_diag,
        **raster_diag,
        "pixel_grid_rule": "explicit_normalized_N40_cube_xy_0_to_40mm",
        "analysis_bbox_extent_residual_to_N40_mm": residual_mm,
        "frozen_stream_direct_status": "blocked_by_bit_exact_square_pixel_guard_for_C1_export_micro_anisotropy",
    }
    mask = np.asarray(mask, dtype=bool)
    if mask.shape != (RESOLUTION, RESOLUTION):
        raise RuntimeError(f"Route C returned unexpected mask shape: {mask.shape}")
    packet.update(
        route_c_runtime_s=runtime,
        route_c_config_hash=stable_hash({
            "pixel_resolution": RESOLUTION,
            "slice_count": SLICE_COUNT,
            "expected_size_mm": EXPECTED_SIZE_MM,
            "normalization_mode": "uniform_bbox_to_expected",
            "axis": "z",
            "slice_index": SELECTED_SLICE_INDEX,
        }),
    )
    return mask, packet


def main() -> None:
    executable = str(Path(sys.executable).resolve()).lower()
    if "kmk312" not in executable or sys.version_info[:2] != (3, 12):
        raise RuntimeError("ROUTE-VALID-001 requires KMK312 Python 3.12.")
    for required in (INVENTORY, PARITY, STRICT018_SCRIPT):
        if not required.is_file():
            raise RuntimeError(f"required input missing: {required}")
    RESULT.mkdir(parents=True, exist_ok=True)

    eligibility_rows, eligibility = audit_eligibility()
    eligibility_path = TABLES / f"{RUN_ID}_source_eligibility.csv"
    write_csv(eligibility_path, eligibility_rows)
    status_counts: dict[str, int] = {}
    for row in eligibility_rows:
        status_counts[str(row["eligibility_status"])] = status_counts.get(str(row["eligibility_status"]), 0) + 1
    c1 = eligibility.get("C1")
    if c1 is None:
        raise RuntimeError("C1 is missing from route inventory.")
    if str(c1["eligibility_status"]) != "paired_confirmed":
        raise RuntimeError(f"C1 asset eligibility failed; Route C is prohibited: {c1['eligibility_status']}")

    # A–B must be inspected before C. These files are the prior direct-STEP,
    # same-source pair; no independently stored STL enters this comparison.
    mask_a, mask_b, ab_meta = load_existing_step_masks()
    ab = metrics(mask_a, mask_b)
    if not np.array_equal(mask_a, mask_b):
        raise RuntimeError("C1 Route A–B is not stable at selected P1000 slice; Route C is intentionally not started.")

    mask_c, c_meta = route_c_mask(c1)
    route_c_path = RESULT / "C1_ZMID_P1000_IMPORTED_STL_ROUTE_C.png"
    if not cv2.imwrite(str(route_c_path), mask_c.astype(np.uint8) * 255):
        raise RuntimeError("could not write Route C artifact")
    ac = metrics(mask_a, mask_c)

    metric_rows = [
        {
            "model_id": "C1",
            "comparison_id": "C1-A-B",
            "route_reference": "A_original_STEP_direct_Brep",
            "route_candidate": "B_controlled_tessellation_from_same_STEP",
            "comparison_scope": "representation_consistency_only_not_imported_STL_validation",
            "official_imported_stl_judgement": "not_applicable",
            "runtime_s_candidate": "preexisting_artifact_reused",
            **ab,
        },
        {
            "model_id": "C1",
            "comparison_id": "C1-A-C",
            "route_reference": "A_original_STEP_direct_Brep",
            "route_candidate": "C_separately_stored_paired_imported_STL_improved_winding_slicer",
            "comparison_scope": "confirmed-source-pair selected-slice geometry-preservation observation",
            "official_imported_stl_judgement": "continuous_metric_only_no_new_pass_threshold",
            "runtime_s_candidate": c_meta["route_c_runtime_s"],
            **ac,
        },
    ]
    metric_path = TABLES / f"{RUN_ID}_C1_three_route_selected_slice_metrics.csv"
    write_csv(metric_path, metric_rows)

    image_rows = [
        {
            "model_id": "C1", "route": "A", "source_type": "original_STEP_direct_Brep",
            "path": ab_meta["route_a_existing_mask_path"], "sha256": ab_meta["route_a_existing_mask_sha256"],
            "interpretation": "original STEP B-rep selected-slice mask",
        },
        {
            "model_id": "C1", "route": "B", "source_type": "controlled_tessellation_same_STEP",
            "path": ab_meta["route_b_existing_mask_path"], "sha256": ab_meta["route_b_existing_mask_sha256"],
            "interpretation": "same STEP controlled tessellation; not independently stored STL",
        },
        {
            "model_id": "C1", "route": "C", "source_type": "separately_stored_paired_imported_STL",
            "path": str(route_c_path), "sha256": sha256_file(route_c_path),
            "interpretation": "frozen imported-STL oriented non-zero winding selected-slice mask",
        },
    ]
    image_path = TABLES / f"{RUN_ID}_C1_image_registry.csv"
    write_csv(image_path, image_rows)

    artifact = {
        "work_id": WORK_ID,
        "run_id": RUN_ID,
        "settings": SETTINGS,
        "status": "completed_c1_only",
        "scope_stop": "C1 eligibility + selected-slice A-B + A-C only; B1/L7/F1/full-Z801 not executed.",
        "runtime_python": sys.version,
        "runtime_executable": str(Path(sys.executable).resolve()),
        "source_inventory": str(INVENTORY),
        "source_inventory_sha256": sha256_file(INVENTORY),
        "metric_parity_registry": str(PARITY),
        "metric_parity_registry_sha256": sha256_file(PARITY),
        "eligibility_table": str(eligibility_path),
        "eligibility_status_counts": status_counts,
        "c1_eligibility": c1,
        "route_ab": {**ab_meta, **ab},
        "route_c": {
            **{key: value for key, value in c_meta.items() if key != "mask"},
            "output_path": str(route_c_path),
            "output_sha256": sha256_file(route_c_path),
            **ac,
        },
        "metric_table": str(metric_path),
        "image_registry": str(image_path),
        "interpretation_guardrails": [
            "A-B success is same-source STEP representation consistency only; it is not imported-STL validation.",
            "A-C is reported only because C1 source pair is confirmed; values are continuous observations, not an invented pass/fail threshold.",
            "Area/mask results do not establish component, Angle, Curvature, full descriptor, Excel/LEGACY-PY parity, y, learning, or inverse-design conclusions.",
            "No conclusion is generalized to STL-only L12-L20 or T1-T16.",
        ],
    }
    artifact_path = RESULT / "ROUTE_VALID_001_C1_PACKET.json"
    artifact_path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": artifact["status"],
        "eligibility_status_counts": status_counts,
        "C1_A_B_iou": ab["mask_iou"],
        "C1_A_C_iou": ac["mask_iou"],
        "C1_A_C_area_relative_delta": ac["area_relative_delta"],
        "packet": str(artifact_path),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
