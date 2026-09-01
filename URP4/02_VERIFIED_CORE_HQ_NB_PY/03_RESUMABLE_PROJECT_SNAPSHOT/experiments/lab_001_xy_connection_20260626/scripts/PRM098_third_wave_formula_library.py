from __future__ import annotations

import math
import time
from dataclasses import dataclass

import networkx as nx
import numpy as np
from scipy import ndimage as ndi
from scipy.special import eval_legendre, sph_harm_y
from skimage.measure import euler_number, marching_cubes
from skimage.morphology import skeletonize


GROUPS = ["LIT-X006", "LIT-X008", "LIT-X019", "LIT-X024", "LIT-X028", "LIT-X031"]
OFFSETS_26 = [(i, j, k) for i in (-1, 0, 1) for j in (-1, 0, 1) for k in (-1, 0, 1) if (i, j, k) != (0, 0, 0)]
ECT_DIRECTION_TUPLES = OFFSETS_26.copy()
ECT_DIRECTIONS = [np.asarray(v, dtype=float) / np.linalg.norm(v) for v in ECT_DIRECTION_TUPLES]


class ResourceStop(RuntimeError):
    pass


@dataclass
class GroupResult:
    outputs: dict[str, float]
    artifacts: dict[str, np.ndarray]
    diagnostics: dict[str, float | int | str]


def _step(a: tuple[int, int, int], b: tuple[int, int, int], pitch: float) -> tuple[float, float]:
    d = np.subtract(b, a)
    return pitch * float(np.linalg.norm(d)), pitch * abs(int(d[2]))


def _neighbors(coord: tuple[int, int, int], shape: tuple[int, int, int]):
    for off in OFFSETS_26:
        q = (coord[0] + off[0], coord[1] + off[1], coord[2] + off[2])
        if 0 <= q[0] < shape[0] and 0 <= q[1] < shape[1] and 0 <= q[2] < shape[2]:
            yield q


