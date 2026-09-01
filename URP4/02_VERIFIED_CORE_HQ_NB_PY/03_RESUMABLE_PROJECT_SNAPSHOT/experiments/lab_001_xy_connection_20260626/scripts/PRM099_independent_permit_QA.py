from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
TABLES = LAB / "reports" / "tables"
FACTORY = LAB / "factories" / "PRM-099"
REPORTS = FACTORY / "reports"
RUNNER = LAB / "scripts" / "PRM099_third_wave_full58_runner.py"
FORMULA = LAB / "scripts" / "PRM098_third_wave_formula_library.py"
CONFIG = FACTORY / "contracts" / "PRM099_FULL58_SIX_OUTPUT_CONFIG_20260723.json"
CONTRACT = FACTORY / "contracts" / "PRM-099_FULL58_PERMIT_DECISION_CONTRACT_20260723.json"
PERMIT = FACTORY / "authorizations" / "PRM-100_THIRD_WAVE_FULL58_V128_EXECUTION_PERMIT_20260723.json"
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
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def relation(x: np.ndarray, y: np.ndarray) -> str:
    exact = np.allclose(x, y, rtol=1e-10, atol=1e-12)
    scale = float(np.dot(x, y) / np.dot(x, x)) if np.dot(x, x) > 0 else np.nan
    denom = np.maximum(np.maximum(np.abs(y), np.abs(scale * x)), 1e-12)
    residual = float(np.max(np.abs(y - scale * x) / denom)) if np.isfinite(scale) else np.nan
    px = float(pearsonr(x, y).statistic) if np.std(x) and np.std(y) else np.nan
    sp = float(spearmanr(x, y).statistic) if np.std(x) and np.std(y) else np.nan
    if exact:
        return "exact_duplicate_small_panel"
    if np.isfinite(residual) and residual <= 1e-8:
        return "proportional_duplicate_small_panel"
    if np.isfinite(px) and np.isfinite(sp) and abs(px) >= .98 and abs(sp) >= .95:
        return "high_redundancy_small_panel"
    return "distinct_or_unresolved_small_panel"


