"""Bounded F1 resolution and half-pixel phase diagnosis.

This run reuses the frozen imported-STL oriented non-zero winding algorithm.
It does not run all 801 slices, access y, fit a model, or modify any protected
source. Every diagnostic mask is retained for manual review.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import sys
from datetime import UTC, datetime
from itertools import combinations
from pathlib import Path

import cv2
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from urp4.geometry_io.v0_4 import (
    ImportedSTLWindingConfig,
    active_triangle_subsets_z,
    load_imported_stl_triangles,
    mask_packedbits_sha256,
    oriented_section_z,
    winding_raster,
)


LAB = ROOT / "experiments/lab_001_xy_connection_20260626"
RUN_ID = "IMSTL-007-20260728-002"
TASK_ID = "IMSTL-007_F1_SELECTED_SLICE_RESOLUTION_AND_PIXEL_PHASE_DIAGNOSIS_NO_Y"
SETTINGS = "IDX-URP4-1-GEOM-IMPORTED-STL / CFG-IMSTL007-F1-P500-750-1000-1500-PHASE4-SELECTED r1"
RUN = LAB / "runs/I007" / RUN_ID
RESULT = LAB / "results/I007_F1" / RUN_ID
TABLES = LAB / "reports/tables"
CONTRACT_PATH = LAB / "factories/IMSTL-007/contracts/IMSTL-007_F1_RESOLUTION_PIXEL_PHASE_v0_2_SHORTPATH_20260728.json"
SOURCE = LAB / "data/processed/n40_all58_20260715/stl/F1__0dff3c1b13__N40.stl"
BASELINE = TABLES / "IMSTL-006-20260728-002_selected_slice_gate_detail.csv"
SELECTED = (0, 1, 100, 200, 400, 600, 700, 799, 800)
INTERIOR = (1, 100, 200, 400, 600, 700, 799)
FAILED_BASELINE = (200, 600)
RESOLUTIONS = (500, 750, 1000, 1500)
PHASES = {
    "P00": (0.0, 0.0),
    "P50X": (0.5, 0.0),
    "P50Y": (0.0, 0.5),
    "P50XY": (0.5, 0.5),
}
RESOLUTION_PAIRS = ((500, 750), (750, 1000), (1000, 1500), (500, 1000), (500, 1500), (750, 1500))
MIN_COMPONENT_AREA_MM2 = 0.0032
IOU_GATE = 0.95
AREA_GATE = 0.05
BOUNDARY_GATE = 0.99


def now() -> str:
    return datetime.now(UTC).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty table: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for row in rows for key in row})
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    os.replace(tmp, path)


def filtered_topology(mask: np.ndarray, resolution: int) -> dict[str, int]:
    binary = np.asarray(mask, dtype=np.uint8)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
    min_pixels = max(1, int(math.ceil(MIN_COMPONENT_AREA_MM2 / (40.0 / resolution) ** 2)))
    filtered = np.zeros_like(binary)
    kept = 0
    for label in range(1, count):
        if int(stats[label, cv2.CC_STAT_AREA]) >= min_pixels:
            filtered[labels == label] = 1
            kept += 1
    contours, hierarchy = cv2.findContours(filtered, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    holes = 0
    if hierarchy is not None:
        holes = sum(int(item[3] >= 0) for item in hierarchy[0])
    return {
        "component_count_raw": int(max(0, count - 1)),
        "component_count_filtered": int(kept),
        "hole_count_filtered": int(holes),
        "min_component_pixels": int(min_pixels),
    }


def boundary_band(mask_a: np.ndarray, mask_b: np.ndarray, radius: int) -> np.ndarray:
    kernel = np.ones((3, 3), dtype=np.uint8)
    a = np.asarray(mask_a, dtype=np.uint8)
    b = np.asarray(mask_b, dtype=np.uint8)
    grad_a = cv2.morphologyEx(a, cv2.MORPH_GRADIENT, kernel)
    grad_b = cv2.morphologyEx(b, cv2.MORPH_GRADIENT, kernel)
    edge = np.asarray((grad_a > 0) | (grad_b > 0), dtype=np.uint8)
    return cv2.dilate(edge, kernel, iterations=max(1, int(radius))).astype(bool)


def compare_masks(mask_a: np.ndarray, mask_b: np.ndarray, *, boundary_radius: int) -> dict[str, object]:
    a = np.asarray(mask_a, dtype=bool)
    b = np.asarray(mask_b, dtype=bool)
    if a.shape != b.shape:
        a = cv2.resize(a.astype(np.uint8), (b.shape[1], b.shape[0]), interpolation=cv2.INTER_NEAREST).astype(bool)
    intersection = int(np.count_nonzero(a & b))
    union = int(np.count_nonzero(a | b))
    area_a = int(a.sum())
    area_b = int(b.sum())
    xor = a ^ b
    xor_count = int(xor.sum())
    band = boundary_band(a, b, boundary_radius)
    explained = 1.0 if xor_count == 0 else float(np.count_nonzero(xor & band) / xor_count)
    return {
        "iou": 1.0 if union == 0 else float(intersection / union),
        "relative_area_difference": 0.0 if max(area_a, area_b) == 0 else float(abs(area_a - area_b) / max(area_a, area_b)),
        "symmetric_difference_pixels": xor_count,
        "symmetric_difference_fraction": float(xor_count / xor.size),
        "boundary_band_radius_pixels": int(boundary_radius),
        "boundary_band_explained_fraction": explained,
    }


def baseline_rows(contract: dict[str, object]) -> dict[tuple[int, int], dict[str, str]]:
    if sha256(BASELINE) != contract["baseline"]["table_sha256"]:
        raise RuntimeError("IMSTL-006 baseline table hash mismatch")
    frame = pd.read_csv(BASELINE, dtype=str, keep_default_na=False)
    frame = frame[frame["model_id"] == "F1"]
    rows: dict[tuple[int, int], dict[str, str]] = {}
    for row in frame.to_dict(orient="records"):
        index = int(row["slice_index"])
        rows[(index, 500)] = {"sha": row["p500_mask_sha256"], "iou": row["p500_upsampled_vs_p1000_iou"]}
        rows[(index, 1000)] = {"sha": row["p1000_mask_sha256"], "iou": row["p500_upsampled_vs_p1000_iou"]}
    if len(rows) != 18:
        raise RuntimeError(f"baseline F1 row map mismatch: {len(rows)}")
    return rows


def contact_sheet(index: int, masks: dict[tuple[int, str, int], np.ndarray], output: Path) -> None:
    tile = 280
    header = 36
    sheet = np.full((len(RESOLUTIONS) * (tile + header), len(PHASES) * tile, 3), 255, dtype=np.uint8)
    for row, resolution in enumerate(RESOLUTIONS):
        for col, phase in enumerate(PHASES):
            mask = masks[(index, phase, resolution)]
            image = cv2.resize(mask.astype(np.uint8) * 255, (tile, tile), interpolation=cv2.INTER_AREA)
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            y = row * (tile + header)
            x = col * tile
            sheet[y + header : y + header + tile, x : x + tile] = image
            cv2.putText(sheet, f"P{resolution} {phase}", (x + 8, y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 1, cv2.LINE_AA)
    output.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output), sheet)


def build_manifest(root: Path) -> list[dict[str, object]]:
    rows = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name == "OUTPUT_MANIFEST.csv":
            continue
        rows.append({"relative_path": path.relative_to(root).as_posix(), "size_bytes": path.stat().st_size, "sha256": sha256(path)})
    return rows


def main() -> None:
    if RUN.exists() or RESULT.exists():
        raise RuntimeError(f"run/result already exists; refuse overwrite: {RUN_ID}")
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if contract["run_id"] != RUN_ID:
        raise RuntimeError("contract run_id mismatch")
    baseline = baseline_rows(contract)
    RUN.mkdir(parents=True)
    RESULT.mkdir(parents=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    write_json(RUN / "CONTRACT.json", contract)

    config = ImportedSTLWindingConfig(pixel_resolution=1000, slice_count=801)
    triangles, lower, upper, source_hash, normalization = load_imported_stl_triangles(
        SOURCE, config, expected_sha256=contract["source"]["sha256"]
    )
    z_values = np.linspace(lower[2], upper[2], 801)
    z_values[0] = np.nextafter(lower[2], upper[2])
    z_values[-1] = np.nextafter(upper[2], lower[2])
    measurements: list[dict[str, object]] = []
    visual_rows: list[dict[str, object]] = []
    masks: dict[tuple[int, str, int], np.ndarray] = {}
    started = now()

    for index, (z_mm, active) in enumerate(active_triangle_subsets_z(triangles, z_values)):
        if index not in SELECTED:
            continue
        base_segments, section = oriented_section_z(active, z_mm)
        for resolution in RESOLUTIONS:
            pixel_size = 40.0 / resolution
            for phase_id, (phase_x, phase_y) in PHASES.items():
                segments = np.asarray(base_segments, dtype=float).copy()
                if len(segments):
                    segments[:, [0, 2]] += phase_x * pixel_size
                    segments[:, [1, 3]] += phase_y * pixel_size
                mask, raster = winding_raster(segments, lower_xy=lower[:2], upper_xy=upper[:2], pixels=resolution)
                masks[(index, phase_id, resolution)] = mask
                image_path = RUN / "masks" / f"P{resolution}" / phase_id / f"F1_z{index:04d}.png"
                image_path.parent.mkdir(parents=True, exist_ok=True)
                if not cv2.imwrite(str(image_path), mask.astype(np.uint8) * 255):
                    raise RuntimeError(f"failed image write: {image_path}")
                topology = filtered_topology(mask, resolution)
                observed_hash = mask_packedbits_sha256(mask)
                expected_replay = baseline.get((index, resolution), {}).get("sha") if phase_id == "P00" and resolution in {500, 1000} else ""
                measurements.append({
                    "run_id": RUN_ID,
                    "model_id": "F1",
                    "family": "F",
                    "slice_index": index,
                    "z_mm": float(z_mm),
                    "interior_gate_slice": index in INTERIOR,
                    "resolution_px": resolution,
                    "pixel_size_mm": pixel_size,
                    "phase_id": phase_id,
                    "phase_x_pixel": phase_x,
                    "phase_y_pixel": phase_y,
                    "phase_x_mm": phase_x * pixel_size,
                    "phase_y_mm": phase_y * pixel_size,
                    "source_geometry_sha256": source_hash,
                    "source_triangle_count": int(len(triangles)),
                    "active_triangle_count": int(len(active)),
                    "segment_count": int(section["segment_count"]),
                    "solid_pixels": int(mask.sum()),
                    "area_fraction": float(mask.mean()),
                    "area_mm2": float(mask.sum() * pixel_size**2),
                    "mask_packedbits_sha256": observed_hash,
                    "baseline_expected_sha256": expected_replay,
                    "baseline_exact_replay": "not_applicable" if not expected_replay else observed_hash == expected_replay,
                    "image_path": image_path.relative_to(ROOT).as_posix(),
                    **topology,
                    **raster,
                    **normalization,
                })
                visual_rows.append({
                    "visual_id": f"I007-F1-Z{index:04d}-P{resolution}-{phase_id}",
                    "slice_index": index,
                    "resolution_px": resolution,
                    "phase_id": phase_id,
                    "image_path": image_path.relative_to(ROOT).as_posix(),
                    "review_status": "pending_human_optional",
                    "human_label": "",
                    "notes": "",
                })

    if len(measurements) != 144:
        raise RuntimeError(f"measurement count mismatch: {len(measurements)}")

    measurement_map = {(int(row["slice_index"]), str(row["phase_id"]), int(row["resolution_px"])): row for row in measurements}
    resolution_rows: list[dict[str, object]] = []
    for index in SELECTED:
        for phase_id in PHASES:
            for low, high in RESOLUTION_PAIRS:
                left = masks[(index, phase_id, low)]
                right = masks[(index, phase_id, high)]
                metric = compare_masks(left, right, boundary_radius=int(math.ceil(high / low)) + 1)
                low_top = measurement_map[(index, phase_id, low)]
                high_top = measurement_map[(index, phase_id, high)]
                resolution_rows.append({
                    "run_id": RUN_ID,
                    "slice_index": index,
                    "interior_gate_slice": index in INTERIOR,
                    "phase_id": phase_id,
                    "low_resolution_px": low,
                    "high_resolution_px": high,
                    "pair_id": f"P{low}_P{high}",
                    **metric,
                    "component_count_low": low_top["component_count_filtered"],
                    "component_count_high": high_top["component_count_filtered"],
                    "hole_count_low": low_top["hole_count_filtered"],
                    "hole_count_high": high_top["hole_count_filtered"],
                    "topology_equal": low_top["component_count_filtered"] == high_top["component_count_filtered"] and low_top["hole_count_filtered"] == high_top["hole_count_filtered"],
                })

    phase_rows: list[dict[str, object]] = []
    for index in SELECTED:
        for resolution in RESOLUTIONS:
            for left_phase, right_phase in combinations(PHASES, 2):
                left = masks[(index, left_phase, resolution)]
                right = masks[(index, right_phase, resolution)]
                metric = compare_masks(left, right, boundary_radius=2)
                left_top = measurement_map[(index, left_phase, resolution)]
                right_top = measurement_map[(index, right_phase, resolution)]
                phase_rows.append({
                    "run_id": RUN_ID,
                    "slice_index": index,
                    "interior_gate_slice": index in INTERIOR,
                    "resolution_px": resolution,
                    "left_phase": left_phase,
                    "right_phase": right_phase,
                    "phase_pair": f"{left_phase}_{right_phase}",
                    **metric,
                    "component_count_left": left_top["component_count_filtered"],
                    "component_count_right": right_top["component_count_filtered"],
                    "hole_count_left": left_top["hole_count_filtered"],
                    "hole_count_right": right_top["hole_count_filtered"],
                    "topology_equal": left_top["component_count_filtered"] == right_top["component_count_filtered"] and left_top["hole_count_filtered"] == right_top["hole_count_filtered"],
                })

    replay_rows = [row for row in measurements if row["baseline_exact_replay"] != "not_applicable"]
    replay_pass = len(replay_rows) == 18 and all(bool(row["baseline_exact_replay"]) for row in replay_rows)
    high_resolution = [row for row in resolution_rows if row["interior_gate_slice"] and row["pair_id"] == "P1000_P1500"]
    high_phase = [row for row in phase_rows if row["interior_gate_slice"] and int(row["resolution_px"]) == 1500]
    resolution_gate = all(float(row["iou"]) >= IOU_GATE and float(row["relative_area_difference"]) <= AREA_GATE and float(row["boundary_band_explained_fraction"]) >= BOUNDARY_GATE and bool(row["topology_equal"]) for row in high_resolution)
    phase_gate = all(float(row["iou"]) >= IOU_GATE and float(row["relative_area_difference"]) <= AREA_GATE and float(row["boundary_band_explained_fraction"]) >= BOUNDARY_GATE and bool(row["topology_equal"]) for row in high_phase)
    improvement_rows = []
    for index in FAILED_BASELINE:
        old = next(row for row in resolution_rows if int(row["slice_index"]) == index and row["phase_id"] == "P00" and row["pair_id"] == "P500_P1000")
        new = next(row for row in resolution_rows if int(row["slice_index"]) == index and row["phase_id"] == "P00" and row["pair_id"] == "P1000_P1500")
        improvement_rows.append({"slice_index": index, "baseline_iou": float(old["iou"]), "high_resolution_iou": float(new["iou"]), "improved": float(new["iou"]) > float(old["iou"]) and float(new["iou"]) >= IOU_GATE})
    failed_slice_improvement = all(bool(row["improved"]) for row in improvement_rows)
    occupancy_gate = all(0.0 < float(row["area_fraction"]) < 1.0 for row in measurements if row["interior_gate_slice"])
    passed = replay_pass and resolution_gate and phase_gate and failed_slice_improvement and occupancy_gate
    decision_label = "screening_pass_benign_discretization" if passed else "hold_resolution_or_pixel_phase_unresolved"

    slice_rows = []
    for index in SELECTED:
        res = [row for row in resolution_rows if int(row["slice_index"]) == index]
        pha = [row for row in phase_rows if int(row["slice_index"]) == index]
        slice_rows.append({
            "slice_index": index,
            "interior_gate_slice": index in INTERIOR,
            "baseline_failed_slice": index in FAILED_BASELINE,
            "min_resolution_iou": min(float(row["iou"]) for row in res),
            "min_p1000_p1500_iou": min(float(row["iou"]) for row in res if row["pair_id"] == "P1000_P1500"),
            "max_p1000_p1500_area_difference": max(float(row["relative_area_difference"]) for row in res if row["pair_id"] == "P1000_P1500"),
            "min_p1000_p1500_boundary_explained": min(float(row["boundary_band_explained_fraction"]) for row in res if row["pair_id"] == "P1000_P1500"),
            "p1000_p1500_topology_all_equal": all(bool(row["topology_equal"]) for row in res if row["pair_id"] == "P1000_P1500"),
            "min_p1500_phase_iou": min(float(row["iou"]) for row in pha if int(row["resolution_px"]) == 1500),
            "max_p1500_phase_area_difference": max(float(row["relative_area_difference"]) for row in pha if int(row["resolution_px"]) == 1500),
            "min_p1500_phase_boundary_explained": min(float(row["boundary_band_explained_fraction"]) for row in pha if int(row["resolution_px"]) == 1500),
            "p1500_phase_topology_all_equal": all(bool(row["topology_equal"]) for row in pha if int(row["resolution_px"]) == 1500),
        })

    measurement_path = TABLES / f"{RUN_ID}_mask_measurements.csv"
    resolution_path = TABLES / f"{RUN_ID}_resolution_comparison.csv"
    phase_path = TABLES / f"{RUN_ID}_phase_comparison.csv"
    slice_path = TABLES / f"{RUN_ID}_slice_summary.csv"
    visual_path = TABLES / f"{RUN_ID}_visual_review_registry.csv"
    write_csv(measurement_path, measurements)
    write_csv(resolution_path, resolution_rows)
    write_csv(phase_path, phase_rows)
    write_csv(slice_path, slice_rows)
    write_csv(visual_path, visual_rows)
    for index in SELECTED:
        contact_sheet(index, masks, RESULT / "figures" / f"F1_z{index:04d}_resolution_phase_grid.png")

    decision = {
        "run_id": RUN_ID,
        "task_id": TASK_ID,
        "settings_address": SETTINGS,
        "status": "passed" if passed else "hold",
        "decision_label": decision_label,
        "source_sha256": source_hash,
        "contract_sha256": sha256(CONTRACT_PATH),
        "mask_count": len(measurements),
        "resolution_comparison_count": len(resolution_rows),
        "phase_comparison_count": len(phase_rows),
        "baseline_exact_replay": replay_pass,
        "resolution_gate": resolution_gate,
        "phase_gate": phase_gate,
        "failed_slice_improvement": failed_slice_improvement,
        "occupancy_gate": occupancy_gate,
        "improvement_rows": improvement_rows,
        "min_high_resolution_iou": min(float(row["iou"]) for row in high_resolution),
        "max_high_resolution_area_difference": max(float(row["relative_area_difference"]) for row in high_resolution),
        "min_high_resolution_boundary_explained": min(float(row["boundary_band_explained_fraction"]) for row in high_resolution),
        "min_p1500_phase_iou": min(float(row["iou"]) for row in high_phase),
        "max_p1500_phase_area_difference": max(float(row["relative_area_difference"]) for row in high_phase),
        "min_p1500_phase_boundary_explained": min(float(row["boundary_band_explained_fraction"]) for row in high_phase),
        "started_at_utc": started,
        "completed_at_utc": now(),
        "normalization": normalization,
        "claim_boundary": contract["preregistered_decision"]["claim_boundary"],
        "forbidden_actions_observed": [],
    }
    write_json(RESULT / "DECISION_PACKET.json", decision)
    producer_qa = {
        "status": "passed" if replay_pass and len(measurements) == 144 and len(resolution_rows) == 216 and len(phase_rows) == 216 else "failed",
        "source_hash_exact": source_hash == contract["source"]["sha256"],
        "baseline_hash_exact": sha256(BASELINE) == contract["baseline"]["table_sha256"],
        "baseline_mask_replay": f"{sum(bool(row['baseline_exact_replay']) for row in replay_rows)}/{len(replay_rows)}",
        "mask_images": len(list((RUN / "masks").rglob("*.png"))),
        "contact_sheets": len(list((RESULT / "figures").glob("*.png"))),
        "measurement_rows": len(measurements),
        "resolution_rows": len(resolution_rows),
        "phase_rows": len(phase_rows),
    }
    write_json(RESULT / "PRODUCER_QA.json", producer_qa)
    if producer_qa["status"] != "passed":
        raise RuntimeError(f"producer QA failed: {producer_qa}")

    report = f"""# IMSTL-007 F1 resolution and pixel-phase diagnosis

