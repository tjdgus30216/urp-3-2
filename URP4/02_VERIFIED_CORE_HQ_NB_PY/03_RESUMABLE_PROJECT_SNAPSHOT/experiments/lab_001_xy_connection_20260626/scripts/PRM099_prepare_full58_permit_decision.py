from __future__ import annotations

import hashlib
import json
import math
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import psutil
from scipy.stats import pearsonr, spearmanr


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
TABLES = LAB / "reports" / "tables"
FACTORY = LAB / "factories" / "PRM-099"
CONTRACTS = FACTORY / "contracts"
AUTH = FACTORY / "authorizations"
REPORTS = FACTORY / "reports"
QUARANTINE = FACTORY / "quarantine" / "permit_mutations"
RUNNER = LAB / "scripts" / "PRM099_third_wave_full58_runner.py"
FORMULA_LIBRARY = LAB / "scripts" / "PRM098_third_wave_formula_library.py"
CONFIG = CONTRACTS / "PRM099_FULL58_SIX_OUTPUT_CONFIG_20260723.json"
CONTRACT = CONTRACTS / "PRM-099_FULL58_PERMIT_DECISION_CONTRACT_20260723.json"
PERMIT = AUTH / "PRM-100_THIRD_WAVE_FULL58_V128_EXECUTION_PERMIT_20260723.json"


