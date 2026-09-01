# ROUTE-VALID-002 merge packet

## Requested work

`ROUTE-VALID-002_B1_L7_CONFIRMED_PAIR_CROSS_FAMILY_SELECTED_SLICE_VALIDATION_NO_Y`

## Preconditions replayed

- ROUTE-VALID-001 official result and `13/13` independent QA exist.
- `RUN-357` and `ROUTE-VALID-001` are present in the required eight official logs.
- B1/L7 each remain `paired_confirmed`, `eligible`, `confirmed_metric_parity`, and hash-matched for original STEP plus separately stored STL.

## Changed / added work files

| Kind | Path |
|---|---|
| Producer | `scripts/ROUTE_VALID_002_b1_l7_cross_family_selected_slice.py` |
| Independent verifier | `scripts/ROUTE_VALID_002_independent_qa.py` |
| Source contract | `reports/tables/ROUTE-VALID-002-20260729-001_B1_L7_source_contract.csv` |
| Measurements | `reports/tables/ROUTE-VALID-002-20260729-001_route_ABC_measurements.csv` |
| Comparisons | `reports/tables/ROUTE-VALID-002-20260729-001_B1_L7_comparisons.csv` |
| Image registry | `reports/tables/ROUTE-VALID-002-20260729-001_image_hash_registry.csv` |
| QA | `results/ROUTE-VALID-002/ROUTE-VALID-002-20260729-001/INDEPENDENT_QA.json` |
| Report | `results/ROUTE-VALID-002/ROUTE-VALID-002-20260729-001/REPORT.md` |

## Result

- B1 and L7 each complete Route A–B and A–C at P500/P1000 z-mid.
- Every comparison is exact: IoU `1.0`, symmetric difference `0 px`, area delta `0`.
- B1’s transparent N40 grid adapter is used for a `2.5431e-6 mm` export micro-anisotropy; L7 uses the frozen exact-square grid without the adapter.
- Independent QA: `14/14 PASS`; protected baseline file hashes unchanged.

## Scope and interpretation locks

- A–B remains same-source STEP representation consistency only.
- A–C is a bounded confirmed-pair selected-slice imported-STL observation.
- No full Z801, descriptor formula parity, Excel/LEGACY-PY, y, feature selection, Training, inverse design, NB integration, source mutation, or all58 operation occurred.
- B3/L1 remain likely/sensitivity-only; F1 remains held for its stress test; T17 and STL-only assets remain excluded from official A–C comparison.

## Merge recommendation

**CONDITIONAL YES:** merge the result packet, run-local evidence, and roadmap/log status. Do not merge a production imported-STL default or any NB integration decision.

## Next action

`proceed_to_ROUTE_VALID_003_F1_stress_test`.
