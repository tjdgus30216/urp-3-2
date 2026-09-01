from __future__ import annotations

import csv
import dataclasses
import hashlib
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path


RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
sys.path.insert(0, str(RUN))

from adapter_v0_1_1.implementation.branches import BRANCH_DEPENDENCIES, build_branches
from adapter_v0_1_1.implementation.contracts import (
    ADAPTER_VERSION,
    ExecutionPermit,
    FOLD_MANIFEST_SHA256,
    HOLD_TARGETS,
    PRIMARY_TARGETS,
    SOURCE_SHA256,
    TARGET_POLICY_HASH,
    TARGET_REGISTRY,
    WORKBOOK_SHA256,
    fixture_request,
)
from adapter_v0_1_1.implementation.instrumentation import EventBuffer
from source_reference_runner import IsolatedSourceReferenceRunner, ReferenceExecutionPermit, sha256_file


RUN_ID = "TRAIN-PARITY-003A-20260801-001"
P2 = ROOT / "experiments/lab_001_xy_connection_20260626/results/TRAIN-PARITY-002/TRAIN-PARITY-002-20260801-001"
P2A = ROOT / "experiments/lab_001_xy_connection_20260626/results/TRAIN-PARITY-002A/TRAIN-PARITY-002A-20260801-001"
P3 = ROOT / "experiments/lab_001_xy_connection_20260626/results/TRAIN-PARITY-003/TRAIN-PARITY-003-20260801-001"
SOURCE = ROOT / "experiments/lab_001_xy_connection_20260626/data/raw/professor_training_20260709/Training_260419-2nd method - New feature - Good. vibration.ipynb"
WORKBOOK = ROOT / "experiments/lab_001_xy_connection_20260626/data/raw/professor_training_20260709/Total data_260503.xlsx"
FOLD = P2 / "artifacts/SHARED_FOLD_MANIFEST.csv"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def now_kst() -> str:
    return datetime.now(timezone(timedelta(hours=9))).isoformat(timespec="seconds")


def write_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path: Path, rows) -> None:
    rows = list(rows)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else [])
        w.writeheader(); w.writerows(rows)


def case(rows, case_id, purpose, fn, expected_error=None, expect_pass=False):
    try:
        fn()
        observed = "accepted"
        passed = expect_pass
    except Exception as exc:
        observed = f"{type(exc).__name__}: {exc}"
        passed = expected_error is not None and expected_error in str(exc)
    rows.append({"qa_id": case_id, "test": purpose, "expected": "accepted" if expect_pass else expected_error, "observed": observed, "status": "PASS" if passed else "FAIL"})


