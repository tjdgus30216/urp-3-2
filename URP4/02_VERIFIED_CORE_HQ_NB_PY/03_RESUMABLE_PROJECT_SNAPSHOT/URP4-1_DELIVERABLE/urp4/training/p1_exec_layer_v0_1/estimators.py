from __future__ import annotations

import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin, clone
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LassoCV, OrthogonalMatchingPursuitCV, Ridge
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.utils.validation import check_array, check_is_fitted, check_X_y

from .models import ExecLayerContractError, ExecutionPermit
from .permit import assert_execution_authorized


class _GuardedEstimator(BaseEstimator, RegressorMixin):
    method_family_id: str
    prospective_fits_per_outer: int

    def _authorize(self) -> None:
        assert_execution_authorized(
            self.permit,
            method_family_id=self.method_family_id,
            outer_fold_id=self.outer_fold_id,
            prospective_fit_count=self.prospective_fits_per_outer,
        )


class GuardedWeightedBlendRegressor(_GuardedEstimator):
    method_family_id = "FS4-METHOD-01"
    prospective_fits_per_outer = 10

    def __init__(self, *, estimators=(), weights=(), outer_fold_id="", permit: ExecutionPermit | None = None):
        self.estimators = estimators
        self.weights = weights
        self.outer_fold_id = outer_fold_id
        self.permit = permit

    def fit(self, X, y):
        self._authorize()
        X_checked, y_checked = check_X_y(X, y, ensure_all_finite="allow-nan")
        if not self.estimators:
            raise ExecLayerContractError("weighted blend has no base estimators")
        weights = np.asarray(self.weights if self.weights else np.ones(len(self.estimators)), dtype=float)
        if len(weights) != len(self.estimators) or not np.isfinite(weights).all() or (weights < 0).any() or weights.sum() <= 0:
            raise ExecLayerContractError("invalid blend weights")
        self.weights_ = weights / weights.sum()
        self.estimators_ = [clone(estimator).fit(X_checked, y_checked) for estimator in self.estimators]
        self.actual_estimator_fits_ = len(self.estimators_)
        return self

    def predict(self, X):
        self._authorize()
        check_is_fitted(self, ("estimators_", "weights_"))
        X_checked = check_array(X, ensure_all_finite="allow-nan")
        predictions = np.column_stack([estimator.predict(X_checked) for estimator in self.estimators_])
        return predictions @ self.weights_


class GuardedStabilityLassoRidge(_GuardedEstimator):
    method_family_id = "FS4-METHOD-02"
    prospective_fits_per_outer = 249

    def __init__(
        self,
        *,
        n_boot=60,
        subsample=0.80,
        probability_threshold=0.35,
        top_keep=6,
        ridge_alpha=1.0,
        random_state=260721,
        outer_fold_id="",
        permit: ExecutionPermit | None = None,
    ):
        self.n_boot = n_boot
        self.subsample = subsample
        self.probability_threshold = probability_threshold
        self.top_keep = top_keep
        self.ridge_alpha = ridge_alpha
        self.random_state = random_state
        self.outer_fold_id = outer_fold_id
        self.permit = permit

    def fit(self, X, y, *, groups=None):
        self._authorize()
        X_checked, y_checked = check_X_y(X, y, ensure_all_finite="allow-nan")
        if groups is None:
            raise ExecLayerContractError("stability selection requires groups")
        groups = np.asarray(groups)
        if len(groups) != len(y_checked):
            raise ExecLayerContractError("groups length mismatch")
        self.imputer_ = SimpleImputer(strategy="median")
        self.scaler_ = StandardScaler()
        X_scaled = self.scaler_.fit_transform(self.imputer_.fit_transform(X_checked))
        unique_groups = np.unique(groups)
        if len(unique_groups) < 4:
            raise ExecLayerContractError("stability selection requires at least four groups")
        rng = np.random.default_rng(self.random_state)
        counts = np.zeros(X_scaled.shape[1], dtype=int)
        selected_group_count = max(2, int(np.ceil(float(self.subsample) * len(unique_groups))))
        for _ in range(int(self.n_boot)):
            chosen = rng.choice(unique_groups, size=selected_group_count, replace=False)
            mask = np.isin(groups, chosen)
            model = LassoCV(cv=4, max_iter=10000, random_state=self.random_state)
            model.fit(X_scaled[mask], y_checked[mask])
            counts += np.abs(model.coef_) > 1e-10
        probabilities = counts / float(self.n_boot)
        selected = np.flatnonzero(probabilities >= float(self.probability_threshold))
        if len(selected) < 2:
            selected = np.argsort(probabilities)[::-1][: max(2, min(int(self.top_keep), X_scaled.shape[1]))]
        elif len(selected) > int(self.top_keep):
            selected = selected[np.argsort(probabilities[selected])[::-1][: int(self.top_keep)]]
        self.selected_features_ = np.asarray(sorted(selected), dtype=int)
        self.selection_probability_ = probabilities
        self.regressor_ = Ridge(alpha=float(self.ridge_alpha)).fit(X_scaled[:, self.selected_features_], y_checked)
        self.actual_estimator_fits_ = int(self.n_boot) + 1
        return self

    def predict(self, X):
        self._authorize()
        check_is_fitted(self, ("imputer_", "scaler_", "selected_features_", "regressor_"))
        X_checked = check_array(X, ensure_all_finite="allow-nan")
        X_scaled = self.scaler_.transform(self.imputer_.transform(X_checked))
        return self.regressor_.predict(X_scaled[:, self.selected_features_])


