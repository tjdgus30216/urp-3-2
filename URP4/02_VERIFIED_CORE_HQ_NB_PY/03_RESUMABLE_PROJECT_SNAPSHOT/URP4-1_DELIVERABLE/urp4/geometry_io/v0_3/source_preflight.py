"""Read-only source router and geometry preflight for IMSTL-001.

This module does not repair, normalize, slice, or overwrite geometry.  Its
purpose is to make source identity and route policy explicit before later
algorithms touch a generated STL, imported STL, or original STEP/STP B-rep.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np
import trimesh


SOURCE_GENERATED_STL = "generated_stl"
SOURCE_IMPORTED_STL = "imported_stl"
SOURCE_ORIGINAL_STP = "original_stp"

ROUTE_GENERATED = "GEN-STL-NATIVE-CONTROLLED"
ROUTE_IMPORTED = "IMP-STL-ROBUST-DEV"
ROUTE_STP_REFERENCE = "IMP-STP-PERSOLID-REFERENCE"


class SourcePreflightError(RuntimeError):
    """Raised when source identity or immutable preflight cannot be proven."""


@dataclass(frozen=True)
class GeometrySourceRecord:
    model_id: str
    pair_id: str
    source_type: str
    path: Path
    geometry_revision: str
    expected_route_id: str = ""

    @classmethod
    def from_values(
        cls,
        *,
        model_id: str,
        pair_id: str,
        source_type: str,
        path: str | Path,
        geometry_revision: str,
        expected_route_id: str = "",
    ) -> "GeometrySourceRecord":
        return cls(
            model_id=str(model_id),
            pair_id=str(pair_id),
            source_type=str(source_type),
            path=Path(path).expanduser().resolve(),
            geometry_revision=str(geometry_revision),
            expected_route_id=str(expected_route_id),
        )


def sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def route_id_for_source_type(source_type: str) -> str:
    mapping = {
        SOURCE_GENERATED_STL: ROUTE_GENERATED,
        SOURCE_IMPORTED_STL: ROUTE_IMPORTED,
        SOURCE_ORIGINAL_STP: ROUTE_STP_REFERENCE,
    }
    try:
        return mapping[str(source_type)]
    except KeyError as exc:
        raise SourcePreflightError(f"Unsupported source_type={source_type!r}") from exc


def _load_stl_raw(path: Path) -> trimesh.Trimesh:
    loaded = trimesh.load(str(path), file_type="stl", process=False, force="mesh")
    if isinstance(loaded, trimesh.Scene):
        meshes = [g for g in loaded.geometry.values() if isinstance(g, trimesh.Trimesh)]
        if not meshes:
            raise SourcePreflightError(f"No mesh in STL scene: {path}")
        loaded = trimesh.util.concatenate(meshes)
    if not isinstance(loaded, trimesh.Trimesh) or len(loaded.faces) == 0:
        raise SourcePreflightError(f"No triangular mesh in STL: {path}")
    if not np.all(np.isfinite(np.asarray(loaded.vertices, dtype=float))):
        raise SourcePreflightError(f"Non-finite STL vertices: {path}")
    return loaded


def _inspect_stl(path: Path, *, weld_tolerance_mm: float) -> dict[str, Any]:
    raw = _load_stl_raw(path)
    vertices = np.asarray(raw.vertices, dtype=float)
    raw_faces = np.asarray(raw.faces, dtype=np.int64)
    if weld_tolerance_mm <= 0:
        raise SourcePreflightError("weld_tolerance_mm must be positive")

    quantized = np.rint(vertices / float(weld_tolerance_mm)).astype(np.int64)
    unique_keys, first_indices, inverse = np.unique(
        quantized, axis=0, return_index=True, return_inverse=True
    )
    del unique_keys
    welded_vertices = vertices[first_indices]
    welded_faces = inverse[raw_faces]

    repeated_vertex_face = np.any(
        np.column_stack(
            [
                welded_faces[:, 0] == welded_faces[:, 1],
                welded_faces[:, 1] == welded_faces[:, 2],
                welded_faces[:, 2] == welded_faces[:, 0],
            ]
        ),
        axis=1,
    )
    p0 = welded_vertices[welded_faces[:, 0]]
    p1 = welded_vertices[welded_faces[:, 1]]
    p2 = welded_vertices[welded_faces[:, 2]]
    double_area = np.linalg.norm(np.cross(p1 - p0, p2 - p0), axis=1)
    degenerate = repeated_vertex_face | (double_area <= 1.0e-12)

    canonical_faces = np.sort(welded_faces, axis=1)
    _, face_counts = np.unique(canonical_faces, axis=0, return_counts=True)
    duplicate_faces = int(np.maximum(face_counts - 1, 0).sum())

    directed_edges = np.vstack(
        [
            welded_faces[:, [0, 1]],
            welded_faces[:, [1, 2]],
            welded_faces[:, [2, 0]],
        ]
    )
    canonical_edges = np.sort(directed_edges, axis=1)
    unique_edges, edge_inverse, edge_counts = np.unique(
        canonical_edges, axis=0, return_inverse=True, return_counts=True
    )
    signs = np.where(directed_edges[:, 0] < directed_edges[:, 1], 1, -1)
    direction_sum = np.bincount(edge_inverse, weights=signs, minlength=len(unique_edges))
    boundary_edges = int(np.count_nonzero(edge_counts == 1))
    manifold_edges = int(np.count_nonzero(edge_counts == 2))
    nonmanifold_edges = int(np.count_nonzero(edge_counts > 2))
    orientation_conflicts = int(np.count_nonzero((edge_counts == 2) & (np.abs(direction_sum) == 2)))

    valid_face_mask = ~degenerate
    merged = trimesh.Trimesh(
        vertices=welded_vertices,
        faces=welded_faces[valid_face_mask],
        process=False,
        validate=False,
    )
    try:
        component_count = int(len(merged.split(only_watertight=False)))
    except Exception:
        component_count = -1

    bounds = np.asarray(raw.bounds, dtype=float)
    extents = bounds[1] - bounds[0]
    signed_volume = float(merged.volume)
    is_watertight = bool(merged.is_watertight)
    winding_consistent = bool(merged.is_winding_consistent)
    topology_clean = bool(
        boundary_edges == 0
        and nonmanifold_edges == 0
        and orientation_conflicts == 0
        and int(np.count_nonzero(degenerate)) == 0
        and duplicate_faces == 0
        and is_watertight
    )
    return {
        "geometry_format": "stl",
        "weld_tolerance_mm": float(weld_tolerance_mm),
        "raw_vertex_record_count": int(len(vertices)),
        "welded_unique_vertex_count": int(len(welded_vertices)),
        "duplicate_vertex_record_count": int(len(vertices) - len(welded_vertices)),
        "triangle_count": int(len(raw_faces)),
        "degenerate_triangle_count": int(np.count_nonzero(degenerate)),
        "duplicate_triangle_count": duplicate_faces,
        "unique_edge_count": int(len(unique_edges)),
        "boundary_edge_count": boundary_edges,
        "manifold_edge_count": manifold_edges,
        "nonmanifold_edge_count": nonmanifold_edges,
        "orientation_conflict_edge_count": orientation_conflicts,
        "normal_winding_consistent": winding_consistent,
        "connected_component_count": component_count,
        "is_watertight_after_weld": is_watertight,
        "signed_volume_mm3_after_weld": signed_volume,
        "bbox_min_x": float(bounds[0, 0]),
        "bbox_min_y": float(bounds[0, 1]),
        "bbox_min_z": float(bounds[0, 2]),
        "bbox_max_x": float(bounds[1, 0]),
        "bbox_max_y": float(bounds[1, 1]),
        "bbox_max_z": float(bounds[1, 2]),
        "extent_x": float(extents[0]),
        "extent_y": float(extents[1]),
        "extent_z": float(extents[2]),
        "topology_clean": topology_clean,
    }


def _count_subshapes(shape: Any, shape_kind: Any) -> int:
    from OCP.TopExp import TopExp_Explorer

    explorer = TopExp_Explorer(shape, shape_kind)
    count = 0
    while explorer.More():
        count += 1
        explorer.Next()
    return count


def _inspect_step(path: Path) -> dict[str, Any]:
    try:
        from OCP.BRepBndLib import BRepBndLib
        from OCP.BRepCheck import BRepCheck_Analyzer
        from OCP.Bnd import Bnd_Box
        from OCP.IFSelect import IFSelect_RetDone
        from OCP.STEPControl import STEPControl_Reader
        from OCP.TopAbs import TopAbs_FACE, TopAbs_SHELL, TopAbs_SOLID
    except Exception as exc:  # pragma: no cover - machine specific
        raise SourcePreflightError("OCP is required for original STP preflight") from exc

    reader = STEPControl_Reader()
    status = reader.ReadFile(str(path))
    if status != IFSelect_RetDone or reader.TransferRoots() < 1:
        raise SourcePreflightError(f"STEP read/transfer failed: {path}")
    shape = reader.OneShape()
    if shape.IsNull():
        raise SourcePreflightError(f"STEP returned a null shape: {path}")
    box = Bnd_Box()
    BRepBndLib.Add_s(shape, box)
    bbox = tuple(float(v) for v in box.Get())
    extents = (bbox[3] - bbox[0], bbox[4] - bbox[1], bbox[5] - bbox[2])
    valid = bool(BRepCheck_Analyzer(shape).IsValid())
    solid_count = _count_subshapes(shape, TopAbs_SOLID)
    shell_count = _count_subshapes(shape, TopAbs_SHELL)
    face_count = _count_subshapes(shape, TopAbs_FACE)
    return {
        "geometry_format": path.suffix.lower().lstrip("."),
        "step_brep_valid": valid,
        "step_solid_count": solid_count,
        "step_shell_count": shell_count,
        "step_face_count": face_count,
        "bbox_min_x": bbox[0],
        "bbox_min_y": bbox[1],
        "bbox_min_z": bbox[2],
        "bbox_max_x": bbox[3],
        "bbox_max_y": bbox[4],
        "bbox_max_z": bbox[5],
        "extent_x": extents[0],
        "extent_y": extents[1],
        "extent_z": extents[2],
        "topology_clean": bool(valid and solid_count > 0),
    }


def inspect_source(
    record: GeometrySourceRecord,
    *,
    weld_tolerance_mm: float = 1.0e-7,
) -> dict[str, Any]:
    path = record.path
    if not path.is_file():
        raise SourcePreflightError(f"Source does not exist: {path}")
    route_id = route_id_for_source_type(record.source_type)
    if record.expected_route_id and record.expected_route_id != route_id:
        raise SourcePreflightError(
            f"Route mismatch for {record.model_id}: expected={record.expected_route_id}, actual={route_id}"
        )
    suffix = path.suffix.lower()
    if record.source_type in {SOURCE_GENERATED_STL, SOURCE_IMPORTED_STL}:
        if suffix != ".stl":
            raise SourcePreflightError(f"{record.source_type} requires .stl: {path}")
        metrics = _inspect_stl(path, weld_tolerance_mm=weld_tolerance_mm)
    else:
        if suffix not in {".stp", ".step"}:
            raise SourcePreflightError(f"original_stp requires .stp/.step: {path}")
        metrics = _inspect_step(path)

    topology_clean = bool(metrics["topology_clean"])
    if record.source_type == SOURCE_GENERATED_STL:
        route_status = "ready_controlled_existing"
        preflight_action = "retain_generated_route_and_regression_guard"
    elif record.source_type == SOURCE_IMPORTED_STL:
        route_status = "ready_for_robust_dev" if topology_clean else "ready_for_robust_dev_with_mesh_risk"
        preflight_action = "send_to_imported_robust_slicer; never_silent_step_proxy"
    else:
        route_status = "reference_ready" if topology_clean else "reference_blocked"
        preflight_action = "use_as_paired_reference" if topology_clean else "block_reference"

    return {
        "model_id": record.model_id,
        "pair_id": record.pair_id,
        "source_type": record.source_type,
        "route_id": route_id,
        "route_status": route_status,
        "preflight_action": preflight_action,
        "geometry_revision": record.geometry_revision,
        "source_path": str(path),
        "source_sha256": sha256_file(path),
        "source_size_bytes": int(path.stat().st_size),
        **metrics,
    }
