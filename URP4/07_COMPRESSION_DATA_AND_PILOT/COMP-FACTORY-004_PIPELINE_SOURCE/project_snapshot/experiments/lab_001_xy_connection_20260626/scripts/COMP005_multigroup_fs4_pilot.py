from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import sys
import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from COMP002_ai_lattice_fs4_pilot import (
    fold_select,
    method_01,
    method_02,
    method_03,
    ridge_pipeline,
    safe_spearman,
    union_find_groups,
)


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
INPUT_RUN = (
    LAB
    / "data"
    / "processed"
    / "COMP-FACTORY-003"
    / "COMP-FACTORY-003-BCL-VORONOI-20260802-001"
)
OUTPUT_ROOT = LAB / "data" / "processed" / "COMP-FACTORY-004"
KST = timezone(timedelta(hours=9))
METHODS = ("FS4-METHOD-01", "FS4-METHOD-02", "FS4-METHOD-03", "FS4-METHOD-04")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def write_csv(path: Path, rows: list[dict]) -> None:
    pd.DataFrame(rows).to_csv(path, index=False, encoding="utf-8-sig")


def metric_dict(y_true: np.ndarray, y_pred: np.ndarray, null_pred: np.ndarray) -> dict[str, float]:
    rmse = math.sqrt(mean_squared_error(y_true, y_pred))
    null_rmse = math.sqrt(mean_squared_error(y_true, null_pred))
    y_std = float(np.std(y_true, ddof=0))
    q25, q75 = np.quantile(y_true, [0.25, 0.75])
    iqr = float(q75 - q25)
    return {
        "r2": float(r2_score(y_true, y_pred)) if len(y_true) > 1 else float("nan"),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(rmse),
        "nrmse_by_std": float(rmse / y_std) if y_std > 0 else float("nan"),
        "nrmse_by_iqr": float(rmse / iqr) if iqr > 0 else float("nan"),
        "spearman": safe_spearman(y_true, y_pred),
        "null_mae": float(mean_absolute_error(y_true, null_pred)),
        "null_rmse": float(null_rmse),
        "delta_mae_vs_null": float(mean_absolute_error(y_true, y_pred) - mean_absolute_error(y_true, null_pred)),
        "delta_rmse_vs_null": float(rmse - null_rmse),
    }


