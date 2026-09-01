# Controlled parity execution prerequisites

## Current decision

Actual parity fitting is **not authorized**. The contract is frozen, but the executable comparison pair does not yet exist.

## Required implementation gate — no fit

Run `TRAIN-PARITY-002_EXACT_METHOD2_ADAPTER_AND_INSTRUMENTATION_IMPLEMENTATION_NO_FIT` first. It must create versioned isolated code and leave the professor notebook, workbook, HQ, `NB-CURRENT`, `NB-ORIG`, and `LEGACY-PY` unchanged.

### 1. Hash-bound dataset extractor

- Require the frozen source and workbook hashes.
- Read only `총정리`, header rows 2–5, rows 7–204, X `I:FU`, and the 16 selected target columns.
- Export ordered source-row, header, value, dtype, and NaN-mask ledgers.
- Reproduce `X_KEY` and `GROUP_ID` exactly.
- Fail closed on any identity, shape, order, header, or value drift.

### 2. Shared fold-manifest interface

- Materialize target-specific outer and nested inner membership using the frozen source rules.
- Hash and version the manifest before either execution path starts.
- Make both the isolated source copy and exact adapter consume that same manifest.
- Refuse random fallback if the manifest is absent or mismatched.

### 3. Exact source-stage adapter

Implement the full ordered stage graph, not merely `FS4-P1-B`:

1. rough groupwise prefilter and 0.85 correlation prune;
2. repeated-y selection;
3. 24-repeat feature-frequency and final ranking;
4. source engineered-feature rules;
5. complete target-dependent method roster;
6. estimator/transform/hyperparameter spaces;
7. source inner and outer selection objectives;
8. 13-target final-refit path, with three holds carried as holds.

The new component must have a new identity such as `TRAIN-2ND-NEWFEATURE-EXACT-ADAPTER-v0.1`. It must not overwrite or relabel the representative `FS4-P1-B` recipe.

### 4. Observation-only source instrumentation

- Launch source copy and adapter with `PYTHONHASHSEED=42`, all documented seeds, one-thread numerical libraries, GPU disabled, and canonical KMK312.
- Record unordered traversal order, selected feature/method ties, swallowed exception details, and every `None` return gate.
- Instrumentation may expose state but must not repair, reorder, skip, or add scientific candidates in the parity run.

### 5. Prediction and metric ledgers

- Record one row per target, outer repeat, source row, `GROUP_ID`, true y, and prediction.
- Recompute R²/RMSE/MAE independently from that ledger.
- Preserve model/method/transform/hyperparameter and selected-feature identities alongside predictions.

### 6. Static and negative QA before a GO decision

- Validate all 12 artifacts in this preregistration packet.
- Test missing/wrong source hash, wrong workbook, header drift, row drift, group leakage, fold drift, target payload mismatch, and missing hold flags.
- Prove no `fit()` or `predict()` was called in the implementation gate.
- Recheck protected assets.

## Subsequent execute-or-stop gate

Only after the no-fit implementation and independent QA pass may a separate gate decide whether to run controlled parity. That gate must bind:

- exact code/config/environment/fold-manifest hashes;
- `TRAIN-PARITY-TOL-v0.1` unchanged;
- 16 outer-CV targets and 13 primary final-refit targets;
- the three explicit holds;
- resource limits and abort conditions.

No earlier compatibility benchmark or historical stored output can substitute for these prerequisites.
