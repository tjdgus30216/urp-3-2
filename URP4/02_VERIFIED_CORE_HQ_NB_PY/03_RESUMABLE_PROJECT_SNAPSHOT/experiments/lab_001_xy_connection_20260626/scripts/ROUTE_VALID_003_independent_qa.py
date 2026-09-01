"""Independent, read-only QA for ROUTE-VALID-003 F1 Route A/B/C evidence."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
TABLES = LAB / "reports" / "tables"
RUN_ID = os.environ.get("ROUTE_VALID_003_RUN_ID", "ROUTE-VALID-003-20260729-001")
RUN = LAB / "runs" / "ROUTE-VALID-003" / RUN_ID
RESULT = LAB / "results" / "ROUTE-VALID-003" / RUN_ID
EXPECTED_SIZE_MM = 40.0
SELECTED = (0, 1, 100, 200, 400, 600, 700, 799, 800)
RESOLUTIONS = (500, 750, 1000, 1500)
PHASES = ("P00", "P50X", "P50Y", "P50XY")
IMSTL007_RUN = LAB / "runs" / "I007" / "IMSTL-007-20260728-002"
IMSTL007_MEASUREMENTS = TABLES / "IMSTL-007-20260728-002_mask_measurements.csv"
PROTECTED_BASELINE = LAB / "results" / "HQ-BLUEPRINT-001" / "PROTECTED_ASSET_BASELINE.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fields = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)


def packed_hash(mask: np.ndarray) -> str:
    return hashlib.sha256(np.packbits(np.asarray(mask, dtype=np.uint8).reshape(-1), bitorder="big").tobytes()).hexdigest()


def load_mask(path: Path) -> np.ndarray:
    image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise RuntimeError(f"unreadable mask: {path}")
    return np.asarray(image > 0, dtype=bool)


def recompute(reference: np.ndarray, candidate: np.ndarray, resolution: int) -> dict[str, float | int]:
    a, b = np.asarray(reference, dtype=bool), np.asarray(candidate, dtype=bool)
    inter, union = int(np.logical_and(a, b).sum()), int(np.logical_or(a, b).sum())
    diff = np.logical_xor(a, b)
    count = int(diff.sum())
    kernel = np.ones((5, 5), dtype=np.uint8)
    band = cv2.morphologyEx(np.maximum(a, b).astype(np.uint8), cv2.MORPH_GRADIENT, kernel).astype(bool)
    return {
        "mask_iou": inter / union if union else 1.0,
        "symmetric_difference_pixels": count,
        "symmetric_difference_area_mm2": float(count * (EXPECTED_SIZE_MM / resolution) ** 2),
        "area_relative_delta": abs(int(a.sum()) - int(b.sum())) / max(int(a.sum()), 1),
        "boundary_band_explained_fraction": 1.0 if count == 0 else float(np.logical_and(diff, band).sum() / count),
    }


def protected_audit() -> bool:
    baseline = json.loads(PROTECTED_BASELINE.read_text(encoding="utf-8"))
    return all((ROOT / asset["path"]).is_file() and sha256_file(ROOT / asset["path"]) == asset["before_sha256"] for asset in baseline["assets"] if asset["asset_kind"] == "file")


def main() -> None:
    required = [
        RUN / "COMMON_RASTER_CONTRACT.json", RESULT / "COMMON_RASTER_CONTRACT.json", RUN / "OUTPUT_MANIFEST.csv", RESULT / "OUTPUT_MANIFEST.csv",
        TABLES / f"{RUN_ID}_source_evidence_replay.csv", TABLES / f"{RUN_ID}_route_A_mask_registry.csv", TABLES / f"{RUN_ID}_route_B_mask_registry.csv", TABLES / f"{RUN_ID}_route_C_reused_mask_registry.csv",
        TABLES / f"{RUN_ID}_A_B_144_comparisons.csv", TABLES / f"{RUN_ID}_A_C_144_comparisons.csv", IMSTL007_RUN / "OUTPUT_MANIFEST.csv", IMSTL007_MEASUREMENTS,
    ]
    if any(not path.is_file() for path in required):
        raise RuntimeError("ROUTE-VALID-003 producer artifacts incomplete; independent QA not run")
    contract = json.loads((RUN / "COMMON_RASTER_CONTRACT.json").read_text(encoding="utf-8"))
    a_rows = read_csv(TABLES / f"{RUN_ID}_route_A_mask_registry.csv")
    b_rows = read_csv(TABLES / f"{RUN_ID}_route_B_mask_registry.csv")
    c_rows = read_csv(TABLES / f"{RUN_ID}_route_C_reused_mask_registry.csv")
    ab_rows = read_csv(TABLES / f"{RUN_ID}_A_B_144_comparisons.csv")
    ac_rows = read_csv(TABLES / f"{RUN_ID}_A_C_144_comparisons.csv")
    expected_keys = {(index, resolution, phase) for index in SELECTED for resolution in RESOLUTIONS for phase in PHASES}
    def keyed(rows: list[dict[str, str]]) -> dict[tuple[int, int, str], dict[str, str]]:
        result = {(int(row["slice_index"]), int(row["resolution_px"]), str(row["phase_id"])): row for row in rows}
        if set(result) != expected_keys or len(result) != 144:
            raise RuntimeError("unexpected 144-case registry key set")
        return result
    amap, bmap, cmap = keyed(a_rows), keyed(b_rows), keyed(c_rows)
    i007_manifest = {row["relative_path"]: row for row in read_csv(IMSTL007_RUN / "OUTPUT_MANIFEST.csv")}
    i007_map = keyed(read_csv(IMSTL007_MEASUREMENTS))
    rows: list[dict[str, object]] = []
    max_error = 0.0
    for key in sorted(expected_keys):
        a, b, c = amap[key], bmap[key], cmap[key]
        path_a, path_b, path_c = ROOT / a["png_path"], ROOT / b["png_path"], ROOT / c["reused_from_image_path"]
        ma, mb, mc = load_mask(path_a), load_mask(path_b), load_mask(path_c)
        rel_c = path_c.resolve().relative_to(IMSTL007_RUN.resolve()).as_posix()
        source_c = i007_map[key]
        c_integrity = rel_c in i007_manifest and sha256_file(path_c) == i007_manifest[rel_c]["sha256"] and packed_hash(mc) == source_c["mask_packedbits_sha256"] and int(mc.sum()) == int(source_c["solid_pixels"])
        a_integrity = sha256_file(path_a) == a["png_sha256"] and packed_hash(ma) == a["mask_packedbits_sha256"] and int(ma.sum()) == int(a["solid_pixels"])
        b_integrity = sha256_file(path_b) == b["png_sha256"] and packed_hash(mb) == b["mask_packedbits_sha256"] and int(mb.sum()) == int(b["solid_pixels"])
        for comparison_id, reference, candidate, producer in (("A-B", ma, mb, next(row for row in ab_rows if (int(row["slice_index"]),int(row["resolution_px"]),str(row["phase_id"])) == key)), ("A-C", ma, mc, next(row for row in ac_rows if (int(row["slice_index"]),int(row["resolution_px"]),str(row["phase_id"])) == key))):
            rec = recompute(reference, candidate, key[1])
            error = max(abs(float(producer[field]) - float(rec[field])) for field in rec)
            max_error = max(max_error, error)
            rows.append({"comparison_id": comparison_id, "slice_index": key[0], "resolution_px": key[1], "phase_id": key[2], "A_png_integrity": a_integrity, "B_png_integrity": b_integrity, "C_reused_manifest_integrity": c_integrity, "max_metric_error": error, "metric_replay_pass": error <= 1.0e-12})
    checks = {
        "common_contract_run_id": contract.get("run_id") == RUN_ID,
        "common_contract_exact_grid": tuple(contract.get("selected_slice_indices", [])) == SELECTED and tuple(contract.get("resolutions_px", [])) == RESOLUTIONS and set(contract.get("phases_pixel", {})) == set(PHASES),
        "single_explicit_common_transform": contract.get("common_transform", {}).get("forbidden") == ["ICP", "rotation", "route-specific bbox fit", "independent alignment"],
        "route_A_rows_144": len(a_rows) == 144,
        "route_B_rows_144": len(b_rows) == 144,
        "route_C_reused_rows_144": len(c_rows) == 144 and all(str(row.get("runtime_s")) == "reused_no_recompute" for row in c_rows),
        "all_new_mask_integrity": all(bool(row["A_png_integrity"]) and bool(row["B_png_integrity"]) for row in rows),
        "all_reused_C_integrity": all(bool(row["C_reused_manifest_integrity"]) for row in rows),
        "comparison_rows_288": len(ab_rows) == 144 and len(ac_rows) == 144,
        "independent_metric_replay": all(bool(row["metric_replay_pass"]) for row in rows),
        "protected_files_unchanged": protected_audit(),
        "no_C_regeneration": all("runs/I007/IMSTL-007-20260728-002/masks/" in str(row["reused_from_image_path"]).replace("\\", "/") for row in c_rows),
    }
    payload = {"work_id": "ROUTE-VALID-003_F1_STEP_REFERENCE_PIXEL_PHASE_AND_RESOLUTION_STRESS_TEST_NO_Y", "run_id": RUN_ID, "status": "passed" if all(checks.values()) else "failed", "checks": checks, "recomputed_comparisons": len(rows), "max_metric_error": max_error, "scope": "independent read-only replay; no source, mask, descriptor, Excel, y, training, or notebook mutation"}
    write_csv(TABLES / f"{RUN_ID}_independent_qa.csv", rows)
    (RESULT / "INDEPENDENT_QA.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
