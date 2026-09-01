"""Source-equivalent TPMS mask, repair, mesh, and QA kernels."""

from __future__ import annotations

import json

import numpy as np
from scipy.ndimage import (
    binary_dilation,
    binary_erosion,
    binary_opening,
    distance_transform_edt,
    label,
)
from skimage import measure

from .fields import make_tpms_grid, tpms_field
from .models import MultiwallCandidate, TPMSGenerationResult, TPMSGeneratorError


def estimate_mask_vf(mask: np.ndarray) -> float:
    return float(np.mean(mask.astype(bool)))


def count_connected_components(mask: np.ndarray) -> int:
    _, count = label(np.asarray(mask, dtype=bool))
    return int(count)


def keep_largest_component(mask: np.ndarray) -> np.ndarray:
    labels, count = label(mask)
    if count == 0:
        return mask
    counts = np.bincount(labels.ravel())
    counts[0] = 0
    return labels == int(np.argmax(counts))


def _draw_voxel_bridge(
    mask: np.ndarray, p0: np.ndarray, p1: np.ndarray, radius_vox: int = 1
) -> tuple[np.ndarray, int]:
    result = np.asarray(mask, dtype=bool).copy()
    p0 = np.asarray(np.rint(p0), dtype=int)
    p1 = np.asarray(np.rint(p1), dtype=int)
    shape = np.asarray(result.shape, dtype=int)
    p0 = np.clip(p0, 0, shape - 1)
    p1 = np.clip(p1, 0, shape - 1)
    coords = []
    current = p0.copy()
    coords.append(current.copy())
    for axis in list(np.argsort(-np.abs(p1 - p0))):
        step = 1 if p1[axis] > current[axis] else -1
        while current[axis] != p1[axis]:
            current = current.copy()
            current[axis] += step
            coords.append(current.copy())
    array = np.asarray(coords, dtype=int)
    array = np.clip(array, 0, shape - 1)
    bridge = np.zeros_like(result, dtype=bool)
    bridge[array[:, 0], array[:, 1], array[:, 2]] = True
    dilation_radius = max(0, int(radius_vox) - 1)
    if dilation_radius > 0:
        bridge = binary_dilation(bridge, iterations=dilation_radius)
    before = int(result.sum())
    result |= bridge
    return result, int(result.sum()) - before


def repair_mask_connectivity(
    mask: np.ndarray,
    mode: str = "bridge",
    bridge_radius_vox: int = 1,
    min_component_voxels: int = 1,
    max_bridges: int = 200,
) -> tuple[np.ndarray, dict[str, object]]:
    result = np.asarray(mask, dtype=bool).copy()
    info: dict[str, object] = {
        "component_count_before": count_connected_components(result),
        "component_count_after": None,
        "connectivity_repaired": False,
        "connectivity_mode": str(mode),
        "bridges_added": 0,
        "voxels_added_by_bridges": 0,
        "small_components_removed": 0,
    }
    if int(info["component_count_before"]) <= 1:
        info["component_count_after"] = info["component_count_before"]
        return result, info
    labels, component_count = label(result)
    counts = np.bincount(labels.ravel())
    counts[0] = 0
    minimum = max(1, int(min_component_voxels))
    if minimum > 1:
        remove_ids = [index for index in range(1, component_count + 1) if counts[index] < minimum]
        if remove_ids:
            result[np.isin(labels, remove_ids)] = False
            info["small_components_removed"] = int(len(remove_ids))
            labels, component_count = label(result)
            counts = np.bincount(labels.ravel()) if component_count > 0 else np.array([0])
            if len(counts) > 0:
                counts[0] = 0
    if component_count <= 1:
        info["component_count_after"] = int(component_count)
        info["connectivity_repaired"] = True
        return result, info
    if str(mode).lower() == "largest":
        repaired = keep_largest_component(result)
        info["component_count_after"] = count_connected_components(repaired)
        info["connectivity_repaired"] = True
        return repaired, info
    largest_id = int(np.argmax(counts))
    connected = labels == largest_id
    remaining_ids = [index for index in range(1, component_count + 1) if index != largest_id and counts[index] > 0]
    repaired = result.copy()
    maximum = max(1, int(max_bridges))
    for _ in range(min(maximum, len(remaining_ids))):
        current_labels, current_count = label(repaired & (~connected))
        if current_count == 0:
            break
        distances, nearest = distance_transform_edt(~connected, return_indices=True)
        best = None
        for component_id in range(1, current_count + 1):
            coords = np.argwhere(current_labels == component_id)
            if coords.size == 0:
                continue
            values = distances[coords[:, 0], coords[:, 1], coords[:, 2]]
            selected = int(np.argmin(values))
            point = coords[selected]
            target = np.array(
                [
                    nearest[0, point[0], point[1], point[2]],
                    nearest[1, point[0], point[1], point[2]],
                    nearest[2, point[0], point[1], point[2]],
                ],
                dtype=int,
            )
            distance = float(values[selected])
            if best is None or distance < best[0]:
                best = (distance, point, target)
        if best is None:
            break
        _, point, target = best
        repaired, added = _draw_voxel_bridge(repaired, point, target, radius_vox=bridge_radius_vox)
        info["bridges_added"] = int(info["bridges_added"]) + 1
        info["voxels_added_by_bridges"] = int(info["voxels_added_by_bridges"]) + int(added)
        connected = keep_largest_component(repaired)
        if count_connected_components(repaired) <= 1:
            break
    info["component_count_after"] = count_connected_components(repaired)
    info["connectivity_repaired"] = int(info["component_count_after"]) <= 1
    return repaired, info


