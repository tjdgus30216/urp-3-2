"""Parity and deletion checks for descriptor-service execution modes."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def compare_tables(
    expected: pd.DataFrame,
    actual: pd.DataFrame,
    *,
    table_role: str,
    key_columns: list[str],
    atol: float = 1e-12,
) -> dict[str, Any]:
    column_match = list(expected.columns) == list(actual.columns)
    row_count_match = len(expected) == len(actual)
    if not column_match or not row_count_match:
        return {
            "table_role": table_role,
            "expected_rows": len(expected),
            "actual_rows": len(actual),
            "columns_exact": column_match,
            "keys_exact": False,
            "numeric_mismatch_cells": -1,
            "string_mismatch_cells": -1,
            "max_abs_error": float("inf"),
            "atol": atol,
            "status": "failed",
        }
    keys_exact = expected[key_columns].astype(str).equals(actual[key_columns].astype(str))
    numeric_columns = [
        column for column in expected.columns
        if column not in key_columns
        and pd.api.types.is_numeric_dtype(expected[column])
        and pd.api.types.is_numeric_dtype(actual[column])
    ]
    string_columns = [column for column in expected.columns if column not in key_columns and column not in numeric_columns]
    numeric_mismatch = 0
    max_abs_error = 0.0
    for column in numeric_columns:
        left = expected[column].astype(float).to_numpy()
        right = actual[column].astype(float).to_numpy()
        finite_pair = np.isfinite(left) & np.isfinite(right)
        same_nonfinite = (~np.isfinite(left)) & (~np.isfinite(right))
        differences = np.zeros_like(left, dtype=float)
        differences[finite_pair] = np.abs(left[finite_pair] - right[finite_pair])
        mismatch = ~(same_nonfinite | (finite_pair & (differences <= atol)))
        numeric_mismatch += int(mismatch.sum())
        if np.any(finite_pair):
            max_abs_error = max(max_abs_error, float(differences[finite_pair].max()))
    string_mismatch = sum(
        int((expected[column].astype(str).to_numpy() != actual[column].astype(str).to_numpy()).sum())
        for column in string_columns
    )
    passed = keys_exact and numeric_mismatch == 0 and string_mismatch == 0
    return {
        "table_role": table_role,
        "expected_rows": len(expected),
        "actual_rows": len(actual),
        "columns_exact": column_match,
        "keys_exact": keys_exact,
        "numeric_mismatch_cells": numeric_mismatch,
        "string_mismatch_cells": string_mismatch,
        "max_abs_error": max_abs_error,
        "atol": atol,
        "status": "passed" if passed else "failed",
    }


def assert_streaming_cleanup(work_dir: str | Path) -> dict[str, Any]:
    path = Path(work_dir)
    remaining = [item for item in path.rglob("*.png") if item.is_file()] if path.exists() else []
    return {
        "work_dir": path.as_posix(),
        "remaining_png": len(remaining),
        "status": "passed" if not remaining else "failed",
    }
