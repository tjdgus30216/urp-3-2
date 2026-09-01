"""Independent read-only QA for ROUTE-VALID-001 C1 bounded pilot."""

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
RESULT = LAB / "results" / "ROUTE-VALID-001" / "ROUTE-VALID-001-20260729-001"
RUN_ID = "ROUTE-VALID-001-20260729-001"
PACKET = RESULT / "ROUTE_VALID_001_C1_PACKET.json"
ELIGIBILITY = TABLES / f"{RUN_ID}_source_eligibility.csv"
METRICS = TABLES / f"{RUN_ID}_C1_three_route_selected_slice_metrics.csv"
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


def metrics(reference: np.ndarray, candidate: np.ndarray) -> dict[str, float | int]:
    reference, candidate = reference.astype(bool), candidate.astype(bool)
    union = int(np.logical_or(reference, candidate).sum())
    inter = int(np.logical_and(reference, candidate).sum())
    sym = int(np.logical_xor(reference, candidate).sum())
    return {
        "mask_iou": inter / union if union else 1.0,
        "symmetric_difference_pixels": sym,
        "area_relative_delta": abs(int(reference.sum()) - int(candidate.sum())) / max(int(reference.sum()), 1),
    }


def main() -> None:
    if "kmk312" not in str(Path(sys.executable).resolve()).lower() or sys.version_info[:2] != (3, 12):
        raise RuntimeError("ROUTE-VALID-001 independent QA requires KMK312 Python 3.12")
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    eligibility = {row["model_id"]: row for row in read_csv(ELIGIBILITY)}
    source = eligibility["C1"]
    image_rows = {row["route"]: row for row in read_csv(Path(packet["image_registry"]))}
    a_path, b_path, c_path = (Path(image_rows[key]["path"]) for key in ("A", "B", "C"))
    masks = {key: cv2.imread(str(path), cv2.IMREAD_GRAYSCALE) for key, path in {"A": a_path, "B": b_path, "C": c_path}.items()}
    if any(mask is None or mask.shape != (1000, 1000) for mask in masks.values()):
        raise RuntimeError("independent QA could not load all C1 P1000 artifacts")
    ab = metrics(masks["A"] > 0, masks["B"] > 0)
    ac = metrics(masks["A"] > 0, masks["C"] > 0)
    expected_metrics = {row["comparison_id"]: row for row in read_csv(METRICS)}
    baseline = json.loads(PROTECTED_BASELINE.read_text(encoding="utf-8"))
    protected_files = [asset for asset in baseline["assets"] if asset["asset_kind"] == "file"]
    protected_hashes = {
        asset["alias"] + "::" + asset["path"]: (
            (ROOT / asset["path"]).is_file()
            and sha256_file(ROOT / asset["path"]) == asset["before_sha256"]
        )
        for asset in protected_files
    }
    checks = {
        "eligibility_exact_count_58": len(eligibility) == 58,
        "eligibility_counts_24_9_25": {
            state: sum(row["eligibility_status"] == state for row in eligibility.values())
            for state in ("paired_confirmed", "paired_likely", "stl_only")
        } == {"paired_confirmed": 24, "paired_likely": 9, "stl_only": 25},
        "no_missing_or_hash_mismatch": not any(row["eligibility_status"] == "missing_or_hash_mismatch" for row in eligibility.values()),
        "c1_pair_confirmed": source["eligibility_status"] == "paired_confirmed" and source["official_route_ac_eligibility"] == "eligible",
        "c1_registered_step_hash": sha256_file(Path(source["stp_path"]) if Path(source["stp_path"]).is_absolute() else ROOT / source["stp_path"]) == source["stp_expected_sha256"],
        "c1_registered_stl_hash": sha256_file(Path(source["stl_path"]) if Path(source["stl_path"]).is_absolute() else ROOT / source["stl_path"]) == source["stl_expected_sha256"],
        "route_ab_metrics_recomputed": all(float(expected_metrics["C1-A-B"][key]) == value for key, value in ab.items()),
        "route_ac_metrics_recomputed": all(float(expected_metrics["C1-A-C"][key]) == value for key, value in ac.items()),
        "route_ab_same_source_label": "same-original-STEP" in packet["route_ab"]["route_ab_interpretation"],
        "route_c_hash_is_paired_stl": packet["route_c"]["source_geometry_sha256"] == source["stl_expected_sha256"],
        "route_c_output_hash": sha256_file(c_path) == packet["route_c"]["output_sha256"],
        "no_overreach_scope_stop": "B1/L7/F1/full-Z801 not executed" in packet["scope_stop"],
        "protected_file_hashes_unchanged": bool(protected_hashes) and all(protected_hashes.values()),
    }
    rows = [{"check_id": key, "status": "PASS" if value else "FAIL", "observed": str(value)} for key, value in checks.items()]
    with OUT_TABLE.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    result = {
        "run_id": RUN_ID,
        "status": "passed" if all(checks.values()) else "failed",
        "checks": checks,
        "recomputed_metrics": {"C1-A-B": ab, "C1-A-C": ac},
        "scope": "read-only QA; it does not calculate a new slice, descriptor, y, or model.",
        "qa_table": str(OUT_TABLE),
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
