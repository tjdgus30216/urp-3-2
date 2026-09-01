
# RESUME RUNBOOK — URP4-1_PROFESSOR_HANDOFF_20260802_v1_3_r1

This snapshot preserves the original project-relative layout expected by the selected scripts.
Treat this directory as `PROJECT_ROOT` after extraction to a short local path such as `C:\URP4_RESUME`.

## Runtime

- Canonical reference: project-local KMK312, Python 3.12.12.
- The environment itself is not embedded. Recreate/copy the environment separately and record `sys.executable`.
- Do not run from Google Drive synchronization paths when performing large image jobs.

## Safe first checks

```powershell
<KMK312_PYTHON> -m compileall -q experiments/lab_001_xy_connection_20260626/scripts URP4-1_DELIVERABLE/urp4
<KMK312_PYTHON> 00_VERIFY_RESUMABLE_HANDOFF.py
```

The verifier is read-only: it checks key paths, hashes, parseability and copied
accepted evidence.  It does not regenerate C1 or fit a model.

## Heavy pipelines — do not start accidentally

1. C1 Direct STEP production
   - Entry: `experiments/lab_001_xy_connection_20260626/scripts/STRICT_STEP_026_c1_direct_legacy_py_xonly.py`
   - Cost: heavy 801-slice direct B-rep job.
   - Input fixture included: C1 STEP and exact LEGACY-PY references.

2. Imported STL validation
   - Entry sequence in `experiments/lab_001_xy_connection_20260626/scripts/`:
     `IMSTL_006_small_generalization_factory.py` →
     `IMSTL_007_f1_resolution_pixel_phase_diagnosis.py` →
     `IMSTL_008_f1_full_p1000_z801_nonregression.py`.
   - Included local fixtures: B3/C1/L1/F1 N40 STL and paired B/C/F/L STEP/STL samples.
   - T1/T8/T9 inputs remain in the separate 67-file geometry archive.

3. XREG reproduction/extension
   - Frozen start: `PRM101_xreg_v0_3_*`.
   - First extract `RAW_SLICE_TABLES_XREG_V2_7.zip` into this snapshot root; it restores `.tmp/t4rs4/P1000_S801`.
   - Run the `PRM102*` through `PRM149*` scripts in numeric order; producer and independent-QA scripts remain paired.
   - Frozen raw inputs: `.tmp/t4rs4/P1000_S801/<model>/tables/*.csv|json`.
   - Final reference: `PRM149_xreg_v2_7_*` (542 candidates, no y, unselected).
   - New descriptor work should extend the final registry under a new version; never overwrite v2.7.

4. Pixel/slice optimization
   - `experiments/lab_001_xy_connection_20260626/scripts/R09_SLICE_005_*` and
     `PRM069_SLICE005_*` / `PRM070_SLICE005_*` are continuation tools.
   - Do not treat their presence as an all-descriptor convergence claim.

## External assets

- Full geometry: separate `URP4-1_GEOMETRY_REFERENCE_20260701_67FILES.zip` plus SHA receipt.
- KMK312 environment: not embedded.
- Large transient PNG streams: intentionally excluded; algorithms use streaming/temp deletion where applicable.

## Claim boundary

This is a packaging/reproducibility revision. It adds no new scientific result and does not authorize feature promotion, production prediction, or inverse design.