class GuardedOMPThenRidge(_GuardedEstimator):
    method_family_id = "FS4-METHOD-03"
    prospective_fits_per_outer = 33

    def __init__(self, *, max_nonzero_coefs=6, ridge_alpha=1.0, outer_fold_id="", permit: ExecutionPermit | None = None):
        self.max_nonzero_coefs = max_nonzero_coefs
        self.ridge_alpha = ridge_alpha
        self.outer_fold_id = outer_fold_id
        self.permit = permit

    def fit(self, X, y):
        self._authorize()
        X_checked, y_checked = check_X_y(X, y, ensure_all_finite="allow-nan")
        self.imputer_ = SimpleImputer(strategy="median")
        self.scaler_ = StandardScaler()
        X_scaled = self.scaler_.fit_transform(self.imputer_.fit_transform(X_checked))
        max_iter = max(2, min(int(self.max_nonzero_coefs), X_scaled.shape[1]))
        self.selector_ = OrthogonalMatchingPursuitCV(max_iter=max_iter).fit(X_scaled, y_checked)
        selected = np.flatnonzero(np.abs(self.selector_.coef_) > 1e-12)
        if not len(selected):
            selected = np.asarray([int(np.argmax(np.abs(X_scaled.T @ y_checked)))])
        self.selected_features_ = selected
        self.regressor_ = Ridge(alpha=float(self.ridge_alpha)).fit(X_scaled[:, selected], y_checked)
        self.actual_estimator_fits_ = 2
        return self

    def predict(self, X):
        self._authorize()
        check_is_fitted(self, ("imputer_", "scaler_", "selector_", "selected_features_", "regressor_"))
        X_checked = check_array(X, ensure_all_finite="allow-nan")
        X_scaled = self.scaler_.transform(self.imputer_.transform(X_checked))
        return self.regressor_.predict(X_scaled[:, self.selected_features_])


def _ridge_pipeline(alpha: float = 1.0) -> Pipeline:
    return Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median", add_indicator=True)),
            ("scaler", StandardScaler()),
            ("ridge", Ridge(alpha=alpha)),
        ]
    )


