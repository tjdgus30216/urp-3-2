"""ROUTE-VALID-003A: F1 z400 Exact-A attribution replay; no y.

This is intentionally a partial attribution run.  It calculates only six new
pixel-centre BRepClass3d_SolidClassifier masks (Exact A), then compares them
with hash-replayed Fast A, baseline B, and frozen imported-STL C masks.  No
new B deflection is invented: the only verified B setting is baseline 0.1 mm.
"""
from __future__ import annotations

import csv
import concurrent.futures
import hashlib
import importlib.util
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from OCP.BRepBuilderAPI import BRepBuilderAPI_GTransform
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.TopAbs import TopAbs_IN, TopAbs_ON
from OCP.gp import gp_GTrsf, gp_Mat, gp_Pnt, gp_Trsf, gp_Vec, gp_XYZ


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
SCRIPTS = LAB / "scripts"
TABLES = LAB / "reports" / "tables"
RUN_ID = "ROUTE-VALID-003A-20260729-003"
WORK_ID = "ROUTE-VALID-003A_F1_Z400_TARGETED_ATTRIBUTION_REPLAY_NO_Y"
RUN = LAB / "runs" / "ROUTE-VALID-003A" / RUN_ID
RESULT = LAB / "results" / "ROUTE-VALID-003A" / RUN_ID
RV003_RUN = LAB / "runs" / "ROUTE-VALID-003" / "ROUTE-VALID-003-20260729-002"
RV003_RESULT = LAB / "results" / "ROUTE-VALID-003" / "ROUTE-VALID-003-20260729-002"
RV003_SCRIPT = SCRIPTS / "ROUTE_VALID_003_f1_step_reference_pixel_phase.py"
RV003_QA = SCRIPTS / "ROUTE_VALID_003_independent_qa.py"
PROTECTED = LAB / "results" / "HQ-BLUEPRINT-001" / "PROTECTED_ASSET_BASELINE.json"

Z_INDEX = 400
Z_MM = 20.0
SIZE_MM = 40.0
RESOLUTIONS = (750, 1000, 1500)
PHASES = {"P00": (0.0, 0.0), "P50X": (0.5, 0.0)}
CLASSIFIER_TOL_MM = 1.0e-9
BASELINE_TESSELLATION_DEFLECTION_MM = 0.1
EXACT_WORKERS = min(8, max(1, (os.cpu_count() or 1)))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stable_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    keys = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def packed_mask_sha(mask: np.ndarray) -> str:
    packed = np.packbits(np.asarray(mask, dtype=np.uint8).reshape(-1), bitorder="big")
    return hashlib.sha256(packed.tobytes()).hexdigest()


def read_mask(path: Path) -> np.ndarray:
    raw = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if raw is None:
        raise RuntimeError(f"cannot read mask: {path}")
    values = set(np.unique(raw).tolist())
    if not values.issubset({0, 255}):
        raise RuntimeError(f"non-binary mask: {path}: {values}")
    return raw > 0


