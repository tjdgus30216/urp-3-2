"""No-fit FS4 integration contract for the four professor method families."""

from .models import FS4ContractError, FS4IntegrationPlan, MethodFamilyRole
from .policy import build_no_fit_plan, validate_candidate_interface, validate_oof_merge_records
from .registry import BASE_METHOD_FAMILIES, COORDINATOR_REFERENCE

__all__ = [
    "BASE_METHOD_FAMILIES",
    "COORDINATOR_REFERENCE",
    "FS4ContractError",
    "FS4IntegrationPlan",
    "MethodFamilyRole",
    "build_no_fit_plan",
    "validate_candidate_interface",
    "validate_oof_merge_records",
]
