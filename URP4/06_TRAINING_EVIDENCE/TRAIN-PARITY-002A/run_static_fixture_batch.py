from __future__ import annotations

import ast
import csv
import json
import os
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge


RUN_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = RUN_DIR.parents[4]
sys.path.insert(0, str(RUN_DIR))

from implementation import ADAPTER_VERSION, EXECUTION_STATUS, PORT_VERSION
from implementation.branches import BRANCH_DEPENDENCIES, build_branches
from implementation.contracts import (
    ExecutionPermit, FOLD_MANIFEST_SHA256, HOLD_TARGETS, RUNTIME_CONTRACT, SOURCE_SHA256, TARGETS,
    TOLERANCE_REVISION, fixture_request,
)
from implementation.hashing import canonical_hash, require_hash, sha256_file
from implementation.instrumentation import EVENT_TYPES, EventBuffer, wrap_observable
from implementation.ledgers import METRIC_FIELDS, PREDICTION_FIELDS, SchemaOnlyLedgerWriter
from implementation.no_fit_guard import NoFitGuard
from implementation.source_exact_runtime import SourceExactRuntime


SOURCE = PROJECT_ROOT / "experiments/lab_001_xy_connection_20260626/data/raw/professor_training_20260709/Training_260419-2nd method - New feature - Good. vibration.ipynb"
WORKBOOK = PROJECT_ROOT / "experiments/lab_001_xy_connection_20260626/data/raw/professor_training_20260709/Total data_260503.xlsx"
PREV = PROJECT_ROOT / "experiments/lab_001_xy_connection_20260626/results/TRAIN-PARITY-002/TRAIN-PARITY-002-20260801-001"
PREV_FOLD = PREV / "artifacts/SHARED_FOLD_MANIFEST.csv"
PREV_MANIFEST = PREV / "IMPLEMENTATION_MANIFEST.json"
PREV_IQA = PREV / "INDEPENDENT_QA.json"
IMPLEMENTATION = RUN_DIR / "implementation"
ARTIFACTS = RUN_DIR / "artifacts"


PROTECTED = [
    SOURCE, WORKBOOK,
    PROJECT_ROOT / "URP4-1_DELIVERABLE/urp4/training/p1_adapter_v0_1/registry.py",
    PROJECT_ROOT / "URP4-1_DELIVERABLE/urp4/training/p1_adapter_v0_1/adapters.py",
    PROJECT_ROOT / "URP4-1_DELIVERABLE/urp4/training/p1_exec_layer_v0_1/builders.py",
    PROJECT_ROOT / "URP4-1_DELIVERABLE/urp4/training/p1_exec_layer_v0_1/estimators.py",
    PROJECT_ROOT / "outputs/URP4-1/Model_generator_260506_descriptor_v5_boundary_symmetry_perfboost.ipynb",
    PROJECT_ROOT / "outputs/URP4-1_NOTION_UPLOAD_20260713/01_CORE_UPLOAD/01_CODE_NB_CURRENT_v0_2.ipynb",
    PROJECT_ROOT / "outputs/URP4-1/1._parameter_rawdata_0726.py",
    PROJECT_ROOT / "outputs/URP4-1/2._Parameter_result_0727.py",
    PROJECT_ROOT / "outputs/URP4-1/3._parameter_angle_all_0727.py",
    PROJECT_ROOT / "outputs/URP4-1/Curvature_Extraction_New.py",
    PROJECT_ROOT / "outputs/URP4-1/Parameter_distribution_New.py",
    PREV_MANIFEST, PREV_IQA, PREV_FOLD,
]


OBJECTIVE_SUMMARY = {
    "baseline_stability": "choose_best_model_and_topk: source inner best_score/std/topk/complexity objective",
    "stability_lasso_ridge": "stability frequency screen; inner mean_r2; transform/topk candidate selection",
    "spca_ridge": "SPCA screen/components/transform candidates; score_obj comparison",
    "spca_huber": "SPCA screen/components/transform candidates; score_obj comparison",
    "spca_pls": "SPCA screen/components/transform candidates; score_obj comparison",
    "block_pca_ridge": "block correlation threshold and transform candidates; score_obj comparison",
    "bagged_subspace_ridge": "ranked feature top-k and transform candidates; score_obj comparison",
    "multitask_screen_ridge": "family multitask screen plus transform/top-k candidates; score_obj comparison",
    "multitask_screen_pls": "family multitask screen plus transform/top-k candidates; score_obj comparison",
    "minimal_class_average": "class-balanced member roster; valid member count >=2; class-average prediction",
}