def main() -> None:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    permit = json.loads(PERMIT.read_text(encoding="utf-8"))
    assets = pd.read_csv(TABLES / "PRM099_full58_V128_asset_registry.csv")
    scope = pd.read_csv(TABLES / "PRM099_returned_six_output_scope.csv")
    parity = pd.read_csv(TABLES / "PRM099_X019_parent_lineage_panel_parity.csv")
    overlaps = pd.read_csv(TABLES / "PRM099_six_output_vs_XREG_v0_2_panel_overlap.csv")
    cost = pd.read_csv(TABLES / "PRM099_full58_cost_projection.csv")
    mutations = pd.read_csv(TABLES / "PRM099_permit_mutation_tests.csv")
    decision = pd.read_csv(TABLES / "PRM099_execute_or_stop_decision.csv")
    xreg = pd.read_csv(TABLES / "PRM096_xreg_v0_2_values_long.csv")
    panel = pd.read_csv(FACTORY.parent / "PRM-098" / "reports" / "PRM098_representative_panel_values_long.csv")
    panel = panel[panel.resolution_id.eq("V128") & panel.model_id.isin(MODELS) & panel.candidate_id.isin(OUTPUTS)]

    replay = []
    for row in assets.itertuples(index=False):
        path = ROOT / row.mask_path
        replay.append({"model_id": row.model_id, "expected": row.expected_mask_sha256, "actual": sha256(path), "status": "PASS" if sha256(path) == row.expected_mask_sha256 else "FAIL"})
    replay_df = pd.DataFrame(replay)
    replay_df.to_csv(REPORTS / "PRM099_independent_asset_hash_replay.csv", index=False, encoding="utf-8-sig")

    parity_replay = []
    for model in MODELS:
        one = xreg[xreg.model_id.eq(model)].set_index("candidate_id")
        ratios = {a: float(one.loc[f"LIT-X001::solid_chord_{a}_q50_mm", "value"]) / float(one.loc[f"LIT-X016::void_chord_{a}_q50_mm", "value"]) for a in "xyz"}
        values = {"LIT-X019::solid_void_chord_q50_geomean_ratio": float(np.exp(np.mean(np.log(list(ratios.values()))))), **{f"LIT-X019::solid_void_chord_{a}_q50_ratio": ratios[a] for a in "xyz"}}
        observed = panel[panel.model_id.eq(model)].set_index("candidate_id")["value"]
        for cid, value in values.items():
            err = abs(value - float(observed.loc[cid]))
            parity_replay.append({"model_id": model, "candidate_id": cid, "abs_error": err, "status": "PASS" if err <= 1e-12 else "FAIL"})
    parity_replay_df = pd.DataFrame(parity_replay)
    parity_replay_df.to_csv(REPORTS / "PRM099_independent_X019_parent_replay.csv", index=False, encoding="utf-8-sig")

    relation_replay = []
    for row in overlaps.itertuples(index=False):
        a = panel[panel.candidate_id.eq(row.candidate_id)][["model_id", "value"]].rename(columns={"value": "a"})
        b = xreg[xreg.candidate_id.eq(row.existing_candidate_id) & xreg.model_id.isin(MODELS)][["model_id", "value"]].rename(columns={"value": "b"})
        m = a.merge(b, on="model_id")
        label = relation(m.a.to_numpy(float), m.b.to_numpy(float))
        relation_replay.append({"candidate_id": row.candidate_id, "existing_candidate_id": row.existing_candidate_id, "expected_relation": row.relation, "replayed_relation": label, "status": "PASS" if label == row.relation else "FAIL"})
    relation_df = pd.DataFrame(relation_replay)
    relation_df.to_csv(REPORTS / "PRM099_independent_overlap_replay.csv", index=False, encoding="utf-8-sig")

    valid = subprocess.run([sys.executable, str(RUNNER), "doctor", "--config", str(CONFIG), "--contract", str(CONTRACT), "--permit", str(PERMIT)], capture_output=True, text=True, check=False)
    valid_payload = json.loads(valid.stdout) if valid.returncode == 0 else {}
    no_permit = subprocess.run([sys.executable, str(RUNNER), "run-cell", "--model", "B3", "--config", str(CONFIG), "--contract", str(CONTRACT)], capture_output=True, text=True, check=False)
    code = RUNNER.read_text(encoding="utf-8")

    checks = []
    def add(i: str, ok: bool, detail: str) -> None:
        checks.append({"check_id": i, "status": "PASS" if ok else "FAIL", "detail": detail})
    add("I099-01", scope.candidate_id.tolist() == OUTPUTS, "exact six output order")
    add("I099-02", len(assets) == 58 and replay_df.status.eq("PASS").all(), "58/58 mask hashes independently replayed")
    add("I099-03", len(parity_replay_df) == 24 and parity_replay_df.status.eq("PASS").all(), "X019 parent parity 24/24")
    add("I099-04", len(relation_df) == 648 and relation_df.status.eq("PASS").all(), "panel overlap labels 648/648")
    add("I099-05", len(overlaps[overlaps.relation.eq("high_redundancy_small_panel")]) == 10, "10 small-panel high-redundancy flags")
    add("I099-06", float(cost.loc[cost.candidate_group_id.eq("LIT-X024"), "projected_full58_wall_s_with_safety"].iloc[0]) < 600, "X024 safety projection below 10 minutes")
    add("I099-07", contract["runner_sha256"] == sha256(RUNNER) and permit["runner_sha256"] == sha256(RUNNER), "runner hash bound twice")
    add("I099-08", contract["config_sha256"] == sha256(CONFIG) and permit["config_sha256"] == sha256(CONFIG), "config hash bound twice")
    add("I099-09", contract["formula_library_sha256"] == sha256(FORMULA) and permit["formula_library_sha256"] == sha256(FORMULA), "formula library hash bound twice")
    add("I099-10", permit["contract_sha256"] == sha256(CONTRACT), "contract hash bound")
    add("I099-11", config["expected_models"] == 58 and config["expected_values"] == 348, "58x6 exact scope")
    add("I099-12", permit["expected_models"] == 58 and permit["expected_values"] == 348 and permit["output_roster"] == OUTPUTS, "permit exact scope")
    add("I099-13", permit["new_mask_cap"] == 0 and all(v == 0 for v in permit["locks"].values()), "zero new mask and all locks")
    add("I099-14", valid.returncode == 0 and valid_payload.get("permit_valid") is True and valid_payload.get("source_mask_cells_verified") == "58/58", "valid-permit doctor passes")
    add("I099-15", no_permit.returncode != 0 and not (FACTORY / "intermediate").exists(), "run-cell fails closed and creates nothing")
    add("I099-16", len(mutations) == 10 and mutations.rejected.astype(bool).all(), "10/10 permit mutations rejected")
    add("I099-17", decision.iloc[0].decision == "ISSUE_EXACT_HASH_PRM100_PERMIT_NO_EXECUTION" and not bool(decision.iloc[0].execution_performed), "issue permit without execution")
    add("I099-18", not (TABLES / "PRM099_third_wave_full58_six_values_long.csv").exists(), "no full58 result table")
    add("I099-19", all(token in code for token in ["partial merge blocked", "competing Python process", "permit mismatch"]), "fail-closed guards present")
    add("I099-20", all(token not in code for token in ["read_excel(", "RandomForest", "train_test_split", ".fit("]), "no Excel/training route")
    frame = pd.DataFrame(checks)
    frame.to_csv(REPORTS / "PRM099_independent_permit_QA.csv", index=False, encoding="utf-8-sig")
    summary = {"status": "PASS" if frame.status.eq("PASS").all() else "FAIL", "checks": f"{int(frame.status.eq('PASS').sum())}/{len(frame)}", "asset_hashes": f"{int(replay_df.status.eq('PASS').sum())}/{len(replay_df)}", "parent_parity": f"{int(parity_replay_df.status.eq('PASS').sum())}/{len(parity_replay_df)}", "overlap_replay": f"{int(relation_df.status.eq('PASS').sum())}/{len(relation_df)}", "execution_performed": False}
    (REPORTS / "PRM099_independent_permit_QA_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if summary["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
