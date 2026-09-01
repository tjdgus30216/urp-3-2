"""Independent full-mask and metric replay for IMSTL-007."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
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
RUN = LAB / "runs/I007" / RUN_ID
RESULT = LAB / "results/I007_F1" / RUN_ID
TABLES = LAB / "reports/tables"
CONTRACT = LAB / "factories/IMSTL-007/contracts/IMSTL-007_F1_RESOLUTION_PIXEL_PHASE_v0_2_SHORTPATH_20260728.json"
SOURCE = LAB / "data/processed/n40_all58_20260715/stl/F1__0dff3c1b13__N40.stl"
GUARD = LAB / "factories/CINT-09/guard/protected_asset_verification.csv"
SELECTED = (0, 1, 100, 200, 400, 600, 700, 799, 800)
RESOLUTIONS = (500, 750, 1000, 1500)
PHASES = {"P00": (0.0, 0.0), "P50X": (0.5, 0.0), "P50Y": (0.0, 0.5), "P50XY": (0.5, 0.5)}
RESOLUTION_PAIRS = ((500, 750), (750, 1000), (1000, 1500), (500, 1000), (500, 1500), (750, 1500))
MIN_COMPONENT_AREA_MM2 = 0.0032


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fields = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def topology(mask: np.ndarray, resolution: int) -> tuple[int, int]:
    count, labels, stats, _ = cv2.connectedComponentsWithStats(np.asarray(mask, dtype=np.uint8), connectivity=8)
    minimum = max(1, int(math.ceil(MIN_COMPONENT_AREA_MM2 / (40.0 / resolution) ** 2)))
    filtered = np.zeros(mask.shape, dtype=np.uint8)
    kept = 0
    for label in range(1, count):
        if int(stats[label, cv2.CC_STAT_AREA]) >= minimum:
            filtered[labels == label] = 1
            kept += 1
    _, hierarchy = cv2.findContours(filtered, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    holes = 0 if hierarchy is None else sum(int(item[3] >= 0) for item in hierarchy[0])
    return int(kept), int(holes)


def compare(a: np.ndarray, b: np.ndarray, radius: int) -> dict[str, float]:
    a = np.asarray(a, dtype=bool)
    b = np.asarray(b, dtype=bool)
    if a.shape != b.shape:
        a = cv2.resize(a.astype(np.uint8), (b.shape[1], b.shape[0]), interpolation=cv2.INTER_NEAREST).astype(bool)
    intersection = int(np.count_nonzero(a & b))
    union = int(np.count_nonzero(a | b))
    aa, bb = int(a.sum()), int(b.sum())
    xor = a ^ b
    kernel = np.ones((3, 3), dtype=np.uint8)
    edge = (cv2.morphologyEx(a.astype(np.uint8), cv2.MORPH_GRADIENT, kernel) > 0) | (cv2.morphologyEx(b.astype(np.uint8), cv2.MORPH_GRADIENT, kernel) > 0)
    band = cv2.dilate(edge.astype(np.uint8), kernel, iterations=max(1, int(radius))).astype(bool)
    xor_count = int(xor.sum())
    return {
        "iou": 1.0 if union == 0 else intersection / union,
        "relative_area_difference": 0.0 if max(aa, bb) == 0 else abs(aa - bb) / max(aa, bb),
        "boundary_band_explained_fraction": 1.0 if xor_count == 0 else float(np.count_nonzero(xor & band) / xor_count),
    }


def manifest_valid(root: Path) -> tuple[bool, int]:
    manifest = pd.read_csv(root / "OUTPUT_MANIFEST.csv", dtype=str, keep_default_na=False)
    for row in manifest.to_dict(orient="records"):
        path = root / row["relative_path"]
        if not path.is_file() or str(path.stat().st_size) != row["size_bytes"] or sha256(path) != row["sha256"]:
            return False, len(manifest)
    return True, len(manifest)


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    measurements = pd.read_csv(TABLES / f"{RUN_ID}_mask_measurements.csv", keep_default_na=False)
    resolution = pd.read_csv(TABLES / f"{RUN_ID}_resolution_comparison.csv", keep_default_na=False)
    phase = pd.read_csv(TABLES / f"{RUN_ID}_phase_comparison.csv", keep_default_na=False)
    decision = json.loads((RESULT / "DECISION_PACKET.json").read_text(encoding="utf-8"))
    measurement_map = {(int(row.slice_index), str(row.phase_id), int(row.resolution_px)): row for row in measurements.itertuples(index=False)}
    resolution_map = {(int(row.slice_index), str(row.phase_id), str(row.pair_id)): row for row in resolution.itertuples(index=False)}
    phase_map = {(int(row.slice_index), int(row.resolution_px), str(row.phase_pair)): row for row in phase.itertuples(index=False)}

    config = ImportedSTLWindingConfig(pixel_resolution=1000, slice_count=801)
    triangles, lower, upper, source_hash, _ = load_imported_stl_triangles(SOURCE, config, expected_sha256=contract["source"]["sha256"])
    z_values = np.linspace(lower[2], upper[2], 801)
    z_values[0] = np.nextafter(lower[2], upper[2])
    z_values[-1] = np.nextafter(upper[2], lower[2])
    masks: dict[tuple[int, str, int], np.ndarray] = {}
    replay_rows: list[dict[str, object]] = []
    for index, (z_mm, active) in enumerate(active_triangle_subsets_z(triangles, z_values)):
        if index not in SELECTED:
            continue
        base, _ = oriented_section_z(active, z_mm)
        for resolution_px in RESOLUTIONS:
            pixel_size = 40.0 / resolution_px
            for phase_id, (phase_x, phase_y) in PHASES.items():
                segments = np.asarray(base, dtype=float).copy()
                if len(segments):
                    segments[:, [0, 2]] += phase_x * pixel_size
                    segments[:, [1, 3]] += phase_y * pixel_size
                mask, _ = winding_raster(segments, lower_xy=lower[:2], upper_xy=upper[:2], pixels=resolution_px)
                masks[(index, phase_id, resolution_px)] = mask
                expected = measurement_map[(index, phase_id, resolution_px)]
                image = cv2.imread(str(ROOT / expected.image_path), cv2.IMREAD_GRAYSCALE)
                image_mask = image > 0 if image is not None else np.zeros((0, 0), dtype=bool)
                observed_hash = mask_packedbits_sha256(mask)
                component_count, hole_count = topology(mask, resolution_px)
                replay_rows.append({
                    "slice_index": index,
                    "resolution_px": resolution_px,
                    "phase_id": phase_id,
                    "source_hash_exact": source_hash == contract["source"]["sha256"],
                    "packed_hash_exact": observed_hash == expected.mask_packedbits_sha256,
                    "png_exact": image_mask.shape == mask.shape and bool(np.array_equal(image_mask, mask)),
                    "area_fraction_error": abs(float(mask.mean()) - float(expected.area_fraction)),
                    "component_count_exact": component_count == int(expected.component_count_filtered),
                    "hole_count_exact": hole_count == int(expected.hole_count_filtered),
                })

    metric_rows: list[dict[str, object]] = []
    for index in SELECTED:
        for phase_id in PHASES:
            for low, high in RESOLUTION_PAIRS:
                observed = compare(masks[(index, phase_id, low)], masks[(index, phase_id, high)], int(math.ceil(high / low)) + 1)
                expected = resolution_map[(index, phase_id, f"P{low}_P{high}")]
                metric_rows.append({
                    "kind": "resolution",
                    "key": f"{index}:{phase_id}:P{low}_P{high}",
                    "iou_error": abs(observed["iou"] - float(expected.iou)),
                    "area_error": abs(observed["relative_area_difference"] - float(expected.relative_area_difference)),
                    "boundary_error": abs(observed["boundary_band_explained_fraction"] - float(expected.boundary_band_explained_fraction)),
                })
        for resolution_px in RESOLUTIONS:
            for left, right in combinations(PHASES, 2):
                observed = compare(masks[(index, left, resolution_px)], masks[(index, right, resolution_px)], 2)
                expected = phase_map[(index, resolution_px, f"{left}_{right}")]
                metric_rows.append({
                    "kind": "phase",
                    "key": f"{index}:P{resolution_px}:{left}_{right}",
                    "iou_error": abs(observed["iou"] - float(expected.iou)),
                    "area_error": abs(observed["relative_area_difference"] - float(expected.relative_area_difference)),
                    "boundary_error": abs(observed["boundary_band_explained_fraction"] - float(expected.boundary_band_explained_fraction)),
                })

    guard_rows = list(csv.DictReader(GUARD.open(encoding="utf-8-sig")))
    protected = []
    for row in guard_rows:
        if row["guard_kind"].startswith("site_"):
            continue
        path = ROOT / row["path"]
        protected.append(path.is_file() and sha256(path) == row["before_sha256"])

    run_manifest_ok, run_manifest_count = manifest_valid(RUN)
    result_manifest_ok, result_manifest_count = manifest_valid(RESULT)
    max_metric_error = max(max(float(row[field]) for row in metric_rows) for field in ("iou_error", "area_error", "boundary_error"))
    gates = {
        "source_hash_exact": source_hash == contract["source"]["sha256"],
        "mask_replay_144": len(replay_rows) == 144 and all(bool(row["packed_hash_exact"]) and bool(row["png_exact"]) and float(row["area_fraction_error"]) <= 1.0e-15 and bool(row["component_count_exact"]) and bool(row["hole_count_exact"]) for row in replay_rows),
        "metric_replay_432": len(metric_rows) == 432 and max_metric_error <= 1.0e-12,
        "producer_decision_consistent": decision["decision_label"] in {"screening_pass_benign_discretization", "hold_resolution_or_pixel_phase_unresolved"},
        "run_manifest": run_manifest_ok,
        "result_manifest": result_manifest_ok,
        "protected_file_assets": len(protected) == 26 and all(protected),
        "no_full801": len(set(int(row["slice_index"]) for row in replay_rows)) == 9,
    }
    status = "passed" if all(gates.values()) else "failed"
    write_csv(TABLES / f"{RUN_ID}_independent_mask_replay.csv", replay_rows)
    write_csv(TABLES / f"{RUN_ID}_independent_metric_replay.csv", metric_rows)
    qa = {
        "status": status,
        "gates": gates,
        "mask_rows": len(replay_rows),
        "metric_rows": len(metric_rows),
        "max_metric_error": max_metric_error,
        "protected_file_assets": f"{sum(protected)}/{len(protected)}",
        "run_manifest_rows": run_manifest_count,
        "result_manifest_rows": result_manifest_count,
    }
    write_json(RESULT / "INDEPENDENT_QA.json", qa)
    print(json.dumps(qa, ensure_ascii=False, indent=2))
    if status != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
