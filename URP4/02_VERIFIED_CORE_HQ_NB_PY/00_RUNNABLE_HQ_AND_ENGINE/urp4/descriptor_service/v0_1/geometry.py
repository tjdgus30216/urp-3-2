"""Binary STL geometry ingestion used by the RUN-139 service."""

from __future__ import annotations

import struct
from pathlib import Path

import numpy as np

from urp4.contracts.v0_1.canonical import sha256_file


def load_binary_stl_vertices(path: str | Path, *, expected_sha256: str | None = None) -> np.ndarray:
    source = Path(path)
    if expected_sha256 is not None and sha256_file(source) != expected_sha256:
        raise ValueError(f"geometry hash mismatch: {source}")
    data = source.read_bytes()
    if len(data) < 84:
        raise ValueError(f"STL too small: {source}")
    n_triangles = struct.unpack_from("<I", data, 80)[0]
    expected_bytes = 84 + n_triangles * 50
    if len(data) != expected_bytes:
        raise ValueError(
            f"binary STL length mismatch: n_triangles={n_triangles}, expected={expected_bytes}, actual={len(data)}"
        )
    dtype = np.dtype(
        [
            ("normal", "<f4", (3,)),
            ("vertices", "<f4", (3, 3)),
            ("attribute", "<u2"),
        ]
    )
    records = np.frombuffer(data, dtype=dtype, count=n_triangles, offset=84)
    vertices = records["vertices"].astype(np.float64, copy=True)
    if vertices.shape != (n_triangles, 3, 3) or not np.all(np.isfinite(vertices)):
        raise ValueError("invalid STL triangle array")
    return vertices


def geometry_bounds(triangles: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    vertices = np.asarray(triangles, dtype=np.float64).reshape(-1, 3)
    if vertices.size == 0 or not np.all(np.isfinite(vertices)):
        raise ValueError("geometry has no finite vertices")
    return vertices.min(axis=0), vertices.max(axis=0)
