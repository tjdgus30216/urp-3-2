"""Small B/C/L/F/T imported-STL generalization and descriptor factory."""

from __future__ import annotations

import contextlib
import argparse
import csv
import hashlib
import io
import json
import math
import os
import shutil
import sys
import time
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

import cv2
import nbformat
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from urp4.geometry_io.v0_4 import (
    ImportedSTLWindingConfig,
    active_triangle_subsets_z,
    load_imported_stl_triangles,
    mask_packedbits_sha256,
    oriented_section_z,
    winding_raster,
)


LAB = ROOT / "experiments/lab_001_xy_connection_20260626"
RUN_ID = "IMSTL-006-20260728-002"
TASK_ID = "IMSTL-006_SMALL_IMPORTED_STL_GENERALIZATION_AND_DESCRIPTOR_CONCLUSION"
SETTINGS = "IDX-URP4-1-GEOM-IMPORTED-STL / CFG-IMSTL006-SELECTED-GATE-THEN-P1000-Z801 r1"
RUN = LAB / "runs/I006" / RUN_ID
RESULT = LAB / "results/IMSTL-006_SMALL_GENERALIZATION" / RUN_ID
TABLES = LAB / "reports/tables"
RUNTIME = Path("C:/URP4_I006_002")
CONTRACT_SOURCE = LAB / "factories/IMSTL-006/contracts/IMSTL-006_SMALL_GENERALIZATION_v0_3_SELECTED_GATE_20260728.json"
NOTEBOOK = LAB / "notebooks/NB_DEV_v0_5_IMPORTED_STL_WINDING_ROUTER.ipynb"
NB_CURRENT = LAB / "notebooks/R06V2_integrated_legacy_candidate_v0_2.ipynb"
SOURCE_DIR = LAB / "data/processed/n40_all58_20260715/stl"
PANEL = {
    "B3": "B3__a272cdb922__N40.stl",
    "C1": "C1__7755dda7d0__N40.stl",
    "L1": "L1__412f5bec5e__N40.stl",
    "F1": "F1__0dff3c1b13__N40.stl",
    "T1": "T1__3e9ba887ed__N40.stl",
    "T8": "T8__9db42618a6__N40.stl",
    "T9": "T9__f466dfe3fd__N40.stl",
}
FAMILY = {model: model[0] for model in PANEL}
RESOLUTIONS = (1000, 500)
FULL_RESOLUTION = 1000
SELECTED = {0, 1, 100, 200, 400, 600, 700, 799, 800}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise RuntimeError(f"empty table: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for row in rows for key in row})
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    os.replace(tmp, path)


def load_formula_namespace() -> dict[str, object]:
    notebook = nbformat.read(NOTEBOOK, as_version=4)
    nbformat.validate(notebook)
    namespace: dict[str, object] = {"__name__": "__main__"}
    capture = io.StringIO()
    previous = Path.cwd()
    previous_root = os.environ.get("URP4_PROJECT_ROOT")
    try:
        os.environ["URP4_PROJECT_ROOT"] = str(ROOT)
        os.chdir(RUNTIME)
        with contextlib.redirect_stdout(capture), contextlib.redirect_stderr(capture):
            for index in range(1, 18):
                source = str(notebook.cells[index].source)
                exec(compile(source, f"{NOTEBOOK.name}:cell-{index}", "exec"), namespace)
    finally:
        os.chdir(previous)
        if previous_root is None:
            os.environ.pop("URP4_PROJECT_ROOT", None)
        else:
            os.environ["URP4_PROJECT_ROOT"] = previous_root
    (RUN / "notebook_definition_load.log").write_text(capture.getvalue(), encoding="utf-8")
    return namespace


def selected_slice_gate(
    model_id: str,
    contract: dict[str, object],
) -> dict[str, object]:
    source = SOURCE_DIR / PANEL[model_id]
    expected = next(
        row["sha256"] for row in contract["panel_frozen_before_results"]
        if row["model_id"] == model_id
    )
    config = ImportedSTLWindingConfig(pixel_resolution=1000, slice_count=801)
    triangles, lower, upper, source_hash, normalization = load_imported_stl_triangles(
        source, config, expected_sha256=expected
    )
    z_values = np.linspace(lower[2], upper[2], 801)
    z_values[0] = np.nextafter(lower[2], upper[2])
    z_values[-1] = np.nextafter(upper[2], lower[2])
    rows: list[dict[str, object]] = []
    for index, (z_mm, active_triangles) in enumerate(active_triangle_subsets_z(triangles, z_values)):
        if index not in SELECTED:
            continue
        segments, section = oriented_section_z(active_triangles, z_mm)
        masks: dict[int, np.ndarray] = {}
        raster_diag: dict[int, dict[str, int]] = {}
        for pixels in RESOLUTIONS:
            mask, raster = winding_raster(
                segments, lower_xy=lower[:2], upper_xy=upper[:2], pixels=pixels
            )
            masks[pixels] = mask
            raster_diag[pixels] = raster
            target = RUN / "selected_gate_masks" / model_id / f"P{pixels}" / f"{model_id}_z{index:04d}.png"
            target.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(target), mask.astype(np.uint8) * 255)
        upsampled = cv2.resize(
            masks[500].astype(np.uint8), (1000, 1000), interpolation=cv2.INTER_NEAREST
        ).astype(bool)
        high = masks[1000]
        intersection = int(np.count_nonzero(high & upsampled))
        union = int(np.count_nonzero(high | upsampled))
        high_area, low_area = int(high.sum()), int(upsampled.sum())
        iou = 1.0 if union == 0 else intersection / union
        area_difference = (
            0.0 if max(high_area, low_area) == 0
            else abs(high_area - low_area) / max(high_area, low_area)
        )
        interior = index not in {0, 800}
        occupancy_pass = (
            True if not interior else 1.0e-6 < float(high.mean()) < 0.999999
        )
        resolution_pass = True if not interior else iou >= 0.95 and area_difference <= 0.05
        rows.append(
            {
                "run_id": RUN_ID,
                "model_id": model_id,
                "family": FAMILY[model_id],
                "slice_index": index,
                "z_mm": z_mm,
                "interior_gate_slice": interior,
                "source_geometry_sha256": source_hash,
                "source_triangle_count": int(len(triangles)),
                "z_active_triangle_count": int(len(active_triangles)),
                "segment_count": int(section["segment_count"]),
                "p1000_solid_pixels": high_area,
                "p1000_area_fraction": float(high.mean()),
                "p500_solid_pixels": int(masks[500].sum()),
                "p500_area_fraction": float(masks[500].mean()),
                "p500_upsampled_vs_p1000_iou": iou,
                "p500_upsampled_vs_p1000_area_difference": area_difference,
                "occupancy_gate_pass": occupancy_pass,
                "resolution_gate_pass": resolution_pass,
                "slice_gate_pass": occupancy_pass and resolution_pass,
                "p1000_mask_sha256": mask_packedbits_sha256(high),
                "p500_mask_sha256": mask_packedbits_sha256(masks[500]),
                "p1000_max_abs_winding": raster_diag[1000]["max_abs_winding"],
                "p500_max_abs_winding": raster_diag[500]["max_abs_winding"],
                **normalization,
            }
        )
    if len(rows) != len(SELECTED):
        raise RuntimeError(f"selected gate row count mismatch {model_id}: {len(rows)}")
    gate_pass = all(bool(row["slice_gate_pass"]) for row in rows)
    return {
        "model_id": model_id,
        "family": FAMILY[model_id],
        "selected_slice_count": len(rows),
        "interior_slice_count": sum(int(row["interior_gate_slice"]) for row in rows),
        "min_interior_resolution_iou": min(
            float(row["p500_upsampled_vs_p1000_iou"])
            for row in rows if row["interior_gate_slice"]
        ),
        "max_interior_area_difference": max(
            float(row["p500_upsampled_vs_p1000_area_difference"])
            for row in rows if row["interior_gate_slice"]
        ),
        "failed_slice_indices": [
            int(row["slice_index"]) for row in rows if not row["slice_gate_pass"]
        ],
        "selected_gate_pass": gate_pass,
        "rows": rows,
    }


