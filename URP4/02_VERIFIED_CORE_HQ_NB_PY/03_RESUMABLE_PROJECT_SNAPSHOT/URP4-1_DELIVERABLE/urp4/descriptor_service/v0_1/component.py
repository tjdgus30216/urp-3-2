"""Overlay-component feature extraction from the frozen R09-017 lineage."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any

import cv2
import numpy as np


def perimeter_pixels(mask: np.ndarray) -> float:
    contours, _ = cv2.findContours(np.asarray(mask, dtype=np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    return float(sum(cv2.arcLength(contour, True) for contour in contours))


def contact_edge_length_pixels(mask_a: np.ndarray, mask_b: np.ndarray) -> int:
    kernel = np.ones((3, 3), np.uint8)
    dilated = cv2.dilate(np.asarray(mask_a, dtype=np.uint8), kernel, iterations=1).astype(bool)
    return int(np.count_nonzero(dilated & np.asarray(mask_b, dtype=bool)))


def safe_div(numerator: float, denominator: float) -> float:
    if denominator <= 1e-15 or not math.isfinite(numerator) or not math.isfinite(denominator):
        return np.nan
    return numerator / denominator


def safe_angle(height: float, length: float) -> float:
    if not math.isfinite(length) or length <= 1e-15:
        return np.nan
    return float(math.degrees(math.atan(height / length)))


@dataclass(frozen=True)
class ComponentFeature:
    pair_index: int
    component_index: int
    red_px: int
    blue_px: int
    purple_px: int
    combined_px: int
    red_area: float
    blue_area: float
    purple_area: float
    combined_area: float
    rp_contact_length: float
    bp_contact_length: float
    combined_perimeter_length: float
    mass_weight_area: float
    physical_weight_volume: float
    mass_orientation: float
    thickness_sqrt_red_purple: float
    thickness_area_red_purple: float
    thickness_equiv_diameter_red_purple: float
    pa_current_red_purple: float
    pa_pixel_unit_red_purple: float
    leff_contact_sum: float
    leff_change_area_over_contact: float
    leff_combined_area_over_perimeter: float
    angle_current_2h_contact_sum: float
    angle_h_contact_sum: float
    angle_h_change_area_over_contact: float
    angle_h_combined_area_over_perimeter: float
    curvature_current_contact_sum_over_2h: float
    curvature_area_over_h_contact_sum: float
    curvature_area_over_h_change_contact: float
    curvature_area_over_h_perimeter_leff: float

    def to_row(self) -> dict[str, Any]:
        return asdict(self)


def component_features_for_pair(
    lower: np.ndarray,
    upper: np.ndarray,
    *,
    pair_index: int,
    area_per_pixel: float,
    length_per_pixel: float,
    layer_height: float,
    min_pixels: int,
    connectivity: int,
) -> tuple[list[ComponentFeature], dict[str, Any]]:
    red = np.asarray(lower, dtype=bool) & ~np.asarray(upper, dtype=bool)
    blue = np.asarray(upper, dtype=bool) & ~np.asarray(lower, dtype=bool)
    purple = np.asarray(lower, dtype=bool) & np.asarray(upper, dtype=bool)
    combined = red | blue | purple
    label_count, labels = cv2.connectedComponents(combined.astype(np.uint8), connectivity=connectivity)
    output: list[ComponentFeature] = []
    for label in range(1, label_count):
        label_mask = labels == label
        combined_px = int(np.count_nonzero(label_mask))
        if combined_px < min_pixels:
            continue
        red_mask = red & label_mask
        blue_mask = blue & label_mask
        purple_mask = purple & label_mask
        red_purple = red_mask | purple_mask
        red_px = int(np.count_nonzero(red_mask))
        blue_px = int(np.count_nonzero(blue_mask))
        purple_px = int(np.count_nonzero(purple_mask))
        red_area = red_px * area_per_pixel
        blue_area = blue_px * area_per_pixel
        purple_area = purple_px * area_per_pixel
        combined_area = combined_px * area_per_pixel
        rp_contact = contact_edge_length_pixels(red_mask, purple_mask) * length_per_pixel
        bp_contact = contact_edge_length_pixels(blue_mask, purple_mask) * length_per_pixel
        combined_perimeter = perimeter_pixels(label_mask) * length_per_pixel
        rp_perimeter = perimeter_pixels(red_purple) * length_per_pixel
        mass_weight = 0.5 * red_area + 0.5 * blue_area + purple_area
        mass_orientation = safe_div(purple_area, mass_weight)
        physical_weight = mass_weight * layer_height
        area_red_purple = red_area + purple_area
        thickness_sqrt = math.sqrt(max(area_red_purple, 0.0))
        thickness_equivalent = 2.0 * math.sqrt(area_red_purple / math.pi) if area_red_purple > 0 else np.nan
        pa_current = safe_div(rp_perimeter, area_red_purple)
        pa_pixel = safe_div(perimeter_pixels(red_purple), float(np.count_nonzero(red_purple)))
        term_red = safe_div(red_area, rp_contact)
        term_blue = safe_div(blue_area, bp_contact)
        terms = [value for value in (term_red, term_blue) if math.isfinite(value)]
        leff_contact_sum = float(sum(terms)) if terms else np.nan
        total_change_area = red_area + blue_area
        total_contact = rp_contact + bp_contact
        leff_change_contact = safe_div(total_change_area, total_contact)
        leff_area_perimeter = safe_div(combined_area, combined_perimeter)
        output.append(
            ComponentFeature(
                pair_index=pair_index,
                component_index=label,
                red_px=red_px,
                blue_px=blue_px,
                purple_px=purple_px,
                combined_px=combined_px,
                red_area=red_area,
                blue_area=blue_area,
                purple_area=purple_area,
                combined_area=combined_area,
                rp_contact_length=rp_contact,
                bp_contact_length=bp_contact,
                combined_perimeter_length=combined_perimeter,
                mass_weight_area=mass_weight,
                physical_weight_volume=physical_weight,
                mass_orientation=mass_orientation,
                thickness_sqrt_red_purple=thickness_sqrt,
                thickness_area_red_purple=area_red_purple,
                thickness_equiv_diameter_red_purple=thickness_equivalent,
                pa_current_red_purple=pa_current,
                pa_pixel_unit_red_purple=pa_pixel,
                leff_contact_sum=leff_contact_sum,
                leff_change_area_over_contact=leff_change_contact,
                leff_combined_area_over_perimeter=leff_area_perimeter,
                angle_current_2h_contact_sum=safe_angle(2.0 * layer_height, leff_contact_sum),
                angle_h_contact_sum=safe_angle(layer_height, leff_contact_sum),
                angle_h_change_area_over_contact=safe_angle(layer_height, leff_change_contact),
                angle_h_combined_area_over_perimeter=safe_angle(layer_height, leff_area_perimeter),
                curvature_current_contact_sum_over_2h=safe_div(leff_contact_sum, 2.0 * layer_height),
                curvature_area_over_h_contact_sum=safe_div(total_change_area, layer_height * leff_contact_sum),
                curvature_area_over_h_change_contact=safe_div(total_change_area, layer_height * leff_change_contact),
                curvature_area_over_h_perimeter_leff=safe_div(total_change_area, layer_height * leff_area_perimeter),
            )
        )
    counts = {
        "pair_index": pair_index,
        "component_count_raw": int(label_count - 1),
        "component_count_kept": len(output),
        "red_pixels": int(np.count_nonzero(red)),
        "blue_pixels": int(np.count_nonzero(blue)),
        "purple_pixels": int(np.count_nonzero(purple)),
        "valid_pair": bool(output),
    }
    return output, counts
