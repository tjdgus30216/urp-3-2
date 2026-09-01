"""Small deterministic Voxel registry; construction only, no geometry batch."""

from __future__ import annotations

import numpy as np

from .models import VOXEL_MODES, VoxelCandidate, VoxelGenerationConfig


MODE_CONFIG = {
    "periodic_isotropic": {"min_t": (1, 2), "min_h": (1, 2), "max_t": (5, 12), "terms": (4, 14), "az": (0.9, 1.1), "sigma": (1.5, 5.0)},
    "periodic_orthotropic": {"min_t": (1, 2), "min_h": (1, 2), "max_t": (5, 12), "terms": (4, 14), "az": (1.2, 2.0), "sigma": (1.5, 5.0)},
    "stochastic": {"min_t": (1, 2), "min_h": (1, 2), "max_t": (5, 14), "terms": None, "az": (0.7, 1.8), "sigma": (1.5, 5.5)},
}


def build_voxel_registry(seed: int = 42, grid_n: int = 40, target_vf: float = 0.30, rows_per_mode: int = 100, size_mm: float = 30.0) -> list[VoxelCandidate]:
    rng = np.random.default_rng(seed)
    rows: list[VoxelCandidate] = []
    for mode in VOXEL_MODES:
        cfg = MODE_CONFIG[mode]
        for index in range(rows_per_mode):
            min_thickness = int(rng.integers(cfg["min_t"][0], cfg["min_t"][1] + 1))
            min_hole = int(rng.integers(cfg["min_h"][0], cfg["min_h"][1] + 1))
            max_thickness = int(rng.integers(cfg["max_t"][0], cfg["max_t"][1] + 1))
            closing = int(rng.integers(0, 2))
            opening = int(rng.integers(0, 2))
            anisotropy = float(rng.uniform(*cfg["az"]))
            random_seed = int(rng.integers(0, 2**31 - 1))
            terms = int(rng.integers(cfg["terms"][0], cfg["terms"][1] + 1)) if cfg["terms"] else None
            sigma = None if mode.startswith("periodic") else float(rng.uniform(*cfg["sigma"]))
            rows.append(VoxelCandidate(
                candidate_id=f"VOX_{mode}_{index:06d}", voxel_mode=mode, target_vf=target_vf,
                random_seed=random_seed,
                config=VoxelGenerationConfig(size_mm=size_mm, grid_n=grid_n),
                min_thickness_vox=min_thickness,
                min_hole_size_vox=min_hole,
                max_thickness_vox=max_thickness,
                closing_iter=closing, opening_iter=opening,
                anisotropy_z=anisotropy, num_fourier_terms=terms, sigma=sigma,
            ))
    return rows
