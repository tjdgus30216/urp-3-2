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
from typing import Iterable

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.base import clone
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Lasso, OrthogonalMatchingPursuit, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
CONTRACT_PATH = (
    LAB
    / "factories"
    / "COMP-FACTORY-001"
    / "config"
    / "AI_LATTICE_MODELING_PILOT_CONTRACT_v0_1.json"
)
OUTPUT_ROOT = LAB / "data" / "processed" / "COMP-FACTORY-002"
KST = timezone(timedelta(hours=9))
METHODS = ("FS4-METHOD-01", "FS4-METHOD-02", "FS4-METHOD-03", "FS4-METHOD-04")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def source_block(model_numeric_id: int) -> str:
    if model_numeric_id <= 50:
        return "AI001_050"
    if model_numeric_id <= 100:
        return "AI051_100"
    return "AI101_150"


def safe_spearman(x: Iterable[float], y: Iterable[float]) -> float:
    value = pd.Series(np.asarray(list(x), dtype=float)).corr(
        pd.Series(np.asarray(list(y), dtype=float)), method="spearman"
    )
    return float(value) if pd.notna(value) else 0.0


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


def ridge_pipeline(alpha: float = 1.0) -> Pipeline:
    return Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("model", Ridge(alpha=alpha)),
        ]
    )


def fit_preprocessor(x_train: np.ndarray) -> tuple[SimpleImputer, StandardScaler, np.ndarray]:
    imputer = SimpleImputer(strategy="median")
    scaler = StandardScaler()
    scaled = scaler.fit_transform(imputer.fit_transform(x_train))
    return imputer, scaler, scaled


def choose_lasso_alpha(
    x_scaled: np.ndarray, y: np.ndarray, groups: np.ndarray
) -> float:
    alphas = np.logspace(-3, -0.15, 18)
    scores: list[tuple[float, float]] = []
    unique = sorted(set(groups))
    for alpha in alphas:
        errors = []
        for held in unique:
            train_mask = groups != held
            valid_mask = groups == held
            model = Lasso(alpha=float(alpha), max_iter=100000, tol=1e-5, random_state=260731)
            model.fit(x_scaled[train_mask], y[train_mask])
            pred = model.predict(x_scaled[valid_mask])
            errors.append(mean_squared_error(y[valid_mask], pred))
        scores.append((float(np.mean(errors)), float(alpha)))
    return min(scores, key=lambda item: (item[0], item[1]))[1]


def method_01(x_train: np.ndarray, y_train: np.ndarray, x_test: np.ndarray) -> tuple[np.ndarray, dict]:
    models = [ridge_pipeline(0.1), ridge_pipeline(10.0)]
    predictions = []
    for model in models:
        model.fit(x_train, y_train)
        predictions.append(model.predict(x_test))
    return np.mean(np.column_stack(predictions), axis=1), {
        "base_models": 2,
        "recipe_status": "runtime_safe_ridge_blend_surrogate",
        "original_recipe_status": "BayesianRidge_native_scipy_svd_crash_0xC06D007F",
    }


def method_02(
    x_train: np.ndarray,
    y_train: np.ndarray,
    groups: np.ndarray,
    x_test: np.ndarray,
) -> tuple[np.ndarray, dict]:
    imputer, scaler, x_scaled = fit_preprocessor(x_train)
    x_test_scaled = scaler.transform(imputer.transform(x_test))
    y_mean = float(np.mean(y_train))
    y_scale = max(float(np.std(y_train, ddof=0)), 1e-12)
    y_selection = (y_train - y_mean) / y_scale
    alpha = choose_lasso_alpha(x_scaled, y_selection, groups)
    rng = np.random.default_rng(260731)
    counts = np.zeros(x_scaled.shape[1], dtype=int)
    n_boot = 30
    for _ in range(n_boot):
        chosen_indices: list[int] = []
        for group in sorted(set(groups)):
            idx = np.flatnonzero(groups == group)
            take = max(3, int(math.ceil(0.80 * len(idx))))
            chosen_indices.extend(rng.choice(idx, size=take, replace=False).tolist())
        chosen = np.asarray(sorted(chosen_indices), dtype=int)
        model = Lasso(alpha=alpha, max_iter=100000, tol=1e-5, random_state=260731)
        model.fit(x_scaled[chosen], y_selection[chosen])
        counts += np.abs(model.coef_) > 1e-10
    probabilities = counts / float(n_boot)
    selected = np.flatnonzero(probabilities >= 0.35)
    if len(selected) < 2:
        selected = np.argsort(probabilities)[::-1][: min(6, x_scaled.shape[1])]
    elif len(selected) > 6:
        selected = selected[np.argsort(probabilities[selected])[::-1][:6]]
    selected = np.asarray(sorted(selected), dtype=int)
    model = Ridge(alpha=1.0).fit(x_scaled[:, selected], y_train)
    return model.predict(x_test_scaled[:, selected]), {
        "lasso_alpha": alpha,
        "selection_y_standardized_within_outer_train": True,
        "internal_selected_indices": "|".join(map(str, selected.tolist())),
        "max_stability_probability": float(probabilities.max()),
        "base_models": n_boot + 1,
    }


