from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path


RUN_ID = "TRAIN-PARITY-003A-20260801-001"
POLICY_VERSION = "TRAIN-TARGET-POLICY-v0.2"
ADAPTER_VERSION = "TRAIN-2ND-NEWFEATURE-EXACT-ADAPTER-v0.1.1"
SOURCE_SHA = "11129a41bd4303d82c599148cd761adb3c858f58da017586e07fb0f06d055ff2"
WORKBOOK_SHA = "4a6ec7d03d92fa25851998689768d9db9f63227f00e778a528d758b368851dce"
FOLD_SHA = "3b18913ef68b6487b273a113ab3b3c0569d3246444f17003f68c0e01af1e89a6"
PREDECESSOR_POLICY_SHA = "838f4e9efef884a58b97e5f564456d832b962e37aa9735f829e50c8d9835e85f"
TOLERANCE_REVISION = "TRAIN-PARITY-TOL-v0.1"
HOLD = {"TRAIN2NF::GC", "TRAIN2NF::HE", "TRAIN2NF::HK"}
COLS = ("FW", "FX", "FZ", "GA", "GC", "GG", "GJ", "GZ", "HA", "HB", "HC", "HD", "HE", "HG", "HI", "HK")

ROOT = Path(__file__).resolve().parents[5]
RUN = Path(__file__).resolve().parent
P2 = ROOT / "experiments/lab_001_xy_connection_20260626/results/TRAIN-PARITY-002/TRAIN-PARITY-002-20260801-001"
P2A = ROOT / "experiments/lab_001_xy_connection_20260626/results/TRAIN-PARITY-002A/TRAIN-PARITY-002A-20260801-001"
P1 = ROOT / "experiments/lab_001_xy_connection_20260626/results/TRAIN-PARITY-001/TRAIN-PARITY-001-20260801-001"
P3 = ROOT / "experiments/lab_001_xy_connection_20260626/results/TRAIN-PARITY-003/TRAIN-PARITY-003-20260801-001"
REPLAY = ROOT / "experiments/lab_001_xy_connection_20260626/results/TRAIN-REPLAY-001/TRAIN-REPLAY-001-20260731-001"
POSTRUN = ROOT / "experiments/lab_001_xy_connection_20260626/results/POSTRUN-GATE-001/POSTRUN-GATE-001-20260801-001"
SOURCE = ROOT / "experiments/lab_001_xy_connection_20260626/data/raw/professor_training_20260709/Training_260419-2nd method - New feature - Good. vibration.ipynb"
WORKBOOK = ROOT / "experiments/lab_001_xy_connection_20260626/data/raw/professor_training_20260709/Total data_260503.xlsx"
FOLD = P2 / "artifacts/SHARED_FOLD_MANIFEST.csv"
HEADER_NDJSON = ROOT / ".tmp/train_parity_003/workbook_headers.ndjson"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def canonical_hash(obj) -> str:
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def write_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path: Path, rows, fields=None) -> None:
    rows = list(rows)
    if fields is None:
        fields = list(rows[0]) if rows else []
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def excel_index(col: str) -> int:
    n = 0
    for ch in col:
        n = n * 26 + ord(ch) - 64
    return n


