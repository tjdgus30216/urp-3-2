from __future__ import annotations

from .models import AdapterContractError, RepresentativeAdapterSpec


DATASET_OBJECT_ID = "DATASET::DATASET-XREG-GM-FS4-V0.1::sha256-33aa35ce6c7f"
ADAPTER_CONTRACT_VERSION = "FS4-P1-ADAPTER-v0.1"
ALLOWED_OUTER_FOLDS = tuple(f"FS4-P1-OUT-{family}" for family in "BCFLT")


ADAPTER_SPECS = (
    RepresentativeAdapterSpec(
        pilot_recipe_id="FS4-P1-A",
        method_family_id="FS4-METHOD-01",
        representative_recipe="weighted_blend_top2",
        source_aliases=("TRAIN-1ST-LEGACY", "TRAIN-1ST-NEWFEATURE"),
        source_components=("WeightedBlendRegressor", "Ridge", "Bayesian_Ridge"),
        compatibility_subset=("Ridge", "Bayesian_Ridge", "top2_score_weighted_blend"),
        target_transforms=("raw", "yeo_johnson"),
        inner_selection_rule="rank base estimators and derive nonnegative blend weights inside inner training/OOF only",
        family_route_policy="one all-family common-feature route; reject family-partial features",
        missingness_policy="median imputation may be fit inside inner train for observed applicable values; never zero-impute not-applicable values",
        conservative_fits_per_outer=10,
        source_faithfulness="source-faithful reduced compatibility subset",
        status="implemented_static_no_fit",
        notes="Two simple source base estimators are used to test adapter compatibility, not to reproduce the full method-1 search.",
    ),
    RepresentativeAdapterSpec(
        pilot_recipe_id="FS4-P1-B",
        method_family_id="FS4-METHOD-02",
        representative_recipe="stability_lasso_ridge",
        source_aliases=("TRAIN-2ND-LEGACY", "TRAIN-2ND-NEWFEATURE"),
        source_components=("stability_select_features", "LassoCV", "Ridge"),
        compatibility_subset=("n_boot=60", "subsample=0.80", "probability>=0.35", "top_keep=6", "Ridge"),
        target_transforms=("raw", "yeo_johnson"),
        inner_selection_rule="stability screen, transform choice and ridge refit inside inner training only",
        family_route_policy="one all-family common-feature route; reject family-partial features",
        missingness_policy="median imputation may be fit inside inner train for observed applicable values; never zero-impute not-applicable values",
        conservative_fits_per_outer=249,
        source_faithfulness="source-faithful parameters with outer leakage-safe wrapper",
        status="implemented_static_no_fit",
        notes="Conservative fit count expands the 60 bootstrap LassoCV screens into their four internal folds.",
    ),
    RepresentativeAdapterSpec(
        pilot_recipe_id="FS4-P1-C",
        method_family_id="FS4-METHOD-03",
        representative_recipe="direct_omp_ridge",
        source_aliases=("TRAIN-3RD-LEGACY", "TRAIN-3RD-NEWFEATURE"),
        source_components=("OMPThenRidge", "OrthogonalMatchingPursuitCV", "Ridge"),
        compatibility_subset=("max_nonzero_grid=2|3|4|6", "ridge_alpha=1.0"),
        target_transforms=("raw", "yeo_johnson"),
        inner_selection_rule="OMP support, support-size and target transform selected inside inner training only",
        family_route_policy="one all-family common-feature route; reject family-partial features",
        missingness_policy="median imputation and scaling fit inside inner train; never zero-impute not-applicable values",
        conservative_fits_per_outer=33,
        source_faithfulness="source-faithful reduced grid with outer leakage-safe wrapper",
        status="implemented_static_no_fit",
        notes="The compatibility grid is bounded to 2, 3, 4 and 6 nonzero coefficients.",
    ),
    RepresentativeAdapterSpec(
        pilot_recipe_id="FS4-P1-D",
        method_family_id="FS4-METHOD-04",
        representative_recipe="featureaware_partial_missing_ensemble",
        source_aliases=("TRAIN-4TH-ENSEMBLE",),
        source_components=("FeatureAwareFittedEnsemble", "common branch", "BCL structural branch", "inner-OOF merger"),
        compatibility_subset=("common_topk=2|3|4|6", "structural_topk=1|2", "Ridge", "raw"),
        target_transforms=("raw",),
        inner_selection_rule="branch and merger weights selected from complete inner-OOF predictions only; outer test sealed",
        family_route_policy="all-family common route plus B/C/L-only specialist; F/T never receive lattice columns or zero surrogates",
        missingness_policy="row-aware branch availability and weight renormalization; never zero-impute family-nonapplicable values",
        conservative_fits_per_outer=15,
        source_faithfulness="source components retained but source outer-score selection replaced by leakage-safe outer wrapper",
        status="implemented_static_no_fit",
        notes="This is intentionally not byte-for-byte source execution because its final choice must be moved inside a new outer wrapper.",
    ),
)


_BY_RECIPE = {item.pilot_recipe_id: item for item in ADAPTER_SPECS}
_BY_METHOD = {item.method_family_id: item for item in ADAPTER_SPECS}


def get_adapter_spec(*, pilot_recipe_id: str | None = None, method_family_id: str | None = None) -> RepresentativeAdapterSpec:
    if bool(pilot_recipe_id) == bool(method_family_id):
        raise AdapterContractError("provide exactly one of pilot_recipe_id or method_family_id")
    if pilot_recipe_id:
        try:
            return _BY_RECIPE[pilot_recipe_id]
        except KeyError as exc:
            raise AdapterContractError(f"unknown pilot recipe: {pilot_recipe_id}") from exc
    try:
        return _BY_METHOD[str(method_family_id)]
    except KeyError as exc:
        raise AdapterContractError(f"unknown method family: {method_family_id}") from exc