class Aggregator:
    def __init__(self, namespace: dict[str, object], pixels: int) -> None:
        self.ns = namespace
        self.pixels = pixels
        self.previous: np.ndarray | None = None
        self.valid_pairs = 0
        self.all_ip: dict[str, list[float]] = defaultdict(list)
        self.all_w: dict[str, list[float]] = defaultdict(list)
        self.lip: dict[str, list[float]] = defaultdict(list)
        self.ltp: dict[str, list[float]] = defaultdict(list)

    def add(self, mask: np.ndarray) -> None:
        if self.previous is not None:
            comp, weights, ltp, _ = self.ns["_slice_pair_descriptors"](
                self.previous,
                mask,
                area_per_pixel=1600.0 / (self.pixels * self.pixels),
                length_per_pixel=40.0 / self.pixels,
                layer_height=0.05,
                min_pixels=2,
            )
            if any(len(values) for values in weights.values()) or any(np.isfinite(list(ltp.values()))):
                self.valid_pairs += 1
                for key, values in comp.items():
                    array = np.asarray(values, dtype=float)
                    if len(array):
                        self.all_ip[key].extend(array.tolist())
                        self.all_w[key].extend(np.asarray(weights.get(key, []), dtype=float)[: len(array)].tolist())
                        self.lip[key].append(float(np.nanmean(array)))
                    if np.isfinite(ltp.get(key, np.nan)):
                        self.ltp[key].append(float(ltp[key]))
        self.previous = mask

    def result(self) -> dict[str, object]:
        output: dict[str, object] = {"slice_z_valid_pair_count": int(self.valid_pairs)}
        stats = self.ns["_stats"]
        for key in ("mass_orientation", "curvature", "thickness", "angle", "perimeter_to_area"):
            output.update(stats(self.all_ip[key], f"slice_z_{key}_IP", weights=self.all_w[key] or None))
            output.update(stats(self.lip[key], f"slice_z_{key}_LIP"))
            output.update(stats(self.ltp[key], f"slice_z_{key}_LTP"))
        return output


