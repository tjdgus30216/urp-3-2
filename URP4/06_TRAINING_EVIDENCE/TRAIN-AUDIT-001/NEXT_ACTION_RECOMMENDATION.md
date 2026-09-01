# Next Action Recommendation

## One next task

`TRAIN-REPLAY-001_TRAIN-2ND-NEWFEATURE_ISOLATED_ORIGINAL_REPLAY`

## Execution order

1. While C1 is running, create only the isolated replay contract:
   source/input hashes, environment manifest, path redirection plan, expected
   output tree, seed/split capture, abort rules, and resource budget.
2. Wait for `STRICT-STEP-026` C1 to finish.
3. Run the already planned C1 independent QA once.
4. Only then execute the isolated `TRAIN-2ND-NEWFEATURE` replay.
5. Compare replay artifacts to the source notebook's stored outputs.
6. Stop before adapter parity; T2 becomes the following task only if replay
   artifacts are complete.

## Why not start with all nine

- three exact legacy inputs are missing;
- one new-feature notebook contains a stored error;
- methods 3–5 are substantially more complex;
- broad replay would mix environment, source, method, and data failures.

## Why this advances the project

It closes the first evidence gap rather than rebuilding policy. It also creates
the minimum artifact set needed to ask the next scientific question:

```text
same input + same folds + same seeds
source notebook result
versus
FS4-P1-B adapter result
```

No feature selection, method winner, ensemble, or inverse-design claim is part
of this next task.