def write_mask(path: Path, mask: np.ndarray) -> tuple[str, str]:
    if path.exists():
        raise RuntimeError(f"refuse overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(path), np.asarray(mask, dtype=np.uint8) * 255):
        raise RuntimeError(f"cannot write mask: {path}")
    return sha256(path), packed_mask_sha(mask)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def protected_audit() -> list[dict[str, object]]:
    baseline = json.loads(PROTECTED.read_text(encoding="utf-8"))
    rows: list[dict[str, object]] = []
    for asset in baseline["assets"]:
        path = ROOT / asset["path"]
        observed = sha256(path) if path.is_file() else ""
        rows.append({"alias": asset["alias"], "path": asset["path"], "expected_sha256": asset["before_sha256"], "observed_sha256": observed, "passed": bool(path.is_file() and observed == asset["before_sha256"])})
    return rows


def bbox(diff: np.ndarray) -> str:
    yy, xx = np.where(diff)
    if len(xx) == 0:
        return ""
    return f"row={int(yy.min())}:{int(yy.max())};col={int(xx.min())}:{int(xx.max())}"


def topology(mask: np.ndarray, resolution: int) -> tuple[int, int]:
    binary = np.asarray(mask, dtype=np.uint8)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
    min_pixels = max(1, int(math.ceil(0.0032 / ((SIZE_MM / resolution) ** 2))))
    retained = np.zeros_like(binary)
    components = 0
    for label in range(1, count):
        if int(stats[label, cv2.CC_STAT_AREA]) >= min_pixels:
            retained[labels == label] = 1
            components += 1
    inverse = (1 - retained).astype(np.uint8)
    bg_count, bg_labels = cv2.connectedComponents(inverse, connectivity=8)
    border = set(np.unique(np.r_[bg_labels[0, :], bg_labels[-1, :], bg_labels[:, 0], bg_labels[:, -1]]).tolist())
    holes = sum(1 for label in range(1, bg_count) if label not in border)
    return components, int(holes)


def boundary_fraction(a: np.ndarray, b: np.ndarray) -> float:
    diff = np.logical_xor(a, b)
    n = int(diff.sum())
    if not n:
        return 1.0
    kernel = np.ones((5, 5), dtype=np.uint8)
    edge = cv2.morphologyEx(np.maximum(a, b).astype(np.uint8), cv2.MORPH_GRADIENT, kernel).astype(bool)
    return float(np.logical_and(diff, edge).sum() / n)


def compare(case: dict[str, object], name: str, reference: str, candidate: str, a: np.ndarray, b: np.ndarray) -> dict[str, object]:
    diff = np.logical_xor(a, b)
    inter = int(np.logical_and(a, b).sum())
    union = int(np.logical_or(a, b).sum())
    px_area = (SIZE_MM / int(case["resolution_px"])) ** 2
    ca, ha = topology(a, int(case["resolution_px"]))
    cb, hb = topology(b, int(case["resolution_px"]))
    return {
        **case, "comparison_id": name, "reference_route": reference, "candidate_route": candidate,
        "mask_iou": inter / union if union else 1.0, "exact": bool(not diff.any()),
        "symmetric_difference_pixels": int(diff.sum()), "symmetric_difference_area_mm2": float(diff.sum() * px_area),
        "relative_area_delta": abs(int(a.sum()) - int(b.sum())) / max(int(a.sum()), 1),
        "signed_solid_pixel_difference_candidate_minus_reference": int(b.sum()) - int(a.sum()),
        "reference_solid_pixels": int(a.sum()), "candidate_solid_pixels": int(b.sum()),
        "reference_component_count": ca, "candidate_component_count": cb,
        "reference_hole_count": ha, "candidate_hole_count": cb if False else hb,
        "difference_bbox": bbox(diff), "boundary_band_explained_fraction": boundary_fraction(a, b),
    }


def exact_classifier_chunk(payload: dict[str, object]) -> tuple[int, np.ndarray, dict[str, int]]:
    """One independent exact-classifier row shard; no geometric shortcut."""
    rv3 = load_module(f"rv003a_exact_{os.getpid()}", RV003_SCRIPT)
    tools = rv3.load_step_tools()
    ocp = tools._ocp_modules()
    raw = tools._read_step_shape(Path(str(payload["step_path"])), ocp)
    scale = payload["scale_xyz"]
    translation = payload["translation_xyz_mm"]
    matrix = gp_GTrsf()
    matrix.SetVectorialPart(gp_Mat(float(scale[0]), 0, 0, 0, float(scale[1]), 0, 0, 0, float(scale[2])))
    matrix.SetTranslationPart(gp_XYZ(float(translation[0]), float(translation[1]), float(translation[2])))
    shape = BRepBuilderAPI_GTransform(raw, matrix, True).Shape()
    if float(payload["phase_x_mm"]) or float(payload["phase_y_mm"]):
        shift = gp_Trsf(); shift.SetTranslation(gp_Vec(float(payload["phase_x_mm"]), float(payload["phase_y_mm"]), 0.0))
        shape = tools.BRepBuilderAPI_Transform(shape, shift, True).Shape()
    resolution, row_start, row_stop = int(payload["resolution"]), int(payload["row_start"]), int(payload["row_stop"])
    pixel = SIZE_MM / resolution
    classifier = BRepClass3d_SolidClassifier(shape)
    out = np.zeros((row_stop - row_start, resolution), dtype=bool)
    on_count = outside_count = other_count = 0
    for local_row, row in enumerate(range(row_start, row_stop)):
        y = SIZE_MM - (row + 0.5) * pixel
        for col in range(resolution):
            x = (col + 0.5) * pixel
            classifier.Perform(gp_Pnt(float(x), float(y), float(payload["z_mm"])), CLASSIFIER_TOL_MM)
            state = classifier.State()
            if state == TopAbs_IN:
                out[local_row, col] = True
            elif state == TopAbs_ON:
                on_count += 1
            elif state is None:
                other_count += 1
            else:
                outside_count += 1
    return row_start, out, {"boundary_state_count": on_count, "outside_state_count": outside_count, "other_state_count": other_count}


def exact_classifier_mask(step_path: Path, transform: dict[str, object], resolution: int, z_mm: float, phase_x_mm: float, phase_y_mm: float) -> tuple[np.ndarray, dict[str, object]]:
    """Original-style slow solid point classifier at every pixel centre.

    Inside rule is `TopAbs_IN`; TopAbs_ON is counted and excluded, matching the
    solid-interior interpretation rather than silently filling boundary points.
    """
    started = time.perf_counter()
    mask = np.zeros((resolution, resolution), dtype=bool)
    edges = np.linspace(0, resolution, min(EXACT_WORKERS, resolution) + 1, dtype=int)
    payloads = [{"step_path": str(step_path), "scale_xyz": transform["scale_xyz"], "translation_xyz_mm": transform["translation_xyz_mm"], "resolution": resolution, "row_start": int(edges[i]), "row_stop": int(edges[i + 1]), "z_mm": z_mm, "phase_x_mm": phase_x_mm, "phase_y_mm": phase_y_mm} for i in range(len(edges) - 1)]
    counts = {"boundary_state_count": 0, "outside_state_count": 0, "other_state_count": 0}
    with concurrent.futures.ProcessPoolExecutor(max_workers=len(payloads)) as pool:
        for row_start, block, local_counts in pool.map(exact_classifier_chunk, payloads):
            mask[row_start:row_start + len(block), :] = block
            for key in counts: counts[key] += int(local_counts[key])
    return mask, {"classifier_backend": "OCP.BRepClass3d.BRepClass3d_SolidClassifier (same pixel-centre semantics; row-sharded process execution)", "classifier_tolerance_mm": CLASSIFIER_TOL_MM, "pixel_center_convention": "x=(col+0.5)*pixel; y=40-(row+0.5)*pixel", "inside_rule": "TopAbs_IN=true; TopAbs_ON counted_and_excluded", "exact_algorithm": "each pixel centre is classified directly; no curve/tessellation shortcut", "worker_count": len(payloads), **counts, "runtime_s": time.perf_counter() - started}


def make_common_step(rv3: Any, contract: dict[str, object]) -> tuple[Any, Any, dict[str, object]]:
    tools = rv3.load_step_tools()
    ocp = tools._ocp_modules()
    step_path = ROOT / str(contract["source_step_relative_path"])
    raw = tools._read_step_shape(step_path, ocp)
    transform = contract["common_transform"]
    scale = np.asarray(transform["scale_xyz"], dtype=float)
    translation = np.asarray(transform["translation_xyz_mm"], dtype=float)
    matrix = gp_GTrsf()
    matrix.SetVectorialPart(gp_Mat(float(scale[0]), 0, 0, 0, float(scale[1]), 0, 0, 0, float(scale[2])))
    matrix.SetTranslationPart(gp_XYZ(float(translation[0]), float(translation[1]), float(translation[2])))
    return BRepBuilderAPI_GTransform(raw, matrix, True).Shape(), tools, {"step_path": step_path, "step_sha256": sha256(step_path)}


def panel(path: Path, masks: dict[str, np.ndarray], title: str) -> None:
    labels = ["ExactA", "FastA", "B", "C", "ExactA_xor_FastA", "ExactA_xor_B", "ExactA_xor_C"]
    sheets = [masks["ExactA"], masks["FastA"], masks["B"], masks["C"], np.logical_xor(masks["ExactA"], masks["FastA"]), np.logical_xor(masks["ExactA"], masks["B"]), np.logical_xor(masks["ExactA"], masks["C"])]
    tiles = []
    for label, image in zip(labels, sheets, strict=True):
        tile = np.dstack([image.astype(np.uint8) * 255] * 3)
        cv2.putText(tile, label, (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1, cv2.LINE_AA)
        tiles.append(tile)
    blank = np.zeros_like(tiles[0]); cv2.putText(blank, title, (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
    while len(tiles) < 8: tiles.append(blank.copy())
    sheet = np.vstack([np.hstack(tiles[:4]), np.hstack(tiles[4:8])])
    path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(path), sheet): raise RuntimeError(f"cannot write figure: {path}")


def main() -> None:
    if "kmk312" not in str(Path(sys.executable).resolve()).lower() or sys.version_info[:2] != (3, 12):
        raise RuntimeError("ROUTE-VALID-003A requires KMK312 Python 3.12.12")
    if RUN.exists() or RESULT.exists():
        raise RuntimeError(f"refuse overwrite run/result: {RUN_ID}")
    required = [RV003_RESULT / "REPORT.md", RV003_RESULT / "MERGE_PACKET.md", RV003_RESULT / "COMMON_RASTER_CONTRACT.json", RV003_RESULT / "INDEPENDENT_QA.json", RV003_RUN / "OUTPUT_MANIFEST.csv", PROTECTED, RV003_SCRIPT, RV003_QA]
    missing = [str(path) for path in required if not path.is_file()]
    if missing: raise RuntimeError(f"missing predecessor: {missing}")
    qa = json.loads((RV003_RESULT / "INDEPENDENT_QA.json").read_text(encoding="utf-8"))
    if qa.get("status") != "passed" or not all(dict(qa["checks"]).values()): raise RuntimeError("ROUTE-VALID-003 QA checkpoint is not passed")
    rv3 = load_module("rv003a_reuse", RV003_SCRIPT)
    contract = json.loads((RV003_RESULT / "COMMON_RASTER_CONTRACT.json").read_text(encoding="utf-8"))
    contract["source_step_relative_path"] = "experiments/lab_001_xy_connection_20260626/data/raw/notion_reference_models_20260701/stp/F1-Foam-Kelvin_foam.stp"
    if int(contract["selected_slice_indices"][4]) != Z_INDEX or abs(float(contract["selected_z_mm"]["400"]) - Z_MM) > 1e-12: raise RuntimeError("z400 contract mismatch")
    table_prefix = TABLES / "ROUTE-VALID-003-20260729-002"
    registries = {route: read_csv(Path(str(table_prefix) + suffix)) for route, suffix in {"FastA": "_route_A_mask_registry.csv", "B": "_route_B_mask_registry.csv", "C": "_route_C_reused_mask_registry.csv"}.items()}
    target: dict[tuple[int, str], dict[str, dict[str, str]]] = {}
    for route, rows in registries.items():
        for row in rows:
            key = (int(row["resolution_px"]), row["phase_id"])
            if int(row["slice_index"]) == Z_INDEX and key[0] in RESOLUTIONS and key[1] in PHASES:
                target.setdefault(key, {})[route] = row
    if set(target) != {(r, p) for r in RESOLUTIONS for p in PHASES} or any(set(rows) != {"FastA", "B", "C"} for rows in target.values()): raise RuntimeError("six-case reuse registry incomplete")
    predecessor_manifest_hash = sha256(RV003_RUN / "OUTPUT_MANIFEST.csv")
    prereg = {
        "work_id": WORK_ID, "run_id": RUN_ID, "status": "partial", "stop_reason": "missing_preregistered_deflection_values",
        "predecessor": {"run_id": "ROUTE-VALID-003-20260729-002", "qa_status": qa["status"], "qa_checks": qa["checks"], "run_output_manifest_sha256": predecessor_manifest_hash},
        "scope": {"model_id": "F1", "slice_index": Z_INDEX, "z_mm": Z_MM, "resolutions_px": list(RESOLUTIONS), "phases": PHASES, "case_count": 6},
        "deflection_search": {"baseline_deflection_mm": BASELINE_TESSELLATION_DEFLECTION_MM, "baseline_evidence": f"{relative(RV003_SCRIPT)}: GeometryRouteConfig(... tessellation_deflection_mm=0.1)", "sweep_values_mm": [], "search_roots": [relative(RV003_RESULT), relative(LAB / "scripts"), "outputs/URP4-1_CHANGELOG.md", "outputs/URP4-1_ROADMAP.md", "outputs/URP4-1_ROADMAP_LOG.md", "decision_log.md"], "result": "no reproducible preregistered sweep-value list found; no new B deflection is executed"},
        "route_C_rule": "reuse only: frozen IMSTL-007-20260728-002 masks; never regenerate", "forbidden": ["new deflection values", "Route C regeneration", "full Z801", "descriptors", "Excel/LEGACY-PY", "y", "NB mutation"]}
    RUN.mkdir(parents=True); RESULT.mkdir(parents=True)
    write_json(RUN / "PREREGISTRATION_AUDIT.json", prereg); (RESULT / "PREREGISTRATION_AUDIT.md").write_text("# Preregistration audit\n\nStatus: **partial** — `missing_preregistered_deflection_values`. Exact A and baseline comparisons are permitted; no deflection sweep is executed.\n", encoding="utf-8")
    common_shape, tools, source = make_common_step(rv3, contract)
    common_transform_hash = stable_hash(contract["common_transform"])
    config_hash = stable_hash({"work_id": WORK_ID, "slice_index": Z_INDEX, "z_mm": Z_MM, "resolutions": RESOLUTIONS, "phases": PHASES, "classifier_tolerance_mm": CLASSIFIER_TOL_MM, "inside_rule": "TopAbs_IN_true_TopAbs_ON_excluded", "common_transform_hash": common_transform_hash})
    exact_contract = {"route": "Exact A", "algorithm": "slow direct pixel-by-pixel BRepClass3d_SolidClassifier", "source_step": relative(source["step_path"]), "source_step_sha256": source["step_sha256"], "common_transform_hash": common_transform_hash, "pixel_center_convention": "x=(col+0.5)*pixel; y=40-(row+0.5)*pixel", "inside_outside_boundary": "TopAbs_IN is solid; TopAbs_ON counted and excluded; all other states are outside/other diagnostics", "classifier_tolerance_mm": CLASSIFIER_TOL_MM, "config_hash": config_hash}
    write_json(RUN / "EXACT_CLASSIFIER_CONTRACT.json", exact_contract); write_json(RESULT / "EXACT_CLASSIFIER_CONTRACT.json", exact_contract)
    deflection_contract = {"status": "not_executed_missing_preregistered_deflection_values", "baseline_route_B_deflection_mm": BASELINE_TESSELLATION_DEFLECTION_MM, "sweep_values_mm": [], "reason": prereg["stop_reason"], "new_tessellation_masks_created": 0}
    write_json(RUN / "DEFLECTION_SWEEP_CONTRACT.json", deflection_contract); write_json(RESULT / "DEFLECTION_SWEEP_CONTRACT.json", deflection_contract)
    inputs: list[dict[str, object]] = []; exact_registry: list[dict[str, object]] = []; reused_registry: list[dict[str, object]] = []; comparisons: list[dict[str, object]] = []; attribution: list[dict[str, object]] = []
    z_grid = np.linspace(0.0, SIZE_MM, 801); z_grid[0] = np.nextafter(0.0, SIZE_MM); z_grid[-1] = np.nextafter(SIZE_MM, 0.0)
    if abs(float(z_grid[Z_INDEX]) - Z_MM) > 1e-12: raise RuntimeError("z grid mismatch")
    for resolution in RESOLUTIONS:
        pixel = SIZE_MM / resolution
        for phase_id, (px, py) in PHASES.items():
            key = (resolution, phase_id); phase_x, phase_y = px * pixel, py * pixel
            case = {"run_id": RUN_ID, "model_id": "F1", "slice_index": Z_INDEX, "z_mm": Z_MM, "resolution_px": resolution, "phase_id": phase_id, "phase_x_pixel": px, "phase_y_pixel": py, "pixel_size_mm": pixel, "config_hash": config_hash, "common_transform_hash": common_transform_hash, "source_step_sha256": source["step_sha256"]}
            masks: dict[str, np.ndarray] = {}
            for route in ("FastA", "B", "C"):
                row = target[key][route]; path = ROOT / str(row["png_path"] if route != "C" else row["reused_from_image_path"])
                mask = read_mask(path); masks[route] = mask
                expected_png = row["png_sha256"]; expected_packed = row["mask_packedbits_sha256"]
                actual_png, actual_packed = sha256(path), packed_mask_sha(mask)
                if actual_png != expected_png or actual_packed != expected_packed: raise RuntimeError(f"reused hash mismatch: {route} {key}")
                record = {**case, "route": route, "reused": True, "source_run_id": row["run_id"] if route != "C" else row["reused_from_run_id"], "mask_path": relative(path), "png_sha256": actual_png, "packed_mask_sha256": actual_packed, "solid_pixels": int(mask.sum()), "source_registry_path": relative(Path(str(table_prefix) + {"FastA":"_route_A_mask_registry.csv", "B":"_route_B_mask_registry.csv", "C":"_route_C_reused_mask_registry.csv"}[route]))}
                reused_registry.append(record)
                inputs.append({**record, "route_C_frozen_from_IMSTL007": route == "C", "source_step_path": relative(source["step_path"])})
            local = common_shape
            if phase_x or phase_y:
                shift = gp_Trsf(); shift.SetTranslation(gp_Vec(float(phase_x), float(phase_y), 0.0)); local = tools.BRepBuilderAPI_Transform(common_shape, shift, True).Shape()
            exact, meta = exact_classifier_mask(source["step_path"], contract["common_transform"], resolution, Z_MM, phase_x, phase_y); masks["ExactA"] = exact
            exact_path = RUN / "masks" / "Exact_A" / f"P{resolution}" / phase_id / "F1_z0400.png"; png_hash, packed_hash = write_mask(exact_path, exact)
            exact_registry.append({**case, "route": "ExactA", "reused": False, "mask_path": relative(exact_path), "png_sha256": png_hash, "packed_mask_sha256": packed_hash, "solid_pixels": int(exact.sum()), **meta})
            for name, left, right in (("ExactA-FastA", "ExactA", "FastA"), ("ExactA-B", "ExactA", "B"), ("ExactA-C", "ExactA", "C"), ("FastA-B", "FastA", "B"), ("FastA-C", "FastA", "C"), ("B-C", "B", "C")):
                comparisons.append(compare(case, name, left, right, masks[left], masks[right]))
            panel(RESULT / "figures" / f"F1_z0400_P{resolution}_{phase_id}_panel.png", masks, f"F1 z400 P{resolution} {phase_id}")
            ef = comparisons[-6]; eb = comparisons[-5]; ec = comparisons[-4]
            attribution.append({**case, "case_id": f"F1-z0400-P{resolution}-{phase_id}", "exact_fast_iou": ef["mask_iou"], "exact_baseline_B_iou": eb["mask_iou"], "exact_C_iou": ec["mask_iou"], "deflection_sweep_status": "not_executed_missing_preregistered_deflection_values", "case_status": "unresolved", "attribution": "cannot separate curve-adapter versus controlled-tessellation versus Route C without preregistered B deflection sweep", "imported_STL_claim": "rejected_for_this_partial_run"})
    write_csv(TABLES / f"{RUN_ID}_input_hash_registry.csv", inputs); write_csv(TABLES / f"{RUN_ID}_exact_A_mask_registry.csv", exact_registry); write_csv(TABLES / f"{RUN_ID}_reused_FastA_B_C_mask_registry.csv", reused_registry); write_csv(TABLES / f"{RUN_ID}_all_pair_comparison.csv", comparisons); write_csv(TABLES / f"{RUN_ID}_deflection_sensitivity.csv", [{"status": deflection_contract["status"], "baseline_deflection_mm": BASELINE_TESSELLATION_DEFLECTION_MM, "sweep_value_mm": "", "executed": False, "reason": prereg["stop_reason"]}]); write_csv(TABLES / f"{RUN_ID}_case_attribution.csv", attribution); write_csv(TABLES / f"{RUN_ID}_protected_asset_audit.csv", protected_audit())
    placeholder = np.zeros((180, 960, 3), dtype=np.uint8); cv2.putText(placeholder, "No deflection sweep executed: missing preregistered values", (18, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 255), 2, cv2.LINE_AA); cv2.putText(placeholder, "Baseline B=0.1 mm is reused only; no new tessellation mask.", (18, 125), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA); cv2.imwrite(str(RESULT / "figures" / "deflection_sweep_not_executed.png"), placeholder)
    producer = {"work_id": WORK_ID, "run_id": RUN_ID, "status": "partial_pending_independent_QA", "stop_reason": prereg["stop_reason"], "exact_A_new_masks": len(exact_registry), "reused_fast_A_B_C_masks": len(reused_registry), "comparison_rows": len(comparisons), "new_route_B_deflection_masks": 0, "route_C_regenerated": False, "protected_files_unchanged": all(bool(row["passed"]) for row in protected_audit())}
    write_json(RESULT / "PRODUCER_PACKET.json", producer)
    write_csv(RUN / "OUTPUT_MANIFEST.csv", [{"relative_path": p.relative_to(RUN).as_posix(), "size_bytes": p.stat().st_size, "sha256": sha256(p)} for p in sorted(RUN.rglob("*")) if p.is_file() and p.name != "OUTPUT_MANIFEST.csv"])
    write_csv(RESULT / "OUTPUT_MANIFEST.csv", [{"relative_path": p.relative_to(RESULT).as_posix(), "size_bytes": p.stat().st_size, "sha256": sha256(p)} for p in sorted(RESULT.rglob("*")) if p.is_file() and p.name != "OUTPUT_MANIFEST.csv"])
    print(json.dumps(producer, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
