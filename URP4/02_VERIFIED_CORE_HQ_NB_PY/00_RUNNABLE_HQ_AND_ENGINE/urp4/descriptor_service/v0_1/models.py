"""Immutable values crossing the descriptor-service boundary."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import pandas as pd


class DescriptorServiceError(ValueError):
    """Fail-closed error raised when frozen input semantics are violated."""


@dataclass(frozen=True)
class PrimitiveTables:
    """Tables persisted by the RUN-139 image/pixel factory for one model."""

    model_id: str
    slice_pixels: pd.DataFrame
    overlay_pixels: pd.DataFrame
    overlay_components: pd.DataFrame


@dataclass(frozen=True)
class ScalarResult:
    """One semantically named scalar output from the descriptor service."""

    model_id: str
    formula_id: str
    descriptor: str
    population_id: str
    statistic: str
    unit: str
    value: float
    population_n: int
    state: str

    def to_row(self) -> dict[str, Any]:
        return asdict(self)
