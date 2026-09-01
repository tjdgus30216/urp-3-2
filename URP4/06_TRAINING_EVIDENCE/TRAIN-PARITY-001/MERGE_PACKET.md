# TRAIN-PARITY-001 preregistration evidence packet

- Packet status: `ready_for_evidence_merge`
- Functional/code merge requested: **no**
- Fit/prediction/feature selection/benchmark performed: **no**
- Source notebook/workbook/adapters/HQ/NB/LEGACY-PY modified: **no**
- Overall execution readiness: `blocked_by_adapter_gap`

## Accepted evidence

1. Source and workbook identities match the frozen SHA-256 values.
2. Accepted clean replay is the primary execution reference; historical stored output remains sensitivity only.
3. `FS4-P1-B` is a representative stability-Lasso-Ridge proxy with an intentionally leakage-safe wrapper, not the full source notebook.
4. P0–P8 are frozen as fail-closed sequential gates.
5. `TRAIN-PARITY-TOL-v0.1` is preregistered before any parity result.
6. Outer-CV schema covers 16 targets; final-refit primary scope is 13; 3 remain hold.

## Required artifacts

- `REPORT.md`
- `SOURCE_ADAPTER_LINEAGE_MATRIX.csv`
- `FROZEN_SOURCE_EXECUTION_CONTRACT.json`
- `DATASET_AND_GROUP_PARITY_CONTRACT.csv`
- `FOLD_MANIFEST_SCHEMA.csv`
- `FEATURE_METHOD_MODEL_PARITY_CONTRACT.csv`
- `PREDICTION_METRIC_TOLERANCE_REGISTRY.csv`
- `TARGET_ELIGIBILITY_AND_HOLD_POLICY.csv`
- `DETERMINISM_AND_RANDOMNESS_REGISTER.csv`
- `ADAPTER_GAP_AND_READINESS_MATRIX.csv`
- `CONTROLLED_PARITY_EXECUTION_PREREQUISITES.md`
- `MERGE_PACKET.md`

## Hold boundary

- `FRF 300–8000 Hz AVG`: final-refit hold; confirmed expected source behavior.
- `FRF 6500–8000 Hz AVG`: final-refit hold; confirmed expected source behavior.
- `Yield strength`: final-refit and method-identity hold; likely source bug/nondeterminism, exact cause unresolved.

## Next allowed task

`TRAIN-PARITY-002_EXACT_METHOD2_ADAPTER_AND_INSTRUMENTATION_IMPLEMENTATION_NO_FIT`

It may create isolated versioned implementation and static QA artifacts only. It may not fit, predict, benchmark, diagnose held targets, or modify protected sources.
