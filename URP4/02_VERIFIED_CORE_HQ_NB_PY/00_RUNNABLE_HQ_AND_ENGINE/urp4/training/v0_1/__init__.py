"""CINT-08 Training-engine v0.1: static adapters and no-fit policies."""

from .contracts import build_pending_training_manifest
from .models import (
    FeatureBlockSpec,
    FeatureRoute,
    FoldAssignment,
    MethodPluginSpec,
    NotebookAudit,
    TrainingPlan,
    TrainingPolicyError,
    TrainingSourceSpec,
)
from .policy import (
    build_training_plan,
    plan_outer_folds,
    route_features,
    validate_oof_ensemble_inputs,
    validate_selection_records,
    validate_semantic_id,
    validate_split_contract,
)
from .registry import (
    ENSEMBLE_POLICY_VERSION,
    FEATURE_POLICY_VERSION,
    METHOD_REGISTRY_VERSION,
    SOURCE_REGISTRY_VERSION,
    SPLIT_POLICY_VERSION,
    build_feature_block_registry,
    build_method_registry,
    build_source_registry,
    feature_registry_by_id,
    method_registry_by_id,
    source_registry_by_alias,
)
from .source_audit import audit_notebook, audit_sources, definition_inventory

__all__ = [
    "ENSEMBLE_POLICY_VERSION",
    "FEATURE_POLICY_VERSION",
    "METHOD_REGISTRY_VERSION",
    "SOURCE_REGISTRY_VERSION",
    "SPLIT_POLICY_VERSION",
    "FeatureBlockSpec",
    "FeatureRoute",
    "FoldAssignment",
    "MethodPluginSpec",
    "NotebookAudit",
    "TrainingPlan",
    "TrainingPolicyError",
    "TrainingSourceSpec",
    "audit_notebook",
    "audit_sources",
    "definition_inventory",
    "build_feature_block_registry",
    "build_method_registry",
    "build_pending_training_manifest",
    "build_source_registry",
    "build_training_plan",
    "feature_registry_by_id",
    "method_registry_by_id",
    "plan_outer_folds",
    "route_features",
    "source_registry_by_alias",
    "validate_oof_ensemble_inputs",
    "validate_selection_records",
    "validate_semantic_id",
    "validate_split_contract",
]
