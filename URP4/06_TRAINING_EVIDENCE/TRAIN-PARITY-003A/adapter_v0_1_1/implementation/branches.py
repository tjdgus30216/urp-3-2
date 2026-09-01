from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .contracts import BranchRequest, ExecutionPermit
from .instrumentation import EventBuffer, SourceTrace


BRANCH_DEPENDENCIES = {
    "baseline_stability": ("choose_best_model_and_topk", "get_candidate_models_for_output"),
    "stability_lasso_ridge": ("stability_select_features", "inner_group_cv_score", "fit_predict_single_model"),
    "spca_ridge": ("fit_spca_transform", "transform_spca", "inner_group_cv_score"),
    "spca_huber": ("fit_spca_transform", "transform_spca", "inner_group_cv_score"),
    "block_pca_ridge": ("fit_block_pca_transform", "transform_block_pca", "inner_group_cv_score"),
    "bagged_subspace_ridge": ("fit_predict_bagged_ridge", "inner_group_cv_score"),
    "minimal_class_average": ("choose_best_model_and_topk", "fit_predict_single_model"),
    "multitask_screen_ridge": ("multitask_screen_features_for_family", "inner_group_cv_score"),
    "multitask_screen_pls": ("multitask_screen_features_for_family", "inner_group_cv_score"),
    "spca_pls": ("fit_spca_transform", "transform_spca", "inner_group_cv_score"),
}


@dataclass
class SourceExactBranch:
    branch_id: str
    runtime: Any
    events: EventBuffer

    @property
    def source_method_name(self) -> str:
        return self.branch_id

    def describe(self) -> dict[str, Any]:
        lineage = self.runtime.branch_lineage[self.branch_id]
        missing = [name for name in BRANCH_DEPENDENCIES[self.branch_id] if name not in self.runtime.namespace]
        return {
            "branch_id": self.branch_id,
            "adapter_symbol": f"SourceExactBranch[{self.branch_id}]",
            "callable_signature": self.runtime.signature("evaluate_method_train_test"),
            "source_lineage": lineage,
            "dependency_symbols": list(BRANCH_DEPENDENCIES[self.branch_id]),
            "missing_dependencies": missing,
            "parameter_construction": "source_exact_evaluate_method_train_test_dispatch",
            "selection_objective": "source_exact_branch_body_and_helpers",
            "instrumentation": "wrapper_events_plus_future_SourceTrace",
            "output_contract": [
                "selected_feature_identity_order", "transform_identity_parameters", "estimator_identity_parameters",
                "selection_trace", "fallback_none_exception_events", "prediction_ledger_writer_handle",
                "metric_ledger_writer_handle", "final_refit_state",
            ],
            "status": "exact_port_complete_no_fit" if not missing else "blocked_by_missing_dependency",
        }

    def __call__(self, request: BranchRequest, permit: ExecutionPermit, *source_args, **source_kwargs):
        known = set(self.runtime.branch_lineage)
        request.validate(permit, known)
        self.events.emit(
            "branch_enter",
            branch_id=self.branch_id,
            target_id=request.target_id,
            source_hash=permit.source_hash,
            fold_manifest_hash=request.fold_manifest_hash,
            final_refit_state=request.final_refit_state,
        )
        if not permit.fit_allowed or not permit.predict_allowed:
            self.events.emit("permit_denied", branch_id=self.branch_id, mode=permit.mode, reason="NO_FIT")
            raise PermissionError(f"NO_FIT_PERMIT: branch {self.branch_id} numerical entry blocked")
        evaluator = self.runtime.function("evaluate_method_train_test")
        with SourceTrace(self.events, str(self.runtime.notebook_path)):
            result = evaluator(self.branch_id, *source_args, **source_kwargs)
        if result is None:
            self.events.emit("none_return", branch_id=self.branch_id)
        self.events.emit("branch_exit", branch_id=self.branch_id, result_type=type(result).__name__)
        return result


def build_branches(runtime, events: EventBuffer):
    expected = set(BRANCH_DEPENDENCIES)
    actual = set(runtime.branch_lineage)
    if expected != actual:
        raise RuntimeError(f"BRANCH_LINEAGE_MISMATCH: missing={sorted(expected-actual)} extra={sorted(actual-expected)}")
    return {branch_id: SourceExactBranch(branch_id, runtime, events) for branch_id in BRANCH_DEPENDENCIES}