def process_model(model_id: str, namespace: dict[str, object], contract: dict[str, object]) -> dict[str, object]:
    done = RUN / "done" / f"{model_id}.json"
    if done.exists():
        return json.loads(done.read_text(encoding="utf-8"))
    source = SOURCE_DIR / PANEL[model_id]
    expected = next(row["sha256"] for row in contract["panel_frozen_before_results"] if row["model_id"] == model_id)
    config = ImportedSTLWindingConfig(pixel_resolution=1000, slice_count=801)
    triangles, lower, upper, source_hash, normalization = load_imported_stl_triangles(
        source, config, expected_sha256=expected
    )
    z_values = np.linspace(lower[2], upper[2], 801)
    z_values[0] = np.nextafter(lower[2], upper[2])
    z_values[-1] = np.nextafter(upper[2], lower[2])
    aggregators = {FULL_RESOLUTION: Aggregator(namespace, FULL_RESOLUTION)}
    traces: dict[int, list[dict[str, object]]] = {FULL_RESOLUTION: []}
    image_root = RUN / "selected_masks" / model_id
    started = time.perf_counter()
    for index, (z_mm, active_triangles) in enumerate(active_triangle_subsets_z(triangles, z_values)):
        segments, section = oriented_section_z(active_triangles, z_mm)
        for pixels in (FULL_RESOLUTION,):
            mask, raster = winding_raster(
                segments, lower_xy=lower[:2], upper_xy=upper[:2], pixels=pixels
            )
            component_count = int(cv2.connectedComponents(mask.astype(np.uint8), connectivity=8)[0] - 1)
            traces[pixels].append(
                {
                    "run_id": RUN_ID,
                    "model_id": model_id,
                    "family": FAMILY[model_id],
                    "pixel_resolution": pixels,
                    "slice_index": index,
                    "z_mm": z_mm,
                    "source_geometry_path": str(source),
                    "source_geometry_sha256": source_hash,
                    "route_id": config.route_id,
                    "source_triangle_count": int(len(triangles)),
                    "z_active_triangle_count": int(len(active_triangles)),
                    "solid_pixel_count": int(mask.sum()),
                    "area_fraction": float(mask.mean()),
                    "component_count": component_count,
                    "mask_packedbits_sha256": mask_packedbits_sha256(mask),
                    "mask_retained": index in SELECTED,
                    **section,
                    **raster,
                }
            )
            aggregators[pixels].add(mask)
            if index in SELECTED:
                target = image_root / f"P{pixels}" / f"{model_id}_z{index:04d}.png"
                target.parent.mkdir(parents=True, exist_ok=True)
                cv2.imwrite(str(target), mask.astype(np.uint8) * 255)
        if index % 100 == 0 or index == 800:
            print(f"I006 {model_id} {index + 1}/801 elapsed={time.perf_counter() - started:.1f}s", flush=True)
    result_rows = []
    for pixels in (FULL_RESOLUTION,):
        trace_path = RUN / "traces" / f"{model_id}_P{pixels}_trace.csv"
        write_csv(trace_path, traces[pixels])
        descriptor = aggregators[pixels].result()
        result_rows.append(
            {
                "run_id": RUN_ID,
                "model_id": model_id,
                "family": FAMILY[model_id],
                "pixel_resolution": pixels,
                "slice_count": 801,
                "source_geometry_path": str(source),
                "source_geometry_sha256": source_hash,
                "route_id": config.route_id,
                "runtime_seconds_model_both_resolutions": time.perf_counter() - started,
                **normalization,
                **descriptor,
            }
        )
    payload = {
        "model_id": model_id,
        "status": "completed",
        "completed_at_utc": datetime.now(UTC).isoformat(),
        "source_hash": source_hash,
        "result_rows": result_rows,
    }
    write_json(done, payload)
    return payload


