"""Deterministic 14 x 7 TPMS Multiwall candidate-registry construction."""

from __future__ import annotations

import numpy as np

from .models import (
    MULTIWALL_MODE_TEMPLATES,
    TPMS_LIBRARY,
    MultiwallCandidate,
    MultiwallGenerationConfig,
    TPMSComponent,
)


def _uniform(rng: np.random.Generator, bounds: tuple[float, float]) -> float:
    return float(rng.uniform(bounds[0], bounds[1]))


def _integer(rng: np.random.Generator, bounds: tuple[int, int]) -> int:
    return int(rng.integers(int(bounds[0]), int(bounds[1]) + 1))


def build_multiwall_candidate_registry(seed: int = 42, grid_n: int = 150) -> list[MultiwallCandidate]:
    """Reproduce current notebook Cell 6's 98-row Multiwall registry.

    This is a registry-only operation.  It does not generate any geometry and
    does not declare the sampled VF range to be the production standard.
    """

    rng = np.random.default_rng(seed)
    candidates: list[MultiwallCandidate] = []
    index = 0
    for tpms_type in TPMS_LIBRARY:
        for combo_name, modes in MULTIWALL_MODE_TEMPLATES.items():
            components = tuple(
                TPMSComponent(
                    tpms_type=tpms_type,
                    mode=mode,
                    level_shift=float(rng.uniform(-0.35, 0.35)),
                    thickness_mm=_uniform(rng, (0.8, 2.5)),
                )
                for mode in modes
            )
            target_vf = _uniform(rng, (0.45, 0.55))
            frequency = _uniform(rng, (5.0, 5.0))
            anisotropy = tuple(_uniform(rng, (0.90, 1.20)) for _ in range(3))
            noise_amp = _uniform(rng, (0.0, 0.015))
            min_hole_size_vox = _integer(rng, (1, 1))
            component_gap_mm = _uniform(rng, (0.05, 0.35))
            random_seed = int(rng.integers(0, 2**31 - 1))
            candidate_id = f"TPMS_multiwall_{tpms_type}_{combo_name}_{index:06d}".replace(
                "/", "_"
            ).replace(" ", "_").replace("+", "-")
            config = MultiwallGenerationConfig(
                size_mm=30.0,
                grid_n=grid_n,
                frequency=frequency,
                anisotropy_xyz=anisotropy,
                noise_amp=noise_amp,
                component_gap_mm=component_gap_mm,
                min_hole_size_vox=min_hole_size_vox,
            )
            candidates.append(
                MultiwallCandidate(
                    candidate_id=candidate_id,
                    combo_name=combo_name,
                    target_vf=target_vf,
                    random_seed=random_seed,
                    components=components,
                    config=config,
                )
            )
            index += 1
    return candidates

