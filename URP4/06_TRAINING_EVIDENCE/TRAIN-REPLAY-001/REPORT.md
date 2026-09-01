# TRAIN-REPLAY-001 report

## Verdict

- Replay status: `QUARANTINED`
- Raw runner status: `REPLAY_PASSED`
- Code cells: **11/11 passed**
- Independent QA: **16/18 FAIL**
- Source alias: `TRAIN-2ND-NEWFEATURE`
- Source SHA-256: `11129a41bd4303d82c599148cd761adb3c858f58da017586e07fb0f06d055ff2`
- Input SHA-256: `4a6ec7d03d92fa25851998689768d9db9f63227f00e778a528d758b368851dce`

## What was actually replayed

- Source notebook was not modified.
- A clean canonical KMK312 kernel executed the isolated copy from the first code cell.
- Input sheet: `총정리`
- Raw data rows: `198`
- Numeric input features: `169`
- Targets: **16**
- Target-specific usable samples: **25–193**
- Target-specific same-X groups: **25–128**

## Training contract

- Target columns: `FW, FX, FZ, GA, GC, GG, GJ, GZ, HA, HB, HC, HD, HE, HG, HI, HK`
- Feature range: `I:FU`, rows `7:204`
- Missing values: numeric coercion; target-specific missing rows removed; estimator pipelines use the original imputation behavior.
- Split: `GroupShuffleSplit` by same-X `GROUP_ID`
- Seed: `42`
- Outer contract: 12 repeats, test fraction 0.22
- Inner contract: 24 grouped splits, test fraction 0.20
- Search threads: 1
- Final selected estimators: MinimalClassAverage (4), Kernel_Ridge_RBF (2), Huber_Regressor (1), PCR_Ridge (3), Ridge (5), PLS (1)
- Predictions: the source notebook computes predictions internally but does **not** export a row-level prediction ledger.
- Exported metrics: grouped outer-CV R²/RMSE/MAE and full-data refit metrics.

## Metric inventory

| target | samples | groups | method | estimator | CV R² mean | CV RMSE mean | CV MAE mean |
|---|---:|---:|---|---|---:|---:|---:|
| Vibrational response / FRF (g/N) / 300-8000 Hz / AVG | 193 | 128 | minimal_class_average | MinimalClassAverage | 0.700745 | 0.0747509 | 0.0521395 |
| Vibrational response / FRF (g/N) / 300-3000 Hz / AVG | 193 | 128 | minimal_class_average | MinimalClassAverage | 0.868676 | 0.0260672 | 0.0143544 |
| Vibrational response / FRF (g/N) / 3000-6500 Hz / AVG | 193 | 128 | baseline_stability | Kernel_Ridge_RBF | 0.825633 | 0.0792329 | 0.0496334 |
| Vibrational response / FRF (g/N) / 6500-8000 Hz / AVG | 193 | 128 | minimal_class_average | MinimalClassAverage | 0.832209 | 0.241525 | 0.146783 |
| Thermal characteristics / Thermal conductivity / W/m.K | 65 | 65 | baseline_stability | Huber_Regressor | 0.365293 | 0.820784 | 0.68383 |
| Thermal characteristics / Heating rate / °C/s | 65 | 65 | baseline_stability | Kernel_Ridge_RBF | 0.163314 | 0.00226502 | 0.00185503 |
| Thermal characteristics / Cooling rate / °C/s | 65 | 65 | baseline_stability | PCR_Ridge | 0.304135 | 0.25277 | 0.191009 |
| Thermal characteristics / Heating Temp / °C/s | 65 | 65 | block_pca_ridge | Ridge | 0.381518 | 10.5224 | 7.68672 |
| Modulus | 56 | 56 | block_pca_ridge | Ridge | 0.361381 | 3487.83 | 2675.47 |
| Com. Strength | 56 | 56 | baseline_stability | Ridge | 0.0725922 | 82.5399 | 53.5294 |
| APS | 56 | 56 | spca_pls | PLS | 0.264069 | 65.0518 | 48.7961 |
| AS | 56 | 56 | baseline_stability | PCR_Ridge | 0.216032 | 86.895 | 70.2173 |
| Yield strength | 56 | 56 | minimal_class_average | MinimalClassAverage | 0.386917 | 42.4081 | 34.49 |
| Densif. strength | 56 | 56 | baseline_stability | Ridge | 0.106473 | 225.635 | 181.663 |
| Total energy | 56 | 56 | block_pca_ridge | Ridge | 0.531076 | 39.061 | 31.383 |
| Thermal characteristics / h / W/m.K | 25 | 25 | baseline_stability | PCR_Ridge | 0.667936 | 0.781057 | 0.553855 |

These values reproduce the notebook execution only. They do not establish adapter parity, fair cross-method benchmarking, held-family generalization, model superiority, or inverse-design validity.

## Declared compatibility delta

1. `IMPORT_PATH` redirected to the hash-matched project-local workbook.
2. `EXPORT_ROOT_DIR` redirected to this isolated run.
3. A short Windows junction was used solely to avoid MAX_PATH; files physically reside under `generated_outputs/`.
4. The stale `python3` kernelspec was replaced in the execution copy with canonical `kmk312-urp4-1`.
5. OMP/MKL/OpenBLAS/NumExpr were capped at one thread and the GPU was hidden.
6. No target, feature, preprocessing, split, seed, estimator, hyperparameter, feature-selection rule, or metric was changed.

Attempt 1 stopped before model comparison because the long physical output path exceeded Windows MAX_PATH. It is preserved under `a1/`. Attempt 2 used the declared junction and is the replay evaluated here.

## Hidden-state and warning assessment

- Clean-kernel success means no hidden notebook-state dependency was required for this source/input/environment combination.
- Notebook error outputs: none in the accepted attempt.
- Runtime warnings are preserved in `warnings_and_errors.md`.

## C1 non-interference record

- Before replay: PID running = `True`, slices = `272`, overlays = `271`, stderr bytes = `0`
- After replay: PID running = `False`, slices = `0`, overlays = `0`, stderr bytes = `283`
- The replay did not change C1 priority, affinity, command, files, or process state.

## Evidence boundary and next gate

This completes **T1_ORIGINAL_REPLAY for 1/9 notebooks only**. It does not complete:

- `T2_ADAPTER_PARITY`
- `T3_COMMON_CONTRACT_BENCHMARK`
- `T4_GROUPED_GENERALIZATION`
- `T5_HQ_INTEGRATION`

Next gate: `TRAIN-PARITY-001_TRAIN_2ND_NEWFEATURE_ADAPTER_PARITY_PREREGISTRATION_NO_FIT`. This should preregister exact source-copy versus adapter equality conditions before any parity fit is run.

## Files

- Executed notebook: `TRAIN-2ND-NEWFEATURE_EXECUTED_ISOLATED.ipynb`
- Runtime: `runtime_environment.json`
- Input manifest: `actual_input_manifest.csv`
- Cell status: `cell_execution_status.csv`
- Contract: `extracted_training_contract.json`
- Metrics: `prediction_and_metric_inventory.csv`
- Generated outputs: `generated_output_manifest.csv` (209 files)
- Warnings: `warnings_and_errors.md`
- Independent QA: `independent_qa.json`, `independent_qa_checks.csv`
