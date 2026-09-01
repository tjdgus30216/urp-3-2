from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

import pandas as pd


RUN_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = RUN_DIR.parents[4]
sys.path.insert(0, str(RUN_DIR))

from implementation.contracts import SOURCE_SHA256, WORKBOOK_SHA256
from implementation.folds import FOLD_COLUMNS
from implementation.hashing import sha256_file


def main():
    checks = []
    def check(check_id, condition, observed, expected):
        checks.append({"check_id": check_id, "status": "PASS" if condition else "FAIL", "observed": observed, "expected": expected})

    manifest = json.loads((RUN_DIR / "IMPLEMENTATION_MANIFEST.json").read_text(encoding="utf-8"))
    source = PROJECT_ROOT / "experiments/lab_001_xy_connection_20260626/data/raw/professor_training_20260709/Training_260419-2nd method - New feature - Good. vibration.ipynb"
    workbook = PROJECT_ROOT / "experiments/lab_001_xy_connection_20260626/data/raw/professor_training_20260709/Total data_260503.xlsx"
    check("IQA-001", sha256_file(source) == SOURCE_SHA256, sha256_file(source), SOURCE_SHA256)
    check("IQA-002", sha256_file(workbook) == WORKBOOK_SHA256, sha256_file(workbook), WORKBOOK_SHA256)

    lineage = pd.read_csv(RUN_DIR / "SOURCE_FUNCTION_LINEAGE.csv")
    check("IQA-003", len(lineage) >= 50 and lineage.symbol.nunique() >= 50, f"rows={len(lineage)} unique={lineage.symbol.nunique()}", ">=50")
    dataset = json.loads((RUN_DIR / "artifacts/DATASET_MANIFEST.json").read_text(encoding="utf-8"))
    check("IQA-004", (dataset["rows"], dataset["x_features"], dataset["targets"]) == (198, 169, 16), [dataset["rows"], dataset["x_features"], dataset["targets"]], [198, 169, 16])

    target_ledger = pd.read_csv(RUN_DIR / "artifacts/TARGET_SAMPLE_LEDGER.csv")
    counts = (int((target_ledger.final_refit_parity == "primary").sum()), int((target_ledger.final_refit_parity == "hold").sum()))
    check("IQA-005", counts == (13, 3), counts, (13, 3))

    fold_meta = json.loads((RUN_DIR / "artifacts/SHARED_FOLD_MANIFEST.meta.json").read_text(encoding="utf-8"))
    fold_path = RUN_DIR / "artifacts/SHARED_FOLD_MANIFEST.csv"
    check("IQA-006", sha256_file(fold_path) == fold_meta["sha256"], sha256_file(fold_path), fold_meta["sha256"])
    fold_head = pd.read_csv(fold_path, nrows=5)
    check("IQA-007", list(fold_head.columns) == list(FOLD_COLUMNS), list(fold_head.columns), list(FOLD_COLUMNS))

    fold_qa = pd.read_csv(RUN_DIR / "GROUP_AND_FOLD_MANIFEST_QA.csv")
    check("IQA-008", fold_qa.status.eq("PASS").all(), f"{int(fold_qa.status.eq('PASS').sum())}/{len(fold_qa)}", f"{len(fold_qa)}/{len(fold_qa)}")
    negative = pd.read_csv(RUN_DIR / "NEGATIVE_FAIL_CLOSED_QA.csv")
    check("IQA-009", negative.status.eq("PASS").all(), f"{int(negative.status.eq('PASS').sum())}/{len(negative)}", f"{len(negative)}/{len(negative)}")

    proof = json.loads((RUN_DIR / "NO_FIT_PROOF.json").read_text(encoding="utf-8"))
    no_fit = proof["completed_fit_calls"] == 0 and proof["completed_predict_calls"] == 0 and proof["prediction_rows"] == 0 and proof["metric_rows"] == 0
    check("IQA-010", no_fit, {key: proof[key] for key in ("completed_fit_calls", "completed_predict_calls", "prediction_rows", "metric_rows")}, "all zero")

    protected = pd.read_csv(RUN_DIR / "PROTECTED_ASSET_HASH_AUDIT.csv")
    check("IQA-011", protected.status.eq("PASS").all(), f"{int(protected.status.eq('PASS').sum())}/{len(protected)}", f"{len(protected)}/{len(protected)}")
    parity001_tol = PROJECT_ROOT / "experiments/lab_001_xy_connection_20260626/results/TRAIN-PARITY-001/TRAIN-PARITY-001-20260801-001/PREDICTION_METRIC_TOLERANCE_REGISTRY.csv"
    tolerance = pd.read_csv(parity001_tol)
    check("IQA-012", set(tolerance.revision) == {"TRAIN-PARITY-TOL-v0.1"} and manifest["tolerance_revision"] == "TRAIN-PARITY-TOL-v0.1", sorted(set(tolerance.revision)), ["TRAIN-PARITY-TOL-v0.1"])

    required = [
        "IMPLEMENTATION_MANIFEST.json", "SOURCE_FUNCTION_LINEAGE.csv", "DATASET_EXTRACTOR_QA.csv",
        "GROUP_AND_FOLD_MANIFEST_QA.csv", "STAGE_GRAPH_COVERAGE.csv", "OBSERVABILITY_EVENT_SCHEMA.csv",
        "PREDICTION_METRIC_LEDGER_SCHEMA.csv", "NEGATIVE_FAIL_CLOSED_QA.csv", "NO_FIT_PROOF.json",
        "PROTECTED_ASSET_HASH_AUDIT.csv",
    ]
    missing = [name for name in required if not (RUN_DIR / name).exists()]
    check("IQA-013", not missing, missing, [])
    implementation_files = manifest["implementation_files"]
    hash_drift = [row["path"] for row in implementation_files if sha256_file(RUN_DIR / row["path"]) != row["sha256"]]
    check("IQA-014", not hash_drift, hash_drift, [])

    stage = pd.read_csv(RUN_DIR / "STAGE_GRAPH_COVERAGE.csv")
    branch = stage[stage.stage == "method_branch"]
    check("IQA-015", len(branch) == 10 and branch.coverage_status.eq("source_ast_bound_no_fit_execution").all(), len(branch), 10)
    check("IQA-016", manifest["implementation_state"] == "partial_branch_coverage", manifest["implementation_state"], "partial_branch_coverage")

    result = {
        "run_id": "TRAIN-PARITY-002-20260801-001",
        "execution_status": "no_fit_no_prediction",
        "qa_passed": sum(row["status"] == "PASS" for row in checks),
        "qa_total": len(checks),
        "overall_status": "PASS" if all(row["status"] == "PASS" for row in checks) else "FAIL",
        "implementation_state": manifest["implementation_state"],
        "ready_for_parity_execution_gate": False,
        "reason": "Fit-dependent source branches are source-AST-bound and specified but do not yet have independently executable exact numerical adapters.",
        "checks": checks,
    }
    (RUN_DIR / "INDEPENDENT_QA.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