- Run: `{RUN_ID}`
- Settings: `{SETTINGS}`
- Runtime: KMK312 / Python 3.12.12
- Scope: F1 fixed nine slices only; 4 resolutions × 4 half-pixel phases
- Result: **{decision_label}**

## Evidence

- Preserved masks: `{len(measurements)}`
- IMSTL-006 P500/P1000 P00 exact replay: **{producer_qa['baseline_mask_replay']}**
- P1000→P1500 interior minimum IoU: `{decision['min_high_resolution_iou']:.6f}`
- P1000→P1500 maximum relative area difference: `{decision['max_high_resolution_area_difference']:.6f}`
- P1000→P1500 minimum boundary-band explanation: `{decision['min_high_resolution_boundary_explained']:.6f}`
- P1500 phase-pair minimum IoU: `{decision['min_p1500_phase_iou']:.6f}`
- P1500 phase-pair maximum relative area difference: `{decision['max_p1500_phase_area_difference']:.6f}`
- P1500 phase-pair minimum boundary-band explanation: `{decision['min_p1500_phase_boundary_explained']:.6f}`
- Failed-slice improvement: `{failed_slice_improvement}` — {improvement_rows}

## Gate

- exact replay: `{replay_pass}`
- high-resolution convergence: `{resolution_gate}`
- half-pixel phase stability: `{phase_gate}`
- interior occupancy: `{occupancy_gate}`

## Interpretation boundary

This run distinguishes bounded raster discretization from route instability for F1. A pass supports only F1 imported-STL **screening** and a separately authorized future full extraction. It does not establish exact STP parity, all-F/all58 generalization, canonical structure factors, x-y utility, Training readiness or inverse design.

No full-801 F1 extraction, y access, model fitting, feature selection, source mutation, NB-CURRENT or LEGACY-PY edit occurred.
"""
    (RESULT / "REPORT.md").write_text(report, encoding="utf-8")
    write_csv(RUN / "OUTPUT_MANIFEST.csv", build_manifest(RUN))
    write_csv(RESULT / "OUTPUT_MANIFEST.csv", build_manifest(RESULT))
    print(json.dumps(decision, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
