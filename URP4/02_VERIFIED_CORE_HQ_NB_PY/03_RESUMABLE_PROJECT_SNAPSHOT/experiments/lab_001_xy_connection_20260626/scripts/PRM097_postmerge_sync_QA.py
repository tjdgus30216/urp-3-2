from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
TABLES = LAB / "reports" / "tables"
FACTORY = LAB / "factories" / "PRM-097"
REPORTS = FACTORY / "reports"
OBSIDIAN = Path(r"G:\내 드라이브\Obsidian\Nexus_vault")


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    roster = pd.read_csv(TABLES / "PRM097_candidate_output_schema.csv", dtype=str, keep_default_na=False)
    formulas = pd.read_csv(TABLES / "PRM097_formula_contract_registry.csv", dtype=str, keep_default_na=False)
    fixtures = pd.read_csv(TABLES / "PRM097_synthetic_truth_fixture_registry.csv", dtype=str, keep_default_na=False)
    panel = pd.read_csv(TABLES / "PRM097_representative_panel_scope.csv", dtype=str, keep_default_na=False)
    resolution = pd.read_csv(TABLES / "PRM097_resolution_parameter_panel.csv", dtype=str, keep_default_na=False)
    later = pd.read_csv(TABLES / "PRM097_later_y_gate_preservation.csv", dtype=str, keep_default_na=False)
    contract = json.loads((FACTORY / "contracts" / "PRM-097_THIRD_WAVE_FORMULA_TEST_CONTRACT_20260723.json").read_text(encoding="utf-8"))
    producer = json.loads((REPORTS / "PRM097_producer_summary.json").read_text(encoding="utf-8"))
    independent = json.loads((REPORTS / "PRM097_independent_QA_summary.json").read_text(encoding="utf-8"))
    manifest = pd.read_csv(FACTORY / "manifests" / "PRM097_changed_file_manifest.csv", dtype=str, keep_default_na=False)

    workspace_manifest = manifest.loc[manifest.scope.eq("workspace")]
    external_manifest = manifest.loc[manifest.scope.eq("obsidian_sync")]
    hashes_ok = all((ROOT / r.path).exists() and sha256(ROOT / r.path) == r.sha256 for r in workspace_manifest.itertuples())
    external_ok = all(Path(r.path).exists() and sha256(Path(r.path)) == r.sha256 for r in external_manifest.itertuples())
    docs = {
        "ai": ROOT / "AI_START_HERE.md",
        "roadmap": ROOT / "outputs" / "URP4-1_ROADMAP.md",
        "roadmap_log": ROOT / "outputs" / "URP4-1_ROADMAP_LOG.md",
        "changelog": ROOT / "outputs" / "URP4-1_CHANGELOG.md",
        "professor": ROOT / "outputs" / "URP4-1_PROFESSOR_PROJECT_ROADMAP_20260629.md",
        "run": LAB / "runlog.md",
        "decision": LAB / "decision_log.md",
        "labchg": LAB / "changelog.md",
        "bb": LAB / "results" / "R09_blackbox_decision_register_20260703.md",
        "obs_project": OBSIDIAN / "50_Projects" / "URP4-1.md",
        "obs_todo": OBSIDIAN / "40_Devices" / "✅ TODO.md",
        "obs_dashboard": OBSIDIAN / "50_Projects" / "📊 Projects Dashboard.md",
    }
    d = {k: text(v) for k, v in docs.items()}
    checks = {
        "producer_15_of_15": producer["status"] == "PASS" and producer["checks"] == "15/15",
        "independent_20_of_20": independent["status"] == "PASS" and independent["independent_checks"] == "20/20",
        "negative_10_of_10": independent["negative_fixtures"] == "10/10",
        "six_groups_72_outputs": roster.candidate_group_id.nunique() == 6 and len(roster) == 72,
        "seventeen_formulas": len(formulas) == 17 and formulas.formula_id.is_unique,
        "twenty_two_fixtures": len(fixtures) == 22 and fixtures.fixture_id.is_unique,
        "panel_36_all_false": len(panel) == 36 and panel.execution_authorized.str.lower().eq("false").all(),
        "resolution_24_all_false": len(resolution) == 24 and resolution.execution_authorized.str.lower().eq("false").all(),
        "contract_locks_zero": all(int(v) == 0 for v in contract["locks"].values()),
        "later_y_eight_unopened": len(later) == 8 and later.PRM097_status.eq("preserved_exact_unopened").all(),
        "attempt_history_present": (REPORTS / "PRM097_attempt_ledger.csv").exists() and len(pd.read_csv(REPORTS / "PRM097_attempt_ledger.csv")) == 3,
        "scientific_report_present": (LAB / "results" / "R09-20260723-PRM097_THIRD_WAVE_FORMULA_AND_SYNTHETIC_TRUTH_PREREGISTRATION_NO_EXECUTION.md").exists(),
        "figure_present": (LAB / "reports" / "figures" / "PRM097_third_wave_preregistration_map.png").exists(),
        "run_index_once_or_more": "RUN-242" in d["run"],
        "decision_index": "DEC-275" in d["decision"],
        "change_indices": "CHG-262" in d["changelog"] and "LAB-CHG-234" in d["labchg"],
        "blackbox_range_complete": all(f"R09-BB-{i}" in d["bb"] for i in range(1103, 1114)),
        "roadmap_and_handoff_synced": "PRM-097 contracts frozen" in d["roadmap"] and "PRM-098_BOUNDED" in d["ai"],
        "professor_roadmap_synced": "11.39 Implementation update — PRM-097" in d["professor"],
        "obsidian_project_synced": "LOG-20260723-066" in d["obs_project"],
        "obsidian_todo_synced": "PRM098-BOUNDED-THIRD-WAVE" in d["obs_todo"],
        "obsidian_dashboard_synced": "PRM-097 contracts frozen" in d["obs_dashboard"],
        "manifest_workspace_hashes": hashes_ok,
        "manifest_obsidian_hashes": external_ok,
        "no_candidate_execution_artifact": not any(FACTORY.rglob("*candidate_matrix*")) and not any(FACTORY.rglob("*model_result*")),
        "next_work_exact": contract["next_work"] == "PRM-098_BOUNDED_THIRD_WAVE_SYNTHETIC_TRUTH_COST_CANARY_AND_REPRESENTATIVE_PANEL",
    }
    qa = pd.DataFrame([{"check_id": f"PM-{i:02d}", "check": k, "status": "PASS" if v else "FAIL"} for i, (k, v) in enumerate(checks.items(), 1)])
    qa.to_csv(REPORTS / "PRM097_postmerge_sync_QA.csv", index=False, encoding="utf-8-sig", lineterminator="\n")
    summary = {"status": "PASS" if qa.status.eq("PASS").all() else "FAIL", "checks": f"{qa.status.eq('PASS').sum()}/{len(qa)}"}
    (REPORTS / "PRM097_postmerge_sync_QA_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary))
    if summary["status"] != "PASS":
        print(qa.loc[qa.status.eq("FAIL")].to_string(index=False))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
