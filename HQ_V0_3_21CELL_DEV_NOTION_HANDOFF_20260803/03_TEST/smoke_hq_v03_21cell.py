"""KMK312 smoke verification for the explicit 21-cell HQ v0.3 development route.

Outputs are intentionally placed in outputs/hq_v03_smoke and are not scientific
evidence or submission assets.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from urp4.hq.v0_1.controller import (  # noqa: E402
    ArtifactControl,
    DescriptorControl,
    GeometryControl,
    PathControl,
    SliceControl,
    URP4Controller,
    WorkflowControl,
)
from urp4.hq.v0_2 import ExecutionControl, HQV02Controller  # noqa: E402
from urp4.hq.v0_3 import HQStageSession  # noqa: E402


def replay_session(table_root: Path) -> HQStageSession:
    base = URP4Controller(
        workflow=WorkflowControl(import_geometry=True, generate_geometry=False, extract_descriptors=True),
        paths=PathControl(output_root="outputs/hq_v03_smoke", experiment_name="HQV03-frozen-smoke"),
        geometry=GeometryControl(model_id="", source_type="imported_stl"),
        slicing=SliceControl(),
        descriptor=DescriptorControl(slice_enabled=True),
        artifacts=ArtifactControl(),
    )
    control = HQV02Controller(
        base=base,
        execution=ExecutionControl(execution_mode="FROZEN_REPLAY", frozen_table_root=str(table_root)),
    )
    session = HQStageSession.create(control, ROOT)
    session.stage_route_status()
    session.source_inventory()
    session.geometry_generation_or_import()
    session.normalization_contract()
    session.geometry_qa()
    session.slicing_pixel_component()
    session.legacy_descriptor()
    session.xreg_factory_status()
    session.descriptor_qa()
    session.full_x_export()
    for cell in ("14", "15", "16", "17", "18", "19"):
        session.fail_closed_stage(cell)
    session.export_manifest()
    session.final_gate()
    return session


def exploratory_session(fixture: Path, policy: str) -> HQStageSession:
    base = URP4Controller(
        workflow=WorkflowControl(import_geometry=True, generate_geometry=False, extract_descriptors=True),
        paths=PathControl(input_geometry=str(fixture), output_root="outputs/hq_v03_smoke", experiment_name=f"HQV03-{policy}"),
        geometry=GeometryControl(model_id="HQV03-EXP-PARITY", source_type="generated_stl", expected_size_mm=40.0),
        slicing=SliceControl(
            physical_size_mm=40.0,
            definition_mode="derive_count_from_spacing",
            slice_count=None,
            slice_spacing_mm=5.0,
            pixel_resolution=128,
            connectivity=8,
            min_component_pixels=2,
        ),
        descriptor=DescriptorControl(slice_enabled=True),
        artifacts=ArtifactControl(image_policy=policy),
    )
    control = HQV02Controller(base=base, execution=ExecutionControl(execution_mode="IMAGE_PIPELINE", qualification_mode="EXPLORATORY"))
    session = HQStageSession.create(control, ROOT)
    session.stage_route_status()
    session.source_inventory()
    session.geometry_generation_or_import()
    session.normalization_contract()
    session.geometry_qa()
    session.slicing_pixel_component()
    session.legacy_descriptor()
    session.xreg_factory_status()
    session.descriptor_qa()
    session.full_x_export()
    session.export_manifest()
    session.final_gate()
    return session


def compare_frames(a: Path, b: Path, keys: list[str]) -> float:
    left, right = pd.read_csv(a, encoding="utf-8-sig"), pd.read_csv(b, encoding="utf-8-sig")
    merged = left.merge(right, on=keys, suffixes=("_a", "_b"), validate="one_to_one")
    if len(merged) != len(left) or len(merged) != len(right):
        raise AssertionError(f"row mismatch: {a} vs {b}")
    return float((merged["value_a"] - merged["value_b"]).abs().max())


def main() -> None:
    primitive = next((ROOT / "outputs" / "smoke_full_descriptor").rglob("overlay_pixel_table.csv"), None)
    fixture = next((ROOT / "outputs" / "smoke").rglob("*.stl"), None)
    if primitive is None or fixture is None:
        raise SystemExit("Missing committed v0.1 smoke fixtures")
    replay = replay_session(primitive.parent)
    replay_csv = replay.run_dir / "descriptor_result.csv"
    frozen_reference = primitive.parent.parent.parent / "descriptor_result.csv"
    frozen_error = compare_frames(frozen_reference, replay_csv, ["formula_id", "statistic"])
    assert frozen_error == 0.0

    full = exploratory_session(fixture, "KEEP_ALL")
    streaming = exploratory_session(fixture, "STREAMING_TEMP_PNG")
    parity_error = compare_frames(full.run_dir / "descriptor_result.csv", streaming.run_dir / "descriptor_result.csv", ["formula_id", "statistic"])
    assert parity_error == 0.0
    for name in ("slice_pixel_count_table.csv", "overlay_pixel_table.csv", "overlay_component_table.csv"):
        a = pd.read_csv(full.run_dir / "descriptor" / "tables" / name)
        b = pd.read_csv(streaming.run_dir / "descriptor" / "tables" / name)
        assert a.equals(b), name
    assert set(pd.read_csv(full.run_dir / "descriptor_result.csv")["state"]) == {"experimental"}

    stp = ROOT / "tests" / "fixtures" / "L28_UBCCz_VF30_original.stp"
    step_base = URP4Controller(
        workflow=WorkflowControl(import_geometry=True, generate_geometry=False, extract_descriptors=True),
        paths=PathControl(input_geometry=str(stp), output_root="outputs/hq_v03_smoke"),
        geometry=GeometryControl(model_id="STEP-BLOCK", source_type="original_stp"),
        slicing=SliceControl(), descriptor=DescriptorControl(slice_enabled=True), artifacts=ArtifactControl(),
    )
    step_session = HQStageSession.create(HQV02Controller(base=step_base, execution=ExecutionControl()), ROOT)
    assert step_session.source_inventory()["status"] == "blocked"
    assert step_session.geometry_generation_or_import()["status"] == "blocked"
    assert step_session.normalization_contract()["status"] == "blocked"

    status = {
        "status": "passed",
        "runtime": sys.executable,
        "frozen_replay_exact_scalar_error": frozen_error,
        "artifact_full_streaming_exact_scalar_error": parity_error,
        "frozen_run": str(replay.run_dir),
        "artifact_full_run": str(full.run_dir),
        "streaming_run": str(streaming.run_dir),
        "step_status": "fail_closed",
        "xreg_status": "fail_closed",
    }
    print(json.dumps(status, ensure_ascii=False))


if __name__ == "__main__":
    main()
