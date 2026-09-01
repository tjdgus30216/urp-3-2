# ROUTE-VALID-003 — F1 STEP-reference pixel-phase/resolution stress test

- Run: `ROUTE-VALID-003-20260729-002`
- Settings: `IDX-URP4-1-GEOM-ROUTES / CFG-ROUTEVALID003-F1-COMMON-N40-Z9-P500-750-1000-1500-PHASE4 r1`
- Runtime: KMK312 / Python 3.12.12
- Independent QA: **PASS** (288 comparisons, maximum recomputation error `0.0`)
- Scope: F1 only; selected 9 z slices × P500/P750/P1000/P1500 × four phases. Route C was reused, not regenerated.

## Results

| comparison | exact cases | nonzero-difference cases | minimum IoU | maximum relative area delta | interpretation |
|---|---:|---:|---:|---:|---|
| A–B | 138/144 | 6 | 0.998849 | 0.000601 | same-STEP representation consistency; six z400 cases remain |
| A–C | 129/144 | 15 | 0.998534 | 0.001468 | paired STEP vs separately stored imported STL; attribution remains mixed at z400 |

- Boundary slices (`z=0,1,799,800`) are pixel-exact for A–B and A–C under all tested resolutions/phases.
- A–C has `9` boundary-only cases and `6` interior-labelled cases.
- The interior-labelled A–C cases occur at `z400`; Route A–B also differs there for six cases. Thus current data does **not** isolate an imported-STL slicer defect.
- The direct B-rep curve adapter is not Route B: it samples native STEP section curves and uses the same pixel-centre convention. Its 12 preserved slow-classifier anchors replayed exactly.

## Final status and recommendation

- F1 source identity/common transform: **confirmed**.
- F1 Route A–B cross-representation consistency: **likely**, not complete.
- F1 Route A–C imported-STL route observation: **unresolved** at z400; no production or universal claim.
- Recommendation: **`repeat_preregistered_F1_targeted_cases`**.

The recommended targeted replay is limited to F1 z400 P750/P1000/P1500 P00/P50X: compare the curve adapter with the original slow direct BRepClassifier and sweep the already-declared controlled-tessellation deflection. No full Z801, no other model, no descriptor/Excel/y/model work is authorized by this result.
