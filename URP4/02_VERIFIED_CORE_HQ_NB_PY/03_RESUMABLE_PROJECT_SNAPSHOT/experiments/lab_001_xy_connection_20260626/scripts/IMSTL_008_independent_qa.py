"""Independent table replay and sampled-family non-regression for IMSTL-008."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from pathlib import Path

import cv2
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments/lab_001_xy_connection_20260626"
DELIVERABLE = ROOT / "URP4-1_DELIVERABLE"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from urp4.geometry_io.v0_4 import (  # noqa: E402
    ImportedSTLWindingConfig,
    active_triangle_subsets_z,
    load_imported_stl_triangles,
    mask_packedbits_sha256,
    oriented_section_z,
    winding_raster,
)


RUN_ID = "IMSTL-008-20260728-002"
CONTRACT_PATH = LAB / "factories/IMSTL-008/contracts/IMSTL-008_F1_FULL_P1000_Z801_NONREGRESSION_v0_2_20260728.json"
RUN = LAB / "runs/I008" / RUN_ID
RESULT = LAB / "results/I008_F1" / RUN_ID
TABLES = LAB / "reports/tables"
I006_RUN = LAB / "runs/I006/IMSTL-006-20260728-002"
I006_RESULT = LAB / "results/IMSTL-006_SMALL_GENERALIZATION/IMSTL-006-20260728-002"
I007_RUN = LAB / "runs/I007/IMSTL-007-20260728-002"
I007_RESULT = LAB / "results/I007_F1/IMSTL-007-20260728-002"
SOURCE_DIR = LAB / "data/processed/n40_all58_20260715/stl"
PANEL = {
    "B3": "B3__a272cdb922__N40.stl", "C1": "C1__7755dda7d0__N40.stl",
    "L1": "L1__412f5bec5e__N40.stl", "T1": "T1__3e9ba887ed__N40.stl",
    "T8": "T8__9db42618a6__N40.stl", "T9": "T9__f466dfe3fd__N40.stl",
}
SELECTED = {0, 1, 100, 200, 400, 600, 700, 799, 800}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tree_identity(path: Path) -> str:
    digest = hashlib.sha256()
    for item in [x for x in sorted(path.rglob("*")) if x.is_file() and "__pycache__" not in x.parts]:
        relative = item.relative_to(path).as_posix()
        size = item.stat().st_size
        digest.update(relative.encode("utf-8") + b"\0" + sha256(item).encode("ascii") + b"\0" + str(size).encode("ascii") + b"\n")
    return digest.hexdigest()


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def recompute_scalars(slice_pixels: pd.DataFrame, overlay_pixels: pd.DataFrame, components: pd.DataFrame) -> list[dict[str, object]]:
    occupancy = slice_pixels.material_pixel_count.to_numpy(float) / 1_000_000.0
    counts = slice_pixels.component_count.to_numpy(float)
    union = overlay_pixels.union_pixel_count.to_numpy(float)
    valid = union > 0
    change = (overlay_pixels.red_pixel_count.to_numpy(float) + overlay_pixels.blue_pixel_count.to_numpy(float))[valid] / union[valid]
    overlap = overlay_pixels.purple_pixel_count.to_numpy(float)[valid] / union[valid]
    thickness = components.thickness_sqrt_red_purple.to_numpy(float)
    thickness = thickness[np.isfinite(thickness)]
    massori = components.mass_orientation.to_numpy(float)
    massori = massori[np.isfinite(massori)]
    return [
        {"formula_id": "XRV1-F001", "statistic": "mean", "value": float(np.mean(occupancy)), "population_n": len(occupancy)},
        {"formula_id": "XRV1-F002", "statistic": "std_pop_ddof0", "value": float(np.std(occupancy, ddof=0)), "population_n": len(occupancy)},
        {"formula_id": "XRV1-F003", "statistic": "mean", "value": float(np.mean(counts)), "population_n": len(counts)},
        {"formula_id": "XRV1-F004", "statistic": "std_pop_ddof0", "value": float(np.std(counts, ddof=0)), "population_n": len(counts)},
        {"formula_id": "XRV1-F005", "statistic": "mean", "value": float(np.mean(change)), "population_n": len(change)},
        {"formula_id": "XRV1-F006", "statistic": "mean", "value": float(np.mean(overlap)), "population_n": len(overlap)},
        {"formula_id": "XRV1-F007", "statistic": "mean", "value": float(np.mean(thickness)), "population_n": len(thickness)},
        {"formula_id": "XRV1-F007", "statistic": "std_pop_ddof0", "value": float(np.std(thickness, ddof=0)), "population_n": len(thickness)},
        {"formula_id": "XRV1-F008", "statistic": "mean", "value": float(np.mean(massori)), "population_n": len(massori)},
    ]


def selected_replay(model_id: str, source: Path, expected_hash: str, expected_trace: pd.DataFrame | None, reference_root: Path | None) -> list[dict[str, object]]:
    config = ImportedSTLWindingConfig(pixel_resolution=1000, slice_count=801)
    triangles, lower, upper, source_hash, _ = load_imported_stl_triangles(source, config, expected_sha256=expected_hash)
    z_values = np.linspace(lower[2], upper[2], 801)
    z_values[0] = np.nextafter(lower[2], upper[2])
    z_values[-1] = np.nextafter(upper[2], lower[2])
    rows: list[dict[str, object]] = []
    for index, (z_mm, active) in enumerate(active_triangle_subsets_z(triangles, z_values)):
        if index not in SELECTED:
            continue
        segments, _ = oriented_section_z(active, z_mm)
        mask, _ = winding_raster(segments, lower_xy=lower[:2], upper_xy=upper[:2], pixels=1000)
        packed_hash = mask_packedbits_sha256(mask)
        if expected_trace is not None:
            expected = str(expected_trace.loc[expected_trace.slice_index.eq(index), "mask_packedbits_sha256"].iloc[0])
            exact = packed_hash == expected
            evidence = "IMSTL-006 trace packedbits"
        else:
            reference = cv2.imread(str(reference_root / f"F1_z{index:04d}.png"), cv2.IMREAD_GRAYSCALE) > 0
            expected = mask_packedbits_sha256(reference)
            exact = bool(np.array_equal(mask, reference))
            evidence = "IMSTL-007 P1000/P00 retained mask"
        rows.append({"model_id": model_id, "slice_index": index, "source_sha256": source_hash, "replay_hash": packed_hash, "expected_hash": expected, "exact": exact, "evidence": evidence})
    return rows


def main() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    producer = json.loads((RESULT / "PRODUCER_SUMMARY.json").read_text(encoding="utf-8"))
    if producer.get("status") != "passed":
        raise RuntimeError("producer did not pass")
    hq = Path(producer["hq_run_dir"])
    if not hq.is_dir():
        raise RuntimeError(f"HQ run directory missing: {hq}")
    table_root = hq / "descriptor/tables"
    slice_pixels = pd.read_csv(table_root / "slice_pixel_count_table.csv")
    overlay_pixels = pd.read_csv(table_root / "overlay_pixel_table.csv")
    slice_components = pd.read_csv(table_root / "slice_component_table.csv")
    components = pd.read_csv(table_root / "overlay_component_table.csv")
    observed = pd.read_csv(hq / "descriptor_result.csv")
    recomputed = recompute_scalars(slice_pixels, overlay_pixels, components)
    scalar_rows: list[dict[str, object]] = []
    for row in recomputed:
        match = observed[(observed.formula_id == row["formula_id"]) & (observed.statistic == row["statistic"])]
        value = float(match.value.iloc[0])
        error = abs(value - float(row["value"]))
        scalar_rows.append({**row, "observed_value": value, "abs_error": error, "population_n_exact": int(match.population_n.iloc[0]) == int(row["population_n"]), "status": "passed" if error <= 1e-12 and int(match.population_n.iloc[0]) == int(row["population_n"]) else "failed"})

    f1_source = ROOT / contract["source"]["path"]
    replay_rows = selected_replay("F1", f1_source, contract["source"]["sha256"], None, I007_RUN / "masks/P1000/P00")
    i006_descriptor = pd.read_csv(TABLES / "IMSTL-006-20260728-002_descriptor_matrix.csv")
    family_rows: list[dict[str, object]] = []
    for model_id, filename in PANEL.items():
        trace = pd.read_csv(I006_RUN / "traces" / f"{model_id}_P1000_trace.csv")
        source = SOURCE_DIR / filename
        expected_hash = str(trace.source_geometry_sha256.iloc[0])
        replay_rows.extend(selected_replay(model_id, source, expected_hash, trace, None))
        descriptor_row = i006_descriptor[i006_descriptor.model_id.eq(model_id)]
        family_rows.append({
            "model_id": model_id,
            "family": model_id[0],
            "source_hash_exact": sha256(source) == expected_hash,
            "trace_rows": len(trace),
            "trace_indices_exact": len(trace) == 801 and trace.slice_index.min() == 0 and trace.slice_index.max() == 800 and trace.slice_index.nunique() == 801,
            "trace_finite": bool(np.isfinite(trace.area_fraction.to_numpy(float)).all()),
            "descriptor_row_count": len(descriptor_row),
            "descriptor_finite": bool(np.isfinite(descriptor_row.filter(regex=r"^slice_z_").to_numpy(float)).all()),
        })

    baseline = json.loads((RUN / "UPSTREAM_BASELINE.json").read_text(encoding="utf-8"))
    upstream_exact = {
        "i006_run_tree": tree_identity(I006_RUN) == baseline["i006_run_tree"],
        "i006_result_tree": tree_identity(I006_RESULT) == baseline["i006_result_tree"],
        "i007_run_tree": tree_identity(I007_RUN) == baseline["i007_run_tree"],
        "i007_result_tree": tree_identity(I007_RESULT) == baseline["i007_result_tree"],
    }
    protected_after = []
    baseline_assets = json.loads((LAB / "results/HQ-BLUEPRINT-001/PROTECTED_ASSET_BASELINE.json").read_text(encoding="utf-8"))["assets"]
    for item in baseline_assets:
        path = ROOT / item["path"]
        current = tree_identity(path) if item["asset_kind"] == "tree" else sha256(path)
        protected_after.append({"alias": item["alias"], "expected_sha256": item["before_sha256"], "current_sha256": current, "status": "passed" if current == item["before_sha256"] else "failed"})

    checks = {
        "producer_passed": producer["status"] == "passed",
        "slice_rows_801": len(slice_pixels) == 801 and slice_pixels.slice_index.min() == 0 and slice_pixels.slice_index.max() == 800 and slice_pixels.slice_index.nunique() == 801,
        "overlay_rows_800": len(overlay_pixels) == 800 and overlay_pixels.pair_index.min() == 0 and overlay_pixels.pair_index.max() == 799 and overlay_pixels.pair_index.nunique() == 800,
        "slice_components_nonempty": len(slice_components) > 0,
        "overlay_components_nonempty": len(components) > 0,
        "primitive_numeric_finite": bool(np.isfinite(slice_pixels[["material_pixel_count", "component_count"]].to_numpy(float)).all() and np.isfinite(overlay_pixels[["red_pixel_count", "blue_pixel_count", "purple_pixel_count", "union_pixel_count"]].to_numpy(float)).all()),
        "scalar_replay_9_of_9": len(scalar_rows) == 9 and all(row["status"] == "passed" for row in scalar_rows),
        "scalar_max_abs_error": max(row["abs_error"] for row in scalar_rows),
        "f1_selected_replay_9_of_9": sum(row["model_id"] == "F1" and row["exact"] for row in replay_rows) == 9,
        "prior_family_selected_replay_54_of_54": sum(row["model_id"] != "F1" and row["exact"] for row in replay_rows) == 54,
        "prior_family_trace_and_descriptor_pass": all(all(bool(row[key]) for key in ("source_hash_exact", "trace_indices_exact", "trace_finite", "descriptor_finite")) and row["descriptor_row_count"] == 1 for row in family_rows),
        "upstream_trees_exact": all(upstream_exact.values()),
        "protected_assets_31_of_31": len(protected_after) == 31 and all(row["status"] == "passed" for row in protected_after),
        "no_y_columns": not any(str(column).lower().startswith("y") or "performance" in str(column).lower() for frame in (slice_pixels, overlay_pixels, slice_components, components, observed) for column in frame.columns),
        "all58_not_executed": True,
    }
    boolean_checks = [value for value in checks.values() if isinstance(value, bool)]
    checks["status"] = "passed" if all(boolean_checks) and checks["scalar_max_abs_error"] <= 1e-12 else "failed"
    write_csv(TABLES / f"{RUN_ID}_independent_scalar_replay.csv", scalar_rows)
    write_csv(TABLES / f"{RUN_ID}_selected_mask_replay.csv", replay_rows)
    write_csv(TABLES / f"{RUN_ID}_family_nonregression.csv", family_rows)
    write_csv(RESULT / "PROTECTED_ASSET_POST_AUDIT.csv", protected_after)
    write_json(RESULT / "INDEPENDENT_QA.json", {"checks": checks, "upstream_exact": upstream_exact})
    print(json.dumps(checks, ensure_ascii=False, indent=2))
    if checks["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
