# COMP-FACTORY-004 pipeline reproduction guide

## Scope

This snapshot contains the exact producer, independent-QA, shared modelling dependency and factory/config files used for the 2026-08-02 B/C/L and Voronoi technical pilots. It does not promote any feature or model.

## Canonical runtime

- Python: 3.12.12
- Environment alias: KMK312
- Original executable provenance: `tools/envs/KMK312/python.exe`
- Portable recreation: use `03_CONFIG_RUNTIME_AND_COMMANDS/KMK312_CONDA_EXPLICIT_LOCK.txt`.

## Included execution chain

1. `COMP003_xlsx_structure_probe.py` — workbook structure probe (audit helper).
2. `COMP004_bcl_voronoi_intake.py` — protected source audit, explicit-ID crosswalk, exact x-y intake.
3. `COMP004_bcl_voronoi_independent_qa.py` — intake independent QA.
4. `COMP005_multigroup_fs4_pilot.py` — grouped four-method pilot.
5. `COMP005_multigroup_independent_qa.py` — metric/manifest independent QA.
6. `COMP006_artifact_output_validation.mjs` — table/image artifact validation.
7. `COMP002_ai_lattice_fs4_pilot.py` — shared model/feature-selection implementation dependency imported by COMP005.

## Pilot replay without the 1.35 GB raw Excel sources

The frozen COMP-FACTORY-003 exact-join dataset is included in the project-relative snapshot. From `project_snapshot/`:

```powershell
$env:URP4_KMK312_PYTHON = '<path-to-KMK312-python.exe>'
& $env:URP4_KMK312_PYTHON experiments/lab_001_xy_connection_20260626/scripts/COMP005_multigroup_fs4_pilot.py --run-id <NEW-BCL-RUN-ID> --cohort bcl
& $env:URP4_KMK312_PYTHON experiments/lab_001_xy_connection_20260626/scripts/COMP005_multigroup_fs4_pilot.py --run-id <NEW-VORONOI-RUN-ID> --cohort voronoi
```

Never reuse an existing run ID. The producer fails closed if the output directory already exists.

## Full intake replay

Download the separately delivered 11-workbook compression source asset and restore its files under:
`project_snapshot/experiments/lab_001_xy_connection_20260626/data/raw/doctor_compression_data_20260802/`.
Then verify every SHA against `04_REFERENCE_INPUTS/doctor_compression_data_20260802/SOURCE_MANIFEST.csv` before running COMP004.

- Drive source folder: https://drive.google.com/drive/folders/1XR1xMdQC9ePp_aWe-wsZB-kfYuGJRcmg
- The package includes the source manifest and small summary workbooks; the large raw workbooks remain an external read-only delivery asset.
- Do not run intake when any filename, byte size or SHA-256 differs from the source manifest.

## Scientific boundary

- B/C/L: 137 exact joins, 8,768 OOF predictions, QA-v2 10/10 PASS_WITH_WARNINGS.
- Voronoi: 30 exact joins, 1,920 OOF predictions, QA-v2 10/10 PASS_WITH_WARNINGS.
- No feature, method, target, production prediction, optimum, or inverse-design promotion.
- Next gate: target-specific grouped nested stability review, one target at a time.