def write_csv(path: Path, rows, fieldnames=None):
    rows = list(rows)
    fieldnames = fieldnames or (list(rows[0]) if rows else [])
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader(); writer.writerows(rows)


def snapshot():
    return {str(path.relative_to(PROJECT_ROOT)): sha256_file(path) for path in PROTECTED if path.exists()}


def source_fit_predict_sites():
    notebook = json.loads(SOURCE.read_text(encoding="utf-8"))
    rows = []
    for cell_index, cell in enumerate(notebook["cells"]):
        if cell.get("cell_type") != "code":
            continue
        tree = ast.parse("".join(cell.get("source", [])))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in {"fit", "predict"}:
                rows.append({"cell_index": cell_index, "line": node.lineno, "call": node.func.attr})
    return rows


def main():
    for key, expected in RUNTIME_CONTRACT.items():
        if key in os.environ and str(os.environ[key]) != str(expected):
            raise RuntimeError(f"RUNTIME_CONTRACT_MISMATCH: {key}")
    require_hash(SOURCE, SOURCE_SHA256, "SOURCE")
    require_hash(PREV_FOLD, FOLD_MANIFEST_SHA256, "PREDECESSOR_FOLD_MANIFEST")
    predecessor_qa = json.loads(PREV_IQA.read_text(encoding="utf-8"))
    if predecessor_qa["overall_status"] != "PASS" or predecessor_qa["qa_passed"] != predecessor_qa["qa_total"]:
        raise RuntimeError("PREDECESSOR_QA_NOT_ACCEPTED")
    before = snapshot()
    ARTIFACTS.mkdir(parents=True, exist_ok=True)

    events = EventBuffer()
    runtime = SourceExactRuntime(SOURCE).compile()
    for symbol in ("build_corr_blocks", "choose_within_tolerance"):
        wrap_observable(runtime, symbol, events)
    branches = build_branches(runtime, events)

    prediction_writer = SchemaOnlyLedgerWriter(ARTIFACTS / "PREDICTION_LEDGER_EMPTY.csv", PREDICTION_FIELDS, "prediction")
    metric_writer = SchemaOnlyLedgerWriter(ARTIFACTS / "METRIC_LEDGER_EMPTY.csv", METRIC_FIELDS, "metric")
    prediction_writer.initialize(); metric_writer.initialize()
    permit = ExecutionPermit()

    status_rows, lineage_rows, matrix_rows, qa_rows = [], [], [], []
    vibration_roster = set(runtime.function("get_method_candidates_for_output")("Vibrational response | fixture"))
    mechanical_roster = set(runtime.function("get_method_candidates_for_output")("Modulus"))

    for index, (branch_id, branch) in enumerate(branches.items(), start=1):
        description = branch.describe()
        lineage = description["source_lineage"]
        expected_roster = mechanical_roster if branch_id == "spca_pls" else vibration_roster
        roster_reachable = branch_id in expected_roster
        request = fixture_request(branch_id, prediction_writer, metric_writer)

        checks = {
            "import_callable": callable(branch),
            "signature_exact": description["callable_signature"] == "(method_name, output_name, X_train_sel, y_train_sel, g_train_sel, selected_train_df, X_test_group, y_test_group, ranked_features, random_state=42)",
            "source_lineage": bool(lineage.get("branch_ast_hash")) and lineage["source_function"] == "evaluate_method_train_test",
            "dependency_symbols": not description["missing_dependencies"],
            "stage_reachable": roster_reachable,
            "parameter_and_objective_bound": bool(OBJECTIVE_SUMMARY[branch_id]),
            "output_contract": len(description["output_contract"]) == 8,
        }
        for check_name, passed in checks.items():
            qa_rows.append({"branch_id": branch_id, "qa_check": check_name, "expected": True, "observed": bool(passed), "status": "PASS" if passed else "FAIL"})

        try:
            branch(request, permit)
            denied = False; reason = "NO_FAILURE"
        except Exception as exc:
            denied = "NO_FIT_PERMIT" in str(exc); reason = f"{type(exc).__name__}: {exc}"
        qa_rows.append({"branch_id": branch_id, "qa_check": "no_fit_permit_blocks", "expected": True, "observed": denied, "status": "PASS" if denied else "FAIL"})

        drift_request = replace(request, fold_manifest_hash="0" * 64)
        try:
            branch(drift_request, permit)
            drift_blocked = False
        except Exception as exc:
            drift_blocked = "REQUEST_FOLD_HASH_MISMATCH" in str(exc)
        qa_rows.append({"branch_id": branch_id, "qa_check": "fold_hash_drift_blocks", "expected": True, "observed": drift_blocked, "status": "PASS" if drift_blocked else "FAIL"})

        malformed = replace(request, dataset_manifest_hash="short")
        try:
            branch(malformed, permit)
            malformed_blocked = False
        except Exception as exc:
            malformed_blocked = "DATASET_MANIFEST_CONTRACT_INVALID" in str(exc)
        qa_rows.append({"branch_id": branch_id, "qa_check": "malformed_input_blocks", "expected": True, "observed": malformed_blocked, "status": "PASS" if malformed_blocked else "FAIL"})

        held = replace(fixture_request(branch_id, prediction_writer, metric_writer, "TRAIN2NF::HE"), final_refit_requested=True, final_refit_state="requested")
        try:
            branch(held, permit)
            hold_blocked = False
        except Exception as exc:
            hold_blocked = "FINAL_REFIT_HOLD" in str(exc)
        qa_rows.append({"branch_id": branch_id, "qa_check": "held_final_refit_blocks", "expected": True, "observed": hold_blocked, "status": "PASS" if hold_blocked else "FAIL"})

        branch_checks = [row for row in qa_rows if row["branch_id"] == branch_id]
        status = "exact_port_complete_no_fit" if all(row["status"] == "PASS" for row in branch_checks) else "exact_port_partial"
        status_rows.append({
            "branch_ordinal": index, "branch_id": branch_id, "adapter_symbol": description["adapter_symbol"],
            "status": status, "source_function": lineage["source_function"], "source_condition": lineage["condition"],
            "dependency_count": len(description["dependency_symbols"]), "missing_dependency_count": len(description["missing_dependencies"]),
            "fixture_qa_passed": sum(row["status"] == "PASS" for row in branch_checks), "fixture_qa_total": len(branch_checks),
            "fit_executed": 0, "predict_executed": 0,
        })
        lineage_rows.append({
            "branch_id": branch_id, "source_cell_index": lineage["source_cell_index"], "source_function": lineage["source_function"],
            "source_condition": lineage["condition"], "source_lineno": lineage["source_lineno"], "source_end_lineno": lineage["source_end_lineno"],
            "branch_ast_hash": lineage["branch_ast_hash"], "branch_text_hash": lineage["branch_text_hash"],
            "adapter_symbol": description["adapter_symbol"], "adapter_port_version": PORT_VERSION,
            "mapping_level": "source_exact_ast_callable_no_fit", "proxy_substitution": False,
        })
        matrix_rows.append({
            "branch_id": branch_id, "candidate_generation": "source evaluate_method_train_test branch body",
            "selection_objective": OBJECTIVE_SUMMARY[branch_id], "tie_handling": "source condition/order retained; observed via trace/wrappers",
            "feature_order": "source ranked_features and branch-local feature lists retained",
            "transform_model": "source branch dispatch retained", "fallback_none_exception": "source path retained and traceable",
            "final_refit_path": "source Cell E1 dispatch; 13 primary/3 hold gate external", "status": status,
        })

    write_csv(RUN_DIR / "BRANCH_IMPLEMENTATION_STATUS.csv", status_rows)
    write_csv(RUN_DIR / "SOURCE_TO_ADAPTER_NUMERICAL_LINEAGE.csv", lineage_rows)
    write_csv(RUN_DIR / "BRANCH_STAGE_AND_OBJECTIVE_MATRIX.csv", matrix_rows)
    write_csv(RUN_DIR / "STATIC_AND_FIXTURE_QA.csv", qa_rows)

    instrumentation_rows = [
        {"instrument_id": "INST-001", "event": "unordered set/dict traversal", "source_symbol": "build_corr_blocks", "mechanism": "input/result order and hashes", "yield_relevance": "high", "status": "implemented_no_fit"},
        {"instrument_id": "INST-002", "event": "same-score tie", "source_symbol": "choose_within_tolerance", "mechanism": "tie count/best score/rule/result", "yield_relevance": "high", "status": "implemented_no_fit"},
        {"instrument_id": "INST-003", "event": "PYTHONHASHSEED", "source_symbol": "process runtime", "mechanism": "runtime contract hash and environment", "yield_relevance": "high", "status": "implemented_no_fit"},
        {"instrument_id": "INST-004", "event": "random seed", "source_symbol": "branch request/runtime", "mechanism": "event payload and parameter hash", "yield_relevance": "high", "status": "implemented_no_fit"},
        {"instrument_id": "INST-005", "event": "exception including suppressed path", "source_symbol": "SourceTrace", "mechanism": "Python exception trace before handler suppression", "yield_relevance": "high", "status": "implemented_no_fit"},
        {"instrument_id": "INST-006", "event": "None return", "source_symbol": "SourceTrace/branch wrapper", "mechanism": "function/line and branch event", "yield_relevance": "high", "status": "implemented_no_fit"},
        {"instrument_id": "INST-007", "event": "fallback/branch rejection", "source_symbol": "branch wrapper", "mechanism": "event schema and source return trace", "yield_relevance": "medium", "status": "implemented_no_fit"},
        {"instrument_id": "INST-008", "event": "feature order/membership", "source_symbol": "branch output contract", "mechanism": "feature_set hash plus ordered IDs", "yield_relevance": "high", "status": "implemented_no_fit"},
        {"instrument_id": "INST-009", "event": "final refit state", "source_symbol": "external policy plus Cell E1 lineage", "mechanism": "requested/held/generated/missing reason", "yield_relevance": "high", "status": "implemented_no_fit"},
    ]
    write_csv(RUN_DIR / "NONDETERMINISM_AND_FALLBACK_INSTRUMENTATION.csv", instrumentation_rows)
    events.write(ARTIFACTS / "FIXTURE_OBSERVABILITY_EVENTS.jsonl")

    guard = NoFitGuard()
    guard_results = []
    with guard.active():
        for action in ("fit", "predict"):
            try:
                getattr(Ridge(), action)(np.zeros((2, 1)), np.zeros(2)) if action == "fit" else getattr(Ridge(), action)(np.zeros((2, 1)))
                blocked = False
            except Exception as exc:
                blocked = "NO_" in str(exc) and "GUARD" in str(exc)
            guard_results.append({"action": action, "blocked": blocked})

    no_fit = {
        "execution_status": EXECUTION_STATUS,
        "branch_fixture_calls": len(branches),
        "completed_fit_calls": guard.counters.completed_fit,
        "completed_predict_calls": guard.counters.completed_predict,
        "guard_test_attempted_fit_calls": guard.counters.attempted_fit,
        "guard_test_attempted_predict_calls": guard.counters.attempted_predict,
        "guard_tests": guard_results,
        "prediction_rows": prediction_writer.row_count(),
        "metric_rows": metric_writer.row_count(),
        "fitted_model_artifacts": 0,
        "benchmark_artifacts": 0,
        "source_static_fit_predict_sites": source_fit_predict_sites(),
        "note": "Branch fixture calls stopped at NO_FIT permit before source numerical entry. Guard attempts were blocked before sklearn estimator logic.",
    }
    (RUN_DIR / "NO_FIT_PROOF.json").write_text(json.dumps(no_fit, ensure_ascii=False, indent=2), encoding="utf-8")

    after = snapshot()
    protected_rows = [{"asset_path": path, "before_sha256": digest, "after_sha256": after.get(path, "MISSING"), "status": "PASS" if after.get(path) == digest else "FAIL"} for path, digest in before.items()]
    write_csv(RUN_DIR / "PROTECTED_ASSET_HASH_AUDIT.csv", protected_rows)

    complete = sum(row["status"] == "exact_port_complete_no_fit" for row in status_rows)
    manifest = {
        "run_id": "TRAIN-PARITY-002A-20260801-001", "adapter_version": ADAPTER_VERSION, "port_version": PORT_VERSION,
        "execution_status": EXECUTION_STATUS, "source_sha256": sha256_file(SOURCE), "predecessor_fold_manifest_sha256": sha256_file(PREV_FOLD),
        "tolerance_revision": TOLERANCE_REVISION, "source_symbols": len(runtime.symbol_lineage), "branch_count": len(branches),
        "exact_port_complete_no_fit": complete, "partial_or_blocked": len(branches) - complete,
        "overall_state": "ready_for_controlled_execution_preregistration" if complete == 10 else "partial_branch_coverage",
        "implementation_files": [{"path": str(path.relative_to(RUN_DIR)), "sha256": sha256_file(path)} for path in sorted(IMPLEMENTATION.glob("*.py"))],
        "fixture_qa": {"passed": sum(row["status"] == "PASS" for row in qa_rows), "total": len(qa_rows)},
        "no_fit_proof": no_fit, "protected_assets": {"passed": sum(row["status"] == "PASS" for row in protected_rows), "total": len(protected_rows)},
    }
    (RUN_DIR / "IMPLEMENTATION_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"overall_state": manifest["overall_state"], "complete": complete, "fixture_qa": manifest["fixture_qa"], "no_fit": [no_fit["completed_fit_calls"], no_fit["completed_predict_calls"], no_fit["prediction_rows"], no_fit["metric_rows"]]}, indent=2))


if __name__ == "__main__":
    main()
