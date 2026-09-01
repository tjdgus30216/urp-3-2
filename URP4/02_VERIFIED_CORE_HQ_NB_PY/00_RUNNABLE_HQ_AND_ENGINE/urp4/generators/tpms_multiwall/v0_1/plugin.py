"""One-request TPMS Multiwall source-replay plugin."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from urp4.contracts.v0_1.canonical import canonical_json_bytes, sha256_file, sha256_hex
from urp4.contracts.v0_1.models import GenerationRequest, GeometryArtifact

from .contracts import GENERATOR_ID, SOURCE_PATH, SOURCE_SHA256, build_geometry_artifact
from .exporters import export_stl, mesh_qa
from .masking import generate_tpms_candidate
from .models import (
    ExportAttempt,
    MultiwallCandidate,
    MultiwallGenerationConfig,
    TPMSComponent,
    TPMSGenerationResult,
    TPMSGeneratorError,
)


@dataclass
class GenerationOutcome:
    request: GenerationRequest
    result: TPMSGenerationResult
    mask_path: Path
    mask_sha256: str
    trace_path: Path
    trace_sha256: str
    export_attempts: list[ExportAttempt]
    geometry_artifacts: list[GeometryArtifact]


def package_code_sha256(root: str | Path) -> str:
    root_path = Path(root).resolve()
    package = root_path / "urp4/generators/tpms_multiwall/v0_1"
    rows = [
        {"path": path.relative_to(root_path).as_posix(), "sha256": sha256_file(path)}
        for path in sorted(package.glob("*.py"))
    ]
    return sha256_hex(rows)


class TPMSMultiwallPlugin:
    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()

    def verify_source(self) -> None:
        source = self.root / SOURCE_PATH
        if not source.is_file():
            raise TPMSGeneratorError(f"immutable source notebook missing: {source}")
        observed = sha256_file(source)
        if observed != SOURCE_SHA256:
            raise TPMSGeneratorError(f"source notebook SHA-256 mismatch: {observed}")

    @staticmethod
    def _candidate_from_request(request: GenerationRequest) -> MultiwallCandidate:
        config_data = dict(request.payload["generation_config"])
        model_id = str(config_data.pop("model_id"))
        combo_name = str(config_data.pop("combo_name"))
        components = tuple(TPMSComponent(**dict(item)) for item in config_data.pop("components"))
        config_data["anisotropy_xyz"] = tuple(config_data["anisotropy_xyz"])
        config = MultiwallGenerationConfig(**config_data)
        return MultiwallCandidate(
            candidate_id=model_id,
            combo_name=combo_name,
            target_vf=float(request.payload["target_vf"]),
            random_seed=int(request.payload["random_seed"]),
            components=components,
            config=config,
        )

    def generate(self, request_document: dict[str, object], output_dir: str | Path) -> GenerationOutcome:
        self.verify_source()
        request = GenerationRequest.from_dict(request_document)
        if request.payload["generator_id"] != GENERATOR_ID or request.payload["generator_family"] != "tpms":
            raise TPMSGeneratorError("request is not for the CINT-05 TPMS Multiwall plugin")
        if request.payload["random_seed"] is None or request.payload["target_vf"] is None:
            raise TPMSGeneratorError("TPMS request requires explicit random_seed and target_vf")
        formats = list(request.payload["requested_geometry_formats"])
        if any(item != "stl" for item in formats):
            raise TPMSGeneratorError("TPMS Multiwall v0.1 supports only deterministic STL export")
        candidate = self._candidate_from_request(request)
        output = Path(output_dir).resolve()
        output.mkdir(parents=True, exist_ok=True)
        result = generate_tpms_candidate(candidate)
        mask_path = output / f"{candidate.candidate_id}.mask.npy"
        np.save(mask_path, result.mask, allow_pickle=False)
        trace = {
            "candidate_id": candidate.candidate_id,
            "mask_shape": list(result.mask.shape),
            "solid_voxels": int(result.mask.sum()),
            "actual_vf_est": result.quick_descriptor["actual_vf_est"],
            "connectivity_info": result.connectivity_info,
            "open_cell_pass_report_only": result.open_cell_pass,
            "open_cell_policy": candidate.config.open_cell_policy,
            "thickness_policy": candidate.config.thickness_policy,
            "component_thicknesses_metadata_mm": [component.thickness_mm for component in candidate.components],
        }
        trace_path = output / f"{candidate.candidate_id}.trace.json"
        trace_path.write_bytes(canonical_json_bytes(trace))
        attempts: list[ExportAttempt] = []
        artifacts: list[GeometryArtifact] = []
        for geometry_format in formats:
            attempt = export_stl(result, output / f"{candidate.candidate_id}.stl")
            qa = mesh_qa(attempt.path)
            relative_path = Path(attempt.path).resolve().relative_to(self.root).as_posix()
            relative_attempt = ExportAttempt(
                geometry_format=attempt.geometry_format,
                status=attempt.status,
                path=relative_path,
                sha256=attempt.sha256,
                size_bytes=attempt.size_bytes,
                backend_id=attempt.backend_id,
                notes=attempt.notes,
            )
            attempts.append(relative_attempt)
            artifacts.append(
                build_geometry_artifact(
                    request=request,
                    attempt=relative_attempt,
                    qa=qa,
                    observed_vf=float(result.quick_descriptor["actual_vf_est"]),
                )
            )
        return GenerationOutcome(
            request=request,
            result=result,
            mask_path=mask_path,
            mask_sha256=sha256_file(mask_path),
            trace_path=trace_path,
            trace_sha256=sha256_file(trace_path),
            export_attempts=attempts,
            geometry_artifacts=artifacts,
        )