def enforce_min_hole_size(mask: np.ndarray, min_hole_size_vox: int = 1) -> np.ndarray:
    size = int(min_hole_size_vox)
    if size <= 1:
        return mask
    pores = ~np.asarray(mask, dtype=bool)
    pores = binary_opening(pores, iterations=max(1, size - 1))
    return ~pores


def _raw_mask_from_band(F: np.ndarray, mode: str, half_band: float, level_shift: float = 0.0) -> np.ndarray:
    if mode == "wall":
        return np.abs(F - level_shift) <= half_band
    if mode == "solid_A":
        return (F >= level_shift) & (F <= level_shift + 2 * half_band)
    if mode == "solid_B":
        return (F <= level_shift) & (F >= level_shift - 2 * half_band)
    raise ValueError(f"Unknown TPMS mode: {mode}")


def make_mask_for_target_vf(
    F: np.ndarray,
    mode: str,
    target_vf: float,
    occupied: np.ndarray | None = None,
    gap_voxels: int = 0,
    level_shift: float = 0.0,
    tol: float = 0.005,
    max_iter: int = 40,
) -> tuple[np.ndarray, float, float]:
    forbidden = None
    if occupied is not None and np.any(occupied):
        forbidden = occupied.copy()
        if gap_voxels > 0:
            forbidden = binary_dilation(forbidden, iterations=int(gap_voxels))
    total = F.size

    def vf_at(half_band: float) -> tuple[float, np.ndarray]:
        component_mask = _raw_mask_from_band(F, mode, half_band, level_shift)
        if forbidden is not None:
            component_mask = component_mask & ~forbidden
        return float(component_mask.sum()) / total, component_mask

    low, high = 0.0, float(np.abs(F - level_shift).max()) + 1e-6
    best_mask: np.ndarray | None = None
    best_vf, best_band = 0.0, high
    for _ in range(max_iter):
        middle = 0.5 * (low + high)
        vf, component_mask = vf_at(middle)
        best_mask, best_vf, best_band = component_mask, vf, middle
        if abs(vf - target_vf) <= tol:
            break
        if vf < target_vf:
            low = middle
        else:
            high = middle
    if best_mask is None:
        raise TPMSGeneratorError("target-VF bisection failed to produce a mask")
    return best_mask, best_vf, best_band


def generate_tpms_mask(candidate: MultiwallCandidate) -> np.ndarray:
    params = candidate.to_source_params()
    config = candidate.config
    rng = np.random.default_rng(candidate.random_seed)
    voxel_size_mm = config.size_mm / config.grid_n
    gap_voxels = int(round(config.component_gap_mm / voxel_size_mm))
    X, Y, Z = make_tpms_grid(
        n=config.grid_n,
        size_mm=config.size_mm,
        frequency=config.frequency,
        anisotropy=config.anisotropy_xyz,
    )
    occupied = np.zeros((config.grid_n, config.grid_n, config.grid_n), dtype=bool)
    components = params["components"]
    for component_index, component in enumerate(components):
        field = tpms_field(str(component["tpms_type"]), X, Y, Z)
        if config.noise_amp > 0:
            field = field + config.noise_amp * rng.normal(size=field.shape)
            field = (field - np.mean(field)) / (np.std(field) + 1e-12)
        cumulative_target = candidate.target_vf * (component_index + 1) / len(components)
        remaining = max(cumulative_target - estimate_mask_vf(occupied), 0.0)
        if remaining <= 0:
            continue
        component_mask, _, _ = make_mask_for_target_vf(
            field,
            mode=str(component["mode"]),
            target_vf=remaining,
            occupied=occupied,
            gap_voxels=gap_voxels,
            level_shift=float(component.get("level_shift", 0.0)),
            tol=0.005,
        )
        occupied |= component_mask
    if config.min_hole_size_vox > 1:
        occupied = enforce_min_hole_size(occupied, config.min_hole_size_vox)
    actual = estimate_mask_vf(occupied)
    if actual > candidate.target_vf + config.vf_tolerance:
        current = occupied.copy()
        island_reference = count_connected_components(current)
        for _ in range(4):
            if estimate_mask_vf(current) <= candidate.target_vf + config.vf_tolerance:
                break
            eroded = binary_erosion(current, iterations=1)
            if not np.any(eroded) or count_connected_components(eroded) > island_reference:
                break
            current = eroded
        occupied = current
    elif actual < candidate.target_vf - config.vf_tolerance:
        current = occupied.copy()
        for _ in range(4):
            current_vf = estimate_mask_vf(current)
            if current_vf >= candidate.target_vf - config.vf_tolerance:
                break
            add_count = int(round((candidate.target_vf - current_vf) * current.size))
            dilated = binary_dilation(current, iterations=1)
            candidates = np.flatnonzero((dilated & ~current).ravel())
            if len(candidates) == 0:
                break
            add_count = min(add_count, len(candidates))
            add_indices = rng.choice(candidates, size=add_count, replace=False)
            flat = current.ravel()
            flat[add_indices] = True
            current = flat.reshape(current.shape)
        occupied = current
    return occupied


