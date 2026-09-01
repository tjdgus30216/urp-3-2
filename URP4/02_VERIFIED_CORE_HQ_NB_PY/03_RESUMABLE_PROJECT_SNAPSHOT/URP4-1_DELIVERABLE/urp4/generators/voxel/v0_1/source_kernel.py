"""Definition-only loader for the approved NB-CURRENT voxel source kernel.

No notebook top-level code, candidate batches, descriptor extraction, Colab
mounts, or output cells are executed.  The selected definitions are compiled
into an isolated namespace whose globals are supplied explicitly per request.
"""

from __future__ import annotations

import ast
import json
import math
import struct
import threading
from pathlib import Path
from typing import Any

import numpy as np
from scipy.ndimage import (
    binary_closing,
    binary_dilation,
    binary_opening,
    distance_transform_edt,
    gaussian_filter,
    label,
)
from skimage import measure

from urp4.contracts.v0_1.canonical import sha256_file


SOURCE_ALIAS = "NB-CURRENT"
SOURCE_PATH = "experiments/lab_001_xy_connection_20260626/notebooks/R06V2_integrated_legacy_candidate_v0_2.ipynb"
SOURCE_SHA256 = "29131ce5f3d8d59cf6a7211d963a23f85c14f950ea335bbd237b52a7ff76980f"

MATCHING_SOURCES = (
    (
        "NB-ORIG",
        "outputs/URP4-1/Model_generator_260506_descriptor_v5_boundary_symmetry_perfboost.ipynb",
        "47aa3889f61d7e4bfbca37b65286e6b7ad81cf185ab4dd86ebdc263af5d8b7b7",
    ),
    (
        "GEN-TPMS-MULTIWALL-VF50-20260716",
        "experiments/lab_001_xy_connection_20260626/data/raw/professor_generators_20260716/Multiwall_model_generator_VF50.ipynb",
        "46dcac9467dcb9904eb0d41ebb6639a8cb304d47e46b6c5d478e74df4f497923",
    ),
)

SELECTED_FUNCTIONS = {
    # Cell 2: mask/mesh/connectivity primitives.
    "json_dumps", "write_binary_stl", "estimate_mask_vf", "mesh_from_binary_mask",
    "keep_largest_component", "count_connected_components", "_draw_voxel_bridge",
    "repair_mask_connectivity", "repair_lattice_voxel_connectivity", "enforce_vf_by_rank",
    # Cell 3: boundary, symmetry and finalization closure.
    "_canonical_face_layer", "_set_canonical_face_layer", "_local_face_slices",
    "_stabilize_contact_pattern_edges", "_contact_depth", "enforce_contact_face_symmetry",
    "contact_face_symmetry_report", "_axis_symmetry_views", "symmetrize_scalar_field",
    "symmetrize_binary_mask", "strongest_connectivity_repair", "_safe_positive_int_scalar",
    "_connect_components_through_interior", "finalize_lattice_voxel_mask",
    # Cell 4: CPU/GPU selector used by the Fourier field.
    "_get_generation_gpu_device", "_xp_for_generation", "_to_numpy_array",
    # Cell 5: voxel generator proper.
    "periodic_fourier_field", "stochastic_gaussian_field", "enforce_periodic_faces",
    "limit_max_thickness_approx", "enforce_voxel_min_hole_size",
    "generate_voxel_mask", "generate_voxel_candidate",
}


def verify_sources(root: str | Path) -> None:
    root_path = Path(root).resolve()
    for alias, relative, expected in ((SOURCE_ALIAS, SOURCE_PATH, SOURCE_SHA256), *MATCHING_SOURCES):
        path = root_path / relative
        if not path.is_file():
            raise RuntimeError(f"immutable source missing: {alias}: {path}")
        observed = sha256_file(path)
        if observed != expected:
            raise RuntimeError(f"immutable source hash mismatch: {alias}: {observed}")


def _selected_module(root: Path) -> ast.Module:
    notebook = json.loads((root / SOURCE_PATH).read_text(encoding="utf-8"))
    nodes: list[ast.stmt] = []
    for cell_index in (2, 3, 4, 5):
        source = "".join(notebook["cells"][cell_index]["source"])
        tree = ast.parse(source)
        nodes.extend(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name in SELECTED_FUNCTIONS
        )
    missing = SELECTED_FUNCTIONS - {node.name for node in nodes if isinstance(node, ast.FunctionDef)}
    if missing:
        raise RuntimeError(f"selected source functions missing: {sorted(missing)}")
    return ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[]))


def load_source_namespace(root: str | Path, config: dict[str, Any]) -> dict[str, Any]:
    """Load an isolated source namespace with every geometry-affecting global explicit."""

    root_path = Path(root).resolve()
    verify_sources(root_path)
    namespace: dict[str, Any] = {
        "np": np,
        "json": json,
        "math": math,
        "struct": struct,
        "threading": threading,
        "Path": Path,
        "measure": measure,
        "binary_closing": binary_closing,
        "binary_dilation": binary_dilation,
        "binary_opening": binary_opening,
        "distance_transform_edt": distance_transform_edt,
        "gaussian_filter": gaussian_filter,
        "label": label,
        "CUPY_AVAILABLE": False,
        "cp": None,
        "USE_GPU_FOR_GENERATION": False,
        "GPU_DEVICE_ID": 0,
        "_GPU_CONTEXT": threading.local(),
        "DEVICE": "cpu",
        "VOXEL_GRID_N": int(config["grid_n"]),
        "SIZE_MM": float(config["size_mm"]),
        # Source generate_voxel_mask reads this global, not params['target_vf'].
        "TARGET_VF": float(config["target_vf"]),
        "VF_TOLERANCE": float(config["vf_tolerance"]),
        "MARCHING_CUBES_STEP_SIZE": int(config["marching_cubes_step_size"]),
        "STRICT_GLOBAL_SYMMETRY": bool(config["strict_global_symmetry"]),
        "STRICT_SYMMETRY_METHOD": "score_threshold",
        "ENFORCE_CONTACT_FACE_SYMMETRY": bool(config["enforce_contact_face_symmetry"]),
        "CONTACT_SURFACE_DEPTH_VOX": int(config["contact_surface_depth_vox"]),
        "FORCE_CONNECTED_LATTICE_VOXEL": bool(config["force_connected"]),
        "CONNECTIVITY_REPAIR_MODE": str(config["connectivity_repair_mode"]),
        "CONNECTIVITY_BRIDGE_RADIUS_VOX": int(config["connectivity_bridge_radius_vox"]),
        "CONNECTIVITY_MIN_COMPONENT_VOXELS": int(config["connectivity_min_component_voxels"]),
        "CONNECTIVITY_MAX_BRIDGES": int(config["connectivity_max_bridges"]),
        "CONNECTIVITY_RETRY_AFTER_CONTACT_SYMMETRY": bool(config["connectivity_retry_after_contact_symmetry"]),
    }
    exec(
        compile(_selected_module(root_path), f"{SOURCE_PATH}::voxel_selected_definitions", "exec"),
        namespace,
    )
    return namespace