def skeleton_graph_outputs(volume: np.ndarray, pitch: float) -> GroupResult:
    volume = np.asarray(volume, dtype=bool)
    skel = np.asarray(skeletonize(volume, method="lee"), dtype=bool)
    kernel = np.ones((3, 3, 3), dtype=np.uint8); kernel[1, 1, 1] = 0
    degree_field = ndi.convolve(skel.astype(np.uint8), kernel, mode="constant", cval=0)
    node_mask = skel & (degree_field != 2)
    node_labels, node_count = ndi.label(node_mask, structure=np.ones((3, 3, 3), dtype=np.uint8))
    graph = nx.MultiGraph()
    graph.add_nodes_from(range(1, node_count + 1))
    edges: list[tuple[int, int, float, float]] = []
    visited_links: set[tuple[tuple[int, int, int], tuple[int, int, int]]] = set()

    def link_key(a, b):
        return (a, b) if a < b else (b, a)

    for node_id in range(1, node_count + 1):
        for raw in np.argwhere(node_labels == node_id):
            start = tuple(map(int, raw))
            for nxt in _neighbors(start, skel.shape):
                if not skel[nxt] or node_labels[nxt] == node_id:
                    continue
                first_key = link_key(start, nxt)
                if first_key in visited_links:
                    continue
                prev, cur = start, nxt
                length, znum = _step(prev, cur, pitch)
                visited_links.add(first_key)
                end_node = int(node_labels[cur])
                guard = 0
                while end_node == 0:
                    options = [q for q in _neighbors(cur, skel.shape) if skel[q] and q != prev]
                    if len(options) != 1:
                        raise RuntimeError(f"degree-two chain violated at {cur}: {len(options)} continuations")
                    follow = options[0]
                    key = link_key(cur, follow)
                    if key in visited_links and follow != start:
                        raise RuntimeError("unexpected previously visited skeleton link")
                    dl, dz = _step(cur, follow, pitch)
                    length += dl; znum += dz; visited_links.add(key)
                    prev, cur = cur, follow
                    end_node = int(node_labels[cur])
                    guard += 1
                    if guard > int(skel.sum()) + 1:
                        raise RuntimeError("skeleton chain trace guard exceeded")
                graph.add_edge(node_id, end_node, length_mm=length, z_numerator_mm=znum)
                edges.append((node_id, end_node, length, znum))

    # Any skeleton connected component with no degree!=2 voxel is a pure loop.
    skel_labels, skel_components = ndi.label(skel, structure=np.ones((3, 3, 3), dtype=np.uint8))
    next_node = node_count + 1
    for comp in range(1, skel_components + 1):
        comp_mask = skel_labels == comp
        if np.any(node_mask & comp_mask):
            continue
        coords = [tuple(map(int, x)) for x in np.argwhere(comp_mask)]
        if not coords:
            continue
        anchor = min(coords)
        graph.add_node(next_node, pure_loop_anchor=anchor)
        length = znum = 0.0
        seen = set()
        for a in coords:
            for b in _neighbors(a, skel.shape):
                if not comp_mask[b]:
                    continue
                key = link_key(a, b)
                if key in seen:
                    continue
                seen.add(key)
                dl, dz = _step(a, b, pitch); length += dl; znum += dz
        graph.add_edge(next_node, next_node, length_mm=length, z_numerator_mm=znum)
        edges.append((next_node, next_node, length, znum))
        next_node += 1

    nodes = graph.number_of_nodes(); edge_count = graph.number_of_edges()
    components = nx.number_connected_components(graph) if nodes else 0
    degrees = np.asarray([d for _, d in graph.degree()], dtype=float)
    lengths = np.asarray([e[2] for e in edges], dtype=float)
    total_length = float(lengths.sum()) if len(lengths) else 0.0
    znum_total = float(sum(e[3] for e in edges))
    degree_map = dict(graph.degree())
    dangling = sum(1 for u, v, *_ in edges if degree_map.get(u, 0) == 1 or degree_map.get(v, 0) == 1)
    cycle_rank = edge_count - nodes + components
    prefix = "LIT-X006::"
    out = {
        prefix + "component_count": float(components),
        prefix + "node_count": float(nodes),
        prefix + "edge_count": float(edge_count),
        prefix + "endpoint_fraction": float(np.mean(degrees == 1)) if nodes else math.nan,
        prefix + "branchpoint_fraction": float(np.mean(degrees >= 3)) if nodes else math.nan,
        prefix + "mean_node_degree": float(np.mean(degrees)) if nodes else math.nan,
        prefix + "population_std_node_degree": float(np.std(degrees, ddof=0)) if nodes else math.nan,
        prefix + "cycle_rank": float(cycle_rank),
        prefix + "cycle_rank_density_per_mm3": float(cycle_rank / 64000.0),
        prefix + "total_edge_length_mm": total_length,
        prefix + "edge_length_q50_mm": float(np.quantile(lengths, 0.5)) if len(lengths) else math.nan,
        prefix + "edge_length_q90_mm": float(np.quantile(lengths, 0.9)) if len(lengths) else math.nan,
        prefix + "z_alignment_abs_cos_mean": znum_total / total_length if total_length > 0 else math.nan,
        prefix + "dangling_edge_fraction": dangling / edge_count if edge_count else math.nan,
    }
    return GroupResult(out, {"skeleton": skel.astype(np.uint8)}, {"skeleton_voxels": int(skel.sum()), "node_voxel_clusters": int(node_count), "pure_loop_components": int(next_node - node_count - 1)})


def local_thickness_field(volume: np.ndarray, pitch: float, max_seconds: float | None = None) -> tuple[np.ndarray, dict[str, int | float]]:
    start = time.perf_counter()
    padded = np.pad(np.asarray(volume, dtype=bool), 1, constant_values=False)
    if not padded.any():
        return np.full(volume.shape, np.nan), {"unique_radius_levels": 0, "assigned": 0}
    edt = ndi.distance_transform_edt(padded)
    radius_sq = np.rint(edt * edt).astype(np.int32)
    levels = sorted(np.unique(radius_sq[padded]).tolist(), reverse=True)
    lt = np.zeros(padded.shape, dtype=np.float32)
    unassigned = padded.copy()
    for level in levels:
        if max_seconds is not None and time.perf_counter() - start > max_seconds:
            raise ResourceStop(f"local-thickness deadline exceeded after {len(levels)-levels.index(level)} levels")
        centers = padded & (radius_sq == level)
        distance_to_level = ndi.distance_transform_edt(~centers)
        covered = unassigned & (distance_to_level <= math.sqrt(level) + 1e-12)
        lt[covered] = 2.0 * math.sqrt(level) * pitch
        unassigned[covered] = False
        if not unassigned.any():
            break
    if np.any(unassigned):
        raise RuntimeError(f"local thickness left {int(unassigned.sum())} solid voxels unassigned")
    cropped = lt[1:-1, 1:-1, 1:-1]
    return cropped, {"unique_radius_levels": len(levels), "assigned": int(volume.sum()), "elapsed_internal_s": time.perf_counter() - start}


