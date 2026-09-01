# TRAINING First Unfinished Gate

## Decision

The first unfinished gate is:

`T1_ORIGINAL_REPLAY`

## Why this is first

T0 is complete for all nine sources. The project has source hashes, notebook
JSON/cell inspection, line-by-line documents, workbook/target/feature
crosswalks, and method registries.

T2 cannot be judged before at least one corresponding source notebook is
replayed under a frozen environment, input, split, and seed. Existing adapter
results are source-mapped compatibility experiments, not source parity.

## Gate split

### Blocked by missing input

- `TRAIN-1ST-LEGACY`
- `TRAIN-2ND-LEGACY`
- `TRAIN-3RD-LEGACY`

Reason: the exact literal input `Total data_260308.xlsx` is not present.

### Ready for controlled replay preparation

- `TRAIN-1ST-NEWFEATURE`
- `TRAIN-2ND-NEWFEATURE`
- `TRAIN-3RD-NEWFEATURE`
- `TRAIN-4TH-ENSEMBLE`
- `TRAIN-5TH-ALLTOGETHER`
- `TRAIN-5TH-FIXED`

Exact input available:

`EXCEL_TRAINING_TOTAL_260503`  
SHA-256:
`4a6ec7d03d92fa25851998689768d9db9f63227f00e778a528d758b368851dce`

## Recommended first source

`TRAIN-2ND-NEWFEATURE`

Reasons:

1. Its exact input is available.
2. Its stored notebook outputs do not contain an error.
3. It is smaller than methods 3–5.
4. A corresponding `FS4-P1-B` adapter path exists.
5. One successful replay gives a direct next step for the first adapter-parity
   comparison.

`TRAIN-1ST-NEWFEATURE` is not first because its stored output already contains
`Unknown model: WeightedBlend_2`; that is a useful debugging target after the
replay harness is proven.

## Completion criteria for the first replay

- raw source bytes and SHA remain unchanged;
- exact input workbook hash is frozen;
- project-local KMK312 runtime identity is recorded;
- path-only adaptations are isolated and diffed;
- random seeds and split/group identities are recorded;
- every executed cell and exception is logged;
- produced files have a manifest and SHA-256;
- stored notebook results and replay results are compared without claiming
  parity until values match under the same contract;
- no feature, model, or ensemble is promoted.

## Resource gate

Do not execute the replay while `STRICT-STEP-026` C1 PID `14108` is running.
Preparation may be read-only, but the fit/replay starts only after C1 completion
and its planned independent QA.

