from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd


RUN_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = RUN_DIR.parents[4]
sys.path.insert(0, str(RUN_DIR))

from implementation.contracts import FOLD_MANIFEST_SHA256, HOLD_TARGETS, SOURCE_SHA256, TARGETS, TOLERANCE_REVISION
from implementation.hashing import sha256_file
from implementation.source_exact_runtime import SourceExactRuntime


def main():
    checks = []
    def add(check_id, ok, observed, expected):
        checks.append({"check_id": check_id, "status": "PASS" if ok else "FAIL", "observed": observed, "expected": expected})

    manifest = json.loads((RUN_DIR / "IMPLEMENTATION_MANIFEST.json").read_text(encoding="utf-8"))
    source = PROJECT_ROOT / "experiments/lab_001_xy_connection_20260626/data/raw/professor_training_20260709/Training_260419-2nd method - New feature - Good. vibration.ipynb"
    prev_fold = PROJECT_ROOT / "experiments/lab_001_xy_connection_20260626/results/TRAIN-PARITY-002/TRAIN-PARITY-002-20260801-001/artifacts/SHARED_FOLD_MANIFEST.csv"
    add("IQA-001", sha256_file(source) == SOURCE_SHA256, sha256_file(source), SOURCE_SHA256)
    add("IQA-002", sha256_file(prev_fold) == FOLD_MANIFEST_SHA256, sha256_file(prev_fold), FOLD_MANIFEST_SHA256)

    runtime = SourceExactRuntime(source).compile()
    status = pd.read_csv(RUN_DIR / "BRANCH_IMPLEMENTATION_STATUS.csv")
    lineage = pd.read_csv(RUN_DIR / "SOURCE_TO_ADAPTER_NUMERICAL_LINEAGE.csv")
    stage = pd.read_csv(RUN_DIR / "BRANCH_STAGE_AND_OBJECTIVE_MATRIX.csv")
    fixture = pd.read_csv(RUN_DIR / "STATIC_AND_FIXTURE_QA.csv")
    add("IQA-003", len(runtime.branch_lineage) == 10, len(runtime.branch_lineage), 10)
    add("IQA-004", len(status) == 10 and status.branch_id.nunique() == 10, [len(status), status.branch_id.nunique()], [10, 10])
    add("IQA-005", status.status.eq("exact_port_complete_no_fit").all(), status.status.value_counts().to_dict(), {"exact_port_complete_no_fit": 10})
    add("IQA-006", len(lineage) == 10 and lineage.branch_ast_hash.nunique() >= 7, [len(lineage), lineage.branch_ast_hash.nunique()], [10, ">=7"])
    add("IQA-007", lineage.proxy_substitution.astype(str).str.lower().eq("false").all(), lineage.proxy_substitution.tolist(), "all false")
    add("IQA-008", len(stage) == 10 and stage.status.eq("exact_port_complete_no_fit").all(), len(stage), 10)
    add("IQA-009", fixture.status.eq("PASS").all(), f"{int(fixture.status.eq('PASS').sum())}/{len(fixture)}", f"{len(fixture)}/{len(fixture)}")
    add("IQA-010", len(TARGETS) == 16 and len(HOLD_TARGETS) == 3, [len(TARGETS), len(HOLD_TARGETS)], [16, 3])
    add("IQA-011", manifest["predecessor_fold_manifest_sha256"] == FOLD_MANIFEST_SHA256, manifest["predecessor_fold_manifest_sha256"], FOLD_MANIFEST_SHA256)
    add("IQA-012", manifest["tolerance_revision"] == TOLERANCE_REVISION, manifest["tolerance_revision"], TOLERANCE_REVISION)

    proof = json.loads((RUN_DIR / "NO_FIT_PROOF.json").read_text(encoding="utf-8"))
    zeros = [proof["completed_fit_calls"], proof["completed_predict_calls"], proof["prediction_rows"], proof["metric_rows"]]
    add("IQA-013", zeros == [0, 0, 0, 0], zeros, [0, 0, 0, 0])
    protected = pd.read_csv(RUN_DIR / "PROTECTED_ASSET_HASH_AUDIT.csv")
    add("IQA-014", protected.status.eq("PASS").all(), f"{int(protected.status.eq('PASS').sum())}/{len(protected)}", f"{len(protected)}/{len(protected)}")
    drift = [row["path"] for row in manifest["implementation_files"] if sha256_file(RUN_DIR / row["path"]) != row["sha256"]]
    add("IQA-015", not drift, drift, [])
    add("IQA-016", manifest["overall_state"] == "ready_for_controlled_execution_preregistration", manifest["overall_state"], "ready_for_controlled_execution_preregistration")
    add("IQA-017", manifest["exact_port_complete_no_fit"] == 10, manifest["exact_port_complete_no_fit"], 10)

    required = ["BRANCH_IMPLEMENTATION_STATUS.csv", "SOURCE_TO_ADAPTER_NUMERICAL_LINEAGE.csv", "BRANCH_STAGE_AND_OBJECTIVE_MATRIX.csv", "STATIC_AND_FIXTURE_QA.csv", "NONDETERMINISM_AND_FALLBACK_INSTRUMENTATION.csv", "NO_FIT_PROOF.json", "PROTECTED_ASSET_HASH_AUDIT.csv"]
    missing = [name for name in required if not (RUN_DIR / name).exists()]
    add("IQA-018", not missing, missing, [])
    result = {
        "run_id": "TRAIN-PARITY-002A-20260801-001", "execution_status": "no_fit_no_prediction",
        "qa_passed": sum(row["status"] == "PASS" for row in checks), "qa_total": len(checks),
        "overall_status": "PASS" if all(row["status"] == "PASS" for row in checks) else "FAIL",
        "overall_state": manifest["overall_state"], "controlled_execution_preregistration_entry": all(row["status"] == "PASS" for row in checks),
        "checks": checks,
    }
    (RUN_DIR / "INDEPENDENT_QA.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