def local_thickness_outputs(volume: np.ndarray, pitch: float, max_seconds: float | None = None) -> GroupResult:
    field, diag = local_thickness_field(volume, pitch, max_seconds=max_seconds)
    values = field[np.asarray(volume, dtype=bool)]
    if not len(values):
        values = np.asarray([math.nan])
    q10, q50, q90 = np.quantile(values, [0.1, 0.5, 0.9]) if np.isfinite(values).any() else (math.nan, math.nan, math.nan)
    mean = float(np.mean(values)); std = float(np.std(values, ddof=0))
    cv = std / mean if mean > 1e-12 else math.nan
    bottleneck = float(q10 / q50) if q50 > 1e-12 else math.nan
    p = "LIT-X008::"
    out = {
        p + "local_thickness_mean_mm": mean,
        p + "local_thickness_population_std_mm": std,
        p + "local_thickness_q10_mm": float(q10),
        p + "local_thickness_q50_mm": float(q50),
        p + "local_thickness_q90_mm": float(q90),
        p + "local_thickness_cv": cv,
        p + "bottleneck_q10_over_q50": bottleneck,
        p + "constriction_index_one_minus_q10_q50": 1.0 - bottleneck if math.isfinite(bottleneck) else math.nan,
    }
    return GroupResult(out, {}, diag)


def _line_runs(line: np.ndarray) -> np.ndarray:
    padded = np.concatenate(([False], np.asarray(line, dtype=bool), [False])).astype(np.int8)
    delta = np.diff(padded)
    return np.flatnonzero(delta == -1) - np.flatnonzero(delta == 1)


def _run_stats(volume: np.ndarray, axis: int) -> tuple[float, float]:
    moved = np.moveaxis(volume, axis, -1)
    runs = []
    for line in moved.reshape(-1, moved.shape[-1]):
        current = _line_runs(line)
        if current.size:
            runs.extend(current.tolist())
    if not runs:
        return math.nan, math.nan
    a = np.asarray(runs, dtype=float)
    return float(a.mean()), float(np.quantile(a, 0.5))


def phase_scale_outputs(volume: np.ndarray, pitch: float) -> GroupResult:
    del pitch  # Ratios are invariant because numerator and denominator share the current-resolution pitch.
    ratios = {}
    q50s = []
    p = "LIT-X019::"
    for axis, name in enumerate("xyz"):
        solid = _run_stats(volume, axis)
        void = _run_stats(~np.asarray(volume, dtype=bool), axis)
        for index, stat in enumerate(["mean", "q50"]):
            value = solid[index] / void[index] if math.isfinite(void[index]) and void[index] > 1e-12 else math.nan
            ratios[p + f"solid_void_chord_{name}_{stat}_ratio"] = value
            if stat == "q50": q50s.append(value)
    ratios[p + "solid_void_chord_q50_geomean_ratio"] = float(math.exp(np.mean(np.log(q50s)))) if len(q50s) == 3 and all(math.isfinite(x) and x > 0 for x in q50s) else math.nan
    return GroupResult(ratios, {}, {"parent_rule": "same current-resolution mask/axis/stat"})


