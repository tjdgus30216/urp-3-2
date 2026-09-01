"""JSON Schema and cross-object semantic validation for URP4 contracts."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Mapping

from jsonschema import Draft202012Validator, FormatChecker

from .canonical import normalize_relative_path
from .ids import expected_identity_sha256, expected_object_id, make_scalar_output_id


SCHEMA_PATH = Path(__file__).with_name("schemas") / "urp4_contracts_v0_1.schema.json"
BARE_EXCEL_COLUMN = re.compile(r"^[A-Z]{1,3}$")


class ContractValidationError(ValueError):
    """Raised when schema or semantic contract checks fail."""


@lru_cache(maxsize=1)
def _validator() -> Draft202012Validator:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _raise_schema_errors(document: Mapping[str, Any]) -> None:
    errors = sorted(_validator().iter_errors(document), key=lambda err: list(err.absolute_path))
    if not errors:
        return
    formatted = []
    for error in errors[:12]:
        location = "$" + "".join(f"[{part!r}]" for part in error.absolute_path)
        formatted.append(f"{location}: {error.message}")
    raise ContractValidationError("schema validation failed: " + " | ".join(formatted))


def _check_paths(value: Any, path: tuple[str, ...] = ()) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = (*path, key)
            if key == "path" or key.endswith("_path"):
                if child is not None:
                    try:
                        normalize_relative_path(str(child))
                    except ValueError as exc:
                        raise ContractValidationError(f"non-portable path at {'.'.join(child_path)}: {exc}") from exc
            _check_paths(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _check_paths(child, (*path, str(index)))


def _check_source_scoped_ids(document: Mapping[str, Any]) -> None:
    payload = document["payload"]
    values: list[tuple[str, str]] = []
    if document["object_type"] == "DescriptorResult":
        values.append(("descriptor_id", payload["descriptor_id"]))
    elif document["object_type"] == "DatasetManifest":
        values.extend(("feature_ids", item) for item in payload["feature_ids"])
        values.extend(("target_ids", item) for item in payload["target_ids"])
    elif document["object_type"] == "TrainingRunManifest":
        values.extend(("feature_ids", item) for item in payload["feature_ids"])
        values.append(("target_id", payload["target_id"]))

    for field, value in values:
        if BARE_EXCEL_COLUMN.fullmatch(value):
            raise ContractValidationError(
                f"{field} contains bare Excel column {value!r}; use a source-scoped semantic ID and keep the column only in legacy_ids"
            )


def validate_document(document: Mapping[str, Any], expected_type: str | None = None) -> None:
    """Validate schema, identity, paths, and semantic separation rules."""

    _raise_schema_errors(document)
    if expected_type and document["object_type"] != expected_type:
        raise ContractValidationError(
            f"expected object_type {expected_type!r}, got {document['object_type']!r}"
        )
    expected_hash = expected_identity_sha256(document)
    if document["identity_sha256"] != expected_hash:
        raise ContractValidationError(
            f"identity_sha256 mismatch: expected {expected_hash}, got {document['identity_sha256']}"
        )
    expected_id = expected_object_id(document)
    if document["object_id"] != expected_id:
        raise ContractValidationError(f"object_id mismatch: expected {expected_id}, got {document['object_id']}")

    _check_paths(document)
    _check_source_scoped_ids(document)

    if document["object_type"] == "DescriptorResult":
        payload = document["payload"]
        expected_scalar = make_scalar_output_id(payload)
        if payload["scalar_output_id"] != expected_scalar:
            raise ContractValidationError(
                f"scalar_output_id mismatch: expected {expected_scalar}, got {payload['scalar_output_id']}"
            )
        if payload["scientific_status"] != document["scientific_status"]:
            raise ContractValidationError(
                "DescriptorResult payload.scientific_status must equal envelope scientific_status"
            )


def validate_bundle(documents: Iterable[Mapping[str, Any]]) -> None:
    """Validate a bundle and its explicit cross-object references."""

    docs = list(documents)
    for document in docs:
        validate_document(document)
    by_id = {document["object_id"]: document for document in docs}
    if len(by_id) != len(docs):
        raise ContractValidationError("bundle contains duplicate object_id values")

    for document in docs:
        payload = document["payload"]
        object_type = document["object_type"]
        if object_type == "GeometryArtifact" and payload["generation_request_id"]:
            parent = by_id.get(payload["generation_request_id"])
            if parent is not None and parent["object_type"] != "GenerationRequest":
                raise ContractValidationError("GeometryArtifact generation_request_id does not point to GenerationRequest")
        elif object_type == "DescriptorResult":
            geometry = by_id.get(payload["geometry_artifact_id"])
            if geometry is not None:
                if geometry["object_type"] != "GeometryArtifact":
                    raise ContractValidationError("DescriptorResult geometry_artifact_id has wrong object type")
                if geometry["payload"]["geometry_sha256"] != payload["geometry_sha256"]:
                    raise ContractValidationError("DescriptorResult geometry_sha256 differs from GeometryArtifact")
        elif object_type == "TrainingRunManifest":
            dataset = by_id.get(payload["dataset_manifest_id"])
            if dataset is not None:
                if dataset["object_type"] != "DatasetManifest":
                    raise ContractValidationError("TrainingRunManifest dataset_manifest_id has wrong object type")
                if dataset["payload"]["data_sha256"] != payload["dataset_sha256"]:
                    raise ContractValidationError("TrainingRunManifest dataset_sha256 differs from DatasetManifest")

