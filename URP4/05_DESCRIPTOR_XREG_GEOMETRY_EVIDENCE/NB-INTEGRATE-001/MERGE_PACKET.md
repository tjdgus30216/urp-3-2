# NB-INTEGRATE-001 merge packet

## Recommendation

**CONDITIONAL YES — additive versioned development integration only.**

## Merge scope

- Add `urp4.route_policy.v0_1` controller package.
- Add `NB_DEV_v0_6_ROUTE_VALID_004_IMPORT_POLICY.ipynb`.
- Add controller smoke/fixture/independent QA scripts and hash-addressed manifests.
- Synchronize logs only after QA.

## Not merged / not changed

- NB-CURRENT, NB-ORIG, LEGACY-PY, original STEP/STL, original Excel.
- No slicer execution, descriptor extraction, y, feature selection, Training or production release.

## Evidence

- ROUTE-VALID-004 policy QA is accepted.
- F1 preflight records the expected raw source SHA and `F1_Z400_UNRESOLVED`.
- Controller tests `9/9`, independent QA `13/13`, notebook static QA `8/8`, protected audit `31/31` pass.

## Remaining lock

`STRICT-F1-001_EXACT_A_LONG_RUN_AND_DECLARED_DEFLECTION_SENSITIVITY_NO_Y` is still required for later scientific F1 qualification, not for this development integration.