def ect_outputs_skimage_reference(volume: np.ndarray, pitch: float, heights: int = 129, max_seconds: float | None = None) -> GroupResult:
    start = time.perf_counter()
    volume = np.asarray(volume, dtype=bool)
    n = volume.shape[0]
    centers = (np.arange(n, dtype=np.float64) + 0.5) * pitch
    t = np.linspace(0.0, 1.0, heights)
    curves = np.zeros((26, heights), dtype=np.float64)
    for di, (raw, direction) in enumerate(zip(ECT_DIRECTION_TUPLES, ECT_DIRECTIONS)):
        projection = direction[0] * centers[:, None, None] + direction[1] * centers[None, :, None] + direction[2] * centers[None, None, :]
        hmin = sum(min(0.0, 40.0 * float(x)) for x in direction)
        hmax = sum(max(0.0, 40.0 * float(x)) for x in direction)
        for hi, threshold in enumerate(hmin + t * (hmax - hmin)):
            if max_seconds is not None and time.perf_counter() - start > max_seconds:
                raise ResourceStop(f"ECT deadline exceeded at direction={raw}, height={hi}")
            sublevel = volume & (projection <= threshold + 1e-12)
            curves[di, hi] = float(euler_number(sublevel, connectivity=3)) / 64000.0 if sublevel.any() else 0.0
    auc = np.trapezoid(np.abs(curves), x=t, axis=1)
    tv = np.abs(np.diff(curves, axis=1)).sum(axis=1)
    lookup = {v: i for i, v in enumerate(ECT_DIRECTION_TUPLES)}
    pair_l1 = []
    used = set()
    for raw in ECT_DIRECTION_TUPLES:
        if raw in used: continue
        neg = tuple(-x for x in raw); used.add(raw); used.add(neg)
        pair_l1.append(float(np.mean(np.abs(curves[lookup[raw]] - curves[lookup[neg]]))))
    p = "LIT-X024::"
    out = {
        p + "ect_abs_auc_direction_mean_per_mm3": float(np.mean(auc)),
        p + "ect_abs_auc_direction_std_per_mm3": float(np.std(auc, ddof=0)),
        p + "ect_total_variation_direction_mean_per_mm3": float(np.mean(tv)),
        p + "ect_total_variation_direction_std_per_mm3": float(np.std(tv, ddof=0)),
        p + "ect_antipodal_l1_mean_per_mm3": float(np.mean(pair_l1)),
        p + "ect_final_chi_solid_density_trace_per_mm3": float(np.mean(curves[:, -1])),
    }
    return GroupResult(out, {"ECT_curve_26x129": curves}, {"directions": 26, "heights": heights, "elapsed_internal_s": time.perf_counter() - start})


def _cell_birth_count(cube_birth: np.ndarray, target_shape: tuple[int, int, int], offsets: list[tuple[int, int, int]], thresholds: np.ndarray) -> np.ndarray:
    n = cube_birth.shape[0]
    births = np.full(target_shape, np.inf, dtype=np.float64)
    for di, dj, dk in offsets:
        view = births[di:di+n, dj:dj+n, dk:dk+n]
        np.minimum(view, cube_birth, out=view)
    finite = births[np.isfinite(births)]
    finite.sort()
    return np.searchsorted(finite, thresholds, side="right")


def _cubical_euler_curve(volume: np.ndarray, projection: np.ndarray, thresholds: np.ndarray) -> np.ndarray:
    """Euler characteristic of the closed voxel cubical complex at every threshold."""
    n = volume.shape[0]
    cube_birth = np.where(volume, projection, np.inf)
    inclusive = thresholds + 1e-12
    cubes = np.searchsorted(np.sort(cube_birth[np.isfinite(cube_birth)]), inclusive, side="right")
    vertices = _cell_birth_count(cube_birth, (n+1, n+1, n+1), [(i,j,k) for i in (0,1) for j in (0,1) for k in (0,1)], inclusive)
    edge_x = _cell_birth_count(cube_birth, (n, n+1, n+1), [(0,j,k) for j in (0,1) for k in (0,1)], inclusive)
    edge_y = _cell_birth_count(cube_birth, (n+1, n, n+1), [(i,0,k) for i in (0,1) for k in (0,1)], inclusive)
    edge_z = _cell_birth_count(cube_birth, (n+1, n+1, n), [(i,j,0) for i in (0,1) for j in (0,1)], inclusive)
    face_x = _cell_birth_count(cube_birth, (n+1, n, n), [(0,0,0),(1,0,0)], inclusive)
    face_y = _cell_birth_count(cube_birth, (n, n+1, n), [(0,0,0),(0,1,0)], inclusive)
    face_z = _cell_birth_count(cube_birth, (n, n, n+1), [(0,0,0),(0,0,1)], inclusive)
    return vertices - edge_x - edge_y - edge_z + face_x + face_y + face_z - cubes


