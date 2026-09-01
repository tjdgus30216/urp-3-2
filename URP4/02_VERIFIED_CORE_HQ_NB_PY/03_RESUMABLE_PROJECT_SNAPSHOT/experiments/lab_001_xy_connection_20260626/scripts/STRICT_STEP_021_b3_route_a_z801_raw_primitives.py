"""STRICT-STEP-021 — resumable B3 Route-A Z801 raw primitive extraction.

The only geometry route is original STEP direct B-rep face rasterization.
It writes raw slice/overlay component populations for later LEGACY-PY replay;
it deliberately computes no final descriptor scalar and never opens y data.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import sys
import time
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
RUN_ID = "STRICT-STEP-021-20260730-001"
WORK_ID = "STRICT-STEP-021_B3_ROUTE_A_DIRECT_STEP_Z801_RAW_COMPONENT_OVERLAY_PRIMITIVES_NO_Y"
OUT = LAB / "results" / "STRICT-STEP-021" / RUN_ID
SOURCE = LAB / "data" / "raw" / "notion_reference_models_20260701" / "stp" / "B3-Basic_Cubic-BCC_Lattice.stp"
SOURCE_SHA256 = "b17a3c9a4ee56cf55b87204e6f7021b39f18c87a2657d4480cfda5b29fe8e0fe"
STRICT020 = LAB / "results" / "STRICT-STEP-020" / "STRICT-STEP-020-20260730-001" / "INDEPENDENT_QA.json"
PROTECTED = LAB / "results" / "HQ-BLUEPRINT-001" / "PROTECTED_ASSET_BASELINE.json"
STRICT007 = LAB / "scripts" / "STRICT_STEP_007_overlay_trace_execution.py"

SETTINGS_INDEX = "IDX-URP4-1-GEOM-DIRECT-STEP"
CONFIG_ID = "CFG-STRICTSTEP021-B3-N40-Z801-P1000-PHASE00-ROUTEA-RAWPRIMITIVES"
CONFIG_REVISION = "r1"
RESOLUTION = 1000
SLICE_COUNT = 801
HEIGHT_MM = 0.05
MIN_COMPONENT_PIXELS = 2
ANCHOR_INDICES = {0, 200, 400, 600, 800}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tree_hash(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(p for p in path.rglob("*") if p.is_file() and "__pycache__" not in p.parts):
        digest.update(item.relative_to(path).as_posix().encode("utf-8") + b"\0")
        digest.update(sha256(item).encode("ascii") + b"\0")
        digest.update(str(item.stat().st_size).encode("ascii") + b"\n")
    return digest.hexdigest()


def load_helper():
    spec = importlib.util.spec_from_file_location("strict_step_021_ss007", STRICT007)
    if spec is None or spec.loader is None:
        raise RuntimeError("STRICT-STEP-007 helper unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def append_rows(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists() and path.stat().st_size > 0
    with path.open("a", newline="", encoding="utf-8-sig" if not exists else "utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        if not exists:
            writer.writeheader()
        writer.writerows(rows)


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def protected_audit() -> list[dict[str, object]]:
    rows = []
    for item in json.loads(PROTECTED.read_text(encoding="utf-8"))["assets"]:
        path = ROOT / item["path"]
        observed = tree_hash(path) if item["asset_kind"] == "tree" else sha256(path)
        rows.append({"alias": item["alias"], "status": "passed" if observed == item["before_sha256"] else "failed"})
    return rows


def write_state(**fields: object) -> None:
    state = {"run_id": RUN_ID, "work_id": WORK_ID, **fields}
    (OUT / "RUN_STATE.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def init_or_validate() -> None:
    runtime = Path(sys.executable).resolve()
    if "kmk312" not in str(runtime).lower() or sys.version_info[:2] != (3, 12):
        raise RuntimeError("STRICT-STEP-021 requires project-local KMK312 Python 3.12")
    if sha256(SOURCE) != SOURCE_SHA256:
        raise RuntimeError("frozen B3 STEP source SHA-256 mismatch")
    if json.loads(STRICT020.read_text(encoding="utf-8"))["checks"]["status"] != "passed":
        raise RuntimeError("STRICT-STEP-020 prerequisite is not passed")
    protected = protected_audit()
    if len(protected) != 31 or not all(row["status"] == "passed" for row in protected):
        raise RuntimeError("protected asset audit failed before execution")
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = OUT / "CONTRACT_MANIFEST.json"
    if not manifest.exists():
        payload = {
            "work_id": WORK_ID, "run_id": RUN_ID, "status": "running_or_resumable",
            "settings": f"{SETTINGS_INDEX} / {CONFIG_ID} {CONFIG_REVISION}",
            "runtime": {"sys_executable": str(runtime), "python_version": sys.version},
            "source": {"path": str(SOURCE), "sha256": SOURCE_SHA256},
            "predecessor": {"strict_step_020": str(STRICT020), "status": "passed"},
            "route": "A only: original STEP direct B-rep section → eligible closed faces → TopAbs_IN XOR mask",
            "analysis": {"domain": "N40", "axis": "z", "slice_count": SLICE_COUNT, "resolution_px": RESOLUTION, "pixel_phase": "PHASE-00", "height_mm": HEIGHT_MM, "min_component_pixels": MIN_COMPONENT_PIXELS},
            "retention": {"all_masks": "in_memory_only", "retained_anchor_indices": sorted(ANCHOR_INDICES), "raw_csv_tables": "append_checkpoint"},
            "scope_guards": {"route_b_not_executed": True, "no_final_descriptor_scalars": True, "no_y": True, "no_excel": True, "no_feature_selection": True, "no_training": True, "no_all58": True, "no_nb_or_legacy_mutation": True},
        }
        manifest.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        append_rows(OUT / "PROTECTED_ASSET_AUDIT_BEFORE.csv", protected)


def direct_mask(helper, sg, local_shape, z_mm: float) -> tuple[np.ndarray, dict[str, object]]:
    sg.Z_MM = z_mm
    edges = sg.section_edge_sequence([local_shape])
    wires, _ = sg.connect_wires(edges)
    records = [sg.face_record(wire, index) for index, wire in enumerate(wires, start=1)]
    faces = [record for record in records if record["eligible"] and record["face_build_done"]]
    if not faces:
        # A zero-edge exterior boundary plane is a physically empty section,
        # not a broken contour.  It must be retained as an explicit empty mask.
        # Any nonzero-edge plane with no eligible face remains fail-closed.
        if int(edges.Length()) == 0:
            return np.zeros((RESOLUTION, RESOLUTION), dtype=bool), {
                "native_section_edge_count": 0, "eligible_wire_count": 0,
                "quarantined_wire_count": 0, "empty_boundary_section": True,
            }
        raise RuntimeError(f"route A has no eligible closed B-rep face at z={z_mm}; fail closed")
    return helper.fmask(sg, faces, RESOLUTION), {
        "native_section_edge_count": int(edges.Length()),
        "eligible_wire_count": len(faces),
        "quarantined_wire_count": len(records) - len(faces),
    }


def component_stats(mask: np.ndarray):
    return cv2.connectedComponentsWithStats(mask.astype(np.uint8), connectivity=8, ltype=cv2.CV_32S)


def slice_tables(mask: np.ndarray, slice_index: int, z_mm: float, meta: dict[str, object]) -> tuple[list[dict[str, object]], dict[str, object]]:
    count, labels, stats, _ = component_stats(mask)
    dx = 40.0 / RESOLUTION
    area_per_pixel = dx * dx
    rows = []
    for label in range(1, count):
        x, y, width, height, pixels = (int(value) for value in stats[label])
        rows.append({"run_id": RUN_ID, "route_id": "A_DIRECT_BREP", "slice_index": slice_index, "z_mm": z_mm, "component_label": label, "pixel_count": pixels, "area_mm2": pixels * area_per_pixel, "bbox_x_px": x, "bbox_y_px": y, "bbox_w_px": width, "bbox_h_px": height, "retained_ge_2px": pixels >= MIN_COMPONENT_PIXELS})
    retained = [row for row in rows if row["retained_ge_2px"]]
    total = {"run_id": RUN_ID, "route_id": "A_DIRECT_BREP", "slice_index": slice_index, "z_mm": z_mm, "foreground_pixels": int(mask.sum()), "area_mm2": float(mask.sum() * area_per_pixel), "raw_component_count": count - 1, "retained_component_count": len(retained), "min_component_pixels": MIN_COMPONENT_PIXELS, **meta}
    return rows, total


def contact_length(mask_a: np.ndarray, mask_b: np.ndarray, dx: float) -> float:
    # Exact morphology policy in LEGACY2 get_contact_edge_length: one 3x3 dilation then overlap.
    contact = cv2.bitwise_and(cv2.dilate(mask_a.astype(np.uint8), np.ones((3, 3), np.uint8), iterations=1), mask_b.astype(np.uint8))
    return float(cv2.countNonZero(contact) * dx)


def overlay_tables(previous: np.ndarray, current: np.ndarray, pair_index: int, z_lower: float, z_upper: float) -> tuple[list[dict[str, object]], dict[str, object], np.ndarray]:
    red = previous & ~current
    blue = ~previous & current
    purple = previous & current
    union = red | blue | purple
    count, labels, stats, _ = component_stats(union)
    dx = 40.0 / RESOLUTION
    area_per_pixel = dx * dx
    rows = []
    for label in range(1, count):
        component = labels == label
        rp = int((red & component).sum()); bp = int((blue & component).sum()); pp = int((purple & component).sum())
        x, y, width, height, pixels = (int(value) for value in stats[label])
        mask_component = component.astype(np.uint8)
        contours, _ = cv2.findContours(mask_component, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        perimeter_px = float(cv2.arcLength(contours[0], True)) if contours else 0.0
        label_red = (red & component).astype(np.uint8)
        label_blue = (blue & component).astype(np.uint8)
        label_purple = (purple & component).astype(np.uint8)
        rows.append({"run_id": RUN_ID, "route_id": "A_DIRECT_BREP", "pair_index": pair_index, "z_lower_mm": z_lower, "z_upper_mm": z_upper, "component_label": label, "pixel_count": pixels, "red_pixels": rp, "blue_pixels": bp, "purple_pixels": pp, "red_area_mm2": rp * area_per_pixel, "blue_area_mm2": bp * area_per_pixel, "purple_area_mm2": pp * area_per_pixel, "contact_red_purple_mm": contact_length(label_red, label_purple, dx), "contact_blue_purple_mm": contact_length(label_blue, label_purple, dx), "perimeter_px": perimeter_px, "perimeter_mm": perimeter_px * dx, "bbox_x_px": x, "bbox_y_px": y, "bbox_w_px": width, "bbox_h_px": height, "retained_ge_2px": pixels >= MIN_COMPONENT_PIXELS})
    total = {"run_id": RUN_ID, "route_id": "A_DIRECT_BREP", "pair_index": pair_index, "z_lower_mm": z_lower, "z_upper_mm": z_upper, "total_red_pixels": int(red.sum()), "total_blue_pixels": int(blue.sum()), "total_purple_pixels": int(purple.sum()), "total_red_area_mm2": float(red.sum() * area_per_pixel), "total_blue_area_mm2": float(blue.sum() * area_per_pixel), "total_purple_area_mm2": float(purple.sum() * area_per_pixel), "union_component_count": count - 1, "retained_component_count": sum(row["retained_ge_2px"] for row in rows), "min_component_pixels": MIN_COMPONENT_PIXELS}
    rgb = np.zeros((*union.shape, 3), dtype=np.uint8)
    rgb[red] = (0, 0, 255); rgb[blue] = (255, 0, 0); rgb[purple] = (255, 0, 255)
    return rows, total, rgb


def reconstruct_previous(helper, sg, local_shape, slice_index: int, z_mm: float) -> np.ndarray:
    mask, _ = direct_mask(helper, sg, local_shape, z_mm)
    return mask


def main() -> None:
    global RUN_ID, OUT
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-new-slices", type=int, default=None, help="bounded smoke/restart increment; omit for all remaining slices")
    parser.add_argument("--run-id", default=RUN_ID, help="new immutable run id; never reuse a quarantined output folder")
    args = parser.parse_args()
    RUN_ID = str(args.run_id)
    OUT = LAB / "results" / "STRICT-STEP-021" / RUN_ID
    init_or_validate()
    start = time.perf_counter()
    helper = load_helper(); sg = helper.loadsg(); ocp = helper._ocp_modules()
    shape = helper._read_step_shape(SOURCE, ocp)
    normalized, _, _ = helper._normalize_shape(shape, helper.GeometryRouteConfig.from_values(input_paths=[str(SOURCE)], normalize_to_size_mm=40.0, allow_stl_to_step_proxy=False), ocp)
    bbox = helper._shape_bbox(normalized, ocp)
    transform = helper.gp_Trsf(); transform.SetTranslation(helper.gp_Vec(-bbox[0], -bbox[1], -bbox[2]))
    local_shape = helper.BRepBuilderAPI_Transform(normalized, transform, True).Shape()
    local_bbox = helper._shape_bbox(local_shape, ocp)
    if max(abs((local_bbox[i + 3] - local_bbox[i]) - 40.0) for i in range(3)) > 1e-8:
        raise RuntimeError("N40 local extent mismatch")
    z_values = np.linspace(np.nextafter(0.0, 40.0), np.nextafter(40.0, 0.0), SLICE_COUNT)
    slice_path = OUT / "slice_total_table.csv"; component_path = OUT / "slice_component_table.csv"; overlay_path = OUT / "overlay_total_table.csv"; overlay_component_path = OUT / "overlay_component_table.csv"
    done = {int(row["slice_index"]) for row in read_rows(slice_path)}
    expected_prefix = set(range(len(done)))
    if done != expected_prefix:
        raise RuntimeError("slice checkpoint is non-contiguous; quarantine instead of guessing resume state")
    next_index = len(done)
    if next_index >= SLICE_COUNT:
        write_state(status="completed", completed_slices=SLICE_COUNT, completed_overlays=SLICE_COUNT - 1, elapsed_seconds=0.0, note="already complete")
        print(json.dumps({"run_id": RUN_ID, "status": "already_completed"}, ensure_ascii=False)); return
    previous_mask = None
    if next_index > 0:
        previous_mask = reconstruct_previous(helper, sg, local_shape, next_index - 1, float(z_values[next_index - 1]))
    end_index = SLICE_COUNT if args.max_new_slices is None else min(SLICE_COUNT, next_index + args.max_new_slices)
    for index in range(next_index, end_index):
        z_mm = float(z_values[index])
        mask, meta = direct_mask(helper, sg, local_shape, z_mm)
        component_rows, total_row = slice_tables(mask, index, z_mm, meta)
        append_rows(component_path, component_rows); append_rows(slice_path, [total_row])
        if index in ANCHOR_INDICES:
            path = OUT / f"ANCHOR_SLICE_{index:04d}_Z{z_mm:.5f}.png"
            if not cv2.imwrite(str(path), mask.astype(np.uint8) * 255): raise RuntimeError("could not write anchor slice")
        if previous_mask is not None:
            overlay_rows, overlay_total, overlay_rgb = overlay_tables(previous_mask, mask, index - 1, float(z_values[index - 1]), z_mm)
            append_rows(overlay_component_path, overlay_rows); append_rows(overlay_path, [overlay_total])
            if index in ANCHOR_INDICES:
                path = OUT / f"ANCHOR_OVERLAY_{index - 1:04d}_{index:04d}.png"
                if not cv2.imwrite(str(path), overlay_rgb): raise RuntimeError("could not write anchor overlay")
        previous_mask = mask
        write_state(status="partial" if index + 1 < SLICE_COUNT else "completed", completed_slices=index + 1, completed_overlays=max(0, index), last_slice_index=index, last_z_mm=z_mm, elapsed_seconds=round(time.perf_counter() - start, 3), next_action="resume same command" if index + 1 < SLICE_COUNT else "run independent QA")
    state = json.loads((OUT / "RUN_STATE.json").read_text(encoding="utf-8"))
    print(json.dumps({"run_id": RUN_ID, "status": state["status"], "new_slices": end_index-next_index, "completed_slices": state["completed_slices"], "elapsed_seconds": state["elapsed_seconds"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
