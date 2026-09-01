---
work_id: IMSTL-008_F1_FULL_P1000_Z801_AND_FAMILY_NONREGRESSION_NO_Y
accepted_run: IMSTL-008-20260728-002
status: merged
indices: RUN-342 / DEC-355 / CHG-340 / LAB-CHG-309 / R09-BB-1308
runtime: KMK312 / Python 3.12.12
---

# IMSTL-008 merge packet

## Merge recommendation

**YES, within the bounded F1 technical-execution scope.**

## Accepted evidence

- F1 full P1000/Z801: 801 slices, 800 overlays, 39,506 slice components and 38,187 overlay components
- Saved-PNG readback mismatch `0`; 1,601 PNG created/deleted; remaining PNG `0`
- RUN-139 scalar output `9/9`; independent replay maximum error `7.11e-15`
- F1 IMSTL-007 selected masks `9/9 exact`
- accepted B/C/L/T family masks `54/54 exact`
- protected assets `31/31`; upstream IMSTL-006/007 trees unchanged

## Quarantine

`IMSTL-008-20260728-001` is an infrastructure-only Windows path-length failure. It must not be merged or interpreted scientifically. Run `002` changes only the output-root length.

## Merge boundary

The merge confirms F1 full imported-STL technical execution and sampled-family non-regression. It does not approve exact STP parity, the whole F family, all58, canonical descriptors, y utility, Feature Selection, Training, prediction or inverse design.

## Protected boundary

HQ v0.1, Blueprint v0.2, NB-CURRENT, NB-ORIG, LEGACY-PY, original Excel, clean submission and accepted IMSTL-006/007 evidence were not modified.

## Next work

`HQ-GEOM-001_GENERATED_FAMILY_40MM_NORMALIZATION_IMPLEMENTATION_AND_REGRESSION_NO_Y`