def ect_outputs(volume: np.ndarray, pitch: float, heights: int = 129, max_seconds: float | None = None) -> GroupResult:
    start = time.perf_counter()
    volume = np.asarray(volume, dtype=bool)
    n = volume.shape[0]
    centers = (np.arange(n, dtype=np.float64) + 0.5) * pitch
    t = np.linspace(0.0, 1.0, heights)
    curves = np.zeros((26, heights), dtype=np.float64)
    for di, (raw, direction) in enumerate(zip(ECT_DIRECTION_TUPLES, ECT_DIRECTIONS)):
        if max_seconds is not None and time.perf_counter() - start > max_seconds:
            raise ResourceStop(f"ECT deadline exceeded before direction={raw}")
        projection = direction[0] * centers[:, None, None] + direction[1] * centers[None, :, None] + direction[2] * centers[None, None, :]
        hmin = sum(min(0.0, 40.0 * float(x)) for x in direction)
        hmax = sum(max(0.0, 40.0 * float(x)) for x in direction)
        thresholds = hmin + t * (hmax - hmin)
        curves[di] = _cubical_euler_curve(volume, projection, thresholds) / 64000.0
    auc = np.trapezoid(np.abs(curves), x=t, axis=1)
    tv = np.abs(np.diff(curves, axis=1)).sum(axis=1)
    lookup = {v: i for i, v in enumerate(ECT_DIRECTION_TUPLES)}
    pair_l1=[]; used=set()
    for raw in ECT_DIRECTION_TUPLES:
        if raw in used: continue
        neg=tuple(-x for x in raw); used.add(raw); used.add(neg)
        pair_l1.append(float(np.mean(np.abs(curves[lookup[raw]]-curves[lookup[neg]]))))
    p="LIT-X024::"
    out={
        p+"ect_abs_auc_direction_mean_per_mm3":float(np.mean(auc)),
        p+"ect_abs_auc_direction_std_per_mm3":float(np.std(auc,ddof=0)),
        p+"ect_total_variation_direction_mean_per_mm3":float(np.mean(tv)),
        p+"ect_total_variation_direction_std_per_mm3":float(np.std(tv,ddof=0)),
        p+"ect_antipodal_l1_mean_per_mm3":float(np.mean(pair_l1)),
        p+"ect_final_chi_solid_density_trace_per_mm3":float(np.mean(curves[:,-1])),
    }
    return GroupResult(out,{"ECT_curve_26x129":curves},{"directions":26,"heights":heights,"implementation":"cubical_cell_birth_counts","elapsed_internal_s":time.perf_counter()-start})


def binary_glcm_at_shift(volume: np.ndarray, axis: int, shift: int) -> dict[str, float]:
    if shift <= 0 or shift >= volume.shape[axis]:
        raise ValueError("invalid GLCM shift")
    left = [slice(None)] * 3; right = [slice(None)] * 3
    left[axis] = slice(0, volume.shape[axis] - shift); right[axis] = slice(shift, volume.shape[axis])
    a = np.asarray(volume[tuple(left)], dtype=np.uint8).ravel(); b = np.asarray(volume[tuple(right)], dtype=np.uint8).ravel()
    counts = np.bincount(2 * a + b, minlength=4).reshape(2, 2).astype(float)
    forward = counts / counts.sum(); P = 0.5 * (forward + forward.T)
    contrast = float(P[0, 1] + P[1, 0])
    homogeneity = float(P[0, 0] + P[1, 1] + 0.5 * (P[0, 1] + P[1, 0]))
    nz = P[P > 0]
    return {"P11": float(P[1, 1]), "contrast": contrast, "homogeneity": homogeneity, "asm": float(np.sum(P**2)), "entropy": float(-np.sum(nz * np.log(nz))), "P00": float(P[0, 0]), "P01": float(P[0, 1]), "P10": float(P[1, 0])}


