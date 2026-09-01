"""Hash-locked generated STL → N40 analysis derivative → RUN-139 development route.

This module deliberately has a narrow surface.  It takes an existing,
controlled generated STL rather than invoking a generator.  That keeps the
source geometry identity, the N40 derivative and descriptor artifacts
separately auditable during development.
"""

from __future__ import annotations

import json
import platform
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from urp4.contracts.v0_1.canonical import sha256_file, sha256_hex, validate_sha256
from urp4.descriptor_service.v0_1 import Run139DescriptorService, Run139ExtractionPipeline
from urp4.geometry_io.v0_3.source_preflight import GeometrySourceRecord, inspect_source
from urp4.geometry_io.v0_5 import GeneratedNormalizationConfig, normalize_generated_stl


DEVELOPMENT_ROUTE_ID = "HQ-V0.3-GEN-N40-DEVELOPMENT"
DEVELOPMENT_REVISION = "HQ-GEOM-002/v0.3/r1"


@dataclass(frozen=True)
class GeneratedN40DevelopmentRequest:
    model_id: str
    source_geometry_path: str
    expected_source_sha256: str
    output_root: str
    geometry_revision: str = "controlled_generated_source"
    target_size_mm: float = 40.0
    route_id: str = DEVELOPMENT_ROUTE_ID
    execute_descriptor: bool = True
    image_policy: str = "STREAMING_TEMP_PNG"


def _assert_kmk312() -> None:
    executable = str(Path(sys.executable).resolve()).lower()
    if "kmk312" not in executable or sys.version_info[:2] != (3, 12):
        raise RuntimeError(f"HQ v0.3 development route requires KMK312/Python 3.12, observed {sys.executable} / {platform.python_version()}")


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")


def validate_generated_n40_request(request: GeneratedN40DevelopmentRequest) -> dict[str, Any]:
    """Fail closed before any geometry write or descriptor calculation."""

    _assert_kmk312()
    if not request.model_id.strip():
        raise ValueError("model_id cannot be empty")
    if request.route_id != DEVELOPMENT_ROUTE_ID:
        raise ValueError("unsupported development route ID")
    if abs(float(request.target_size_mm) - 40.0) > 1.0e-12:
        raise ValueError("target_size_mm is frozen at 40.0 for the analysis contract")
    if request.image_policy != "STREAMING_TEMP_PNG":
        raise ValueError("development route only admits streaming PNG readback")
    validate_sha256(request.expected_source_sha256)
    source = Path(request.source_geometry_path).resolve()
    if source.suffix.lower() != ".stl" or not source.is_file():
        raise FileNotFoundError(f"controlled generated STL missing: {source}")
    observed_hash = sha256_file(source)
    if observed_hash != request.expected_source_sha256:
        raise ValueError(f"controlled source SHA-256 mismatch: {source}")
    output_root = Path(request.output_root).resolve()
    identity = {
        "development_revision": DEVELOPMENT_REVISION,
        "request": asdict(request),
        "source_sha256": observed_hash,
        "runtime": "KMK312 Python 3.12",
        "no_y_training_selection_inverse": True,
    }
    return {
        "request": asdict(request),
        "source": str(source),
        "source_sha256": observed_hash,
        "output_root": str(output_root),
        "config_sha256": sha256_hex(identity),
        "identity": identity,
    }


