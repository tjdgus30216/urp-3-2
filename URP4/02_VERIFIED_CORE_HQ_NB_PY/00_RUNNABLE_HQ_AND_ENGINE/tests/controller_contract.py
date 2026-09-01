"""Fast fail-closed contract checks for the HQ Cell-1 controller."""

from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from urp4.hq.v0_1 import URP4Controller, validate_and_freeze
from urp4.hq.v0_1.controller import (
    ArtifactControl,
    GeneratorControl,
    GeometryControl,
    ImportControl,
    LatticeControl,
    PathControl,
    SliceControl,
    TPMSControl,
    TrainingControl,
    VoxelControl,
    WorkflowControl,
)


FIXTURES = ROOT / "tests" / "fixtures"
L28_STL = FIXTURES / "L28_UBCCz_VF30_imported.stl"
L28_STP = FIXTURES / "L28_UBCCz_VF30_original.stp"


def generated(*, descriptors: bool = False) -> URP4Controller:
    return URP4Controller(
        workflow=WorkflowControl(import_geometry=False, generate_geometry=True, extract_descriptors=descriptors),
        paths=PathControl(output_root="outputs"),
        geometry=GeometryControl(model_id="CONTRACT-GEN", source_type="generated_stl", expected_size_mm=40.0),
        generator=GeneratorControl(family="lattice_type_a", random_seed=42, target_vf=0.30),
        lattice=LatticeControl(total_length_mm=40.0, cells_per_axis=5),
        artifacts=ArtifactControl(image_policy="STREAMING_TEMP_PNG"),
    )


def imported(*, source_type: str = "imported_stl", descriptors: bool = True) -> URP4Controller:
    path = L28_STP if source_type == "original_stp" else L28_STL
    return URP4Controller(
        workflow=WorkflowControl(import_geometry=True, generate_geometry=False, extract_descriptors=descriptors),
        paths=PathControl(input_geometry=str(path), output_root="outputs"),
        geometry=GeometryControl(model_id="CONTRACT-IMP", source_type=source_type, expected_size_mm=40.0),
        artifacts=ArtifactControl(image_policy="STREAMING_TEMP_PNG"),
    )


def main() -> None:
    passed: list[str] = []

    def accept(name: str, cfg: URP4Controller) -> None:
        validate_and_freeze(cfg, ROOT)
        passed.append(name)

    def reject(name: str, cfg: URP4Controller) -> None:
        try:
            validate_and_freeze(cfg, ROOT)
        except Exception:
            passed.append(name)
            return
        raise AssertionError(f"{name}: unexpectedly accepted")

    accept("generated_generation_only", generated())
    accept("generated_descriptor_profile", generated(descriptors=True))
    accept("imported_descriptor_profile", imported())
    accept("original_stp_preflight_only", imported(source_type="original_stp", descriptors=False))
    accept("imported_keep_flagged", replace(imported(), artifacts=ArtifactControl(image_policy="KEEP_FLAGGED")))
    accept("derive_spacing_from_count", replace(generated(), slicing=SliceControl(definition_mode="derive_spacing_from_count", slice_count=801, slice_spacing_mm=None)))
    accept("tpms_source_replay_vf", replace(generated(), generator=GeneratorControl(family="tpms", random_seed=42, target_vf=0.50)))

    base = generated()
    reject("import_generate_xor", replace(base, workflow=WorkflowControl(import_geometry=True, generate_geometry=True, extract_descriptors=False)))
    reject("input_directory_locked", replace(base, paths=replace(base.paths, input_directory="future_batch")))
    reject("batch_locked", replace(base, workflow=replace(base.workflow, run_batch=True)))
    reject("training_locked", replace(base, workflow=replace(base.workflow, training=True)))
    reject("point_descriptor_locked", replace(base, descriptor=replace(base.descriptor, point_enabled=True)))
    reject("axis_locked", replace(base, slicing=replace(base.slicing, axis="x")))
    reject("threshold_locked", replace(base, slicing=replace(base.slicing, threshold_rule="other")))
    reject("empty_output_root", replace(base, paths=replace(base.paths, output_root="")))
    reject("empty_model_id", replace(base, geometry=replace(base.geometry, model_id="")))
    reject("empty_geometry_revision", replace(base, geometry=replace(base.geometry, geometry_revision="")))
    reject("nonpositive_expected_size", replace(base, geometry=replace(base.geometry, expected_size_mm=0.0)))
    reject("negative_seed", replace(base, generator=replace(base.generator, random_seed=-1)))
    reject("invalid_target_vf", replace(base, generator=replace(base.generator, target_vf=1.0)))
    reject("tpms_unqualified_vf", replace(base, generator=GeneratorControl(family="tpms", random_seed=42, target_vf=0.30)))
    reject("negative_registry_index", replace(base, tpms=TPMSControl(registry_index=-1, grid_n=40)))
    reject("invalid_grid", replace(base, voxel=VoxelControl(registry_index=0, grid_n=1, rows_per_mode=1)))
    reject("invalid_rows_per_mode", replace(base, voxel=VoxelControl(registry_index=0, grid_n=40, rows_per_mode=0)))
    reject("conflicting_slice_count", replace(base, slicing=replace(base.slicing, slice_count=801)))
    reject("conflicting_slice_spacing", replace(base, slicing=SliceControl(definition_mode="derive_spacing_from_count", slice_count=801, slice_spacing_mm=0.05)))
    reject("conflicting_cell_size", replace(base, lattice=replace(base.lattice, cell_size_mm=8.0)))
    reject("conflicting_cell_count", replace(base, lattice=LatticeControl(cell_definition_mode="cell_size_mm", cells_per_axis=5, cell_size_mm=8.0)))
    reject("overwrite_locked", replace(base, artifacts=replace(base.artifacts, overwrite=True)))
    reject("prefer_stp_policy_locked", replace(base, import_control=ImportControl(prefer_original_stp=False)))
    reject("grouped_split_policy_locked", replace(base, training=TrainingControl(grouped_split_required=False)))
    reject("duplicate_training_method_id", replace(base, training=TrainingControl(method_ids=("TRAIN-METHOD-01", "TRAIN-METHOD-01"))))
    reject("generate_with_input_path", replace(base, paths=replace(base.paths, input_geometry=str(L28_STL))))
    reject("generate_source_type_mismatch", replace(base, geometry=replace(base.geometry, source_type="imported_stl")))
    reject("stp_descriptor_locked", imported(source_type="original_stp", descriptors=True))
    reject("descriptor_expected_size_n40", replace(imported(), geometry=replace(imported().geometry, expected_size_mm=30.0)))
    reject("descriptor_physical_size_match", replace(imported(), slicing=replace(imported().slicing, physical_size_mm=30.0)))
    reject("lattice_size_match", replace(generated(descriptors=True), lattice=replace(generated(descriptors=True).lattice, total_length_mm=30.0)))
    reject("generated_keep_flagged_locked", replace(generated(descriptors=True), artifacts=ArtifactControl(image_policy="KEEP_FLAGGED")))
    reject("imported_stl_disallowed", replace(imported(), import_control=ImportControl(allow_imported_stl=False)))

    summary = {"status": "passed", "case_count": len(passed), "cases": passed}
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
