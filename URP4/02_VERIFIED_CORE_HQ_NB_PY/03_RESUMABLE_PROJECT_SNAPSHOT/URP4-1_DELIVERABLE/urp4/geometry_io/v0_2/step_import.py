"""STEP-first geometry intake.

This module deliberately separates source formats:

* Existing ``.stp/.step`` files are read as B-rep solids with OCP/OpenCascade.
* ``.stl`` is never silently treated as an equivalent B-rep.  It is converted
  to a *facet-derived STEP proxy* only when explicitly allowed and its lineage
  remains ``stl_to_step_proxy``.

The proxy permits one reproducible code path when a STEP source is absent, but
does not recover analytical CAD surfaces or erase STL discretisation error.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import re
from typing import Any, Iterable

import numpy as np


class GeometryRouteError(RuntimeError):
    """Raised when a requested STEP-preferred route cannot be proven."""


@dataclass(frozen=True)
class GeometryRouteConfig:
    input_paths: tuple[str, ...]
    recursive: bool = True
    expected_size_mm: float | None = 40.0
    size_tolerance_mm: float = 1.0e-3
    normalize_to_size_mm: float | None = 40.0
    tessellation_deflection_mm: float = 0.10
    tessellation_angle_rad: float = 0.35
    allow_stl_to_step_proxy: bool = True
    conversion_output_dir: str = ""

    @classmethod
    def from_values(cls, **kwargs: Any) -> "GeometryRouteConfig":
        paths = kwargs.pop("input_paths", ())
        if isinstance(paths, (str, Path)):
            paths = (str(paths),)
        return cls(input_paths=tuple(str(x) for x in paths), **kwargs)


MODEL_ID_RE = re.compile(r"(?<![A-Za-z0-9])([BCLFT]\d{1,2})(?![A-Za-z0-9])", re.IGNORECASE)
STEP_SUFFIXES = {".stp", ".step"}


def sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _model_id_from_path(path: Path) -> str | None:
    match = MODEL_ID_RE.search(path.stem)
    return match.group(1).upper() if match else None


def _iter_geometry_files(paths: Iterable[str], recursive: bool) -> list[Path]:
    files: list[Path] = []
    for raw in paths:
        root = Path(raw).expanduser().resolve()
        if not root.exists():
            raise GeometryRouteError(f"Input path does not exist: {root}")
        if root.is_file():
            files.append(root)
            continue
        iterator = root.rglob("*") if recursive else root.glob("*")
        files.extend(p for p in iterator if p.is_file() and p.suffix.lower() in {*STEP_SUFFIXES, ".stl"})
    return sorted(set(files), key=lambda p: p.as_posix().lower())


def inventory_step_preferred_inputs(config: GeometryRouteConfig) -> list[dict[str, Any]]:
    """Inventory one selected source per parsable model ID, preferring STEP."""
    files = _iter_geometry_files(config.input_paths, config.recursive)
    grouped: dict[str, list[Path]] = {}
    unparsed: list[str] = []
    for path in files:
        model_id = _model_id_from_path(path)
        if model_id is None:
            unparsed.append(str(path))
            continue
        grouped.setdefault(model_id, []).append(path)

    rows: list[dict[str, Any]] = []
    for model_id in sorted(grouped):
        candidates = grouped[model_id]
        steps = [p for p in candidates if p.suffix.lower() in STEP_SUFFIXES]
        stls = [p for p in candidates if p.suffix.lower() == ".stl"]
        # Multiple STEP files are allowed only when the user resolves the source
        # registry.  Selecting one alphabetically would hide an identity choice.
        if len(steps) > 1:
            rows.append({
                "candidate_id": model_id,
                "geometry_route": "blocked_ambiguous_step",
                "source_geometry_format": "step",
                "source_geometry_path": "",
                "source_sha256": "",
                "route_status": "blocked",
                "route_reason": f"multiple STEP/STEP candidates: {[p.name for p in steps]}",
                "available_step_count": len(steps),
                "available_stl_count": len(stls),
            })
            continue
        if len(steps) == 1:
            chosen = steps[0]
            route = "step_direct_brep"
            fmt = "step"
            reason = "direct STEP/STEP B-rep source selected over any STL sibling"
        elif len(stls) == 1:
            chosen = stls[0]
            route = "stl_to_step_proxy" if config.allow_stl_to_step_proxy else "blocked_no_step"
            fmt = "stl"
            reason = "no STEP source; STL must be converted to a facet-derived STEP proxy" if config.allow_stl_to_step_proxy else "no STEP source and STL conversion is disabled"
        elif len(stls) > 1:
            rows.append({
                "candidate_id": model_id,
                "geometry_route": "blocked_ambiguous_stl",
                "source_geometry_format": "stl",
                "source_geometry_path": "",
                "source_sha256": "",
                "route_status": "blocked",
                "route_reason": f"multiple STL candidates: {[p.name for p in stls]}",
                "available_step_count": 0,
                "available_stl_count": len(stls),
            })
            continue
        else:
            continue
        rows.append({
            "candidate_id": model_id,
            "geometry_route": route,
            "source_geometry_format": fmt,
            "source_geometry_path": str(chosen),
            "source_sha256": sha256_file(chosen),
            "source_byte_size": chosen.stat().st_size,
            "route_status": "ready" if route != "blocked_no_step" else "blocked",
            "route_reason": reason,
            "available_step_count": len(steps),
            "available_stl_count": len(stls),
        })
    if unparsed:
        rows.append({
            "candidate_id": "__UNPARSED__",
            "geometry_route": "unparsed_filename",
            "source_geometry_format": "",
            "source_geometry_path": " | ".join(unparsed),
            "source_sha256": "",
            "route_status": "blocked",
            "route_reason": "model ID parser could not derive B/C/L/F/T ID",
            "available_step_count": 0,
            "available_stl_count": 0,
        })
    return rows


def _ocp_modules() -> dict[str, Any]:
    try:
        from OCP.BRep import BRep_Builder, BRep_Tool
        from OCP.BRepBndLib import BRepBndLib
        from OCP.BRepBuilderAPI import (
            BRepBuilderAPI_MakeFace,
            BRepBuilderAPI_MakePolygon,
            BRepBuilderAPI_Sewing,
            BRepBuilderAPI_Transform,
        )
        from OCP.BRepCheck import BRepCheck_Analyzer
        from OCP.BRepGProp import BRepGProp
        from OCP.BRepMesh import BRepMesh_IncrementalMesh
        from OCP.Bnd import Bnd_Box
        from OCP.GProp import GProp_GProps
        from OCP.IFSelect import IFSelect_RetDone
        from OCP.STEPControl import STEPControl_AsIs, STEPControl_Reader, STEPControl_Writer
        from OCP.TopAbs import TopAbs_FACE
        from OCP.TopExp import TopExp_Explorer
        from OCP.TopLoc import TopLoc_Location
        from OCP.TopoDS import TopoDS, TopoDS_Compound
        from OCP.gp import gp_Pnt, gp_Trsf
    except Exception as exc:  # pragma: no cover - machine-specific backend
        raise GeometryRouteError(
            "OCP/OpenCascade STEP backend unavailable. Install cadquery-ocp plus compatible vtk in KMK312."
        ) from exc
    return locals()


def _shape_bbox(shape: Any, ocp: dict[str, Any]) -> tuple[float, float, float, float, float, float]:
    box = ocp["Bnd_Box"]()
    ocp["BRepBndLib"].Add_s(shape, box)
    return tuple(float(v) for v in box.Get())


def _shape_volume(shape: Any, ocp: dict[str, Any]) -> float:
    props = ocp["GProp_GProps"]()
    ocp["BRepGProp"].VolumeProperties_s(shape, props)
    return float(props.Mass())


def _normalize_shape(shape: Any, config: GeometryRouteConfig, ocp: dict[str, Any]) -> tuple[Any, float, tuple[float, ...]]:
    bbox = _shape_bbox(shape, ocp)
    extents = np.array([bbox[3] - bbox[0], bbox[4] - bbox[1], bbox[5] - bbox[2]], dtype=float)
    if np.any(extents <= 0):
        raise GeometryRouteError(f"Invalid STEP B-rep bounding extents: {extents.tolist()}")
    target = config.normalize_to_size_mm
    if target is None:
        return shape, 1.0, bbox
    scale = float(target) / float(np.max(extents))
    if abs(scale - 1.0) <= 1e-12:
        return shape, 1.0, bbox
    center = ocp["gp_Pnt"](
        float((bbox[0] + bbox[3]) / 2.0),
        float((bbox[1] + bbox[4]) / 2.0),
        float((bbox[2] + bbox[5]) / 2.0),
    )
    transform = ocp["gp_Trsf"]()
    transform.SetScale(center, scale)
    normalized = ocp["BRepBuilderAPI_Transform"](shape, transform, True).Shape()
    return normalized, scale, bbox


def _read_step_shape(path: Path, ocp: dict[str, Any]) -> Any:
    reader = ocp["STEPControl_Reader"]()
    status = reader.ReadFile(str(path))
    if status != ocp["IFSelect_RetDone"]:
        raise GeometryRouteError(f"STEP reader failed with status={status}: {path}")
    if reader.NbRootsForTransfer() < 1 or reader.TransferRoots() < 1:
        raise GeometryRouteError(f"STEP reader could not transfer a root shape: {path}")
    shape = reader.OneShape()
    if shape.IsNull():
        raise GeometryRouteError(f"STEP reader returned null shape: {path}")
    return shape


def _shape_to_arrays(shape: Any, config: GeometryRouteConfig, ocp: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    ocp["BRepMesh_IncrementalMesh"](
        shape,
        float(config.tessellation_deflection_mm),
        False,
        float(config.tessellation_angle_rad),
        True,
    )
    vertices: list[list[float]] = []
    faces: list[list[int]] = []
    explorer = ocp["TopExp_Explorer"](shape, ocp["TopAbs_FACE"])
    while explorer.More():
        face = ocp["TopoDS"].Face_s(explorer.Current())
        location = ocp["TopLoc_Location"]()
        triangulation = ocp["BRep_Tool"].Triangulation_s(face, location)
        if triangulation is not None and triangulation.NbTriangles() > 0:
            offset = len(vertices)
            transform = location.Transformation()
            for index in range(1, triangulation.NbNodes() + 1):
                point = triangulation.Node(index).Transformed(transform)
                vertices.append([float(point.X()), float(point.Y()), float(point.Z())])
            for index in range(1, triangulation.NbTriangles() + 1):
                a, b, c = triangulation.Triangle(index).Get()
                faces.append([offset + int(a) - 1, offset + int(b) - 1, offset + int(c) - 1])
        explorer.Next()
    V = np.asarray(vertices, dtype=float)
    F = np.asarray(faces, dtype=np.int64)
    if len(V) == 0 or len(F) == 0:
        raise GeometryRouteError("STEP B-rep tessellation yielded no triangles")
    return V, F


def _stl_to_step_proxy(stl_path: Path, output_path: Path, ocp: dict[str, Any]) -> dict[str, Any]:
    """Make a facet-derived STEP proxy; never call it recovered analytical CAD."""
    try:
        import trimesh
    except Exception as exc:  # pragma: no cover
        raise GeometryRouteError("trimesh is required for STL→STEP proxy conversion") from exc
    mesh = trimesh.load_mesh(stl_path, force="mesh", process=True)
    if mesh.is_empty or len(mesh.faces) == 0 or not bool(mesh.is_watertight):
        raise GeometryRouteError(
            f"STL→STEP proxy requires a processed watertight mesh; {stl_path.name} is not a closed volume"
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    compound = ocp["TopoDS_Compound"]()
    builder = ocp["BRep_Builder"]()
    builder.MakeCompound(compound)
    sewing = ocp["BRepBuilderAPI_Sewing"](1.0e-7)
    for tri in np.asarray(mesh.faces, dtype=int):
        points = np.asarray(mesh.vertices[tri], dtype=float)
        polygon = ocp["BRepBuilderAPI_MakePolygon"]()
        for x, y, z in points:
            polygon.Add(ocp["gp_Pnt"](float(x), float(y), float(z)))
        polygon.Close()
        face = ocp["BRepBuilderAPI_MakeFace"](polygon.Wire(), True).Face()
        sewing.Add(face)
    sewing.Perform()
    shape = sewing.SewedShape()
    if shape.IsNull():
        raise GeometryRouteError(f"STL→STEP proxy sewing returned null shape for {stl_path.name}")
    writer = ocp["STEPControl_Writer"]()
    transfer_status = writer.Transfer(shape, ocp["STEPControl_AsIs"])
    if int(transfer_status) != 1:
        raise GeometryRouteError(f"STL→STEP proxy transfer failed with status={transfer_status}")
    write_status = writer.Write(str(output_path))
    if int(write_status) != 1 or not output_path.exists():
        raise GeometryRouteError(f"STL→STEP proxy write failed with status={write_status}")
    return {
        "analysis_geometry_path": str(output_path),
        "proxy_shape_valid": bool(ocp["BRepCheck_Analyzer"](shape).IsValid()),
        "proxy_face_count": int(len(mesh.faces)),
    }


def prepare_analysis_geometry(row: dict[str, Any], config: GeometryRouteConfig) -> dict[str, Any]:
    """Load a route row as B-rep, normalize it and return analysis mesh arrays.

    Returned arrays are transient descriptor inputs.  The original STEP remains
    untouched; a converted STL proxy, when needed, is written only below the
    configured processed output directory and is explicitly tagged as a proxy.
    """
    if row.get("route_status") != "ready":
        raise GeometryRouteError(f"Geometry row is not ready: {row.get('route_reason', '')}")
    ocp = _ocp_modules()
    source = Path(str(row["source_geometry_path"])).resolve()
    route = str(row["geometry_route"])
    analysis_path = source
    proxy_meta: dict[str, Any] = {}
    if route == "stl_to_step_proxy":
        if not config.allow_stl_to_step_proxy:
            raise GeometryRouteError("STL→STEP proxy route disabled")
        if not config.conversion_output_dir:
            raise GeometryRouteError("conversion_output_dir is required for STL→STEP proxy route")
        destination = Path(config.conversion_output_dir).resolve() / f"{row['candidate_id']}__mesh_proxy.stp"
        if not destination.exists():
            proxy_meta = _stl_to_step_proxy(source, destination, ocp)
        else:
            proxy_meta = {"analysis_geometry_path": str(destination), "proxy_reused": True}
        analysis_path = destination
    elif route != "step_direct_brep":
        raise GeometryRouteError(f"Unsupported geometry route: {route}")

    shape = _read_step_shape(analysis_path, ocp)
    source_bbox = _shape_bbox(shape, ocp)
    source_extents = [source_bbox[3] - source_bbox[0], source_bbox[4] - source_bbox[1], source_bbox[5] - source_bbox[2]]
    valid = bool(ocp["BRepCheck_Analyzer"](shape).IsValid())
    normalized, scale, _ = _normalize_shape(shape, config, ocp)
    bbox = _shape_bbox(normalized, ocp)
    extents = [bbox[3] - bbox[0], bbox[4] - bbox[1], bbox[5] - bbox[2]]
    V, F = _shape_to_arrays(normalized, config, ocp)
    return {
        "vertices": V,
        "faces": F,
        "geometry_route": route,
        "source_geometry_path": str(source),
        "analysis_geometry_path": str(analysis_path),
        "source_geometry_format": str(row.get("source_geometry_format", "")),
        "source_sha256": str(row.get("source_sha256", "")),
        "analysis_sha256": sha256_file(analysis_path),
        "step_brep_valid": valid,
        "step_source_bbox": source_bbox,
        "step_source_extents_mm": source_extents,
        "step_normalization_scale": float(scale),
        "step_analysis_bbox": bbox,
        "step_analysis_extents_mm": extents,
        "step_brep_volume_mm3": _shape_volume(normalized, ocp),
        "step_tessellation_deflection_mm": float(config.tessellation_deflection_mm),
        "step_tessellation_angle_rad": float(config.tessellation_angle_rad),
        "analysis_mesh_vertex_count": int(len(V)),
        "analysis_mesh_face_count": int(len(F)),
        **proxy_meta,
    }
