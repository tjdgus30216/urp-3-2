# TRAIN-PARITY-002A evidence merge packet

- Evidence status: `ready_for_evidence_merge`
- Overall state: `ready_for_controlled_execution_preregistration`
- Exact branch ports: `10/10`
- Partial/blocked: `0/10`
- Static/fixture QA: `110/110 PASS`
- Independent QA: `18/18 PASS`
- Protected assets: `16/16 unchanged`
- Completed fit/predict: `0/0`
- Prediction/metric rows: `0/0`
- Actual fit authorization: **no**

## Mergeable scope

- `implementation/` source-exact AST runtime and common branch interface;
- branch/source lineage and objective matrices;
- nondeterminism/fallback instrumentation contracts;
- static/fixture QA;
- no-fit proof;
- protected-asset and independent QA evidence.

## Non-mergeable scientific claims

- source↔adapter numerical equality;
- successful prediction or metric parity;
- best branch/model/feature;
- held-target resolution;
- Training integration into HQ/FS4/NB;
- model generalization or inverse design.

## Preserved boundaries

- `FS4-P1-B` and PRM-071 unchanged and not used as branch substitutes.
- Professor notebook/workbook unchanged.
- `NB-CURRENT`, `NB-ORIG`, `LEGACY-PY`, HQ unchanged.
- `TRAIN-PARITY-TOL-v0.1` unchanged.
- 13 primary / 3 final-refit hold unchanged.

## Next allowed gate

`TRAIN-PARITY-003_CONTROLLED_EXECUTION_PREREGISTRATION_AND_GO_NO_GO_NO_FIT`

That gate may prepare an explicit, bounded GO/NO-GO contract only. This packet does not authorize `.fit()` or `.predict()`.