def choose_omp_k(x_scaled: np.ndarray, y: np.ndarray, groups: np.ndarray) -> int:
    candidates = range(1, min(6, x_scaled.shape[1]) + 1)
    scored = []
    for k in candidates:
        errors = []
        for held in sorted(set(groups)):
            train_mask = groups != held
            valid_mask = groups == held
            model = OrthogonalMatchingPursuit(n_nonzero_coefs=k, fit_intercept=True)
            model.fit(x_scaled[train_mask], y[train_mask])
            pred = model.predict(x_scaled[valid_mask])
            errors.append(mean_squared_error(y[valid_mask], pred))
        scored.append((float(np.mean(errors)), int(k)))
    return min(scored, key=lambda item: (item[0], item[1]))[1]


def method_03(
    x_train: np.ndarray,
    y_train: np.ndarray,
    groups: np.ndarray,
    x_test: np.ndarray,
) -> tuple[np.ndarray, dict]:
    imputer, scaler, x_scaled = fit_preprocessor(x_train)
    x_test_scaled = scaler.transform(imputer.transform(x_test))
    k = choose_omp_k(x_scaled, y_train, groups)
    selector = OrthogonalMatchingPursuit(n_nonzero_coefs=k, fit_intercept=True)
    selector.fit(x_scaled, y_train)
    selected = np.flatnonzero(np.abs(selector.coef_) > 1e-12)
    if not len(selected):
        selected = np.asarray([int(np.argmax(np.abs(x_scaled.T @ y_train)))])
    model = Ridge(alpha=1.0).fit(x_scaled[:, selected], y_train)
    return model.predict(x_test_scaled[:, selected]), {
        "omp_k": k,
        "internal_selected_indices": "|".join(map(str, selected.tolist())),
        "base_models": 2,
    }


def method_04(
    x_train: np.ndarray,
    y_train: np.ndarray,
    groups: np.ndarray,
    x_test: np.ndarray,
    selected_feature_ids: list[str],
    feature_roles: dict[str, str],
) -> tuple[np.ndarray, dict]:
    domain_indices: dict[str, list[int]] = {"full": list(range(len(selected_feature_ids)))}
    condition = [
        index
        for index, feature_id in enumerate(selected_feature_ids)
        if feature_roles.get(feature_id) in {"physical_condition_candidate", "condition_sensitivity"}
    ]
    topology = [
        index
        for index, feature_id in enumerate(selected_feature_ids)
        if 5 <= int(feature_id.replace("AIX", "")) <= 32
    ]
    geometry = [
        index
        for index, feature_id in enumerate(selected_feature_ids)
        if int(feature_id.replace("AIX", "")) >= 33
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
            pred = model.predict(x_train[valid_mask][:, indices])
            branch_errors[name].append(mean_squared_error(y_train[valid_mask], pred))
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
        "base_models": len(ordered_names) * 3,
    }


def union_find_groups(correlation: pd.DataFrame, threshold: float) -> dict[str, str]:
    columns = list(correlation.columns)
    parent = {column: column for column in columns}

    def find(value: str) -> str:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def union(left: str, right: str) -> None:
        root_left, root_right = find(left), find(right)
        if root_left != root_right:
            parent[max(root_left, root_right)] = min(root_left, root_right)

    for i, left in enumerate(columns):
        for right in columns[i + 1 :]:
            value = correlation.loc[left, right]
            if pd.notna(value) and abs(float(value)) >= threshold:
                union(left, right)
    roots = {column: find(column) for column in columns}
    root_order = {root: index + 1 for index, root in enumerate(sorted(set(roots.values())))}
    return {column: f"AIX-BLOCK-{root_order[root]:03d}" for column, root in roots.items()}


