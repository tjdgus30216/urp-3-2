# TRAIN-AUDIT-001 — Existing Nine Notebook Completion and First Gap

Date: 2026-07-31 KST  
Mode: read-only evidence audit  
Status: completed_with_evidence  
Parallel authority: `experiments/lab_001_xy_connection_20260626/results/CURRENT_PARALLEL_QUEUE_20260731.md`

## 1. Outcome

The nine professor/TA Training notebooks are all present and their current
workspace bytes match the registered SHA-256 values. Static source analysis,
line-by-line reading documents, method/feature/split policies, and a guarded
module layer exist.

That does **not** mean that the nine notebooks have been replayed or that the
adapters reproduce them.

| Question | Result |
|---|---|
| Nine-source audit | `9/9 completed_with_evidence` |
| Project-controlled original notebook replay | `0/9` |
| Source-notebook ↔ adapter result parity | `0/9` |
| One common 1–5 benchmark | `partial` |
| Grouped/held-family generalization | `partial` |
| HQ execution integration | `partial readiness/lock only; actual fit absent` |
| First unfinished gate | `T1_ORIGINAL_REPLAY` |

## 2. Six states that must not be collapsed

1. **Code exists** — confirmed for all nine raw notebooks and the versioned
   `urp4/training` modules.
2. **Code ran** — historical outputs are stored inside the source notebooks,
   and project pilots ran separate source-mapped/reduced methods. This is not a
   project-controlled replay of the nine notebooks.
3. **Original parity exists** — not established.
4. **Common benchmark finished** — partial only.
5. **Generalization validated** — partial only.
6. **HQ integrated** — status/readiness and fail-closed locks exist; Training
   model fitting is not called by HQ.

## 3. T0–T5 gate audit

### T0_SOURCE_AUDIT — completed_with_evidence

- Raw notebooks: `9/9` present.
- Source hashes: `9/9` match the CINT-08 source registry.
- Notebook JSON and cell source were directly parsed in this audit.
- Static inventory:
  - code/markdown cell structure recorded for every notebook;
  - input workbook literals, old/new Excel layouts, target columns, method
    families, split APIs, metrics, and stored execution/output state inspected;
  - nine line-by-line documents exist and are linked to the same source hashes.
- `Total data_260503.xlsx` exists at SHA-256
  `4a6ec7d03d92fa25851998689768d9db9f63227f00e778a528d758b368851dce`.
- Exact `Total data_260308.xlsx`, required by the three LEGACY layouts, was not
  found in the audited project roots.

Important source observation:

- All nine notebooks contain historical execution counts and stored outputs.
- `TRAIN-1ST-NEWFEATURE` contains a stored
  `ValueError: Unknown model: WeightedBlend_2`.
- Stored notebook output is historical evidence only. It does not identify a
  reproducible local environment, full output directory, or project replay.

### T1_ORIGINAL_REPLAY — first unfinished gate

- Completed replays: `0/9`.
- `TRAIN-1ST/2ND/3RD-LEGACY`: `blocked_by_data` because their literal input is
  `Total data_260308.xlsx`, which is absent.
- The six `Total data_260503.xlsx` sources: `not_started`.
- No matching `Result_enhanced_featureaware_*`,
  `Result_sequential_stage_outputwise_*`, `FinalModelBackup`,
  `FinalSelectedDatasets`, or model-backup artifact tree exists in the project.
- CINT-08 explicitly records `source_notebook_cells=false`,
  `models_fitted=0`, and `predictions_created=0`.

### T2_ADAPTER_PARITY — not_started

The following implementation pieces exist:

- static method/source registry;
- feature routing and grouped-evaluation policy;
- no-fit adapters for method families 1–4;
- guarded estimator/execution modules for four representative recipes.

However:

- method 1 uses a reduced compatibility subset;
- method 3 uses a bounded grid;
- method 4 intentionally changes the selection boundary to avoid leakage;
- method 5 is a coordinator/reference, not a fifth executable adapter;
- no same-input, same-fold, same-seed notebook-versus-adapter prediction or
  metric comparison exists.

Therefore adapter code existence is confirmed, but adapter parity is `0/9`.

### T3_COMMON_CONTRACT_BENCHMARK — partial

Strong existing evidence:

- PRM-071 used one frozen GM dataset, one target policy, five
  leave-one-family-out folds, and the same metrics for four representative
  method families.
