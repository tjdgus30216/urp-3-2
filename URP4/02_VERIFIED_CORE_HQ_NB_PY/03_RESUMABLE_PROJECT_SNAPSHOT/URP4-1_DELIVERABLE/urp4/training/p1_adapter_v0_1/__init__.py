"""No-fit compatibility adapters for the frozen FS4-P1 representatives.

This package deliberately contains no estimator ``fit`` or ``predict`` path.
It compiles and validates execution plans only.  A later, separately hashed
authorization must provide the executable estimator layer.
"""

from .adapters import compile_adapter_plan, deny_execution
from .models import AdapterContractError, AdapterPlan, RepresentativeAdapterSpec
from .registry import ADAPTER_SPECS, DATASET_OBJECT_ID, get_adapter_spec

__all__ = [
    "ADAPTER_SPECS",
    "DATASET_OBJECT_ID",
    "AdapterContractError",
    "AdapterPlan",
    "RepresentativeAdapterSpec",
    "compile_adapter_plan",
    "deny_execution",
    "get_adapter_spec",
]
