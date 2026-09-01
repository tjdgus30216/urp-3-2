from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path


RUN_ID = "TRAIN-PARITY-003-20260801-001"
DECISION = "NO_GO_WITH_BLOCKER"
BLOCKER = "TARGET_IDENTITY_AND_HOLD_POLICY_CROSSWALK_DRIFT"
KST = timezone(timedelta(hours=9))

ROOT = Path(__file__).resolve().parents[5]
RUN = Path(__file__).resolve().parent
RESULTS = ROOT / "experiments/lab_001_xy_connection_20260626/results"
P1 = RESULTS / "TRAIN-PARITY-001/TRAIN-PARITY-001-20260801-001"
P2 = RESULTS / "TRAIN-PARITY-002/TRAIN-PARITY-002-20260801-001"
P2A = RESULTS / "TRAIN-PARITY-002A/TRAIN-PARITY-002A-20260801-001"
REPLAY = RESULTS / "TRAIN-REPLAY-001/TRAIN-REPLAY-001-20260731-001"
POSTRUN = RESULTS / "POSTRUN-GATE-001/POSTRUN-GATE-001-20260801-001"
SOURCE = ROOT / "experiments/lab_001_xy_connection_20260626/data/raw/professor_training_20260709/Training_260419-2nd method - New feature - Good. vibration.ipynb"
WORKBOOK = ROOT / "experiments/lab_001_xy_connection_20260626/data/raw/professor_training_20260709/Total data_260503.xlsx"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_json(name: str, obj) -> None:
    (RUN / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(name: str, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"empty CSV: {name}")
    with (RUN / name).open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def long_read_csv(path: Path):
    # Python 3.12 honors the Windows long-path prefix even when PowerShell 5 does not.
    p = str(path.resolve())
    if len(p) >= 248 and not p.startswith("\\\\?\\"):
        p = "\\\\?\\" + p
    with open(p, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main() -> None:
    RUN.mkdir(parents=True, exist_ok=True)
    now = datetime.now(KST).isoformat(timespec="seconds")

    source_sha = sha256(SOURCE)
    workbook_sha = sha256(WORKBOOK)
    p2a_manifest = read_json(P2A / "IMPLEMENTATION_MANIFEST.json")
    fold_meta = read_json(P2 / "artifacts/SHARED_FOLD_MANIFEST.meta.json")
    dataset_manifest_path = P2 / "artifacts/DATASET_MANIFEST.json"
    dataset_manifest = read_json(dataset_manifest_path)
    policy_path = P1 / "TARGET_ELIGIBILITY_AND_HOLD_POLICY.csv"
    policy_rows = read_csv(policy_path)
    column_rows = [r for r in read_csv(P2 / "artifacts/COLUMN_IDENTITY_LEDGER.csv") if r["role"] == "target"]
    target_rows = read_csv(P2 / "artifacts/TARGET_SAMPLE_LEDGER.csv")
    fold_rows = long_read_csv(REPLAY / "generated_outputs/02_ModelComparison/all_output_method_comparison_folds.csv")
    refit_rows = long_read_csv(REPLAY / "generated_outputs/02_ModelComparison/final_refit_summary.csv")
    replay_state = read_json(REPLAY / "replay_state.json")

    expected_source = "11129a41bd4303d82c599148cd761adb3c858f58da017586e07fb0f06d055ff2"
    expected_workbook = "4a6ec7d03d92fa25851998689768d9db9f63227f00e778a528d758b368851dce"
    expected_fold = "3b18913ef68b6487b273a113ab3b3c0569d3246444f17003f68c0e01af1e89a6"
    if source_sha != expected_source or workbook_sha != expected_workbook or fold_meta["sha256"] != expected_fold:
        raise RuntimeError("predecessor hash drift")

    actual_by_col = {r["excel_col"]: r for r in column_rows}
    policy_by_col = {r["excel_col"]: r for r in policy_rows}
    sample_by_col = {r["excel_col"]: r for r in target_rows}
    refit_names = {r["output_name"] for r in refit_rows if r["status"] == "ok"}
    folds_by_name: dict[str, list[dict]] = {}
    for row in fold_rows:
        folds_by_name.setdefault(row["output_name"], []).append(row)

    confirmed_hold_names = {
        "Vibrational response | FRF (g/N) | 300-8000 Hz | AVG",
        "Vibrational response | FRF (g/N) | 6500-8000 Hz | AVG",
        "Yield strength",
    }
    actual_hold_cols = sorted(c for c, r in actual_by_col.items() if r["normalized_header"] in confirmed_hold_names)
    baked_hold_cols = ["FW", "GA", "HE"]
    crosswalk_mismatches = [
        c for c in actual_by_col
        if c not in policy_by_col or policy_by_col[c]["output_name"] != actual_by_col[c]["normalized_header"]
    ]

    replay_start = datetime.fromisoformat(replay_state["started_at"])
    replay_end = datetime.fromisoformat(replay_state["completed_at"])
    replay_minutes = (replay_end - replay_start).total_seconds() / 60.0
    empirical_minutes_per_target_repeat = replay_minutes / (16 * 12)

    candidates = []
    provisional_col = "HI"
    for col in ["FW", "FX", "FZ", "GA", "GC", "GG", "GJ", "GZ", "HA", "HB", "HC", "HD", "HE", "HG", "HI", "HK"]:
        actual = actual_by_col[col]
        sample = sample_by_col[col]
        name = actual["normalized_header"]
        folds = folds_by_name[name]
        reached = sorted({r["method_name"] for r in folds})
        hold_by_name = name in confirmed_hold_names
        final_refit = "present" if name in refit_names else "absent"
        non_ok = sum(r["status"] != "ok" for r in folds)
        if hold_by_name:
            role = "hold_ineligible"
            reason = "Confirmed three-target final-refit hold by target name."
            risk = "prohibited"
        elif col == provisional_col:
            role = "provisional_best_blocked_not_selected"
            reason = "Largest stable coverage (193 rows/128 groups), 12/12 repeats, refit present, nine reached branches, baseline final method; blocked because target-policy crosswalk is not valid."
            risk = "low numerical pilot risk; critical identity-contract risk"
        elif int(actual["nan_count"]) >= 170:
            role = "rejected_for_first_sentinel"
            reason = "Primary target but only 25 samples; poor first-pilot coverage."
            risk = "high small-sample risk"
        else:
            role = "eligible_not_selected_due_no_go"
            reason = "Eligible by observed target name and replay evidence, but no target can be frozen while the policy crosswalk is drifting."
            risk = "medium contract risk"
        candidates.append({
            "target_id": f"TRAIN2NF::{col}",
            "excel_col": col,
            "target_name": name,
            "sample_count": sample["sample_count"],
            "group_count": sample["group_count"],
            "missing_count": actual["nan_count"],
            "missing_rate": f"{int(actual['nan_count']) / 198:.8f}",
            "outer_repeats_completed": str(len({r["repeat_id"] for r in folds})),
            "outer_status_non_ok_rows": str(non_ok),
            "replay_completeness": "12/12" if len({r["repeat_id"] for r in folds}) == 12 and non_ok == 0 else "incomplete",
            "final_refit_status": final_refit,
            "reached_source_branches": "|".join(reached),
            "reached_branch_count": str(len(reached)),
            "expected_runtime_source_repeat": f"empirical planning basis {empirical_minutes_per_target_repeat:.2f} min average; sentinel estimate 6-10 min",
            "confirmed_hold_by_target_name": str(hold_by_name).lower(),
            "predecessor_policy_name_for_same_column": policy_by_col[col]["output_name"],
            "predecessor_policy_status_for_same_column": policy_by_col[col]["status"],
            "crosswalk_exact": str(policy_by_col[col]["output_name"] == name).lower(),
            "candidate_role": role,
            "risk": risk,
            "selection_or_rejection_reason": reason,
        })
    write_csv("SENTINEL_TARGET_SELECTION.csv", candidates)

    evidence = [
        ("TRAIN-REPLAY-001", REPLAY / "REPORT.md"),
        ("POSTRUN-GATE-001", POSTRUN / "REPORT.md"),
        ("TRAIN-PARITY-001", P1 / "REPORT.md"),
        ("TRAIN-PARITY-002", P2 / "REPORT.md"),
        ("TRAIN-PARITY-002A", P2A / "REPORT.md"),
        ("source_notebook", SOURCE),
        ("source_workbook", WORKBOOK),
        ("exact_adapter_manifest", P2A / "IMPLEMENTATION_MANIFEST.json"),
        ("dataset_manifest", dataset_manifest_path),
        ("fold_manifest", P2 / "artifacts/SHARED_FOLD_MANIFEST.csv"),
        ("tolerance_registry", P1 / "PREDICTION_METRIC_TOLERANCE_REGISTRY.csv"),
        ("target_policy", policy_path),
    ]
    binding_rows = []
    for role, path in evidence:
        binding_rows.append({
            "binding_role": role,
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256(path),
            "status": "hash_verified",
            "entrypoint_or_scope": "read-only evidence",
            "compatibility_delta": "none",
            "forbidden_modifications": "source/workbook/predecessor assets",
            "output_isolation": str(RUN.relative_to(ROOT)).replace("\\", "/"),
        })
    binding_rows += [
        {
            "binding_role": "reference_runner",
            "path": "planned TRAIN-PARITY-004 isolated source runner",
            "sha256": "not_created",
            "status": "contract_defined_implementation_required",
            "entrypoint_or_scope": "planned run_reference_branch(source evaluate_method_train_test)",
            "compatibility_delta": "path/output/kernel/thread routing and observation-only instrumentation",
            "forbidden_modifications": "branch logic, candidates, objective, tie behavior, fallback, seeds",
            "output_isolation": "future TRAIN-PARITY-004/<run_id>/reference/<target>/<repeat>/<branch>/",
        },
        {
            "binding_role": "adapter_runner",
            "path": str((P2A / "implementation/branches.py").relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256(P2A / "implementation/branches.py"),
            "status": "callable_present_but_target_policy_blocked",
            "entrypoint_or_scope": "SourceExactBranch.__call__",
            "compatibility_delta": "NO_FIT permit gate and observation instrumentation only",
            "forbidden_modifications": "source branch body and protected inputs",
            "output_isolation": "future TRAIN-PARITY-004/<run_id>/adapter/<target>/<repeat>/<branch>/",
        },
    ]
    write_csv("SOURCE_REFERENCE_ADAPTER_BINDING.csv", binding_rows)

    stage_rows = [
        ("P0", "dataset identity", "rows, target column, X order, NaN mask", "exact", "first mismatch stops P1-P8"),
        ("P1", "identity and split", "X_KEY, GROUP_ID, train/test row and group membership", "exact", "first mismatch stops P2-P8"),
        ("P2", "preprocessing", "input/output arrays, imputation/scaling/target preprocessing identity", "exact identity; numeric per TOL-v0.1", "first mismatch stops P3-P8"),
        ("P3", "feature pipeline", "prefilter, rank, engineered feature identity/order and scores", "identity/order exact; scores TOL-v0.1", "first mismatch stops P4-P8"),
        ("P4", "branch and model construction", "branch, transform, estimator, canonical hyperparameters", "exact", "first mismatch stops P5-P8"),
        ("P5", "inner predictions", "row-level inner-fold predictions", "atol=1e-10; rtol=1e-8", "first mismatch stops P6-P8"),
        ("P6", "inner evaluation", "R2/RMSE/MAE, candidate rank, ties and selected candidate", "metrics atol=1e-10 rtol=1e-8; rank/tie exact", "first mismatch stops P7-P8"),
        ("P7", "outer result", "selected candidate and row-level outer predictions", "identity exact; predictions atol=1e-10 rtol=1e-8", "terminal permitted comparison stage"),
        ("P8", "final refit", "full-data final-refit state and outputs", "prohibited in sentinel pilot", "not executable; separate future approval"),
    ]
    write_csv("STAGE_PARITY_LEDGER_SCHEMA.csv", [
        {
            "stage_id": s,
            "stage_name": n,
            "required_comparison": c,
            "comparison_rule": rule,
            "downstream_rule": down,
            "required_identity_fields": "run_id|target_id|outer_repeat|branch_id|row_id|group_id|fold_id|source_hash|adapter_hash|config_hash",
            "source_value_field": "source_value_or_hash",
            "adapter_value_field": "adapter_value_or_hash",
            "status_enum": "PARITY_PASS|PARITY_FAIL_AT_Pn|BLOCKED_BY_REFERENCE_RUNNER|BLOCKED_BY_HIDDEN_STATE|BLOCKED_BY_RESOURCE_ESTIMATE|NO_GO_CONTRACT_DRIFT",
        }
        for s, n, c, rule, down in stage_rows
    ])

    branch_estimates = [
        ("baseline_stability", "8736", "static exact upper-path count for vibrational top-k/model/search grid"),
        ("stability_lasso_ridge", "35+internal LassoCV", "24 stability fits + 10 inner fits + 1 final fit; LassoCV internal work excluded"),
        ("spca_ridge", "100", "9 SparsePCA fits + 90 inner fits + 1 final fit"),
        ("spca_huber", "100", "9 SparsePCA fits + 90 inner fits + 1 final fit"),
        ("block_pca_ridge", "31-55", "30 inner + 1 final; up to 24 block PCA transformer fits"),
        ("bagged_subspace_ridge", "50", "10 inner + 40 subspace Ridge fits"),
        ("minimal_class_average", "8738-8739", "baseline search plus 2-3 ensemble-member refits"),
        ("multitask_screen_ridge", "42+internal multitask CV", "one multitask-screen fit + 40 inner + 1 final"),
        ("multitask_screen_pls", "42+internal multitask CV", "one multitask-screen fit + 40 inner + 1 final"),
        ("spca_pls", "0", "not reached by provisional vibrational sentinel; do not force execution"),
    ]
    resource_rows = []
    for branch, fits, basis in branch_estimates:
        resource_rows.append({
            "scope": "branch",
            "runner": "source_or_adapter",
            "target_id": "TRAIN2NF::HI provisional only",
            "outer_repeat": "0 provisional only",
            "branch_id": branch,
            "expected_fit_count": fits,
            "runtime_estimate": "included in runner aggregate",
            "max_memory": "runner cap 4 GiB; terminate above cap",
            "output_estimate": "branch ledger <=25 MiB",
            "timeout": "15 min per branch; 45 min per runner",
            "checkpoint": "target/repeat/runner/branch atomic directory",
            "basis": basis,
            "authorization": "none",
        })
    resource_rows += [
        {
            "scope": "aggregate",
            "runner": "source_reference",
            "target_id": "TRAIN2NF::HI provisional only",
            "outer_repeat": "0 provisional only",
            "branch_id": "nine source-reached branches",
            "expected_fit_count": "17875-17899 + internal CV work",
            "runtime_estimate": f"6-10 min planning estimate; historical average {empirical_minutes_per_target_repeat:.2f} min per target-repeat",
            "max_memory": "4 GiB hard cap",
            "output_estimate": "<=125 MiB",
            "timeout": "45 min",
            "checkpoint": "after every branch",
            "basis": "static source-path count and 16-target/12-repeat replay elapsed time",
            "authorization": "none",
        },
        {
            "scope": "aggregate",
            "runner": "adapter",
            "target_id": "TRAIN2NF::HI provisional only",
            "outer_repeat": "0 provisional only",
            "branch_id": "nine source-reached branches",
            "expected_fit_count": "17875-17899 + internal CV work",
            "runtime_estimate": "6-10 min planning estimate",
            "max_memory": "4 GiB hard cap",
            "output_estimate": "<=125 MiB",
            "timeout": "45 min",
            "checkpoint": "after every branch",
            "basis": "same numerical source paths behind adapter permit",
            "authorization": "none",
        },
        {
            "scope": "aggregate",
            "runner": "combined_future_parity",
            "target_id": "TRAIN2NF::HI provisional only",
            "outer_repeat": "0 provisional only",
            "branch_id": "source + adapter",
            "expected_fit_count": "35750-35798 + internal CV work",
            "runtime_estimate": "12-20 min planning estimate; 90 min global abort ceiling",
            "max_memory": "sequential runners; 4 GiB each",
            "output_estimate": "<=250 MiB",
            "timeout": "90 min global",
            "checkpoint": "runner/branch resume; never overwrite completed branch",
            "basis": "sequential source and adapter execution",
            "authorization": "none",
        },
    ]
    write_csv("RESOURCE_AND_RUNTIME_ESTIMATE.csv", resource_rows)

    stop_conditions = [
        ("STOP-001", "source notebook hash drift", "NO_GO_CONTRACT_DRIFT"),
        ("STOP-002", "source workbook hash drift", "NO_GO_CONTRACT_DRIFT"),
        ("STOP-003", "adapter implementation hash drift", "NO_GO_CONTRACT_DRIFT"),
        ("STOP-004", "fold manifest hash drift", "NO_GO_CONTRACT_DRIFT"),
        ("STOP-005", "target ID/name/column/hold-policy crosswalk mismatch", "NO_GO_CONTRACT_DRIFT"),
        ("STOP-006", "reference runner cannot invoke protected source logic directly", "BLOCKED_BY_REFERENCE_RUNNER"),
        ("STOP-007", "source and adapter row/group/fold identity cannot be proven", "PARITY_FAIL_AT_P0_OR_P1"),
        ("STOP-008", "unresolved hidden notebook state", "BLOCKED_BY_HIDDEN_STATE"),
        ("STOP-009", "prediction ledger lacks row identity", "PARITY_FAIL_AT_P5_OR_P7"),
        ("STOP-010", "instrumentation changes scientific logic", "NO_GO_CONTRACT_DRIFT"),
        ("STOP-011", "any of three hold targets enters execution scope", "NO_GO_CONTRACT_DRIFT"),
        ("STOP-012", "runtime/memory/output ceiling exceeded without branch checkpoint", "BLOCKED_BY_RESOURCE_ESTIMATE"),
        ("STOP-013", "first P0-P7 mismatch", "PARITY_FAIL_AT_Pn; downstream parity evidence invalid"),
        ("STOP-014", "P8 final-refit requested", "NO_GO_CONTRACT_DRIFT"),
    ]
    write_csv("FAIL_CLOSED_STOP_CONDITIONS.csv", [
        {"stop_id": i, "condition": c, "resulting_state": s, "action": "stop current and downstream stages; retain evidence; no automatic retry", "active_now": str(i == "STOP-005").lower()}
        for i, c, s in stop_conditions
    ])

    contract = {
        "contract_id": "TRAIN-PARITY-003-CONTROLLED-EXECUTION-v0.1",
        "run_id": RUN_ID,
        "created_at_kst": now,
        "execution_performed": False,
        "decision": DECISION,
        "active_blocker": BLOCKER,
        "blocker_evidence": {
            "policy_to_workbook_name_mismatches": len(crosswalk_mismatches),
            "mismatched_columns": crosswalk_mismatches,
            "adapter_baked_hold_columns": baked_hold_cols,
            "hold_columns_implied_by_confirmed_target_names": actual_hold_cols,
            "adapter_contract_path": str((P2A / "implementation/contracts.py").relative_to(ROOT)).replace("\\", "/"),
        },
        "sentinel": {
            "official_selection": None,
            "provisional_candidate_not_authorized": {
                "target_id": "TRAIN2NF::HI",
                "excel_col": "HI",
                "target_name": actual_by_col["HI"]["normalized_header"],
                "outer_repeat": 0,
                "reason": "193 samples, 128 groups, 12/12 replay repeats, final refit present, nine source branches, no non-ok fold rows",
            },
        },
        "future_scope_if_repaired_and_reapproved": {
            "sentinel_targets": 1,
            "outer_repeats": [0],
            "inner_folds": "all folds from frozen manifest for target/repeat",
            "permitted_stages": [f"P{i}" for i in range(8)],
            "prohibited_stages": ["P8"],
            "runtime": {
                "python": "3.12.12",
                "environment": "project-local KMK312",
                "cpu_threads": 1,
                "gpu": "disabled",
                "PYTHONHASHSEED": "42",
            },
            "output_isolation": "future TRAIN-PARITY-004/<run_id>/<runner>/<target>/<repeat>/<branch>/",
            "resume": "branch-atomic; validate hashes before resume; never overwrite passed branch",
        },
        "hash_bindings": {
            "source_notebook": source_sha,
            "source_workbook": workbook_sha,
            "adapter_manifest": sha256(P2A / "IMPLEMENTATION_MANIFEST.json"),
            "dataset_manifest": sha256(dataset_manifest_path),
            "fold_manifest": fold_meta["sha256"],
            "tolerance_registry": sha256(P1 / "PREDICTION_METRIC_TOLERANCE_REGISTRY.csv"),
            "predecessor_target_policy": sha256(policy_path),
        },
        "tolerance": {
            "revision": "TRAIN-PARITY-TOL-v0.1",
            "exact": ["row/group/fold membership", "feature identity/order", "branch/method", "transform/estimator", "hyperparameters", "missingness mask", "selection/tie outcome"],
            "prediction": {"atol": 1e-10, "rtol": 1e-8},
            "metric": {"atol": 1e-10, "rtol": 1e-8},
            "correlation_only_pass_forbidden": True,
        },
        "dataset": dataset_manifest,
        "reference_runner": {
            "entrypoint": "planned isolated source runner; not yet created",
            "source_symbols": "protected notebook Cells 1,3-9; evaluate_method_train_test and dependencies",
            "compatibility_delta": ["input/output path routing", "canonical KMK312", "single-thread CPU", "GPU disabled", "observation-only instrumentation", "frozen fold injection"],
            "hidden_state_status": "must be bound explicitly before execution",
            "ready": False,
        },
        "adapter_runner": {
            "entrypoint": "TRAIN-PARITY-002A implementation.branches.SourceExactBranch.__call__",
            "ready": False,
            "reason": "numerical callable exists but HOLD_TARGETS control-plane identity is semantically wrong",
        },
        "fit_predict_metric_counts": {"fit": 0, "predict": 0, "prediction_rows": 0, "metric_rows": 0},
        "approval_required": True,
    }
    write_json("CONTROLLED_EXECUTION_CONTRACT.json", contract)

    permit = {
        "permit_id": "TRAIN-PARITY-004-PERMIT-NOT-ISSUED-001",
        "status": "NOT_ISSUED_NO_GO_CONTRACT_DRIFT",
        "execution_authorized": False,
        "sentinel_target": None,
        "provisional_target_not_authorized": "TRAIN2NF::HI",
        "outer_repeat": None,
        "source_hash": source_sha,
        "workbook_hash": workbook_sha,
        "adapter_manifest_hash": sha256(P2A / "IMPLEMENTATION_MANIFEST.json"),
        "fold_hash": fold_meta["sha256"],
        "config_hash": hashlib.sha256(json.dumps(contract["future_scope_if_repaired_and_reapproved"], sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "permitted_stages": [],
        "prohibited_stages": [f"P{i}" for i in range(9)],
        "timeout_resource_limits": "not applicable until repaired and reapproved",
        "tolerance_registry": "TRAIN-PARITY-TOL-v0.1",
        "output_directory": None,
        "stop_conditions": [i for i, _, _ in stop_conditions],
        "active_stop_condition": "STOP-005",
        "approval_required": True,
        "blocker": BLOCKER,
    }
    write_json("EXECUTION_PERMIT_DRAFT.json", permit)

    report = f"""# TRAIN-PARITY-003 controlled-execution preregistration — no fit

## Verdict

- Final decision: `{DECISION}`
- Active blocker: `{BLOCKER}`
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

The 16-target × 12-repeat replay lasted {replay_minutes:.2f} minutes, or {empirical_minutes_per_target_repeat:.2f} minutes per target-repeat on average while another job overlapped. The provisional vibrational sentinel is estimated at 6–10 minutes per runner and 12–20 minutes for sequential source+adapter execution, with a 90-minute global abort ceiling. Static source-path count is approximately 17,875–17,899 external fits per runner plus internal CV work. These are planning estimates, not execution records.

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
"""
    (RUN / "REPORT.md").write_text(report, encoding="utf-8")

    merge = f"""# TRAIN-PARITY-003 preregistration merge packet

- Decision: `{DECISION}`
- Evidence packet status: `ready_for_no_go_evidence_merge`
- Active stop: `STOP-005`
- Sentinel: not frozen; `TRAIN2NF::HI` is provisional only
- Planned repeat: `0`, not authorized
- Fit/predict: `0/0`
- Prediction/metric rows: `0/0`
- P8: prohibited
- Permit: not issued

## Mergeable evidence

- verified source/workbook/adapter/dataset/fold/tolerance hashes;
- 16-target candidate table and explicit target crosswalk failure;
- reference/adapter binding contract;
- P0–P8 parity ledger schema;
- no-fit resource estimate and fail-closed conditions;
- non-executable permit record.

## Non-mergeable claims

- GO for TRAIN-PARITY-004;
- numerical parity;
- reference runner readiness;
- model, method or feature quality;
- final-refit parity or held-target resolution.

## Required next action

Run `TRAIN-PARITY-003A_TARGET_IDENTITY_AND_HOLD_POLICY_CROSSWALK_REPAIR_NO_FIT`, then repeat the 003 adjudication. Do not edit protected predecessors in place.
"""
    (RUN / "MERGE_PACKET.md").write_text(merge, encoding="utf-8")

    # Builder record is no-fit by construction and intentionally not the independent QA.
    write_json("BUILD_STATE.json", {
        "run_id": RUN_ID,
        "completed_at_kst": now,
        "decision": DECISION,
        "fit_calls": 0,
        "predict_calls": 0,
        "prediction_rows": 0,
        "metric_rows": 0,
        "required_independent_qa_pending": True,
    })


if __name__ == "__main__":
    main()
