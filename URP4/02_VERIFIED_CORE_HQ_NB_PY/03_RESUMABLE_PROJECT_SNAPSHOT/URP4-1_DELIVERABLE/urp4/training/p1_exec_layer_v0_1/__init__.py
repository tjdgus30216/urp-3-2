"""Guarded executable estimator layer for the FS4-P1 representatives.

Estimator graphs are constructible, cloneable and inspectable.  Every real
``fit`` or ``predict`` call requires a separately hashed AUTH2 permit.  This
package does not ship such a permit and therefore cannot authorize itself.
"""

from .builders import build_representative_estimator, build_representative_graph
from .estimators import (
    GuardedFeatureAwareEnsemble,
    GuardedOMPThenRidge,
    GuardedStabilityLassoRidge,
    GuardedWeightedBlendRegressor,
)
from .ledger import prospective_fit_ledger, prospective_fit_summary
from .models import ExecLayerContractError, ExecutionGraph, ExecutionPermit
from .permit import load_execution_permit

__all__ = [
    "ExecLayerContractError",
    "ExecutionGraph",
    "ExecutionPermit",
    "GuardedFeatureAwareEnsemble",
    "GuardedOMPThenRidge",
    "GuardedStabilityLassoRidge",
    "GuardedWeightedBlendRegressor",
    "build_representative_estimator",
    "build_representative_graph",
    "load_execution_permit",
    "prospective_fit_ledger",
    "prospective_fit_summary",
]
