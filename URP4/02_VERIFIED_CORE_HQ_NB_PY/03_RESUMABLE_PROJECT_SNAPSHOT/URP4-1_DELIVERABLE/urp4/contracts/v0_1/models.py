"""Small immutable runtime wrappers around validated JSON contract documents."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any, ClassVar, Mapping


@dataclass(frozen=True)
class ContractDocument:
    document: Mapping[str, Any]
    OBJECT_TYPE: ClassVar[str] = ""

    @classmethod
    def from_dict(cls, document: Mapping[str, Any]) -> "ContractDocument":
        from .validation import validate_document

        copied = copy.deepcopy(dict(document))
        validate_document(copied, expected_type=cls.OBJECT_TYPE)
        return cls(copied)

    @property
    def object_id(self) -> str:
        return str(self.document["object_id"])

    @property
    def payload(self) -> Mapping[str, Any]:
        return self.document["payload"]

    def to_dict(self) -> dict[str, Any]:
        return copy.deepcopy(dict(self.document))


class GenerationRequest(ContractDocument):
    OBJECT_TYPE = "GenerationRequest"


class GeometryArtifact(ContractDocument):
    OBJECT_TYPE = "GeometryArtifact"


class DescriptorResult(ContractDocument):
    OBJECT_TYPE = "DescriptorResult"


class DatasetManifest(ContractDocument):
    OBJECT_TYPE = "DatasetManifest"


class TrainingRunManifest(ContractDocument):
    OBJECT_TYPE = "TrainingRunManifest"

