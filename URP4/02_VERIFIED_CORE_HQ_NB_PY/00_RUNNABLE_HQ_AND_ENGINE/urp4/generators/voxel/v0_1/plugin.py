"""One-request Voxel source-replay plugin."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from urp4.contracts.v0_1.canonical import canonical_json_bytes, sha256_file, sha256_hex
from urp4.contracts.v0_1.models import GenerationRequest, GeometryArtifact

from .contracts import GENERATOR_ID, build_geometry_artifact
from .exporters import export_stl, mesh_qa
from .kernel import generate_voxel_candidate
from .models import ExportAttempt, VoxelCandidate, VoxelGenerationConfig, VoxelGenerationResult, VoxelGeneratorError
from .source_kernel import verify_sources


@dataclass
class GenerationOutcome:
    request: GenerationRequest
    result: VoxelGenerationResult
    mask_path: Path
    mask_sha256: str
    trace_path: Path
    trace_sha256: str
    export_attempts: list[ExportAttempt]
    geometry_artifacts: list[GeometryArtifact]


def package_code_sha256(root: str | Path) -> str:
    root_path = Path(root).resolve()
    rows = [{"path": path.relative_to(root_path).as_posix(), "sha256": sha256_file(path)} for path in sorted((root_path / "urp4/generators/voxel/v0_1").glob("*.py"))]
    return sha256_hex(rows)


class VoxelPlugin:
    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()

    @staticmethod
    def _candidate_from_request(request: GenerationRequest) -> VoxelCandidate:
        data = dict(request.payload["generation_config"])
        model_id = str(data.pop("model_id"))
        mode = str(data.pop("voxel_mode"))
        candidate_fields = {key: data.pop(key) for key in ("min_thickness_vox", "min_hole_size_vox", "max_thickness_vox", "closing_iter", "opening_iter", "anisotropy_z", "num_fourier_terms", "sigma")}
        if isinstance(candidate_fields["num_fourier_terms"], float) and np.isnan(candidate_fields["num_fourier_terms"]):
            candidate_fields["num_fourier_terms"] = None
        if isinstance(candidate_fields["sigma"], float) and np.isnan(candidate_fields["sigma"]):
            candidate_fields["sigma"] = None
        # Source-only duplication in the GenerationRequest is removed before
        # constructing the typed configuration.
        for key in ("seed", "force_connected", "connectivity_repair_mode", "connectivity_bridge_radius_vox", "connectivity_min_component_voxels", "connectivity_max_bridges", "connectivity_retry_after_contact_symmetry", "strict_global_symmetry", "contact_surface_depth_vox", "stl_mesh_size_mm", "lattice_grid_n", "node_blend_factor", "lattice_binary_closing_iters", "lattice_radius_search_iters"):
            data.pop(key, None)
        config = VoxelGenerationConfig(**data)
        return VoxelCandidate(model_id, mode, float(request.payload["target_vf"]), int(request.payload["random_seed"]), config, **candidate_fields)

    def generate(self, request_document: dict[str, object], output_dir: str | Path) -> GenerationOutcome:
        verify_sources(self.root)
        request = GenerationRequest.from_dict(request_document)
        if request.payload["generator_id"] != GENERATOR_ID or request.payload["generator_family"] != "voxel":
            raise VoxelGeneratorError("request is not for CINT-06 Voxel plugin")
        if request.payload["random_seed"] is None or request.payload["target_vf"] is None:
            raise VoxelGeneratorError("Voxel request requires explicit seed and VF")
        formats = list(request.payload["requested_geometry_formats"])
        if any(item != "stl" for item in formats):
            raise VoxelGeneratorError("Voxel v0.1 supports only deterministic STL export")
        candidate = self._candidate_from_request(request)
        result = generate_voxel_candidate(str(self.root), candidate)
        output = Path(output_dir).resolve()
        output.mkdir(parents=True, exist_ok=True)
        mask_path = output / f"{candidate.candidate_id}.mask.npy"
        np.save(mask_path, result.mask, allow_pickle=False)
        trace = {
            "candidate_id": candidate.candidate_id,
            "mode": candidate.voxel_mode,
            "mask_shape": list(result.mask.shape),
            "solid_voxels": int(result.mask.sum()),
            "actual_vf_est": float(result.quick_descriptor["actual_vf_est"]),
            "source_vf_policy": candidate.config.source_vf_policy,
            "global_target_vf": candidate.target_vf,
            "params_target_vf": candidate.to_source_params()["target_vf"],
            "boundary_policy": {"strict_global_symmetry": candidate.config.strict_global_symmetry, "enforce_contact_face_symmetry": candidate.config.enforce_contact_face_symmetry, "contact_surface_depth_vox": candidate.config.contact_surface_depth_vox},
            "quick_descriptor": result.quick_descriptor,
        }
        trace_path = output / f"{candidate.candidate_id}.trace.json"
        trace_path.write_bytes(canonical_json_bytes(trace))
        attempts: list[ExportAttempt] = []
        artifacts: list[GeometryArtifact] = []
        for geometry_format in formats:
            attempt = export_stl(result, output / f"{candidate.candidate_id}.stl")
            qa = mesh_qa(attempt.path)
            relative_path = Path(attempt.path).resolve().relative_to(self.root).as_posix()
            relative_attempt = ExportAttempt(attempt.geometry_format, attempt.status, relative_path, attempt.sha256, attempt.size_bytes, attempt.backend_id, attempt.notes)
            attempts.append(relative_attempt)
            artifacts.append(build_geometry_artifact(request=request, attempt=relative_attempt, qa=qa, observed_vf=float(result.quick_descriptor["actual_vf_est"])))
        return GenerationOutcome(request, result, mask_path, sha256_file(mask_path), trace_path, sha256_file(trace_path), attempts, artifacts)

