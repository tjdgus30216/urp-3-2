"""Deterministic STL export and optional analytical FreeCAD STEP backend."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import trimesh

from urp4.contracts.v0_1.canonical import sha256_file

from .models import ExportAttempt, GenerationConfig, LatticeGraph


def _cylinder_between(first: np.ndarray, second: np.ndarray, radius: float, sections: int) -> trimesh.Trimesh | None:
    vector = np.asarray(second, dtype=float) - np.asarray(first, dtype=float)
    height = float(np.linalg.norm(vector))
    if height <= 1e-9 or radius <= 1e-12:
        return None
    mesh = trimesh.creation.cylinder(radius=float(radius), height=height, sections=sections)
    transform = trimesh.geometry.align_vectors(np.array([0.0, 0.0, 1.0]), vector / height)
    transform[:3, 3] = 0.5 * (np.asarray(first) + np.asarray(second))
    mesh.apply_transform(transform)
    return mesh


def build_cylinder_sphere_mesh(graph: LatticeGraph, config: GenerationConfig) -> trimesh.Trimesh:
    meshes: list[trimesh.Trimesh] = []
    node_radii = np.zeros(len(graph.nodes), dtype=float)
    for edge_index, (first, second) in enumerate(graph.edges):
        radius = float(graph.radii[edge_index])
        node_radii[int(first)] = max(node_radii[int(first)], radius)
        node_radii[int(second)] = max(node_radii[int(second)], radius)
        cylinder = _cylinder_between(graph.nodes[int(first)], graph.nodes[int(second)], radius, config.cylinder_sections)
        if cylinder is not None:
            meshes.append(cylinder)
    for node_index, point in enumerate(graph.nodes):
        sphere = trimesh.creation.icosphere(
            subdivisions=config.node_sphere_subdivisions, radius=max(float(node_radii[node_index]), 1e-6)
        )
        sphere.apply_translation(np.asarray(point, dtype=float))
        meshes.append(sphere)
    if not meshes:
        raise ValueError("No mesh primitives were generated")
    return trimesh.util.concatenate(meshes)


def export_stl(graph: LatticeGraph, path: str | Path, config: GenerationConfig) -> ExportAttempt:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    mesh = build_cylinder_sphere_mesh(graph, config)
    output.write_bytes(mesh.export(file_type="stl"))
    return ExportAttempt("stl", "passed", output.as_posix(), sha256_file(output), output.stat().st_size, "TRIMESH-CYLINDER-SPHERE-v0.1", "")


def _freecad_modules(library_path: str | None = None):
    if library_path and library_path not in sys.path:
        sys.path.append(library_path)
    try:
        import FreeCAD  # type: ignore
        import Part  # type: ignore
        from FreeCAD import Base  # type: ignore
    except Exception:
        return None, None, None
    return FreeCAD, Part, Base


def export_step_optional(
    graph: LatticeGraph, path: str | Path, config: GenerationConfig, freecad_library_path: str | None = None
) -> ExportAttempt:
    output = Path(path)
    freecad, part, base_api = _freecad_modules(freecad_library_path)
    if freecad is None or part is None:
        return ExportAttempt(
            "stp", "unavailable", None, None, None, "FREECAD-PART-ANALYTICAL-v0.1",
            "FreeCAD/Part Python modules are absent; notebook source also returns False and emits no STP in this environment.",
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    document = freecad.newDocument("urp4_lattice_step_export")
    try:
        shapes = []
        node_radii = np.zeros(len(graph.nodes), dtype=float)
        for edge_index, (first, second) in enumerate(graph.edges):
            radius = float(graph.radii[edge_index])
            node_radii[int(first)] = max(node_radii[int(first)], radius)
            node_radii[int(second)] = max(node_radii[int(second)], radius)
            p0, p1 = graph.nodes[int(first)], graph.nodes[int(second)]
            vector = p1 - p0
            height = float(np.linalg.norm(vector))
            if height <= config.min_edge_length_mm or radius <= 0:
                continue
            shapes.append(part.makeCylinder(radius, height, base_api.Vector(*map(float, p0)), base_api.Vector(*map(float, vector))))
        fallback_radius = float(np.mean(graph.radii))
        for index, point in enumerate(graph.nodes):
            shapes.append(part.makeSphere(max(float(node_radii[index]), fallback_radius), base_api.Vector(*map(float, point))))
        part.Compound(shapes).exportStep(str(output))
    finally:
        freecad.closeDocument(document.Name)
    return ExportAttempt("stp", "passed", output.as_posix(), sha256_file(output), output.stat().st_size, "FREECAD-PART-ANALYTICAL-v0.1", "")


def mesh_qa(path: str | Path) -> dict[str, object]:
    # Binary STL repeats vertices per triangle. ``process=True`` welds those
    # serialization duplicates before edge-incidence QA; otherwise every face
    # is incorrectly reported as an isolated open body.
    mesh = trimesh.load_mesh(Path(path), file_type="stl", process=True)
    if not isinstance(mesh, trimesh.Trimesh):
        raise ValueError("STL did not load as one Trimesh")
    incidence = np.bincount(mesh.edges_unique_inverse, minlength=len(mesh.edges_unique))
    bounds = mesh.bounds
    extent = bounds[1] - bounds[0]
    boundary_count = int(np.sum(incidence == 1))
    nonmanifold_count = int(np.sum(incidence > 2))
    finite = len(mesh.faces) > 0 and np.isfinite(mesh.vertices).all()
    if not finite or boundary_count > 0:
        technical_status = "fail_open_or_invalid"
        topology_status = "open_or_invalid"
    elif nonmanifold_count > 0:
        technical_status = "pass_with_topology_warning"
        topology_status = "overlapping_primitives_nonmanifold_not_boolean_unioned"
    else:
        technical_status = "pass"
        topology_status = "closed_compound_not_boolean_unioned"
    return {
        "technical_status": technical_status,
        "topology_status": topology_status,
        "connected_region_count": int(mesh.body_count),
        "boundary_edge_count": boundary_count,
        "nonmanifold_edge_count": nonmanifold_count,
        "vertex_count": int(len(mesh.vertices)),
        "face_count": int(len(mesh.faces)),
        "bbox_x_mm": float(extent[0]), "bbox_y_mm": float(extent[1]), "bbox_z_mm": float(extent[2]),
    }
