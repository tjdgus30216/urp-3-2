"""Data objects and fail-closed errors for the Lattice Type A/B plugin."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np


class LatticeGeneratorError(RuntimeError):
    """Base error for a rejected or failed generation request."""


class TypeBInputUnavailable(LatticeGeneratorError):
    """Raised when Type-B is requested without an identity-locked workbook."""


class StepBackendUnavailable(LatticeGeneratorError):
    """Raised when analytical STEP export is requested without FreeCAD/Part."""


@dataclass(frozen=True)
class GenerationConfig:
    """Explicit subset of notebook ``GenerationConfig`` used by the plugin.

    Defaults preserve the professor-delivered Type-A topology and mesh settings.
    Candidate-pool/LHS counts and author-specific paths are orchestration settings,
    so they are deliberately outside this one-request generator contract.
    """

    total_length_mm: float = 30.0
    cells_per_axis: int = 5
    random_interior_nodes_min: int = 4
    random_interior_nodes_max: int = 12
    random_face_pair_nodes_min: int = 1
    random_face_pair_nodes_max: int = 4
    min_degree: int = 3
    max_degree: int = 6
    merge_round_digits: int = 6
    min_edge_length_mm: float = 0.05
    cylinder_sections: int = 16
    node_sphere_subdivisions: int = 2
    mesh_mode: str = "cylinders"
    type_b_node_jitter_mm: float = 0.10
    type_b_edge_dropout_prob: float = 0.0
    type_b_anisotropic_scale_std: float = 0.015

    def __post_init__(self) -> None:
        if self.total_length_mm <= 0:
            raise ValueError("total_length_mm must be positive")
        if self.cells_per_axis < 1:
            raise ValueError("cells_per_axis must be >= 1")
        if not (0 <= self.random_interior_nodes_min <= self.random_interior_nodes_max):
            raise ValueError("invalid random interior-node range")
        if not (0 <= self.random_face_pair_nodes_min <= self.random_face_pair_nodes_max):
            raise ValueError("invalid random face-pair range")
        if not (1 <= self.min_degree <= self.max_degree):
            raise ValueError("invalid node-degree range")
        if self.min_edge_length_mm <= 0:
            raise ValueError("min_edge_length_mm must be positive")
        if self.cylinder_sections < 3:
            raise ValueError("cylinder_sections must be >= 3")
        if self.node_sphere_subdivisions < 0:
            raise ValueError("node_sphere_subdivisions must be >= 0")
        if self.mesh_mode != "cylinders":
            raise ValueError("CINT-04 v0.1 permits only the notebook cylinder/sphere mesh backend")
        if self.type_b_node_jitter_mm < 0 or self.type_b_edge_dropout_prob < 0:
            raise ValueError("Type-B modification settings cannot be negative")
        if not 0 <= self.type_b_edge_dropout_prob < 1:
            raise ValueError("type_b_edge_dropout_prob must be in [0, 1)")
        if self.type_b_anisotropic_scale_std < 0:
            raise ValueError("type_b_anisotropic_scale_std cannot be negative")

    @property
    def cell_size_mm(self) -> float:
        return self.total_length_mm / self.cells_per_axis

    def to_identity_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LatticeGraph:
    nodes: np.ndarray
    edges: np.ndarray
    radii: np.ndarray
    source_type: str
    target_vf: float
    actual_vf: float
    source_name: str

    def validate(self) -> None:
        self.nodes = np.asarray(self.nodes, dtype=float)
        self.edges = np.asarray(self.edges, dtype=int)
        self.radii = np.asarray(self.radii, dtype=float)
        if self.nodes.ndim != 2 or self.nodes.shape[1] != 3 or len(self.nodes) < 2:
            raise LatticeGeneratorError("nodes must have shape (N, 3) with N >= 2")
        if self.edges.ndim != 2 or self.edges.shape[1] != 2 or len(self.edges) < 1:
            raise LatticeGeneratorError("edges must have shape (S, 2) with S >= 1")
        if len(self.radii) != len(self.edges) or np.any(self.radii <= 0):
            raise LatticeGeneratorError("radii must be positive and aligned one-to-one with edges")
        if not np.isfinite(self.nodes).all() or not np.isfinite(self.radii).all():
            raise LatticeGeneratorError("graph arrays contain non-finite values")
        if self.edges.min() < 0 or self.edges.max() >= len(self.nodes):
            raise LatticeGeneratorError("edge references an invalid node")
        if not 0 < float(self.target_vf) <= 1 or not 0 < float(self.actual_vf) <= 1:
            raise LatticeGeneratorError("target_vf and actual_vf must be in (0, 1]")


@dataclass(frozen=True)
class ExportAttempt:
    geometry_format: str
    status: str
    path: str | None
    sha256: str | None
    size_bytes: int | None
    backend_id: str
    reason: str

