"""Build the 21-cell, stage-explicit HQ v0.3 development notebook."""

from __future__ import annotations

from pathlib import Path
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "URP4-1_DELIVERABLE" / "URP4_1_HQ_v0_3_21CELL_DEV.ipynb"

def code(source: str):
    return nbf.v4.new_code_cell(source.strip() + "\n")

def main() -> None:
    introduction = """# URP4-1 HQ v0.3 — 21-cell controlled development integration

**Purpose.** This additive development HQ exposes the actual v0.1/v0.2
geometry → image → PNG readback → pixel/component → direct-descriptor path as
explicit stages. It does not modify the submitted `URP4_1_HQ.ipynb`,
NB-CURRENT, NB-ORIG, LEGACY-PY, original Excel, or source geometry.

**Status labels.** `passed` means the named runtime stage actually ran;
`partial` means only direct-9 output exists; `blocked` is a deliberate
fail-closed boundary; `exploratory_not_parity` means real image/pixel work
under a changed configuration, not an Excel/LEGACY parity claim."""
    user_control = r'''
# Cell 01 — 사용자 설정 | actual input contract
from pathlib import Path
from urp4.hq.v0_1.controller import (URP4Controller, WorkflowControl, PathControl, GeometryControl, ImportControl, GeneratorControl, LatticeControl, TPMSControl, VoxelControl, SliceControl, DescriptorControl, ArtifactControl, TrainingControl)
from urp4.hq.v0_2 import ExecutionControl, HQV02Controller

ROOT = Path.cwd().resolve()
if not (ROOT / "urp4").is_dir():
    raise RuntimeError("Open URP4-1_DELIVERABLE as the notebook working directory.")

# source_type: generated_stl | imported_stl | original_stp (inventory-only / fail-closed)
# STRICT = P1000/Z801/N40; a changed valid config needs EXPLORATORY.
EXECUTION = ExecutionControl(execution_mode="IMAGE_PIPELINE", qualification_mode="STRICT", descriptor_lane="LEGACY_DIRECT", frozen_table_root="", frozen_model_id="")
WORKFLOW = WorkflowControl(import_geometry=True, generate_geometry=False, extract_descriptors=True, feature_selection=False, training=False, run_batch=False)
PATHS = PathControl(input_geometry=r"", input_directory=r"", output_root="outputs/hq_v03_runs", experiment_name="URP4-HQ-v0.3", target_y="")
GEOMETRY = GeometryControl(model_id="MODEL-001", source_type="imported_stl", geometry_revision="user-input", expected_size_mm=40.0, normalize_imported_stl=True)
IMPORT = ImportControl(prefer_original_stp=True, allow_imported_stl=True, reject_topology_risk=False)
GENERATOR = GeneratorControl(family="lattice_type_a", random_seed=42, target_vf=0.30, requested_format="stl")
LATTICE = LatticeControl(total_length_mm=40.0, cell_definition_mode="cells_per_axis", cells_per_axis=5, cell_size_mm=None)
TPMS, VOXEL = TPMSControl(registry_index=0, grid_n=40), VoxelControl(registry_index=0, grid_n=40, rows_per_mode=1)
SLICING = SliceControl(axis="z", physical_size_mm=40.0, definition_mode="derive_count_from_spacing", slice_count=None, slice_spacing_mm=0.05, pixel_resolution=1000, connectivity=8, min_component_pixels=2, threshold_rule="binary_nonzero_png_readback")
DESCRIPTOR = DescriptorControl(point_enabled=False, surface_enabled=False, slice_enabled=True, lattice_enabled=False, candidate_enabled=False)
ARTIFACTS = ArtifactControl(image_policy="STREAMING_TEMP_PNG", overwrite=False, export_component_tables=True, visual_review_export=False)
CONTROL = HQV02Controller(base=URP4Controller(workflow=WORKFLOW, paths=PATHS, geometry=GEOMETRY, import_control=IMPORT, generator=GENERATOR, lattice=LATTICE, tpms=TPMS, voxel=VOXEL, slicing=SLICING, descriptor=DESCRIPTOR, artifacts=ARTIFACTS, training=TrainingControl()), execution=EXECUTION)
CONTROL
'''
    commands = [
        "# Cell 02 — config freeze | stage runtime validation\nfrom urp4.hq.v0_3 import HQStageSession\nSESSION = HQStageSession.create(CONTROL, ROOT)\nSESSION.contract",
        "# Cell 03 — stage / route 상태 | no geometry calculation\ndisplay(SESSION.stage_route_status())\ndisplay(SESSION.stage_status())",
        "# Cell 04 — source inventory | tables / immutable STL / STEP fail-closed\ndisplay(SESSION.source_inventory())",
        "# Cell 05 — geometry generation / import | submitted generator or immutable STL import\ndisplay(SESSION.geometry_generation_or_import())",
        "# Cell 06 — normalization | imported winding contract; execution happens in Cell 08\ndisplay(SESSION.normalization_contract())",
        "# Cell 07 — geometry QA | preflight / topology policy\ndisplay(SESSION.geometry_qa())",
        "# Cell 08 — slicing | actual image/mask/PNG-readback engine\ndisplay(SESSION.slicing_pixel_component())",
        "# Cell 09 — pixel / component | actual primitive table result\ndisplay(SESSION.records['09'])",
        "# Cell 10 — LEGACY descriptor | actual direct F001–F008 (9 scalar rows)\nDIRECT_X = SESSION.legacy_descriptor()\ndisplay(DIRECT_X)",
        "# Cell 11 — XREG candidate factory | separate lane; no hidden substitute\ndisplay(SESSION.xreg_factory_status())",
        "# Cell 12 — descriptor QA | direct/image QA\ndisplay(SESSION.descriptor_qa())",
        "# Cell 13 — full X export | direct-9 only; XREG API blocked\ndisplay(SESSION.full_x_export())",
        "# Cell 14 — y intake | fail-closed\ndisplay(SESSION.fail_closed_stage('14'))",
        "# Cell 15 — feature selection | fail-closed\ndisplay(SESSION.fail_closed_stage('15'))",
        "# Cell 16 — Training 1–5 | fail-closed\ndisplay(SESSION.fail_closed_stage('16'))",
        "# Cell 17 — model / ensemble | fail-closed\ndisplay(SESSION.fail_closed_stage('17'))",
        "# Cell 18 — forward chain | fail-closed\ndisplay(SESSION.fail_closed_stage('18'))",
        "# Cell 19 — inverse chain | fail-closed\ndisplay(SESSION.fail_closed_stage('19'))",
        "# Cell 20 — export / manifest | only this versioned run\ndisplay(SESSION.export_manifest())",
        "# Cell 21 — final gate | development result, never scientific production release\ndisplay(SESSION.final_gate())\ndisplay(SESSION.stage_status())",
    ]
    cells = [nbf.v4.new_markdown_cell(introduction), code(user_control), *[code(item) for item in commands]]
    nb = nbf.v4.new_notebook(cells=cells, metadata={"kernelspec": {"display_name": "KMK312 (Python 3.12.12)", "language": "python", "name": "kmk312"}, "language_info": {"name": "python", "version": "3.12.12"}})
    nbf.write(nb, TARGET)
    print(TARGET)

if __name__ == "__main__":
    main()
