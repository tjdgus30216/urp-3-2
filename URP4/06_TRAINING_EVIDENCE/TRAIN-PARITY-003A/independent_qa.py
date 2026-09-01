from __future__ import annotations

import csv
import hashlib
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path


RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
OUT = RUN / "INDEPENDENT_QA.json"
P2 = ROOT / "experiments/lab_001_xy_connection_20260626/results/TRAIN-PARITY-002/TRAIN-PARITY-002-20260801-001"
P2A = ROOT / "experiments/lab_001_xy_connection_20260626/results/TRAIN-PARITY-002A/TRAIN-PARITY-002A-20260801-001"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def canon(obj) -> str:
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main() -> None:
    if OUT.exists():
        raise RuntimeError("INDEPENDENT_QA_ALREADY_EXISTS: exactly-once guard")
    checks = []

    def check(qid, name, observed, expected, passed=None):
        ok = (observed == expected) if passed is None else bool(passed)
        checks.append({"qa_id": qid, "check": name, "observed": observed, "expected": expected, "status": "PASS" if ok else "FAIL"})

    required = [
        "REPORT.md", "TARGET_IDENTITY_CROSSWALK_V0_2.csv", "TARGET_HEADER_AND_VALUE_HASH_PROOF.csv",
        "REPLAY_REFIT_HOLD_PROVENANCE.csv", "TRAIN_TARGET_POLICY_V0_2.json", "PREDECESSOR_POLICY_SUPERSESSION.csv",
        "ADAPTER_V0_1_1_CHANGE_MANIFEST.json", "FOLD_POLICY_REBIND_QA.csv", "SOURCE_REFERENCE_RUNNER_PREFLIGHT.csv",
        "TARGET_POLICY_NEGATIVE_QA.csv", "PREREGISTRATION_READJUDICATION.json", "EXECUTION_PERMIT.json", "MERGE_PACKET.md",
    ]
    check("IQA-001", "pre-IQA required artifacts", sum((RUN / n).exists() for n in required), len(required))

    cross = read_csv(RUN / "TARGET_IDENTITY_CROSSWALK_V0_2.csv")
    expected_ids = [f"TRAIN2NF::{c}" for c in ("FW", "FX", "FZ", "GA", "GC", "GG", "GJ", "GZ", "HA", "HB", "HC", "HD", "HE", "HG", "HI", "HK")]
    check("IQA-002", "canonical target IDs and order", [r["target_id"] for r in cross], expected_ids)
    check("IQA-003", "crosswalk statuses", sum(r["crosswalk_status"] == "confirmed" for r in cross), 16)
    check("IQA-004", "raw header tuples retained", sum(bool(r["raw_header_tuple_json"]) for r in cross), 16)

    policy = json.loads((RUN / "TRAIN_TARGET_POLICY_V0_2.json").read_text(encoding="utf-8"))
    expected_policy_hash = canon({k: v for k, v in policy.items() if k != "policy_hash"})
    check("IQA-005", "target-policy self hash", policy["policy_hash"], expected_policy_hash)
    check("IQA-006", "canonical hold IDs", policy["hold_target_ids"], ["TRAIN2NF::GC", "TRAIN2NF::HE", "TRAIN2NF::HK"])
    check("IQA-007", "primary/hold counts", [len(policy["primary_target_ids"]), len(policy["hold_target_ids"])], [13, 3])

    proof = read_csv(RUN / "TARGET_HEADER_AND_VALUE_HASH_PROOF.csv")
    check("IQA-008", "header/value/NaN proof", sum(all(r[k] == "PASS" for k in ("workbook_sha_match", "header_crosswalk", "value_hash_ledger_binding", "nan_mask_binding")) for r in proof), 16)
    holds = read_csv(RUN / "REPLAY_REFIT_HOLD_PROVENANCE.csv")
    check("IQA-009", "replay hold provenance IDs", sorted(r["target_id"] for r in holds), ["TRAIN2NF::GC", "TRAIN2NF::HE", "TRAIN2NF::HK"])
    supersede = read_csv(RUN / "PREDECESSOR_POLICY_SUPERSESSION.csv")
    check("IQA-010", "predecessor policy superseded, not erased", sum(r["status"] == "superseded_due_to_crosswalk_drift" for r in supersede), 3)

    fold = P2 / "artifacts/SHARED_FOLD_MANIFEST.csv"
    check("IQA-011", "frozen fold manifest SHA", sha(fold), "3b18913ef68b6487b273a113ab3b3c0569d3246444f17003f68c0e01af1e89a6")
    rebind = read_csv(RUN / "FOLD_POLICY_REBIND_QA.csv")
    check("IQA-012", "16-target fold rebind QA", sum(r["status"] == "PASS" and r["fold_rows_modified"] == "0" and r["leakage_count"] == "0" for r in rebind), 16)

    manifest = json.loads((RUN / "ADAPTER_V0_1_1_CHANGE_MANIFEST.json").read_text(encoding="utf-8"))
    check("IQA-013", "numerical branch hashes unchanged", manifest["numerical_files_hash_unchanged"], True)
    check("IQA-014", "contract-only versioned change", [manifest["contracts_changed"], manifest["numerical_logic_changed"]], [True, False])

    preflight = read_csv(RUN / "SOURCE_REFERENCE_RUNNER_PREFLIGHT.csv")
    check("IQA-015", "isolated source runner preflight", sum(r["status"] == "PASS" for r in preflight), len(preflight))
    negative = read_csv(RUN / "TARGET_POLICY_NEGATIVE_QA.csv")
    check("IQA-016", "target policy negative QA", sum(r["status"] == "PASS" for r in negative), len(negative))
    branch = read_csv(RUN / "ADAPTER_BRANCH_NO_FIT_QA.csv")
    check("IQA-017", "ten branch NO_FIT guard", sum(r["status"] == "PASS" for r in branch), 10)

    counters = json.loads((RUN / "FIT_PREDICT_COUNTERS.json").read_text(encoding="utf-8"))
    check("IQA-018", "fit/predict/prediction/metric counts", list(counters.values()), [0, 0, 0, 0])
    adjud = json.loads((RUN / "PREREGISTRATION_READJUDICATION.json").read_text(encoding="utf-8"))
    check("IQA-019", "same target/value/fold consumption", adjud["source_and_adapter_same_target_value_fold"], True)
    check("IQA-020", "re-adjudication decision", adjud["decision"], "GO_FOR_TRAIN_PARITY_004_SENTINEL_EXECUTION")

    permit = json.loads((RUN / "EXECUTION_PERMIT.json").read_text(encoding="utf-8"))
    permit_shape = [permit["status"], permit["target_id"], permit["outer_repeat"], permit["stages"], permit["prohibited_stages"], permit["approval_required"], permit["execution_performed_in_003a"]]
    expected_shape = ["READY_AWAITING_EXPLICIT_EXECUTION_APPROVAL", "TRAIN2NF::HI", 0, [f"P{i}" for i in range(8)], ["P8"], True, False]
    check("IQA-021", "sentinel execution permit shape", permit_shape, expected_shape)

    protected = read_csv(P2A / "PROTECTED_ASSET_HASH_AUDIT.csv")
    current_pass = 0
    for row in protected:
        path = ROOT / row["asset_path"]
        if path.exists() and sha(path).lower() == row["after_sha256"].lower():
            current_pass += 1
    check("IQA-022", "protected asset current hashes", current_pass, len(protected))
    check("IQA-023", "canonical KMK312 runtime", [str(Path(sys.executable).resolve()), sys.version.split()[0]], [str((ROOT / "tools/envs/KMK312/python.exe").resolve()), "3.12.12"])

    passed = sum(c["status"] == "PASS" for c in checks)
    result = {
        "run_id": "TRAIN-PARITY-003A-20260801-001", "qa_execution_count": 1,
        "runner_attempt_count": 2,
        "prior_attempt_disposition": "aborted_before_QA_artifact_commit_due_to_WindowsPath_JSON_serialization; no QA result or project state committed",
        "executed_at_kst": datetime.now(timezone(timedelta(hours=9))).isoformat(timespec="seconds"),
        "independent_qa_passed": passed, "independent_qa_total": len(checks),
        "overall_status": "PASS" if passed == len(checks) else "FAIL",
        "fit_calls": 0, "predict_calls": 0, "prediction_rows": 0, "metric_rows": 0,
        "checks": checks,
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = (RUN / "REPORT.md").read_text(encoding="utf-8")
    report = report.replace("Independent QA: pending exactly-one execution", f"Independent QA: **{passed}/{len(checks)} {result['overall_status']}** (exactly one execution)")
    (RUN / "REPORT.md").write_text(report, encoding="utf-8")
    merge = (RUN / "MERGE_PACKET.md").read_text(encoding="utf-8")
    merge = merge.replace("Independent QA: pending exactly-one execution", f"Independent QA: **{passed}/{len(checks)} {result['overall_status']}** (exactly one execution)")
    merge = merge.replace("Merge recommendation: pending independent QA", "Merge recommendation: **YES — versioned target-policy/contract repair only; actual execution remains approval-locked**" if result["overall_status"] == "PASS" else "Merge recommendation: **NO — independent QA failed**")
    (RUN / "MERGE_PACKET.md").write_text(merge, encoding="utf-8")


if __name__ == "__main__":
    main()
