"""Immutable configuration for the NB-DEV STL import boundary."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class GeometryImportError(ValueError):
    """Raised when an external geometry input cannot be accepted safely."""


@dataclass(frozen=True)
class STLImportConfig:
    input_path: Path
    pattern: str = "*.stl"
    recursive: bool = False
    require_files: bool = True
    expected_size_mm: float | None = None
    size_tolerance_mm: float = 1.0e-3
    topology_qa: bool = False

    @classmethod
    def from_values(
        cls,
        *,
        input_path: str | Path,
        pattern: str = "*.stl",
        recursive: bool = False,
        require_files: bool = True,
        expected_size_mm: float | None = None,
        size_tolerance_mm: float = 1.0e-3,
        topology_qa: bool = False,
    ) -> "STLImportConfig":
        return cls(
            input_path=Path(input_path).expanduser(),
            pattern=str(pattern),
            recursive=bool(recursive),
            require_files=bool(require_files),
            expected_size_mm=None if expected_size_mm is None else float(expected_size_mm),
            size_tolerance_mm=float(size_tolerance_mm),
            topology_qa=bool(topology_qa),
        )
