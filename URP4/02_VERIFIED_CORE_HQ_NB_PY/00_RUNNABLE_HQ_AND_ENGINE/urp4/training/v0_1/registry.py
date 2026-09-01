"""Immutable source, method, and feature-block registries for CINT-08."""

from __future__ import annotations

from .models import FeatureBlockSpec, MethodPluginSpec, TrainingSourceSpec


SOURCE_REGISTRY_VERSION = "TRAINING-SOURCE-REGISTRY-v0.1"
METHOD_REGISTRY_VERSION = "TRAINING-METHOD-PLUGIN-REGISTRY-v0.1"
FEATURE_POLICY_VERSION = "TRAINING-FEATURE-ROUTER-v0.1"
SPLIT_POLICY_VERSION = "TRAINING-GROUPED-EVALUATION-v0.1"
ENSEMBLE_POLICY_VERSION = "TRAINING-OOF-ENSEMBLE-v0.1"

# Deliverable-local short path.  The workspace source path exceeds the legacy
# Windows MAX_PATH limit for the longest professor filename when nested under
# URP4-1_DELIVERABLE; bytes and registered SHA-256 identities are unchanged.
RAW = "reference_sources/training"

LEGACY_OUTPUTS = ("FH", "FN", "FK", "FU", "GK", "GM", "GN", "GO", "GP", "GR", "GT", "GV")
NEW_OUTPUTS = ("FW", "FX", "FZ", "GA", "GC", "GG", "GJ", "GZ", "HA", "HB", "HC", "HD", "HE", "HG", "HI", "HK")


def build_source_registry() -> tuple[TrainingSourceSpec, ...]:
    rows = (
        TrainingSourceSpec("TRAIN-1ST-LEGACY", f"{RAW}/Training_260418-1st method.ipynb", "2d4e6b256c37bf8309bbeeb2869f6a5c2935216aab4b959d09c8b55802103402", "method_family_1", "baseline_method_reference", "legacy_K_FF_to_FG_GW", "medium", "general", 11, 10, 1, 42, 1, LEGACY_OUTPUTS, notes="Method number is not an ordinal quality rank."),
        TrainingSourceSpec("TRAIN-1ST-NEWFEATURE", f"{RAW}/Training_260418-1st method - New feature.ipynb", "7f75fa05e34fb8aafb39362f6b39aa7d3d924efe7d6af5f3bc0b42debc393cb6", "method_family_1", "new_feature_method_reference", "new_I_FU_to_FV_HL", "medium", "lattice_feature_layout", 11, 10, 1, 42, 1, NEW_OUTPUTS),
        TrainingSourceSpec("TRAIN-2ND-LEGACY", f"{RAW}/Training_260419-2nd method.ipynb", "7514863928df8e71833f97d0bedb905d7d0654f20cbff8c4f42ee371c182fd39", "method_family_2", "stability_method_reference", "legacy_K_FF_to_FG_GW", "medium", "general", 12, 11, 1, 58, 1, LEGACY_OUTPUTS),
        TrainingSourceSpec("TRAIN-2ND-NEWFEATURE", f"{RAW}/Training_260419-2nd method - New feature - Good. vibration.ipynb", "11129a41bd4303d82c599148cd761adb3c858f58da017586e07fb0f06d055ff2", "method_family_2", "new_feature_method_reference", "new_I_FU_to_FV_HL", "medium", "vibration_hint_not_proof", 12, 11, 1, 58, 1, NEW_OUTPUTS, notes="Good/vibration in filename is a source hint, not canonical superiority."),
        TrainingSourceSpec("TRAIN-3RD-LEGACY", f"{RAW}/Training_260420-3rd method.ipynb", "e265a21f1f836c2d81cfe8c4cf7063c3c2aa4e5f52e40a859f31a217f7aca3bd", "method_family_3", "direct_residual_method_reference", "legacy_K_FF_to_FG_GW", "medium", "general", 17, 15, 2, 86, 3, LEGACY_OUTPUTS),
        TrainingSourceSpec("TRAIN-3RD-NEWFEATURE", f"{RAW}/Training_260420-3rd method - New feature - Good. h.ipynb", "09cf2d4213d689cfe272314c41d4b0fd0b9b5a10c4d1b0fe6e44ffe192ec037c", "method_family_3", "new_feature_method_reference", "new_I_FU_to_FV_HL", "medium", "heat_hint_not_proof", 17, 15, 2, 86, 3, NEW_OUTPUTS, notes="Good/heat in filename is a source hint, not canonical superiority."),
        TrainingSourceSpec("TRAIN-4TH-ENSEMBLE", f"{RAW}/Training_260503_Ensemble-4th method.ipynb", "d9f6548c8a239fe213732a78ed4e3da8e0843ccb4f98a4fd996f2cc579af8100", "method_family_4_ensemble", "partial_branch_ensemble_reference", "new_I_FU_to_FV_HL", "high", "family_partial_branch", 14, 13, 1, 107, 6, NEW_OUTPUTS, notes="Ensemble cannot repair invalid splits or unavailable features."),
        TrainingSourceSpec("TRAIN-5TH-ALLTOGETHER", f"{RAW}/Training_260508_Alltogether-5th method.ipynb", "5076091043319f042f5fd08b4fd9bdc20c042c81d18a7a9cd794acd99268b792", "method_family_5_alltogether", "all_together_crosswalk_reference", "new_I_FU_to_FV_HL", "high", "output_wise_stage_selection", 15, 13, 2, 126, 6, NEW_OUTPUTS),
        TrainingSourceSpec("TRAIN-5TH-FIXED", f"{RAW}/Training_260508_Alltogether-5th_method_FIXED.ipynb", "238b7092c5532c695a6f2c8edeb6aa0ae26177bd63fa0f4ebd98754091dfae69", "method_family_5_alltogether", "first_implementation_crosswalk_reference", "new_I_FU_to_FV_HL", "highest", "exact_output_wise_selection", 15, 13, 2, 130, 6, NEW_OUTPUTS, notes="FIXED is the first crosswalk reference, not a universal canonical model."),
    )
    if len({row.alias_id for row in rows}) != len(rows):
        raise RuntimeError("duplicate Training source alias")
    if len({row.sha256 for row in rows}) != len(rows):
        raise RuntimeError("duplicate Training source hash")
    return rows


