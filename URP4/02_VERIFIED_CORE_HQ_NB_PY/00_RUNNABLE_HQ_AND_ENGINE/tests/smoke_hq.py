"""KMK312 smoke tests for HQ routing, generation and fail-closed guards."""

from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from urp4.hq.v0_1 import URP4Controller, run_hq, validate_and_freeze
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


OUTPUT = ROOT / "outputs" / "smoke"
FIXTURES = ROOT / "tests" / "fixtures"
L28_STL = FIXTURES / "L28_UBCCz_VF30_imported.stl"
L28_STP = FIXTURES / "L28_UBCCz_VF30_original.stp"


def base() -> URP4Controller:
    return URP4Controller(
        workflow=WorkflowControl(import_geometry=False, generate_geometry=True, extract_descriptors=False),
        paths=PathControl(output_root=str(OUTPUT)),
        geometry=GeometryControl(model_id="SMOKE", source_type="generated_stl", expected_size_mm=40.0),
        generator=GeneratorControl(family="lattice_type_a", random_seed=42, target_vf=0.30),
        lattice=LatticeControl(total_length_mm=40.0, cells_per_axis=3),
        tpms=TPMSControl(registry_index=0, grid_n=40),
        voxel=VoxelControl(registry_index=0, grid_n=40, rows_per_mode=1),
        artifacts=ArtifactControl(image_policy="STREAMING_TEMP_PNG"),
    )


def main() -> None:
    rows: list[dict[str, object]] = []
    for family in ("lattice_type_a", "tpms", "voxel"):
        target_vf = 0.50 if family == "tpms" else 0.30
        cfg = replace(
            base(),
            geometry=replace(base().geometry, model_id=f"SMOKE-{family.upper()}"),
            generator=replace(base().generator, family=family, target_vf=target_vf),
        )
        try:
            status = run_hq(cfg, ROOT)
            rows.append({"case": family, "expected": "passed", "observed": status["status"], "route": status["route_id"], "run_dir": status["run_dir"]})
        except Exception as exc:
            rows.append({"case": family, "expected": "passed", "observed": "failed", "route": "", "run_dir": "", "error": f"{type(exc).__name__}: {exc}"})

    for source_type, path in (("imported_stl", L28_STL), ("original_stp", L28_STP)):
        cfg = replace(
            base(),
            workflow=WorkflowControl(import_geometry=True, generate_geometry=False, extract_descriptors=False),
            paths=PathControl(input_geometry=str(path), output_root=str(OUTPUT)),
            geometry=GeometryControl(model_id=f"SMOKE-{source_type.upper()}", source_type=source_type, expected_size_mm=40.0),
        )
        try:
            status = run_hq(cfg, ROOT)
            rows.append({"case": source_type, "expected": "passed", "observed": status["status"], "route": status["route_id"], "run_dir": status["run_dir"]})
        except Exception as exc:
            rows.append({"case": source_type, "expected": "passed", "observed": "failed", "route": "", "run_dir": "", "error": f"{type(exc).__name__}: {exc}"})

    guard_cases = {
        "import_generate_xor": replace(base(), workflow=WorkflowControl(import_geometry=True, generate_geometry=True, extract_descriptors=False)),
        "training_without_y": replace(base(), workflow=WorkflowControl(import_geometry=False, generate_geometry=True, extract_descriptors=False, training=True)),
        "type_b_missing_workbook": replace(base(), generator=replace(base().generator, family="lattice_type_b")),
        "stp_descriptor_fail_closed": replace(
            base(),
            workflow=WorkflowControl(import_geometry=True, generate_geometry=False, extract_descriptors=True),
            paths=PathControl(input_geometry=str(L28_STP), output_root=str(OUTPUT)),
            geometry=GeometryControl(model_id="SMOKE-STP-DESC", source_type="original_stp"),
        ),
    }
    for name, cfg in guard_cases.items():
        try:
            if name == "type_b_missing_workbook":
                run_hq(cfg, ROOT)
            else:
                validate_and_freeze(cfg, ROOT)
            rows.append({"case": name, "expected": "rejected", "observed": "unexpected_pass", "route": "", "run_dir": ""})
        except Exception as exc:
            rows.append({"case": name, "expected": "rejected", "observed": "rejected", "route": "", "run_dir": "", "error": f"{type(exc).__name__}: {exc}"})

    frame = pd.DataFrame(rows)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    frame.to_csv(OUTPUT / "smoke_results.csv", index=False, encoding="utf-8-sig")
    passed = bool(((frame["expected"] == "passed") & (frame["observed"] == "passed") | (frame["expected"] == "rejected") & (frame["observed"] == "rejected")).all())
    summary = {"status": "passed" if passed else "failed", "case_count": len(frame), "passed_case_count": int(sum(frame["expected"].eq(frame["observed"]))), "results_csv": str(OUTPUT / "smoke_results.csv")}
    (OUTPUT / "smoke_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(frame.to_string(index=False))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
