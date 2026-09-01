"""Contract-safe extraction of the professor-delivered Lattice Type A/B notebook."""

from .contracts import build_type_a_request
from .models import (
    GenerationConfig,
    LatticeGeneratorError,
    LatticeGraph,
    StepBackendUnavailable,
    TypeBInputUnavailable,
)
from .plugin import GenerationOutcome, LatticeTypeABPlugin

__all__ = [
    "GenerationConfig",
    "GenerationOutcome",
    "LatticeGeneratorError",
    "LatticeGraph",
    "LatticeTypeABPlugin",
    "StepBackendUnavailable",
    "TypeBInputUnavailable",
    "build_type_a_request",
]

