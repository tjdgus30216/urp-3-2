# TRAIN-PARITY-003 preregistration merge packet

- Decision: `NO_GO_WITH_BLOCKER`
- Evidence packet status: `ready_for_no_go_evidence_merge`
- Active stop: `STOP-005`
- Sentinel: not frozen; `TRAIN2NF::HI` is provisional only
- Planned repeat: `0`, not authorized
- Fit/predict: `0/0`
- Prediction/metric rows: `0/0`
- P8: prohibited
- Permit: not issued

## Mergeable evidence

- verified source/workbook/adapter/dataset/fold/tolerance hashes;
- 16-target candidate table and explicit target crosswalk failure;
- reference/adapter binding contract;
- P0–P8 parity ledger schema;
- no-fit resource estimate and fail-closed conditions;
- non-executable permit record.

## Non-mergeable claims

- GO for TRAIN-PARITY-004;
- numerical parity;
- reference runner readiness;
- model, method or feature quality;
- final-refit parity or held-target resolution.

## Required next action

Run `TRAIN-PARITY-003A_TARGET_IDENTITY_AND_HOLD_POLICY_CROSSWALK_REPAIR_NO_FIT`, then repeat the 003 adjudication. Do not edit protected predecessors in place.
