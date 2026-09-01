"""URP4-CONTRACT-v0.1 builders for Voxel source replay."""

from __future__ import annotations

from typing import Iterable

from urp4.contracts.v0_1.canonical import sha256_hex
from urp4.contracts.v0_1.ids import build_document
from urp4.contracts.v0_1.models import GenerationRequest, GeometryArtifact

from .models import ExportAttempt, VoxelCandidate
from .source_kernel import MATCHING_SOURCES, SOURCE_ALIAS, SOURCE_PATH, SOURCE_SHA256


GENERATOR_ID = "GEN-VOXEL-v0.1"


def _contract_safe_params(candidate: VoxelCandidate) -> dict[str, object]:
    params = candidate.to_source_params()
    for key in ("num_fourier_terms", "sigma"):
        value = params.get(key)
        if isinstance(value, float) and value != value:
            params[key] = None
    return params


def _theta(candidate: VoxelCandidate) -> list[dict[str, object]]:
    rows = [
        ("THETA-VOX-MODE", "voxel_mode", candidate.voxel_mode, "category", "discrete"),
        ("THETA-VOX-VF", "target_vf", candidate.target_vf, "fraction", "continuous"),
        ("THETA-VOX-MIN-T", "min_thickness_vox", candidate.min_thickness_vox, "voxel", "discrete"),
        ("THETA-VOX-MIN-H", "min_hole_size_vox", candidate.min_hole_size_vox, "voxel", "discrete"),
        ("THETA-VOX-MAX-T", "max_thickness_vox", candidate.max_thickness_vox, "voxel", "discrete"),
        ("THETA-VOX-CLOSE", "closing_iter", candidate.closing_iter, "iteration", "discrete"),
        ("THETA-VOX-OPEN", "opening_iter", candidate.opening_iter, "iteration", "discrete"),
        ("THETA-VOX-AZ", "anisotropy_z", candidate.anisotropy_z, "ratio", "continuous"),
    ]
    if candidate.num_fourier_terms is not None:
        rows.append(("THETA-VOX-FOURIER", "num_fourier_terms", candidate.num_fourier_terms, "count", "discrete"))
    if candidate.sigma is not None:
        rows.append(("THETA-VOX-SIGMA", "sigma", candidate.sigma, "voxel", "continuous"))
    return [{"parameter_id": pid, "raw_parameter_name": name, "normalized_name": name, "value": value, "unit": unit, "value_type": kind, "applicable_family": [candidate.voxel_mode]} for pid, name, value, unit, kind in rows]


def build_voxel_request(*, candidate: VoxelCandidate, requested_formats: Iterable[str], code_sha256: str) -> GenerationRequest:
    formats = list(dict.fromkeys(requested_formats))
    safe_params = _contract_safe_params(candidate)
    identity = {"candidate": safe_params, "config": candidate.config.to_identity_dict(), "requested_formats": formats}
    source_rows = [{"source_alias": SOURCE_ALIAS, "path": SOURCE_PATH, "sha256": SOURCE_SHA256, "role": "approved_immutable_notebook_source"}]
    source_rows.extend({"source_alias": alias, "path": path, "sha256": digest, "role": "matching_core_source"} for alias, path, digest in MATCHING_SOURCES)
    payload = {
        "generator_id": GENERATOR_ID,
        "generator_version": "0.1",
        "generator_family": "voxel",
        "theta_schema_id": "THETA-VOXEL-v0.1",
        "theta_values": _theta(candidate),
        "generation_config": {"model_id": candidate.candidate_id, "voxel_mode": candidate.voxel_mode, **candidate.config.to_identity_dict(), **{k: v for k, v in safe_params.items() if k not in {"generator_type", "voxel_mode", "size_mm", "target_vf", "grid_n", "candidate_id"}}},
        "physical_size_mm": {axis: candidate.config.size_mm for axis in ("x", "y", "z")},
        "target_vf": candidate.target_vf,
        "random_seed": candidate.random_seed,
        "requested_geometry_formats": formats,
        "base_geometry_id": f"BASEGEOM::{candidate.candidate_id}",
        "legacy_ids": [SOURCE_ALIAS],
        "notes": "CINT-06 fixed-mask source replay. Production grid/VF/boundary policy is not approved.",
    }
    provenance = {
        "producer": "CINT-06-voxel-plugin",
        "runtime_alias": "KMK312",
        "code_identity": {"id": "URP4-VOXEL-v0.1", "sha256": code_sha256},
        "config_identity": {"id": "CINT-06-VOXEL-FIXTURE-v0.1", "sha256": sha256_hex(identity)},
        "source_aliases": [SOURCE_ALIAS, *[item[0] for item in MATCHING_SOURCES]],
        "source_artifacts": source_rows,
        "parent_object_ids": [],
        "notes": "Definition-only replay; no notebook top-level execution.",
    }
    return GenerationRequest.from_dict(build_document("GenerationRequest", payload, provenance, execution_status="passed", scientific_status="likely"))


def build_geometry_artifact(*, request: GenerationRequest, attempt: ExportAttempt, qa: dict[str, object], observed_vf: float) -> GeometryArtifact:
    if attempt.status != "passed" or not attempt.path or not attempt.sha256 or attempt.size_bytes is None:
        raise ValueError("only passed exports can become GeometryArtifact")
    payload = {
        "model_id": request.payload["generation_config"]["model_id"],
        "base_geometry_id": request.payload["base_geometry_id"],
        "model_family": "Voxel",
        "geometry_role": "generated",
        "geometry_format": attempt.geometry_format,
        "path": attempt.path,
        "geometry_sha256": attempt.sha256,
        "size_bytes": attempt.size_bytes,
        "units": "mm",
        "physical_size_mm": {axis: float(qa[f"bbox_{axis}_mm"]) for axis in ("x", "y", "z")},
        "generation_request_id": request.object_id,
        "parent_geometry_artifact_id": None,
        "observed_vf": observed_vf,
        "qa": {key: qa[key] for key in ("technical_status", "topology_status", "connected_region_count", "boundary_edge_count", "nonmanifold_edge_count")},
        "legacy_ids": [SOURCE_ALIAS],
        "notes": "Source-exact selected-function replay; printability and production fidelity are not claimed.",
    }
    provenance = {
        "producer": "CINT-06-voxel-plugin",
        "runtime_alias": "KMK312",
        "code_identity": request.document["provenance"]["code_identity"],
        "config_identity": request.document["provenance"]["config_identity"],
        "source_aliases": [SOURCE_ALIAS],
        "source_artifacts": [{"source_alias": SOURCE_ALIAS, "path": SOURCE_PATH, "sha256": SOURCE_SHA256, "role": "approved_immutable_notebook_source"}, {"source_alias": f"CINT06::{request.payload['generation_config']['model_id']}::stl", "path": attempt.path, "sha256": attempt.sha256, "role": "generated_geometry"}],
        "parent_object_ids": [request.object_id],
        "notes": f"Export backend {attempt.backend_id}",
    }
    return GeometryArtifact.from_dict(build_document("GeometryArtifact", payload, provenance, execution_status="passed", scientific_status="likely"))
