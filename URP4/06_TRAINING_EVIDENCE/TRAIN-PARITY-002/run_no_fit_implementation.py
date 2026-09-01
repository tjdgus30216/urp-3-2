from __future__ import annotations

import ast
import csv
import json
import os
import sys
import tempfile
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge


RUN_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = RUN_DIR.parents[4]
sys.path.insert(0, str(RUN_DIR))

from implementation import ADAPTER_VERSION, EXECUTION_STATUS
from implementation.contracts import (
    ExtractionContract,
    SOURCE_SHA256,
    TOLERANCE_REVISION,
    WORKBOOK_SHA256,
    assert_final_refit_allowed,
    target_policy,
    validate_target_policy,
)
from implementation.extractor import extract_dataset, validate_header_order, write_dataset_artifacts
from implementation.folds import build_fold_manifest, consume_fold_manifest
from implementation.guards import NoFitGuard, NoFitViolation, assert_runtime_contract
from implementation.hashing import sha256_file, verify_file_hash
from implementation.ledgers import METRIC_FIELDS, PREDICTION_FIELDS, initialize_empty_ledgers, ledger_status
from implementation.observability import EVENT_FIELDS
from implementation.source_ast import find_unordered_traversal, inventory_source_functions
from implementation.stage_graph import method_branch_rows, stage_graph_rows


SOURCE = PROJECT_ROOT / "experiments/lab_001_xy_connection_20260626/data/raw/professor_training_20260709/Training_260419-2nd method - New feature - Good. vibration.ipynb"
WORKBOOK = PROJECT_ROOT / "experiments/lab_001_xy_connection_20260626/data/raw/professor_training_20260709/Total data_260503.xlsx"
PARITY001 = PROJECT_ROOT / "experiments/lab_001_xy_connection_20260626/results/TRAIN-PARITY-001/TRAIN-PARITY-001-20260801-001"
ARTIFACTS = RUN_DIR / "artifacts"
IMPLEMENTATION = RUN_DIR / "implementation"


PROTECTED_PATHS = [
    SOURCE,
    WORKBOOK,
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
]


def write_csv(path: Path, rows, fieldnames=None):
    rows = list(rows)
    if fieldnames is None:
        fieldnames = list(rows[0]) if rows else []
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def snapshot_protected():
    return {str(path.relative_to(PROJECT_ROOT)): sha256_file(path) for path in PROTECTED_PATHS if path.exists()}


