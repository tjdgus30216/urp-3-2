# POSTRUN-GATE-001 report

## Final decisions

- C1 independent QA: **PASS — 9/9**
- QA-015: **remains failed for final-refit completeness**
- QA-018: **passed under lifecycle-aware QA-v2; original failure rejected**
- T1 status: `T1_COMPLETED_WITH_EVIDENCE_AND_DECLARED_REFIT_GAP`
- Adapter-parity preregistration: **allowed, no fit**

## 1. C1 independent QA

The QA script had no prior result file and was executed exactly once at `2026-08-01 11:13:16 KST` with canonical project-local KMK312. It did not rerun slicing or LEGACY-PY.

All nine checks passed:

1. run ID
2. completed slice/overlay counts
3. source STEP SHA-256
4. 801-row slice manifest and contiguous indices
5. 800-row overlay manifest and contiguous indices
6. 40 direct scalar rows
7. nine retained anchor PNGs
8. expected bulk-PNG eviction
9. all scalar values finite

C1's 283-byte stderr is preserved and classified as a **CuPy CUDA-path warning**, not an empty log and not a scientific execution failure.

## 2. TRAIN-REPLAY-001 facts

- Source/input SHA matched.
- Clean KMK312 kernel executed 11/11 code cells without notebook error output.
- All 16 targets produced outer-CV results.
- Final refit table contains 13/16 targets.
- No adapter parity, new fit, benchmark sweep or model promotion was performed here.

## 3. QA-015 adjudication

### FRF 300–8000 Hz AVG and FRF 6500–8000 Hz AVG

Classification: `expected_source_behavior` — **confirmed**.

Both are absent from the source notebook's stored historical Cell E1 final-refit output and absent from the clean replay final-refit output, while outer-CV metrics exist. The source's `minimal_class_average` branch contains several silent `None` exits and catches member-fit exceptions without recording them; Cell E1 then silently `continue`s. Thus the repeated omission is faithful source behavior, but it is still an incomplete final-refit artifact.

### Yield strength

Classification: `source_code_bug` — **likely**.

Historical output selected and refit `block_pca_ridge`. The clean replay selected `minimal_class_average` and then omitted the refit. Scientific cells were unchanged and the clean kernel passed, rejecting compatibility-delta and hidden-state explanations. The source uses `next(iter(set(...)))` in `build_corr_blocks` while `PYTHONHASHSEED` is not fixed, creating an uncontrolled ordering path that can alter method competition. The exact silent return gate cannot be recovered from existing artifacts because source diagnostics were suppressed.

### Aggregate QA-015 disposition

QA-015 is **not passed or waived**. The replay is a faithful execution record, while final-refit output completeness is separately false. A no-fit diagnostic plan is recorded; no new fitting occurred.

## 4. QA-018 lifecycle-aware adjudication

The original check read an exited PID and intentionally deleted temporary PNGs as zero progress. Terminal evidence instead shows:

- `RUN_STATE.status = completed`
- 801/801 slices
- 800/800 overlays
- 1,601 bulk PNGs evicted by policy
- nine anchor PNGs retained
- C1 independent QA 9/9 PASS
- 283-byte CUDA-path warning retained

Therefore QA-018 passes in QA-v2, and the original failure is rejected as a lifecycle-contract error. This correction has no effect on QA-015.

## 5. Separated status ledger

| State | Decision |
|---|---|
| Original notebook executed | confirmed |
| 16 target outer-CV completed | confirmed |
| 16 final-refit outputs complete | rejected — 13/16 |
| Code/input/environment replay fidelity | confirmed |
| Exact historical numerical parity | unresolved |
| Adapter parity | not established |
| Ready for adapter-parity preregistration | confirmed — no fit |

## 6. Official T1 decision

`T1_COMPLETED_WITH_EVIDENCE_AND_DECLARED_REFIT_GAP`

This means T1 execution evidence is accepted without claiming complete final models or exact historical numerical parity. The three missing refits remain explicit holds.

## Evidence boundaries

No C1 or Training replay was rerun. No other notebook, adapter fit, benchmark, feature selection, HQ function, original notebook, Excel, NB-CURRENT, NB-ORIG or LEGACY-PY was modified.
