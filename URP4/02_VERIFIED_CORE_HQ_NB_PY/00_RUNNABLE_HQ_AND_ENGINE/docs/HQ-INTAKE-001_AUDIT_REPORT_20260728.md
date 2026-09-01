# HQ-INTAKE-001 — actual-file and side-chat conflict audit

## Outcome

The side-chat design was usable as a UX/controller draft, but not as current scientific authority. Current disk artifacts and official decisions supersede three old directions: silent STL→STEP fallback, NB-DEV v0.3/v0.4 currency, and immediate y-based Training.

The audit found no blocker to a safe HQ v0.1. It did find that the existing `urp4/orchestration/v0_1` is intentionally a contract-validation engine and must not be reused as production orchestration. The final deliverable therefore reuses qualified generator/import/descriptor/training-registry modules and adds only `urp4/hq/v0_1` as a new controller/engine boundary.

## Reusable status

- **confirmed**: contracts, RUN-139 descriptor service, source router, generated native route, source identities and reporting primitives.
- **partial/conditional**: imported STL screening route, Lattice Type A, TPMS, Voxel and Training registry.
- **missing/disabled**: Type B identity workbook, direct STP-to-descriptor adapter and official y/modeling gate.
- **superseded**: NB-DEV v0.3/v0.4 as latest.
- **rejected**: silent STL→STEP fallback, old orchestration as production HQ, automatic feature selection/training.

## Explicit conflict resolutions

1. Original STP is strict/reference when available. Imported STL does not silently become STEP; it uses the IMSTL winding route.
2. NB-DEV v0.5/`geometry_io.v0_4` is the latest imported implementation.
3. Feature selection and Training appear as a schema/interface only and fail closed without a later authorization.
4. “Modularized” means code exists; it does not imply every production policy is confirmed. Conditional modules keep their scientific labels.

## Evidence

- Detailed intake table: `reports/tables/URP4-1_HQ_INTAKE_AUDIT_20260728.csv`
- Conflict table: `reports/tables/URP4-1_HQ_SIDECHAT_CONFLICT_RESOLUTION_20260728.csv`
- Module audit: `reports/tables/URP4-1_HQ_MODULE_AUDIT_20260728.csv`
- Integration manifest: `reports/tables/URP4-1_HQ_INTEGRATION_MANIFEST_20260728.csv`

