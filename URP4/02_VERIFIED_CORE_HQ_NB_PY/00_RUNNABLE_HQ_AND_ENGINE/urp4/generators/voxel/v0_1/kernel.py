"""Explicit wrapper around the immutable notebook Voxel definitions."""

from __future__ import annotations

import numpy as np

from .models import VoxelCandidate, VoxelGenerationResult
from .source_kernel import load_source_namespace


def source_runtime_config(candidate: VoxelCandidate) -> dict[str, object]:
    config = candidate.config.to_identity_dict()
    config["target_vf"] = float(candidate.target_vf)
    return config


def generate_voxel_candidate(root: str, candidate: VoxelCandidate) -> VoxelGenerationResult:
    namespace = load_source_namespace(root, source_runtime_config(candidate))
    params_for_mask = candidate.to_source_params()
    if float(params_for_mask["target_vf"]) != float(namespace["TARGET_VF"]):
        raise ValueError("params target_vf must equal the explicit source global TARGET_VF")
    # The notebook candidate API does not return its mask.  Generate the exact
    # mask first and keep the mutation trace, then replay the deterministic
    # candidate API with a fresh params dict for source-exact arrays/quick data.
    mask = namespace["generate_voxel_mask"](params_for_mask)
    info = dict(params_for_mask.get("_last_connectivity_info", {}))
    vertices, faces, quick = namespace["generate_voxel_candidate"](candidate.to_source_params())
    return VoxelGenerationResult(
        candidate=candidate,
        mask=np.asarray(mask, dtype=bool),
        vertices=np.asarray(vertices, dtype=np.float32),
        faces=np.asarray(faces, dtype=np.int32),
        quick_descriptor=dict(quick),
        connectivity_info=info,
    )


def generate_voxel_mask(root: str, candidate: VoxelCandidate) -> np.ndarray:
    namespace = load_source_namespace(root, source_runtime_config(candidate))
    params = candidate.to_source_params()
    return np.asarray(namespace["generate_voxel_mask"](params), dtype=bool)
