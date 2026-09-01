# L28 statistical-flag interpretation addendum

Run: `L28-DESCVAL-PKG-20260727-002`  
Source: `SG027-L28TRIAD-P1000-Z801-20260727-002`

## Decision

The archival source and descriptor package pass. No defective stored slice was demonstrated.

The automatic registry contains `92` high robust-z flags (`VF30=0`, `VF45=38`, `VF60=54`, excluding the six expected endpoint blanks). Every high flag is caused solely by a large *relative-to-local-MAD* adjacent-area change. The following defect indicators are all zero:

- PNG/hash mismatch
- packed-mask identity mismatch
- connected-component count replay mismatch
- odd scanline
- component smaller than 2 px
- near-full mask

Representative images at VF45 slice 0067 and 0100 show coherent lattice cross-sections. The flagged indices occur in repeated geometric transition bands; removing them deletes actual L28 geometry. Consequently:

1. `all-slice` is the reference aggregation.
2. `quality-filtered` is a stress test only.
3. sensitivity to that filter does not by itself reject a descriptor.
4. robust median/IQR/MAD remain alternative summaries, not replacements.

## Readiness

- `likely`: D002 Thickness sqrt-total-area and D003 MassOri ratio are stable and traceable for L28.
- `confirmed_formula / unselected`: D007–D011 are reproducible derived candidates from preserved component/layer/overlay populations.
- `hold`: D001 and D006 retain historical population/contour-parity uncertainty.
- `unresolved`: D004 Curvature and D005 Angle retain effective-length lineage uncertainty.

No candidate is promoted to primary/canonical and no inference beyond L28 is made.
