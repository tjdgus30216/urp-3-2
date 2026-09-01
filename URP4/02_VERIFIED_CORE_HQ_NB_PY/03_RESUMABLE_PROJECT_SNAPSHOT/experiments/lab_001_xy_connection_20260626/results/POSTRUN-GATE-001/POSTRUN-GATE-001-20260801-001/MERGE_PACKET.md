# POSTRUN-GATE-001 MERGE_PACKET

## Packet type

Post-run evidence adjudication packet. This is not a code/function/model merge request.

## Accepted decisions

- C1 independent QA: `passed`, 9/9, executed exactly once after completion.
- C1 stderr: 283-byte CUDA-path warning; the prior “empty stderr” wording is rejected.
- TRAIN QA-018: lifecycle-aware v2 `passed`; original failure rejected.
- TRAIN QA-015: remains failed because final refit is 13/16.
- T1: `T1_COMPLETED_WITH_EVIDENCE_AND_DECLARED_REFIT_GAP`.
- Adapter-parity preregistration: allowed; adapter fit remains prohibited.

## QA-015 target dispositions

- FRF 300–8000 Hz AVG: confirmed `expected_source_behavior`, final-refit hold.
- FRF 6500–8000 Hz AVG: confirmed `expected_source_behavior`, final-refit hold.
- Yield strength: likely `source_code_bug`, final-refit hold.

## Files in packet

- `REPORT.md`
- `C1_INDEPENDENT_QA_RESULT.json`
- `TRAIN_REPLAY_QA_FAILURE_DISPOSITION.csv`
- `TRAIN_REPLAY_LIFECYCLE_AWARE_QA_V2.json`
- `CLAIM_AND_STATUS_LEDGER.csv`
- `NEXT_GATE_RECOMMENDATION.md`
- `MERGE_PACKET.md`

## Integrity anchors

- C1 QA SHA-256: `88efe036266847bfb29a74f967318ec8634a1ce07b0ebf9bb9ed1cfcd57d2c96`
- C1 RUN_STATE SHA-256: `631ad313e9e38140f3d3a9d9f6daa5b6c033243ee873cae58f407972ac17f7aa`
- C1 stderr SHA-256: `77ae62a89a5ae86363148d50dc43a6ba697c948d0431ec52fbb930e10de085af`
- Training source SHA-256: `11129a41bd4303d82c599148cd761adb3c858f58da017586e07fb0f06d055ff2`
- Training executed notebook SHA-256: `a0fdcbba251fbc220b72256dc60c6905f38f9ddf02d411975c0f22cc6dba3fb2`
- Original Training QA remains preserved with SHA-256 `47ac16494dc5dc77774774e4dade5c22c399c6223c8f762ef0a43b850e206be9`.

## Non-modification

Existing Training REPORT/QA/MERGE_PACKET were not overwritten. C1 was not rerun. Original notebooks, Excel, NB-CURRENT, NB-ORIG, LEGACY-PY and HQ were not modified.

## Next gate

`TRAIN-PARITY-001_TRAIN_2ND_NEWFEATURE_ADAPTER_PARITY_PREREGISTRATION_NO_FIT`

The separate three-target diagnostic must be preregistered before any new diagnostic fit.
