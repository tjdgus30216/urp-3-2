"""Semantic ID construction for URP4 contract objects."""

from __future__ import annotations

import copy
import re
from datetime import datetime, timezone
from typing import Any, Mapping

from .canonical import sha256_hex


CONTRACT_VERSION = "URP4-CONTRACT-v0.1"

OBJECT_PREFIX = {
    "GenerationRequest": "GENREQ",
    "GeometryArtifact": "GEOM",
    "DescriptorResult": "DOBS",
    "DatasetManifest": "DATASET",
    "TrainingRunManifest": "TRAINRUN",
}


def _slug(value: str, fallback: str = "OBJECT") -> str:
    token = re.sub(r"[^A-Za-z0-9._-]+", "-", str(value).strip()).strip("-")
    return (token or fallback).upper()[:80]


def scalar_output_identity(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Fields that define the meaning of a descriptor scalar independent of geometry."""

    return {
        "descriptor_schema_version": payload["descriptor_schema_version"],
        "descriptor_schema_sha256": payload["descriptor_schema_sha256"],
        "descriptor_id": payload["descriptor_id"],
        "formula_id": payload["formula_id"],
        "population_id": payload["population_id"],
        "backend_id": payload["backend_id"],
        "statistic": payload["statistic"],
        "unit": payload["unit"],
    }


def make_scalar_output_id(payload: Mapping[str, Any]) -> str:
    identity = scalar_output_identity(payload)
    digest = sha256_hex(identity)
    label = f"{payload['formula_id']}-{payload['population_id']}-{payload['backend_id']}"
    return f"SCALAR::{_slug(label)}::sha256-{digest[:12]}"


def identity_payload(document: Mapping[str, Any]) -> dict[str, Any]:
    """Return the immutable semantic identity subset for a contract document.

    Deliberate exclusions: timestamps, execution/scientific review state, local
    source paths, notes, output/report locations, descriptor numeric values, and
    training metrics. A changed value under the same DescriptorResult ID is thus
    detectable as computational drift rather than silently becoming a new player.
    """

    object_type = document["object_type"]
    payload = document["payload"]
    provenance = document["provenance"]
    common = {
        "contract_version": document["contract_version"],
        "object_type": object_type,
        "code_sha256": provenance["code_identity"]["sha256"],
        "config_sha256": provenance["config_identity"]["sha256"],
    }

    if object_type == "GenerationRequest":
        specific = {
            key: payload.get(key)
            for key in (
                "generator_id",
                "generator_version",
                "generator_family",
                "theta_schema_id",
                "theta_values",
                "generation_config",
                "physical_size_mm",
                "target_vf",
                "random_seed",
                "requested_geometry_formats",
                "base_geometry_id",
            )
        }
    elif object_type == "GeometryArtifact":
        specific = {
            key: payload.get(key)
            for key in (
                "model_id",
                "base_geometry_id",
                "model_family",
                "geometry_role",
                "geometry_format",
                "geometry_sha256",
                "units",
                "physical_size_mm",
                "generation_request_id",
                "parent_geometry_artifact_id",
            )
        }
    elif object_type == "DescriptorResult":
        specific = {
            "geometry_artifact_id": payload["geometry_artifact_id"],
            "geometry_sha256": payload["geometry_sha256"],
            "scalar_output": scalar_output_identity(payload),
            "run_id": payload["run_id"],
        }
    elif object_type == "DatasetManifest":
        specific = {
            key: payload.get(key)
            for key in (
                "dataset_version",
                "data_sha256",
                "grain",
                "row_count",
                "model_count",
                "descriptor_schema_version",
                "descriptor_schema_sha256",
                "primary_key_fields",
                "source_object_ids",
                "feature_ids",
                "target_ids",
                "grouping_keys",
                "domain_policy_id",
                "missingness_policy",
                "excluded_ids",
            )
        }
    elif object_type == "TrainingRunManifest":
        specific = {
            key: payload.get(key)
            for key in (
                "training_run_label",
                "dataset_manifest_id",
                "dataset_version",
                "dataset_sha256",
                "target_id",
                "objective_direction",
                "performance_domain",
                "feature_ids",
                "method_id",
                "split_contract",
                "runtime_alias",
            )
        }
    else:
        raise ValueError(f"unsupported object_type: {object_type!r}")
    return {**common, "identity": specific}


def expected_identity_sha256(document: Mapping[str, Any]) -> str:
    return sha256_hex(identity_payload(document))


def expected_object_id(document: Mapping[str, Any]) -> str:
    payload = document["payload"]
    object_type = document["object_type"]
    digest = expected_identity_sha256(document)
    if object_type == "GenerationRequest":
        label = payload["generator_id"]
    elif object_type == "GeometryArtifact":
        label = payload["model_id"]
    elif object_type == "DescriptorResult":
        label = f"{payload['formula_id']}-{payload['population_id']}"
    elif object_type == "DatasetManifest":
        label = payload["dataset_version"]
    elif object_type == "TrainingRunManifest":
        label = f"{payload['method_id']}-{payload['target_id']}"
    else:
        raise ValueError(f"unsupported object_type: {object_type!r}")
    return f"{OBJECT_PREFIX[object_type]}::{_slug(label)}::sha256-{digest[:12]}"


def build_document(
    object_type: str,
    payload: Mapping[str, Any],
    provenance: Mapping[str, Any],
    *,
    execution_status: str = "pending",
    scientific_status: str = "unresolved",
    created_at_utc: str | None = None,
) -> dict[str, Any]:
    """Build a contract envelope without reading global configuration."""

    if object_type not in OBJECT_PREFIX:
        raise ValueError(f"unsupported object_type: {object_type!r}")
    body = copy.deepcopy(dict(payload))
    if object_type == "DescriptorResult":
        body["scalar_output_id"] = make_scalar_output_id(body)
    document: dict[str, Any] = {
        "contract_version": CONTRACT_VERSION,
        "object_type": object_type,
        "object_id": "PENDING",
        "identity_sha256": "0" * 64,
        "created_at_utc": created_at_utc or datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "execution_status": execution_status,
        "scientific_status": scientific_status,
        "provenance": copy.deepcopy(dict(provenance)),
        "payload": body,
    }
    document["identity_sha256"] = expected_identity_sha256(document)
    document["object_id"] = expected_object_id(document)
    return document

