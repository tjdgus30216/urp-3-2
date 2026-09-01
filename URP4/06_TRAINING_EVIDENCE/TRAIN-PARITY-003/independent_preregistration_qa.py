from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
RUN = Path(__file__).resolve().parent
OUTPUT = RUN / "PREREGISTRATION_QA.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def check(checks, check_id, condition, observed, expected):
    checks.append({"check_id": check_id, "status": "PASS" if condition else "FAIL", "observed": observed, "expected": expected})


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError("independent preregistration QA already executed; exactly-once guard")

    required = [
        "REPORT.md", "SENTINEL_TARGET_SELECTION.csv", "CONTROLLED_EXECUTION_CONTRACT.json",
        "SOURCE_REFERENCE_ADAPTER_BINDING.csv", "STAGE_PARITY_LEDGER_SCHEMA.csv",
        "RESOURCE_AND_RUNTIME_ESTIMATE.csv", "FAIL_CLOSED_STOP_CONDITIONS.csv",
        "EXECUTION_PERMIT_DRAFT.json", "MERGE_PACKET.md",
    ]
    contract = json.loads((RUN / "CONTROLLED_EXECUTION_CONTRACT.json").read_text(encoding="utf-8"))
    permit = json.loads((RUN / "EXECUTION_PERMIT_DRAFT.json").read_text(encoding="utf-8"))
    build = json.loads((RUN / "BUILD_STATE.json").read_text(encoding="utf-8"))
    selection = rows(RUN / "SENTINEL_TARGET_SELECTION.csv")
    stages = rows(RUN / "STAGE_PARITY_LEDGER_SCHEMA.csv")
    stops = rows(RUN / "FAIL_CLOSED_STOP_CONDITIONS.csv")
    bindings = rows(RUN / "SOURCE_REFERENCE_ADAPTER_BINDING.csv")

    source = ROOT / "experiments/lab_001_xy_connection_20260626/data/raw/professor_training_20260709/Training_260419-2nd method - New feature - Good. vibration.ipynb"
    workbook = ROOT / "experiments/lab_001_xy_connection_20260626/data/raw/professor_training_20260709/Total data_260503.xlsx"
    p2a = ROOT / "experiments/lab_001_xy_connection_20260626/results/TRAIN-PARITY-002A/TRAIN-PARITY-002A-20260801-001"
    p2a_manifest = json.loads((p2a / "IMPLEMENTATION_MANIFEST.json").read_text(encoding="utf-8"))
    fold = ROOT / "experiments/lab_001_xy_connection_20260626/results/TRAIN-PARITY-002/TRAIN-PARITY-002-20260801-001/artifacts/SHARED_FOLD_MANIFEST.csv"
    tol = ROOT / "experiments/lab_001_xy_connection_20260626/results/TRAIN-PARITY-001/TRAIN-PARITY-001-20260801-001/PREDICTION_METRIC_TOLERANCE_REGISTRY.csv"

    checks = []
    check(checks, "QA-001", all((RUN / p).exists() for p in required), sum((RUN / p).exists() for p in required), len(required))
    check(checks, "QA-002", sha256(source) == contract["hash_bindings"]["source_notebook"], sha256(source), contract["hash_bindings"]["source_notebook"])
    check(checks, "QA-003", sha256(workbook) == contract["hash_bindings"]["source_workbook"], sha256(workbook), contract["hash_bindings"]["source_workbook"])
    check(checks, "QA-004", sha256(fold) == contract["hash_bindings"]["fold_manifest"], sha256(fold), contract["hash_bindings"]["fold_manifest"])
    check(checks, "QA-005", sha256(tol) == contract["hash_bindings"]["tolerance_registry"], sha256(tol), contract["hash_bindings"]["tolerance_registry"])
    impl_ok = 0
    for item in p2a_manifest["implementation_files"]:
        if sha256(p2a / item["path"]) == item["sha256"]:
            impl_ok += 1
    check(checks, "QA-006", impl_ok == 8, impl_ok, 8)
    check(checks, "QA-007", len(selection) == 16, len(selection), 16)
    mismatch_count = sum(r["crosswalk_exact"] == "false" for r in selection)
    check(checks, "QA-008", mismatch_count == 16, mismatch_count, 16)
    check(checks, "QA-009", contract["blocker_evidence"]["adapter_baked_hold_columns"] == ["FW", "GA", "HE"], contract["blocker_evidence"]["adapter_baked_hold_columns"], ["FW", "GA", "HE"])
    check(checks, "QA-010", contract["blocker_evidence"]["hold_columns_implied_by_confirmed_target_names"] == ["GC", "HE", "HK"], contract["blocker_evidence"]["hold_columns_implied_by_confirmed_target_names"], ["GC", "HE", "HK"])
    check(checks, "QA-011", [r["stage_id"] for r in stages] == [f"P{i}" for i in range(9)], [r["stage_id"] for r in stages], [f"P{i}" for i in range(9)])
    check(checks, "QA-012", stages[-1]["comparison_rule"] == "prohibited in sentinel pilot", stages[-1]["comparison_rule"], "prohibited in sentinel pilot")
    check(checks, "QA-013", contract["tolerance"]["revision"] == "TRAIN-PARITY-TOL-v0.1", contract["tolerance"]["revision"], "TRAIN-PARITY-TOL-v0.1")
    check(checks, "QA-014", contract["decision"] == "NO_GO_WITH_BLOCKER", contract["decision"], "NO_GO_WITH_BLOCKER")
    check(checks, "QA-015", permit["status"] == "NOT_ISSUED_NO_GO_CONTRACT_DRIFT" and not permit["execution_authorized"], [permit["status"], permit["execution_authorized"]], ["NOT_ISSUED_NO_GO_CONTRACT_DRIFT", False])
    check(checks, "QA-016", permit["permitted_stages"] == [] and permit["prohibited_stages"] == [f"P{i}" for i in range(9)], [permit["permitted_stages"], permit["prohibited_stages"]], [[], [f"P{i}" for i in range(9)]])
    check(checks, "QA-017", sum(r["active_now"] == "true" for r in stops) == 1 and next(r for r in stops if r["active_now"] == "true")["stop_id"] == "STOP-005", [r["stop_id"] for r in stops if r["active_now"] == "true"], ["STOP-005"])
    counts = contract["fit_predict_metric_counts"]
    check(checks, "QA-018", list(counts.values()) == [0, 0, 0, 0] and build["fit_calls"] == 0 and build["predict_calls"] == 0, [counts, build], "fit/predict/prediction/metric all zero")
    forbidden_ext = {".pkl", ".pickle", ".joblib", ".onnx", ".pt", ".pth", ".h5"}
    model_artifacts = [str(p.relative_to(RUN)) for p in RUN.rglob("*") if p.is_file() and p.suffix.lower() in forbidden_ext]
    check(checks, "QA-019", not model_artifacts, model_artifacts, [])
    check(checks, "QA-020", sum(r["status"] == "hash_verified" for r in bindings) == 12, sum(r["status"] == "hash_verified" for r in bindings), 12)

    passed = sum(c["status"] == "PASS" for c in checks)
    result = {
        "run_id": "TRAIN-PARITY-003-20260801-001",
        "qa_execution_count": 1,
        "execution_status": "no_fit_no_prediction",
        "qa_passed": passed,
        "qa_total": len(checks),
        "overall_status": "PASS" if passed == len(checks) else "FAIL",
        "final_decision": "NO_GO_WITH_BLOCKER",
        "blocker": "TARGET_IDENTITY_AND_HOLD_POLICY_CROSSWALK_DRIFT",
        "fit_calls": 0,
        "predict_calls": 0,
        "prediction_rows": 0,
        "metric_rows": 0,
        "checks": checks,
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if passed != len(checks):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
