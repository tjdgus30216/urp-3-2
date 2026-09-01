"""Saved-PNG readback and OpenCV connected-component operations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image


def save_mask(mask: np.ndarray, path: str | Path, *, compress_level: int = 1) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.asarray(mask, dtype=np.uint8) * 255).save(target, compress_level=compress_level)


def read_mask(path: str | Path) -> np.ndarray:
    with Image.open(path) as image:
        return np.asarray(image.convert("L")) > 0


def save_overlay(lower: np.ndarray, upper: np.ndarray, path: str | Path, *, compress_level: int = 1) -> dict[str, int]:
    red = lower & ~upper
    blue = upper & ~lower
    purple = lower & upper
    height, width = lower.shape
    rgb = np.full((height, width, 3), 255, dtype=np.uint8)
    rgb[red] = [255, 0, 0]
    rgb[blue] = [0, 70, 255]
    rgb[purple] = [160, 0, 160]
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgb).save(target, compress_level=compress_level)
    return {
        "red_pixel_count": int(red.sum()),
        "blue_pixel_count": int(blue.sum()),
        "purple_pixel_count": int(purple.sum()),
        "union_pixel_count": int((lower | upper).sum()),
    }


def read_overlay_counts(path: str | Path) -> dict[str, int]:
    with Image.open(path) as image:
        rgb = np.asarray(image.convert("RGB"))
    red = np.all(rgb == np.array([255, 0, 0], dtype=np.uint8), axis=2)
    blue = np.all(rgb == np.array([0, 70, 255], dtype=np.uint8), axis=2)
    purple = np.all(rgb == np.array([160, 0, 160], dtype=np.uint8), axis=2)
    return {
        "red_pixel_count": int(red.sum()),
        "blue_pixel_count": int(blue.sum()),
        "purple_pixel_count": int(purple.sum()),
        "union_pixel_count": int((red | blue | purple).sum()),
    }


def connected_components(mask: np.ndarray, *, min_pixels: int, connectivity: int) -> tuple[list[dict[str, Any]], np.ndarray]:
    count, labels, stats, _centroids = cv2.connectedComponentsWithStats(
        np.asarray(mask, dtype=np.uint8), connectivity=connectivity, ltype=cv2.CV_32S
    )
    rows: list[dict[str, Any]] = []
    for source_label in range(1, count):
        area = int(stats[source_label, cv2.CC_STAT_AREA])
        if area < min_pixels:
            continue
        rows.append(
            {
                "component_id": len(rows) + 1,
                "source_label": source_label,
                "pixel_count": area,
                "bbox_col_min": int(stats[source_label, cv2.CC_STAT_LEFT]),
                "bbox_row_min": int(stats[source_label, cv2.CC_STAT_TOP]),
                "bbox_col_max": int(stats[source_label, cv2.CC_STAT_LEFT] + stats[source_label, cv2.CC_STAT_WIDTH] - 1),
                "bbox_row_max": int(stats[source_label, cv2.CC_STAT_TOP] + stats[source_label, cv2.CC_STAT_HEIGHT] - 1),
            }
        )
    return rows, labels
