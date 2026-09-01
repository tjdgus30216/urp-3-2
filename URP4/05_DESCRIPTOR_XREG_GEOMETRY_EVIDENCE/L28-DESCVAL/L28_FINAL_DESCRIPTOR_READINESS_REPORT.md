# L28 final descriptor readiness report

- Run: `L28-DESCVAL-PKG-20260727-002`
- Source: `SG027-L28TRIAD-P1000-Z801-20260727-002`
- Phase gates: Phase 1 PASS; Phase 2 PASS; Phase 3 PASS; Phase 4 complete.
- Scope: L28 VF30/VF45/VF60 only; no y, fitting, feature selection or canonical promotion.

## Archival audit

- Masks: 2,403/2,403, every PNG SHA and packed-mask hash replayed.
- Slice rows: 2,403; overlay rows: 2,400.
- Quality severity: `{'normal': 1829, 'low': 196, 'moderate': 286, 'high': 92}`. Endpoint blank slices are labeled expected boundary states rather than corruption.

## Descriptor readiness

- L28-stable candidates: `L28-D002, L28-D003`.
- Hold/quality-sensitive candidates: `L28-D001, L28-D004, L28-D005, L28-D006, L28-D007, L28-D008, L28-D009, L28-D010, L28-D011`.
- Curvature `L28-D004` and Angle `L28-D005` remain hold because their historical effective-length populations are unresolved even when their numerical outputs are finite.
- No candidate is promoted to primary or canonical.

## Manual interpretation of statistical flags

- The `92` high-severity rows are **not 92 defective masks**. All 92 are triggered only by `extreme_adjacent_area_change`; there are zero PNG/hash failures, odd scanlines, `<2 px` components or near-full masks.
- Representative review of VF45 slices 0067 and 0100 shows coherent periodic geometry rather than broken raster fill. The flagged indices recur at geometric transitions across the 40 mm height.
- Therefore `all-slice` remains the L28 reference population. `quality-filtered` values are retained only as a deliberately aggressive sensitivity perturbation and must not replace valid geometric transitions.
- Under this interpretation, D007–D011 remain valid, unselected derived candidates. Their sensitivity to deleting real transitions is informative, not evidence that their formulas failed.
- The refined readiness table is `L28-DESCVAL-PKG-20260727-002_descriptor_readiness_refined.csv`.

## Required artifacts for the STP import pipeline

Preserve source hash/config, per-slice mask, mask hash, slice/component table, adjacent-overlay table, quality registry, formula lineage and an immutable run ID.

## Minimum gate before another model

Require complete source/config identity, all slice hashes, per-solid closure, half-open ray parity, complete slice/overlay coverage, anomaly-propagation sensitivity and explicit unresolved-formula labels. This report does not authorize a 58-model expansion.
