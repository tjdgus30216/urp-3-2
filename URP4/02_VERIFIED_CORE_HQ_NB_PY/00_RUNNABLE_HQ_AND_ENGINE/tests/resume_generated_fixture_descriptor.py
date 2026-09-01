"""Resume the generated-route full descriptor smoke with a minimal controlled STL."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import trimesh

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from urp4.hq.v0_1 import URP4Controller, run_hq
from urp4.hq.v0_1.controller import ArtifactControl, GeometryControl, PathControl, WorkflowControl


OUTPUT = ROOT / "outputs" / "smoke_full_descriptor"
FIXTURE = ROOT / "tests" / "fixtures" / "generated_controlled_box_N40.stl"


def main() -> None:
    FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    if not FIXTURE.is_file():
        mesh = trimesh.creation.box(extents=(40.0, 40.0, 40.0))
        mesh.export(FIXTURE, file_type="stl")
    cfg = URP4Controller(
        workflow=WorkflowControl(import_geometry=True, generate_geometry=False, extract_descriptors=True),
        paths=PathControl(input_geometry=str(FIXTURE), output_root=str(OUTPUT)),
        geometry=GeometryControl(model_id="HQ-SMOKE-GENERATED-FIXTURE", source_type="generated_stl", expected_size_mm=40.0),
        artifacts=ArtifactControl(image_policy="STREAMING_TEMP_PNG"),
    )
    status = run_hq(cfg, ROOT)
    descriptor = status["descriptor"] or {}
    row = {
        "model_id": cfg.geometry.model_id,
        "route_id": status["route_id"],
        "status": status["status"],
        "descriptor_status": descriptor.get("status"),
        "descriptor_rows": descriptor.get("row_count"),
        "slice_rows": descriptor.get("qa", {}).get("slice_rows"),
        "overlay_rows": descriptor.get("qa", {}).get("overlay_rows"),
        "readback_mismatch_sum": descriptor.get("qa", {}).get("readback_mismatch_sum"),
        "remaining_png": descriptor.get("qa", {}).get("remaining_png"),
        "run_dir": status["run_dir"],
    }
    result_path = OUTPUT / "generated_fixture_descriptor_smoke.csv"
    pd.DataFrame([row]).to_csv(result_path, index=False, encoding="utf-8-sig")
    passed = (
        row["status"] == "passed"
        and row["descriptor_status"] == "passed"
        and row["descriptor_rows"] == 9
        and row["slice_rows"] == 801
        and row["overlay_rows"] == 800
        and row["readback_mismatch_sum"] == 0
        and row["remaining_png"] == 0
    )
    summary = {"status": "passed" if passed else "failed", "result_csv": str(result_path), "run_dir": status["run_dir"]}
    (OUTPUT / "generated_fixture_descriptor_smoke_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(pd.DataFrame([row]).to_string(index=False))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
