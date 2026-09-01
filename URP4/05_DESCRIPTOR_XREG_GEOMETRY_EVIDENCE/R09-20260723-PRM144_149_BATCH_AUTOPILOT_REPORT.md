# PRM-144~149 batch-autopilot report (FAST no-y lane)

## Official FAST snapshot

`XREG-v2.7-TECHNICAL`: **542 candidates / 31,436 values / 31,434 finite / 411 non-selecting blocks / 175 x-only edges**.

| Cycle | Batch → consolidation | Candidate family | New values | Cross/internal high | Snapshot |
|---|---|---|---:|---:|---|
| 1 | PRM144 → PRM145 | slice raw/kept mean component-piece-area profile shape | 12×58=696 | 0 / 5 | v2.5: 506 candidates, 29,348 values, 382 blocks, 162 edges |
| 2 | PRM146 → PRM147 | phase-balance/purple-share profile shape | 18×58=1,044 | 7 / 1 | v2.6: 524 candidates, 30,392 values, 395 blocks, 170 edges |
| 3 | PRM148 → PRM149 | overlay pair-area inequality/effective-count/top1-share profile shape | 18×58=1,044 | 5 / 0 | v2.7: 542 candidates, 31,436 values, 411 blocks, 175 edges |

All new candidates use frozen SLICE-004 pixel/component tables, are finite on all 58 models, and remain unselected. Independent predecessor/cohort replay passes `3/3`.

This is FAST candidate-bank expansion only, not STRICT Excel/Ntop/LEGACY-PY parity. No y access, x-y analysis, feature selection/promotion, fitting, theta, prediction, inverse-design claim, new image/slicing/mask/mesh work, or protected-source edit occurred.

Evidence: [factory source](LINK_TARGETS_R2/PRM144_149_fast_batch_autopilot.py), [independent QA](LINK_TARGETS_R2/PRM144_149_independent_QA.csv), [final bank](XREG-v2.7/PRM149_xreg_v2_7_candidate_bank.csv).
