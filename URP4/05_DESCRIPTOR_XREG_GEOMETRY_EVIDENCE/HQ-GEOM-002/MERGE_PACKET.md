---
work_id: HQ-GEOM-002_VERSIONED_DEVELOPMENT_ROUTE_INTEGRATION_AND_CONTRACT_TESTS_NO_Y
run_id: HQ-GEOM-002-20260728-001
status: ready_for_versioned_development_merge
runtime: KMK312 Python 3.12.12
---

# HQ-GEOM-002 merge packet

## Proposed merge scope

- Add `URP4-1_DELIVERABLE/urp4/hq/v0_3/` as a new development-only generated-N40 route.
- Add its isolated producer and independent-QA scripts.
- Preserve produced Voxel evidence and this report.

## Verified result

- Native Voxel N40 run passes P1000/Z801: `801` slices, `800` overlays, `9` scalars, PNG mismatch/remaining `0/0`.
- Contract fixtures pass `6/6`, including fail-closed rejection of the non-clean Lattice source.
- HQ-GEOM-001 Voxel derivative/table/result parity passes `6/6`.
- Protected assets pass `31/31`; no y, x-y, selection, training, prediction, inverse design, or all58 action occurred.

## Excluded scope

- No HQ v0.1 or Blueprint v0.2 alteration.
- No NB-CURRENT, NB-ORIG, LEGACY-PY, original Excel, or source STL alteration.
- No Lattice/TPMS admission: both remain `topology_clean=false` and fail closed under this Voxel-qualified contract.
- No scientific claim of generated-family physical standardization or LEGACY-PY/Excel parity.

## Recommendation

`CONDITIONAL YES`: merge the isolated HQ v0.3 development route as a traceable Voxel-only proof pattern. Keep Lattice/TPMS behind a separately preregistered topology-exception contract.
