from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pandas as pd
import psutil


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
FACTORY = LAB / "factories" / "PRM-098"
TABLES = LAB / "reports" / "tables"
OUT = FACTORY / "reports" / "PRM098_postmerge_sync_QA.csv"
SUMMARY = FACTORY / "reports" / "PRM098_postmerge_sync_QA_summary.json"
MANIFEST = FACTORY / "reports" / "PRM098_output_manifest.csv"
VAULT = Path(r"G:\내 드라이브\Obsidian\Nexus_vault")


EXPECTED = {
    "LIT-X019::solid_void_chord_q50_geomean_ratio",
    "LIT-X019::solid_void_chord_x_q50_ratio",
    "LIT-X019::solid_void_chord_y_q50_ratio",
    "LIT-X019::solid_void_chord_z_q50_ratio",
    "LIT-X024::ect_abs_auc_direction_mean_per_mm3",
    "LIT-X024::ect_total_variation_direction_mean_per_mm3",
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(check_id: str, ok: bool, observed: object, expected: object) -> None:
        checks.append({"check_id": check_id, "status": "PASS" if ok else "FAIL", "observed": observed, "expected": expected})

    synth = pd.read_csv(FACTORY / "reports" / "PRM098_synthetic_truth_results.csv")
    canary = pd.read_csv(FACTORY / "reports" / "PRM098_V064_cost_canary.csv")
    ledger = pd.read_csv(FACTORY / "reports" / "PRM098_progressive_panel_execution_ledger.csv")
    values = pd.read_csv(FACTORY / "reports" / "PRM098_representative_panel_values_long.csv")
    gates = pd.read_csv(TABLES / "PRM098_output_resolution_gate.csv")
    controls = pd.read_csv(TABLES / "PRM098_analytic_identity_controls.csv")
    lineage = pd.read_csv(FACTORY / "reports" / "PRM098_independent_lineage_replay.csv")
    ect = pd.read_csv(FACTORY / "reports" / "PRM098_independent_ECT_curve_replay.csv")
    independent = pd.read_csv(FACTORY / "reports" / "PRM098_independent_QA.csv")
    attempts = pd.read_csv(FACTORY / "reports" / "PRM098_attempt_ledger.csv")
    sources = pd.read_csv(TABLES / "PRM098_input_mask_source_registry.csv")
    routes = pd.read_csv(TABLES / "PRM098_group_technical_route.csv")
    manifest = pd.read_csv(MANIFEST)

    counts = ledger["status"].value_counts().to_dict()
    likely = set(gates.loc[gates["technical_state"] == "likely_resolution_qualified_not_selected", "candidate_id"])
    technical = gates[(gates["candidate_group_id"] != "LIT-X028") & (gates["technical_state"] != "diagnostic_or_negative_control_only")]

    check("Q01_synthetic_22", len(synth) == 22 and (synth["status"] == "PASS").all(), len(synth), "22 PASS")
    check("Q02_canary_6", len(canary) == 6 and (canary["status"] == "passed").all(), len(canary), "6 passed")
    check("Q03_panel_144", len(ledger) == 144, len(ledger), 144)
    check("Q04_panel_status", counts == {"passed": 139, "not_run_group_hold": 4, "timeout": 1}, counts, "139/4/1")
    check("Q05_panel_values", len(values) == 1658, len(values), 1658)
    check("Q06_technical_37", len(technical) == 37, len(technical), 37)
    check("Q07_likely_exact_six", likely == EXPECTED, sorted(likely), sorted(EXPECTED))
    check("Q08_analytic_204", len(controls) == 204 and (controls["status"] == "PASS").all(), len(controls), "204 PASS")
    check("Q09_lineage_60", len(lineage) == 60 and (lineage["status"] == "PASS").all(), len(lineage), "60 PASS")
    ect_points = int(ect["curve_points"].sum())
    check("Q10_ECT_10062", len(ect) == 3 and ect_points == 10062 and (ect["status"] == "PASS").all(), ect_points, "10062 PASS")
    check("Q11_independent_22", len(independent) == 22 and (independent["status"] == "PASS").all(), len(independent), "22 PASS")
    check("Q12_attempts_8", len(attempts) == 8, len(attempts), 8)
    check("Q13_sources_24", len(sources) == 24 and sources["hash_pass"].astype(bool).all(), len(sources), "24 hash-pass")
    check("Q14_routes_6", len(routes) == 6, len(routes), 6)

    bad_manifest = []
    for row in manifest.itertuples(index=False):
        p = ROOT / row.path
        if not p.exists() or digest(p) != row.sha256:
            bad_manifest.append(row.path)
    check("Q15_manifest_hashes", not bad_manifest, len(manifest) - len(bad_manifest), f"{len(manifest)} hash matches")

    official = {
        "AI_START_HERE": ROOT / "AI_START_HERE.md",
        "ROADMAP": ROOT / "outputs" / "URP4-1_ROADMAP.md",
        "ROADMAP_LOG": ROOT / "outputs" / "URP4-1_ROADMAP_LOG.md",
        "CHANGELOG": ROOT / "outputs" / "URP4-1_CHANGELOG.md",
        "PROFESSOR": ROOT / "outputs" / "URP4-1_PROFESSOR_PROJECT_ROADMAP_20260629.md",
        "RUNLOG": LAB / "runlog.md",
        "DECISION": LAB / "decision_log.md",
        "LAB_CHANGELOG": LAB / "changelog.md",
        "BLACKBOX": LAB / "results" / "R09_blackbox_decision_register_20260703.md",
    }
    tokens = {
        "AI_START_HERE": "PRM-098 / RUN-243 / DEC-276 / CHG-263 / LAB-CHG-235",
        "ROADMAP": "PRM-098 bounded panel returned",
        "ROADMAP_LOG": "R09-20260723-PRM098",
        "CHANGELOG": "CHG-263",
        "PROFESSOR": "11.40 Implementation update",
        "RUNLOG": "RUN-243",
        "DECISION": "DEC-276",
        "LAB_CHANGELOG": "LAB-CHG-235",
        "BLACKBOX": "R09-BB-1126",
    }
    for name, path in official.items():
        text = path.read_text(encoding="utf-8")
        check(f"Q_official_{name}", tokens[name] in text, tokens[name] if tokens[name] in text else "missing", tokens[name])

    obsidian = {
        "PROJECT": VAULT / "50_Projects" / "URP4-1.md",
        "TODO": VAULT / "40_Devices" / "✅ TODO.md",
        "DASHBOARD": VAULT / "50_Projects" / "📊 Projects Dashboard.md",
        "SESSION": VAULT / "50_Projects" / "🧵 Session Ledger" / "SES-20260710-CODEX-002 — URP4-1 descriptor validation control tower.md",
    }
    obs_tokens = {"PROJECT": "LOG-20260723-067", "TODO": "PRM099-THIRD-WAVE-FULL58-PERMIT", "DASHBOARD": "PRM-098 bounded panel", "SESSION": "PRM-098 bounded third-wave review"}
    for name, path in obsidian.items():
        text = path.read_text(encoding="utf-8")
        check(f"Q_obsidian_{name}", obs_tokens[name] in text, obs_tokens[name] if obs_tokens[name] in text else "missing", obs_tokens[name])

    report = LAB / "results" / "R09-20260723-PRM098_BOUNDED_THIRD_WAVE_SYNTHETIC_COST_PANEL.md"
    figure = LAB / "reports" / "figures" / "PRM098_third_wave_bounded_gate.png"
    check("Q29_report_figure", report.exists() and figure.exists() and figure.stat().st_size > 10000, figure.stat().st_size if figure.exists() else 0, ">10000")
    report_text = report.read_text(encoding="utf-8")
    check("Q30_claim_locks", all(t in report_text for t in ["no evidence", "unselected", "full-58 expansion"]), "claim boundary present", "claim boundary present")

    competitors = []
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            name = (proc.info["name"] or "").lower()
            if "python" in name and proc.info["pid"] != os.getpid():
                competitors.append({"pid": proc.info["pid"], "name": proc.info["name"], "cmdline": proc.info["cmdline"]})
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    check("Q31_competing_python", len(competitors) == 0, competitors, [])

    OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(checks).to_csv(OUT, index=False, encoding="utf-8-sig")
    failed = [r["check_id"] for r in checks if r["status"] != "PASS"]
    SUMMARY.write_text(json.dumps({"status": "PASS" if not failed else "FAIL", "checks": f"{len(checks)-len(failed)}/{len(checks)}", "failed": failed}, indent=2), encoding="utf-8")
    print(SUMMARY.read_text(encoding="utf-8"))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
