"""URP4-1 HQ v0.2: real execution wrapper around the submitted v0.1 engine.

v0.2 does not change the submitted v0.1 controller.  It adds two explicit,
traceable operating modes: an exploratory image pipeline and frozen-table
replay.  Strict image runs delegate unchanged to v0.1.
"""

from .control import ExecutionControl, HQV02Controller, run_hq_v02, validate_v02

__all__ = ["ExecutionControl", "HQV02Controller", "run_hq_v02", "validate_v02"]