def binary_glcm_outputs(volume: np.ndarray, pitch: float) -> GroupResult:
    out = {}; diagnostics = {}; p = "LIT-X028::"
    for axis, name in enumerate("xyz"):
        for lag in [2.5, 10.0]:
            shift_float = lag / pitch; shift = int(round(shift_float))
            if abs(shift - shift_float) > 1e-12:
                raise ValueError(f"physical lag {lag} mm is not integer at pitch {pitch}")
            values = binary_glcm_at_shift(volume, axis, shift)
            tag = str(lag).replace(".", "p").replace("p0", "") + "mm"
            for metric in ["P11", "contrast", "homogeneity", "asm", "entropy"]:
                out[p + f"binary_glcm_{name}_{tag}_{metric}"] = values[metric]
            diagnostics[f"{name}_{tag}_homogeneity_identity_error"] = abs(values["homogeneity"] - (1 - values["contrast"] / 2))
    return GroupResult(out, {}, diagnostics)


def normal_harmonics_from_normals(normals: np.ndarray, area: np.ndarray) -> dict[str, float]:
    normals = np.asarray(normals, dtype=float); area = np.asarray(area, dtype=float)
    keep = np.isfinite(normals).all(axis=1) & np.isfinite(area) & (area > 0)
    normals = normals[keep]; area = area[keep]
    if not len(area):
        return {f"LIT-X031::surface_normal_{kind}{l}{suffix}": math.nan for l in (2, 4, 6) for kind, suffix in [("H", ""), ("Q", "_z")]}
    normals = normals / np.linalg.norm(normals, axis=1)[:, None]
    weights = area / area.sum()
    theta = np.arccos(np.clip(normals[:, 2], -1.0, 1.0))
    phi = np.mod(np.arctan2(normals[:, 1], normals[:, 0]), 2 * np.pi)
    out = {}
    for l in (2, 4, 6):
        coeff = [np.sum(weights * sph_harm_y(l, m, theta, phi)) for m in range(-l, l + 1)]
        H = (4 * np.pi / (2 * l + 1)) * sum(abs(x) ** 2 for x in coeff)
        Q = np.sum(weights * eval_legendre(l, np.abs(normals[:, 2])))
        out[f"LIT-X031::surface_normal_H{l}"] = float(np.real(H))
        out[f"LIT-X031::surface_normal_Q{l}_z"] = float(Q)
    return out


def surface_normal_harmonic_outputs(volume: np.ndarray, pitch: float) -> GroupResult:
    padded = np.pad(np.asarray(volume, dtype=np.float32), 1, constant_values=0)
    if not np.any(volume):
        return GroupResult(normal_harmonics_from_normals(np.empty((0, 3)), np.empty(0)), {}, {"surface_faces": 0})
    vertices, faces, _, _ = marching_cubes(padded, level=0.5, spacing=(pitch, pitch, pitch), allow_degenerate=False)
    triangles = vertices[faces].astype(np.float64, copy=False)
    cross = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    double_area = np.linalg.norm(cross, axis=1); keep = double_area > 0
    normals = cross[keep] / double_area[keep, None]; area = 0.5 * double_area[keep]
    return GroupResult(normal_harmonics_from_normals(normals, area), {}, {"surface_faces": int(keep.sum()), "surface_area_mm2": float(area.sum())})


def compute_group(group: str, volume: np.ndarray, pitch: float, max_seconds: float | None = None) -> GroupResult:
    if group == "LIT-X006": return skeleton_graph_outputs(volume, pitch)
    if group == "LIT-X008": return local_thickness_outputs(volume, pitch, max_seconds=max_seconds)
    if group == "LIT-X019": return phase_scale_outputs(volume, pitch)
    if group == "LIT-X024": return ect_outputs(volume, pitch, max_seconds=max_seconds)
    if group == "LIT-X028": return binary_glcm_outputs(volume, pitch)
    if group == "LIT-X031": return surface_normal_harmonic_outputs(volume, pitch)
    raise KeyError(group)
