"""Pure scalar aggregation extracted from RUN-139 without formula changes.

Lineage authority:
``R09_RESLICE_002_r1v2_pathsafe_native_smoke.py:508-544``.  RUN-139 imports
that function unchanged through ``R09_RESLICE_003_all58_resumable_factory.py``.
This module intentionally starts *after* image slicing, saved-PNG readback and
connected-component extraction.  Those upstream artifacts remain frozen input
evidence; this module only provides a small, testable aggregation boundary.
"""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd

from .formula import population_mean, population_std_ddof0
from .models import DescriptorServiceError, PrimitiveTables, ScalarResult
from .population import (
    finite_component_population,
    overlay_change_fraction,
    overlay_overlap_fraction,
    slice_component_count,
    slice_occupancy,
)


RUN139_BACKEND_ID = "BACKEND-R09-RESLICE-003-SAVED-PNG-READBACK-v0.1"
RUN139_RUN_ID = "R09-RESLICE-003"
RUN139_SCHEMA_VERSION = "DESCRIPTOR-SCHEMA-v0.1"

SLICE_COUNT = 801
OVERLAY_COUNT = 800
PIXEL_WIDTH = 1000
PIXEL_HEIGHT = 1000


class Run139DescriptorService:
    """Reproduce RUN-139 F001--F008 scalar aggregation from primitive tables."""

    _SLICE_COLUMNS = {
        "model_id",
        "slice_index",
        "material_pixel_count",
        "component_count",
    }
    _OVERLAY_COLUMNS = {
        "model_id",
        "pair_index",
        "red_pixel_count",
        "blue_pixel_count",
        "purple_pixel_count",
        "union_pixel_count",
    }
    _COMPONENT_COLUMNS = {
        "model_id",
        "pair_index",
        "thickness_sqrt_red_purple",
        "mass_orientation",
    }

    @staticmethod
    def _require_columns(frame: pd.DataFrame, required: set[str], label: str) -> None:
        missing = sorted(required.difference(frame.columns))
        if missing:
            raise DescriptorServiceError(f"{label}: missing columns {missing}")

    @staticmethod
    def _require_model(frame: pd.DataFrame, model_id: str, label: str) -> None:
        observed = set(frame["model_id"].astype(str).unique())
        if observed != {model_id}:
            raise DescriptorServiceError(
                f"{label}: model_id mismatch; expected {model_id!r}, observed {sorted(observed)!r}"
            )

    @staticmethod
    def _require_index(frame: pd.DataFrame, column: str, expected_n: int, label: str) -> None:
        if len(frame) != expected_n:
            raise DescriptorServiceError(f"{label}: expected {expected_n} rows, got {len(frame)}")
        values = pd.to_numeric(frame[column], errors="raise").astype(int).to_numpy()
        expected = np.arange(expected_n, dtype=int)
        if not np.array_equal(values, expected):
            raise DescriptorServiceError(f"{label}: {column} must be ordered contiguous 0..{expected_n - 1}")

    @staticmethod
    def _numeric(frame: pd.DataFrame, columns: Iterable[str], label: str) -> dict[str, np.ndarray]:
        arrays: dict[str, np.ndarray] = {}
        for column in columns:
            values = pd.to_numeric(frame[column], errors="raise").astype(float).to_numpy()
            if not np.all(np.isfinite(values)):
                raise DescriptorServiceError(f"{label}: non-finite values in {column}")
            arrays[column] = values
        return arrays

    def validate(self, tables: PrimitiveTables) -> None:
        model_id = str(tables.model_id).strip()
        if not model_id:
            raise DescriptorServiceError("model_id cannot be empty")
        self._require_columns(tables.slice_pixels, self._SLICE_COLUMNS, "slice_pixels")
        self._require_columns(tables.overlay_pixels, self._OVERLAY_COLUMNS, "overlay_pixels")
        self._require_columns(tables.overlay_components, self._COMPONENT_COLUMNS, "overlay_components")
        self._require_model(tables.slice_pixels, model_id, "slice_pixels")
        self._require_model(tables.overlay_pixels, model_id, "overlay_pixels")
        self._require_model(tables.overlay_components, model_id, "overlay_components")
        self._require_index(tables.slice_pixels, "slice_index", SLICE_COUNT, "slice_pixels")
        self._require_index(tables.overlay_pixels, "pair_index", OVERLAY_COUNT, "overlay_pixels")
        pair_index = pd.to_numeric(tables.overlay_components["pair_index"], errors="raise").astype(int)
        if pair_index.empty or pair_index.min() < 0 or pair_index.max() >= OVERLAY_COUNT:
            raise DescriptorServiceError("overlay_components: pair_index outside 0..799 or empty")

    def compute(self, tables: PrimitiveTables) -> tuple[ScalarResult, ...]:
        """Return the exact nine RUN-139 scalar rows for one validated model."""

        self.validate(tables)
        model_id = tables.model_id
        slice_values = self._numeric(
            tables.slice_pixels,
            ("material_pixel_count", "component_count"),
            "slice_pixels",
        )
        overlay_values = self._numeric(
            tables.overlay_pixels,
            ("red_pixel_count", "blue_pixel_count", "purple_pixel_count", "union_pixel_count"),
            "overlay_pixels",
        )
        component_values = self._numeric(
            tables.overlay_components,
            ("thickness_sqrt_red_purple", "mass_orientation"),
            "overlay_components",
        )

        del slice_values, overlay_values, component_values
        try:
            occupancy = slice_occupancy(
                tables.slice_pixels,
                pixel_count=PIXEL_WIDTH * PIXEL_HEIGHT,
            )
            component_count = slice_component_count(tables.slice_pixels)
            change_fraction = overlay_change_fraction(tables.overlay_pixels)
            overlap_fraction = overlay_overlap_fraction(tables.overlay_pixels)
            thickness = finite_component_population(
                tables.overlay_components,
                "thickness_sqrt_red_purple",
            )
            mass_orientation = finite_component_population(
                tables.overlay_components,
                "mass_orientation",
            )
        except ValueError as exc:
            raise DescriptorServiceError(str(exc)) from exc

        def scalar(
            formula_id: str,
            descriptor: str,
            population_id: str,
            statistic: str,
            unit: str,
            value: float,
            population_n: int,
            state: str,
        ) -> ScalarResult:
            if not np.isfinite(value):
                raise DescriptorServiceError(f"{formula_id}/{statistic}: non-finite aggregate")
            return ScalarResult(
                model_id=model_id,
                formula_id=formula_id,
                descriptor=descriptor,
                population_id=population_id,
                statistic=statistic,
                unit=unit,
                value=float(value),
                population_n=int(population_n),
                state=state,
            )

        return (
            scalar("XRV1-F001", "slice_occupancy_mean", "XRV1-P-SLICE-801-Z", "mean", "dimensionless", population_mean(occupancy), len(occupancy), "confirmed"),
            scalar("XRV1-F002", "slice_occupancy_std_pop", "XRV1-P-SLICE-801-Z", "std_pop_ddof0", "dimensionless", population_std_ddof0(occupancy), len(occupancy), "confirmed"),
            scalar("XRV1-F003", "component_count_mean", "XRV1-P-SLICE-801-Z-CC8M2", "mean", "count", population_mean(component_count), len(component_count), "confirmed"),
            scalar("XRV1-F004", "component_count_std_pop", "XRV1-P-SLICE-801-Z-CC8M2", "std_pop_ddof0", "count", population_std_ddof0(component_count), len(component_count), "confirmed"),
            scalar("XRV1-F005", "overlay_change_fraction_mean", "XRV1-P-OVERLAY-800-Z-VALID-UNION", "mean", "dimensionless", population_mean(change_fraction), len(change_fraction), "confirmed"),
            scalar("XRV1-F006", "overlay_overlap_fraction_mean", "XRV1-P-OVERLAY-800-Z-VALID-UNION", "mean", "dimensionless", population_mean(overlap_fraction), len(overlap_fraction), "confirmed"),
            scalar("XRV1-F007", "thickness_component_sqrt_red_purple_area", "XRV1-P-OVERLAY-COMPONENT-POOLED-CC8M2", "mean", "mm", population_mean(thickness), len(thickness), "likely"),
            scalar("XRV1-F007", "thickness_component_sqrt_red_purple_area", "XRV1-P-OVERLAY-COMPONENT-POOLED-CC8M2", "std_pop_ddof0", "mm", population_std_ddof0(thickness), len(thickness), "likely"),
            scalar("XRV1-F008", "massori_component_pool_mean", "XRV1-P-OVERLAY-COMPONENT-POOLED-UNWEIGHTED-CC8M2", "mean", "dimensionless", population_mean(mass_orientation), len(mass_orientation), "likely"),
        )