def finite(value: object) -> bool:
    try:
        return bool(np.isfinite(float(value)))
    except (TypeError, ValueError):
        return False


def analyze(
    payloads: list[dict[str, object]],
    selected_gates: list[dict[str, object]],
) -> dict[str, object]:
    rows = [row for payload in payloads for row in payload["result_rows"]]
    descriptor_table = TABLES / f"{RUN_ID}_descriptor_matrix.csv"
    write_csv(descriptor_table, rows)
    descriptor_df = pd.DataFrame(rows)
    average_fields = sorted(
        column for column in descriptor_df.columns
        if column.startswith("slice_z_") and column.endswith("_avg")
    )
    stdev_fields = sorted(
        column for column in descriptor_df.columns
        if column.startswith("slice_z_") and column.endswith("_stdev")
    )
    coverage_rows = []
    for _, row in descriptor_df.iterrows():
        coverage_rows.append(
            {
                "model_id": row.model_id,
                "family": row.family,
                "pixel_resolution": int(row.pixel_resolution),
                "average_field_count": len(average_fields),
                "finite_average_count": sum(finite(row[field]) for field in average_fields),
                "finite_average_fraction": sum(finite(row[field]) for field in average_fields) / len(average_fields),
                "stdev_field_count": len(stdev_fields),
                "finite_stdev_count": sum(finite(row[field]) for field in stdev_fields),
                "valid_pair_count": int(row.slice_z_valid_pair_count),
                "finite_gate_pass": sum(finite(row[field]) for field in average_fields) / len(average_fields) >= 0.90,
                "pair_gate_pass": int(row.slice_z_valid_pair_count) >= 760,
            }
        )
    write_csv(TABLES / f"{RUN_ID}_descriptor_coverage.csv", coverage_rows)

    trace_summary = []
    all_trace_rows: list[dict[str, object]] = []
    completed_models = [str(payload["model_id"]) for payload in payloads]
    for model_id in completed_models:
        for pixels in (FULL_RESOLUTION,):
            trace = pd.read_csv(RUN / "traces" / f"{model_id}_P{pixels}_trace.csv")
            interior = trace[(trace.slice_index > 0) & (trace.slice_index < 800)]
            abrupt = np.abs(np.diff(trace.area_fraction.to_numpy(float)))
            trace_summary.append(
                {
                    "model_id": model_id,
                    "family": FAMILY[model_id],
                    "pixel_resolution": pixels,
                    "trace_rows": len(trace),
                    "interior_zero_fraction": float((interior.solid_pixel_count == 0).mean()),
                    "area_fraction_min": float(trace.area_fraction.min()),
                    "area_fraction_median": float(trace.area_fraction.median()),
                    "area_fraction_max": float(trace.area_fraction.max()),
                    "max_adjacent_area_fraction_change": float(abrupt.max()),
                    "component_count_max": int(trace.component_count.max()),
                    "max_abs_winding": int(trace.max_abs_winding.max()),
                    "active_triangle_median": float(trace.z_active_triangle_count.median()),
                    "selected_mask_count": int(trace.mask_retained.astype(bool).sum()),
                    "catastrophic_numeric_flag": bool(
                        (interior.solid_pixel_count == 0).mean() > 0.05
                        or trace.area_fraction.max() >= 0.999999
                    ),
                }
            )
            all_trace_rows.extend(trace.to_dict("records"))
    write_csv(TABLES / f"{RUN_ID}_slice_trace_summary.csv", trace_summary)

    hi = descriptor_df.set_index("model_id")
    X = hi[average_fields].astype(float)
    med = X.median(axis=0)
    scale = X.std(axis=0, ddof=0).replace(0, 1.0)
    Z = (X - med) / scale
    collision_rows = []
    ids = list(Z.index)
    for i, left in enumerate(ids):
        for right in ids[i + 1 :]:
            values_left = X.loc[left].to_numpy(float)
            values_right = X.loc[right].to_numpy(float)
            exact = bool(np.allclose(values_left, values_right, rtol=0, atol=1.0e-12, equal_nan=True))
            distance = float(np.linalg.norm(Z.loc[left].to_numpy(float) - Z.loc[right].to_numpy(float)))
            collision_rows.append(
                {
                    "left_model": left,
                    "right_model": right,
                    "left_family": FAMILY[left],
                    "right_family": FAMILY[right],
                    "feature_count": len(average_fields),
                    "exact_duplicate": exact,
                    "standardized_euclidean_distance": distance,
                    "is_T8_T9": {left, right} == {"T8", "T9"},
                }
            )
    write_csv(TABLES / f"{RUN_ID}_xonly_collision_audit.csv", collision_rows)

    gate_passed = [str(row["model_id"]) for row in selected_gates if row["selected_gate_pass"]]
    gate_failed = [str(row["model_id"]) for row in selected_gates if not row["selected_gate_pass"]]
    if {"T8", "T9"}.issubset(set(completed_models)):
        t8_t9 = next(row for row in collision_rows if row["is_T8_T9"])
    else:
        t8_t9 = {
            "status": "not_compared_because_selected_gate_failed",
            "T8_pass": "T8" in gate_passed,
            "T9_pass": "T9" in gate_passed,
        }
    summary = {
        "task_id": TASK_ID,
        "run_id": RUN_ID,
        "completed_at_utc": datetime.now(UTC).isoformat(),
        "selected_gate_passed_models": gate_passed,
        "selected_gate_failed_models": gate_failed,
        "models_completed_full": len(payloads),
        "families_completed_full": sorted({FAMILY[model] for model in completed_models}),
        "all_primary_trace_complete": all(row["trace_rows"] == 801 for row in trace_summary if row["pixel_resolution"] == 1000),
        "all_finite_gates_pass": all(row["finite_gate_pass"] for row in coverage_rows),
        "all_pair_gates_pass": all(row["pair_gate_pass"] for row in coverage_rows),
        "catastrophic_numeric_flags": sum(int(row["catastrophic_numeric_flag"]) for row in trace_summary),
        "selected_gate_min_resolution_iou": min(float(row["min_interior_resolution_iou"]) for row in selected_gates),
        "selected_gate_max_area_difference": max(float(row["max_interior_area_difference"]) for row in selected_gates),
        "exact_duplicate_pair_count": sum(int(row["exact_duplicate"]) for row in collision_rows),
        "t8_t9": t8_t9,
        "operational_generalization": (
            "pass_all_panel" if not gate_failed and all(row["finite_gate_pass"] and row["pair_gate_pass"] for row in coverage_rows)
            else "partial_pass" if payloads and all(row["finite_gate_pass"] and row["pair_gate_pass"] for row in coverage_rows)
            else "fail"
        ),
        "physical_parity": "unresolved_without_paired_STP",
        "feature_promotion": "none",
        "y_access": False,
        "all58_executed": False,
    }
    write_json(RESULT / "DECISION_PACKET.json", summary)
    return summary


