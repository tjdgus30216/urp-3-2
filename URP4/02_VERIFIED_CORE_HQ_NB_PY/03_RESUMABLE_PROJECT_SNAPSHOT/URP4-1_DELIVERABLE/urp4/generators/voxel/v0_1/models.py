"""Typed configuration and result objects for the Voxel source-replay plugin."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


VOXEL_MODES = ("periodic_isotropic", "periodic_orthotropic", "stochastic")


class VoxelGeneratorError(RuntimeError):
    """Raised when a voxel request cannot be executed without ambiguity."""


@dataclass(frozen=True)
class VoxelGenerationConfig:
    size_mm: float = 30.0
    grid_n: int = 40
    vf_tolerance: float = 0.050
    marching_cubes_step_size: int = 1
    strict_global_symmetry: bool = True
    enforce_contact_face_symmetry: bool = True
    contact_surface_depth_vox: int = 3
    force_connected: bool = True
    connectivity_repair_mode: str = "bridge"
    connectivity_bridge_radius_vox: int = 1
    connectivity_min_component_voxels: int = 1
    connectivity_max_bridges: int = 200
    connectivity_retry_after_contact_symmetry: bool = True
    source_vf_policy: str = "explicit_global_target_equals_request"
    export_policy: str = "source_binary_stl_only"

    def __post_init__(self) -> None:
        if not np.isfinite(self.size_mm) or self.size_mm <= 0:
            raise ValueError("size_mm must be positive")
        if self.grid_n < 16:
            raise ValueError("grid_n must be >= 16")
        if not 0 < self.vf_tolerance < 1:
            raise ValueError("vf_tolerance must lie in (0,1)")
        if self.marching_cubes_step_size < 1 or self.contact_surface_depth_vox < 1:
            raise ValueError("mesh step and contact depth must be >= 1")
        if self.connectivity_repair_mode not in {"bridge", "largest"}:
            raise ValueError("unsupported connectivity_repair_mode")
        if self.connectivity_bridge_radius_vox < 1 or self.connectivity_min_component_voxels < 1:
            raise ValueError("connectivity voxel controls must be >= 1")
        if self.connectivity_max_bridges < 1:
            raise ValueError("connectivity_max_bridges must be >= 1")
        if self.source_vf_policy != "explicit_global_target_equals_request":
            raise ValueError("CINT-06 v0.1 permits only explicit global TARGET_VF authority")
        if self.export_policy != "source_binary_stl_only":
            raise ValueError("CINT-06 v0.1 permits only source binary STL export")

    def to_identity_dict(self) -> dict[str, object]:
        return {
            "size_mm": float(self.size_mm),
            "grid_n": int(self.grid_n),
            "vf_tolerance": float(self.vf_tolerance),
            "marching_cubes_step_size": int(self.marching_cubes_step_size),
            "strict_global_symmetry": bool(self.strict_global_symmetry),
            "enforce_contact_face_symmetry": bool(self.enforce_contact_face_symmetry),
            "contact_surface_depth_vox": int(self.contact_surface_depth_vox),
            "force_connected": bool(self.force_connected),
            "connectivity_repair_mode": self.connectivity_repair_mode,
            "connectivity_bridge_radius_vox": int(self.connectivity_bridge_radius_vox),
            "connectivity_min_component_voxels": int(self.connectivity_min_component_voxels),
            "connectivity_max_bridges": int(self.connectivity_max_bridges),
            "connectivity_retry_after_contact_symmetry": bool(self.connectivity_retry_after_contact_symmetry),
            "source_vf_policy": self.source_vf_policy,
            "export_policy": self.export_policy,
        }


@dataclass(frozen=True)
class VoxelCandidate:
    candidate_id: str
    voxel_mode: str
    target_vf: float
    random_seed: int
    config: VoxelGenerationConfig
    min_thickness_vox: int = 1
    min_hole_size_vox: int = 1
    max_thickness_vox: int = 8
    closing_iter: int = 0
    opening_iter: int = 0
    anisotropy_z: float = 1.0
    num_fourier_terms: int | None = 8
    sigma: float | None = None

    def __post_init__(self) -> None:
        if self.voxel_mode not in VOXEL_MODES:
            raise ValueError(f"unsupported voxel_mode: {self.voxel_mode}")
        if not 0 < self.target_vf < 1:
            raise ValueError("target_vf must lie in (0,1)")
        if self.random_seed < 0:
            raise ValueError("random_seed must be non-negative")
        for value, name in ((self.min_thickness_vox, "min_thickness_vox"), (self.min_hole_size_vox, "min_hole_size_vox"), (self.max_thickness_vox, "max_thickness_vox")):
            if value < 1:
                raise ValueError(f"{name} must be >= 1")
        if self.closing_iter < 0 or self.opening_iter < 0:
            raise ValueError("morphology iterations must be non-negative")
        if not np.isfinite(self.anisotropy_z) or self.anisotropy_z <= 0:
            raise ValueError("anisotropy_z must be positive")
        if self.voxel_mode.startswith("periodic"):
            if self.num_fourier_terms is None or self.num_fourier_terms < 1:
                raise ValueError("periodic modes require num_fourier_terms >= 1")
        elif self.sigma is None or not np.isfinite(self.sigma) or self.sigma <= 0:
            raise ValueError("stochastic mode requires positive sigma")

    def to_notebook_params(self) -> dict[str, Any]:
        config = self.config
        return {
            "generator_type": "voxel",
            "voxel_mode": self.voxel_mode,
            "size_mm": float(config.size_mm),
            # Kept for provenance; source mask code uses global TARGET_VF.
            "target_vf": float(self.target_vf),
            "stl_mesh_size_mm": 0.08,
            "grid_n": int(config.grid_n),
            "min_thickness_vox": int(self.min_thickness_vox),
            "min_hole_size_vox": int(self.min_hole_size_vox),
            "max_thickness_vox": int(self.max_thickness_vox),
            "closing_iter": int(self.closing_iter),
            "opening_iter": int(self.opening_iter),
            "anisotropy_z": float(self.anisotropy_z),
            "seed": int(self.random_seed),
            "num_fourier_terms": int(self.num_fourier_terms) if self.num_fourier_terms is not None else np.nan,
            "sigma": float(self.sigma) if self.sigma is not None else np.nan,
            "lattice_grid_n": 280,
            "node_blend_factor": 1.0,
            "lattice_binary_closing_iters": 0,
            "lattice_radius_search_iters": 6,
            "force_connected": bool(config.force_connected),
            "connectivity_repair_mode": config.connectivity_repair_mode,
            "connectivity_bridge_radius_vox": int(config.connectivity_bridge_radius_vox),
            "connectivity_min_component_voxels": int(config.connectivity_min_component_voxels),
            "connectivity_max_bridges": int(config.connectivity_max_bridges),
            "connectivity_retry_after_contact_symmetry": bool(config.connectivity_retry_after_contact_symmetry),
            "candidate_id": self.candidate_id,
        }

    def to_source_params(self) -> dict[str, Any]:
        """Notebook params plus explicit wrappers for formerly implicit globals."""
        params = self.to_notebook_params()
        params.update(
            {
                "strict_global_symmetry": bool(self.config.strict_global_symmetry),
                "contact_surface_depth_vox": int(self.config.contact_surface_depth_vox),
            }
        )
        return params


@dataclass
class VoxelGenerationResult:
    candidate: VoxelCandidate
    mask: np.ndarray
    vertices: np.ndarray
    faces: np.ndarray
    quick_descriptor: dict[str, Any]
    connectivity_info: dict[str, Any]


@dataclass(frozen=True)
class ExportAttempt:
    geometry_format: str
    status: str
    path: str | None
    sha256: str | None
    size_bytes: int | None
    backend_id: str
    notes: str
