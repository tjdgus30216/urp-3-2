"""Traceable imported-STL z-slicing using signed non-zero winding.

The implementation is the production-shaped extraction of the frozen
``ORIENTED_NONZERO_RAW`` candidate validated by IMSTL-004.  It preserves raw
triangle multiplicity and orientation.  It does not deduplicate faces, fill
holes, bridge gaps, dilate masks, mutate source geometry, or inspect a paired
STEP while constructing a mask.  When requested, a uniform analysis-space
normalization is derived from the STL bbox alone and recorded explicitly.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import numpy as np

from urp4.contracts.v0_1.canonical import sha256_file
from urp4.descriptor_service.v0_1.geometry import geometry_bounds, load_binary_stl_vertices


@dataclass(frozen=True)
class ImportedSTLWindingConfig:
    """Frozen route settings.

    Only z slicing is qualified.  Other axes must receive their own validation
    rather than silently reusing this contract.
    """

    pixel_resolution: int = 1000
    slice_count: int = 801
    expected_size_mm: float = 40.0
    size_tolerance_mm: float = 1.0e-3
    normalization_mode: str = "uniform_bbox_to_expected"
    isotropic_extent_tolerance_mm: float = 1.0e-3
    axis: str = "z"
    route_id: str = "IMP-STL-ORIENTED-NONZERO-SCREENING-L28"
    algorithm_revision: str = "ORIENTED_NONZERO_RAW/IMSTL-004/r1"

    def __post_init__(self) -> None:
        if self.pixel_resolution < 2:
            raise ValueError("pixel_resolution must be >= 2")
        if self.slice_count < 2:
            raise ValueError("slice_count must be >= 2")
        if not np.isfinite(self.expected_size_mm) or self.expected_size_mm <= 0:
            raise ValueError("expected_size_mm must be positive")
        if self.axis.lower() != "z":
            raise ValueError("v0.4 is qualified for z slicing only")
        if self.normalization_mode not in {"require_expected_size", "uniform_bbox_to_expected"}:
            raise ValueError("unsupported normalization_mode")

    @classmethod
    def from_values(cls, **values: object) -> "ImportedSTLWindingConfig":
        return cls(**values)


def load_imported_stl_triangles(
    path: str | Path,
    config: ImportedSTLWindingConfig,
    *,
    expected_sha256: str | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, str, dict[str, object]]:
    """Load immutable binary STL triangles and fail closed on scale/hash drift."""

    source = Path(path).resolve()
    source_hash = sha256_file(source)
    if expected_sha256 and source_hash.lower() != str(expected_sha256).lower():
        raise ValueError(f"imported STL hash mismatch: {source}")
    triangles = load_binary_stl_vertices(source, expected_sha256=source_hash)
    lower, upper = geometry_bounds(triangles)
    extents = upper - lower
    if np.all(np.abs(extents - config.expected_size_mm) <= config.size_tolerance_mm):
        analysis = triangles
        analysis_lower, analysis_upper = lower, upper
        scale = 1.0
        center = (lower + upper) / 2.0
        normalization_status = "already_expected_size"
    elif config.normalization_mode == "uniform_bbox_to_expected":
        if float(np.max(extents) - np.min(extents)) > config.isotropic_extent_tolerance_mm:
            raise ValueError(f"non-isotropic bbox cannot use uniform normalization: {extents.tolist()}")
        center = (lower + upper) / 2.0
        scale = float(config.expected_size_mm / np.max(extents))
        analysis = (triangles - center) * scale + config.expected_size_mm / 2.0
        analysis_lower, analysis_upper = geometry_bounds(analysis)
        normalization_status = "uniform_bbox_normalized_in_memory"
    else:
        raise ValueError(
            f"imported STL extent mismatch: expected={config.expected_size_mm}, actual={extents.tolist()}"
        )
    normalization = {
        "normalization_status": normalization_status,
        "normalization_mode": config.normalization_mode,
        "source_bbox_center_mm": center.tolist(),
        "source_bbox_extent_mm": extents.tolist(),
        "analysis_uniform_scale": scale,
        "analysis_bbox_extent_mm": (analysis_upper - analysis_lower).tolist(),
    }
    return analysis, analysis_lower, analysis_upper, source_hash, normalization


def oriented_section_z(
    triangles: np.ndarray,
    z_mm: float,
) -> tuple[np.ndarray, dict[str, int]]:
    """Intersect oriented triangles with a half-open z plane."""

    tri = np.asarray(triangles, dtype=np.float64)
    if tri.ndim != 3 or tri.shape[1:] != (3, 3):
        raise ValueError(f"triangles must have shape (n,3,3), got {tri.shape}")
    p1 = tri[:, [0, 1, 2], :]
    p2 = tri[:, [1, 2, 0], :]
    z1, z2 = p1[:, :, 2], p2[:, :, 2]
    active = ((z1 <= z_mm) & (z_mm < z2)) | ((z2 <= z_mm) & (z_mm < z1))
    denom = z2 - z1
    safe = active & (np.abs(denom) > 1.0e-9)
    t = np.zeros_like(denom)
    t[safe] = (z_mm - z1[safe]) / denom[safe]
    hit = p1 + t[:, :, None] * (p2 - p1)
    triangle_ids = np.nonzero(safe.sum(axis=1) == 2)[0]
    normals = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    target = np.column_stack((-normals[:, 1], normals[:, 0]))
    segments: list[list[float]] = []
    reversed_count = 0
    for triangle_id in triangle_ids.tolist():
        pair = hit[triangle_id, safe[triangle_id], :2]
        if len(pair) != 2 or np.sum((pair[0] - pair[1]) ** 2) <= 1.0e-18:
            continue
        if np.dot(pair[1] - pair[0], target[triangle_id]) < 0:
            pair = pair[::-1]
            reversed_count += 1
        segments.append([*pair[0], *pair[1]])
    array = np.asarray(segments, dtype=np.float64)
    if array.size == 0:
        array = np.empty((0, 4), dtype=np.float64)
    return array, {
        "triangle_count": int(len(tri)),
        "intersected_triangle_count": int(len(triangle_ids)),
        "segment_count": int(len(array)),
        "orientation_reversed_segment_count": int(reversed_count),
    }


def active_triangle_subsets_z(
    triangles: np.ndarray,
    z_values: np.ndarray,
) -> Iterator[tuple[float, np.ndarray]]:
    """Yield exact half-open z-active triangle subsets in one sorted sweep.

    This changes only computational cost.  A triangle is active when
    ``min_z <= z < max_z``, exactly matching ``oriented_section_z``.
    """

    tri = np.asarray(triangles, dtype=np.float64)
    lower = np.min(tri[:, :, 2], axis=1)
    upper = np.max(tri[:, :, 2], axis=1)
    lower_order = np.argsort(lower, kind="stable")
    upper_order = np.argsort(upper, kind="stable")
    active: set[int] = set()
    add_cursor = 0
    remove_cursor = 0
    for z_mm in np.asarray(z_values, dtype=float).tolist():
        while add_cursor < len(tri) and lower[lower_order[add_cursor]] <= z_mm:
            active.add(int(lower_order[add_cursor]))
            add_cursor += 1
        while remove_cursor < len(tri) and upper[upper_order[remove_cursor]] <= z_mm:
            active.discard(int(upper_order[remove_cursor]))
            remove_cursor += 1
        ids = np.fromiter(active, dtype=np.int64, count=len(active))
        yield float(z_mm), tri[ids]


def winding_raster(
    segments: np.ndarray,
    *,
    lower_xy: np.ndarray,
    upper_xy: np.ndarray,
    pixels: int,
) -> tuple[np.ndarray, dict[str, int]]:
    """Rasterize material where signed winding is non-zero."""

    mask = np.zeros((pixels, pixels), dtype=bool)
    empty = {
        "nonzero_row_count": 0,
        "max_abs_winding": 0,
        "coincident_crossing_group_count": 0,
    }
    seg = np.asarray(segments, dtype=np.float64)
    if len(seg) == 0:
        return mask, empty
    xmin, ymin = np.asarray(lower_xy, dtype=float)
    xmax, ymax = np.asarray(upper_xy, dtype=float)
    dx = (xmax - xmin) / pixels
    dy = (ymax - ymin) / pixels
    if not np.isfinite(dx) or not np.isfinite(dy) or dx <= 0 or dy <= 0:
        raise ValueError("invalid raster bounds")
    if not np.isclose(dx, dy, rtol=0, atol=1.0e-12):
        raise ValueError("v0.4 requires square physical pixels")

    x1, y1, x2, y2 = seg.T
    keep = np.abs(y2 - y1) > 1.0e-12
    if not np.any(keep):
        return mask, empty
    x1, y1, x2, y2 = x1[keep], y1[keep], x2[keep], y2[keep]
    lo, hi = np.minimum(y1, y2), np.maximum(y1, y2)
    start = np.floor((ymax - hi) / dy - 0.5).astype(int) + 1
    end = np.floor((ymax - lo) / dy - 0.5).astype(int)
    start = np.clip(start, 0, pixels - 1)
    end = np.clip(end, -1, pixels - 1)
    counts = np.maximum(0, end - start + 1)
    valid = counts > 0
    if not np.any(valid):
        return mask, empty
    start, counts = start[valid], counts[valid]
    x1, y1, x2, y2 = x1[valid], y1[valid], x2[valid], y2[valid]
    offsets = np.repeat(np.cumsum(counts) - counts, counts)
    rows = np.repeat(start, counts) + (np.arange(int(counts.sum())) - offsets)
    segment_index = np.repeat(np.arange(len(counts)), counts)
    yy = ymax - (rows + 0.5) * dy
    xs = x1[segment_index] + (yy - y1[segment_index]) * (
        x2[segment_index] - x1[segment_index]
    ) / (y2[segment_index] - y1[segment_index])
    delta = np.where(y2[segment_index] > y1[segment_index], 1, -1)
    order = np.lexsort((xs, rows))
    rows, xs, delta = rows[order], xs[order], delta[order]
    starts = np.r_[0, np.flatnonzero(np.diff(rows)) + 1]
    stops = np.r_[starts[1:], len(rows)]
    max_winding = 0
    coincident = 0
    nonzero_rows = 0
    for a, b in zip(starts.tolist(), stops.tolist(), strict=True):
        row = int(rows[a])
        xv, dv = xs[a:b], delta[a:b]
        cuts = np.r_[0, np.flatnonzero(np.abs(np.diff(xv)) > 1.0e-9) + 1]
        ends = np.r_[cuts[1:], len(xv)]
        gx = np.asarray([float(np.mean(xv[u:v])) for u, v in zip(cuts, ends, strict=True)])
        gd = np.asarray([int(np.sum(dv[u:v])) for u, v in zip(cuts, ends, strict=True)])
        coincident += int(sum((v - u) > 1 for u, v in zip(cuts, ends, strict=True)))
        winding = 0
        row_nonzero = False
        for j in range(len(gx) - 1):
            winding += int(gd[j])
            max_winding = max(max_winding, abs(winding))
            if winding == 0 or gx[j + 1] <= gx[j]:
                continue
            c0 = max(0, min(pixels - 1, int(math.ceil((gx[j] - xmin) / dx - 0.5))))
            c1 = max(0, min(pixels - 1, int(math.floor((gx[j + 1] - xmin) / dx - 0.5))))
            if c1 >= c0:
                mask[row, c0 : c1 + 1] = True
                row_nonzero = True
        nonzero_rows += int(row_nonzero)
    return mask, {
        "nonzero_row_count": int(nonzero_rows),
        "max_abs_winding": int(max_winding),
        "coincident_crossing_group_count": int(coincident),
    }


def imported_stl_mask_stream(
    path: str | Path,
    config: ImportedSTLWindingConfig,
    *,
    expected_sha256: str | None = None,
    slice_indices: set[int] | None = None,
) -> Iterator[dict[str, object]]:
    """Yield one transient mask and its complete lineage at a time."""

    triangles, lower, upper, source_hash, normalization = load_imported_stl_triangles(
        path, config, expected_sha256=expected_sha256
    )
    z_values = np.linspace(lower[2], upper[2], config.slice_count)
    z_values[0] = np.nextafter(lower[2], upper[2])
    z_values[-1] = np.nextafter(upper[2], lower[2])
    for slice_index, (z_mm, active_triangles) in enumerate(active_triangle_subsets_z(triangles, z_values)):
        if slice_indices is not None and slice_index not in slice_indices:
            continue
        segments, section_diag = oriented_section_z(active_triangles, float(z_mm))
        section_diag["source_triangle_count"] = int(len(triangles))
        section_diag["z_active_triangle_count"] = int(len(active_triangles))
        mask, raster_diag = winding_raster(
            segments,
            lower_xy=lower[:2],
            upper_xy=upper[:2],
            pixels=config.pixel_resolution,
        )
        yield {
            "slice_index": int(slice_index),
            "z_mm": float(z_mm),
            "endpoint_adjusted": bool(slice_index in (0, config.slice_count - 1)),
            "mask": mask,
            "mask_packedbits_sha256": mask_packedbits_sha256(mask),
            "source_geometry_sha256": source_hash,
            "route_id": config.route_id,
            "algorithm_revision": config.algorithm_revision,
            **normalization,
            **section_diag,
            **raster_diag,
        }


def mask_packedbits_sha256(mask: np.ndarray) -> str:
    return hashlib.sha256(np.packbits(np.asarray(mask, dtype=np.uint8), axis=None).tobytes()).hexdigest()
