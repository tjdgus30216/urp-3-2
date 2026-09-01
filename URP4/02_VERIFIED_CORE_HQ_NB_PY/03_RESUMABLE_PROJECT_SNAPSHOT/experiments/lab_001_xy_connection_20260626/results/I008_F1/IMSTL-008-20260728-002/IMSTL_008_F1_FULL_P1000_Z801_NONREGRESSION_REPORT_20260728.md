# IMSTL-008 F1 full P1000/Z801 extraction and family non-regression

- Accepted run: `IMSTL-008-20260728-002`
- Settings: `IDX-URP4-1-GEOM-IMPORTED-STL / CFG-IMSTL008-F1-P1000-Z801-HQREADBACK-NONREG r2`
- Runtime: KMK312 / Python 3.12.12
- Source: `F1__0dff3c1b13__N40.stl`
- Source SHA-256: `d76883bc10af4f4b3817ccbe90b2863f97c9b843f30c5214cde81d2f76fdb0f8`
- Result: **PASS — F1 full technical extraction and sampled-family non-regression**

## Execution history

`IMSTL-008-20260728-001` completed the expensive mask/readback loop but failed when Windows could not open the overlong primitive-table path. It is preserved as an infrastructure-only quarantine and has no scientific standing. Run `002` repeats the unchanged source, algorithm and P1000/Z801 settings with only a shorter project-local output root.

## Producer evidence

| Evidence | Result |
|---|---:|
| Slice images/readback rows | 801 |
| Adjacent overlays | 800 |
| Slice components | 39,506 |
| Overlay components | 38,187 |
| RUN-139 scalar rows | 9 |
| Temporary PNG created/deleted | 1,601 / 1,601 |
| PNG readback mismatch | 0 |
| Remaining PNG | 0 |
| Required artifact set | complete |

The run uses the official HQ v0.1 imported-STL image pipeline: oriented-winding slice mask → saved PNG → PNG readback → connected components and overlay pixel/component tables → RUN-139 scalar aggregation.

## F1 scalar results

| Formula | Statistic | Value | State |
|---|---|---:|---|
| `XRV1-F001` slice occupancy | mean | 0.2882551623 | confirmed |
| `XRV1-F002` slice occupancy | std_pop | 0.0982941481 | confirmed |
| `XRV1-F003` component count | mean | 49.32084894 | confirmed |
| `XRV1-F004` component count | std_pop | 30.82519969 | confirmed |
| `XRV1-F005` overlay change fraction | mean | 0.0554537366 | confirmed |
| `XRV1-F006` overlay overlap fraction | mean | 0.9445462634 | confirmed |
| `XRV1-F007` thickness component | mean | 2.9592604390 mm | likely |
| `XRV1-F007` thickness component | std_pop | 0.9575777509 mm | likely |
| `XRV1-F008` MassOri component pool | mean | 0.9720345420 | likely |

The state labels are formula-lineage labels inherited from HQ v0.1. A technically reproducible value is not automatically a canonical physical descriptor or a predictive feature.

## Independent QA

- All nine scalar rows were recalculated directly from the four primitive CSV tables: `9/9 PASS`.
- Maximum scalar replay error: `7.105427357601002e-15`.
- F1 selected P1000 masks reproduce the accepted IMSTL-007 P00 masks: `9/9 exact`.
- B3/C1/L1/T1/T8/T9 selected P1000 masks reproduce the accepted IMSTL-006 traces: `54/54 exact`.
- Each prior-family trace remains 801 rows, finite and source-hash exact.
- IMSTL-006 and IMSTL-007 run/result tree identities are unchanged.
- Blueprint protected assets remain `31/31` unchanged.
- No y columns, all58 run, feature selection, model fitting, NB-CURRENT edit or LEGACY-PY edit occurred.

## Scientific decision

- **confirmed:** F1 can complete the approved imported-STL P1000/Z801 image-readback technical chain.
- **confirmed:** the new F1 run does not regress the accepted sampled B/C/L/T evidence.
- **likely:** F1's RUN-139 F007/F008 values are reproducible under their current formula lineage.
- **unresolved:** exact original-STP parity, other F geometries, all58 generalization, canonical descriptor identity and performance utility.
- **rejected:** interpreting the earlier F1 selected-slice miss as a broken imported-STL route.

This closes the bounded IMSTL-007→008 F1 question. It does not unlock y, Training, feature promotion, all58, direct STP descriptors or inverse design.

## Next gate

`HQ-GEOM-001_GENERATED_FAMILY_40MM_NORMALIZATION_IMPLEMENTATION_AND_REGRESSION_NO_Y`

This next gate implements and tests the already-adopted 40×40×40 mm analysis-geometry policy for generated Lattice/TPMS/Voxel without changing the protected source generators or opening y/modeling.

