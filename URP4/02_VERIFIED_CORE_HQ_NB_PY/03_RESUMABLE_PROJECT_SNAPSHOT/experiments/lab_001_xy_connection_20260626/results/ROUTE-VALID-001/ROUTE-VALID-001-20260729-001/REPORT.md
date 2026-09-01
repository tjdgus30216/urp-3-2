# ROUTE-VALID-001 — source eligibility and C1 three-route selected-slice validation

- Work / run: `ROUTE-VALID-001_SOURCE_ELIGIBILITY_AND_THREE_ROUTE_SELECTED_SLICE_VALIDATION_NO_Y` / `ROUTE-VALID-001-20260729-001`
- Settings: `IDX-URP4-1-GEOM-ROUTES / CFG-ROUTEVALID001-C1-ZMID-P1000 r1`
- Runtime: `KMK312` (Python 3.12.12)
- Scope stop: source eligibility for all 58 and C1 at one selected `z-mid`, `1000×1000 px` slice only. No B1/L7/F1 expansion, no full Z801, no descriptor, Excel/LEGACY-PY parity, y, learning, or inverse design.

## 1. Correct route meanings

| Route | Input | Meaning | What it may establish |
|---|---|---|---|
| A | original STEP direct B-rep | native STEP section and material raster | STEP-reference mask for the bounded slice |
| B | controlled tessellation generated from that same STEP | second representation of the same source | A–B representation consistency only |
| C | separately stored paired imported STL | `ORIENTED_NONZERO_RAW/IMSTL-004/r1` winding path | A–C selected-slice geometry-preservation observation, only for a confirmed source pair |

**Important correction:** prior STRICT-STEP-015/016 (B3) and STRICT-STEP-018 (C1/L1) A–B results are not independent imported-STL tests. They use controlled tessellation from the same original STEP. They must not be cited as imported-STL slicer validation.

## 2. Hash-bound asset eligibility audit

The audit read the authoritative inventory and metric-parity registry and SHA-256 rechecked every inventory source plus every registered STEP/STL pair on disk.

| Eligibility | Count | Route A–C policy |
|---|---:|---|
| `paired_confirmed` | 24 | official selected-slice A–C observation allowed |
| `paired_likely` | 9 | sensitivity only; never an official imported-STL accuracy judgement |
| `stl_only` | 25 | STEP↔STL comparison prohibited |
| `missing_or_hash_mismatch` | 0 | none found in this audit |

The `stl_only` group is exactly `L12–L20` and `T1–T16`. The inventory does not justify inferring any absent STEP source for those models. `B3` and `L1` are `paired_likely`, not confirmed. `T17` remains excluded from official A–C comparison until its recorded orientation crosswalk is solved.

Core-pilot eligibility after SHA replay:

| Model | Eligibility | Official A–C use |
|---|---|---|
| C1 | `paired_confirmed` | eligible — executed in this run |
| B1 | `paired_confirmed` | eligible — not executed |
| L7 | `paired_confirmed` | eligible — not executed |
| F1 | `paired_confirmed` | eligible, pixel-phase stress test — not executed |
| B3 / L1 | `paired_likely` | sensitivity only — not executed |
| T17 | `paired_likely` | orientation hold — not executed |

Evidence: [eligibility table](../../../reports/tables/ROUTE-VALID-001-20260729-001_source_eligibility.csv).

## 3. C1 selected-slice result

C1 is a hash-matched `confirmed_metric_parity` STEP/STL pair. Route A and B use the pre-existing, hash-recorded `STRICT-STEP-018` C1 P1000 masks. Route C uses the **separately stored C1 STL** (`7755…999bd`), not a tessellation produced during this task.

| Comparison | Mask IoU | Symmetric difference | Area relative delta | Components / holes (diagnostic) |
|---|---:|---:|---:|---:|
| A–B (same STEP) | 1.000000 | 0 px / 0.0000 mm² | 0.000000 | 37 / 41 vs 37 / 41 |
| A–C (original STEP vs paired imported STL) | 1.000000 | 0 px / 0.0000 mm² | 0.000000 | 37 / 41 vs 37 / 41 |

At this one selected C1 slice, the confirmed paired STL gives an exact P1000 mask match with the original STEP reference. Route C took `0.163 s` for section plus rasterization after source load.

### Route-C micro-anisotropy record

The frozen `imported_stl_mask_stream` encountered its bit-exact square-pixel guard because C1's STL export has bbox extents `[30.000000954, 30.0, 30.0] mm`. Uniform N40 scaling therefore retains a maximum `1.2716e-6 mm` residual.

No STL bytes, triangles, topology, or protected implementation were changed. This bounded run records a transparent analysis-grid adapter: it applies the same frozen oriented-triangle intersection and non-zero winding rasterization to the explicit normalized N40 grid `[0,40]×[0,40] mm`, which is also the Route-A/B analysis domain. The residual and rule are retained in the packet. This makes the C1 result reproducible, but **does not approve the adapter as a general imported-STL production route**.

## 4. Interpretation and limits

- **confirmed:** 58-source eligibility audit has no missing/hash mismatch; C1 is a confirmed STEP/STL pair; its retained A–B consistency and bounded A–C selected-slice metrics are exactly equal.
- **likely:** the explicit N40 pixel-grid adapter is the appropriate way to handle sub-pixel export micro-anisotropy in this C1 run. It needs more confirmed-pair evidence before general adoption.
- **unresolved:** B1/L7/F1 cross-family behavior; F1 pixel phase; STL-only 25-model handling; resolution/full-Z801 behavior; descriptor populations and formula parity.
- **rejected:** interpreting same-source A–B evidence as imported-STL validation; generalizing C1 to B3/L1 or the STL-only group; claiming component/Angle/Curvature/full-descriptor, Excel/LEGACY-PY, y, learning, or inverse-design parity.

No new pass threshold was invented: all reported values are continuous measurements.

## 5. Files and independent QA

- [Source eligibility audit](../../../reports/tables/ROUTE-VALID-001-20260729-001_source_eligibility.csv)
- [C1 A/B/C metrics](../../../reports/tables/ROUTE-VALID-001-20260729-001_C1_three_route_selected_slice_metrics.csv)
- [C1 image/hash registry](../../../reports/tables/ROUTE-VALID-001-20260729-001_C1_image_registry.csv)
- [C1 machine packet](ROUTE_VALID_001_C1_PACKET.json)
- [Independent QA](INDEPENDENT_QA.json) — `13/13` PASS, including 58-row eligibility counts, both C1 source hashes, metric replay, scope stop, and all protected baseline file hashes.

## 6. Required review before extension

Review this C1 packet before executing B1/L7/F1. If extended, each confirmed pair must first repeat A–B selected-slice consistency, then A–C. F1 must remain a separate pixel-phase/resolution stress-test. B3/L1 may only be run as clearly labelled sensitivity cases; `L12–L20`, `T1–T16`, and orientation-held `T17` remain outside official STEP↔STL comparison.