def source_registry_by_alias() -> dict[str, TrainingSourceSpec]:
    return {row.alias_id: row for row in build_source_registry()}


def build_method_registry() -> tuple[MethodPluginSpec, ...]:
    return (
        MethodPluginSpec("TRAIN-METHOD-01", "method_family_1", "Stage-A", "weighted and engineered blend candidates", ("TRAIN-1ST-LEGACY", "TRAIN-1ST-NEWFEATURE"), ("WeightedBlendRegressor", "Ridge", "ElasticNet", "SVR", "engineered_features"), ("legacy_K_FF_to_FG_GW", "new_I_FU_to_FV_HL"), ("legacy_core_only", "added_only_BCL", "all_features_BCL"), False, False, "general", "static_adapter_only_no_fit", "likely", "Candidate per output; not rank 1."),
        MethodPluginSpec("TRAIN-METHOD-02", "method_family_2", "Stage-B", "stability, block compression, bagging and multitask candidates", ("TRAIN-2ND-LEGACY", "TRAIN-2ND-NEWFEATURE"), ("BaggedSubspaceRidge", "Lasso", "ElasticNet", "Ridge", "SVR", "BlockPCA", "multitask"), ("legacy_K_FF_to_FG_GW", "new_I_FU_to_FV_HL"), ("legacy_core_only", "added_only_BCL", "all_features_BCL"), False, False, "vibration source hint on new-feature branch", "static_adapter_only_no_fit", "likely", "Output-specific candidate; filename hint is not proof."),
        MethodPluginSpec("TRAIN-METHOD-03", "method_family_3", "Stage-C", "direct, residual and shallow nonlinear candidates", ("TRAIN-3RD-LEGACY", "TRAIN-3RD-NEWFEATURE"), ("OMPThenRidge", "ResidualExtraTreesRegressor", "RandomForest", "ExtraTrees", "GradientBoosting", "SVR", "KNeighbors", "GaussianProcess"), ("legacy_K_FF_to_FG_GW", "new_I_FU_to_FV_HL"), ("legacy_core_only", "added_only_BCL", "all_features_BCL"), False, False, "heat source hint on new-feature branch", "static_adapter_only_no_fit", "likely", "Output-specific candidate; filename hint is not proof."),
        MethodPluginSpec("TRAIN-METHOD-04", "method_family_4_ensemble", "Stage-D", "feature-aware partial branch and merge/ensemble coordinator", ("TRAIN-4TH-ENSEMBLE",), ("FeatureAwareFittedEnsemble", "ConservativeEngineeredRegressor", "WeightedBlendRegressor", "OOF_merge"), ("new_I_FU_to_FV_HL",), ("legacy_core_only", "added_only_BCL", "all_features_BCL", "family_partial_branch"), True, True, "BCL added-feature specialist plus all-family core branch", "static_adapter_only_no_fit", "likely", "Only outer-OOF base predictions may be merged."),
        MethodPluginSpec("TRAIN-METHOD-05", "method_family_5_alltogether", "Stage-A+B+C+D", "output-wise exact combo and feature-scope selection coordinator", ("TRAIN-5TH-ALLTOGETHER", "TRAIN-5TH-FIXED"), ("output_wise_selection", "exact_combo", "WeightedBlendRegressor", "BaggedSubspaceRidge", "OMPThenRidge", "ResidualExtraTreesRegressor", "FeatureAwareFittedEnsemble"), ("new_I_FU_to_FV_HL",), ("legacy_core_only", "added_only_BCL", "all_features_BCL", "family_partial_branch"), True, True, "general crosswalk reference", "static_adapter_only_no_fit", "likely", "FIXED is not universal; compare method families per output inside grouped evaluation."),
    )


