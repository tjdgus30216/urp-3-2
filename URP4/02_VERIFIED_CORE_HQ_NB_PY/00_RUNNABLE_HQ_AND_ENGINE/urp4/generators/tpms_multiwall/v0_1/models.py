"""Typed TPMS Multiwall configuration and runtime result objects."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


TPMS_LIBRARY = (
    "gyroid", "primitive", "diamond", "iwp", "neovius", "lidinoid",
    "split_p", "double_gyroid", "frd", "fischer_koch_s",
    "fischer_koch_c", "pw_hybrid", "srs_like", "karcher_k_like",
)

MULTIWALL_MODE_TEMPLATES: dict[str, tuple[str, ...]] = {
    "A+B": ("solid_A", "solid_B"),
    "Wall+A": ("wall", "solid_A"),
    "Wall+B": ("wall", "solid_B"),
    "Double-wall": ("wall", "wall"),
    "Double-wall+A": ("wall", "wall", "solid_A"),
    "Double-wall+B": ("wall", "wall", "solid_B"),
    "Double-wall+A+B": ("wall", "wall", "solid_A", "solid_B"),
}


class TPMSGeneratorError(RuntimeError):
    """Raised when a TPMS request cannot be executed without ambiguity."""


@dataclass(frozen=True)
class TPMSComponent:
    tpms_type: str
    mode: str
    level_shift: float
    thickness_mm: float

    def __post_init__(self) -> None:
        if self.tpms_type not in TPMS_LIBRARY:
            raise ValueError(f"unsupported TPMS type: {self.tpms_type}")
        if self.mode not in {"wall", "solid_A", "solid_B"}:
            raise ValueError(f"unsupported TPMS component mode: {self.mode}")
        if not np.isfinite(self.level_shift):
            raise ValueError("level_shift must be finite")
        if not np.isfinite(self.thickness_mm) or self.thickness_mm <= 0:
            raise ValueError("thickness_mm metadata must be finite and positive")

    def to_dict(self) -> dict[str, object]:
        return {
            "tpms_type": self.tpms_type,
            "mode": self.mode,
            "level_shift": float(self.level_shift),
            "thickness_mm": float(self.thickness_mm),
        }


@dataclass(frozen=True)
class MultiwallGenerationConfig:
    size_mm: float = 30.0
    grid_n: int = 40
    frequency: float = 5.0
    anisotropy_xyz: tuple[float, float, float] = (1.0, 1.0, 1.0)
    noise_amp: float = 0.0
    component_gap_mm: float = 0.10
    min_hole_size_vox: int = 1
    vf_tolerance: float = 0.050
    marching_cubes_step_size: int = 1
    connectivity_bridge_radius_vox: int = 3
    connectivity_min_component_voxels: int = 1
    connectivity_max_bridges: int = 500
    max_islands_before_skip_repair: int = 400
    open_cell_policy: str = "source_inactive_report_only"
    thickness_policy: str = "metadata_only_target_vf_bisection"

    def __post_init__(self) -> None:
        if not np.isfinite(self.size_mm) or self.size_mm <= 0:
            raise ValueError("size_mm must be positive")
        if self.grid_n < 16:
            raise ValueError("grid_n must be >= 16")
        if not np.isfinite(self.frequency) or self.frequency <= 0:
            raise ValueError("frequency must be positive")
        if len(self.anisotropy_xyz) != 3 or any((not np.isfinite(v) or v <= 0) for v in self.anisotropy_xyz):
            raise ValueError("anisotropy_xyz must contain three positive values")
        if not np.isfinite(self.noise_amp) or self.noise_amp < 0:
            raise ValueError("noise_amp must be non-negative")
        if not np.isfinite(self.component_gap_mm) or self.component_gap_mm < 0:
            raise ValueError("component_gap_mm must be non-negative")
        if self.min_hole_size_vox < 1 or self.marching_cubes_step_size < 1:
            raise ValueError("voxel and marching-cubes controls must be >= 1")
        if not (0 < self.vf_tolerance < 1):
            raise ValueError("vf_tolerance must lie in (0, 1)")
        if self.open_cell_policy != "source_inactive_report_only":
            raise ValueError("CINT-05 v0.1 only permits source-inactive report-only open-cell policy")
        if self.thickness_policy != "metadata_only_target_vf_bisection":
            raise ValueError("CINT-05 v0.1 preserves source thickness as metadata only")

    def to_identity_dict(self) -> dict[str, object]:
        return {
            "size_mm": float(self.size_mm),
            "grid_n": int(self.grid_n),
            "frequency": float(self.frequency),
            "anisotropy_xyz": [float(v) for v in self.anisotropy_xyz],
            "noise_amp": float(self.noise_amp),
            "component_gap_mm": float(self.component_gap_mm),
            "min_hole_size_vox": int(self.min_hole_size_vox),
            "vf_tolerance": float(self.vf_tolerance),
            "marching_cubes_step_size": int(self.marching_cubes_step_size),
            "connectivity_bridge_radius_vox": int(self.connectivity_bridge_radius_vox),
            "connectivity_min_component_voxels": int(self.connectivity_min_component_voxels),
            "connectivity_max_bridges": int(self.connectivity_max_bridges),
            "max_islands_before_skip_repair": int(self.max_islands_before_skip_repair),
            "open_cell_policy": self.open_cell_policy,
            "thickness_policy": self.thickness_policy,
        }


@dataclass(frozen=True)
class MultiwallCandidate:
    candidate_id: str
    combo_name: str
    target_vf: float
    random_seed: int
    components: tuple[TPMSComponent, ...]
    config: MultiwallGenerationConfig

    def __post_init__(self) -> None:
        expected = MULTIWALL_MODE_TEMPLATES.get(self.combo_name)
        modes = tuple(component.mode for component in self.components)
        if expected is None or modes != expected:
            raise ValueError(f"component modes {modes} do not match combo {self.combo_name}: {expected}")
        if not (0 < self.target_vf < 1):
            raise ValueError("target_vf must lie in (0, 1)")
        if self.random_seed < 0:
            raise ValueError("random_seed must be non-negative")

    def to_source_params(self) -> dict[str, Any]:
        config = self.config
        return {
            "generator_type": "tpms",
            "tpms_stage": "multiwall",
            "multiwall_combo": self.combo_name,
            "size_mm": float(config.size_mm),
            "target_vf": float(self.target_vf),
            "stl_mesh_size_mm": 0.08,
            "grid_n": int(config.grid_n),
            "frequency": float(config.frequency),
            "anisotropy_xyz": [float(v) for v in config.anisotropy_xyz],
            "noise_amp": float(config.noise_amp),
            "min_hole_size_vox": int(config.min_hole_size_vox),
            "component_gap_mm": float(config.component_gap_mm),
            "components": [component.to_dict() for component in self.components],
            "seed": int(self.random_seed),
            "lattice_grid_n": 280,
            "node_blend_factor": 1.0,
            "lattice_binary_closing_iters": 0,
            "lattice_radius_search_iters": 6,
            "candidate_id": self.candidate_id,
        }


@dataclass
class TPMSGenerationResult:
    candidate: MultiwallCandidate
    mask: np.ndarray
    vertices: np.ndarray
    faces: np.ndarray
    quick_descriptor: dict[str, Any]
    connectivity_info: dict[str, Any]
    open_cell_pass: bool


@dataclass(frozen=True)
class ExportAttempt:
    geometry_format: str
    status: str
    path: str | None
    sha256: str | None
    size_bytes: int | None
    backend_id: str
    notes: str

