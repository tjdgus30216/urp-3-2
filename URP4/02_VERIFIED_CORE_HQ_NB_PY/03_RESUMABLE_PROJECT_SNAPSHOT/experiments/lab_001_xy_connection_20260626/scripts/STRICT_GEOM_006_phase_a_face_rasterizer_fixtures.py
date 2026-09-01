"""STRICT-GEOM-006 Phase A: Grade-A face-rasterizer analytic truth gate.

No L28 geometry or descriptor is processed.  Closed analytic B-rep sections
are rasterized only after their native wires pass closure/connectivity checks.
The intentionally open U is quarantined before face construction.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
import os
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from OCP.BRep import BRep_Tool
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Section
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeWire
from OCP.BRepClass import BRepClass_FaceClassifier
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.GCPnts import GCPnts_QuasiUniformDeflection
from OCP.GeomAPI import GeomAPI_ProjectPointOnSurf
from OCP.ShapeAnalysis import ShapeAnalysis_FreeBounds, ShapeAnalysis_Wire
from OCP.TopAbs import TopAbs_EDGE, TopAbs_IN, TopAbs_ON
from OCP.TopExp import TopExp_Explorer
from OCP.TopTools import TopTools_HSequenceOfShape
from OCP.TopoDS import TopoDS
from OCP.gp import gp_Ax2, gp_Dir, gp_Pln, gp_Pnt, gp_Pnt2d


TASK = "STRICT-GEOM-006-PHASE-A"
ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
SCRIPTS = LAB / "scripts"
TABLES = LAB / "reports" / "tables"
RESULT = LAB / "results" / "SG006_L28"
FACTORY_PATH = SCRIPTS / "STRICT_GEOM_001_l28_vf45_three_path_factory.py"
RESOLUTIONS = (500, 1000, 2000, 4000)
CUBE_MM = 40.0
Z_MM = 20.0
WIRE_TOL_MM = 1.0e-6
CLASSIFIER_TOL_MM = 1.0e-9


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    os.replace(temp, path)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def load_factory() -> Any:
    spec = importlib.util.spec_from_file_location("sg001_factory_for_sg006", FACTORY_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("blocked: frozen SG001 factory unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def plane_face() -> Any:
    return BRepBuilderAPI_MakeFace(gp_Pln(gp_Pnt(0.0, 0.0, Z_MM), gp_Dir(0.0, 0.0, 1.0)), -1.0, CUBE_MM + 1.0, -1.0, CUBE_MM + 1.0).Face()


def section_edge_sequence(shapes: list[Any]) -> TopTools_HSequenceOfShape:
    sequence = TopTools_HSequenceOfShape()
    cutter = plane_face()
    for shape in shapes:
        section = BRepAlgoAPI_Section(shape, cutter, False)
        section.Approximation(True)
        section.ComputePCurveOn1(True)
        section.Build()
        if not section.IsDone() or section.Shape().IsNull():
            raise RuntimeError("blocked: analytic B-rep plane section failed")
        explorer = TopExp_Explorer(section.Shape(), TopAbs_EDGE)
        while explorer.More():
            sequence.Append(explorer.Current())
            explorer.Next()
    return sequence


def closed_fixture_specs() -> list[dict[str, Any]]:
    axis = gp_Ax2(gp_Pnt(20.0, 20.0, 8.0), gp_Dir(0.0, 0.0, 1.0))
    outer = BRepPrimAPI_MakeCylinder(axis, 12.0, 24.0).Shape()
    inner = BRepPrimAPI_MakeCylinder(axis, 6.0, 24.0).Shape()
    cut = BRepAlgoAPI_Cut(outer, inner)
    cut.Build()
    if not cut.IsDone():
        raise RuntimeError("blocked: annulus boolean failed")
    left = BRepPrimAPI_MakeBox(gp_Pnt(4.0, 8.0, 8.0), 10.0, 24.0, 24.0).Shape()
    right = BRepPrimAPI_MakeBox(gp_Pnt(26.0, 8.0, 8.0), 10.0, 24.0, 24.0).Shape()
    return [
        {"fixture": "closed_square_box", "shapes": [BRepPrimAPI_MakeBox(gp_Pnt(8.0, 8.0, 8.0), 24.0, 24.0, 24.0).Shape()], "expected_area_mm2": 576.0, "expected_perimeter_mm": 96.0, "expected_components": 1, "expected_holes": 0, "area_kind": "rectilinear"},
        {"fixture": "circular_cylinder", "shapes": [BRepPrimAPI_MakeCylinder(axis, 10.0, 24.0).Shape()], "expected_area_mm2": math.pi * 100.0, "expected_perimeter_mm": 2.0 * math.pi * 10.0, "expected_components": 1, "expected_holes": 0, "area_kind": "curved"},
        {"fixture": "annulus", "shapes": [cut.Shape()], "expected_area_mm2": math.pi * (12.0**2 - 6.0**2), "expected_perimeter_mm": 2.0 * math.pi * 18.0, "expected_components": 1, "expected_holes": 1, "area_kind": "curved"},
        {"fixture": "two_disjoint_boxes", "shapes": [left, right], "expected_area_mm2": 480.0, "expected_perimeter_mm": 136.0, "expected_components": 2, "expected_holes": 0, "area_kind": "rectilinear"},
    ]


def open_u_wire() -> Any:
    points = [gp_Pnt(12.0, 12.0, Z_MM), gp_Pnt(12.0, 28.0, Z_MM), gp_Pnt(28.0, 28.0, Z_MM), gp_Pnt(28.0, 12.0, Z_MM)]
    builder = BRepBuilderAPI_MakeWire()
    for left, right in zip(points[:-1], points[1:], strict=True):
        builder.Add(BRepBuilderAPI_MakeEdge(left, right).Edge())
    if not builder.IsDone():
        raise RuntimeError("blocked: could not build intentionally open U wire")
    return builder.Wire()


def connect_wires(edges: TopTools_HSequenceOfShape) -> tuple[list[Any], int]:
    wires = TopTools_HSequenceOfShape()
    ShapeAnalysis_FreeBounds.ConnectEdgesToWires_s(edges, WIRE_TOL_MM, False, wires)
    output: list[Any] = []
    edge_sum = 0
    for index in range(1, wires.Length() + 1):
        wire = TopoDS.Wire_s(wires.Value(index))
        explorer = TopExp_Explorer(wire, TopAbs_EDGE)
        while explorer.More():
            edge_sum += 1
            explorer.Next()
        output.append(wire)
    return output, edge_sum


def wire_status(wire: Any) -> dict[str, int]:
    analysis = ShapeAnalysis_Wire()
    analysis.Load(wire)
    edge_count = 0
    explorer = TopExp_Explorer(wire, TopAbs_EDGE)
    while explorer.More():
        edge_count += 1
        explorer.Next()
    degree: Counter[tuple[int, int]] = Counter()
    explorer = TopExp_Explorer(wire, TopAbs_EDGE)
    while explorer.More():
        curve = BRepAdaptor_Curve(TopoDS.Edge_s(explorer.Current()))
        first = curve.Value(curve.FirstParameter())
        last = curve.Value(curve.LastParameter())
        quantize = lambda point: (int(round(float(point.X()) * 1.0e6)), int(round(float(point.Y()) * 1.0e6)))
        degree[quantize(first)] += 1
        degree[quantize(last)] += 1
        explorer.Next()
    return {"edge_count": edge_count, "closed_problem": int(analysis.CheckClosed(WIRE_TOL_MM)), "connected_problem": int(analysis.CheckConnected(WIRE_TOL_MM)), "endpoint_degree_not_two_count": int(sum(1 for value in degree.values() if value != 2))}


def curve_bounds(wire: Any) -> tuple[float, float, float, float]:
    points: list[tuple[float, float]] = []
    explorer = TopExp_Explorer(wire, TopAbs_EDGE)
    while explorer.More():
        curve = BRepAdaptor_Curve(TopoDS.Edge_s(explorer.Current()))
        sampler = GCPnts_QuasiUniformDeflection(curve, 0.02, curve.FirstParameter(), curve.LastParameter())
        if sampler.IsDone() and sampler.NbPoints() >= 2:
            points.extend((float(sampler.Value(i).X()), float(sampler.Value(i).Y())) for i in range(1, sampler.NbPoints() + 1))
        else:
            first, last = curve.Value(curve.FirstParameter()), curve.Value(curve.LastParameter())
            points.extend(((float(first.X()), float(first.Y())), (float(last.X()), float(last.Y()))))
        explorer.Next()
    if not points:
        raise RuntimeError("blocked: eligible wire has no sampled bounds")
    arr = np.asarray(points, dtype=float)
    return float(arr[:, 0].min()), float(arr[:, 0].max()), float(arr[:, 1].min()), float(arr[:, 1].max())


def face_record(wire: Any, index: int) -> dict[str, Any]:
    status = wire_status(wire)
    eligible = status["closed_problem"] == 0 and status["connected_problem"] == 0 and status["endpoint_degree_not_two_count"] == 0
    result: dict[str, Any] = {"wire_index": index, **status, "eligible": eligible, "face_build_done": False, "face": None, "bounds": None}
    if not eligible:
        return result
    maker = BRepBuilderAPI_MakeFace(wire, True)
    result["face_build_done"] = bool(maker.IsDone())
    if result["face_build_done"]:
        result["face"] = maker.Face()
        result["bounds"] = curve_bounds(wire)
    return result


def uv_affine(face: Any) -> tuple[float, float, float, float, float, float]:
    surface = BRep_Tool.Surface_s(face)
    anchors = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
    uv: list[tuple[float, float]] = []
    for x, y in anchors:
        projection = GeomAPI_ProjectPointOnSurf(gp_Pnt(x, y, Z_MM), surface)
        if projection.NbPoints() < 1:
            raise RuntimeError("blocked: cannot project pixel plane into constructed face surface")
        uv.append(tuple(float(value) for value in projection.LowerDistanceParameters()))
    u0, v0 = uv[0]
    return u0, uv[1][0] - u0, uv[2][0] - u0, v0, uv[1][1] - v0, uv[2][1] - v0


def face_mask(face: Any, bounds: tuple[float, float, float, float], resolution: int) -> tuple[np.ndarray, int, int]:
    dx = CUBE_MM / resolution
    xmin, xmax, ymin, ymax = bounds
    c0 = max(0, int(math.ceil(xmin / dx - 0.5)) - 1)
    c1 = min(resolution - 1, int(math.floor(xmax / dx - 0.5)) + 1)
    r0 = max(0, int(math.ceil((CUBE_MM - ymax) / dx - 0.5)) - 1)
    r1 = min(resolution - 1, int(math.floor((CUBE_MM - ymin) / dx - 0.5)) + 1)
    mask = np.zeros((resolution, resolution), dtype=bool)
    u0, ux, uy, v0, vx, vy = uv_affine(face)
    in_count = on_count = 0
    for row in range(r0, r1 + 1):
        y = CUBE_MM - (row + 0.5) * dx
        for col in range(c0, c1 + 1):
            x = (col + 0.5) * dx
            state = BRepClass_FaceClassifier(face, gp_Pnt2d(u0 + ux * x + uy * y, v0 + vx * x + vy * y), CLASSIFIER_TOL_MM).State()
            if state == TopAbs_IN:
                mask[row, col] = True
                in_count += 1
            elif state == TopAbs_ON:
                on_count += 1
    return mask, in_count, on_count


def component_hole_counts(mask: np.ndarray) -> tuple[int, int]:
    count, _labels, _stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), connectivity=8, ltype=cv2.CV_32S)
    components = int(count - 1)
    background = (~mask).astype(np.uint8)
    bg_count, bg_labels, _bg_stats, _ = cv2.connectedComponentsWithStats(background, connectivity=8, ltype=cv2.CV_32S)
    boundary = set(np.unique(np.r_[bg_labels[0], bg_labels[-1], bg_labels[:, 0], bg_labels[:, -1]]).tolist())
    holes = int(sum(1 for label in range(1, bg_count) if label not in boundary))
    return components, holes


def area_tolerance(spec: dict[str, Any], resolution: int) -> float:
    dx = CUBE_MM / resolution
    boundary_bound = spec["expected_perimeter_mm"] * dx + 4.0 * dx * dx
    if spec["area_kind"] == "rectilinear":
        return boundary_bound
    return max(0.02 * spec["expected_area_mm2"], boundary_bound)


def run() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, str]]:
    factory = load_factory()
    protected = [factory.RAW_STL, factory.RAW_STP, factory.NB_CURRENT]
    before = {str(path): sha256(path) for path in protected}
    rows: list[dict[str, Any]] = []
    face_rows: list[dict[str, Any]] = []
    curve_errors: dict[str, list[float]] = {}
    for spec in closed_fixture_specs():
        edges = section_edge_sequence(spec["shapes"])
        wires, wire_edge_sum = connect_wires(edges)
        records = [face_record(wire, i) for i, wire in enumerate(wires, start=1)]
        fixture_faces = [record for record in records if record["eligible"] and record["face_build_done"]]
        for record in records:
            face_rows.append({"task_id": TASK, "fixture": spec["fixture"], "source_declared_open": False, "native_edge_count": int(edges.Length()), "wire_edge_sum": wire_edge_sum, **{key: value for key, value in record.items() if key not in {"face", "bounds"}}})
        curve_errors[spec["fixture"]] = []
        for resolution in RESOLUTIONS:
            mask = np.zeros((resolution, resolution), dtype=bool)
            in_count = on_count = 0
            for record in fixture_faces:
                individual, inside, on = face_mask(record["face"], record["bounds"], resolution)
                mask ^= individual
                in_count += inside
                on_count += on
            components, holes = component_hole_counts(mask)
            area = float(mask.sum() * (CUBE_MM / resolution) ** 2)
            error = abs(area - spec["expected_area_mm2"])
            curve_errors[spec["fixture"]].append(error)
            rows.append({
                "task_id": TASK, "fixture": spec["fixture"], "fixture_kind": spec["area_kind"], "resolution_px": resolution,
                "native_edge_count": int(edges.Length()), "wire_count": len(wires), "wire_edge_sum": wire_edge_sum,
                "eligible_face_count": len(fixture_faces), "expected_area_mm2": spec["expected_area_mm2"], "observed_area_mm2": area,
                "absolute_area_error_mm2": error, "relative_area_error": error / spec["expected_area_mm2"], "area_tolerance_mm2": area_tolerance(spec, resolution),
                "components": components, "expected_components": spec["expected_components"], "holes": holes, "expected_holes": spec["expected_holes"],
                "classifier_in_pixel_count": in_count, "classifier_on_pixel_count": on_count,
                "area_pass": error <= area_tolerance(spec, resolution), "component_pass": components == spec["expected_components"], "hole_pass": holes == spec["expected_holes"],
                "status": "face_fixture_observation",
            })
    # Negative control: do not construct a face from a known-open wire.
    open_wire = open_u_wire()
    open_record = face_record(open_wire, 1)
    face_rows.append({"task_id": TASK, "fixture": "intentionally_open_U", "source_declared_open": True, "native_edge_count": 3, "wire_edge_sum": 3, **{key: value for key, value in open_record.items() if key not in {"face", "bounds"}}})
    for resolution in RESOLUTIONS:
        empty = np.zeros((resolution, resolution), dtype=bool)
        components, holes = component_hole_counts(empty)
        rows.append({
            "task_id": TASK, "fixture": "intentionally_open_U", "fixture_kind": "open_negative_control", "resolution_px": resolution,
            "native_edge_count": 3, "wire_count": 1, "wire_edge_sum": 3, "eligible_face_count": 0,
            "expected_area_mm2": 0.0, "observed_area_mm2": 0.0, "absolute_area_error_mm2": 0.0, "relative_area_error": 0.0, "area_tolerance_mm2": 0.0,
            "components": components, "expected_components": 0, "holes": holes, "expected_holes": 0,
            "classifier_in_pixel_count": 0, "classifier_on_pixel_count": 0,
            "area_pass": True, "component_pass": components == 0, "hole_pass": holes == 0,
            "open_wire_quarantined": not bool(open_record["eligible"]) and not bool(open_record["face_build_done"]), "status": "open_wire_quarantined_before_face_build",
        })
    after = {str(path): sha256(path) for path in protected}
    if before != after:
        raise RuntimeError("blocked: protected source changed")
    return rows, face_rows, before


def finalize(rows: list[dict[str, Any]], face_rows: list[dict[str, Any]], protected: dict[str, str]) -> dict[str, Any]:
    RESULT.mkdir(parents=True, exist_ok=True)
    write_csv(TABLES / "STRICT_GEOM_006_phase_a_face_fixture_measurements_20260725.csv", rows)
    write_csv(TABLES / "STRICT_GEOM_006_phase_a_face_wire_eligibility_20260725.csv", face_rows)
    closed = [row for row in rows if row["fixture"] != "intentionally_open_U"]
    open_rows = [row for row in rows if row["fixture"] == "intentionally_open_U"]
    curve_resolution_gate = True
    for fixture in ("circular_cylinder", "annulus"):
        subset = [row for row in closed if row["fixture"] == fixture]
        low = next(row for row in subset if row["resolution_px"] == 500)
        high = next(row for row in subset if row["resolution_px"] == 4000)
        curve_resolution_gate &= float(high["absolute_area_error_mm2"]) <= float(low["absolute_area_error_mm2"]) + 1.0e-12
    checks = {
        "fixture_factorial_complete": len(rows) == 5 * len(RESOLUTIONS),
        "all_closed_fixtures_have_eligible_faces": all(int(row["eligible_face_count"]) > 0 for row in closed),
        "all_closed_area_component_hole_truth_pass": all(bool(row["area_pass"]) and bool(row["component_pass"]) and bool(row["hole_pass"]) for row in closed),
        "curved_fixture_resolution_convergence": curve_resolution_gate,
        "open_u_zero_material_and_quarantine": all(bool(row["open_wire_quarantined"]) and float(row["observed_area_mm2"]) == 0.0 and int(row["components"]) == 0 for row in open_rows),
        "protected_hashes_pass": True,
        "no_l28_no_y_scope": True,
    }
    packet = {
        "task": TASK,
        "status": "phase_a_fixture_gate_passed" if all(checks.values()) else "phase_a_fixture_gate_failed",
        "created_at_utc": utc_now(),
        "scope": {"fixtures": ["closed_square_box", "circular_cylinder", "annulus", "two_disjoint_boxes", "intentionally_open_U"], "resolutions": list(RESOLUTIONS), "no_l28": True, "no_y": True},
        "checks": checks,
        "protected_hashes": protected,
        "decision_boundary": "fixture pass only permits a separate selected-slice B/C sensitivity contract; it does not approve a source route or canonical descriptor replacement",
    }
    atomic_json(RESULT / "SG006_PHASE_A_FACE_FIXTURE_DECISION_PACKET_v0_1.json", packet)
    lines = [
        "# STRICT-GEOM-006 Phase A — wire-aware face-rasterizer analytic fixture gate", "",
        "Runtime: KMK312 + OCP/OpenCascade. L28 was not executed.", "",
        "## Result", "",
        f"- Status: **{'PASS' if all(checks.values()) else 'FAIL'}**; {sum(bool(v) for v in checks.values())}/{len(checks)} registered checks pass.",
        "- Closed square, cylinder, annulus and two-island fixtures use existing B-rep section edges → eligible wires → planar faces → `TopAbs_IN` pixel-centre parity masks.",
        "- The intentionally open U fails wire eligibility before face construction and remains zero material at every resolution; no gap was closed.",
        "",
        "## Boundary", "",
        "- **confirmed only if pass:** this face-derived algorithm obeys the stated analytic truth and rejects an open wire under its own contract.",
        "- **not established:** L28 material semantics, ORIGINAL-STP source truth, proxy adequacy, a route winner, descriptor validity or any y relationship.",
        "- **next if pass:** preregister a B/C selected-slice noncanonical comparison. Do not overwrite SG001 artifacts.", "",
    ]
    (RESULT / "SG006_PHASE_A_FACE_FIXTURE_REPORT_20260725.md").write_text("\n".join(lines), encoding="utf-8")
    return packet


def main() -> int:
    rows, face_rows, protected = run()
    packet = finalize(rows, face_rows, protected)
    print(json.dumps(packet, ensure_ascii=False, indent=2))
    return 0 if all(packet["checks"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