def method_04_generic(
    x_train: np.ndarray,
    y_train: np.ndarray,
    groups: np.ndarray,
    x_test: np.ndarray,
    selected_feature_ids: list[str],
    feature_names: dict[str, str],
) -> tuple[np.ndarray, dict]:
    domain_indices: dict[str, list[int]] = {"full": list(range(len(selected_feature_ids)))}
    condition = [
        index
        for index, feature_id in enumerate(selected_feature_ids)
        if feature_names[feature_id] in {"Actual VF"}
    ]
    topology = [
        index
        for index, feature_id in enumerate(selected_feature_ids)
        if any(token in feature_names[feature_id].lower() for token in ("node", "strut", "angle-z", "angle-x", "angle-y"))
    ]
    geometry = [
        index
        for index, feature_id in enumerate(selected_feature_ids)
        if index not in set(condition + topology)
    ]
    if condition:
        domain_indices["condition"] = condition
    if topology:
        domain_indices["topology"] = topology
    if geometry:
        domain_indices["geometry"] = geometry

    branch_errors: dict[str, list[float]] = {name: [] for name in domain_indices}
    for held in sorted(set(groups)):
        train_mask = groups != held
        valid_mask = groups == held
        for name, indices in domain_indices.items():
            model = ridge_pipeline(1.0)
            model.fit(x_train[train_mask][:, indices], y_train[train_mask])
            prediction = model.predict(x_train[valid_mask][:, indices])
            branch_errors[name].append(mean_squared_error(y_train[valid_mask], prediction))
    raw_weights = {
        name: 1.0 / max(float(np.mean(errors)), 1e-12)
        for name, errors in branch_errors.items()
        if errors
    }
    total = sum(raw_weights.values())
    weights = {name: value / total for name, value in raw_weights.items()}
    predictions = []
    ordered_names = sorted(weights)
    for name in ordered_names:
        indices = domain_indices[name]
        model = ridge_pipeline(1.0)
        model.fit(x_train[:, indices], y_train)
        predictions.append(model.predict(x_test[:, indices]))
    matrix = np.column_stack(predictions)
    weight_array = np.asarray([weights[name] for name in ordered_names], dtype=float)
    return matrix @ weight_array, {
        "branch_weights_json": json.dumps(weights, sort_keys=True),
        "branches": "|".join(ordered_names),
        "base_models": len(ordered_names) * len(set(groups)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--cohort", required=True, choices=("bcl", "voronoi"))
    args = parser.parse_args()

    output = OUTPUT_ROOT / args.run_id
    if output.exists():
        raise RuntimeError(f"refusing to overwrite run: {output}")
    output.mkdir(parents=True)
    started = datetime.now(KST)
    started_perf = time.perf_counter()

    required = [
        INPUT_RUN / "xy_eligible_exact_join.csv",
        INPUT_RUN / "feature_registry.csv",
        INPUT_RUN / "target_registry.csv",
        INPUT_RUN / "independent_QA.json",
    ]
    source_hash_rows = [
        {"path": str(path.relative_to(ROOT)), "sha256": sha256(path), "status": "PASS"}
        for path in required
    ]
    intake_qa = json.loads((INPUT_RUN / "independent_QA.json").read_text(encoding="utf-8"))
    if intake_qa["status"] != "PASS":
        raise RuntimeError("input intake independent QA did not pass")

    data = pd.read_csv(INPUT_RUN / "xy_eligible_exact_join.csv")
    feature_registry = pd.read_csv(INPUT_RUN / "feature_registry.csv")
    target_registry = pd.read_csv(INPUT_RUN / "target_registry.csv")
    data = data.loc[data.source_group.eq(args.cohort)].copy().reset_index(drop=True)
    expected_rows = 137 if args.cohort == "bcl" else 30
    if len(data) != expected_rows:
        raise RuntimeError(f"cohort row count drift: {len(data)}")
    data["outer_group"] = (
        data.family_group.astype(str)
        if args.cohort == "bcl"
        else "VF" + data.vf_group.astype(int).astype(str)
    )
    expected_groups = {"B", "C", "L"} if args.cohort == "bcl" else {"VF30", "VF45", "VF60"}
    if set(data.outer_group) != expected_groups:
        raise RuntimeError(f"outer group drift: {sorted(set(data.outer_group))}")

    feature_registry = feature_registry.copy()
    feature_registry["feature_id"] = feature_registry.feature_id.astype(str)
    feature_names = dict(zip(feature_registry.feature_id, feature_registry.feature_name_raw.astype(str)))
    candidate_rows = feature_registry.loc[
        feature_registry.status.eq("available_unselected")
        & ~feature_registry.feature_name_raw.eq("Target VF")
    ].copy()
    feature_id_to_column = dict(zip(candidate_rows.feature_id, candidate_rows.column_name))
    x_all = pd.DataFrame(
        {
            feature_id: pd.to_numeric(data[column], errors="coerce")
            for feature_id, column in feature_id_to_column.items()
        }
    )
    eligible_feature_ids = [
        feature_id
        for feature_id in x_all.columns
        if x_all[feature_id].notna().any() and float(x_all[feature_id].fillna(x_all[feature_id].median()).var(ddof=0)) > 0
    ]
    x_all = x_all[eligible_feature_ids]
    if not eligible_feature_ids:
        raise RuntimeError("no eligible features")

    feature_census_rows = []
    for feature_id in eligible_feature_ids:
        values = x_all[feature_id]
        finite = values.dropna()
        feature_census_rows.append(
            {
                "feature_id": feature_id,
                "feature_name_raw": feature_names[feature_id],
                "finite_count": len(finite),
                "missing_count": int(values.isna().sum()),
                "unique_count": int(finite.nunique()),
                "variance": float(finite.var(ddof=0)),
                "iqr": float(finite.quantile(0.75) - finite.quantile(0.25)),
                "status": "unselected_candidate",
            }
        )
    correlation = x_all.corr(method="pearson")
    block_ids = union_find_groups(correlation, 0.999999)
    redundancy_rows = []
    for i, left in enumerate(eligible_feature_ids):
        for right in eligible_feature_ids[i + 1 :]:
            value = correlation.loc[left, right]
            if pd.notna(value) and abs(float(value)) >= 0.999999:
                redundancy_rows.append(
                    {
                        "left_feature_id": left,
                        "right_feature_id": right,
                        "pearson": float(value),
                        "block_id": block_ids[left],
                        "action": "preserve_nonselecting_redundancy_edge",
                    }
                )

    targets = target_registry.loc[target_registry.status.eq("available_unselected")].copy()
    if len(targets) != 16:
        raise RuntimeError(f"target count drift: {len(targets)}")
    target_name = dict(zip(targets.target_id, targets.target_name_raw))

    prediction_rows: list[dict] = []
    selection_rows: list[dict] = []
    fold_rows: list[dict] = []
    method_detail_rows: list[dict] = []
    groups = data.outer_group.astype(str).to_numpy()
    unique_groups = sorted(set(groups))

    for target in targets.itertuples(index=False):
        target_column = "y__" + str(target.target_name_raw)
        y_all = pd.to_numeric(data[target_column], errors="coerce").to_numpy(float)
        if not np.isfinite(y_all).all() or float(np.std(y_all)) == 0:
            raise RuntimeError(f"invalid target: {target.target_id}")
        for held in unique_groups:
            train_mask = groups != held
            test_mask = groups == held
            x_train_frame = x_all.loc[train_mask].reset_index(drop=True)
            y_train = y_all[train_mask]
            x_test_frame = x_all.loc[test_mask].reset_index(drop=True)
            selected, records = fold_select(x_train_frame, y_train, block_ids, 8)
            fold_id = f"HOLD_{held}"
            for record in records:
                selection_rows.append(
                    {
                        "cohort": args.cohort,
                        "target_id": target.target_id,
                        "target_name_raw": target.target_name_raw,
                        "outer_fold_id": fold_id,
                        **record,
                        "feature_name_raw": feature_names[record["selected_feature_id"]],
                        "promotion_status": "not_promoted",
                    }
                )
            fold_rows.append(
                {
                    "cohort": args.cohort,
                    "target_id": target.target_id,
                    "outer_fold_id": fold_id,
                    "held_group": held,
                    "train_groups": "|".join(sorted(set(groups[train_mask]))),
                    "test_groups": "|".join(sorted(set(groups[test_mask]))),
                    "train_rows": int(train_mask.sum()),
                    "test_rows": int(test_mask.sum()),
                    "selected_feature_ids": "|".join(selected),
                }
            )
            x_train = x_train_frame[selected].to_numpy(float)
            x_test = x_test_frame[selected].to_numpy(float)
            groups_train = groups[train_mask]
            null_value = float(np.mean(y_train))
            methods = {
                "FS4-METHOD-01": lambda: method_01(x_train, y_train, x_test),
                "FS4-METHOD-02": lambda: method_02(x_train, y_train, groups_train, x_test),
                "FS4-METHOD-03": lambda: method_03(x_train, y_train, groups_train, x_test),
                "FS4-METHOD-04": lambda: method_04_generic(x_train, y_train, groups_train, x_test, selected, feature_names),
            }
            test_indices = np.flatnonzero(test_mask)
            for method_id in METHODS:
                method_started = time.perf_counter()
                prediction, detail = methods[method_id]()
                if not np.isfinite(prediction).all():
                    raise RuntimeError(f"nonfinite prediction {target.target_id} {fold_id} {method_id}")
                method_detail_rows.append(
                    {
                        "cohort": args.cohort,
                        "target_id": target.target_id,
                        "outer_fold_id": fold_id,
                        "method_id": method_id,
                        "selected_feature_ids": "|".join(selected),
                        "runtime_seconds": time.perf_counter() - method_started,
                        "detail_json": json.dumps(detail, sort_keys=True),
                    }
                )
                for row_index, predicted in zip(test_indices, prediction):
                    prediction_rows.append(
                        {
                            "cohort": args.cohort,
                            "model_key": data.iloc[row_index].model_key,
                            "outer_group": groups[row_index],
                            "outer_fold_id": fold_id,
                            "target_id": target.target_id,
                            "target_name_raw": target.target_name_raw,
                            "method_id": method_id,
                            "y_true": float(y_all[row_index]),
                            "y_pred": float(predicted),
                            "null_pred": null_value,
                        }
                    )

    predictions = pd.DataFrame(prediction_rows)
    metric_rows: list[dict] = []
    for target_id in targets.target_id:
        for method_id in METHODS:
            part = predictions.loc[predictions.target_id.eq(target_id) & predictions.method_id.eq(method_id)]
            metric_rows.append(
                {
                    "cohort": args.cohort,
                    "scope": "pooled_oof",
                    "target_id": target_id,
                    "target_name_raw": target_name[target_id],
                    "method_id": method_id,
                    "fold_id": "ALL",
                    "n": len(part),
                    **metric_dict(part.y_true.to_numpy(), part.y_pred.to_numpy(), part.null_pred.to_numpy()),
                }
            )
            for fold_id, fold_part in part.groupby("outer_fold_id"):
                metric_rows.append(
                    {
                        "cohort": args.cohort,
                        "scope": "outer_fold",
                        "target_id": target_id,
                        "target_name_raw": target_name[target_id],
                        "method_id": method_id,
                        "fold_id": fold_id,
                        "n": len(fold_part),
                        **metric_dict(fold_part.y_true.to_numpy(), fold_part.y_pred.to_numpy(), fold_part.null_pred.to_numpy()),
                    }
                )

    metrics = pd.DataFrame(metric_rows)
    pooled = metrics.loc[metrics.scope.eq("pooled_oof")].copy()
    fold_metrics = metrics.loc[metrics.scope.eq("outer_fold")].copy()
    summary_rows = []
    for target_id in targets.target_id:
        candidates = pooled.loc[pooled.target_id.eq(target_id)].sort_values(["r2", "mae"], ascending=[False, True])
        best = candidates.iloc[0]
        best_folds = fold_metrics.loc[fold_metrics.target_id.eq(target_id) & fold_metrics.method_id.eq(best.method_id)]
        selection = [row for row in selection_rows if row["target_id"] == target_id]
        counts = Counter(row["selected_feature_id"] for row in selection)
        stable = sorted(feature_id for feature_id, count in counts.items() if count == len(unique_groups))
        summary_rows.append(
            {
                "cohort": args.cohort,
                "target_id": target_id,
                "target_name_raw": target_name[target_id],
                "best_method_by_pooled_r2": best.method_id,
                "best_pooled_r2": float(best.r2),
                "best_pooled_mae": float(best.mae),
                "best_pooled_rmse": float(best.rmse),
                "best_delta_rmse_vs_null": float(best.delta_rmse_vs_null),
                "median_outer_fold_r2": float(best_folds.r2.median()),
                "min_outer_fold_r2": float(best_folds.r2.min()),
                "features_selected_in_all_outer_folds": "|".join(stable),
                "promotion_status": "not_promoted",
                "interpretation": "technical pilot only",
            }
        )

    frequency_rows = []
    for (target_id, feature_id), count in Counter((row["target_id"], row["selected_feature_id"]) for row in selection_rows).items():
        frequency_rows.append(
            {
                "cohort": args.cohort,
                "target_id": target_id,
                "feature_id": feature_id,
                "feature_name_raw": feature_names[feature_id],
                "selected_outer_fold_count": count,
                "outer_fold_total": len(unique_groups),
                "promotion_status": "not_promoted",
            }
        )

    expected_predictions = len(data) * len(targets) * len(METHODS)
    qa = [
        {"check_id": "P01", "check": "intake independent QA PASS", "passed": intake_qa["status"] == "PASS", "observed": intake_qa["status"]},
        {"check_id": "P02", "check": "cohort row count", "passed": len(data) == expected_rows, "observed": len(data)},
        {"check_id": "P03", "check": "three outer groups", "passed": len(unique_groups) == 3, "observed": "|".join(unique_groups)},
        {"check_id": "P04", "check": "16 targets", "passed": len(targets) == 16, "observed": len(targets)},
        {"check_id": "P05", "check": "eligible feature candidates", "passed": len(eligible_feature_ids) > 0, "observed": len(eligible_feature_ids)},
        {"check_id": "P06", "check": "complete OOF prediction census", "passed": len(predictions) == expected_predictions, "observed": len(predictions)},
        {"check_id": "P07", "check": "finite OOF predictions", "passed": np.isfinite(predictions.y_pred).all(), "observed": int((~np.isfinite(predictions.y_pred)).sum())},
        {"check_id": "P08", "check": "group-disjoint outer folds", "passed": all(set(row["train_groups"].split("|")) & set(row["test_groups"].split("|")) == set() for row in fold_rows), "observed": "disjoint"},
        {"check_id": "P09", "check": "fold-local feature ceiling <=8", "passed": all(len(row["selected_feature_ids"].split("|")) <= 8 for row in fold_rows), "observed": max(len(row["selected_feature_ids"].split("|")) for row in fold_rows)},
        {"check_id": "P10", "check": "no feature or method promoted", "passed": all(row["promotion_status"] == "not_promoted" for row in summary_rows), "observed": "not_promoted"},
    ]

    write_csv(output / "source_hash_audit.csv", source_hash_rows)
    write_csv(output / "feature_x_only_census.csv", feature_census_rows)
    write_csv(output / "feature_redundancy_edges.csv", redundancy_rows)
    write_csv(output / "outer_fold_registry.csv", fold_rows)
    write_csv(output / "fold_local_feature_selection.csv", selection_rows)
    write_csv(output / "feature_selection_frequency.csv", frequency_rows)
    write_csv(output / "oof_predictions.csv", prediction_rows)
    write_csv(output / "metrics.csv", metric_rows)
    write_csv(output / "method_execution_details.csv", method_detail_rows)
    write_csv(output / "target_screening_summary.csv", summary_rows)
    write_csv(output / "producer_QA.csv", qa)

    summary = pd.DataFrame(summary_rows).sort_values("best_pooled_r2", ascending=False)
    fig, ax = plt.subplots(figsize=(10, 7))
    ordered = summary.sort_values("best_pooled_r2")
    ax.barh(ordered.target_name_raw, ordered.best_pooled_r2)
    ax.axvline(0.0, color="black", linewidth=0.8)
    ax.set_xlabel("Best pooled grouped-OOF R² (screening only)")
    ax.set_title(f"{args.cohort.upper()} compression target screening")
    fig.tight_layout()
    fig.savefig(output / "target_screening_pooled_r2.png", dpi=180)
    plt.close(fig)

    best_target = summary.iloc[0]
    part = predictions.loc[
        predictions.target_id.eq(best_target.target_id)
        & predictions.method_id.eq(best_target.best_method_by_pooled_r2)
    ]
    fig, ax = plt.subplots(figsize=(7, 7))
    for group, group_part in part.groupby("outer_group"):
        ax.scatter(group_part.y_true, group_part.y_pred, label=group, alpha=0.8)
    low = min(part.y_true.min(), part.y_pred.min())
    high = max(part.y_true.max(), part.y_pred.max())
    ax.plot([low, high], [low, high], "k--", linewidth=1)
    ax.set_xlabel("Observed y")
    ax.set_ylabel("Grouped-OOF predicted y")
    ax.set_title(f"{best_target.target_name_raw} / {best_target.best_method_by_pooled_r2}")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output / "best_target_y_vs_oof_prediction.png", dpi=180)
    plt.close(fig)

    passed = all(bool(row["passed"]) for row in qa)
    completed = datetime.now(KST)
    report = f"""# COMP-FACTORY-004 {args.cohort.upper()} FS4 technical pilot

- Run ID: `{args.run_id}`
- Status: `{'PASS' if passed else 'FAIL'}`
- Runtime: `{sys.executable}` / Python `{platform.python_version()}`
- Rows: `{len(data)}`
- Outer split: `{'leave-one-B/C/L-family-out' if args.cohort == 'bcl' else 'leave-one-VF-group-out'}`
- Candidate features after provenance/Target-VF/zero-variance exclusions: `{len(eligible_feature_ids)}`
- Targets: `{len(targets)}`
- Methods: `{len(METHODS)}`
- OOF predictions: `{len(predictions)}`
- Runtime seconds: `{time.perf_counter() - started_perf:.3f}`

## Highest screening results

{summary.head(8).to_markdown(index=False)}

## Claim boundary

This is a grouped technical screening pilot. Feature selection is performed inside each outer training fold, and no feature, target, or method is promoted. The result is not a production model, physical optimum, or inverse-design validation.
"""
    (output / "REPORT.md").write_text(report, encoding="utf-8")

    files = []
    for path in sorted(output.iterdir()):
        if path.is_file():
            files.append({"file": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "run_id": args.run_id,
        "cohort": args.cohort,
        "status": "PASS" if passed else "FAIL",
        "started_at_kst": started.isoformat(),
        "completed_at_kst": completed.isoformat(),
        "runtime": {
            "sys_executable": sys.executable,
            "python": platform.python_version(),
            "threads": {key: os.environ.get(key, "") for key in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS")},
        },
        "counts": {
            "rows": len(data),
            "outer_groups": unique_groups,
            "features": len(eligible_feature_ids),
            "targets": len(targets),
            "methods": len(METHODS),
            "oof_predictions": len(predictions),
        },
        "outputs": files,
    }
    (output / "MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(output), "status": manifest["status"], "counts": manifest["counts"]}, ensure_ascii=False, indent=2))
    if not passed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
