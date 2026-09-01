from __future__ import annotations

from collections import defaultdict
from typing import Any

from .permit import OUTER_FOLDS


_PHASES = {
    "FS4-P1-A": (
        ("inner_base_model_evaluation", 8, "2 bases x 4 inner folds"),
        ("outer_refit_base_models", 2, "2 selected bases"),
    ),
    "FS4-P1-B": (
        ("stability_lasso_internal_cv", 240, "60 bootstraps x 4 LassoCV folds"),
        ("inner_transform_ridge_evaluation", 8, "2 target transforms x 4 inner folds"),
        ("outer_refit", 1, "selected screen and Ridge"),
    ),
    "FS4-P1-C": (
        ("inner_omp_grid_evaluation", 32, "4 support sizes x 2 transforms x 4 inner folds"),
        ("outer_refit", 1, "selected OMP-Ridge"),
    ),
    "FS4-P1-D": (
        ("inner_branch_evaluation", 12, "3 branches x 4 inner folds"),
        ("outer_refit_branches", 3, "common, full and structural branches"),
    ),
}


def prospective_fit_ledger() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for recipe_id, phases in _PHASES.items():
        for outer_fold_id in OUTER_FOLDS:
            for phase, fit_count, rationale in phases:
                rows.append(
                    {
                        "pilot_recipe_id": recipe_id,
                        "outer_fold_id": outer_fold_id,
                        "phase": phase,
                        "prospective_estimator_fits": fit_count,
                        "rationale": rationale,
                        "actual_estimator_fits": 0,
                        "performance_y_read": 0,
                        "status": "prospective_no_fit",
                    }
                )
    return rows


def prospective_fit_summary() -> dict[str, int]:
    totals: dict[str, int] = defaultdict(int)
    for row in prospective_fit_ledger():
        totals[str(row["pilot_recipe_id"])] += int(row["prospective_estimator_fits"])
    totals["TOTAL"] = sum(totals.values())
    return dict(totals)
