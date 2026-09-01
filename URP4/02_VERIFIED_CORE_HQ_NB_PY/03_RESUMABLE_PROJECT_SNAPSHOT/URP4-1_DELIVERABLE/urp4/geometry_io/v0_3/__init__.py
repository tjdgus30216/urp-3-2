"""Explicit generated/imported/STP source routing and immutable preflight."""

from .source_preflight import (
    GeometrySourceRecord,
    SOURCE_GENERATED_STL,
    SOURCE_IMPORTED_STL,
    SOURCE_ORIGINAL_STP,
    inspect_source,
    route_id_for_source_type,
)

__all__ = [
    "GeometrySourceRecord",
    "SOURCE_GENERATED_STL",
    "SOURCE_IMPORTED_STL",
    "SOURCE_ORIGINAL_STP",
    "inspect_source",
    "route_id_for_source_type",
]
