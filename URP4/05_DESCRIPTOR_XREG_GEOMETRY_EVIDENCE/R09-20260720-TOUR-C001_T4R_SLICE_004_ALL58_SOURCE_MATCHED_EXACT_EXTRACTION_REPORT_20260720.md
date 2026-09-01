# TOUR-C001-T4R-SLICE-004 all-58 source-matched exact extraction

## Outcome

Status: **confirmed technical/source pass; scientific promotion not evaluated**.

The canonical N40 population was processed under one frozen image/pixel/direct-LEGACY contract. All 58 models have a source path and SHA-256, a complete per-model trace packet, and 40 mapped candidate values. This run creates the source-matched all-58 `x` database requested by the frozen contract; it does not select a feature or test predictive utility.

## Frozen execution boundary

- Runtime: `KMK312`, Python `3.12.12`
- Geometry: canonical N40 STL, `40 × 40 × 40 mm`
- Axis/configuration: `z`, `1000 × 1000 px`, 801 endpoint slices, 0.05 mm spacing
- Trace: saved-PNG readback, pixel/component tables, direct `LEGACY-PY` calculation
- Output: 40 lineage-labelled candidates per model
- Explicitly absent: performance `y`, model fitting, feature selection/promotion, Excel parity conclusion, NB-CURRENT/LEGACY-PY modification, inverse-design claim

Frozen contract:

`experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/contracts/TOUR-C001_T4R_SLICE_004_ALL58_SOURCE_MATCHED_EXACT_EXTRACTION_20260720.json`

## Execution result

| Check | Result |
|---|---:|
| canonical geometry path/hash | 58/58 |
| complete model packets | 58/58 |
| reused / newly sliced | 7 / 51 |
| slice rows | 46,458 |
| overlay rows | 46,400 |
| component rows | 3,279,507 |
| mapped candidate rows | 2,320 = 58 × 40 |
| finite / missing candidate values | 2,320 / 0 |
| fixed rescue-signal rows | 232 = 58 × 4 |
| saved-PNG readback mismatches | 0 |
| transient PNG deleted / remaining | 91,258 / 0 |
| audit PNG retained | 348 = 58 × 6 |
| performance y / fits / promotions | 0 / 0 / 0 |

The seven reused models were B3, C1, L1, F1, F2, T8 and T9. Reuse required matching geometry/configuration/output evidence; the other 51 models were calculated anew.

## Failure isolation and resume evidence

The two-worker batch completed 57 models without a scientific failure. T16 initially exhausted memory while both workers were active because its source mesh contains approximately 42.79 million vertices and 14.26 million faces. A first single-worker retry was invalidated by an orchestration stdout-handle failure. Neither attempt produced an accepted complete packet.

T16 was then restarted as the sole worker under the unchanged frozen source/configuration and passed in 699.0 seconds. No completed model or shard was rerun. The complete attempt record is:

`experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/analysis_factory/reports/TOUR-C001-T4R-SLICE-004_attempt_history.csv`

## Independent integrity review

Independent QA passed 19/19 gates:

- execution-code hash matched the contract;
- parent evidence 8/8 and canonical geometry 58/58 matched frozen hashes;
- all per-model and aggregate row-count gates passed;
- all 2,320 values are finite;
- PNG readback mismatch and transient remainder are zero;
- protected research assets, Master Ledger v0.2 and Tournament HQ are unchanged 29/29;
- no KMK312 worker remained after completion;
- output files were hashed in the retained-artifact manifest.

Evidence:

- `experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/analysis_factory/reports/TOUR-C001-T4R-SLICE-004_independent_QA.csv`
- `experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/analysis_factory/reports/TOUR-C001-T4R-SLICE-004_protected_asset_verification.csv`
- `experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/analysis_factory/reports/TOUR-C001-T4R-SLICE-004_output_manifest.csv`

## Principal data products

- All 40 candidates: `experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/analysis_factory/frozen/TOUR-C001-T4R-SLICE-004_all58_direct_legacy_candidate_values.csv`
- Four fixed rescue signals: `experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/analysis_factory/frozen/TOUR-C001-T4R-SLICE-004_all58_selected_rescue_signals.csv`
- Per-model QA: `experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/analysis_factory/reports/TOUR-C001-T4R-SLICE-004_model_execution_QA.csv`
- Per-model trace packets: `.tmp/t4rs4/P1000_S801/<model_id>/`

## Scientific interpretation and stop boundary

This run confirms that the exact source-matched extraction pipeline can produce a complete, finite and traceable 58-model detailed-`x` database. It does **not** confirm that any candidate is canonical, historically Excel-identical, nonredundant across all 58 models, or predictive of performance.

Per the task boundary, work stops here. Candidate census, `x-x`, Excel parity, `x-y`, feature promotion and model fitting require a separate preregistered/reviewed task.
