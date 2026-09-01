"""Fail-closed implementation of ROUTE-VALID-004.

This controller is deliberately *not* a slicer.  It returns a hash-addressed
development preflight decision and a manifest only.  A later, separately
authorized stage must decide whether to invoke an imported-STL slicer.
"""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .models import ImportRouteRequest, RouteDecision


CONTROLLER_ID = "ROUTE-POLICY-004/NB-INTEGRATE-001/r1"
ROUTE_C_ID = "IMP-STL-ORIENTED-NONZERO-DEVELOPMENT-ROUTE-C"
ROUTE_G_ID = "GEN-STL-NATIVE-CONTROLLED-DEVELOPMENT"
F1_Z400_WARNING = "F1_Z400_UNRESOLVED"
ALLOWED_IMPORTED_CONFIG = {
    "axis": "z",
    "algorithm_revision": "ORIENTED_NONZERO_RAW/IMSTL-004/r1",
    "normalization_mode": "uniform_bbox_to_expected",
    "source_mutation": False,
    "mesh_repair": False,
    "stl_to_step_proxy": False,
}


class RoutePolicyError(ValueError):
    """Explicit failure used for every policy refusal."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise RoutePolicyError(code, message)


def _validated_import_config(raw: dict[str, Any] | None) -> dict[str, Any]:
    _require(isinstance(raw, dict), "CFG-001", "route_config is required")
    config = dict(raw)
    for key, value in ALLOWED_IMPORTED_CONFIG.items():
        _require(config.get(key) == value, "CFG-002", f"route_config[{key!r}] must equal {value!r}")
    forbidden = {"hole_fill", "contour_bridge", "dilation", "repair", "proxy_step"}
    _require(not (forbidden & set(config)), "CFG-003", "repair/heal/proxy configuration is forbidden")
    return config


def decide_route(request: ImportRouteRequest) -> RouteDecision:
    """Apply ROUTE-VALID-004 without any fallback route selection.

    Every accepted decision remains development-only and `execution_enabled`
    is always false.  Downstream code must therefore opt in through a later
    authorized execution contract rather than accidentally slicing here.
    """

    _require(bool(request.model_id.strip()), "REQ-001", "model_id is required")
    _require(bool(request.policy_evidence_sha256.strip()), "REQ-002", "policy evidence hash is required")
    _require(not request.production_requested, "POL-001", "scientific production qualification is closed")

    if request.input_mode == "generated":
        _require(request.source_type == "generated_controlled_stl_topology_clean", "GEN-001", "generated mode requires controlled topology-clean source type")
        _require(request.source_identity_status == "controlled", "GEN-002", "generated mode requires source_identity_status=controlled")
        _require(request.topology_clean is True, "GEN-003", "generated development route requires topology_clean=true")
        config_hash = _canonical_hash({"controller": CONTROLLER_ID, "request": request.to_dict(), "route": ROUTE_G_ID})
        return RouteDecision(
            decision_status="approved_development",
            route_id=ROUTE_G_ID,
            source_sha256="",
            config_sha256=config_hash,
            warning_flags=(),
            execution_enabled=False,
            scientific_production_qualified=False,
            reason="generated native route represented only; execution remains separately gated",
            policy_evidence_sha256=request.policy_evidence_sha256,
        )

    _require(request.input_mode == "imported", "REQ-003", "input_mode must be generated or imported")
    _require(request.source_type == "paired_confirmed", "SRC-001", "only paired_confirmed imported STL is eligible for this development controller")
    _require(request.source_identity_status == "confirmed", "SRC-002", "paired imported STL requires confirmed source identity")
    _require(bool(request.source_path.strip()), "SRC-003", "imported source_path is required")
    _require(bool(request.expected_source_sha256.strip()), "SRC-004", "expected_source_sha256 is required")
    source = Path(request.source_path).expanduser().resolve()
    _require(source.is_file(), "SRC-005", f"source file does not exist: {source}")
    source_sha = sha256_file(source)
    _require(source_sha.lower() == request.expected_source_sha256.lower(), "SRC-006", "source SHA-256 mismatch")
    config = _validated_import_config(request.route_config)
    warning_flags = (F1_Z400_WARNING,) if request.model_id.strip().upper() == "F1" else ()
    config_hash = _canonical_hash({
        "controller": CONTROLLER_ID,
        "route": ROUTE_C_ID,
        "request": request.to_dict(),
        "validated_route_config": config,
        "source_sha256": source_sha,
        "warning_flags": warning_flags,
    })
    return RouteDecision(
        decision_status="approved_development",
        route_id=ROUTE_C_ID,
        source_sha256=source_sha,
        config_sha256=config_hash,
        warning_flags=warning_flags,
        execution_enabled=False,
        scientific_production_qualified=False,
        reason="paired-confirmed Route C preflight only; no slice/descriptor execution authorized",
        policy_evidence_sha256=request.policy_evidence_sha256,
    )


def build_development_manifest(
    request: ImportRouteRequest,
    decision: RouteDecision,
    *,
    command: list[str],
) -> dict[str, Any]:
    """Make immutable provenance explicit without executing geometry work."""

    _require(decision.decision_status == "approved_development", "MAN-001", "cannot manifest a rejected decision")
    return {
        "schema_version": "NB-INTEGRATE-001-MANIFEST/r1",
        "controller_id": CONTROLLER_ID,
        "request": asdict(request),
        "decision": asdict(decision),
        "runtime": {
            "sys_executable": sys.executable,
            "python_version": platform.python_version(),
            "environment_path": sys.prefix,
            "implementation": platform.python_implementation(),
            "command": list(command),
        },
        "execution": {
            "geometry_executed": False,
            "slice_executed": False,
            "descriptor_executed": False,
            "y_accessed": False,
            "model_fit_executed": False,
            "production_claim": False,
        },
    }
