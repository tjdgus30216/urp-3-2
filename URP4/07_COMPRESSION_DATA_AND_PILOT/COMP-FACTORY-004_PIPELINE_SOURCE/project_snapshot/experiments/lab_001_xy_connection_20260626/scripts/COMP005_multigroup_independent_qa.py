from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def write_csv(path: Path, rows: list[dict]) -> None:
    pd.DataFrame(rows).to_csv(path, index=False, encoding="utf-8-sig")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--qa-version", default="v2")
    args = parser.parse_args()
    run = Path(args.run_dir).resolve()
    manifest = json.loads((run / "MANIFEST.json").read_text(encoding="utf-8"))
    predictions = pd.read_csv(run / "oof_predictions.csv")
    metrics = pd.read_csv(run / "metrics.csv")
    folds = pd.read_csv(run / "outer_fold_registry.csv")
    selections = pd.read_csv(run / "fold_local_feature_selection.csv")
    summary = pd.read_csv(run / "target_screening_summary.csv")
    producer_qa = pd.read_csv(run / "producer_QA.csv")

    checks: list[dict] = []

    def add(check_id: str, check: str, passed: bool, observed: object) -> None:
        checks.append({"check_id": check_id, "check": check, "passed": bool(passed), "observed": observed})

    add("IQA-01", "producer status PASS", manifest["status"] == "PASS", manifest["status"])
    add("IQA-02", "producer QA all passed", producer_qa.passed.astype(str).str.lower().eq("true").all(), f"{producer_qa.passed.astype(str).str.lower().eq('true').sum()}/{len(producer_qa)}")
    expected = int(manifest["counts"]["rows"]) * 16 * 4
    add("IQA-03", "prediction census", len(predictions) == expected, len(predictions))
    add("IQA-04", "predictions finite", np.isfinite(predictions.y_pred).all(), int((~np.isfinite(predictions.y_pred)).sum()))
    add("IQA-05", "unique model-target-method OOF records", not predictions.duplicated(["model_key", "target_id", "method_id"]).any(), int(predictions.duplicated(["model_key", "target_id", "method_id"]).sum()))
    add("IQA-06", "outer groups disjoint", all(not (set(row.train_groups.split("|")) & set(row.test_groups.split("|"))) for row in folds.itertuples(index=False)), "disjoint")
    add("IQA-07", "fold-local feature ceiling", selections.groupby(["target_id", "outer_fold_id"]).size().max() <= 8, int(selections.groupby(["target_id", "outer_fold_id"]).size().max()))
    add("IQA-08", "no promotions", summary.promotion_status.eq("not_promoted").all(), sorted(summary.promotion_status.unique()))

    metric_deltas = []
    pooled = metrics.loc[metrics.scope.eq("pooled_oof")]
    for row in pooled.itertuples(index=False):
        part = predictions.loc[predictions.target_id.eq(row.target_id) & predictions.method_id.eq(row.method_id)]
        recomputed = {
            "r2": r2_score(part.y_true, part.y_pred),
            "mae": mean_absolute_error(part.y_true, part.y_pred),
            "rmse": math.sqrt(mean_squared_error(part.y_true, part.y_pred)),
        }
        for name, value in recomputed.items():
            expected_value = float(getattr(row, name))
            absolute_delta = abs(expected_value - float(value))
            metric_deltas.append(absolute_delta / max(1.0, abs(expected_value), abs(float(value))))
    max_metric_delta = max(metric_deltas) if metric_deltas else float("inf")
    add("IQA-09", "pooled metrics independently reproduced", max_metric_delta <= 1e-10, max_metric_delta)

    manifest_mismatches = []
    for item in manifest["outputs"]:
        path = run / item["file"]
        if not path.exists() or path.stat().st_size != item["bytes"] or sha256(path) != item["sha256"]:
            manifest_mismatches.append(item["file"])
    add("IQA-10", "producer output manifest matches", not manifest_mismatches, "|".join(manifest_mismatches) if manifest_mismatches else "all")

    warning_rows: list[dict] = []
    extreme = pooled.loc[pooled.r2 < -1000]
    if len(extreme):
        for row in extreme.itertuples(index=False):
            warning_rows.append(
                {
                    "warning_id": "NUMERICAL_EXTREME_NEGATIVE_R2",
                    "target_id": row.target_id,
                    "method_id": row.method_id,
                    "severity": "major_screening_warning",
                    "evidence": f"pooled_r2={row.r2}",
                    "effect": "target/method is not eligible for interpretation or promotion",
                }
            )
    unstable_targets = summary.loc[(summary.min_outer_fold_r2 < -1.0) | (summary.median_outer_fold_r2 < 0)]
    for row in unstable_targets.itertuples(index=False):
        warning_rows.append(
            {
                "warning_id": "HELD_GROUP_INSTABILITY",
                "target_id": row.target_id,
                "method_id": row.best_method_by_pooled_r2,
                "severity": "screening_warning",
                "evidence": f"median_fold_r2={row.median_outer_fold_r2};min_fold_r2={row.min_outer_fold_r2}",
                "effect": "pooled R2 must not be read as stable generalization",
            }
        )
    warning_rows.append(
        {
            "warning_id": "CONSOLE_WARNING_CLASS",
            "target_id": "multiple",
            "method_id": "FS4-METHOD-02/selection",
            "severity": "runtime_warning",
            "evidence": "ConstantInputWarning and Lasso ConvergenceWarning were emitted during the controlled run",
            "effect": "technical outputs remain finite; numerical convergence must be reviewed before any method promotion",
        }
    )
    warning_rows.append(
        {
            "warning_id": "PILOT_ONLY",
            "target_id": "all",
            "method_id": "all",
            "severity": "claim_boundary",
            "evidence": "grouped technical screening with fold-local selection",
            "effect": "no production prediction, physical optimum, or inverse-design claim",
        }
    )

    core_pass = all(row["passed"] for row in checks)
    status = "PASS_WITH_WARNINGS" if core_pass else "FAIL"
    suffix = f"_{args.qa_version}" if args.qa_version else ""
    write_csv(run / f"independent_QA{suffix}.csv", checks)
    write_csv(run / f"WARNING_AND_LIMITATION_REGISTER{suffix}.csv", warning_rows)
    result = {
        "status": status,
        "checks_passed": sum(row["passed"] for row in checks),
        "checks_total": len(checks),
        "warnings": len(warning_rows),
        "scientific_promotion_ready": False,
        "run_dir": str(run),
    }
    (run / f"independent_QA{suffix}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not core_pass:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
