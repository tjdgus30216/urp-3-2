# TRAIN-REPLAY-001 audit MERGE_PACKET

## Packet status

- Packet type: **read-only replay evidence packet**
- Replay verdict: `QUARANTINED`
- Independent QA: `FAIL` (16/18)
- Ready for evidence-index merge: `no`
- Request to merge Training functionality into HQ: **no**

## Scope accepted

- One original source replay only: `TRAIN-2ND-NEWFEATURE`
- T1 evidence may be updated from `not_started` to `completed_with_evidence` for this alias after control-tower review.
- Compatibility deltas are I/O/runtime routing only and are fully declared.

## Scope explicitly not accepted

- Adapter parity
- Common-contract model comparison
- Grouped/held-family generalization
- Feature or model promotion
- Ensemble construction
- HQ fit enablement
- Any y-performance or inverse-design claim

## Integrity

- Source SHA-256: `11129a41bd4303d82c599148cd761adb3c858f58da017586e07fb0f06d055ff2`
- Input SHA-256: `4a6ec7d03d92fa25851998689768d9db9f63227f00e778a528d758b368851dce`
- Environment hash: `d9a2d20180a68a0d73b64323495af64a04ecf83cd3fbb6bbe02bac922011a10d`
- Config hash: `7d50ea4f4a22e6c489881cd337a5392083ef3d2a73de3e35d5e3c2d9b174a4a4`
- Generated output count: `209`
- Source notebook and input workbook remained unchanged.
- NB-CURRENT, NB-ORIG, LEGACY-PY, HQ, DELIVERABLE and official Excel were not modified.

## Attempt history

- Attempt 1: preserved `BLOCKED_WITH_EVIDENCE` due Windows MAX_PATH before model comparison.
- Attempt 2: accepted replay using a declared short-path junction to the same physical isolated output directory.

## C1

- C1 was not stopped, reprioritized, restarted, affinity-changed, or modified.
- Progress was nondecreasing and its stderr remained empty across the replay window.

## Recommended next action

`TRAIN-PARITY-001_TRAIN_2ND_NEWFEATURE_ADAPTER_PARITY_PREREGISTRATION_NO_FIT`