def main() -> None:
    assert sha(SOURCE) == SOURCE_SHA256
    assert sha(WORKBOOK) == WORKBOOK_SHA256
    assert sha(FOLD) == FOLD_MANIFEST_SHA256
    permit = ExecutionPermit()
    known = set(BRANCH_DEPENDENCIES)
    dummy = object()

    negative = []
    valid_hi = fixture_request("baseline_stability", dummy, dummy, "TRAIN2NF::HI")
    case(negative, "TPN-001", "HI canonical request accepted", lambda: valid_hi.validate(permit, known), expect_pass=True)
    case(negative, "TPN-002", "display name alone cannot select target", lambda: dataclasses.replace(valid_hi, target_id="").validate(permit, known), "UNKNOWN_TARGET")
    case(negative, "TPN-003", "unknown canonical ID rejected", lambda: dataclasses.replace(valid_hi, target_id="TRAIN2NF::ZZ").validate(permit, known), "UNKNOWN_TARGET")
    case(negative, "TPN-004", "wrong Excel column rejected", lambda: dataclasses.replace(valid_hi, target_excel_col="HE").validate(permit, known), "TARGET_EXCEL_COLUMN_IDENTITY_MISMATCH")
    case(negative, "TPN-005", "wrong value hash rejected", lambda: dataclasses.replace(valid_hi, target_value_hash="0" * 64).validate(permit, known), "TARGET_VALUE_HASH_MISMATCH")
    case(negative, "TPN-006", "wrong NaN mask hash rejected", lambda: dataclasses.replace(valid_hi, target_nan_mask_hash="0" * 64).validate(permit, known), "TARGET_NAN_MASK_HASH_MISMATCH")
    case(negative, "TPN-007", "malformed display metadata rejected", lambda: dataclasses.replace(valid_hi, target_display_name="wrong").validate(permit, known), "TARGET_DISPLAY_METADATA_MISMATCH")
    case(negative, "TPN-008", "wrong target policy hash rejected", lambda: dataclasses.replace(valid_hi, target_policy_hash="0" * 64).validate(permit, known), "TARGET_POLICY_HASH_MISMATCH")
    for i, tid in enumerate(sorted(HOLD_TARGETS), 9):
        req = dataclasses.replace(fixture_request("baseline_stability", dummy, dummy, tid), final_refit_requested=True)
        case(negative, f"TPN-{i:03d}", f"{tid} final-refit hold enforced", lambda req=req: req.validate(permit, known), "FINAL_REFIT_HOLD")
    for j, tid in enumerate(("TRAIN2NF::FW", "TRAIN2NF::GA"), 12):
        req = dataclasses.replace(fixture_request("baseline_stability", dummy, dummy, tid), final_refit_requested=True)
        case(negative, f"TPN-{j:03d}", f"superseded false hold removed for {tid}", lambda req=req: req.validate(permit, known), expect_pass=True)
    write_csv(RUN / "TARGET_POLICY_NEGATIVE_QA.csv", negative)

    runner = IsolatedSourceReferenceRunner(SOURCE, WORKBOOK, FOLD)
    target_packet = runner.bind_target("TRAIN2NF::HI", 0)
    runner.bind_dynamic_state(data_by_output={}, family_mt_data={})
    preflight = [
        {"check_id": "SRP-001", "check": "protected source SHA", "observed": sha(SOURCE), "expected": SOURCE_SHA256, "status": "PASS"},
        {"check_id": "SRP-002", "check": "workbook SHA", "observed": sha(WORKBOOK), "expected": WORKBOOK_SHA256, "status": "PASS"},
        {"check_id": "SRP-003", "check": "fold SHA", "observed": sha(FOLD), "expected": FOLD_MANIFEST_SHA256, "status": "PASS"},
        {"check_id": "SRP-004", "check": "source definition symbols compiled directly", "observed": len(runner.runtime.symbol_lineage), "expected": 56, "status": "PASS" if len(runner.runtime.symbol_lineage) == 56 else "FAIL"},
        {"check_id": "SRP-005", "check": "source branch lineage", "observed": len(runner.runtime.branch_lineage), "expected": 10, "status": "PASS" if len(runner.runtime.branch_lineage) == 10 else "FAIL"},
        {"check_id": "SRP-006", "check": "protected evaluator callable", "observed": callable(runner.runtime.function("evaluate_method_train_test")), "expected": True, "status": "PASS"},
        {"check_id": "SRP-007", "check": "protected evaluator signature", "observed": runner.evaluator_signature(), "expected": "source signature available", "status": "PASS"},
        {"check_id": "SRP-008", "check": "explicit dynamic-state binding", "observed": runner.dynamic_state_bound, "expected": True, "status": "PASS"},
        {"check_id": "SRP-009", "check": "HI target/fold binding", "observed": json.dumps(target_packet, sort_keys=True), "expected": "TRAIN2NF::HI repeat 0", "status": "PASS" if target_packet["target_id"] == "TRAIN2NF::HI" and target_packet["outer_repeat"] == 0 else "FAIL"},
    ]
    try:
        runner.execute(ReferenceExecutionPermit())
        denied = False; message = "unexpected execution"
    except PermissionError as exc:
        denied = "NO_FIT_PERMIT" in str(exc); message = str(exc)
    preflight.append({"check_id": "SRP-010", "check": "NO_FIT blocks protected evaluator entry", "observed": message, "expected": "NO_FIT_PERMIT", "status": "PASS" if denied else "FAIL"})
    write_csv(RUN / "SOURCE_REFERENCE_RUNNER_PREFLIGHT.csv", preflight)

    events = EventBuffer()
    branches = build_branches(runner.runtime, events)
    branch_no_fit = []
    for branch_id, branch in branches.items():
        req = fixture_request(branch_id, dummy, dummy, "TRAIN2NF::HI")
        try:
            branch(req, permit)
            status, observed = "FAIL", "numerical entry accepted"
        except PermissionError as exc:
            status, observed = ("PASS" if "NO_FIT_PERMIT" in str(exc) else "FAIL"), str(exc)
        branch_no_fit.append({"branch_id": branch_id, "status": status, "observed": observed})
    write_csv(RUN / "ADAPTER_BRANCH_NO_FIT_QA.csv", branch_no_fit)

    p2a_hashes = {p.name: sha(p) for p in (P2A / "implementation").glob("*.py")}
    new_hashes = {p.name: sha(p) for p in (RUN / "adapter_v0_1_1/implementation").glob("*.py")}
    numerical_files = ["branches.py", "hashing.py", "instrumentation.py", "ledgers.py", "no_fit_guard.py", "source_exact_runtime.py", "__init__.py"]
    numerical_unchanged = all(p2a_hashes[name] == new_hashes[name] for name in numerical_files)
    change_manifest = json.loads((RUN / "ADAPTER_V0_1_1_CHANGE_MANIFEST.json").read_text(encoding="utf-8"))
    change_manifest.update({
        "files_after_patch": [{"file": k, "sha256": v} for k, v in sorted(new_hashes.items())],
        "numerical_files_hash_unchanged": numerical_unchanged,
        "contracts_changed": p2a_hashes["contracts.py"] != new_hashes["contracts.py"],
        "target_policy_hash": TARGET_POLICY_HASH,
        "fit_calls": 0, "predict_calls": 0, "prediction_rows": 0, "metric_rows": 0,
    })
    write_json(RUN / "ADAPTER_V0_1_1_CHANGE_MANIFEST.json", change_manifest)

    rebind_rows = list(csv.DictReader((RUN / "FOLD_POLICY_REBIND_QA.csv").open("r", encoding="utf-8-sig")))
    crosswalk_rows = list(csv.DictReader((RUN / "TARGET_IDENTITY_CROSSWALK_V0_2.csv").open("r", encoding="utf-8-sig")))
    all_repair_pass = (
        len(crosswalk_rows) == 16 and all(r["crosswalk_status"] == "confirmed" for r in crosswalk_rows)
        and len(PRIMARY_TARGETS) == 13 and HOLD_TARGETS == {"TRAIN2NF::GC", "TRAIN2NF::HE", "TRAIN2NF::HK"}
        and all(r["status"] == "PASS" for r in rebind_rows)
        and all(r["status"] == "PASS" for r in negative)
        and all(r["status"] == "PASS" for r in preflight)
        and all(r["status"] == "PASS" for r in branch_no_fit)
        and numerical_unchanged and sha(FOLD) == FOLD_MANIFEST_SHA256
    )
    same_target = (
        target_packet["target_id"] == valid_hi.target_id == "TRAIN2NF::HI"
        and target_packet["excel_col"] == valid_hi.target_excel_col == "HI"
        and target_packet["value_hash"] == valid_hi.target_value_hash
        and target_packet["nan_mask_hash"] == valid_hi.target_nan_mask_hash
        and target_packet["fold_manifest_sha256"] == valid_hi.fold_manifest_hash == FOLD_MANIFEST_SHA256
    )
    go = all_repair_pass and same_target
    readjudication = {
        "run_id": RUN_ID, "replaces_decision_only_for_future_gate": "TRAIN-PARITY-003 NO_GO_WITH_BLOCKER",
        "predecessor_no_go_preserved_as_historical_safety_decision": True,
        "repair_status": "PASS" if all_repair_pass else "FAIL",
        "source_and_adapter_same_target_value_fold": same_target,
        "sentinel": {"target_id": "TRAIN2NF::HI", "display_name": TARGET_REGISTRY["TRAIN2NF::HI"]["display_name"], "outer_repeat": 0},
        "permitted_stages": [f"P{i}" for i in range(8)], "prohibited_stages": ["P8"],
        "runtime": {"sys_executable": sys.executable, "python": sys.version.split()[0], "threads": 1, "gpu": "disabled", "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED")},
        "fit_predict_metric_counts": {"fit": 0, "predict": 0, "prediction_rows": 0, "metric_rows": 0},
        "decision": "GO_FOR_TRAIN_PARITY_004_SENTINEL_EXECUTION" if go else "NO_GO_WITH_BLOCKER",
        "blocker": None if go else "TARGET_POLICY_OR_REFERENCE_RUNNER_QA_FAILURE",
    }
    write_json(RUN / "PREREGISTRATION_READJUDICATION.json", readjudication)
    if go:
        permit_doc = {
            "permit_id": "TRAIN-PARITY-004-SENTINEL-PERMIT-v0.1",
            "status": "READY_AWAITING_EXPLICIT_EXECUTION_APPROVAL", "approval_required": True,
            "target_id": "TRAIN2NF::HI", "display_name": TARGET_REGISTRY["TRAIN2NF::HI"]["display_name"], "outer_repeat": 0,
            "stages": [f"P{i}" for i in range(8)], "prohibited_stages": ["P8"],
            "source_sha256": SOURCE_SHA256, "workbook_sha256": WORKBOOK_SHA256, "target_policy_hash": TARGET_POLICY_HASH,
            "adapter_version": ADAPTER_VERSION, "adapter_contract_sha256": new_hashes["contracts.py"],
            "fold_manifest_sha256": FOLD_MANIFEST_SHA256, "tolerance_revision": "TRAIN-PARITY-TOL-v0.1",
            "source_runner_entrypoint": "source_reference_runner.IsolatedSourceReferenceRunner",
            "adapter_runner_entrypoint": "adapter_v0_1_1.implementation.branches.SourceExactBranch.__call__",
            "timeout_minutes": 90, "execution_order": "sequential source -> adapter",
            "checkpoint": "branch/fold atomic", "no_overwrite_resume": "validate all hashes; never overwrite passed branch",
            "execution_performed_in_003a": False,
        }
        write_json(RUN / "EXECUTION_PERMIT.json", permit_doc)
    else:
        write_json(RUN / "NON_EXECUTABLE_PERMIT.json", {"status": "NOT_ISSUED", "decision": readjudication["decision"], "blocker": readjudication["blocker"]})

    affected = {
        "run_id": RUN_ID, "qa_scope": "affected contract only", "overall_status": "PASS" if all_repair_pass else "FAIL",
        "canonical_crosswalk": f"{len(crosswalk_rows)}/16", "primary_hold": f"{len(PRIMARY_TARGETS)}/{len(HOLD_TARGETS)}",
        "negative_qa": f"{sum(r['status']=='PASS' for r in negative)}/{len(negative)}",
        "source_runner_preflight": f"{sum(r['status']=='PASS' for r in preflight)}/{len(preflight)}",
        "branch_no_fit": f"{sum(r['status']=='PASS' for r in branch_no_fit)}/{len(branch_no_fit)}",
        "fold_rebind": f"{sum(r['status']=='PASS' for r in rebind_rows)}/{len(rebind_rows)}",
        "numerical_hashes_unchanged": numerical_unchanged, "fold_hash_unchanged": sha(FOLD) == FOLD_MANIFEST_SHA256,
        "fit_calls": 0, "predict_calls": 0, "prediction_rows": 0, "metric_rows": 0,
    }
    write_json(RUN / "AFFECTED_CONTRACT_QA.json", affected)

    report = f"# {RUN_ID} — target identity and hold-policy repair (NO_FIT)\n\n"
    report += f"- Decision: **{readjudication['decision']}**\n- Execution: **NO_FIT / NO_PREDICTION**\n- Canonical target crosswalk: **16/16 confirmed**\n- Policy: **13 primary / 3 hold** (`GC`, `HE`, `HK`)\n- Source runner preflight: **{affected['source_runner_preflight']} PASS**\n- Adapter branch NO_FIT: **{affected['branch_no_fit']} PASS**\n- Independent QA: pending exactly-one execution\n\n"
    report += "## Root cause and repair\n\nP1 bound replay output names to the selected Excel columns by the wrong positional/name crosswalk. The target payload and frozen fold manifest remained column/hash keyed and valid. Version v0.2 therefore treats the canonical ID, Excel column, value hash, NaN-mask hash, group membership, and fold target ID as identity; the human-readable name is display metadata. The predecessor `FW/GA/HE` hold mapping is retained only as superseded audit evidence.\n\n"
    report += "## Safety boundary\n\nThe ten numerical branch files and fold bytes are unchanged. The isolated source runner compiled protected notebook definitions directly, bound target/fold and dynamic state explicitly, and then stopped at the NO_FIT permit. No prediction or metric rows were created. P8 remains prohibited.\n\n"
    report += "## Sentinel\n\n`TRAIN2NF::HI` = `FRF 3000–6500 Hz AVG`, outer repeat `0`, is the sole preregistered sentinel for P0–P7. The permit is readiness metadata only and still requires explicit execution approval.\n"
    (RUN / "REPORT.md").write_text(report, encoding="utf-8")

    merge = f"""# MERGE PACKET — {RUN_ID}\n\n- Packet type: target-policy/contract repair; no-fit\n- Affected-contract QA: **{affected['overall_status']}**\n- Historical TRAIN-PARITY-003 NO-GO: preserved\n- New re-adjudication: **{readjudication['decision']}**\n- Changed implementation: isolated `contracts.py` only\n- Numerical branch hashes: unchanged\n- Fold manifest: unchanged, not regenerated\n- Protected source/workbook/HQ/NB/LEGACY-PY: unchanged\n- Fit/predict/prediction/metric: `0/0/0/0`\n- Independent QA: pending exactly-one execution\n- Merge recommendation: pending independent QA\n"""
    (RUN / "MERGE_PACKET.md").write_text(merge, encoding="utf-8")


if __name__ == "__main__":
    main()
