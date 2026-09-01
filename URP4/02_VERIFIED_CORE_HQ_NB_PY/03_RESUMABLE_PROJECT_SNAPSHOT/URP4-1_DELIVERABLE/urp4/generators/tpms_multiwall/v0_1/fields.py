"""CPU TPMS field definitions copied from immutable notebook display Cell 4."""

from __future__ import annotations

import numpy as np


def make_tpms_grid(
    n: int = 96,
    size_mm: float = 8.0,
    frequency: float = 2.0,
    anisotropy: tuple[float, float, float] = (1.0, 1.0, 1.0),
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    # size_mm is retained for exact source signature compatibility. The source
    # field domain is phase-based and does not use the physical size directly.
    _ = size_mm
    x = np.linspace(0, 2 * np.pi * frequency * anisotropy[0], n)
    y = np.linspace(0, 2 * np.pi * frequency * anisotropy[1], n)
    z = np.linspace(0, 2 * np.pi * frequency * anisotropy[2], n)
    return np.meshgrid(x, y, z, indexing="ij")


def tpms_field(tpms_type: str, X: np.ndarray, Y: np.ndarray, Z: np.ndarray) -> np.ndarray:
    t = tpms_type.lower()
    if t == "gyroid":
        F = np.sin(X) * np.cos(Y) + np.sin(Y) * np.cos(Z) + np.sin(Z) * np.cos(X)
    elif t == "primitive":
        F = np.cos(X) + np.cos(Y) + np.cos(Z)
    elif t == "diamond":
        F = (
            np.sin(X) * np.sin(Y) * np.sin(Z)
            + np.sin(X) * np.cos(Y) * np.cos(Z)
            + np.cos(X) * np.sin(Y) * np.cos(Z)
            + np.cos(X) * np.cos(Y) * np.sin(Z)
        )
    elif t == "iwp":
        F = 2 * (np.cos(X) * np.cos(Y) + np.cos(Y) * np.cos(Z) + np.cos(Z) * np.cos(X)) - (
            np.cos(2 * X) + np.cos(2 * Y) + np.cos(2 * Z)
        )
    elif t == "neovius":
        F = 3 * (np.cos(X) + np.cos(Y) + np.cos(Z)) + 4 * np.cos(X) * np.cos(Y) * np.cos(Z)
    elif t == "lidinoid":
        F = 0.5 * (
            np.sin(2 * X) * np.cos(Y) * np.sin(Z)
            + np.sin(2 * Y) * np.cos(Z) * np.sin(X)
            + np.sin(2 * Z) * np.cos(X) * np.sin(Y)
        ) - 0.5 * (
            np.cos(2 * X) * np.cos(2 * Y)
            + np.cos(2 * Y) * np.cos(2 * Z)
            + np.cos(2 * Z) * np.cos(2 * X)
        ) + 0.15
    elif t == "split_p":
        F = 1.1 * (np.cos(X) + np.cos(Y) + np.cos(Z)) + 0.25 * (
            np.cos(2 * X) + np.cos(2 * Y) + np.cos(2 * Z)
        )
    elif t == "double_gyroid":
        G = np.sin(X) * np.cos(Y) + np.sin(Y) * np.cos(Z) + np.sin(Z) * np.cos(X)
        F = G**2 - 0.35
    elif t == "frd":
        F = 4 * np.cos(X) * np.cos(Y) * np.cos(Z) - (
            np.cos(2 * X) * np.cos(2 * Y)
            + np.cos(2 * Y) * np.cos(2 * Z)
            + np.cos(2 * Z) * np.cos(2 * X)
        )
    elif t == "fischer_koch_s":
        F = (
            np.cos(2 * X) * np.sin(Y) * np.cos(Z)
            + np.cos(X) * np.cos(2 * Y) * np.sin(Z)
            + np.sin(X) * np.cos(Y) * np.cos(2 * Z)
        )
    elif t == "fischer_koch_c":
        F = (
            np.cos(2 * X) * np.cos(Y) * np.sin(Z)
            + np.sin(X) * np.cos(2 * Y) * np.cos(Z)
            + np.cos(X) * np.sin(Y) * np.cos(2 * Z)
        )
    elif t == "pw_hybrid":
        Fp = np.cos(X) + np.cos(Y) + np.cos(Z)
        Fg = np.sin(X) * np.cos(Y) + np.sin(Y) * np.cos(Z) + np.sin(Z) * np.cos(X)
        F = 0.55 * Fp + 0.45 * Fg
    elif t == "srs_like":
        F = np.cos(X) * np.sin(Y) + np.cos(Y) * np.sin(Z) + np.cos(Z) * np.sin(X)
    elif t == "karcher_k_like":
        F = (
            np.cos(X) * np.cos(Y)
            + np.cos(Y) * np.cos(Z)
            + np.cos(Z) * np.cos(X)
            - np.sin(X) * np.sin(Y) * np.sin(Z)
        )
    else:
        raise ValueError(f"Unknown TPMS type: {tpms_type}")
    return (F - np.mean(F)) / (np.std(F) + 1e-12)

