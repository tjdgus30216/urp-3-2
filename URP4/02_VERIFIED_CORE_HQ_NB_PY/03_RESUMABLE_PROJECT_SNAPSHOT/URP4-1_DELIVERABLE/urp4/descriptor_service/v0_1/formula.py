"""Small statistical operators used by frozen descriptor formulas."""

from __future__ import annotations

import numpy as np


def population_mean(values: np.ndarray) -> float:
    result = float(np.mean(values))
    if not np.isfinite(result):
        raise ValueError("non-finite population mean")
    return result


def population_std_ddof0(values: np.ndarray) -> float:
    result = float(np.std(values, ddof=0))
    if not np.isfinite(result):
        raise ValueError("non-finite population standard deviation")
    return result
