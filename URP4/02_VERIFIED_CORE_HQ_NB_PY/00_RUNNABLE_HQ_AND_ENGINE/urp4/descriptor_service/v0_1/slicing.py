"""Triangle-plane intersection and filled scanline rasterization kernels."""

from __future__ import annotations

import math

import numpy as np


def vectorized_segments(triangles: np.ndarray, z: float, eps: float = 1e-9) -> np.ndarray:
    if triangles.size == 0:
        return np.zeros((0, 4), dtype=np.float64)
    p1 = triangles[:, [0, 1, 2], :]
    p2 = triangles[:, [1, 2, 0], :]
    dz1 = p1[:, :, 2] - z
    dz2 = p2[:, :, 2] - z
    cross = ((dz1 <= 0.0) & (dz2 > 0.0)) | ((dz2 <= 0.0) & (dz1 > 0.0))
    valid = cross.sum(axis=1) == 2
    if not np.any(valid):
        return np.zeros((0, 4), dtype=np.float64)
    p1_valid = p1[valid]
    p2_valid = p2[valid]
    cross_valid = cross[valid]
    denominator = p2_valid[:, :, 2] - p1_valid[:, :, 2]
    fraction = np.zeros_like(denominator, dtype=np.float64)
    np.divide(z - p1_valid[:, :, 2], denominator, out=fraction, where=cross_valid)
    xy = p1_valid[:, :, :2] + fraction[:, :, None] * (p2_valid[:, :, :2] - p1_valid[:, :, :2])
    selected = xy[cross_valid].reshape(-1, 2, 2)
    length_squared = ((selected[:, 0, :] - selected[:, 1, :]) ** 2).sum(axis=1)
    selected = selected[length_squared > eps**2]
    return selected.reshape(-1, 4) if selected.size else np.zeros((0, 4), dtype=np.float64)


def rasterize_segments_scanline(
    segments: np.ndarray,
    bbox_min_xy: tuple[float, float],
    bbox_max_xy: tuple[float, float],
    width: int,
    height: int,
    eps: float = 1e-12,
) -> tuple[np.ndarray, dict[str, int]]:
    xmin, ymin = bbox_min_xy
    xmax, ymax = bbox_max_xy
    dx = (xmax - xmin) / width
    dy = (ymax - ymin) / height
    if dx <= 0 or dy <= 0:
        raise ValueError("degenerate XY geometry bounds")
    mask = np.zeros((height, width), dtype=bool)
    odd_rows = 0
    filled_rows = 0
    max_intersections = 0
    if segments.size == 0:
        return mask, {"odd_scanline_rows": 0, "filled_rows": 0, "max_intersections": 0}
    x1, y1, x2, y2 = (segments[:, index] for index in range(4))
    dy_segment = y2 - y1
    non_horizontal = np.abs(dy_segment) > eps
    for row in range(height):
        y = ymax - (row + 0.5) * dy
        active = non_horizontal & (((y1 <= y) & (y < y2)) | ((y2 <= y) & (y < y1)))
        if not np.any(active):
            continue
        intersections = x1[active] + (y - y1[active]) * (x2[active] - x1[active]) / (y2[active] - y1[active])
        intersections = intersections[(intersections >= xmin - eps) & (intersections <= xmax + eps)]
        if intersections.size == 0:
            continue
        intersections.sort()
        max_intersections = max(max_intersections, int(intersections.size))
        if intersections.size % 2 == 1:
            odd_rows += 1
            intersections = intersections[:-1]
        for index in range(0, intersections.size, 2):
            left = max(float(intersections[index]), xmin)
            right = min(float(intersections[index + 1]), xmax)
            if right <= left:
                continue
            column_start = max(0, min(width - 1, int(math.ceil((left - xmin) / dx - 0.5))))
            column_end = max(0, min(width - 1, int(math.floor((right - xmin) / dx - 0.5))))
            if column_end >= column_start:
                mask[row, column_start : column_end + 1] = True
                filled_rows += 1
    return mask, {
        "odd_scanline_rows": odd_rows,
        "filled_rows": filled_rows,
        "max_intersections": max_intersections,
    }
