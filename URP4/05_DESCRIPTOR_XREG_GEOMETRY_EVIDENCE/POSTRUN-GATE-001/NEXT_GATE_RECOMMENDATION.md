# POSTRUN-GATE-001 next gate recommendation

## Decision

Adapter-parity **preregistration may begin**. Adapter-parity fitting may not begin in this gate.

Recommended next gate:

`TRAIN-PARITY-001_TRAIN_2ND_NEWFEATURE_ADAPTER_PARITY_PREREGISTRATION_NO_FIT`

## Required preregistration boundaries

1. Freeze the original source/input SHA, KMK312 environment, row/column ranges, target list, same-X grouping rule, split seeds and metrics.
2. Define exact equality/tolerance checks separately for dataset extraction, fold membership, selected method, prediction and metric.
3. Do not treat historical stored notebook output as deterministic ground truth until source nondeterminism is controlled.
4. Carry the following three targets as `final_refit_hold`:
   - FRF 300–8000 Hz AVG
   - FRF 6500–8000 Hz AVG
   - Yield strength
5. Outer-CV parity may be preregistered for all 16 targets, but final-model parity may be declared only for the 13 targets with replay refits.

## Separate diagnostic plan — do not execute now

Before any new fit intended to resolve the three-target gap, preregister:

`TRAIN-REFIT-DIAG-001_MINIMAL_CLASS_AVERAGE_THREE_TARGET_RETURN_PATH_NO_BROAD_SWEEP`

The diagnostic must:

- use only the three held targets;
- fix and record `PYTHONHASHSEED`;
- replace unordered block traversal with an observation-only deterministic trace in an isolated copy, without modifying the source notebook;
- log which `minimal_class_average` return gate fires:
  `best_choice_none`, `search_empty`, `filtered_candidates_empty`, `valid_member_count_lt_2`, or `nonfinite_r2`;
- log suppressed member-fit exceptions instead of changing model behavior;
- compare the historical method choice, replay method choice and diagnostic choice;
- perform no hyperparameter expansion, model promotion, ensemble redesign or HQ integration.

No diagnostic fit was executed by POSTRUN-GATE-001.
