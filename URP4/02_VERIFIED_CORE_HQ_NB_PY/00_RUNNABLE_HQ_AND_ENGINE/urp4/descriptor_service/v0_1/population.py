"""Named population construction for RUN-139 scalar formulas."""

from __future__ import annotations

import numpy as np
import pandas as pd


def slice_occupancy(slice_pixels: pd.DataFrame, *, pixel_count: int) -> np.ndarray:
    return slice_pixels["material_pixel_count"].astype(float).to_numpy() / float(pixel_count)


def slice_component_count(slice_pixels: pd.DataFrame) -> np.ndarray:
    return slice_pixels["component_count"].astype(float).to_numpy()


def overlay_change_fraction(overlay_pixels: pd.DataFrame) -> np.ndarray:
    union = overlay_pixels["union_pixel_count"].astype(float).to_numpy()
    change = overlay_pixels["red_pixel_count"].astype(float).to_numpy() + overlay_pixels["blue_pixel_count"].astype(float).to_numpy()
    valid = union > 0
    if not np.any(valid):
        raise ValueError("no positive union population")
    return change[valid] / union[valid]


def overlay_overlap_fraction(overlay_pixels: pd.DataFrame) -> np.ndarray:
    union = overlay_pixels["union_pixel_count"].astype(float).to_numpy()
    purple = overlay_pixels["purple_pixel_count"].astype(float).to_numpy()
    valid = union > 0
    if not np.any(valid):
        raise ValueError("no positive union population")
    return purple[valid] / union[valid]


def finite_component_population(overlay_components: pd.DataFrame, column: str) -> np.ndarray:
    values = overlay_components[column].astype(float).to_numpy()
    values = values[np.isfinite(values)]
    if values.size == 0:
        raise ValueError(f"empty finite component population: {column}")
    return values