OUTPUTS = [
    "LIT-X019::solid_void_chord_q50_geomean_ratio",
    "LIT-X019::solid_void_chord_x_q50_ratio",
    "LIT-X019::solid_void_chord_y_q50_ratio",
    "LIT-X019::solid_void_chord_z_q50_ratio",
    "LIT-X024::ect_abs_auc_direction_mean_per_mm3",
    "LIT-X024::ect_total_variation_direction_mean_per_mm3",
]
MODELS = ["B3", "C1", "L1", "F1", "T8", "T9"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def stable_hash(payload: object) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def subprocess_doctor(permit: Path | None = None) -> tuple[int, str, str]:
    command = [sys.executable, str(RUNNER), "doctor", "--config", str(CONFIG), "--contract", str(CONTRACT)]
    if permit is not None:
        command += ["--permit", str(permit)]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def parent_derived(model: str, xreg: pd.DataFrame) -> dict[str, float]:
    one = xreg[xreg.model_id.eq(model)].set_index("candidate_id")
    ratios = {}
    for axis in "xyz":
        s = float(one.loc[f"LIT-X001::solid_chord_{axis}_q50_mm", "value"])
        v = float(one.loc[f"LIT-X016::void_chord_{axis}_q50_mm", "value"])
        ratios[axis] = s / v
    return {
        "LIT-X019::solid_void_chord_q50_geomean_ratio": float(math.exp(np.mean(np.log(list(ratios.values()))))),
        **{f"LIT-X019::solid_void_chord_{a}_q50_ratio": ratios[a] for a in "xyz"},
    }


def relation(x: np.ndarray, y: np.ndarray) -> dict:
    finite = np.isfinite(x) & np.isfinite(y)
    x, y = x[finite], y[finite]
    n = len(x)
    if n < 5:
        return {"common_n": n, "pearson": np.nan, "spearman": np.nan, "scale": np.nan, "max_scaled_relative_residual": np.nan, "relation": "undercoverage"}
    px = float(pearsonr(x, y).statistic) if np.std(x) > 0 and np.std(y) > 0 else np.nan
    sp = float(spearmanr(x, y).statistic) if np.std(x) > 0 and np.std(y) > 0 else np.nan
    exact = np.allclose(x, y, rtol=1e-10, atol=1e-12)
    scale = float(np.dot(x, y) / np.dot(x, x)) if np.dot(x, x) > 0 else np.nan
    denom = np.maximum(np.maximum(np.abs(y), np.abs(scale * x)), 1e-12)
    residual = float(np.max(np.abs(y - scale * x) / denom)) if np.isfinite(scale) else np.nan
    if exact:
        label = "exact_duplicate_small_panel"
    elif np.isfinite(residual) and residual <= 1e-8:
        label = "proportional_duplicate_small_panel"
    elif np.isfinite(px) and np.isfinite(sp) and abs(px) >= 0.98 and abs(sp) >= 0.95:
        label = "high_redundancy_small_panel"
    else:
        label = "distinct_or_unresolved_small_panel"
    return {"common_n": n, "pearson": px, "spearman": sp, "scale": scale, "max_scaled_relative_residual": residual, "relation": label}


def main() -> None:
    for d in [CONTRACTS, AUTH, REPORTS, QUARANTINE, TABLES]:
        d.mkdir(parents=True, exist_ok=True)

    gate = pd.read_csv(TABLES / "PRM098_output_resolution_gate.csv")
    selected = gate.loc[gate.technical_state.eq("likely_resolution_qualified_not_selected")].copy()
    if selected.candidate_id.tolist() != OUTPUTS:
        raise SystemExit("PRM098 six-output order/scope mismatch")
    schema = pd.read_csv(TABLES / "PRM097_candidate_output_schema.csv")
    scope = selected.merge(schema[["candidate_id", "formula_id", "unit", "source_lineage", "direct_or_derived"]], on="candidate_id", how="left")
    scope["PRM099_route"] = scope.candidate_group_id.map({"LIT-X019": "derive_from_existing_full58_X001_X016_V128", "LIT-X024": "compute_ECT_from_existing_full58_V128_mask"})
    scope["full58_authorization_role"] = "permit_candidate_not_executed"
    scope["active_feature"] = False
    scope["promoted"] = False
    scope["y_evidence"] = False
    scope.to_csv(TABLES / "PRM099_returned_six_output_scope.csv", index=False, encoding="utf-8-sig")

    source = pd.read_csv(TABLES / "PRM092_full58_V128_scope.csv", dtype=str, keep_default_na=False)
    asset_rows = []
    for row in source.itertuples(index=False):
        mask = ROOT / row.reuse_mask_path
        actual = sha256(mask) if mask.is_file() else ""
        asset_rows.append({
            "model_id": row.model_id, "model_family": row.model_family, "resolution_id": row.resolution_id,
            "mask_path": row.reuse_mask_path, "expected_mask_sha256": row.reuse_mask_sha256,
            "actual_mask_sha256": actual, "hash_pass": actual == row.reuse_mask_sha256,
            "new_mask_authorized": False,
        })
    assets = pd.DataFrame(asset_rows)
    assets.to_csv(TABLES / "PRM099_full58_V128_asset_registry.csv", index=False, encoding="utf-8-sig")

    xreg_path = TABLES / "PRM096_xreg_v0_2_values_long.csv"
    xreg = pd.read_csv(xreg_path)
    panel = pd.read_csv(FACTORY.parent / "PRM-098" / "reports" / "PRM098_representative_panel_values_long.csv")
    panel = panel[panel.resolution_id.eq("V128") & panel.model_id.isin(MODELS) & panel.candidate_id.isin(OUTPUTS)].copy()

    parity_rows = []
    for model in MODELS:
        derived = parent_derived(model, xreg)
        observed = panel[panel.model_id.eq(model)].set_index("candidate_id")["value"]
        for cid, value in derived.items():
            obs = float(observed.loc[cid])
            parity_rows.append({"model_id": model, "candidate_id": cid, "parent_derived_value": value, "PRM098_value": obs, "abs_error": abs(value - obs), "status": "PASS" if abs(value - obs) <= 1e-12 else "FAIL"})
    parity = pd.DataFrame(parity_rows)
    parity.to_csv(TABLES / "PRM099_X019_parent_lineage_panel_parity.csv", index=False, encoding="utf-8-sig")

    overlap_rows = []
    existing_ids = sorted(xreg.candidate_id.unique())
    for cid in OUTPUTS:
        left = panel[panel.candidate_id.eq(cid)][["model_id", "value"]].rename(columns={"value": "new_value"})
        for existing in existing_ids:
            right = xreg[xreg.candidate_id.eq(existing) & xreg.model_id.isin(MODELS)][["model_id", "value"]].rename(columns={"value": "existing_value"})
            merged = left.merge(right, on="model_id", how="inner")
            stats = relation(merged.new_value.to_numpy(float), merged.existing_value.to_numpy(float))
            overlap_rows.append({"candidate_id": cid, "existing_candidate_id": existing, **stats, "evidence_scope": "six_model_panel_diagnostic_only", "selection_effect": "none"})
    overlap = pd.DataFrame(overlap_rows)
    overlap.to_csv(TABLES / "PRM099_six_output_vs_XREG_v0_2_panel_overlap.csv", index=False, encoding="utf-8-sig")

    led = pd.read_csv(FACTORY.parent / "PRM-098" / "reports" / "PRM098_progressive_panel_execution_ledger.csv")
    cost_rows = []
    for group, route in [("LIT-X019", "derive_existing_parents"), ("LIT-X024", "compute_existing_V128_mask")]:
        sample = led[(led.candidate_group_id.eq(group)) & (led.resolution_id.eq("V128")) & (led.status.eq("passed"))]
        median = float(sample.runtime_s.median())
        p90 = float(sample.runtime_s.quantile(.9))
        peak = float(sample.peak_rss_gib.max())
        if group == "LIT-X019":
            projected = 1.0
            note = "full58 X019 is authorized as CSV parent derivation, so mask timing is reference only"
        else:
            projected = p90 * 58 * 2.0
            note = "2x p90 serial safety projection; full ECT curve artifact retained"
        cost_rows.append({"candidate_group_id": group, "execution_route": route, "panel_n": len(sample), "V128_median_s": median, "V128_p90_s": p90, "V128_peak_rss_gib": peak, "projected_full58_wall_s_with_safety": projected, "projected_full58_wall_min": projected / 60, "note": note})
    cost = pd.DataFrame(cost_rows)
    cost.to_csv(TABLES / "PRM099_full58_cost_projection.csv", index=False, encoding="utf-8-sig")

    cells = [{"model_id": r.model_id, "model_family": r.model_family, "mask_path": r.mask_path, "mask_sha256": r.expected_mask_sha256} for r in assets.itertuples(index=False)]
    scope_hash = stable_hash({"cells": cells, "outputs": OUTPUTS, "resolution": "V128"})
    config = {
        "work_id": "PRM-099", "title": "THIRD_WAVE_SIX_OUTPUT_FULL58_V128_CONFIG",
        "resolution_id": "V128", "pitch_mm": 0.3125, "expected_models": 58, "expected_values": 348,
        "output_roster": OUTPUTS, "cells": cells, "scope_hash": scope_hash,
        "xreg_parent_table_path": str(xreg_path.relative_to(ROOT)), "xreg_parent_table_sha256": sha256(xreg_path),
        "resource_stop": {"single_cell_wall_seconds_max": 30.0, "process_rss_gib_max": 1.0, "serial_workers": 1, "partial_merge": False},
        "routes": {"LIT-X019": "derive existing X001/X016 q50 V128 parents", "LIT-X024": "compute ECT from existing V128 mask and retain full curve artifact"},
    }
    write_json(CONFIG, config)
    contract = {
        "work_id": "PRM-099", "title": "THIRD_WAVE_FULL58_PERMIT_DECISION_CONTRACT",
        "created_at_kst": datetime.now(ZoneInfo("Asia/Seoul")).isoformat(),
        "execution_authorized_by_contract": False, "runner_sha256": sha256(RUNNER), "config_sha256": sha256(CONFIG),
        "formula_library_sha256": sha256(FORMULA_LIBRARY), "scope_hash": scope_hash, "output_roster": OUTPUTS,
        "allowed_PRM099_actions": ["doctor", "permit_review", "invalid_permit_guard_tests"],
        "future_actions_require_permit": ["run-cell", "merge"],
        "locks": {"performance_y_read": 0, "model_fit": 0, "feature_selection": 0, "feature_promotion": 0, "inverse_design_claim": 0, "new_mask": 0, "NB_CURRENT_mutation": 0, "LEGACY_PY_mutation": 0, "original_Excel_mutation": 0},
    }
    write_json(CONTRACT, contract)

    rc, stdout, stderr = subprocess_doctor()
    doctor_payload = json.loads(stdout) if rc == 0 else {}
    no_permit_cell = subprocess.run([sys.executable, str(RUNNER), "run-cell", "--model", "B3", "--config", str(CONFIG), "--contract", str(CONTRACT)], capture_output=True, text=True, check=False)
    prm098_qa = json.loads((FACTORY.parent / "PRM-098" / "reports" / "PRM098_postmerge_sync_QA_summary.json").read_text(encoding="utf-8"))
    available = psutil.virtual_memory().available / 2**30
    disk = shutil.disk_usage(ROOT).free / 2**30
    checks = [
        ("P099-01", prm098_qa.get("status") == "PASS" and prm098_qa.get("checks") == "31/31", "PRM098 sealed QA 31/31"),
        ("P099-02", selected.candidate_id.tolist() == OUTPUTS, "exact six technical returns"),
        ("P099-03", len(assets) == 58 and assets.hash_pass.all(), "58/58 existing V128 masks hash-valid"),
        ("P099-04", len(parity) == 24 and parity.status.eq("PASS").all(), "X019 parent-derived panel parity 24/24"),
        ("P099-05", len(overlap) == 648, "six-model x-only overlap diagnostic 6x108"),
        ("P099-06", float(cost.loc[cost.candidate_group_id.eq("LIT-X024"), "projected_full58_wall_s_with_safety"].iloc[0]) < 600 and float(cost.V128_peak_rss_gib.max()) < 1.0, "bounded X024 cost projection"),
        ("P099-07", rc == 0 and doctor_payload.get("source_mask_cells_verified") == "58/58" and doctor_payload.get("competing_python_processes") == [], "fresh doctor 58/58 and no competing Python"),
        ("P099-08", available >= 4 and disk >= 2, "resource floor available"),
        ("P099-09", not (FACTORY / "intermediate").exists(), "no scientific intermediate before permit"),
        ("P099-10", no_permit_cell.returncode != 0 and not (FACTORY / "intermediate").exists(), "run-cell fails closed without permit"),
        ("P099-11", config["expected_values"] == 348 and contract["execution_authorized_by_contract"] is False, "exact scope and preparation-only contract"),
        ("P099-12", all(v == 0 for v in contract["locks"].values()), "all scientific locks remain zero"),
    ]
    review = pd.DataFrame([{"check_id": i, "status": "PASS" if ok else "FAIL", "detail": detail} for i, ok, detail in checks])
    review.to_csv(REPORTS / "PRM099_permit_review_QA.csv", index=False, encoding="utf-8-sig")
    all_pass = review.status.eq("PASS").all()
    decision = "ISSUE_EXACT_HASH_PRM100_PERMIT_NO_EXECUTION" if all_pass else "STOP_WITHHOLD_PERMIT"

    if all_pass:
        permit = {
            "authorized_work_id": "PRM-100", "title": "THIRD_WAVE_FULL58_V128_SIX_OUTPUT_EXECUTION_PERMIT",
            "created_at_kst": datetime.now(ZoneInfo("Asia/Seoul")).isoformat(), "execution_authorized": True,
            "authorization_status": "exact_hash_permitted_not_executed", "allowed_actions": ["run-cell", "merge"],
            "runner_sha256": sha256(RUNNER), "config_sha256": sha256(CONFIG), "contract_sha256": sha256(CONTRACT),
            "formula_library_sha256": sha256(FORMULA_LIBRARY), "scope_hash": scope_hash,
            "expected_models": 58, "expected_values": 348, "output_roster": OUTPUTS,
            "routes": config["routes"], "new_mask_cap": 0,
            "required_runtime": {"environment": "KMK312", "python": "tools/envs/KMK312/python.exe", "serial_workers": 1},
            "required_fresh_preflight": ["doctor PASS", "58/58 mask hashes", "no competing Python", "available RAM >=4 GiB", "free disk >=2 GiB", "permit_valid true"],
            "stop_conditions": ["hash or scope drift", "new mask attempt", "cell >30 s", "RSS >1 GiB", "nonfinite or roster mismatch", "partial merge", "competing Python"],
            "locks": contract["locks"],
            "claim_boundary": "Technical x-only census only; no y, fit, selection, promotion, prediction or inverse-design authorization.",
        }
        write_json(PERMIT, permit)

    decision_table = pd.DataFrame([{
        "work_id": "PRM-099", "decision": decision, "permit_path": str(PERMIT.relative_to(ROOT)) if all_pass else "",
        "authorized_future_work": "PRM-100" if all_pass else "", "execution_performed": False,
        "expected_models": 58, "expected_values": 348, "new_masks": 0, "y_fit_selection_promotion": "0/0/0/0",
    }])
    decision_table.to_csv(TABLES / "PRM099_execute_or_stop_decision.csv", index=False, encoding="utf-8-sig")

    mutations = []
    if all_pass:
        valid = json.loads(PERMIT.read_text(encoding="utf-8"))
        cases = {
            "runner_hash": ("runner_sha256", "0" * 64), "config_hash": ("config_sha256", "0" * 64),
            "contract_hash": ("contract_sha256", "0" * 64), "formula_hash": ("formula_library_sha256", "0" * 64),
            "expected_models": ("expected_models", 57), "expected_values": ("expected_values", 347),
            "output_roster": ("output_roster", OUTPUTS[:-1]), "actions": ("allowed_actions", ["run-cell"]),
            "execution_flag": ("execution_authorized", False), "lock": ("locks", {**valid["locks"], "feature_selection": 1}),
        }
        for name, (key, value) in cases.items():
            mutated = dict(valid)
            mutated[key] = value
            path = QUARANTINE / f"{name}.json"
            write_json(path, mutated)
            rc_m, out_m, err_m = subprocess_doctor(path)
            mutations.append({"mutation_id": name, "returncode": rc_m, "rejected": rc_m != 0, "stderr_tail": err_m[-240:], "scientific_value_created": False})
    mutation_df = pd.DataFrame(mutations)
    mutation_df.to_csv(TABLES / "PRM099_permit_mutation_tests.csv", index=False, encoding="utf-8-sig")

    valid_rc, valid_out, valid_err = subprocess_doctor(PERMIT) if all_pass else (1, "", "permit withheld")
    valid_payload = json.loads(valid_out) if valid_rc == 0 else {}
    summary = {
        "status": "PASS" if all_pass and valid_rc == 0 and mutation_df.rejected.all() else "FAIL",
        "review_checks": f"{int(review.status.eq('PASS').sum())}/{len(review)}",
        "mutation_rejections": f"{int(mutation_df.rejected.sum())}/{len(mutation_df)}" if len(mutation_df) else "0/0",
        "decision": decision, "permit_valid_doctor": valid_payload.get("permit_valid", False),
        "execution_performed": False, "full58_values_created": 0, "panel_overlap_relations": len(overlap),
        "X019_parent_parity": f"{int(parity.status.eq('PASS').sum())}/{len(parity)}",
    }
    write_json(REPORTS / "PRM099_permit_decision_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if summary["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
