"""Versioned cross-module contracts for URP4-1."""

from .v0_1 import (
    CONTRACT_VERSION,
    DatasetManifest,
    DescriptorResult,
    GenerationRequest,
    GeometryArtifact,
    TrainingRunManifest,
    build_document,
    validate_bundle,
    validate_document,
)

__all__ = [
    "CONTRACT_VERSION",
    "GenerationRequest",
    "GeometryArtifact",
    "DescriptorResult",
    "DatasetManifest",
    "TrainingRunManifest",
    "build_document",
    "validate_document",
    "validate_bundle",
]

