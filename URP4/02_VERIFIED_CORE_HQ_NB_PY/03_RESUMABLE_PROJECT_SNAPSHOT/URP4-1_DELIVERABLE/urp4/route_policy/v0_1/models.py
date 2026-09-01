"""Typed, immutable inputs and outputs for the development-only route gate."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ImportRouteRequest:
    """A preflight request only; it never authorizes geometry execution.

    ``source_type`` is intentionally a policy category rather than a file
    extension.  This prevents a caller from treating any `.stl` as an eligible
    paired imported STL merely because it has the right suffix.
    """

    model_id: str
    input_mode: str  # generated | imported
    source_type: str
    source_identity_status: str
    source_path: str = ""
    expected_source_sha256: str = ""
    topology_clean: bool | None = None
    route_config: dict[str, Any] | None = None
    policy_evidence_sha256: str = ""
    production_requested: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RouteDecision:
    decision_status: str  # approved_development | rejected
    route_id: str
    source_sha256: str
    config_sha256: str
    warning_flags: tuple[str, ...]
    execution_enabled: bool
    scientific_production_qualified: bool
    reason: str
    policy_evidence_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
