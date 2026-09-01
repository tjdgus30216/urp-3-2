# ROUTE-VALID-002 — B1/L7 confirmed-pair cross-family selected-slice validation

- Work / run: `ROUTE-VALID-002_B1_L7_CONFIRMED_PAIR_CROSS_FAMILY_SELECTED_SLICE_VALIDATION_NO_Y` / `ROUTE-VALID-002-20260729-001`
- Settings: `IDX-URP4-1-GEOM-ROUTES / CFG-ROUTEVALID002-B1L7-N40-ZMID-P500P1000-PHASE00 r1`
- Runtime: `KMK312` Python 3.12.12 + OCP/OpenCascade
- Scope: B1 and L7 only; transient N40, z-mid, PHASE-00, P500/P1000. C1 was not rerun. No F1, B3/L1, T17, STL-only model, full Z801, descriptor, Excel/LEGACY-PY, y, feature-selection, Training, notebook, or source mutation work occurred.

## 1. Precalculation contract replay

ROUTE-VALID-001 was first rechecked as officially merged: required result files exist, independent QA is `13/13 PASS`, and all eight required project logs carry the `RUN-357` / `ROUTE-VALID-001` record. B1 and L7 each then passed a fresh source-contract replay.

| Model | Family | Registry state | STEP SHA | separately stored STL SHA | Contract |
|---|---|---|---|---|---|
| B1 | B | `paired_confirmed` | `db57…6387` | `a3de…b08a` | passed |
| L7 | L | `paired_confirmed` | `bcb4…567a` | `0524…d8a7` | passed |

Every registered source file was present and its SHA-256 matched before any slice was calculated.

## 2. Route meanings remain fixed

| Route | Input | Interpretation |
|---|---|---|
| A | original STEP direct B-rep | STEP reference selected-slice raster |
| B | controlled tessellation from that **same** STEP | same-source representation-consistency only |
| C | separately stored paired imported STL via oriented non-zero winding | confirmed-pair imported-STL geometry-preservation observation |

Route A–B is **not** imported-STL validation. Route A–C is the only imported-STL comparison in this run.

## 3. Continuous comparison results

All eight route comparisons are exact at their respective resolution.

| Model | P | A–B IoU / sym diff / area Δ | A–C IoU / sym diff / area Δ |
|---|---:|---|---|
| B1 | 500 | `1.0 / 0 px / 0` | `1.0 / 0 px / 0` |
| B1 | 1000 | `1.0 / 0 px / 0` | `1.0 / 0 px / 0` |
| L7 | 500 | `1.0 / 0 px / 0` | `1.0 / 0 px / 0` |
| L7 | 1000 | `1.0 / 0 px / 0` | `1.0 / 0 px / 0` |

Diagnostic component/hole counts also agree route-for-route at each resolution: B1 `36 / 0`; L7 `100 / 0`.

### Resolution observation, intentionally separated

L7’s selected-slice area is `276.48 mm²` at P500 and `296.00 mm²` at P1000. This is a **resolution response of the same model**, not a Route A–B or A–C mismatch: all three routes agree exactly within each resolution. No threshold or route winner was introduced from this observation.

## 4. Imported-STL grid handling

| Model | Adapter | N40 bbox residual | Reason |
|---|---|---:|---|
| B1 | explicit N40 grid adapter used | `2.5431e-6 mm` | retained export bbox has non-bit-exact XY pitch after uniform normalization |
| L7 | not used | `0 mm` | retained export bbox is an exact 40 mm square analysis domain |

The B1 adapter is transparent and run-local. It modifies neither STL bytes nor triangle/topology data; it uses the frozen `ORIENTED_NONZERO_RAW/IMSTL-004/r1` section and winding primitives on the explicit `[0,40]×[0,40] mm` N40 pixel grid. It is not promoted to a global default policy.

## 5. Scientific status

- **confirmed:** B1 and L7 source contracts are confirmed/hash-matched pairs. At z-mid PHASE-00, P500/P1000, their A–B and A–C masks, areas, components, and holes match exactly. Independent QA is `14/14 PASS`.
- **likely:** C1+B1+L7 provide cross-family selected-slice support that the imported-STL route can preserve the corresponding confirmed STEP geometry under these settings.
- **unresolved:** additional slice positions, phase behavior, full Z801 profiles, F1 stress behavior, component-population/descriptor formulas, and all 25 STL-only models.
- **rejected:** calling A–B independent STL validation; using a C1/B1/L7 selected slice as full descriptor/Excel/LEGACY-PY/y proof; auto-promoting the adapter; generalizing to B3/L1/T17/STL-only assets.

## 6. Required next decision

**Recommendation: `proceed_to_ROUTE_VALID_003_F1_stress_test`.**

Reason: the confirmed B/C/L pilot now has exact A–C results at two resolutions; the next designated uncertainty is F1’s pixel-phase/resolution stress behavior. This is not authorization for full Z801 or NB integration. `NB-INTEGRATE-001` remains prohibited until the F1 result is reviewed.

## 7. Evidence

- [B1/L7 source contract](../../../reports/tables/ROUTE-VALID-002-20260729-001_B1_L7_source_contract.csv)
- [Route A/B/C measurements](../../../reports/tables/ROUTE-VALID-002-20260729-001_route_ABC_measurements.csv)
- [Comparison metrics](../../../reports/tables/ROUTE-VALID-002-20260729-001_B1_L7_comparisons.csv)
- [Image/hash registry](../../../reports/tables/ROUTE-VALID-002-20260729-001_image_hash_registry.csv)
- [Machine packet](ROUTE_VALID_002_PACKET.json)
- [Independent QA](INDEPENDENT_QA.json)