- Dataset: 54 rows.
- Methods: 4.
- OOF predictions: 216.
- Independent QA: 24/24.
- All four methods were worse than the pooled null on MAE and RMSE; no winner
  or feature was promoted.

Why it is not complete:

- the compared methods were representative/compatibility adapters, not exact
  replays of all nine sources;
- method 5 remained a coordinator/reference;
- method D was a `common_only_degraded_probe` because its official lattice
  specialist input was absent;
- only GM was used.

The 2026-07-31 AI Lattice pilot is additional technical evidence, not closure:
149 rows, 16 targets, four methods, 9,536 OOF predictions, 36/36 QA, but
Method-01 used a Ridge surrogate after BayesianRidge failed in the canonical
environment and the result is strongly source-block confounded.

### T4_GROUPED_GENERALIZATION — partial

Completed evidence:

- GM leave-one-family-out evaluation over B/C/F/L/T exists.
- R09-TRAIN-004/005/007 contain held-family OOF ledgers.
- The AI Lattice pilot uses three source-workbook blocks as outer holdouts.

Open limitations:

- no exact nine-notebook replay under the grouped contract;
- no complete output-wise 1–5 comparison;
- F has only two rows in the GM experiment;
- replicate/direction policy is specified but not demonstrated across the new
  doctor compression population;
- B/C/L and Voronoi summary workbooks are still pending;
- AI Lattice source blocks may encode generation order, test batch, or both.

### T5_HQ_INTEGRATION — partial

Confirmed:

- HQ writes Training-required input/readiness metadata.
- HQ controller rejects enabled feature selection or Training.
- HQ blueprint lists Feature Selection and Training stages as `LOCKED`.
- Versioned Training registries, policies, adapters, and guarded estimators are
  shipped under `URP4-1_DELIVERABLE/urp4/training/`.

Not established:

- HQ does not call an authorized Training fit;
- no HQ TrainingRunManifest with an executed fit/prediction exists;
- no selected model or ensemble is integrated.

This is status/readiness integration with fail-closed behavior, not functional
Training integration.

## 4. Existing execution evidence

| Evidence | Actual inspected value | Interpretation |
|---|---:|---|
| CINT-08 | 31/31 local tests; 114/114 cross-CINT; 0 fit; 0 prediction | static contract only |
| PRM-071 | 54 rows; 4 methods; 5 family folds; 216 OOF; QA 24/24 | partial common benchmark |
| TRAIN-004 | 165 OOF rows | interpretable grouped GM baseline |
| TRAIN-005 | 165 OOF rows | AQ sensitivity; no promotion |
| TRAIN-007 | 165 OOF rows | nested one-feature sensitivity; no promotion |
| COMP-FACTORY-001 | 149 eligible joins; QA 22/22 | new-data intake/crosswalk |
| COMP-FACTORY-002 | 9,536 OOF; QA 36/36 | source-block technical pilot |

## 5. Doctor compression data status

- `Structural_Factors_All.xlsx` and three reference strut workbooks are
  preserved read-only with SHA-256 provenance.
- AI Lattice:
  - 150 x rows;
  - 149 eligible x-y joins;
  - AI092 remains x-only because a valid y row is absent;
  - source-block pilot completed, but no feature/method promotion.
- B/C/L summary: pending intake.
- Voronoi summary: pending intake.

These new-data results do not count as original notebook replay or adapter
parity.

## 6. First gap and next action

The first unfinished stage is `T1_ORIGINAL_REPLAY`.

Recommended next work:

`TRAIN-REPLAY-001_TRAIN-2ND-NEWFEATURE_ISOLATED_ORIGINAL_REPLAY`

Rationale:

- its exact input workbook is available;
- historical notebook outputs contain no stored error;
- it is smaller than method 3–5;
- a corresponding method-2 adapter exists, so successful replay creates the
  shortest path to the first T2 parity test.

Do not launch it while C1 is consuming the canonical runtime. First create the
isolated replay contract; execute only after C1 completion and its one planned
independent QA.

## 7. Protection and parallel status

- No Training notebook, Excel source, HQ, DELIVERABLE module, NB-CURRENT,
  NB-ORIG, or LEGACY-PY file was modified.
- No Training notebook was executed.
- No fit, feature selection, benchmark sweep, winner selection, or ensemble
  construction was performed.
- C1 PID `14108` remained running throughout the audit.