def run_selected_phase(contract: dict[str, object]) -> list[dict[str, object]]:
    packet_path = RESULT / "SELECTED_GATE_PACKET.json"
    if packet_path.exists():
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
        if packet.get("contract_sha256") != sha256(CONTRACT_SOURCE):
            raise RuntimeError("selected gate packet contract mismatch")
        return list(packet["gate_summaries"])

    selected_gates = [selected_slice_gate(model_id, contract) for model_id in PANEL]
    selected_rows = [row for gate in selected_gates for row in gate.pop("rows")]
    write_csv(TABLES / f"{RUN_ID}_selected_slice_gate_detail.csv", selected_rows)
    write_csv(TABLES / f"{RUN_ID}_selected_slice_gate_summary.csv", selected_gates)
    packet = {
        "task_id": TASK_ID,
        "run_id": RUN_ID,
        "settings": SETTINGS,
        "completed_at_utc": datetime.now(UTC).isoformat(),
        "contract_path": str(CONTRACT_SOURCE),
        "contract_sha256": sha256(CONTRACT_SOURCE),
        "gate_summaries": selected_gates,
        "passed_models": [
            str(gate["model_id"]) for gate in selected_gates if gate["selected_gate_pass"]
        ],
        "failed_models": [
            str(gate["model_id"]) for gate in selected_gates if not gate["selected_gate_pass"]
        ],
        "full_extraction_started": False,
    }
    write_json(packet_path, packet)
    return selected_gates


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("selected", "full", "auto"), default="auto")
    args = parser.parse_args()
    contract = json.loads(CONTRACT_SOURCE.read_text(encoding="utf-8"))
    if RUN.exists():
        existing = json.loads((RUN / "CONTRACT.json").read_text(encoding="utf-8"))
        if existing != contract:
            raise RuntimeError("resume contract mismatch")
    else:
        RUN.mkdir(parents=True)
        RESULT.mkdir(parents=True)
        RUNTIME.mkdir(parents=True)
        write_json(RUN / "CONTRACT.json", contract)
    if not RUNTIME.exists():
        RUNTIME.mkdir(parents=True)
    protected_before = {"nb_current": sha256(NB_CURRENT), "notebook": sha256(NOTEBOOK)}
    selected_gates = run_selected_phase(contract)
    if args.phase == "selected":
        print((RESULT / "SELECTED_GATE_PACKET.json").read_text(encoding="utf-8"))
        return

    passed_models = [str(gate["model_id"]) for gate in selected_gates if gate["selected_gate_pass"]]
    if not passed_models:
        raise RuntimeError("no selected-slice gate pass; full extraction is forbidden")
    packet_path = RESULT / "SELECTED_GATE_PACKET.json"
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    packet["full_extraction_started"] = True
    packet["full_extraction_started_at_utc"] = datetime.now(UTC).isoformat()
    write_json(packet_path, packet)
    namespace = load_formula_namespace()
    payloads = [process_model(model_id, namespace, contract) for model_id in passed_models]
    decision = analyze(payloads, selected_gates)
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    packet["full_extraction_completed"] = True
    packet["full_extraction_completed_at_utc"] = datetime.now(UTC).isoformat()
    packet["full_completed_models"] = [str(payload["model_id"]) for payload in payloads]
    write_json(packet_path, packet)
    protected_after = {"nb_current": sha256(NB_CURRENT), "notebook": sha256(NOTEBOOK)}
    decision["protected_before"] = protected_before
    decision["protected_after"] = protected_after
    decision["protected_unchanged"] = protected_before == protected_after
    write_json(RESULT / "DECISION_PACKET.json", decision)
    write_json(RESULT / "PRODUCER_QA.json", {"status": "passed" if decision["operational_generalization"] in {"pass_all_panel", "partial_pass"} and decision["protected_unchanged"] else "failed", "decision": decision})
    print(json.dumps(decision, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
