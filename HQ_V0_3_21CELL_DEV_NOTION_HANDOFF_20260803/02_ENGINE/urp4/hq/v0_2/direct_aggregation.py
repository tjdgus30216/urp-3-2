"""Config-addressed direct-descriptor aggregation for v0.2 exploratory runs.

The arithmetic is intentionally the same as RUN-139 F001--F008.  The changed
population size and image resolution are recorded in population IDs and every
row is labelled ``experimental``.  It is therefore not a replacement for the
frozen v0.1 parity service.
"""

from __future__ import annotations

import numpy as np

from urp4.descriptor_service.v0_1.formula import population_mean, population_std_ddof0
from urp4.descriptor_service.v0_1.models import DescriptorServiceError, PrimitiveTables, ScalarResult
from urp4.descriptor_service.v0_1.population import (
    finite_component_population,
    overlay_change_fraction,
    overlay_overlap_fraction,
    slice_component_count,
    slice_occupancy,
)
from urp4.descriptor_service.v0_1.service import Run139DescriptorService


def _contiguous(frame, column: str, expected_n: int, label: str) -> None:
    if len(frame) != expected_n:
        raise DescriptorServiceError(f"{label}: expected {expected_n} rows, got {len(frame)}")
    observed = frame[column].to_numpy(dtype=int)
    if not np.array_equal(observed, np.arange(expected_n, dtype=int)):
        raise DescriptorServiceError(f"{label}: {column} must be ordered contiguous")


def compute_exploratory_direct(tables: PrimitiveTables, *, slice_count: int, pixel_resolution: int) -> tuple[ScalarResult, ...]:
    """Compute F001--F008 with an explicitly non-parity population address."""

    # Reuse column/model validation, then replace only fixed 801/800 checks.
    service = Run139DescriptorService()
    model_id = str(tables.model_id).strip()
    if not model_id:
        raise DescriptorServiceError("model_id cannot be empty")
    service._require_columns(tables.slice_pixels, service._SLICE_COLUMNS, "slice_pixels")
    service._require_columns(tables.overlay_pixels, service._OVERLAY_COLUMNS, "overlay_pixels")
    service._require_columns(tables.overlay_components, service._COMPONENT_COLUMNS, "overlay_components")
    service._require_model(tables.slice_pixels, model_id, "slice_pixels")
    service._require_model(tables.overlay_pixels, model_id, "overlay_pixels")
    service._require_model(tables.overlay_components, model_id, "overlay_components")
    _contiguous(tables.slice_pixels, "slice_index", slice_count, "slice_pixels")
    _contiguous(tables.overlay_pixels, "pair_index", slice_count - 1, "overlay_pixels")

    occupancy = slice_occupancy(tables.slice_pixels, pixel_count=pixel_resolution * pixel_resolution)
    component_count = slice_component_count(tables.slice_pixels)
    change_fraction = overlay_change_fraction(tables.overlay_pixels)
    overlap_fraction = overlay_overlap_fraction(tables.overlay_pixels)
    thickness = finite_component_population(tables.overlay_components, "thickness_sqrt_red_purple")
    mass_orientation = finite_component_population(tables.overlay_components, "mass_orientation")
    scope = f"EXPLORATORY-P{pixel_resolution}-Z{slice_count}"

    def result(fid, descriptor, population, statistic, unit, value, n):
        if not np.isfinite(value):
            raise DescriptorServiceError(f"{fid}/{statistic}: non-finite aggregate")
        return ScalarResult(model_id, fid, descriptor, f"{scope}-{population}", statistic, unit, float(value), int(n), "experimental")

    return (
        result("XRV1-F001", "slice_occupancy_mean", "SLICE", "mean", "dimensionless", population_mean(occupancy), len(occupancy)),
        result("XRV1-F002", "slice_occupancy_std_pop", "SLICE", "std_pop_ddof0", "dimensionless", population_std_ddof0(occupancy), len(occupancy)),
        result("XRV1-F003", "component_count_mean", "SLICE-CC", "mean", "count", population_mean(component_count), len(component_count)),
        result("XRV1-F004", "component_count_std_pop", "SLICE-CC", "std_pop_ddof0", "count", population_std_ddof0(component_count), len(component_count)),
        result("XRV1-F005", "overlay_change_fraction_mean", "OVERLAY", "mean", "dimensionless", population_mean(change_fraction), len(change_fraction)),
        result("XRV1-F006", "overlay_overlap_fraction_mean", "OVERLAY", "mean", "dimensionless", population_mean(overlap_fraction), len(overlap_fraction)),
        result("XRV1-F007", "thickness_component_sqrt_red_purple_area", "OVERLAY-COMPONENT", "mean", "mm", population_mean(thickness), len(thickness)),
        result("XRV1-F007", "thickness_component_sqrt_red_purple_area", "OVERLAY-COMPONENT", "std_pop_ddof0", "mm", population_std_ddof0(thickness), len(thickness)),
        result("XRV1-F008", "massori_component_pool_mean", "OVERLAY-COMPONENT", "mean", "dimensionless", population_mean(mass_orientation), len(mass_orientation)),
    )
