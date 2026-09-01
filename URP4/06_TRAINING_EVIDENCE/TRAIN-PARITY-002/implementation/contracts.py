from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


SOURCE_SHA256 = "11129a41bd4303d82c599148cd761adb3c858f58da017586e07fb0f06d055ff2"
WORKBOOK_SHA256 = "4a6ec7d03d92fa25851998689768d9db9f63227f00e778a528d758b368851dce"
TOLERANCE_REVISION = "TRAIN-PARITY-TOL-v0.1"
ADAPTER_VERSION = "TRAIN-2ND-NEWFEATURE-EXACT-ADAPTER-v0.1"
SHEET = "총정리"
HEADER_MAIN_ROW = 2
HEADER_SUB_ROWS = (3, 4, 5)
DATA_ROW_START = 7
DATA_ROW_END = 204
X_START = "I"
X_END = "FU"
Y_START = "FV"
Y_END = "HL"
TARGET_COLUMNS = ("FW", "FX", "FZ", "GA", "GC", "GG", "GJ", "GZ", "HA", "HB", "HC", "HD", "HE", "HG", "HI", "HK")
EXPECTED_ROWS = 198
EXPECTED_X_FEATURES = 169
EXPECTED_TARGETS = 16
ROUND_X_DECIMALS = 8
OUTER_REPEATS = 12
OUTER_TEST_SIZE = 0.22
OUTER_SEED_BASE = 42
INNER_SPLITS = 24
INNER_TEST_SIZE = 0.20

TARGET_IDS = tuple(f"TRAIN2NF::{col}" for col in TARGET_COLUMNS)
HOLD_COLUMNS = frozenset(("FW", "GA", "HE"))


@dataclass(frozen=True)
class SourcePaths:
    project_root: Path
    source_notebook: Path
    workbook: Path
    parity001: Path


@dataclass(frozen=True)
class ExtractionContract:
    sheet: str = SHEET
    header_main_row: int = HEADER_MAIN_ROW
    header_sub_rows: tuple[int, ...] = HEADER_SUB_ROWS
    data_row_start: int = DATA_ROW_START
    data_row_end: int = DATA_ROW_END
    x_start: str = X_START
    x_end: str = X_END
    y_start: str = Y_START
    y_end: str = Y_END
    target_columns: tuple[str, ...] = TARGET_COLUMNS
    expected_rows: int = EXPECTED_ROWS
    expected_x_features: int = EXPECTED_X_FEATURES
    expected_targets: int = EXPECTED_TARGETS


METHOD_BRANCHES = (
    "baseline_stability",
    "stability_lasso_ridge",
    "spca_ridge",
    "spca_huber",
    "block_pca_ridge",
    "bagged_subspace_ridge",
    "minimal_class_average",
    "multitask_screen_ridge",
    "multitask_screen_pls",
    "spca_pls",
)


STAGE_SPECS = (
    ("S01", "workbook_extraction", 3, "extract_range_df", "extractor.extract_dataset", "implemented_no_fit"),
    ("S02", "target_selection", 3, "output_letter_to_name/OUTPUT_COLUMNS", "extractor.extract_dataset", "implemented_no_fit"),
    ("S03", "same_x_grouping", 4, "build_group_ids_from_x", "extractor.build_group_ids", "implemented_no_fit"),
    ("S04", "outer_split", 6, "repeated_group_splits", "folds.build_fold_manifest", "implemented_no_fit"),
    ("S05", "inner_split", 6, "fit_search_model/GroupShuffleSplit", "folds.build_fold_manifest", "implemented_no_fit_group_level"),
    ("S06", "prefilter", 6, "prefilter_features_groupwise", "source_ast exact function binding", "source_bound_no_execution"),
    ("S07", "feature_ranking", 6, "build_feature_frequency/corr_prune_from_ranked", "source_ast exact function binding", "source_bound_no_execution"),
    ("S08", "feature_engineering", 6, "source helper block", "source_ast cell/function inventory", "partial_branch_coverage"),
    ("S09", "repeated_y", 6, "select_best_y_within_group", "source_ast exact function binding", "source_bound_no_execution"),
    ("S10", "method_roster", 7, "get_method_candidates_for_output", "stage_graph METHOD_BRANCHES", "implemented_no_fit_spec"),
    ("S11", "estimator_model_selection", 6, "choose_best_model_and_topk/evaluate_method_train_test", "source_ast exact function binding", "source_bound_no_execution"),
    ("S12", "transform_selection", 6, "make_target_transformer/make_y_transformer", "source_ast exact function binding", "source_bound_no_execution"),
    ("S13", "fold_prediction_collection", 8, "Cell D1 transient prediction", "ledgers PredictionLedgerWriter", "schema_only_no_prediction"),
    ("S14", "metric_calculation", 7, "score_prediction and Cell D1", "ledgers MetricLedgerWriter", "schema_only_no_metric"),
    ("S15", "final_refit", 9, "Cell E1", "policy final_refit guard", "source_bound_no_execution_13_primary_3_hold"),
    ("S16", "output_serialization", 2, "export_df/export_json", "ledgers versioned writers", "implemented_no_fit_empty_ledgers"),
)


def target_policy() -> list[dict[str, object]]:
    rows = []
    for index, col in enumerate(TARGET_COLUMNS, start=1):
        hold = col in HOLD_COLUMNS
        rows.append(
            {
                "target_id": f"TRAIN2NF::{col}",
                "excel_col": col,
                "outer_cv_parity": "eligible",
                "final_refit_parity": "hold" if hold else "primary",
                "policy_status": "final_refit_hold" if hold else "primary",
                "ordinal": index,
            }
        )
    return rows


def validate_target_policy(rows: list[dict[str, object]]) -> None:
    ids = [str(row["target_id"]) for row in rows]
    if ids != list(TARGET_IDS):
        raise ValueError("TARGET_POLICY_MISMATCH: target identity/order drift")
    primary = sum(row["final_refit_parity"] == "primary" for row in rows)
    hold = sum(row["final_refit_parity"] == "hold" for row in rows)
    if (primary, hold) != (13, 3):
        raise ValueError("TARGET_POLICY_MISMATCH: expected 13 primary and 3 hold")
    actual_hold = {str(row["excel_col"]) for row in rows if row["final_refit_parity"] == "hold"}
    if actual_hold != HOLD_COLUMNS:
        raise ValueError("TARGET_POLICY_MISMATCH: hold set drift")


def assert_final_refit_allowed(target_id: str) -> None:
    col = target_id.rsplit("::", 1)[-1]
    if col in HOLD_COLUMNS:
        raise PermissionError(f"FINAL_REFIT_HOLD: {target_id}")
    if target_id not in TARGET_IDS:
        raise KeyError(f"UNKNOWN_TARGET: {target_id}")
