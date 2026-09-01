# TRAIN-PARITY-001 preregistration report

## Verdict

- Task: `TRAIN-PARITY-001_TRAIN_2ND_NEWFEATURE_ADAPTER_PARITY_PREREGISTRATION_NO_FIT`
- Source alias: `TRAIN-2ND-NEWFEATURE`
- Overall readiness: `blocked_by_adapter_gap`
- Target scope: outer-CV parity schema `16/16`; final-refit primary `13/16`; `3/16 final_refit_hold`
- Fit, prediction, feature selection, benchmark, diagnostic execution: **0**

The source/input contract and comparison tolerances are sufficiently frozen to design a controlled parity run. The current versioned adapter is not an end-to-end implementation of the source notebook, so actual parity fitting is not authorized.

## Evidence identity

| Item | Identity |
|---|---|
| Source notebook | `Training_260419-2nd method - New feature - Good. vibration.ipynb` |
| Source SHA-256 | `11129a41bd4303d82c599148cd761adb3c858f58da017586e07fb0f06d055ff2` |
| Input workbook | `Total data_260503.xlsx` / `총정리` |
| Input SHA-256 | `4a6ec7d03d92fa25851998689768d9db9f63227f00e778a528d758b368851dce` |
| Primary execution reference | `TRAIN-REPLAY-001-20260731-001` |
| Adjudication | `POSTRUN-GATE-001-20260801-001` |
| Runtime | project-local `KMK312`, Python 3.12.12, environment hash `d9a2d20180a68a0d73b64323495af64a04ecf83cd3fbb6bbe02bac922011a10d` |

The source and workbook hashes were replayed during this gate and match the preregistered identities.

## Source-to-adapter finding

`FS4-P1-B` is a **representative proxy with an intentionally altered leakage-safe wrapper**, not an exact implementation of the full `TRAIN-2ND-NEWFEATURE` notebook.

What it retains:

- stability selection using bootstrap group subsets;
- `LassoCV` screening;
- a final `Ridge` regressor;
- declared `n_boot=60`, `subsample=0.80`, probability threshold `0.35`, and `top_keep=6`;
- fail-closed execution permit and group metadata requirement.

What it does not implement end to end:

- workbook extraction, normalized multi-row headers, 169-feature construction, or target-specific NaN filtering;
- same-X `X_KEY`/`GROUP_ID` construction;
- the source's 12 repeated target-specific `GroupShuffleSplit` outer folds and 24-split inner searches;
- groupwise rough prefilter, weighted ranking, correlation pruning, engineered features, and repeated-y selection;
- the complete source candidate set (`baseline_stability`, `stability_lasso_ridge`, SPCA, BlockPCA, bagged, minimal-class, multitask, and mechanical-energy PLS branches);
- per-target method/model/transform selection and source score objective;
- row-level prediction ledger, exact source metric ledger, or 13-target final-refit path.

The existing PRM-071 run is valid evidence that four representative adapters executed on a different 54-row/220-feature/leave-one-family-out contract. It is not source-notebook parity evidence.

## Frozen source contract

- Sheet `총정리`; headers rows 2–5; data rows 7–204.
- X `I:FU`; Y `FV:HL`; selected Y columns `FW,FX,FZ,GA,GC,GG,GJ,GZ,HA,HB,HC,HD,HE,HG,HI,HK`.
- 198 raw rows; 169 numeric X columns; 16 targets.
- Target-specific usable samples 25–193 and same-X groups 25–128.
- `pandas.to_numeric(errors='coerce')`; all-missing columns removed while order is retained; rows missing the current target are removed.
- `X_KEY`: X rounded to 8 decimals, converted to strings, joined by `||`; `GROUP_ID`: `pd.factorize(..., sort=False)`.
- Outer split: 12 one-fold `GroupShuffleSplit` runs, test size 0.22, seed `42 + repeat_id`.
- Inner search: grouped split count 24, test size 0.20; random state inherited from the fold path.
- Metrics: R², RMSE, MAE. Final method objective: mean outer R² − `0.12 × std(R²)` + `0.10 × support_share` − `0.01 × topk`.

The complete machine-readable contract is in `FROZEN_SOURCE_EXECUTION_CONTRACT.json`.

## Fail-closed parity ladder

| Gate | Requirement | Current state |
|---|---|---|
| P0 | source/input/config/environment identity | preregistered |
| P1 | dataset/header/value/NaN/sample parity | contract ready; adapter path absent |
| P2 | X_KEY/GROUP_ID/membership parity | contract ready; adapter path absent |
| P3 | exact shared train/test rows and groups | schema ready; injection absent |
| P4 | candidate/rank/engineered/selected-feature parity | source contract frozen; exact adapter absent |
| P5 | method/estimator/transform/hyperparameter parity | representative proxy only |
| P6 | row/group prediction ledger parity | ledger path absent |
| P7 | R²/RMSE/MAE parity | tolerances frozen; blocked by P1–P6 |
| P8 | final-refit parity | 13 primary; 3 hold |

Each gate requires all earlier gates to pass. A later numerical resemblance cannot waive an earlier identity failure.

## Deterministic reference hierarchy

1. **Accepted clean replay** is the primary execution reference for this parity program.
2. **Future deterministic parity** must use `PYTHONHASHSEED=42`, canonical KMK312, single-thread numerical libraries, explicit seeds, a prebuilt shared fold manifest, traversal traces, and logs for swallowed exceptions/`None` returns.
3. **Historical stored notebook output** is sensitivity evidence only. It is not deterministic ground truth.

Fixing `PYTHONHASHSEED` applies only to isolated execution copies and the future exact adapter. It does not modify the professor's source notebook.

## Target policy

- All 16 targets may enter P0–P7 outer-CV parity after an exact adapter exists.
- 13 targets are eligible for primary P8 final-refit parity.
- `FRF 300–8000 Hz AVG`, `FRF 6500–8000 Hz AVG`, and `Yield strength` remain `final_refit_hold` until `TRAIN-REFIT-DIAG-001` is completed.
- Yield-strength method identity is additionally `unresolved`: historical stored output used `block_pca_ridge`, while the accepted replay selected `minimal_class_average`.

## Tolerance policy

The tolerance registry is frozen as revision `TRAIN-PARITY-TOL-v0.1`. Strings, order, membership, NaN masks, feature sets/ranks, methods, and hyperparameters require exact equality. Source-derived dataset values require exact equality. Predictions use `atol=1e-10`, `rtol=1e-8`; aggregate metrics use `atol=1e-10`, `rtol=1e-8`. Any change after results exist requires a new immutable revision and cannot retroactively relabel a failed run.

## Largest blocker and next gate

The largest blocker is the absence of an exact source-equivalent adapter that can consume the same extracted dataset and prebuilt fold manifest while exporting per-row predictions and exception/`None` diagnostics. The existing `FS4-P1-B` must remain a representative compatibility recipe.

Recommended next gate:

`TRAIN-PARITY-002_EXACT_METHOD2_ADAPTER_AND_INSTRUMENTATION_IMPLEMENTATION_NO_FIT`

That gate may implement and statically test the missing extraction, fold-injection, source-method, prediction-ledger, and observability interfaces. It must still perform no fit. A separate execute-or-stop gate is required afterward.

## Claim boundary

This packet establishes a preregistered comparison contract and a blocking gap. It does not establish adapter parity, model validity, method superiority, grouped generalization, feature importance, or inverse design.
