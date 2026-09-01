"""Two end-to-end P1000/Z801 descriptor smokes for the HQ deliverable."""

from __future__ import annotations

import json
import hashlib
import sys
from dataclasses import replace
from pathlib import Path

import pandas as pd
import trimesh

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from urp4.hq.v0_1 import URP4Controller, run_hq
from urp4.hq.v0_1.controller import (
    ArtifactControl,
    GeneratorControl,
    GeometryControl,
    LatticeControl,
    PathControl,
    TPMSControl,
    VoxelControl,
    WorkflowControl,
)


OUTPUT = ROOT / "outputs" / "smoke_full_descriptor"
FIXTURES = ROOT / "tests" / "fixtures"
L28_STL = FIXTURES / "L28_UBCCz_VF30_imported.stl"
GENERATED_FIXTURE = FIXTURES / "generated_controlled_box_N40.stl"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    GENERATED_FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    if not GENERATED_FIXTURE.is_file():
        trimesh.creation.box(extents=(40.0, 40.0, 40.0)).export(GENERATED_FIXTURE, file_type="stl")
    imported = URP4Controller(
            workflow=WorkflowControl(import_geometry=True, generate_geometry=False, extract_descriptors=True),
            paths=PathControl(input_geometry=str(L28_STL), output_root=str(OUTPUT)),
            geometry=GeometryControl(model_id="HQ-SMOKE-L28-VF30", source_type="imported_stl", expected_size_mm=40.0),
            artifacts=ArtifactControl(image_policy="STREAMING_TEMP_PNG"),
        )
    cases = [
        ("imported_l28_repeat_1", imported),
        ("imported_l28_repeat_2", imported),
        ("generated_fixture", URP4Controller(
            workflow=WorkflowControl(import_geometry=True, generate_geometry=False, extract_descriptors=True),
            paths=PathControl(input_geometry=str(GENERATED_FIXTURE), output_root=str(OUTPUT)),
            geometry=GeometryControl(model_id="HQ-SMOKE-GENERATED-FIXTURE", source_type="generated_stl", expected_size_mm=40.0),
            artifacts=ArtifactControl(image_policy="STREAMING_TEMP_PNG"),
        )),
        ("generated_lattice_type_a", URP4Controller(
            workflow=WorkflowControl(import_geometry=False, generate_geometry=True, extract_descriptors=True),
            paths=PathControl(output_root=str(OUTPUT)),
            geometry=GeometryControl(model_id="HQ-SMOKE-GEN-LATTICE", source_type="generated_stl", expected_size_mm=40.0),
            generator=GeneratorControl(family="lattice_type_a", random_seed=42, target_vf=0.30),
            lattice=LatticeControl(total_length_mm=40.0, cells_per_axis=3),
            artifacts=ArtifactControl(image_policy="STREAMING_TEMP_PNG"),
        )),
        ("generated_tpms", URP4Controller(
            workflow=WorkflowControl(import_geometry=False, generate_geometry=True, extract_descriptors=True),
            paths=PathControl(output_root=str(OUTPUT)),
            geometry=GeometryControl(model_id="HQ-SMOKE-GEN-TPMS", source_type="generated_stl", expected_size_mm=40.0),
            generator=GeneratorControl(family="tpms", random_seed=42, target_vf=0.50),
            tpms=TPMSControl(registry_index=0, grid_n=40),
            artifacts=ArtifactControl(image_policy="STREAMING_TEMP_PNG"),
        )),
        ("generated_voxel", URP4Controller(
            workflow=WorkflowControl(import_geometry=False, generate_geometry=True, extract_descriptors=True),
            paths=PathControl(output_root=str(OUTPUT)),
            geometry=GeometryControl(model_id="HQ-SMOKE-GEN-VOXEL", source_type="generated_stl", expected_size_mm=40.0),
            generator=GeneratorControl(family="voxel", random_seed=42, target_vf=0.30),
            voxel=VoxelControl(registry_index=0, grid_n=40, rows_per_mode=1),
            artifacts=ArtifactControl(image_policy="STREAMING_TEMP_PNG"),
        )),
    ]
    rows: list[dict[str, object]] = []
    for case_id, cfg in cases:
        try:
            status = run_hq(cfg, ROOT)
            descriptor = status["descriptor"] or {}
            rows.append({
                "case_id": case_id,
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
                "error": "",
            })
        except Exception as exc:
            rows.append({"case_id": case_id, "model_id": cfg.geometry.model_id, "status": "failed", "error": f"{type(exc).__name__}: {exc}"})
    frame = pd.DataFrame(rows)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    frame.to_csv(OUTPUT / "full_descriptor_smoke_results.csv", index=False, encoding="utf-8-sig")
    required_artifacts = (
        "run_manifest.json",
        "input_geometry_manifest.json",
        "output_manifest.csv",
        "training_required_input_schema.json",
        "descriptor_result.csv",
        "descriptor/tables/slice_pixel_count_table.csv",
        "descriptor/tables/slice_component_table.csv",
        "descriptor/tables/overlay_pixel_table.csv",
        "descriptor/tables/overlay_component_table.csv",
    )
    complete_manifests = all(
        all((Path(run_dir) / rel).is_file() for rel in required_artifacts)
        for run_dir in frame.loc[frame["status"].eq("passed"), "run_dir"]
    )
    repeat_dirs = [Path(path) for path in frame.loc[frame["case_id"].str.startswith("imported_l28_repeat_") & frame["status"].eq("passed"), "run_dir"]]
    imported_repeat_exact = len(repeat_dirs) == 2 and all(
        sha256(repeat_dirs[0] / rel) == sha256(repeat_dirs[1] / rel)
        for rel in (
            "descriptor_result.csv",
            "descriptor/tables/slice_pixel_count_table.csv",
            "descriptor/tables/slice_component_table.csv",
            "descriptor/tables/overlay_pixel_table.csv",
            "descriptor/tables/overlay_component_table.csv",
        )
    )
    passed = bool(
        (frame["status"] == "passed").all()
        and (frame["descriptor_status"] == "passed").all()
        and (frame["descriptor_rows"] == 9).all()
        and (frame["slice_rows"] == 801).all()
        and (frame["overlay_rows"] == 800).all()
        and (frame["readback_mismatch_sum"] == 0).all()
        and (frame["remaining_png"] == 0).all()
        and complete_manifests
        and imported_repeat_exact
    )
    summary = {
        "status": "passed" if passed else "failed",
        "case_count": len(frame),
        "complete_run_manifests": complete_manifests,
        "imported_repeat_exact": imported_repeat_exact,
        "results_csv": str(OUTPUT / "full_descriptor_smoke_results.csv"),
    }
    (OUTPUT / "full_descriptor_smoke_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(frame.to_string(index=False))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