def method_registry_by_id() -> dict[str, MethodPluginSpec]:
    return {row.method_id: row for row in build_method_registry()}


def build_feature_block_registry() -> tuple[FeatureBlockSpec, ...]:
    return (
        FeatureBlockSpec("TRAIN-FEATURE-METADATA", "EXCEL_TRAINING_TOTAL_260503", "A:D", "sample/family metadata", ("B", "C", "L", "F", "T"), "excluded", "record_only", False, "Never a numeric predictor or ID encoding."),
        FeatureBlockSpec("TRAIN-FEATURE-BASE-LATTICE", "EXCEL_TRAINING_TOTAL_260503", "E:H", "base Maxwell/thickness lattice columns", ("B", "C", "L"), "sensitivity", "not_applicable_outside_BCL", True, "Review semantic identity before promotion."),
        FeatureBlockSpec("TRAIN-FEATURE-ADDED-LATTICE", "EXCEL_TRAINING_TOTAL_260503", "I:Y", "new lattice graph features", ("B", "C", "L"), "family_specific", "exclude_for_FT_never_zero_impute", True, "TA-confirmed B/C/L-only feature block."),
        FeatureBlockSpec("TRAIN-FEATURE-LEGACY-DESCRIPTOR-CORE", "EXCEL_TRAINING_TOTAL_260503", "Z:FU", "legacy-compatible descriptor core", ("B", "C", "L", "F", "T"), "primary_candidate", "explicit_descriptor_missingness", True, "Source-scoped semantic feature IDs required; bare Excel letters prohibited."),
        FeatureBlockSpec("TRAIN-OUTPUT-BLOCK", "EXCEL_TRAINING_TOTAL_260503", "FV:HL", "performance targets", ("B", "C", "L", "F", "T"), "target_only", "not_applicable", False, "Must be addressed by semantic target ID plus workbook/sheet/column provenance."),
    )


def feature_registry_by_id() -> dict[str, FeatureBlockSpec]:
    return {row.block_id: row for row in build_feature_block_registry()}