class GuardedFeatureAwareEnsemble(_GuardedEstimator):
    method_family_id = "FS4-METHOD-04"
    prospective_fits_per_outer = 15

    def __init__(
        self,
        *,
        common_feature_indices=(),
        structural_feature_indices=(),
        ridge_alpha=1.0,
        inner_splits=4,
        weight_floor=1e-4,
        outer_fold_id="",
        permit: ExecutionPermit | None = None,
    ):
        self.common_feature_indices = common_feature_indices
        self.structural_feature_indices = structural_feature_indices
        self.ridge_alpha = ridge_alpha
        self.inner_splits = inner_splits
        self.weight_floor = weight_floor
        self.outer_fold_id = outer_fold_id
        self.permit = permit

    def _validate_indices(self, width: int) -> tuple[np.ndarray, np.ndarray]:
        common = np.asarray(self.common_feature_indices, dtype=int)
        structural = np.asarray(self.structural_feature_indices, dtype=int)
        if not len(common):
            raise ExecLayerContractError("feature-aware ensemble requires common features")
        if len(np.unique(common)) != len(common) or len(np.unique(structural)) != len(structural):
            raise ExecLayerContractError("feature indices must be unique")
        if set(common).intersection(set(structural)):
            raise ExecLayerContractError("common and structural feature indices overlap")
        if (common < 0).any() or (common >= width).any() or (structural < 0).any() or (structural >= width).any():
            raise ExecLayerContractError("feature index is out of range")
        return common, structural

    def fit(self, X, y, *, groups=None, families=None):
        self._authorize()
        X_checked, y_checked = check_X_y(X, y, ensure_all_finite="allow-nan")
        if groups is None or families is None:
            raise ExecLayerContractError("feature-aware ensemble requires groups and families")
        groups = np.asarray(groups)
        families = np.asarray(families).astype(str)
        if len(groups) != len(y_checked) or len(families) != len(y_checked):
            raise ExecLayerContractError("metadata length mismatch")
        common, structural = self._validate_indices(X_checked.shape[1])
        bcl = np.isin(families, np.asarray(list("BCL")))
        if structural.size and bcl.sum() < 4:
            raise ExecLayerContractError("BCL specialist lacks training rows")
        branches = {"common": (common, np.ones(len(y_checked), dtype=bool))}
        if structural.size:
            branches["full_bcl"] = (np.concatenate([common, structural]), bcl)
            branches["structural_bcl"] = (structural, bcl)
        unique_groups = np.unique(groups)
        splits = min(int(self.inner_splits), len(unique_groups))
        if splits < 2:
            raise ExecLayerContractError("feature-aware ensemble requires at least two groups")
        branch_errors: dict[str, list[float]] = {name: [] for name in branches}
        splitter = GroupKFold(n_splits=splits)
        for train_idx, valid_idx in splitter.split(X_checked, y_checked, groups):
            for name, (indices, availability) in branches.items():
                train_mask = availability[train_idx]
                valid_mask = availability[valid_idx]
                if train_mask.sum() < 2 or valid_mask.sum() == 0:
                    continue
                model = _ridge_pipeline(float(self.ridge_alpha))
                model.fit(X_checked[train_idx][train_mask][:, indices], y_checked[train_idx][train_mask])
                prediction = model.predict(X_checked[valid_idx][valid_mask][:, indices])
                branch_errors[name].append(mean_squared_error(y_checked[valid_idx][valid_mask], prediction))
        raw_weights = {}
        for name, errors in branch_errors.items():
            if errors:
                raw_weights[name] = 1.0 / max(float(np.mean(errors)), float(self.weight_floor))
        if "common" not in raw_weights:
            raise ExecLayerContractError("common branch lacks complete inner-OOF evidence")
        total = sum(raw_weights.values())
        self.branch_weights_ = {name: value / total for name, value in raw_weights.items()}
        self.branch_models_ = {}
        self.branch_indices_ = {}
        for name, (indices, availability) in branches.items():
            if name not in self.branch_weights_:
                continue
            model = _ridge_pipeline(float(self.ridge_alpha))
            model.fit(X_checked[availability][:, indices], y_checked[availability])
            self.branch_models_[name] = model
            self.branch_indices_[name] = indices
        self.actual_estimator_fits_ = sum(len(errors) for errors in branch_errors.values()) + len(self.branch_models_)
        return self

    def predict(self, X, *, families=None):
        self._authorize()
        check_is_fitted(self, ("branch_models_", "branch_weights_", "branch_indices_"))
        X_checked = check_array(X, ensure_all_finite="allow-nan")
        if families is None:
            raise ExecLayerContractError("feature-aware prediction requires families")
        families = np.asarray(families).astype(str)
        if len(families) != len(X_checked):
            raise ExecLayerContractError("families length mismatch")
        result = np.empty(len(X_checked), dtype=float)
        for row_index, family in enumerate(families):
            available = ["common"]
            if family in set("BCL"):
                available.extend(name for name in ("full_bcl", "structural_bcl") if name in self.branch_models_)
            weights = np.asarray([self.branch_weights_[name] for name in available], dtype=float)
            weights /= weights.sum()
            values = [self.branch_models_[name].predict(X_checked[row_index : row_index + 1, self.branch_indices_[name]])[0] for name in available]
            result[row_index] = float(np.dot(weights, values))
        return result
