"""Independent replay and artifact audit for IMSTL-006 selected-gate/full run."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

import cv2
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
RUN = LAB / "runs/I006" / RUN_ID
RESULT = LAB / "results/IMSTL-006_SMALL_GENERALIZATION" / RUN_ID
TABLES = LAB / "reports/tables"
SOURCE_DIR = LAB / "data/processed/n40_all58_20260715/stl"
CONTRACT = LAB / "factories/IMSTL-006/contracts/IMSTL-006_SMALL_GENERALIZATION_v0_3_SELECTED_GATE_20260728.json"
NOTEBOOK = LAB / "notebooks/NB_DEV_v0_5_IMPORTED_STL_WINDING_ROUTER.ipynb"
NB_CURRENT = LAB / "notebooks/R06V2_integrated_legacy_candidate_v0_2.ipynb"
PANEL = {
    "B3": "B3__a272cdb922__N40.stl",
    "C1": "C1__7755dda7d0__N40.stl",
    "L1": "L1__412f5bec5e__N40.stl",
    "F1": "F1__0dff3c1b13__N40.stl",
    "T1": "T1__3e9ba887ed__N40.stl",
    "T8": "T8__9db42618a6__N40.stl",
    "T9": "T9__f466dfe3fd__N40.stl",
}
SELECTED = {0, 1, 100, 200, 400, 600, 700, 799, 800}


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    gate = pd.read_csv(TABLES / f"{RUN_ID}_selected_slice_gate_detail.csv")
    summaries = pd.read_csv(TABLES / f"{RUN_ID}_selected_slice_gate_summary.csv")
    descriptors = pd.read_csv(TABLES / f"{RUN_ID}_descriptor_matrix.csv")
    expected_hashes = {
        row["model_id"]: row["sha256"] for row in contract["panel_frozen_before_results"]
    }
    replay_rows: list[dict[str, object]] = []
    for model_id, filename in PANEL.items():
        source = SOURCE_DIR / filename
        config = ImportedSTLWindingConfig(pixel_resolution=1000, slice_count=801)
        triangles, lower, upper, source_hash, _ = load_imported_stl_triangles(
            source, config, expected_sha256=expected_hashes[model_id]
        )
        z_values = np.linspace(lower[2], upper[2], 801)
        z_values[0] = np.nextafter(lower[2], upper[2])
        z_values[-1] = np.nextafter(upper[2], lower[2])
        for index, (z_mm, active) in enumerate(active_triangle_subsets_z(triangles, z_values)):
            if index not in SELECTED:
                continue
            segments, _ = oriented_section_z(active, z_mm)
            masks = {
                pixels: winding_raster(
                    segments, lower_xy=lower[:2], upper_xy=upper[:2], pixels=pixels
                )[0]
                for pixels in (1000, 500)
            }
            reference = gate[(gate.model_id == model_id) & (gate.slice_index == index)].iloc[0]
            upsampled = cv2.resize(
                masks[500].astype(np.uint8), (1000, 1000), interpolation=cv2.INTER_NEAREST
            ).astype(bool)
            high = masks[1000]
            intersection = int(np.count_nonzero(high & upsampled))
            union = int(np.count_nonzero(high | upsampled))
            iou = 1.0 if union == 0 else intersection / union
            area_diff = 0.0 if max(high.sum(), upsampled.sum()) == 0 else (
                abs(int(high.sum()) - int(upsampled.sum())) / max(int(high.sum()), int(upsampled.sum()))
            )
            replay_rows.append(
                {
                    "model_id": model_id,
                    "slice_index": index,
                    "source_hash_match": source_hash == expected_hashes[model_id],
                    "p1000_hash_match": mask_packedbits_sha256(high) == reference.p1000_mask_sha256,
                    "p500_hash_match": mask_packedbits_sha256(masks[500]) == reference.p500_mask_sha256,
                    "iou_abs_error": abs(iou - float(reference.p500_upsampled_vs_p1000_iou)),
                    "area_difference_abs_error": abs(
                        area_diff - float(reference.p500_upsampled_vs_p1000_area_difference)
                    ),
                }
            )

    passed = summaries[summaries.selected_gate_pass.astype(str).str.lower() == "true"].model_id.tolist()
    failed = summaries[summaries.selected_gate_pass.astype(str).str.lower() != "true"].model_id.tolist()
    trace_rows: list[dict[str, object]] = []
    for model_id in passed:
        trace_path = RUN / "traces" / f"{model_id}_P1000_trace.csv"
        trace = pd.read_csv(trace_path)
        trace_rows.append(
            {
                "model_id": model_id,
                "trace_exists": trace_path.exists(),
                "trace_row_count": len(trace),
                "slice_index_min": int(trace.slice_index.min()),
                "slice_index_max": int(trace.slice_index.max()),
                "unique_slice_count": int(trace.slice_index.nunique()),
                "source_hash_exact": trace.source_geometry_sha256.nunique() == 1
                and trace.source_geometry_sha256.iloc[0] == expected_hashes[model_id],
                "retained_selected_count": int(trace.mask_retained.astype(bool).sum()),
                "finite_area_fraction": bool(np.isfinite(trace.area_fraction.to_numpy(float)).all()),
            }
        )

    full_exclusion_pass = all(
        not (RUN / "done" / f"{model}.json").exists() for model in failed
    ) and set(descriptors.model_id) == set(passed)
    protected = json.loads((RESULT / "DECISION_PACKET.json").read_text(encoding="utf-8"))
    checks = {
        "selected_replay_rows": len(replay_rows),
        "selected_replay_expected_rows": len(PANEL) * len(SELECTED),
        "all_source_hashes_exact": all(row["source_hash_match"] for row in replay_rows),
        "all_p1000_hashes_exact": all(row["p1000_hash_match"] for row in replay_rows),
        "all_p500_hashes_exact": all(row["p500_hash_match"] for row in replay_rows),
        "max_iou_abs_error": max(row["iou_abs_error"] for row in replay_rows),
        "max_area_difference_abs_error": max(row["area_difference_abs_error"] for row in replay_rows),
        "passed_models": passed,
        "failed_models": failed,
        "full_trace_model_count": len(trace_rows),
        "all_full_traces_exact_801": all(row["trace_row_count"] == 801 for row in trace_rows),
        "all_full_trace_indices_exact": all(
            row["slice_index_min"] == 0 and row["slice_index_max"] == 800
            and row["unique_slice_count"] == 801 for row in trace_rows
        ),
        "all_full_trace_hashes_exact": all(row["source_hash_exact"] for row in trace_rows),
        "all_full_trace_area_finite": all(row["finite_area_fraction"] for row in trace_rows),
        "all_selected_masks_retained": all(row["retained_selected_count"] == 9 for row in trace_rows),
        "failed_models_excluded_from_full": full_exclusion_pass,
        "descriptor_model_count": len(descriptors),
        "descriptor_average_fields": len(
            [column for column in descriptors if column.startswith("slice_z_") and column.endswith("_avg")]
        ),
        "no_y_column": not any(
            str(column).lower().startswith("y") or "performance" in str(column).lower()
            for column in descriptors.columns
        ),
        "all58_not_executed": set(PANEL) == set(summaries.model_id) and len(PANEL) == 7,
        "protected_notebooks_unchanged": protected["protected_unchanged"]
        and file_sha256(NB_CURRENT) == protected["protected_before"]["nb_current"]
        and file_sha256(NOTEBOOK) == protected["protected_before"]["notebook"],
    }
    boolean_checks = [value for value in checks.values() if isinstance(value, bool)]
    checks["status"] = "passed" if all(boolean_checks) and checks["selected_replay_rows"] == checks["selected_replay_expected_rows"] else "failed"
    write_csv(TABLES / f"{RUN_ID}_independent_selected_replay.csv", replay_rows)
    write_csv(TABLES / f"{RUN_ID}_independent_trace_audit.csv", trace_rows)
    (RESULT / "INDEPENDENT_QA.json").write_text(
        json.dumps(checks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    visual_rows = []
    for _, row in gate.iterrows():
        failed_slice = str(row.slice_gate_pass).lower() != "true"
        visual_rows.append(
            {
                "visual_id": f"I006-{row.model_id}-Z{int(row.slice_index):04d}",
                "model_id": row.model_id,
                "slice_index": int(row.slice_index),
                "gate_status": "failed" if failed_slice else "passed",
                "review_priority": "high" if failed_slice else "routine",
                "reason": "P500-to-P1000 resolution gate below threshold" if failed_slice else "selected-slice retained diagnostic",
                "p1000_image": str(RUN / "selected_gate_masks" / row.model_id / "P1000" / f"{row.model_id}_z{int(row.slice_index):04d}.png"),
                "p500_image": str(RUN / "selected_gate_masks" / row.model_id / "P500" / f"{row.model_id}_z{int(row.slice_index):04d}.png"),
            }
        )
    write_csv(TABLES / f"{RUN_ID}_selected_slice_visual_review_registry.csv", visual_rows)
    print(json.dumps(checks, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
