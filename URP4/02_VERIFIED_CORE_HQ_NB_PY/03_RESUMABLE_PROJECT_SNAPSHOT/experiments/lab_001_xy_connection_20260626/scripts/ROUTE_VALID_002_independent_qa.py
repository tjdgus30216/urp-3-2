"""Read-only independent QA for ROUTE-VALID-002 B1/L7 selected-slice packet."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
TABLES = LAB / "reports" / "tables"
RESULT = LAB / "results" / "ROUTE-VALID-002" / "ROUTE-VALID-002-20260729-001"
RUN_ID = "ROUTE-VALID-002-20260729-001"
PACKET = RESULT / "ROUTE_VALID_002_PACKET.json"
CONTRACT = TABLES / f"{RUN_ID}_B1_L7_source_contract.csv"
MEASUREMENTS = TABLES / f"{RUN_ID}_route_ABC_measurements.csv"
COMPARISONS = TABLES / f"{RUN_ID}_B1_L7_comparisons.csv"
IMAGES = TABLES / f"{RUN_ID}_image_hash_registry.csv"
OUT = RESULT / "INDEPENDENT_QA.json"
OUT_TABLE = TABLES / f"{RUN_ID}_independent_qa.csv"
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


def image_metrics(a: np.ndarray, b: np.ndarray) -> dict[str, float | int]:
    a, b = a.astype(bool), b.astype(bool)
    union = int(np.logical_or(a, b).sum())
    inter = int(np.logical_and(a, b).sum())
    symmetric = int(np.logical_xor(a, b).sum())
    return {
        "mask_iou": inter / union if union else 1.0,
        "symmetric_difference_pixels": symmetric,
        "area_relative_delta": abs(int(a.sum()) - int(b.sum())) / max(int(a.sum()), 1),
    }


def main() -> None:
    if "kmk312" not in str(Path(sys.executable).resolve()).lower() or sys.version_info[:2] != (3, 12):
        raise RuntimeError("ROUTE-VALID-002 independent QA requires KMK312 Python 3.12.12")
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    contracts = {row["model_id"]: row for row in read_csv(CONTRACT)}
    measurements = read_csv(MEASUREMENTS)
    comparisons = {(row["model_id"], row["comparison_id"], int(row["resolution_px"])): row for row in read_csv(COMPARISONS)}
    image_rows = read_csv(IMAGES)
    images = {(row["model_id"], row["route"], int(row["resolution_px"])): row for row in image_rows}
    expected_keys = {(model, route, resolution) for model in ("B1", "L7") for route in ("A", "B", "C") for resolution in (500, 1000)}

    replay_ok = True
    exact_pair_values = True
    for model in ("B1", "L7"):
        for resolution in (500, 1000):
            masks: dict[str, np.ndarray] = {}
            for route in ("A", "B", "C"):
                item = images[(model, route, resolution)]
                path = Path(item["path"])
                image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
                valid = path.is_file() and sha256_file(path) == item["sha256"] and image is not None and image.shape == (resolution, resolution)
                replay_ok &= valid
                masks[route] = image > 0
            for comp, candidate in (("A-B", "B"), ("A-C", "C")):
                observed = image_metrics(masks["A"], masks[candidate])
                declared = comparisons[(model, comp, resolution)]
                replay_ok &= all(float(declared[key]) == value for key, value in observed.items())
                exact_pair_values &= observed["mask_iou"] == 1.0 and observed["symmetric_difference_pixels"] == 0 and observed["area_relative_delta"] == 0.0

    c_rows = [row for row in measurements if row["route"] == "C"]
    adapter_b1 = all(row["explicit_n40_grid_adapter_used"] == "True" and float(row["bbox_residual_to_N40_mm"]) <= 1.0e-3 for row in c_rows if row["model_id"] == "B1")
    adapter_l7 = all(row["explicit_n40_grid_adapter_used"] == "False" and float(row["bbox_residual_to_N40_mm"]) == 0.0 for row in c_rows if row["model_id"] == "L7")
    baseline = json.loads(PROTECTED_BASELINE.read_text(encoding="utf-8"))
    protected = [asset for asset in baseline["assets"] if asset["asset_kind"] == "file"]
    protected_ok = all((ROOT / a["path"]).is_file() and sha256_file(ROOT / a["path"]) == a["before_sha256"] for a in protected)
    result_files = [path.name for path in RESULT.iterdir() if path.is_file()]
    checks = {
        "contract_exactly_B1_L7": set(contracts) == {"B1", "L7"} and all(row["contract_status"] == "passed" for row in contracts.values()),
        "all_pair_source_hashes_replay": all(row["stp_hash_match"] == "True" and row["stl_hash_match"] == "True" for row in contracts.values()),
        "measurement_row_count_12": len(measurements) == 12,
        "image_registry_exact_expected_12": set(images) == expected_keys and len(images) == 12,
        "image_hash_shape_replay": replay_ok,
        "metric_replay_exact": replay_ok,
        "all_reported_A_B_A_C_values_exact": exact_pair_values,
        "route_ab_scope_is_same_source_only": all("same_source_STEP" in row["comparison_scope"] for key, row in comparisons.items() if key[1] == "A-B"),
        "route_ac_scope_is_confirmed_pair": all("confirmed_source_pair" in row["comparison_scope"] for key, row in comparisons.items() if key[1] == "A-C"),
        "B1_adapter_is_explicit_and_bounded": adapter_b1,
        "L7_uses_frozen_square_grid_without_adapter": adapter_l7,
        "no_unapproved_model_images": all(name.startswith(("B1_", "L7_", "ROUTE_", "INDEPENDENT")) for name in result_files),
        "scope_stop_preserved": "C1 not re-executed" in packet["scope_stop"] and "full Z801" in packet["scope_stop"],
        "protected_file_hashes_unchanged": protected_ok,
    }
    rows = [{"check_id": key, "status": "PASS" if value else "FAIL", "observed": str(value)} for key, value in checks.items()]
    with OUT_TABLE.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    result = {
        "work_id": "ROUTE-VALID-002_B1_L7_CONFIRMED_PAIR_CROSS_FAMILY_SELECTED_SLICE_VALIDATION_NO_Y",
        "run_id": RUN_ID,
        "status": "passed" if all(checks.values()) else "failed",
        "checks": checks,
        "scope": "read-only image/hash/metric replay; no new slice, descriptor, y, or model calculation.",
        "qa_table": str(OUT_TABLE),
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
