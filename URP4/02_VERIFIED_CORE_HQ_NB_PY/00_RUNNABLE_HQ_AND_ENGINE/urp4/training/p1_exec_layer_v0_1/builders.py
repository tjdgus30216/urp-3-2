from __future__ import annotations

from sklearn.impute import SimpleImputer
from sklearn.linear_model import BayesianRidge, Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from urp4.training.p1_adapter_v0_1 import get_adapter_spec

from .estimators import (
    GuardedFeatureAwareEnsemble,
    GuardedOMPThenRidge,
    GuardedStabilityLassoRidge,
    GuardedWeightedBlendRegressor,
)
from .models import ExecLayerContractError, ExecutionGraph, ExecutionPermit
from .permit import EXEC_LAYER_VERSION, OUTER_FOLDS


def _base_pipeline(model):
    return Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("model", model),
        ]
    )


def _validate_outer(outer_fold_id: str) -> None:
    if outer_fold_id not in OUTER_FOLDS:
        raise ExecLayerContractError("outer fold is not frozen by PRM-063")


def build_representative_estimator(
    pilot_recipe_id: str,
    *,
    outer_fold_id: str,
    common_feature_indices=(),
    structural_feature_indices=(),
    permit: ExecutionPermit | None = None,
):
    _validate_outer(outer_fold_id)
    spec = get_adapter_spec(pilot_recipe_id=pilot_recipe_id)
    if pilot_recipe_id == "FS4-P1-A":
        return GuardedWeightedBlendRegressor(
            estimators=(
                _base_pipeline(Ridge(alpha=1.0)),
                _base_pipeline(BayesianRidge()),
            ),
            weights=(0.5, 0.5),
            outer_fold_id=outer_fold_id,
            permit=permit,
        )
    if pilot_recipe_id == "FS4-P1-B":
        return GuardedStabilityLassoRidge(outer_fold_id=outer_fold_id, permit=permit)
    if pilot_recipe_id == "FS4-P1-C":
        return GuardedOMPThenRidge(max_nonzero_coefs=6, ridge_alpha=1.0, outer_fold_id=outer_fold_id, permit=permit)
    if pilot_recipe_id == "FS4-P1-D":
        common = tuple(int(index) for index in common_feature_indices)
        structural = tuple(int(index) for index in structural_feature_indices)
        if not common:
            raise ExecLayerContractError("method D requires at least one common feature index")
        if len(common) != len(set(common)) or len(structural) != len(set(structural)):
            raise ExecLayerContractError("feature indices must be unique")
        if set(common).intersection(structural):
            raise ExecLayerContractError("common and structural feature indices overlap")
        if any(index < 0 for index in common + structural):
            raise ExecLayerContractError("feature indices must be nonnegative")
        return GuardedFeatureAwareEnsemble(
            common_feature_indices=common,
            structural_feature_indices=structural,
            outer_fold_id=outer_fold_id,
            permit=permit,
        )
    raise ExecLayerContractError(f"no executable constructor for {spec.pilot_recipe_id}")


def build_representative_graph(
    pilot_recipe_id: str,
    *,
    outer_fold_id: str,
    common_feature_indices=(),
    structural_feature_indices=(),
) -> ExecutionGraph:
    estimator = build_representative_estimator(
        pilot_recipe_id,
        outer_fold_id=outer_fold_id,
        common_feature_indices=common_feature_indices,
        structural_feature_indices=structural_feature_indices,
        permit=None,
    )
    spec = get_adapter_spec(pilot_recipe_id=pilot_recipe_id)
    metadata = ("groups",) if pilot_recipe_id == "FS4-P1-B" else (("groups", "families") if pilot_recipe_id == "FS4-P1-D" else ())
    prediction_metadata = ("families",) if pilot_recipe_id == "FS4-P1-D" else ()
    return ExecutionGraph(
        executable_layer_version=EXEC_LAYER_VERSION,
        pilot_recipe_id=pilot_recipe_id,
        method_family_id=spec.method_family_id,
        representative_recipe=spec.representative_recipe,
        estimator_class=type(estimator).__name__,
        estimator_components=spec.source_components,
        preprocessing_components=("median_imputer", "standard_scaler", "source_mapped_regressor"),
        required_fit_metadata=tuple(metadata),
        prediction_metadata=tuple(prediction_metadata),
        common_feature_indices=tuple(common_feature_indices),
        structural_feature_indices=tuple(structural_feature_indices),
        prospective_fits_per_outer=spec.conservative_fits_per_outer,
        permit_required=True,
        fit_called=0,
        prediction_called=0,
        status="constructed_no_fit_AUTH2_required",
        notes="Executable graph only. The package contains no permit and cannot authorize itself.",
    )
