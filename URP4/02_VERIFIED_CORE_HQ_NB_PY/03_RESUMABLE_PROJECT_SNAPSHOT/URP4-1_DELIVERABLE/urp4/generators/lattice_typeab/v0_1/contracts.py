"""URP4-CONTRACT-v0.1 builders for the Lattice Type-A generator."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from urp4.contracts.v0_1.canonical import sha256_file, sha256_hex
from urp4.contracts.v0_1.ids import build_document
from urp4.contracts.v0_1.models import GenerationRequest, GeometryArtifact

from .models import ExportAttempt, GenerationConfig


SOURCE_ALIAS = "GEN-LATTICE-TYPEAB-20260716"
SOURCE_PATH = "experiments/lab_001_xy_connection_20260626/data/raw/professor_generators_20260716/Type A+B Gen. Image slicing.ipynb"
SOURCE_SHA256 = "1ef01006d93be95e56525c91bd0943405ee6cd54e2347413699472fe7c6d24f7"
GENERATOR_ID = "GEN-LATTICE-TYPEAB-TYPEA-v0.1"


def _theta(config: GenerationConfig) -> list[dict[str, object]]:
    values = [
        ("THETA-LAT-CELLS", "cells_per_axis", config.cells_per_axis, "count", "discrete"),
        ("THETA-LAT-INT-MIN", "random_interior_nodes_min", config.random_interior_nodes_min, "count", "discrete"),
        ("THETA-LAT-INT-MAX", "random_interior_nodes_max", config.random_interior_nodes_max, "count", "discrete"),
        ("THETA-LAT-FACE-MIN", "random_face_pair_nodes_min", config.random_face_pair_nodes_min, "count", "discrete"),
        ("THETA-LAT-FACE-MAX", "random_face_pair_nodes_max", config.random_face_pair_nodes_max, "count", "discrete"),
        ("THETA-LAT-DEG-MIN", "min_degree", config.min_degree, "count", "discrete"),
        ("THETA-LAT-DEG-MAX", "max_degree", config.max_degree, "count", "discrete"),
    ]
    return [
        {
            "parameter_id": parameter_id, "raw_parameter_name": name, "normalized_name": name,
            "value": value, "unit": unit, "value_type": value_type, "applicable_family": ["lattice_type_a"],
        }
        for parameter_id, name, value, unit, value_type in values
    ]


def build_type_a_request(
    *, config: GenerationConfig, target_vf: float, random_seed: int, model_id: str,
    requested_formats: Iterable[str], code_sha256: str, root: str | Path,
) -> GenerationRequest:
    formats = list(dict.fromkeys(requested_formats))
    config_identity = {
        "model_id": model_id, "config": config.to_identity_dict(), "target_vf": target_vf,
        "random_seed": random_seed, "requested_formats": formats,
    }
    config_sha256 = sha256_hex(config_identity)
    payload = {
        "generator_id": GENERATOR_ID, "generator_version": "0.1", "generator_family": "lattice",
        "theta_schema_id": "THETA-LATTICE-TYPEA-v0.1", "theta_values": _theta(config),
        "generation_config": {"model_id": model_id, **config.to_identity_dict()},
        "physical_size_mm": {"x": config.total_length_mm, "y": config.total_length_mm, "z": config.total_length_mm},
        "target_vf": target_vf, "random_seed": random_seed, "requested_geometry_formats": formats,
        "base_geometry_id": f"BASEGEOM::{model_id}", "legacy_ids": [SOURCE_ALIAS],
        "notes": "Single fixed-seed Type-A request extracted from the professor notebook; no candidate-pool/LHS execution.",
    }
    provenance = {
        "producer": "CINT-04-lattice-typeab-plugin", "runtime_alias": "KMK312",
        "code_identity": {"id": "URP4-LATTICE-TYPEAB-v0.1", "sha256": code_sha256},
        "config_identity": {"id": "CINT-04-TYPEA-FIXTURE-v0.1", "sha256": config_sha256},
        "source_aliases": [SOURCE_ALIAS],
        "source_artifacts": [{"source_alias": SOURCE_ALIAS, "path": SOURCE_PATH, "sha256": SOURCE_SHA256, "role": "immutable_notebook_source"}],
        "parent_object_ids": [], "notes": "Source notebook bytes remain immutable and are verified before generation.",
    }
    return GenerationRequest.from_dict(build_document(
        "GenerationRequest", payload, provenance, execution_status="passed", scientific_status="likely"
    ))


def build_geometry_artifact(
    *, request: GenerationRequest, attempt: ExportAttempt, model_id: str, qa: dict[str, object],
    observed_vf: float, root: str | Path,
) -> GeometryArtifact:
    if attempt.status != "passed" or attempt.path is None or attempt.sha256 is None or attempt.size_bytes is None:
        raise ValueError("only a passed export can become a GeometryArtifact")
    root_path = Path(root).resolve()
    relative = Path(attempt.path).resolve().relative_to(root_path).as_posix()
    code_identity = request.document["provenance"]["code_identity"]
    config_identity = request.document["provenance"]["config_identity"]
    payload = {
        "model_id": model_id, "base_geometry_id": request.payload["base_geometry_id"],
        "model_family": "Lattice Type A", "geometry_role": "generated",
        "geometry_format": attempt.geometry_format, "path": relative, "geometry_sha256": attempt.sha256,
        "size_bytes": attempt.size_bytes, "units": "mm",
        "physical_size_mm": {"x": float(qa["bbox_x_mm"]), "y": float(qa["bbox_y_mm"]), "z": float(qa["bbox_z_mm"])},
        "generation_request_id": request.object_id, "parent_geometry_artifact_id": None,
        "observed_vf": observed_vf,
        "qa": {key: qa[key] for key in ("technical_status", "topology_status", "connected_region_count", "boundary_edge_count", "nonmanifold_edge_count")},
        "legacy_ids": [SOURCE_ALIAS],
        "notes": "Analytical graph VF; STL is a non-boolean-unioned cylinder/sphere compound and may extend beyond node-domain faces by the strut radius.",
    }
    provenance = {
        "producer": "CINT-04-lattice-typeab-plugin", "runtime_alias": "KMK312",
        "code_identity": code_identity, "config_identity": config_identity,
        "source_aliases": [SOURCE_ALIAS],
        "source_artifacts": [
            {"source_alias": SOURCE_ALIAS, "path": SOURCE_PATH, "sha256": SOURCE_SHA256, "role": "immutable_notebook_source"},
            {"source_alias": f"CINT04::{model_id}::{attempt.geometry_format}", "path": relative, "sha256": attempt.sha256, "role": "generated_geometry"},
        ],
        "parent_object_ids": [request.object_id], "notes": f"Export backend {attempt.backend_id}",
    }
    return GeometryArtifact.from_dict(build_document(
        "GeometryArtifact", payload, provenance, execution_status="passed", scientific_status="likely"
    ))

