"""Versioned 21-cell development HQ.

This package is additive.  It does not modify HQ v0.1, the v0.2 controlled
wrapper, or the unrelated v0.2 blueprint models/runtime modules.
"""

from .stage_runtime import HQStageSession, STAGE_DEFINITIONS, freeze_hq_v03

__all__ = ["HQStageSession", "STAGE_DEFINITIONS", "freeze_hq_v03"]
