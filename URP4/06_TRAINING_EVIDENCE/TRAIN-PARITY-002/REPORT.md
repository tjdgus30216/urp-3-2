# TRAIN-PARITY-002 exact-adapter implementation report — no fit

## Verdict

- Task: `TRAIN-PARITY-002_EXACT_METHOD2_ADAPTER_AND_INSTRUMENTATION_IMPLEMENTATION_NO_FIT`
- Isolated implementation: `TRAIN-2ND-NEWFEATURE-EXACT-ADAPTER-v0.1`
- Status: `partial_branch_coverage`
- `ready_for_parity_execution_gate`: **false**
- Completed estimator fit calls: **0**
- Completed prediction calls: **0**
- Prediction rows: **0**
- Metric rows: **0**

This run implements and validates the dataset/group/fold control plane, source-AST lineage, observability schema, empty ledger writers, target holds, and fail-closed no-fit guards. It does not yet provide independently executable exact numerical adapters for the source notebook's fit-dependent branches.

## Implemented coverage

### Fully implemented and exercised without y-modeling

1. Source and workbook SHA-256 fail-closed verification.
2. `총정리` extraction using the source header rules: rows 2–5, data rows 7–204, X `I:FU`, and 16 selected targets.
3. Ordered row, Excel-row, header, feature, target, dtype, NaN-mask, and raw-value hash ledgers.
4. Source-equivalent same-X grouping: round 8 decimals, `||` serialization, `factorize(sort=False)`.
5. Target-specific outer and inner shared fold manifest with row/group membership and order.
6. Version/hash-bound fold-manifest consumer that refuses absence or drift.
7. 13-primary/3-hold final-refit policy and hold-request blocker.
8. Observation-only event schema covering traversal, ties, exceptions, `None`, fallback, seeds, parameters, rows, and metrics.
9. Prediction and metric ledger schemas with empty `no_fit_no_prediction` artifacts.
10. Static fit/predict inventory and dynamic estimator guards.

### Source lineage frozen but not numerically executable

- 56 source functions/classes were parsed directly from the protected notebook and individually hashed.
- All 16 pipeline stages have a source-cell/symbol mapping.
- Ten source method branches have versioned branch specifications:
  `baseline_stability`, `stability_lasso_ridge`, `spca_ridge`, `spca_huber`, `block_pca_ridge`, `bagged_subspace_ridge`, `minimal_class_average`, `multitask_screen_ridge`, `multitask_screen_pls`, and `spca_pls`.
- Numerical branch adapter implementations: **0/10**. They were deliberately not approximated with `FS4-P1-B` or another proxy.

Therefore the correct state is `partial_branch_coverage`, not `implementation_complete_no_fit` and not `ready_for_parity_execution_gate`.

## Extractor QA

- Source SHA: PASS.
- Workbook SHA: PASS.
- Dataset shape: **198 rows × 169 X × 16 targets**.
- Target policy: **13 primary / 3 hold**.
- Same-X contract: PASS.
- `DATASET_EXTRACTOR_QA.csv`: **7/7 PASS**.

Generated identity artifacts:

- `artifacts/ROW_IDENTITY_LEDGER.csv`
- `artifacts/COLUMN_IDENTITY_LEDGER.csv`
- `artifacts/TARGET_SAMPLE_LEDGER.csv`
- `artifacts/DATASET_MANIFEST.json`

## Group/fold manifest QA

- Manifest rows: **338,028**.
- Targets: 16.
- Outer repeats per target: 12.
- Inner splits per target/outer repeat: 24.
- Outer group leakage: 0.
- Inner group leakage: 0.
- Manifest SHA-256: `3b18913ef68b6487b273a113ab3b3c0569d3246444f17003f68c0e01af1e89a6`.
- `GROUP_AND_FOLD_MANIFEST_QA.csv`: **6/6 PASS**.

The inner manifest is group-membership based on each target's outer-train population. Exact row choice after repeated-y processing remains a downstream fit-stage concern and must be checked when numerical branch adapters are implemented.

## Fail-closed QA

All **13/13** negative tests passed:

- wrong source SHA;
- wrong workbook identity;
- wrong sheet;
- header-order drift;
- row-count drift;
- target-column mismatch;
- missing fold manifest;
- fold-manifest hash drift;
- target-policy drift;
- held-target P8 request;
- `PYTHONHASHSEED` drift;
- attempted estimator `.fit()`;
- attempted estimator `.predict()`.

The two estimator attempts were guard tests. They were intercepted before estimator logic; completed fit/predict counts remained zero.

## Determinism and observability

The implementation ran with canonical project-local KMK312 / Python 3.12.12, `PYTHONHASHSEED=42`, OMP/MKL/OpenBLAS/NumExpr thread counts 1, and GPU disabled. The event schema explicitly includes unordered traversal order/hash, tie count/rule, silent exception, `None` gate, fallback, seed, parameter hash, and final-refit state.

The source audit retained the known `build_corr_blocks` unordered-set path. No ordering repair was applied to the professor notebook. A later exact numerical adapter must reproduce and log the frozen behavior rather than silently canonicalize it.

## Independent QA and protected assets

- Independent QA: **16/16 PASS**.
- Protected assets: **13/13 unchanged**.
- Tolerance binding: `TRAIN-PARITY-TOL-v0.1` PASS.
- Implementation source hash replay: PASS.

Protected scope includes the Training source/workbook, current FS4 representative adapter and execution files, `NB-ORIG`/`NB-CURRENT` copies used by this project, and the principal `LEGACY-PY` files. None were modified.

## Largest blocker

The largest blocker is the absence of independently executable, source-exact numerical adapters for all ten target-dependent method branches. The current package can freeze inputs/folds, bind source functions, observe events, and block unauthorized execution, but it cannot yet produce a fair source-versus-adapter prediction ledger.

## Next gate

Recommended next task:

`TRAIN-PARITY-002A_EXACT_NUMERICAL_BRANCH_PORT_AND_STATIC_QA_NO_FIT`

It should port the ten branches and source selection objectives into isolated versioned callables, bind them to the shared fold consumer and event recorder, and statically prove no call occurs. Only after independent QA may a separate GO/NO-GO gate consider a controlled fit.

## Claim boundary

This result proves control-plane implementation, deterministic manifest generation, fail-closed behavior, and no-fit compliance. It does not prove source↔adapter numerical parity, model validity, method superiority, feature selection, held-target resolution, grouped generalization, or inverse design.
