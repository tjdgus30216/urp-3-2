from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pandas as pd
import psutil


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
FACTORY = LAB / "factories" / "PRM-099"
TABLES = LAB / "reports" / "tables"
REPORTS = FACTORY / "reports"
MANIFEST = REPORTS / "PRM099_output_manifest.csv"
CONFIG = FACTORY / "contracts" / "PRM099_FULL58_SIX_OUTPUT_CONFIG_20260723.json"
CONTRACT = FACTORY / "contracts" / "PRM-099_FULL58_PERMIT_DECISION_CONTRACT_20260723.json"
PERMIT = FACTORY / "authorizations" / "PRM-100_THIRD_WAVE_FULL58_V128_EXECUTION_PERMIT_20260723.json"
RUNNER = LAB / "scripts" / "PRM099_third_wave_full58_runner.py"
VAULT = Path(r"G:\내 드라이브\Obsidian\Nexus_vault")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def main() -> None:
    checks = []
    def add(i: str, ok: bool, observed: object, expected: object) -> None:
        checks.append({"check_id": i, "status": "PASS" if ok else "FAIL", "observed": observed, "expected": expected})

    summary = json.loads((REPORTS / "PRM099_permit_decision_summary.json").read_text(encoding="utf-8"))
    independent_summary = json.loads((REPORTS / "PRM099_independent_permit_QA_summary.json").read_text(encoding="utf-8"))
    review = pd.read_csv(REPORTS / "PRM099_permit_review_QA.csv")
    independent = pd.read_csv(REPORTS / "PRM099_independent_permit_QA.csv")
    assets = pd.read_csv(TABLES / "PRM099_full58_V128_asset_registry.csv")
    parity = pd.read_csv(TABLES / "PRM099_X019_parent_lineage_panel_parity.csv")
    overlap = pd.read_csv(TABLES / "PRM099_six_output_vs_XREG_v0_2_panel_overlap.csv")
    mutations = pd.read_csv(TABLES / "PRM099_permit_mutation_tests.csv")
    scope = pd.read_csv(TABLES / "PRM099_returned_six_output_scope.csv")
    attempts = pd.read_csv(REPORTS / "PRM099_attempt_ledger.csv")
    manifest = pd.read_csv(MANIFEST)
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    permit = json.loads(PERMIT.read_text(encoding="utf-8"))

    add("Q01_summary", summary.get("status") == "PASS", summary.get("status"), "PASS")
    add("Q02_review", len(review) == 12 and review.status.eq("PASS").all(), len(review), "12 PASS")
    add("Q03_mutations", len(mutations) == 10 and mutations.rejected.astype(str).str.lower().eq("true").all(), len(mutations), "10 rejected")
    add("Q04_independent", len(independent) == 20 and independent.status.eq("PASS").all(), len(independent), "20 PASS")
    add("Q05_independent_summary", independent_summary.get("checks") == "20/20", independent_summary.get("checks"), "20/20")
    add("Q06_assets", len(assets) == 58 and assets.hash_pass.astype(str).str.lower().eq("true").all(), len(assets), "58 hash-pass")
    add("Q07_parity", len(parity) == 24 and parity.status.eq("PASS").all(), len(parity), "24 PASS")
    add("Q08_overlap", len(overlap) == 648, len(overlap), 648)
    add("Q09_high_flags", overlap.relation.eq("high_redundancy_small_panel").sum() == 10, int(overlap.relation.eq("high_redundancy_small_panel").sum()), 10)
    add("Q10_scope", len(scope) == 6 and scope.active_feature.astype(str).str.lower().eq("false").all(), len(scope), "6 inactive")
    add("Q11_config", config["expected_models"] == 58 and config["expected_values"] == 348, [config["expected_models"], config["expected_values"]], [58, 348])
    add("Q12_permit_hashes", permit["runner_sha256"] == digest(RUNNER) and permit["config_sha256"] == digest(CONFIG) and permit["contract_sha256"] == digest(CONTRACT), "live", "exact")
    add("Q13_locks", permit["new_mask_cap"] == 0 and all(v == 0 for v in permit["locks"].values()), permit["locks"], "all zero")
    doctor = subprocess.run([sys.executable, str(RUNNER), "doctor", "--config", str(CONFIG), "--contract", str(CONTRACT), "--permit", str(PERMIT)], capture_output=True, text=True, check=False)
    payload = json.loads(doctor.stdout) if doctor.returncode == 0 else {}
    add("Q14_live_doctor", doctor.returncode == 0 and payload.get("permit_valid") is True and payload.get("source_mask_cells_verified") == "58/58", payload.get("status"), "PASS")
    add("Q15_no_intermediate", not (FACTORY / "intermediate").exists(), (FACTORY / "intermediate").exists(), False)
    result_tables = [TABLES / "PRM099_third_wave_full58_six_values_long.csv", TABLES / "PRM099_third_wave_full58_six_values_wide.csv"]
    add("Q16_no_results", not any(p.exists() for p in result_tables), [p.exists() for p in result_tables], [False, False])
    add("Q17_attempts", len(attempts) == 5, len(attempts), 5)
    bad = [r.path for r in manifest.itertuples(index=False) if not (ROOT / r.path).exists() or digest(ROOT / r.path) != r.sha256]
    add("Q18_manifest", not bad, len(manifest) - len(bad), len(manifest))

    official = {
        ROOT / "AI_START_HERE.md": "PRM-099 / RUN-244 / DEC-277 / CHG-264 / LAB-CHG-236",
        ROOT / "outputs" / "URP4-1_ROADMAP.md": "PRM-099 exact-hash permit issued",
        ROOT / "outputs" / "URP4-1_ROADMAP_LOG.md": "R09-20260723-PRM099",
        ROOT / "outputs" / "URP4-1_CHANGELOG.md": "CHG-264",
        ROOT / "outputs" / "URP4-1_PROFESSOR_PROJECT_ROADMAP_20260629.md": "11.41 Implementation update",
        LAB / "runlog.md": "RUN-244", LAB / "decision_log.md": "DEC-277", LAB / "changelog.md": "LAB-CHG-236",
        LAB / "results" / "R09_blackbox_decision_register_20260703.md": "R09-BB-1133",
    }
    for n, (path, token) in enumerate(official.items(), start=19):
        add(f"Q{n:02d}_official", token in path.read_text(encoding="utf-8"), token, token)

    obs = {
        VAULT / "50_Projects" / "URP4-1.md": "LOG-20260723-068",
        VAULT / "40_Devices" / "✅ TODO.md": "PRM100-THIRD-WAVE-FULL58-SIX-OUTPUT",
        VAULT / "50_Projects" / "📊 Projects Dashboard.md": "PRM-099 exact PRM-100 permit",
        VAULT / "50_Projects" / "🧵 Session Ledger" / "SES-20260710-CODEX-002 — URP4-1 descriptor validation control tower.md": "PRM-099 exact-hash full58 permit issued",
    }
    start = 28
    for n, (path, token) in enumerate(obs.items(), start=start):
        add(f"Q{n:02d}_obsidian", token in path.read_text(encoding="utf-8"), token, token)
    report = LAB / "results" / "R09-20260723-PRM099_THIRD_WAVE_TECHNICAL_RETURN_AND_FULL58_PERMIT_DECISION_NO_Y.md"
    fig = LAB / "reports" / "figures" / "PRM099_full58_permit_decision.png"
    add("Q32_report_figure", report.exists() and fig.exists() and fig.stat().st_size > 10000, fig.stat().st_size if fig.exists() else 0, ">10000")
    competitors = []
    ancestors = {p.pid for p in psutil.Process(os.getpid()).parents()}
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            if proc.pid != os.getpid() and proc.pid not in ancestors and "python" in (proc.info["name"] or "").lower():
                competitors.append(proc.pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    add("Q33_no_competing_python", not competitors, competitors, [])

    out = pd.DataFrame(checks)
    out.to_csv(REPORTS / "PRM099_postmerge_sync_QA.csv", index=False, encoding="utf-8-sig")
    failed = out.loc[out.status.ne("PASS"), "check_id"].tolist()
    final = {"status": "PASS" if not failed else "FAIL", "checks": f"{len(out)-len(failed)}/{len(out)}", "failed": failed, "permit_valid": payload.get("permit_valid", False), "execution_performed": False}
    (REPORTS / "PRM099_postmerge_sync_QA_summary.json").write_text(json.dumps(final, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(final, indent=2))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