def run_generated_n40_development(request: GeneratedN40DevelopmentRequest) -> dict[str, Any]:
    """Run the narrow development route; repeated identical requests resume safely."""

    frozen = validate_generated_n40_request(request)
    run_id = f"HQG3-{frozen['config_sha256'][:12]}"
    run_dir = Path(frozen["output_root"]) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    frozen_path = run_dir / "frozen_request.json"
    if frozen_path.exists():
        observed = json.loads(frozen_path.read_text(encoding="utf-8"))
        if observed.get("config_sha256") != frozen["config_sha256"]:
            raise FileExistsError(f"run ID collision with non-identical request: {run_dir}")
    else:
        _write_json(frozen_path, {**frozen, "run_id": run_id, "route_status": "development_only_not_hq_v0_1"})

    source = Path(frozen["source"])
    source_preflight = inspect_source(GeometrySourceRecord.from_values(
        model_id=request.model_id,
        pair_id=request.model_id,
        source_type="generated_stl",
        path=source,
        geometry_revision=request.geometry_revision,
        expected_route_id="GEN-STL-NATIVE-CONTROLLED",
    ))
    if not bool(source_preflight.get("topology_clean")):
        raise RuntimeError(
            "HQ v0.3 generated-N40 route admits only topology-clean generated STL. "
            "Lattice/TPMS non-clean sources require a separately registered topology contract."
        )
    derivative = run_dir / "geometry" / f"{request.model_id}__N40_ANALYSIS_DERIVATIVE.stl"
    normalization = normalize_generated_stl(
        source, derivative,
        config=GeneratedNormalizationConfig(target_size_mm=request.target_size_mm),
        expected_source_sha256=request.expected_source_sha256,
    )
    derivative_preflight = inspect_source(GeometrySourceRecord.from_values(
        model_id=request.model_id,
        pair_id=request.model_id,
        source_type="generated_stl",
        path=derivative,
        geometry_revision=f"{DEVELOPMENT_REVISION}:n40_derivative",
        expected_route_id="GEN-STL-NATIVE-CONTROLLED",
    ))
    _write_json(run_dir / "source_preflight.json", source_preflight)
    _write_json(run_dir / "derivative_preflight.json", derivative_preflight)
    _write_json(run_dir / "normalization_manifest.json", normalization)

    status: dict[str, Any] = {
        "run_id": run_id,
        "route_id": DEVELOPMENT_ROUTE_ID,
        "route_status": "development_only_not_hq_v0_1",
        "model_id": request.model_id,
        "source_sha256": request.expected_source_sha256,
        "derivative_sha256": normalization["derivative_sha256"],
        "source_preflight": source_preflight,
        "derivative_preflight": derivative_preflight,
        "normalization": normalization,
        "descriptor": None,
        "prohibitions": ["y", "feature_selection", "training", "prediction", "inverse_design", "all58"],
    }
    if request.execute_descriptor:
        descriptor_root = run_dir / "descriptor"
        scalar_path = run_dir / "descriptor_result.csv"
        if (descriptor_root / "qa.json").is_file() and scalar_path.is_file():
            qa = json.loads((descriptor_root / "qa.json").read_text(encoding="utf-8"))
            scalar_frame = pd.read_csv(scalar_path)
            execution = "resumed"
        else:
            extraction = Run139ExtractionPipeline().extract(
                model_id=request.model_id,
                geometry_path=derivative,
                output_dir=descriptor_root,
                mode="STREAMING",
                expected_geometry_sha256=str(normalization["derivative_sha256"]),
                overwrite=False,
            )
            qa = extraction.qa
            scalar_frame = pd.DataFrame([row.to_row() for row in Run139DescriptorService().compute(extraction.tables)])
            scalar_frame.to_csv(scalar_path, index=False, encoding="utf-8-sig")
            execution = "executed"
        status["descriptor"] = {
            "status": qa.get("status"), "execution": execution,
            "slice_rows": qa.get("slice_rows"), "overlay_rows": qa.get("overlay_rows"),
            "readback_mismatch_sum": qa.get("readback_mismatch_sum"),
            "remaining_png": qa.get("remaining_png"), "scalar_rows": len(scalar_frame),
            "descriptor_root": str(descriptor_root), "descriptor_result_csv": str(scalar_path),
        }
    status["status"] = "passed" if (
        not request.execute_descriptor or (
            status["descriptor"]["status"] == "passed" and status["descriptor"]["slice_rows"] == 801
            and status["descriptor"]["overlay_rows"] == 800 and status["descriptor"]["readback_mismatch_sum"] == 0
            and status["descriptor"]["remaining_png"] == 0 and status["descriptor"]["scalar_rows"] == 9
        )
    ) else "failed"
    _write_json(run_dir / "run_status.json", status)
    if status["status"] != "passed":
        raise RuntimeError(f"development route failed: {run_dir}")
    return status
