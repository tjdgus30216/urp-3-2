"""Source-exact binary STL export plus transparent mesh QA."""

from __future__ import annotations

import struct
from pathlib import Path

import numpy as np
import trimesh

from urp4.contracts.v0_1.canonical import sha256_file

from .models import ExportAttempt, VoxelGenerationResult


def write_binary_stl(path: str | Path, vertices: np.ndarray, faces: np.ndarray, solid_name: str = "mesh") -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    vertices = np.asarray(vertices, dtype=np.float32)
    faces = np.asarray(faces, dtype=np.int32)
    triangle_vertices = vertices[faces]
    p0, p1, p2 = triangle_vertices[:, 0, :], triangle_vertices[:, 1, :], triangle_vertices[:, 2, :]
    normals = np.cross(p1 - p0, p2 - p0)
    norms = np.linalg.norm(normals, axis=1)
    valid = norms > 1e-12
    normals[valid] = normals[valid] / norms[valid, None]
    normals[~valid] = 0.0
    records = np.zeros(len(faces), dtype=[("normal", "<f4", (3,)), ("vertices", "<f4", (3, 3)), ("attr", "<u2")])
    records["normal"] = normals.astype(np.float32)
    records["vertices"] = triangle_vertices.astype(np.float32)
    header = solid_name[:70].encode("ascii", errors="ignore")
    header = header + b" " * (80 - len(header))
    with output.open("wb") as handle:
        handle.write(header)
        handle.write(struct.pack("<I", len(faces)))
        records.tofile(handle)
    return output


def export_stl(result: VoxelGenerationResult, path: str | Path) -> ExportAttempt:
    output = write_binary_stl(path, result.vertices, result.faces, result.candidate.candidate_id)
    return ExportAttempt("stl", "passed", output.as_posix(), sha256_file(output), output.stat().st_size, "SOURCE-BINARY-STL-MARCHING-CUBES-v0.1", "Exact notebook binary STL layout; no silent repair.")


def mesh_qa(path: str | Path) -> dict[str, object]:
    mesh = trimesh.load_mesh(Path(path), file_type="stl", process=True)
    if not isinstance(mesh, trimesh.Trimesh):
        raise ValueError("STL did not load as one Trimesh")
    incidence = np.bincount(mesh.edges_unique_inverse, minlength=len(mesh.edges_unique))
    extent = mesh.bounds[1] - mesh.bounds[0]
    boundary = int(np.sum(incidence == 1))
    nonmanifold = int(np.sum(incidence > 2))
    finite = len(mesh.faces) > 0 and np.isfinite(mesh.vertices).all()
    technical = "fail_open_or_invalid" if (not finite or boundary > 0) else ("pass_with_topology_warning" if nonmanifold > 0 else "pass")
    topology = "open_or_invalid" if (not finite or boundary > 0) else ("source_equivalent_nonmanifold_marching_cubes" if nonmanifold > 0 else "closed_2_manifold")
    return {
        "technical_status": technical,
        "topology_status": topology,
        "connected_region_count": int(mesh.body_count),
        "boundary_edge_count": boundary,
        "nonmanifold_edge_count": nonmanifold,
        "vertex_count": int(len(mesh.vertices)),
        "face_count": int(len(mesh.faces)),
        "bbox_x_mm": float(extent[0]),
        "bbox_y_mm": float(extent[1]),
        "bbox_z_mm": float(extent[2]),
        "watertight": bool(mesh.is_watertight),
    }

