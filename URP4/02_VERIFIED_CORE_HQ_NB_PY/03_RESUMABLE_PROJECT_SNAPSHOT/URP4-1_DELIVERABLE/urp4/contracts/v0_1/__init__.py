"""URP4 common interface and identity contract v0.1."""

from .ids import CONTRACT_VERSION, build_document
from .models import (
    DatasetManifest,
    DescriptorResult,
    GenerationRequest,
    GeometryArtifact,
    TrainingRunManifest,
)
from .validation import validate_bundle, validate_document

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

