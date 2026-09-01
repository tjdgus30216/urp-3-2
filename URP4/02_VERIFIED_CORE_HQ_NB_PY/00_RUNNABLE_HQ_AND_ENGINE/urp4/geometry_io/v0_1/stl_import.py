"""Deterministic STL discovery and descriptor-compatible row construction.

The importer does not repair, rescale, or overwrite geometry.  It records the
source bytes and mesh QA needed to make the later descriptor calculation
traceable, then exposes the exact ``stl_path`` column consumed by NB-CURRENT's
descriptor runner.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import trimesh

from urp4.contracts.v0_1.canonical import sha256_file
from urp4.descriptor_service.v0_1.geometry import geometry_bounds, load_binary_stl_vertices

from .models import GeometryImportError, STLImportConfig


_MODEL_PREFIX = re.compile(r"^(?P<model>[BCLFT]\d+)(?:\b|[_\-])", re.IGNORECASE)


def _model_id(path: Path) -> str:
    stem = path.stem
    match = _MODEL_PREFIX.match(stem)
    return match.group("model").upper() if match else stem


def _family_and_generator(model_id: str) -> tuple[str, str]:
    prefix = model_id[:1].upper()
    if prefix in {"B", "C", "L"}:
        return prefix, "lattice"
    if prefix == "T":
        return prefix, "tpms"
    if prefix == "F":
        return prefix, "foam"
    return "UNKNOWN", "external_import"


def discover_stl_files(config: STLImportConfig) -> list[Path]:
    root = config.input_path.resolve()
    if not root.exists():
        raise GeometryImportError(f"STL import path does not exist: {root}")
    if root.is_file():
        files = [root] if root.suffix.lower() == ".stl" else []
    elif config.recursive:
        files = list(root.rglob(config.pattern))
    else:
        files = list(root.glob(config.pattern))
    files = sorted((path.resolve() for path in files if path.is_file()), key=lambda p: p.as_posix().lower())
    if config.require_files and not files:
        raise GeometryImportError(
            f"STL import is enabled but no files match pattern={config.pattern!r} under {root}"
        )
    return files


def _load_mesh(path: Path) -> trimesh.Trimesh:
    try:
        # STL stores triangles independently, so ``process=False`` makes even a
        # closed mesh look disconnected/watertight=False.  In-memory processing
        # merges coincident vertices for QA only; source bytes are never changed.
        loaded = trimesh.load(str(path), file_type="stl", process=True)
    except Exception as exc:
        raise GeometryImportError(f"STL parser failed for {path}: {type(exc).__name__}: {exc}") from exc
    if isinstance(loaded, trimesh.Scene):
        meshes = [geometry for geometry in loaded.geometry.values() if isinstance(geometry, trimesh.Trimesh)]
        if not meshes:
            raise GeometryImportError(f"STL scene contains no mesh: {path}")
        loaded = trimesh.util.concatenate(meshes)
    if not isinstance(loaded, trimesh.Trimesh):
        raise GeometryImportError(f"STL did not produce a mesh: {path}")
    vertices = np.asarray(loaded.vertices, dtype=float)
    faces = np.asarray(loaded.faces, dtype=np.int64)
    if vertices.ndim != 2 or vertices.shape[1] != 3 or len(vertices) == 0:
        raise GeometryImportError(f"STL has no usable vertices: {path}")
    if faces.ndim != 2 or faces.shape[1] != 3 or len(faces) == 0:
        raise GeometryImportError(f"STL has no usable triangular faces: {path}")
    if not np.all(np.isfinite(vertices)):
        raise GeometryImportError(f"STL contains non-finite vertices: {path}")
    return loaded


def inspect_stl(
    path: str | Path,
    *,
    expected_size_mm: float | None = None,
    size_tolerance_mm: float = 1.0e-3,
    topology_qa: bool = False,
) -> dict[str, object]:
    source = Path(path).resolve()
    try:
        triangles = load_binary_stl_vertices(source)
        lower, upper = geometry_bounds(triangles)
        bounds = np.vstack([lower, upper])
        face_count = int(len(triangles))
        vertex_record_count = int(face_count * 3)
        parser = "custom_binary_stl_parser"
    except Exception:
        raw_mesh = trimesh.load(str(source), file_type="stl", process=False)
        if isinstance(raw_mesh, trimesh.Scene):
            meshes = [geometry for geometry in raw_mesh.geometry.values() if isinstance(geometry, trimesh.Trimesh)]
            if not meshes:
                raise GeometryImportError(f"STL scene contains no mesh: {source}")
            raw_mesh = trimesh.util.concatenate(meshes)
        if not isinstance(raw_mesh, trimesh.Trimesh) or len(raw_mesh.faces) == 0:
            raise GeometryImportError(f"STL did not produce a usable mesh: {source}")
        vertices = np.asarray(raw_mesh.vertices, dtype=float)
        if not np.all(np.isfinite(vertices)):
            raise GeometryImportError(f"STL contains non-finite vertices: {source}")
        bounds = np.asarray(raw_mesh.bounds, dtype=float)
        face_count = int(len(raw_mesh.faces))
        vertex_record_count = int(len(raw_mesh.vertices))
        parser = "trimesh_ascii_or_fallback_process_false"
    extents = bounds[1] - bounds[0]
    if np.any(extents <= 0.0):
        raise GeometryImportError(f"STL has non-positive bounding-box extent: {source}")
    if expected_size_mm is None:
        size_status = "not_checked"
    else:
        size_status = "match" if np.all(np.abs(extents - expected_size_mm) <= size_tolerance_mm) else "mismatch"
    if topology_qa:
        mesh = _load_mesh(source)
        watertight: bool | None = bool(mesh.is_watertight)
        euler_number: int | None = int(mesh.euler_number)
        unique_vertices: int | None = int(len(mesh.vertices))
        topology_status = "checked"
    else:
        watertight = None
        euler_number = None
        unique_vertices = None
        topology_status = "not_checked"
    return {
        "source_geometry_file": source.name,
        "source_geometry_path": str(source),
        "source_geometry_sha256": sha256_file(source),
        "source_geometry_size_bytes": int(source.stat().st_size),
        "mesh_vertex_record_count_import": vertex_record_count,
        "mesh_unique_vertex_count_import": unique_vertices,
        "mesh_face_count_import": face_count,
        "mesh_is_watertight_import": watertight,
        "mesh_euler_number_import": euler_number,
        "mesh_parser_import": parser,
        "mesh_topology_qa_status": topology_status,
        "mesh_qa_processing": "trimesh_process_true_in_memory_only" if topology_qa else "none_fast_intake_only",
        "bbox_min_x_mm": float(bounds[0, 0]),
        "bbox_min_y_mm": float(bounds[0, 1]),
        "bbox_min_z_mm": float(bounds[0, 2]),
        "bbox_max_x_mm": float(bounds[1, 0]),
        "bbox_max_y_mm": float(bounds[1, 1]),
        "bbox_max_z_mm": float(bounds[1, 2]),
        "physical_size_x_mm": float(extents[0]),
        "physical_size_y_mm": float(extents[1]),
        "physical_size_z_mm": float(extents[2]),
        "expected_size_mm": expected_size_mm,
        "size_check_status": size_status,
        "mesh_qa_status": "passed",
    }


def build_stl_import_table(config: STLImportConfig) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for source in discover_stl_files(config):
        model_id = _model_id(source)
        family, generator_type = _family_and_generator(model_id)
        row = {
            "candidate_id": model_id,
            "model_id": model_id,
            "base_geometry_id": f"BASEGEOM::{model_id}",
            "family_id": family,
            "generator_type": generator_type,
            "status": "ok",
            "source_mode": "import_stl",
            "geometry_role": "external_import",
            "geometry_format": "stl",
            "stl_path": str(source),
            "import_enabled": True,
        }
        row.update(
            inspect_stl(
                source,
                expected_size_mm=config.expected_size_mm,
                size_tolerance_mm=config.size_tolerance_mm,
                topology_qa=config.topology_qa,
            )
        )
        rows.append(row)
    table = pd.DataFrame(rows)
    if table.empty:
        return table
    duplicate_ids = table.loc[table["candidate_id"].duplicated(keep=False), "candidate_id"].unique().tolist()
    if duplicate_ids:
        raise GeometryImportError(f"duplicate model/candidate IDs after filename parsing: {duplicate_ids}")
    return table.sort_values(["family_id", "candidate_id", "source_geometry_file"], kind="stable").reset_index(drop=True)


def iter_source_hashes(table: pd.DataFrame) -> Iterable[tuple[str, str]]:
    for row in table.itertuples(index=False):
        yield str(row.stl_path), str(row.source_geometry_sha256)
