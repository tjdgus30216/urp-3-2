"""URP4-CONTRACT-v0.1 builders for the TPMS Multiwall plugin."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from urp4.contracts.v0_1.canonical import sha256_hex
from urp4.contracts.v0_1.ids import build_document
from urp4.contracts.v0_1.models import GenerationRequest, GeometryArtifact

from .models import ExportAttempt, MultiwallCandidate


SOURCE_ALIAS = "GEN-TPMS-MULTIWALL-VF50-20260716"
SOURCE_PATH = "experiments/lab_001_xy_connection_20260626/data/raw/professor_generators_20260716/Multiwall_model_generator_VF50.ipynb"
SOURCE_SHA256 = "46dcac9467dcb9904eb0d41ebb6639a8cb304d47e46b6c5d478e74df4f497923"
GENERATOR_ID = "GEN-TPMS-MULTIWALL-v0.1"


def _theta(candidate: MultiwallCandidate) -> list[dict[str, object]]:
    values: list[tuple[str, str, object, str, str]] = [
        ("THETA-TPMS-TYPE", "tpms_type", candidate.components[0].tpms_type, "category", "discrete"),
        ("THETA-TPMS-COMBO", "multiwall_combo", candidate.combo_name, "category", "discrete"),
        ("THETA-TPMS-VF", "target_vf", candidate.target_vf, "fraction", "continuous"),
        ("THETA-TPMS-FREQ", "frequency", candidate.config.frequency, "cycles_per_domain", "continuous"),
        ("THETA-TPMS-AX", "anisotropy_x", candidate.config.anisotropy_xyz[0], "ratio", "continuous"),
        ("THETA-TPMS-AY", "anisotropy_y", candidate.config.anisotropy_xyz[1], "ratio", "continuous"),
        ("THETA-TPMS-AZ", "anisotropy_z", candidate.config.anisotropy_xyz[2], "ratio", "continuous"),
        ("THETA-TPMS-NOISE", "noise_amp", candidate.config.noise_amp, "normalized_field", "continuous"),
        ("THETA-TPMS-GAP", "component_gap_mm", candidate.config.component_gap_mm, "mm", "continuous"),
        ("THETA-TPMS-HOLE", "min_hole_size_vox", candidate.config.min_hole_size_vox, "voxel", "discrete"),
    ]
    for index, component in enumerate(candidate.components):
        values.append((f"THETA-TPMS-LS-{index}", f"component_{index}_level_shift", component.level_shift, "normalized_field", "continuous"))
        values.append((f"THETA-TPMS-TMETA-{index}", f"component_{index}_thickness_metadata", component.thickness_mm, "mm", "continuous"))
    return [
        {
            "parameter_id": parameter_id,
            "raw_parameter_name": name,
            "normalized_name": name,
            "value": value,
            "unit": unit,
            "value_type": value_type,
            "applicable_family": ["tpms_multiwall"],
        }
        for parameter_id, name, value, unit, value_type in values
    ]


def build_multiwall_request(
    *, candidate: MultiwallCandidate, requested_formats: Iterable[str], code_sha256: str
) -> GenerationRequest:
    formats = list(dict.fromkeys(requested_formats))
    config_identity = {
        "candidate": candidate.to_source_params(),
        "config_policy": candidate.config.to_identity_dict(),
        "requested_formats": formats,
    }
    config_hash = sha256_hex(config_identity)
    payload = {
        "generator_id": GENERATOR_ID,
        "generator_version": "0.1",
        "generator_family": "tpms",
        "theta_schema_id": "THETA-TPMS-MULTIWALL-v0.1",
        "theta_values": _theta(candidate),
        "generation_config": {
            "model_id": candidate.candidate_id,
            "combo_name": candidate.combo_name,
            "components": [component.to_dict() for component in candidate.components],
            **candidate.config.to_identity_dict(),
        },
        "physical_size_mm": {axis: candidate.config.size_mm for axis in ("x", "y", "z")},
        "target_vf": candidate.target_vf,
        "random_seed": candidate.random_seed,
        "requested_geometry_formats": formats,
        "base_geometry_id": f"BASEGEOM::{candidate.candidate_id}",
        "legacy_ids": [SOURCE_ALIAS],
        "notes": (
            "CINT-05 source-replay fixture only. VF=0.50 or sampled 0.45-0.55 is not a production-policy approval; "
            "component thickness remains source metadata and open-cell is report-only."
        ),
    }
    provenance = {
        "producer": "CINT-05-tpms-multiwall-plugin",
        "runtime_alias": "KMK312",
        "code_identity": {"id": "URP4-TPMS-MULTIWALL-v0.1", "sha256": code_sha256},
        "config_identity": {"id": "CINT-05-TPMS-SOURCE-REPLAY-FIXTURE-v0.1", "sha256": config_hash},
        "source_aliases": [SOURCE_ALIAS],
        "source_artifacts": [
            {"source_alias": SOURCE_ALIAS, "path": SOURCE_PATH, "sha256": SOURCE_SHA256, "role": "immutable_notebook_source"}
        ],
        "parent_object_ids": [],
        "notes": "Selected function definitions are replayed without notebook top-level execution or Colab mount.",
    }
    return GenerationRequest.from_dict(
        build_document("GenerationRequest", payload, provenance, execution_status="passed", scientific_status="likely")
    )


def build_geometry_artifact(
    *, request: GenerationRequest, attempt: ExportAttempt, qa: dict[str, object], observed_vf: float
) -> GeometryArtifact:
    if attempt.status != "passed" or not attempt.path or not attempt.sha256 or attempt.size_bytes is None:
        raise ValueError("only a passed export can become a GeometryArtifact")
    payload = {
        "model_id": request.payload["generation_config"]["model_id"],
        "base_geometry_id": request.payload["base_geometry_id"],
        "model_family": "TPMS Multiwall",
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
        "notes": "Marching-cubes STL from source-equivalent repaired voxel mask; printability beyond mesh closure is not claimed.",
    }
    provenance = {
        "producer": "CINT-05-tpms-multiwall-plugin",
        "runtime_alias": "KMK312",
        "code_identity": request.document["provenance"]["code_identity"],
        "config_identity": request.document["provenance"]["config_identity"],
        "source_aliases": [SOURCE_ALIAS],
        "source_artifacts": [
            {"source_alias": SOURCE_ALIAS, "path": SOURCE_PATH, "sha256": SOURCE_SHA256, "role": "immutable_notebook_source"},
            {"source_alias": f"CINT05::{request.payload['generation_config']['model_id']}::stl", "path": attempt.path, "sha256": attempt.sha256, "role": "generated_geometry"},
        ],
        "parent_object_ids": [request.object_id],
        "notes": f"Export backend {attempt.backend_id}",
    }
    return GeometryArtifact.from_dict(
        build_document("GeometryArtifact", payload, provenance, execution_status="passed", scientific_status="likely")
    )

