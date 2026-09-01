# TRAIN-PARITY-003 controlled-execution preregistration — no fit

## Verdict

- Final decision: `NO_GO_WITH_BLOCKER`
- Active blocker: `TARGET_IDENTITY_AND_HOLD_POLICY_CROSSWALK_DRIFT`
- Fit/predict calls: **0/0**
- Prediction/metric rows: **0/0**
- Executable permit: **not issued**

The numerical branch port remains valid as a source-exact no-fit implementation. This gate stops because the target control plane cannot yet prove that a target ID, workbook column, target name, hold status, and fold membership refer to the same scientific variable.

## Blocking evidence

The protected notebook selects columns `FW, FX, FZ, GA, GC, GG, GJ, GZ, HA, HB, HC, HD, HE, HG, HI, HK`. Direct workbook/column-ledger inspection gives:

- `FW = Modulus`
- `GC = Yield strength`
- `HE = FRF 300–8000 Hz AVG`
- `HG = FRF 300–3000 Hz AVG`
- `HI = FRF 3000–6500 Hz AVG`
- `HK = FRF 6500–8000 Hz AVG`

`TRAIN-PARITY-001` instead assigns a different target name to every one of the 16 selected columns. `TRAIN-PARITY-002A/implementation/contracts.py` consequently freezes `HOLD_TARGETS = FW, GA, HE`, while the three confirmed hold target names map to `GC, HE, HK` in the workbook. All **16/16 column-name pairs mismatch**. Counts remain 13/3, but membership is not scientifically equivalent.

The fold manifest itself is still valid by column ID and hash. The blocker is the semantic target/hold-policy binding around it, not the fold bytes.

## Sentinel evaluation

No official sentinel is selected under a drifting contract. `TRAIN2NF::HI` / `FRF 3000–6500 Hz AVG` is retained only as the best provisional candidate after repair because it has 193 samples, 128 groups, 12/12 clean replay repeats, a replay final refit, nine reached source branches, and no non-ok fold rows. Planned outer repeat is `0`; neither is authorized here.

## Future minimal scope after repair and reapproval

- one sentinel target;
- outer repeat `0` only;
- all frozen inner folds belonging to that target/repeat;
- isolated original-source reference runner versus exact adapter v0.1;
- identical workbook bytes, row/group identities, folds, seeds and runtime;
- sequential single-thread CPU, GPU disabled;
- P0–P7 only; P8 final refit prohibited;
- branch-atomic output directories and resume.

## Stage order

P0 dataset → P1 row/group/fold identity → P2 preprocessing → P3 features → P4 branch/model construction → P5 inner predictions → P6 inner metrics/ties → P7 outer selection/predictions. The first mismatch invalidates downstream parity evidence. P8 is locked.

`TRAIN-PARITY-TOL-v0.1` is bound without modification. Correlation alone can never produce `PARITY_PASS`.

## Resource planning only

The 16-target × 12-repeat replay lasted 990.77 minutes, or 5.16 minutes per target-repeat on average while another job overlapped. The provisional vibrational sentinel is estimated at 6–10 minutes per runner and 12–20 minutes for sequential source+adapter execution, with a 90-minute global abort ceiling. Static source-path count is approximately 17,875–17,899 external fits per runner plus internal CV work. These are planning estimates, not execution records.

## Reference/adapter readiness

- Source symbols and source-exact adapter callable exist.
- A separately isolated reference-runner entrypoint has not been created.
- The adapter target control plane is blocked by the wrong baked hold identities.
- Therefore source/reference readiness is **false for execution**.

## Next required repair gate

`TRAIN-PARITY-003A_TARGET_IDENTITY_AND_HOLD_POLICY_CROSSWALK_REPAIR_NO_FIT`

It must version, not overwrite, the target policy and adapter contract; bind column/name/value-hash/NaN-mask/fold target IDs; set holds to the three confirmed target names; replay static/fixture QA; and then rerun the 003 GO/NO-GO adjudication. No fit is needed for that repair.

## Claim boundary

No model was fitted, no prediction or metric was produced, no feature/model was compared, and no scientific parity result exists. `TRAIN-PARITY-002A` is not rejected; only its current target-policy control plane is ineligible for controlled execution.
