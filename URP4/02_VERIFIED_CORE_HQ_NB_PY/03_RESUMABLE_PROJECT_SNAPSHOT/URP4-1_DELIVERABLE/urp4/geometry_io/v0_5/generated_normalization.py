"""Write a 40 mm, centered, uniformly-scaled analysis derivative of a generated STL.

The source mesh stays byte-for-byte untouched.  This utility intentionally
does not weld vertices, remove triangles, fill holes, repair normals, or
otherwise alter topology.  Its only geometric operation is the documented
affine transform ``(p - bbox_center) * scale + target_center``.
"""

from __future__ import annotations

import hashlib
import json
import struct
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from urp4.contracts.v0_1.canonical import sha256_file
from urp4.descriptor_service.v0_1.geometry import geometry_bounds, load_binary_stl_vertices


@dataclass(frozen=True)
class GeneratedNormalizationConfig:
    target_size_mm: float = 40.0
    isotropic_extent_tolerance_mm: float = 1.0e-3
    method: str = "centered_uniform_bbox_to_40mm"
    revision: str = "HQ-GEOM-001/v0.5/r1"

    def validate(self) -> None:
        if not np.isfinite(self.target_size_mm) or self.target_size_mm <= 0:
            raise ValueError("target_size_mm must be positive")
        if self.method != "centered_uniform_bbox_to_40mm":
            raise ValueError("only centered_uniform_bbox_to_40mm is approved")


def _write_binary_stl(path: Path, triangles: np.ndarray, header: bytes) -> None:
    """Persist triangle positions in stable input order without mesh repair."""

    array = np.asarray(triangles, dtype=np.float64)
    if array.ndim != 3 or array.shape[1:] != (3, 3):
        raise ValueError(f"expected triangles [n,3,3], got {array.shape}")
    vectors = array[:, 1] - array[:, 0]
    normals = np.cross(vectors, array[:, 2] - array[:, 0])
    norm = np.linalg.norm(normals, axis=1)
    nonzero = norm > 0
    normals[nonzero] /= norm[nonzero, None]
    normals[~nonzero] = 0.0
    record = np.empty(len(array), dtype=np.dtype([
        ("normal", "<f4", (3,)),
        ("vertices", "<f4", (3, 3)),
        ("attribute", "<u2"),
    ]))
    record["normal"] = normals.astype("<f4")
    record["vertices"] = array.astype("<f4")
    record["attribute"] = 0
    padded = (header[:80] + b" " * 80)[:80]
    with path.open("wb") as handle:
        handle.write(padded)
        handle.write(struct.pack("<I", len(record)))
        handle.write(record.tobytes(order="C"))


def _manifest_payload(
    *, source: Path, derivative: Path, source_triangles: np.ndarray,
    derivative_triangles: np.ndarray, config: GeneratedNormalizationConfig,
    source_sha256: str, scale: float, center: np.ndarray,
) -> dict[str, object]:
    source_lower, source_upper = geometry_bounds(source_triangles)
    derivative_lower, derivative_upper = geometry_bounds(derivative_triangles)
    return {
        "normalization_status": "created_analysis_derivative",
        "normalization_method": config.method,
        "normalization_revision": config.revision,
        "source_geometry_path": str(source),
        "source_sha256": source_sha256,
        "derivative_geometry_path": str(derivative),
        "derivative_sha256": sha256_file(derivative) if derivative.is_file() else None,
        "source_triangle_count": int(len(source_triangles)),
        "derivative_triangle_count": int(len(derivative_triangles)),
        "source_bbox_min_mm": source_lower.tolist(),
        "source_bbox_max_mm": source_upper.tolist(),
        "source_bbox_extent_mm": (source_upper - source_lower).tolist(),
        "source_bbox_center_mm": center.tolist(),
        "analysis_uniform_scale": float(scale),
        "analysis_target_center_mm": [config.target_size_mm / 2.0] * 3,
        "analysis_bbox_min_mm": derivative_lower.tolist(),
        "analysis_bbox_max_mm": derivative_upper.tolist(),
        "analysis_bbox_extent_mm": (derivative_upper - derivative_lower).tolist(),
        "topology_operation": "none_positions_only_uniform_affine_transform",
        "config": asdict(config),
    }


def normalize_generated_stl(
    source_path: str | Path,
    derivative_path: str | Path,
    *,
    config: GeneratedNormalizationConfig = GeneratedNormalizationConfig(),
    expected_source_sha256: str | None = None,
) -> dict[str, object]:
    """Create or verify a deterministic generated-STL analysis derivative."""

    config.validate()
    source = Path(source_path).resolve()
    derivative = Path(derivative_path).resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    source_sha = sha256_file(source)
    if expected_source_sha256 and source_sha.lower() != expected_source_sha256.lower():
        raise ValueError(f"source SHA-256 mismatch: {source}")
    triangles = load_binary_stl_vertices(source, expected_sha256=source_sha)
    lower, upper = geometry_bounds(triangles)
    extents = upper - lower
    if float(np.max(extents) - np.min(extents)) > config.isotropic_extent_tolerance_mm:
        raise ValueError(f"non-isotropic bbox cannot use uniform normalization: {extents.tolist()}")
    center = (lower + upper) / 2.0
    scale = float(config.target_size_mm / np.max(extents))
    transformed = (triangles - center) * scale + config.target_size_mm / 2.0
    derivative.parent.mkdir(parents=True, exist_ok=True)
    expected = _manifest_payload(
        source=source, derivative=derivative, source_triangles=triangles,
        derivative_triangles=transformed, config=config, source_sha256=source_sha,
        scale=scale, center=center,
    )
    manifest_path = derivative.with_suffix(derivative.suffix + ".normalization.json")
    if derivative.exists() or manifest_path.exists():
        if not derivative.is_file() or not manifest_path.is_file():
            raise FileExistsError(f"partial derivative state: {derivative}")
        observed = json.loads(manifest_path.read_text(encoding="utf-8"))
        stable_fields = (
            "source_sha256", "derivative_sha256", "source_triangle_count", "derivative_triangle_count",
            "source_bbox_extent_mm", "analysis_uniform_scale", "analysis_bbox_extent_mm",
            "normalization_method", "normalization_revision",
        )
        if any(observed.get(key) != expected.get(key) for key in stable_fields):
            raise FileExistsError(f"existing derivative manifest differs: {derivative}")
        return observed
    header = f"URP4 HQ-GEOM-001 {config.revision}".encode("ascii", errors="replace")
    _write_binary_stl(derivative, transformed, header)
    expected["derivative_sha256"] = sha256_file(derivative)
    manifest_path.write_text(json.dumps(expected, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return expected