def check_thickness_consistency(candidate: MultiwallCandidate, max_deviation_ratio: float = 1.5) -> bool:
    values = [component.thickness_mm for component in candidate.components]
    minimum, maximum = min(values), max(values)
    return minimum > 0 and (maximum - minimum) / minimum <= max_deviation_ratio


def check_open_cell(mask: np.ndarray) -> bool:
    void = ~np.asarray(mask, dtype=bool)
    labels, count = label(void)
    if count == 0:
        return True
    for component_id in range(1, count + 1):
        component = labels == component_id
        touches = (
            component[0, :, :].any()
            or component[-1, :, :].any()
            or component[:, 0, :].any()
            or component[:, -1, :].any()
            or component[:, :, 0].any()
            or component[:, :, -1].any()
        )
        if not touches:
            return False
    return True


def mesh_from_binary_mask(
    mask: np.ndarray, size_mm: float, marching_cubes_step_size: int
) -> tuple[np.ndarray, np.ndarray]:
    binary = np.asarray(mask, dtype=bool)
    if np.count_nonzero(binary) == 0:
        return np.empty((0, 3), dtype=np.float32), np.empty((0, 3), dtype=np.int32)
    padded = np.pad(binary.astype(np.float32), pad_width=1, mode="constant", constant_values=0)
    spacing = tuple(size_mm / binary.shape[index] for index in range(3))
    vertices, faces, _, _ = measure.marching_cubes(
        padded,
        level=0.5,
        spacing=spacing,
        step_size=max(1, int(marching_cubes_step_size)),
        allow_degenerate=False,
    )
    vertices -= np.array(spacing)
    vertices = np.clip(vertices, 0.0, size_mm)
    return vertices.astype(np.float32), faces.astype(np.int32)


def generate_tpms_candidate(candidate: MultiwallCandidate) -> TPMSGenerationResult:
    mask = generate_tpms_mask(candidate)
    before = count_connected_components(mask)
    if before > candidate.config.max_islands_before_skip_repair:
        raise TPMSGeneratorError(f"not_printable: too_many_islands_skipped_repair (islands={before})")
    repaired, repair_info = repair_mask_connectivity(
        mask,
        mode="bridge",
        bridge_radius_vox=candidate.config.connectivity_bridge_radius_vox,
        min_component_voxels=candidate.config.connectivity_min_component_voxels,
        max_bridges=candidate.config.connectivity_max_bridges,
    )
    reasons = []
    if not (0.10 <= candidate.target_vf <= 0.80):
        reasons.append("vf_out_of_range")
    if not check_thickness_consistency(candidate):
        reasons.append("thickness_deviation_too_large")
    if count_connected_components(repaired) > 1:
        reasons.append("island_detected")
    # Source Cell 4 explicitly comments out closed-cell rejection. The result is
    # measured and recorded but deliberately not appended to rejection reasons.
    open_cell = check_open_cell(repaired)
    if reasons:
        raise TPMSGeneratorError(f"not_printable: {reasons}")
    vertices, faces = mesh_from_binary_mask(
        repaired, candidate.config.size_mm, candidate.config.marching_cubes_step_size
    )
    quick = {
        "actual_vf_est": estimate_mask_vf(repaired),
        "voxel_grid_n": int(repaired.shape[0]),
        "component_count": len(candidate.components),
        "component_modes": "+".join(component.mode for component in candidate.components),
        "component_tpms_types": "+".join(component.tpms_type for component in candidate.components),
        "component_thicknesses_mm": json.dumps(
            [round(component.thickness_mm, 3) for component in candidate.components],
            ensure_ascii=False,
            sort_keys=True,
        ),
        "multiwall_combo": candidate.combo_name,
        "min_hole_size_vox": int(candidate.config.min_hole_size_vox),
        "compute_backend": "cpu",
        "islands_before_repair": before,
    }
    return TPMSGenerationResult(
        candidate=candidate,
        mask=repaired,
        vertices=vertices,
        faces=faces,
        quick_descriptor=quick,
        connectivity_info=repair_info,
        open_cell_pass=open_cell,
    )