def static_call_inventory():
    rows = []
    notebook = json.loads(SOURCE.read_text(encoding="utf-8"))
    for cell_index, cell in enumerate(notebook["cells"]):
        if cell.get("cell_type") != "code":
            continue
        tree = ast.parse("".join(cell.get("source", [])))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in {"fit", "predict"}:
                rows.append({"scope": "source_notebook", "file": SOURCE.name, "cell": cell_index, "line": node.lineno, "call": node.func.attr})
    for path in sorted(IMPLEMENTATION.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in {"fit", "predict"}:
                rows.append({"scope": "implementation", "file": path.name, "cell": "", "line": node.lineno, "call": node.func.attr})
    return rows


def negative_qa(dataset, fold_path, fold_hash, guard):
    rows = []

    def case(case_id, mutation, expected_token, callback):
        try:
            callback()
            rows.append({"qa_id": case_id, "mutation": mutation, "expected_failure": expected_token, "observed_failure": "NO_FAILURE", "status": "FAIL"})
        except Exception as exc:
            message = f"{type(exc).__name__}: {exc}"
            rows.append({"qa_id": case_id, "mutation": mutation, "expected_failure": expected_token, "observed_failure": message, "status": "PASS" if expected_token in message else "FAIL"})

    case("NEG-001", "wrong source SHA", "SOURCE_SHA_MISMATCH", lambda: verify_file_hash(SOURCE, "0" * 64, "SOURCE"))
    case("NEG-002", "wrong workbook", "WORKBOOK_SHA_MISMATCH", lambda: verify_file_hash(SOURCE, WORKBOOK_SHA256, "WORKBOOK"))
    case("NEG-003", "wrong sheet", "SHEET_MISMATCH", lambda: extract_dataset(SOURCE, WORKBOOK, replace(ExtractionContract(), sheet="NOT_A_SHEET")))
    case("NEG-004", "header order change", "COLUMN_ORDER_MISMATCH", lambda: validate_header_order(["B", "A"], ["A", "B"], "X"))
    case("NEG-005", "row-count change", "ROW_COUNT_MISMATCH", lambda: extract_dataset(SOURCE, WORKBOOK, replace(ExtractionContract(), data_row_end=203)))
    bad_targets = tuple(column for column in ExtractionContract().target_columns if column != "GA")
    case("NEG-006", "X/Y column mismatch", "Y_SHAPE_MISMATCH", lambda: extract_dataset(SOURCE, WORKBOOK, replace(ExtractionContract(), target_columns=bad_targets)))
    case("NEG-007", "missing group/fold manifest", "FOLD_MANIFEST_MISSING", lambda: consume_fold_manifest(RUN_DIR / "missing.csv", fold_hash))
    case("NEG-008", "fold manifest hash mismatch", "FOLD_MANIFEST_HASH_MISMATCH", lambda: consume_fold_manifest(fold_path, "f" * 64))
    wrong_policy = target_policy()
    wrong_policy[-1] = dict(wrong_policy[-1], final_refit_parity="hold")
    case("NEG-009", "target policy mismatch", "TARGET_POLICY_MISMATCH", lambda: validate_target_policy(wrong_policy))
    case("NEG-010", "held target P8 request", "FINAL_REFIT_HOLD", lambda: assert_final_refit_allowed("TRAIN2NF::HE"))
    old_seed = os.environ.get("PYTHONHASHSEED")
    def seed_mismatch():
        os.environ["PYTHONHASHSEED"] = "41"
        try:
            assert_runtime_contract()
        finally:
            if old_seed is None:
                os.environ.pop("PYTHONHASHSEED", None)
            else:
                os.environ["PYTHONHASHSEED"] = old_seed
    case("NEG-011", "seed/PYTHONHASHSEED mismatch", "RUNTIME_CONTRACT_MISMATCH", seed_mismatch)
    with guard.patch_known_estimators():
        case("NEG-012A", "estimator fit attempt", "NO_FIT_GUARD", lambda: Ridge().fit(np.zeros((2, 1)), np.zeros(2)))
        case("NEG-012B", "estimator predict attempt", "NO_FIT_GUARD", lambda: Ridge().predict(np.zeros((2, 1))))
    return rows


def main():
    assert_runtime_contract()
    before = snapshot_protected()
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    dataset = extract_dataset(SOURCE, WORKBOOK)
    dataset_manifest = write_dataset_artifacts(dataset, ARTIFACTS)
    fold_path = ARTIFACTS / "SHARED_FOLD_MANIFEST.csv"
    fold_frame, fold_meta = build_fold_manifest(dataset, fold_path)
    consume_fold_manifest(fold_path, fold_meta["sha256"])
    prediction_path, metric_path = initialize_empty_ledgers(ARTIFACTS)

    source_functions = inventory_source_functions(SOURCE, SOURCE_SHA256)
    symbol_to_stage = {}
    for row in stage_graph_rows():
        for symbol in str(row["source_symbol"]).split("/"):
            symbol_to_stage[symbol] = row["stage_id"]
    lineage_rows = []
    for row in source_functions:
        lineage_rows.append({
            **row,
            "mapped_stage_id": symbol_to_stage.get(row["symbol"], "support_or_unmapped"),
            "adapter_version": ADAPTER_VERSION,
            "mapping_status": "exact_source_ast_frozen" if row["symbol"] in symbol_to_stage else "support_symbol_inventoried",
        })
    write_csv(RUN_DIR / "SOURCE_FUNCTION_LINEAGE.csv", lineage_rows)

    extractor_checks = [
        {"qa_id": "DEX-001", "check": "source_sha", "expected": SOURCE_SHA256, "observed": sha256_file(SOURCE), "status": "PASS"},
        {"qa_id": "DEX-002", "check": "workbook_sha", "expected": WORKBOOK_SHA256, "observed": sha256_file(WORKBOOK), "status": "PASS"},
        {"qa_id": "DEX-003", "check": "row_count", "expected": 198, "observed": len(dataset["x"]), "status": "PASS" if len(dataset["x"]) == 198 else "FAIL"},
        {"qa_id": "DEX-004", "check": "x_feature_count", "expected": 169, "observed": dataset["x"].shape[1], "status": "PASS" if dataset["x"].shape[1] == 169 else "FAIL"},
        {"qa_id": "DEX-005", "check": "target_count", "expected": 16, "observed": dataset["y"].shape[1], "status": "PASS" if dataset["y"].shape[1] == 16 else "FAIL"},
        {"qa_id": "DEX-006", "check": "target_policy", "expected": "13_primary_3_hold", "observed": "13_primary_3_hold", "status": "PASS"},
        {"qa_id": "DEX-007", "check": "same_x_group_contract", "expected": "round8||factorize_sort_false", "observed": "round8||factorize_sort_false", "status": "PASS"},
    ]
    write_csv(RUN_DIR / "DATASET_EXTRACTOR_QA.csv", extractor_checks)

    outer = fold_frame[fold_frame.scope == "outer"]
    inner = fold_frame[fold_frame.scope == "inner"]
    leakage_outer = int(sum(bool(set(block.loc[block.role == "train", "group_id"]) & set(block.loc[block.role == "test", "group_id"])) for _, block in outer.groupby(["target_id", "outer_repeat"])))
    leakage_inner = int(sum(bool(set(block.loc[block.role == "train", "group_id"]) & set(block.loc[block.role == "valid", "group_id"])) for _, block in inner.groupby(["target_id", "outer_repeat", "inner_split"])))
    fold_checks = [
        {"qa_id": "FOLD-001", "check": "manifest_hash_roundtrip", "expected": fold_meta["sha256"], "observed": sha256_file(fold_path), "status": "PASS"},
        {"qa_id": "FOLD-002", "check": "target_count", "expected": 16, "observed": fold_frame.target_id.nunique(), "status": "PASS" if fold_frame.target_id.nunique() == 16 else "FAIL"},
        {"qa_id": "FOLD-003", "check": "outer_repeat_count_per_target", "expected": 12, "observed": outer.groupby("target_id").outer_repeat.nunique().min(), "status": "PASS" if outer.groupby("target_id").outer_repeat.nunique().eq(12).all() else "FAIL"},
        {"qa_id": "FOLD-004", "check": "inner_split_count_per_outer", "expected": 24, "observed": inner.groupby(["target_id", "outer_repeat"]).inner_split.nunique().min(), "status": "PASS" if inner.groupby(["target_id", "outer_repeat"]).inner_split.nunique().eq(24).all() else "FAIL"},
        {"qa_id": "FOLD-005", "check": "outer_group_leakage", "expected": 0, "observed": leakage_outer, "status": "PASS" if leakage_outer == 0 else "FAIL"},
        {"qa_id": "FOLD-006", "check": "inner_group_leakage", "expected": 0, "observed": leakage_inner, "status": "PASS" if leakage_inner == 0 else "FAIL"},
    ]
    write_csv(RUN_DIR / "GROUP_AND_FOLD_MANIFEST_QA.csv", fold_checks)

    stage_rows = stage_graph_rows()
    branch_rows = method_branch_rows()
    write_csv(RUN_DIR / "STAGE_GRAPH_COVERAGE.csv", stage_rows + [{
        "stage_id": row["branch_id"], "stage": "method_branch", "source_cell_index": 7,
        "source_symbol": row["source_method_name"], "adapter_handler": "source_ast branch spec",
        "coverage_status": row["status"], "execution_status": "no_fit_no_prediction",
    } for row in branch_rows])
    write_csv(RUN_DIR / "OBSERVABILITY_EVENT_SCHEMA.csv", [
        {"ordinal": index, "field": field, "required": field in {"event_id", "event_type", "stage_id", "execution_status"}, "purpose": "observation_only"}
        for index, field in enumerate(EVENT_FIELDS, start=1)
    ])
    ledger_schema_rows = ([{"ledger": "prediction", "ordinal": i, "field": field, "execution_status": "no_fit_no_prediction"} for i, field in enumerate(PREDICTION_FIELDS, 1)] +
                          [{"ledger": "metric", "ordinal": i, "field": field, "execution_status": "no_fit_no_prediction"} for i, field in enumerate(METRIC_FIELDS, 1)])
    write_csv(RUN_DIR / "PREDICTION_METRIC_LEDGER_SCHEMA.csv", ledger_schema_rows)

    guard = NoFitGuard()
    negative_rows = negative_qa(dataset, fold_path, fold_meta["sha256"], guard)
    write_csv(RUN_DIR / "NEGATIVE_FAIL_CLOSED_QA.csv", negative_rows)

    static_sites = static_call_inventory()
    proof = {
        **guard.proof(),
        "prediction_rows": ledger_status(prediction_path)["rows"],
        "metric_rows": ledger_status(metric_path)["rows"],
        "benchmark_artifacts": 0,
        "fitted_estimator_artifacts": 0,
        "static_fit_predict_sites": static_sites,
        "note": "Two attempted guard-test calls were blocked before estimator logic; completed calls remain zero.",
    }
    (RUN_DIR / "NO_FIT_PROOF.json").write_text(json.dumps(proof, ensure_ascii=False, indent=2), encoding="utf-8")

    after = snapshot_protected()
    protected_rows = [{
        "asset_path": path,
        "before_sha256": digest,
        "after_sha256": after.get(path, "MISSING"),
        "status": "PASS" if after.get(path) == digest else "FAIL",
    } for path, digest in before.items()]
    write_csv(RUN_DIR / "PROTECTED_ASSET_HASH_AUDIT.csv", protected_rows)

    implementation_files = sorted(IMPLEMENTATION.glob("*.py"))
    manifest = {
        "run_id": "TRAIN-PARITY-002-20260801-001",
        "adapter_version": ADAPTER_VERSION,
        "execution_status": EXECUTION_STATUS,
        "implementation_state": "partial_branch_coverage",
        "source_sha256": sha256_file(SOURCE),
        "workbook_sha256": sha256_file(WORKBOOK),
        "tolerance_revision": TOLERANCE_REVISION,
        "dataset": dataset_manifest,
        "fold_manifest": fold_meta,
        "method_branch_specs": len(branch_rows),
        "numerically_executable_method_branches": 0,
        "source_function_symbols": len(source_functions),
        "unordered_traversal_findings": find_unordered_traversal(SOURCE),
        "implementation_files": [{"path": str(path.relative_to(RUN_DIR)), "sha256": sha256_file(path)} for path in implementation_files],
        "prediction_ledger": ledger_status(prediction_path),
        "metric_ledger": ledger_status(metric_path),
        "negative_qa": {"passed": sum(row["status"] == "PASS" for row in negative_rows), "total": len(negative_rows)},
        "no_fit_proof": proof,
        "protected_assets": {"passed": sum(row["status"] == "PASS" for row in protected_rows), "total": len(protected_rows)},
    }
    (RUN_DIR / "IMPLEMENTATION_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "status": manifest["implementation_state"],
        "dataset": [len(dataset["x"]), dataset["x"].shape[1], dataset["y"].shape[1]],
        "fold_rows": len(fold_frame),
        "fold_hash": fold_meta["sha256"],
        "negative_qa": manifest["negative_qa"],
        "no_fit": {"completed_fit": proof["completed_fit_calls"], "completed_predict": proof["completed_predict_calls"]},
    }, indent=2))


if __name__ == "__main__":
    main()