def fold_select(
    x_train: pd.DataFrame,
    y_train: np.ndarray,
    block_ids: dict[str, str],
    max_features: int,
) -> tuple[list[str], list[dict]]:
    by_block: dict[str, list[str]] = {}
    for feature_id in x_train.columns:
        by_block.setdefault(block_ids[feature_id], []).append(feature_id)
    scored = []
    for block_id, members in by_block.items():
        member_scores = {
            feature_id: abs(safe_spearman(x_train[feature_id], y_train))
            for feature_id in members
        }
        representative = min(
            members,
            key=lambda feature_id: (-member_scores[feature_id], feature_id),
        )
        scored.append((member_scores[representative], block_id, representative, member_scores))
    scored.sort(key=lambda item: (-item[0], item[1], item[2]))
    selected = [item[2] for item in scored[:max_features]]
    records = [
        {
            "selection_rank": rank,
            "block_id": item[1],
            "selected_feature_id": item[2],
            "abs_spearman_train": item[0],
            "block_member_scores_json": json.dumps(item[3], sort_keys=True),
        }
        for rank, item in enumerate(scored[:max_features], start=1)
    ]
    return selected, records


def write_csv(path: Path, rows: list[dict]) -> None:
    pd.DataFrame(rows).to_csv(path, index=False, encoding="utf-8-sig")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    out = OUTPUT_ROOT / args.run_id
    if out.exists():
        raise RuntimeError(f"run folder already exists: {out}")
    out.mkdir(parents=True)
    started = datetime.now(KST)
    t0 = time.perf_counter()
    print(f"[COMP002] start {args.run_id}", flush=True)

    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    input_paths: dict[str, Path] = {}
    source_hash_rows = []
    for item in contract["inputs"]:
        path = ROOT / item["path"]
        actual = sha256(path)
        if actual != item["sha256"]:
            raise RuntimeError(f"source hash mismatch: {path}")
        input_paths[path.name] = path
        source_hash_rows.append(
            {
                "path": item["path"],
                "expected_sha256": item["sha256"],
                "actual_sha256": actual,
                "status": "PASS",
            }
        )

    data = pd.read_csv(input_paths["ai_lattice_xy_eligible149.csv"])
    feature_registry = pd.read_csv(input_paths["feature_registry.csv"])
    target_registry = pd.read_csv(input_paths["target_registry.csv"])
    print("[COMP002] sources loaded and hashes verified", flush=True)
    if len(data) != contract["row_policy"]["eligible_rows"]:
        raise RuntimeError("eligible row count drift")
    if set(data.model_id) & set(contract["row_policy"]["excluded_model_ids"]):
        raise RuntimeError("excluded model entered pilot")
    data["source_block"] = data.model_numeric_id.astype(int).map(source_block)

    feature_registry["column_name"] = "x__" + feature_registry.feature_name_raw.astype(str)
    feature_registry["numeric_feature_id"] = feature_registry.feature_id.str.replace("AIX", "", regex=False).astype(int)
    candidate_rows = feature_registry.loc[
        ~feature_registry.feature_role.isin(contract["feature_policy"]["exclude_roles"])
        & ~feature_registry.feature_id.isin(contract["feature_policy"]["exclude_feature_ids"])
    ].copy()
    census_rows = []
    eligible_ids = []
    feature_id_to_column = dict(zip(feature_registry.feature_id, feature_registry.column_name))
    feature_roles = dict(zip(feature_registry.feature_id, feature_registry.feature_role))
    for row in candidate_rows.itertuples(index=False):
        values = pd.to_numeric(data[row.column_name], errors="coerce")
        finite = np.isfinite(values.to_numpy(float))
        unique_count = int(values[finite].nunique())
        std = float(values[finite].std(ddof=0)) if finite.any() else float("nan")
        q25, q75 = values[finite].quantile([0.25, 0.75]) if finite.any() else (np.nan, np.nan)
        median = float(values[finite].median()) if finite.any() else float("nan")
        mad = float(np.median(np.abs(values[finite] - median))) if finite.any() else float("nan")
        status = "eligible"
        if finite.sum() != len(data):
            status = "excluded_nonfinite"
        elif unique_count < 2 or not np.isfinite(std) or std <= 0:
            status = "excluded_zero_variance"
        else:
            eligible_ids.append(row.feature_id)
        census_rows.append(
            {
                "feature_id": row.feature_id,
                "feature_name_raw": row.feature_name_raw,
                "feature_role": row.feature_role,
                "finite_count": int(finite.sum()),
                "missing_count": int((~finite).sum()),
                "unique_count": unique_count,
                "std": std,
                "median": median,
                "iqr": float(q75 - q25) if finite.any() else float("nan"),
                "mad": mad,
                "x_only_status": status,
            }
        )
    if not eligible_ids:
        raise RuntimeError("no eligible features")

    x_by_id = pd.DataFrame(
        {
            feature_id: pd.to_numeric(data[feature_id_to_column[feature_id]], errors="coerce")
            for feature_id in eligible_ids
        }
    )
    correlation = x_by_id.corr(method="pearson")
    block_ids = union_find_groups(
        correlation,
        float(contract["feature_policy"]["global_x_only_redundancy_threshold_abs_pearson"]),
    )
    print(f"[COMP002] x-only census complete: {len(eligible_ids)} eligible", flush=True)
    redundancy_rows = []
    for left_index, left in enumerate(eligible_ids):
        for right in eligible_ids[left_index + 1 :]:
            corr = float(correlation.loc[left, right])
            if abs(corr) >= 0.95:
                redundancy_rows.append(
                    {
                        "left_feature_id": left,
                        "right_feature_id": right,
                        "pearson": corr,
                        "abs_pearson": abs(corr),
                        "same_nonselecting_block": block_ids[left] == block_ids[right],
                        "left_block_id": block_ids[left],
                        "right_block_id": block_ids[right],
                    }
                )

    collision_rows = []
    standardized = (x_by_id - x_by_id.mean()) / x_by_id.std(ddof=0)
    matrix = standardized.to_numpy(float)
    for index, model_id in enumerate(data.model_id.astype(str)):
        distances = np.sqrt(np.mean((matrix - matrix[index]) ** 2, axis=1))
        distances[index] = np.inf
        neighbor_index = int(np.argmin(distances))
        collision_rows.append(
            {
                "model_id": model_id,
                "nearest_model_id": str(data.iloc[neighbor_index].model_id),
                "standardized_rms_distance": float(distances[neighbor_index]),
                "exact_collision": bool(distances[neighbor_index] <= 1e-12),
            }
        )

    target_rows = target_registry.loc[
        target_registry.status.eq(contract["target_policy"]["include_status"])
        & ~target_registry.target_id.isin(contract["target_policy"]["exclude_target_ids"])
    ].copy()
    if len(target_rows) != contract["target_policy"]["expected_targets"]:
        raise RuntimeError("target registry eligibility drift")
    print(f"[COMP002] targets ready: {len(target_rows)}", flush=True)

    target_id_to_column = {
        row.target_id: "y__" + str(row.target_name_raw)
        for row in target_rows.itertuples(index=False)
    }
    target_census_rows = []
    target_vectors = {}
    for row in target_rows.itertuples(index=False):
        values = pd.to_numeric(
            data[target_id_to_column[row.target_id]], errors="coerce"
        ).to_numpy(float)
        target_vectors[row.target_id] = values
        target_census_rows.append(
            {
                "target_id": row.target_id,
                "target_name_raw": row.target_name_raw,
                "finite_count": int(np.isfinite(values).sum()),
                "unique_count": int(pd.Series(values).nunique()),
                "mean": float(np.mean(values)),
                "std": float(np.std(values, ddof=0)),
                "min": float(np.min(values)),
                "q25": float(np.quantile(values, 0.25)),
                "median": float(np.median(values)),
                "q75": float(np.quantile(values, 0.75)),
                "max": float(np.max(values)),
                "objective_direction": "unresolved",
                "selection_status": "unselected",
            }
        )
    target_redundancy_rows = []
    target_ids = list(target_rows.target_id)
    for left_index, left in enumerate(target_ids):
        for right in target_ids[left_index + 1 :]:
            left_values, right_values = target_vectors[left], target_vectors[right]
            pearson = float(np.corrcoef(left_values, right_values)[0, 1])
            spearman = safe_spearman(left_values, right_values)
            exact = bool(np.array_equal(left_values, right_values))
            if exact or abs(pearson) >= 0.95 or abs(spearman) >= 0.95:
                target_redundancy_rows.append(
                    {
                        "left_target_id": left,
                        "right_target_id": right,
                        "exact_equal": exact,
                        "pearson": pearson,
                        "spearman": spearman,
                        "relationship_status": (
                            "exact_duplicate" if exact else "high_redundancy_review"
                        ),
                        "promotion_status": "not_promoted",
                    }
                )
    target_block_rows = []
    for row in target_rows.itertuples(index=False):
        values = target_vectors[row.target_id]
        for block in sorted(data.source_block.unique()):
            mask = data.source_block.eq(block).to_numpy()
            block_values = values[mask]
            target_block_rows.append(
                {
                    "target_id": row.target_id,
                    "target_name_raw": row.target_name_raw,
                    "source_block": block,
                    "n": int(mask.sum()),
                    "mean": float(np.mean(block_values)),
                    "std": float(np.std(block_values, ddof=0)),
                    "median": float(np.median(block_values)),
                    "min": float(np.min(block_values)),
                    "max": float(np.max(block_values)),
                }
            )

    fold_rows = []
    selection_rows = []
    prediction_rows = []
    metric_rows = []
    method_detail_rows = []
    blocks = sorted(data.source_block.unique())
    for held_block in blocks:
        test_mask = data.source_block.eq(held_block).to_numpy()
        train_mask = ~test_mask
        fold_rows.append(
            {
                "outer_fold_id": f"HOLD_{held_block}",
                "held_source_block": held_block,
                "train_count": int(train_mask.sum()),
                "test_count": int(test_mask.sum()),
                "train_model_ids": "|".join(data.loc[train_mask, "model_id"].astype(str)),
                "test_model_ids": "|".join(data.loc[test_mask, "model_id"].astype(str)),
            }
        )

    for target in target_rows.itertuples(index=False):
        print(f"[COMP002] target {target.target_id}", flush=True)
        target_column = "y__" + str(target.target_name_raw)
        y_all = pd.to_numeric(data[target_column], errors="coerce").to_numpy(float)
        if not np.isfinite(y_all).all() or np.std(y_all) <= 0:
            raise RuntimeError(f"target is nonfinite or constant: {target.target_id}")
        for held_block in blocks:
            outer_id = f"HOLD_{held_block}"
            test_mask = data.source_block.eq(held_block).to_numpy()
            train_mask = ~test_mask
            train_frame = x_by_id.loc[train_mask].reset_index(drop=True)
            y_train = y_all[train_mask]
            y_test = y_all[test_mask]
            selected, selected_records = fold_select(
                train_frame,
                y_train,
                block_ids,
                int(contract["feature_policy"]["max_selected_scalars_per_outer_fold"]),
            )
            for record in selected_records:
                record.update(
                    {
                        "target_id": target.target_id,
                        "target_name_raw": target.target_name_raw,
                        "outer_fold_id": outer_id,
                        "held_source_block": held_block,
                    }
                )
                selection_rows.append(record)
            x_train = x_by_id.loc[train_mask, selected].to_numpy(float)
            x_test = x_by_id.loc[test_mask, selected].to_numpy(float)
            groups_train = data.loc[train_mask, "source_block"].to_numpy(str)
            null_pred = np.repeat(float(np.mean(y_train)), len(y_test))
            method_functions = {
                "FS4-METHOD-01": lambda: method_01(x_train, y_train, x_test),
                "FS4-METHOD-02": lambda: method_02(x_train, y_train, groups_train, x_test),
                "FS4-METHOD-03": lambda: method_03(x_train, y_train, groups_train, x_test),
                "FS4-METHOD-04": lambda: method_04(
                    x_train, y_train, groups_train, x_test, selected, feature_roles
                ),
            }
            for method_id in METHODS:
                print(f"[COMP002] {target.target_id} {outer_id} {method_id}", flush=True)
                method_started = time.perf_counter()
                prediction, detail = method_functions[method_id]()
                if len(prediction) != len(y_test) or not np.isfinite(prediction).all():
                    raise RuntimeError(f"invalid prediction: {target.target_id} {outer_id} {method_id}")
                fold_metrics = metric_dict(y_test, prediction, null_pred)
                metric_rows.append(
                    {
                        "scope": "outer_fold",
                        "target_id": target.target_id,
                        "target_name_raw": target.target_name_raw,
                        "method_id": method_id,
                        "outer_fold_id": outer_id,
                        "held_source_block": held_block,
                        "n": len(y_test),
                        **fold_metrics,
                    }
                )
                method_detail_rows.append(
                    {
                        "target_id": target.target_id,
                        "method_id": method_id,
                        "outer_fold_id": outer_id,
                        "selected_feature_ids": "|".join(selected),
                        "runtime_seconds": time.perf_counter() - method_started,
                        "detail_json": json.dumps(detail, sort_keys=True),
                        "status": "completed_unselected",
                    }
                )
                test_rows = data.loc[test_mask].reset_index(drop=True)
                for row_index, model_id in enumerate(test_rows.model_id.astype(str)):
                    prediction_rows.append(
                        {
                            "target_id": target.target_id,
                            "target_name_raw": target.target_name_raw,
                            "method_id": method_id,
                            "outer_fold_id": outer_id,
                            "held_source_block": held_block,
                            "model_id": model_id,
                            "source_block": str(test_rows.iloc[row_index].source_block),
                            "y_true": float(y_test[row_index]),
                            "y_pred": float(prediction[row_index]),
                            "null_pred": float(null_pred[row_index]),
                            "residual": float(y_test[row_index] - prediction[row_index]),
                        }
                    )

    predictions = pd.DataFrame(prediction_rows)
    pooled_rows = []
    for target_id in target_rows.target_id:
        for method_id in METHODS:
            part = predictions.loc[
                predictions.target_id.eq(target_id) & predictions.method_id.eq(method_id)
            ]
            values = metric_dict(
                part.y_true.to_numpy(float),
                part.y_pred.to_numpy(float),
                part.null_pred.to_numpy(float),
            )
            pooled = {
                "scope": "pooled_source_block_oof",
                "target_id": target_id,
                "target_name_raw": str(part.target_name_raw.iloc[0]),
                "method_id": method_id,
                "outer_fold_id": "ALL_3_BLOCKS",
                "held_source_block": "ALL",
                "n": len(part),
                **values,
            }
            metric_rows.append(pooled)
            pooled_rows.append(pooled)

    pooled = pd.DataFrame(pooled_rows)
    target_summary_rows = []
    for target in target_rows.itertuples(index=False):
        part = pooled.loc[pooled.target_id.eq(target.target_id)].copy()
        part["rank_key"] = part.r2.fillna(-np.inf)
        best = part.sort_values(["rank_key", "rmse"], ascending=[False, True]).iloc[0]
        feature_counts = Counter(
            row["selected_feature_id"]
            for row in selection_rows
            if row["target_id"] == target.target_id
        )
        stable = sorted(
            feature_id
            for feature_id, count in feature_counts.items()
            if count == len(blocks)
        )
        r2 = float(best.r2)
        best_fold_rows = pd.DataFrame(metric_rows)
        best_fold_rows = best_fold_rows.loc[
            best_fold_rows.scope.eq("outer_fold")
            & best_fold_rows.target_id.eq(target.target_id)
            & best_fold_rows.method_id.eq(best.method_id)
        ]
        fold_positive_r2_count = int((best_fold_rows.r2 > 0).sum())
        fold_improved_null_count = int((best_fold_rows.delta_rmse_vs_null < 0).sum())
        median_fold_r2 = float(best_fold_rows.r2.median())
        minimum_fold_r2 = float(best_fold_rows.r2.min())
        if median_fold_r2 >= 0.30 and fold_positive_r2_count == 3:
            signal = "strong_within_block_pilot_signal"
        elif median_fold_r2 >= 0.10 and fold_positive_r2_count >= 2:
            signal = "moderate_within_block_pilot_signal"
        elif median_fold_r2 > 0 and fold_positive_r2_count >= 2:
            signal = "weak_within_block_plus_between_block_signal"
        elif r2 >= 0.20:
            signal = "between_block_dominated_signal"
        elif float(best.delta_rmse_vs_null) < 0:
            signal = "weak_positive_pooled_signal"
        else:
            signal = "no_oof_improvement"
        target_summary_rows.append(
            {
                "target_id": target.target_id,
                "target_name_raw": target.target_name_raw,
                "best_method_by_pooled_r2": best.method_id,
                "best_pooled_r2": r2,
                "best_pooled_mae": float(best.mae),
                "best_pooled_rmse": float(best.rmse),
                "best_nrmse_by_std": float(best.nrmse_by_std),
                "best_spearman": float(best.spearman),
                "delta_rmse_vs_null": float(best.delta_rmse_vs_null),
                "positive_outer_fold_r2_count": fold_positive_r2_count,
                "improved_train_mean_null_fold_count": fold_improved_null_count,
                "median_outer_fold_r2": median_fold_r2,
                "minimum_outer_fold_r2": minimum_fold_r2,
                "signal_status": signal,
                "features_selected_in_all_3_outer_folds": "|".join(stable),
                "objective_direction": "unresolved",
                "promotion_status": "not_promoted",
            }
        )

    selection_frequency_rows = []
    for target_id in target_rows.target_id:
        target_selection = [
            row for row in selection_rows if row["target_id"] == target_id
        ]
        counts = Counter(row["selected_feature_id"] for row in target_selection)
        for feature_id, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
            selection_frequency_rows.append(
                {
                    "target_id": target_id,
                    "feature_id": feature_id,
                    "feature_name_raw": feature_registry.loc[
                        feature_registry.feature_id.eq(feature_id), "feature_name_raw"
                    ].iloc[0],
                    "selected_outer_fold_count": count,
                    "outer_fold_count": len(blocks),
                    "selection_frequency": count / len(blocks),
                    "promotion_status": "not_promoted",
                }
            )

    producer_qa = [
        {"check_id": "P01", "check": "eligible rows 149", "passed": len(data) == 149, "observed": len(data)},
        {"check_id": "P02", "check": "AI092 excluded", "passed": "AI092" not in set(data.model_id), "observed": "AI092" in set(data.model_id)},
        {"check_id": "P03", "check": "three source blocks", "passed": len(blocks) == 3, "observed": len(blocks)},
        {"check_id": "P04", "check": "16 finite targets", "passed": len(target_rows) == 16, "observed": len(target_rows)},
        {"check_id": "P05", "check": "feature ceiling respected", "passed": all(sum(1 for row in selection_rows if row["target_id"] == target and row["outer_fold_id"] == fold) <= 8 for target in target_rows.target_id for fold in [f"HOLD_{block}" for block in blocks]), "observed": max(Counter((row["target_id"], row["outer_fold_id"]) for row in selection_rows).values())},
        {"check_id": "P06", "check": "complete predictions", "passed": len(prediction_rows) == 16 * 4 * 149, "observed": len(prediction_rows)},
        {"check_id": "P07", "check": "pooled metric rows", "passed": len(pooled_rows) == 16 * 4, "observed": len(pooled_rows)},
        {"check_id": "P08", "check": "all predictions finite", "passed": bool(np.isfinite(predictions[["y_true", "y_pred", "null_pred"]].to_numpy(float)).all()), "observed": "finite"},
        {"check_id": "P09", "check": "no feature promoted", "passed": all(row["promotion_status"] == "not_promoted" for row in target_summary_rows), "observed": "not_promoted"},
        {"check_id": "P10", "check": "target census 16", "passed": len(target_census_rows) == 16, "observed": len(target_census_rows)},
        {"check_id": "P11", "check": "target redundancy audit produced", "passed": len(target_redundancy_rows) >= 1, "observed": len(target_redundancy_rows)},
        {"check_id": "P12", "check": "target block summary 16x3", "passed": len(target_block_rows) == 48, "observed": len(target_block_rows)},
    ]
    if not all(row["passed"] for row in producer_qa):
        raise RuntimeError("producer QA failed")
    print("[COMP002] producer QA passed; publishing artifacts", flush=True)

    write_csv(out / "source_hash_audit.csv", source_hash_rows)
    write_csv(out / "target_y_census.csv", target_census_rows)
    write_csv(out / "target_y_redundancy_edges.csv", target_redundancy_rows)
    write_csv(out / "target_y_source_block_summary.csv", target_block_rows)
    write_csv(out / "feature_x_only_census.csv", census_rows)
    write_csv(out / "feature_redundancy_edges.csv", redundancy_rows)
    write_csv(out / "nearest_neighbor_collision_audit.csv", collision_rows)
    write_csv(out / "outer_fold_registry.csv", fold_rows)
    write_csv(out / "fold_local_feature_selection.csv", selection_rows)
    write_csv(out / "feature_selection_frequency.csv", selection_frequency_rows)
    write_csv(out / "oof_predictions.csv", prediction_rows)
    write_csv(out / "metrics.csv", metric_rows)
    write_csv(out / "method_execution_details.csv", method_detail_rows)
    write_csv(out / "target_screening_summary.csv", target_summary_rows)
    write_csv(out / "producer_QA.csv", producer_qa)

    figures = out / "figures"
    figures.mkdir()
    target_summary_frame = pd.DataFrame(target_summary_rows).sort_values(
        "best_pooled_r2", ascending=False
    )
    top_targets = target_summary_frame.head(8)
    colors = {
        "AI001_050": "#2563eb",
        "AI051_100": "#f59e0b",
        "AI101_150": "#16a34a",
    }
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    for ax, target_row in zip(axes.ravel(), top_targets.itertuples(index=False)):
        part = predictions.loc[
            predictions.target_id.eq(target_row.target_id)
            & predictions.method_id.eq(target_row.best_method_by_pooled_r2)
        ]
        for block, group in part.groupby("source_block"):
            ax.scatter(
                group.y_true,
                group.y_pred,
                s=18,
                alpha=0.75,
                label=block,
                color=colors[block],
            )
        low = min(float(part.y_true.min()), float(part.y_pred.min()))
        high = max(float(part.y_true.max()), float(part.y_pred.max()))
        ax.plot([low, high], [low, high], "--", color="#111827", linewidth=1)
        ax.set_title(
            f"{target_row.target_name_raw}\n"
            f"pooled R²={target_row.best_pooled_r2:.3f}, "
            f"median fold R²={target_row.median_outer_fold_r2:.3f}"
        )
        ax.set_xlabel("actual y")
        ax.set_ylabel("OOF predicted y")
        ax.grid(alpha=0.2)
    handles, labels = axes.ravel()[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3)
    fig.suptitle("AI Lattice source-block OOF: actual y vs predicted y", fontsize=14)
    fig.tight_layout(rect=(0, 0.05, 1, 0.96))
    fig.savefig(figures / "f1_yx.png", dpi=170)
    plt.close(fig)

    ordered = target_summary_frame.sort_values("best_pooled_r2")
    y_pos = np.arange(len(ordered))
    fig, ax = plt.subplots(figsize=(11, 8))
    ax.scatter(ordered.best_pooled_r2, y_pos, label="pooled OOF R²", color="#2563eb")
    ax.scatter(ordered.median_outer_fold_r2, y_pos, label="median within-block R²", color="#dc2626")
    ax.axvline(0, color="#111827", linewidth=1)
    ax.set_yticks(y_pos, ordered.target_name_raw)
    ax.set_xlabel("R²")
    ax.set_title("Pooled signal versus within-source-block consistency")
    ax.legend()
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(figures / "f2_r2.png", dpi=170)
    plt.close(fig)

    block_frame = pd.DataFrame(target_block_rows)
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    for ax, target_row in zip(axes.ravel(), top_targets.head(4).itertuples(index=False)):
        part = block_frame.loc[block_frame.target_id.eq(target_row.target_id)]
        ax.errorbar(
            part.source_block,
            part["mean"],
            yerr=part["std"],
            fmt="o-",
            capsize=4,
            color="#7c3aed",
        )
        ax.set_title(target_row.target_name_raw)
        ax.set_ylabel("mean ± population std")
        ax.tick_params(axis="x", rotation=15)
        ax.grid(alpha=0.2)
    fig.suptitle("Performance distribution shift across the three source workbooks", fontsize=14)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(figures / "f3_block.png", dpi=170)
    plt.close(fig)

    report = f"""# {args.run_id}

## Result

- Status: PASS
- Rows: {len(data)}
- Excluded missing-y model: AI092
- Evaluated targets: {len(target_rows)}
- Eligible nonconstant x candidates: {len(eligible_ids)}
- Outer policy: leave one source workbook block out (3 folds)
- Methods: {len(METHODS)}
- OOF predictions: {len(prediction_rows)}
- Feature promotion: 0
- Production/inverse-design claim: 0
- Method-01 runtime deviation: fixed Ridge blend surrogate; exact BayesianRidge recipe not executed
- Figures: `figures/f1_yx.png`, `figures/f2_r2.png`, `figures/f3_block.png`

## Interpretation boundary

This is a source-block OOF technical pilot. The three summary workbooks are used as provisional groups,
but they are not proven generator-lineage groups. Target units and maximize/minimize directions remain unresolved.
All feature selection occurs inside each outer training fold. No feature or method is promoted.
Method-01 is a runtime-safe surrogate because canonical KMK312 crashed in SciPy SVD during BayesianRidge.
"""
    (out / "REPORT.md").write_text(report, encoding="utf-8")
    completed = datetime.now(KST)
    manifest = {
        "run_id": args.run_id,
        "contract_id": contract["contract_id"],
        "status": "passed",
        "started_at_kst": started.isoformat(),
        "completed_at_kst": completed.isoformat(),
        "runtime_seconds": time.perf_counter() - t0,
        "runtime": {
            "sys_executable": sys.executable,
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "omp_num_threads": os.environ.get("OMP_NUM_THREADS"),
            "mkl_num_threads": os.environ.get("MKL_NUM_THREADS"),
        },
        "counts": {
            "rows": len(data),
            "targets": len(target_rows),
            "eligible_features": len(eligible_ids),
            "outer_folds": len(blocks),
            "methods": len(METHODS),
            "predictions": len(prediction_rows),
        },
        "input_hashes": source_hash_rows,
        "output_hashes": {},
        "claim_boundary": contract["claims"],
    }
    for path in sorted(out.rglob("*")):
        if path.is_file() and path.name != "MANIFEST.json":
            manifest["output_hashes"][path.relative_to(out).as_posix()] = sha256(path)
    (out / "MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({"run_id": args.run_id, "status": "PASS", "output": str(out), "counts": manifest["counts"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
