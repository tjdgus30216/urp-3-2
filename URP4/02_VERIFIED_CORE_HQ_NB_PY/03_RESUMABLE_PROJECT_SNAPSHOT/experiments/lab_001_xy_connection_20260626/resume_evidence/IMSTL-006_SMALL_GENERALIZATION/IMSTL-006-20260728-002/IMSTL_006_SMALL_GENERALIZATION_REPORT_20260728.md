# IMSTL-006 selected-slice gate and small-family full extraction report

- Run: `IMSTL-006-20260728-002`
- Settings: `IDX-URP4-1-GEOM-IMPORTED-STL / CFG-IMSTL006-SELECTED-GATE-THEN-P1000-Z801 r1`
- Runtime: KMK312
- Scope: B3, C1, L1, F1, T1, T8, T9 only
- Forbidden actions preserved: all58, performance y, model training, feature promotion, NB-CURRENT/LEGACY-PY edits

## Outcome

The selected-slice gate passed B3, C1, L1, T1, T8 and T9. Only those six models proceeded to the full `1000 × 1000 px`, `801 slices`, `0.05 mm` extraction. F1 failed the frozen resolution gate at slices 200 and 600 and did not proceed.

| Model | Family | Selected gate | Minimum interior P500→P1000 IoU | Maximum area difference | Full extraction |
|---|---:|---:|---:|---:|---:|
| B3 | B | pass | 0.965707 | 0.006839 | completed |
| C1 | C | pass | 0.968484 | 0.031516 | completed |
| L1 | L | pass | 0.957816 | 0.021139 | completed |
| F1 | F | fail | 0.949045 | 0.010035 | not run |
| T1 | T | pass | 0.969949 | 0.004808 | completed |
| T8 | T | pass | 0.976080 | 0.010701 | completed |
| T9 | T | pass | 0.975574 | 0.010333 | completed |

## F1 interpretation

F1 fails only the preregistered IoU threshold (`0.95`) at the symmetric slices 200 and 600. Both give IoU `0.9490451919`, but their relative occupied-area difference is only `0.0006017532` (`0.0602%`). Manual inspection shows coherent repeated geometry without an obvious broken contour, random speckle or missing region. The present result is therefore a **contractual fail but a likely boundary-pixel/resolution sensitivity**, not confirmed slice corruption. F1 remains unresolved and must not be silently admitted to full extraction.

## Full extraction result

- Completed full models: 6 (`B3`, `C1`, `L1`, `T1`, `T8`, `T9`)
- Full trace rows: `801` per model, unique indices `0…800`
- Valid adjacent slice pairs: `800` per model
- Finite average fields: `15/15` for every model
- Finite stdev fields: `15/15` for every model
- Catastrophic numeric flags: `0`
- Exact descriptor duplicates: `0`
- T8/T9: not exact duplicates across the 15 average fields; standardized distance `0.458408`, still the closest pair in this small panel
- Retained images: the nine selected diagnostic masks per completed model; non-selected full masks were transient

The route therefore demonstrates **operational generalization to the sampled B/C/L/T sources**, not universal imported-STL generalization and not exact physical/STP parity. The F family has not passed this gate.

## Independent QA

Independent replay recalculated all `7 × 9 = 63` selected slices at both resolutions.

- Source hashes: exact for 63/63
- P1000 packed-mask hashes: exact for 63/63
- P500 packed-mask hashes: exact for 63/63
- Maximum IoU replay error: `1.11e-16`
- Maximum area-difference replay error: `9.58e-17`
- Passed-only full execution and failed-source exclusion: pass
- Full trace/hash/finite checks: pass
- NB-CURRENT and NB-DEV protected hashes: unchanged
- y columns/access: absent
- all58: not executed
- Independent QA status: `passed`

## Decision

- **confirmed:** selected-first gating and passed-only full execution work as designed.
- **confirmed:** sampled B/C/L/T models complete P1000/Z801 descriptors without catastrophic numerical failure.
- **confirmed:** F1 failed the frozen selected-slice resolution gate and was excluded from full execution.
- **likely:** the F1 miss is dominated by boundary raster sensitivity rather than gross contour corruption.
- **unresolved:** whether F1 can pass a preregistered multi-resolution/pixel-phase diagnostic without changing the physical formula.
- **unresolved:** physical/exact-STP parity outside the paired L28 evidence.
- **rejected:** claiming all-family or all58 readiness from this run.

## Next controlled task

`IMSTL-007_F1_SELECTED_SLICE_RESOLUTION_AND_PIXEL_PHASE_DIAGNOSIS_NO_Y`: reuse F1 and fixed slices, compare preregistered P500/P750/P1000/P1500 and controlled half-pixel phase variants, preserve every diagnostic image, and decide whether the 0.949 IoU is a benign discretization effect or route instability. Do not run F1 full extraction, all58, y, training or NB-CURRENT modification before this decision.

## Evidence

- `SELECTED_GATE_PACKET.json`
- `DECISION_PACKET.json`
- `PRODUCER_QA.json`
- `INDEPENDENT_QA.json`
- `reports/tables/IMSTL-006-20260728-002_selected_slice_gate_detail.csv`
- `reports/tables/IMSTL-006-20260728-002_selected_slice_gate_summary.csv`
- `reports/tables/IMSTL-006-20260728-002_descriptor_matrix.csv`
- `reports/tables/IMSTL-006-20260728-002_descriptor_coverage.csv`
- `reports/tables/IMSTL-006-20260728-002_slice_trace_summary.csv`
- `reports/tables/IMSTL-006-20260728-002_xonly_collision_audit.csv`
- `reports/tables/IMSTL-006-20260728-002_independent_selected_replay.csv`
- `reports/tables/IMSTL-006-20260728-002_independent_trace_audit.csv`
- `reports/tables/IMSTL-006-20260728-002_selected_slice_visual_review_registry.csv`