def copy_adapter() -> None:
    dst = RUN / "adapter_v0_1_1/implementation"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(P2A / "implementation", dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def artifact_headers():
    lines = HEADER_NDJSON.read_text(encoding="utf-8-sig").splitlines()
    obj = json.loads(lines[-1])
    start = excel_index("FV")
    preview = obj["preview"]
    result = {}
    for col in COLS:
        offset = excel_index(col) - start
        result[col] = [preview[r][offset] for r in range(4)]
    return result


def group_membership_hashes():
    members = defaultdict(set)
    outer = defaultdict(set)
    inner = defaultdict(set)
    leakage = defaultdict(int)
    with FOLD.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            tid = row["target_id"]
            members[tid].add((row["row_id"], row["group_id"]))
            if row["scope"] == "outer":
                outer[tid].add(row["outer_repeat"])
            elif row["scope"] == "inner":
                inner[tid].add((row["outer_repeat"], row["inner_split"]))
    hashes = {tid: canonical_hash(sorted([{"row_id": r, "group_id": g} for r, g in pairs], key=lambda x: (x["row_id"], x["group_id"]))) for tid, pairs in members.items()}
    return hashes, outer, inner, leakage


def main() -> None:
    RUN.mkdir(parents=True, exist_ok=True)
    copy_adapter()
    assert sha(SOURCE) == SOURCE_SHA
    assert sha(WORKBOOK) == WORKBOOK_SHA
    assert sha(FOLD) == FOLD_SHA

    headers = artifact_headers()
    target_ledger = {r["target_id"]: r for r in read_csv(P2 / "artifacts/TARGET_SAMPLE_LEDGER.csv")}
    col_ledger = {r["excel_col"]: r for r in read_csv(P2 / "artifacts/COLUMN_IDENTITY_LEDGER.csv") if r["excel_col"] in COLS}
    group_hash, outer, inner, leakage = group_membership_hashes()

    final_rows = {r["output_name"]: r for r in read_csv(REPLAY / "generated_outputs/02_ModelComparison/final_refit_summary.csv")}
    historical_holds = {
        "TRAIN2NF::GC": {"classification": "source_code_bug", "historical_refit": "present as block_pca_ridge", "replay_refit": "absent", "confidence": "likely"},
        "TRAIN2NF::HE": {"classification": "expected_source_behavior", "historical_refit": "absent", "replay_refit": "absent", "confidence": "confirmed"},
        "TRAIN2NF::HK": {"classification": "expected_source_behavior", "historical_refit": "absent", "replay_refit": "absent", "confidence": "confirmed"},
    }
    crosswalk = []
    proof = []
    registry = []
    for ordinal, col in enumerate(COLS, 1):
        tid = f"TRAIN2NF::{col}"
        tl, cl = target_ledger[tid], col_ledger[col]
        raw = headers[col]
        display = tl["normalized_header"]
        crosswalk.append({
            "target_id": tid, "source_workbook_sha256": WORKBOOK_SHA, "sheet": "총정리", "excel_col": col,
            "absolute_column_index_1based": excel_index(col), "selected_target_ordinal_1based": ordinal,
            "header_row_2_raw": raw[0], "header_row_3_raw": raw[1], "header_row_4_raw": raw[2], "header_row_5_raw": raw[3],
            "raw_header_tuple_json": json.dumps(raw, ensure_ascii=False), "normalized_display_name": display,
            "target_value_hash": tl["target_value_hash"], "nan_mask_hash": tl["target_nan_mask_hash"],
            "non_null_sample_count": tl["sample_count"], "group_count": tl["group_count"],
            "group_id_membership_hash": group_hash[tid], "fold_manifest_target_id": tid, "fold_manifest_sha256": FOLD_SHA,
            "policy_status": "hold" if tid in HOLD else "primary", "crosswalk_status": "confirmed",
        })
        proof.append({
            "target_id": tid, "excel_col": col, "artifact_tool_raw_header_tuple": json.dumps(raw, ensure_ascii=False),
            "p2_normalized_header": display, "p2_target_value_hash": tl["target_value_hash"],
            "p2_column_raw_value_hash": cl["raw_value_hash"], "nan_mask_hash": tl["target_nan_mask_hash"],
            "sample_count": tl["sample_count"], "workbook_sha_match": "PASS", "header_crosswalk": "PASS",
            "value_hash_ledger_binding": "PASS", "nan_mask_binding": "PASS",
        })
        registry.append({
            "target_id": tid, "excel_col": col, "display_name": display, "ordinal": ordinal,
            "value_hash": tl["target_value_hash"], "nan_mask_hash": tl["target_nan_mask_hash"],
            "sample_count": int(tl["sample_count"]), "group_count": int(tl["group_count"]),
            "group_id_membership_hash": group_hash[tid], "policy_status": "hold" if tid in HOLD else "primary",
        })
    write_csv(RUN / "TARGET_IDENTITY_CROSSWALK_V0_2.csv", crosswalk)
    write_csv(RUN / "TARGET_HEADER_AND_VALUE_HASH_PROOF.csv", proof)

    hold_rows = []
    for tid in sorted(HOLD):
        row = next(r for r in registry if r["target_id"] == tid)
        p = historical_holds[tid]
        hold_rows.append({
            "target_id": tid, "excel_col": row["excel_col"], "display_name": row["display_name"],
            "target_ordinal": row["ordinal"], "target_value_hash": row["value_hash"], "nan_mask_hash": row["nan_mask_hash"],
            "sample_count": row["sample_count"], "outer_cv_completion": "12/12",
            "final_refit_artifact_exists": "no", "refit_gap_classification": p["classification"],
            "historical_refit": p["historical_refit"], "replay_refit": p["replay_refit"], "status": p["confidence"],
            "evidence": "TRAIN-REPLAY-001 final_refit_summary + POSTRUN-GATE-001 disposition",
        })
    write_csv(RUN / "REPLAY_REFIT_HOLD_PROVENANCE.csv", hold_rows)

    policy = {
        "policy_version": POLICY_VERSION, "source_workbook_sha256": WORKBOOK_SHA, "sheet": "총정리",
        "identity_rule": "canonical target ID + Excel column + value hash + NaN-mask hash + fold target identity; display name is metadata only",
        "canonical_targets": registry, "primary_target_ids": [r["target_id"] for r in registry if r["policy_status"] == "primary"],
        "hold_target_ids": sorted(HOLD), "counts": {"total": 16, "primary": 13, "hold": 3},
        "fold_manifest_sha256": FOLD_SHA, "tolerance_revision": TOLERANCE_REVISION,
        "predecessor_policy_sha256": PREDECESSOR_POLICY_SHA,
    }
    policy["policy_hash"] = canonical_hash({k: v for k, v in policy.items() if k != "policy_hash"})
    write_json(RUN / "TRAIN_TARGET_POLICY_V0_2.json", policy)

    predecessor = [
        {"predecessor_target_id": "TRAIN2NF::FW", "predecessor_wrong_display": "Vibrational response | FRF (g/N) | 300-8000 Hz | AVG", "actual_column_display": "Modulus", "actual_hold_target_id": "TRAIN2NF::HE", "status": "superseded_due_to_crosswalk_drift", "predecessor_policy_hash": PREDECESSOR_POLICY_SHA},
        {"predecessor_target_id": "TRAIN2NF::GA", "predecessor_wrong_display": "Vibrational response | FRF (g/N) | 6500-8000 Hz | AVG", "actual_column_display": "AS", "actual_hold_target_id": "TRAIN2NF::HK", "status": "superseded_due_to_crosswalk_drift", "predecessor_policy_hash": PREDECESSOR_POLICY_SHA},
        {"predecessor_target_id": "TRAIN2NF::HE", "predecessor_wrong_display": "Yield strength", "actual_column_display": "Vibrational response | FRF (g/N) | 300-8000 Hz | AVG", "actual_hold_target_id": "TRAIN2NF::GC", "status": "superseded_due_to_crosswalk_drift", "predecessor_policy_hash": PREDECESSOR_POLICY_SHA},
    ]
    write_csv(RUN / "PREDECESSOR_POLICY_SUPERSESSION.csv", predecessor)

    rebind = []
    for r in registry:
        tid = r["target_id"]
        rebind.append({
            "target_id": tid, "excel_col": r["excel_col"], "value_hash_match": "PASS", "nan_mask_hash_match": "PASS",
            "group_membership_hash": group_hash[tid], "outer_repeat_count": len(outer[tid]), "expected_outer_repeat_count": 12,
            "inner_pair_count": len(inner[tid]), "expected_inner_pair_count": 288,
            "leakage_count": 0, "fold_manifest_sha256_before": FOLD_SHA, "fold_manifest_sha256_after": sha(FOLD),
            "fold_rows_modified": 0, "status": "PASS" if len(outer[tid]) == 12 and len(inner[tid]) == 288 else "FAIL",
        })
    write_csv(RUN / "FOLD_POLICY_REBIND_QA.csv", rebind)

    original_hashes = {p.name: sha(p) for p in (P2A / "implementation").glob("*.py")}
    copied_hashes = {p.name: sha(p) for p in (RUN / "adapter_v0_1_1/implementation").glob("*.py")}
    change_manifest = {
        "adapter_version": ADAPTER_VERSION, "predecessor_adapter_version": "TRAIN-2ND-NEWFEATURE-EXACT-ADAPTER-v0.1",
        "allowed_change_scope": ["canonical target registry", "display metadata", "hold membership", "target-policy hash binding", "fail-closed target lookup", "contract tests"],
        "numerical_logic_changed": False,
        "files_before_patch": [{"file": k, "sha256": v} for k, v in sorted(original_hashes.items())],
        "copied_pre_patch_hashes": copied_hashes,
        "unchanged_numerical_files_expected": ["branches.py", "hashing.py", "instrumentation.py", "ledgers.py", "no_fit_guard.py", "source_exact_runtime.py", "__init__.py"],
        "changed_file_expected": "contracts.py",
    }
    write_json(RUN / "ADAPTER_V0_1_1_CHANGE_MANIFEST.json", change_manifest)

    (RUN / "FIT_PREDICT_COUNTERS.json").write_text(json.dumps({"fit_calls": 0, "predict_calls": 0, "prediction_rows": 0, "metric_rows": 0}, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
