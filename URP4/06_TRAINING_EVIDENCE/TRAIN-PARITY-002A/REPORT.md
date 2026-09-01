# TRAIN-PARITY-002A source-exact numerical branch port — no fit

## Verdict

- Adapter: `TRAIN-2ND-NEWFEATURE-EXACT-ADAPTER-v0.1`
- Port version: `TRAIN-PARITY-002A-BRANCH-PORT-v0.1`
- Overall state: `ready_for_controlled_execution_preregistration`
- Exact ports: **10/10**
- Partial/blocked branches: **0/10**
- Static/fixture QA: **110/110 PASS**
- Independent QA: **18/18 PASS**
- Completed fit/predict calls: **0/0**
- Prediction/metric rows: **0/0**
- Protected assets: **16/16 unchanged**

This state allows the next controlled-execution preregistration to be designed. It does not authorize a fit.

## Port strategy and source fidelity

The ten branches were not rewritten from an interpretation and were not replaced with `FS4-P1-B` or PRM-071 proxies. The adapter:

1. verifies the protected notebook SHA-256;
2. reads the notebook JSON directly;
3. extracts the original import, literal configuration, function, and class AST nodes;
4. compiles the original definitions into an isolated namespace without executing workflow cells;
5. identifies each branch inside the original `evaluate_method_train_test` body and records its AST/text hash;
6. places the common dataset/fold/target/permit interface before the source callable;
7. keeps the permit at `NO_FIT`, so numerical entry is unreachable in this gate.

The runtime contains 56 source functions/classes. All ten branch conditions were found in the protected source. Seven branch-AST hashes are unique because SPCA and multitask variants intentionally share source `if` blocks.

## Branch results

| Branch | Status |
|---|---|
| `baseline_stability` | `exact_port_complete_no_fit` |
| `stability_lasso_ridge` | `exact_port_complete_no_fit` |
| `spca_ridge` | `exact_port_complete_no_fit` |
| `spca_huber` | `exact_port_complete_no_fit` |
| `block_pca_ridge` | `exact_port_complete_no_fit` |
| `bagged_subspace_ridge` | `exact_port_complete_no_fit` |
| `minimal_class_average` | `exact_port_complete_no_fit` |
| `multitask_screen_ridge` | `exact_port_complete_no_fit` |
| `multitask_screen_pls` | `exact_port_complete_no_fit` |
| `spca_pls` | `exact_port_complete_no_fit` |

No missing dependency, hidden-state blocker, or proxy substitution was recorded. The multitask global state is explicit through the isolated runtime's `bind_dynamic_state()` interface; it was not populated or executed during this gate.

## Common interface

Every branch consumes the same `BranchRequest` plus `ExecutionPermit` contract:

- dataset manifest identity/hash;
- target identity;
- shared fold path/hash;
- row/group identity hash;
- branch identity;
- deterministic runtime hash;
- target policy hash;
- config hash;
- prediction/metric writer handles;
- final-refit request/state;
- execution permit.

The output contract fixes ordered selected features, transform and estimator identities/parameters, selection trace, fallback/`None`/exception events, writer handles, and final-refit state. In this gate the writer handles are schema-only and reject appends.

## Source objective and fallback preservation

Branch callables point to the original `evaluate_method_train_test` implementation and original helper functions, including:

- groupwise prefilter and ranking;
- repeated-y handling;
- SPCA and BlockPCA transformations;
- stability screening and bagging;
- multitask screening;
- target transform/model searches;
- branch-specific candidate objectives;
- source tie/order behavior;
- `None`, exception, and fallback paths.

Source bugs or nondeterministic behavior were not repaired. The known `build_corr_blocks` set traversal remains source behavior and is exposed through traversal-order/hash instrumentation.

## Nondeterminism instrumentation

The adapter can observe:

- unordered container input/result order and hashes;
- score ties and source tie-break results;
- `PYTHONHASHSEED` and stage seeds;
- Python exception events before a source handler suppresses them;
- `None` returns with function/line information;
- branch fallback/rejection;
- ordered feature identities and hashes;
- parameters and final-refit state.

This is observation-only. It does not sort, repair, retry, or substitute source behavior.

## Static and fixture QA

Each branch passed 11 checks:

1. import/callable;
2. exact source signature;
3. branch AST lineage;
4. dependency symbols;
5. source method-roster reachability;
6. parameter/objective binding;
7. output contract;
8. `NO_FIT` permit denial;
9. fold-hash drift denial;
10. malformed input denial;
11. held-target final-refit denial.

Total: **10 × 11 = 110/110 PASS**.

The fixture used only synthetic identities and schema-only ledger handles. It did not load the 198×169 research matrix or invoke a source numerical branch.

## No-fit and policy proof

- Branch calls stopped at the permit gate before source numerical entry.
- Guard-test fit attempts: 1, blocked before estimator logic.
- Guard-test predict attempts: 1, blocked before estimator logic.
- Completed fit calls: 0.
- Completed predict calls: 0.
- Prediction rows: 0.
- Metric rows: 0.
- Fitted model artifacts: 0.
- Benchmark artifacts: 0.
- `TRAIN-PARITY-TOL-v0.1`: unchanged.
- Target policy: 13 primary / 3 final-refit hold unchanged.
- Shared fold manifest hash: `3b18913ef68b6487b273a113ab3b3c0569d3246444f17003f68c0e01af1e89a6`.

## Independent QA

Independent process result: **18/18 PASS**.

It recompiled the protected source, verified ten branch identities and hashes, checked no proxy substitution, replayed implementation hashes, verified fold/tolerance/target bindings, confirmed zero execution rows/calls, and confirmed protected assets remained unchanged.

## Maximum remaining blocker

The largest remaining blocker is the absence of a separately preregistered and authorized controlled-execution contract. No branch has yet consumed real target data or produced a source-versus-adapter prediction ledger, so numerical parity remains untested.

## Next gate

Recommended next task:

`TRAIN-PARITY-003_CONTROLLED_EXECUTION_PREREGISTRATION_AND_GO_NO_GO_NO_FIT`

It should choose a bounded first target/branch scope, freeze code/config/fold/environment hashes, define abort conditions and fit budget, retain the three holds, and decide GO/NO-GO. It must itself remain no-fit. Only a later explicitly authorized execution run may call the source-exact branches.

## Claim boundary

This task establishes source-exact callable availability and static/fixture safety. It does not establish numerical parity, model quality, feature importance, historical-output identity, held-target resolution, grouped generalization, or inverse design.
