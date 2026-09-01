"""HQ v0.3 development-only generated-N40 route.

This revision is intentionally separate from the official HQ v0.1 controller
and the status-only HQ v0.2 blueprint.  It admits a hash-locked, already
generated STL into the N40 analysis-copy contract; it does not generate a
model, consume y, train, select features, or replace the official surface.
"""

from .generated_n40_development import (
    GeneratedN40DevelopmentRequest,
    run_generated_n40_development,
    validate_generated_n40_request,
)

__all__ = [
    "GeneratedN40DevelopmentRequest",
    "run_generated_n40_development",
    "validate_generated_n40_request",
]
