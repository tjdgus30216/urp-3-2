from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pandas as pd
import psutil


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
FACTORY = LAB / "factories" / "PRM-100"
TABLES = LAB / "reports" / "tables"
REPORTS = FACTORY / "reports"
MANIFEST = REPORTS / "PRM100_output_manifest.csv"
VAULT = Path(r"G:\내 드라이브\Obsidian\Nexus_vault")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    checks: list[dict[str, object]] = []

    def add(check_id: str, ok: bool, observed: object, expected: object) -> None:
        checks.append({"check_id": check_id, "status": "PASS" if ok else "FAIL", "observed": observed, "expected": expected})

    execution = json.loads((REPORTS / "PRM100_execution_summary.json").read_text(encoding="utf-8"))
    technical = json.loads((REPORTS / "PRM100_technical_review_summary.json").read_text(encoding="utf-8"))
    independent_summary = json.loads((REPORTS / "PRM100_independent_QA_summary.json").read_text(encoding="utf-8"))
    ledger = pd.read_csv(REPORTS / "PRM100_execution_ledger.csv")
    producer = pd.read_csv(REPORTS / "PRM100_producer_QA.csv")
    independent = pd.read_csv(REPORTS / "PRM100_independent_QA.csv")
    long = pd.read_csv(TABLES / "PRM099_third_wave_full58_six_values_long.csv")
    wide = pd.read_csv(TABLES / "PRM099_third_wave_full58_six_values_wide.csv")
    coverage = pd.read_csv(TABLES / "PRM100_full58_coverage_variation.csv")
    parent = pd.read_csv(TABLES / "PRM100_X019_full58_parent_lineage_replay.csv")
    ect = pd.read_csv(TABLES / "PRM100_X024_final_chi_lineage_replay.csv")
    cross = pd.read_csv(TABLES / "PRM100_full58_vs_XREG_redundancy.csv")
    internal = pd.read_csv(TABLES / "PRM100_internal_six_redundancy.csv")
    difficult = pd.read_csv(TABLES / "PRM100_difficult_pair_diagnostic.csv")
    attempts = pd.read_csv(REPORTS / "PRM100_attempt_ledger.csv")
    manifest = pd.read_csv(MANIFEST)

    add("Q01_execution_summary", execution.get("status") == "PASS" and execution.get("completed") == "58/58", execution.get("completed"), "58/58")
    add("Q02_atomic_ledger", len(ledger) == 58 and ledger.status.eq("passed").all() and ledger.output_count.eq(6).all(), f"{len(ledger)} rows", "58 passed x6")
    add("Q03_merge_long", len(long) == 348 and long.model_id.nunique() == 58 and long.candidate_id.nunique() == 6 and long.value.notna().all(), f"{len(long)} rows", "348 finite")
    add("Q04_merge_wide", wide.shape == (58, 7) and wide.iloc[:, 1:].notna().all().all(), str(wide.shape), "(58, 7) finite")
    add("Q05_producer", len(producer) == 12 and producer.status.eq("PASS").all() and technical.get("checks") == "12/12", technical.get("checks"), "12/12")
    add("Q06_independent", len(independent) == 14 and independent.status.eq("PASS").all() and independent_summary.get("checks") == "14/14", independent_summary.get("checks"), "14/14")
    add("Q07_parent_lineage", len(parent) == 232 and parent.status.eq("PASS").all(), len(parent), "232 PASS")
    add("Q08_ect_lineage", len(ect) == 58 and ect.status.eq("PASS").all(), len(ect), "58 PASS")
    add("Q09_coverage", len(coverage) == 6 and coverage.finite_count.eq(58).all() and coverage.technical_state.eq("full58_xonly_unselected").all(), len(coverage), "6 full58 candidates")
    cross_counts = cross.relation.value_counts().to_dict()
    add("Q10_crossbank_scope", len(cross) == 648, len(cross), 648)
    add("Q11_crossbank_high", cross_counts.get("high_redundancy", 0) == 2, cross_counts.get("high_redundancy", 0), 2)
    add("Q12_crossbank_no_exact_prop", cross_counts.get("exact_duplicate", 0) == 0 and cross_counts.get("proportional_duplicate", 0) == 0, {k: cross_counts.get(k, 0) for k in ["exact_duplicate", "proportional_duplicate"]}, "0/0")
    add("Q13_internal_scope", len(internal) == 15 and not internal.relation.isin(["exact_duplicate", "proportional_duplicate", "high_redundancy"]).any(), len(internal), "15 with no block relation")
    add("Q14_difficult_pairs", len(difficult) == 12 and difficult.pair_id.nunique() == 2, f"{len(difficult)} rows/{difficult.pair_id.nunique()} pairs", "12/2")
    x019 = difficult[difficult.candidate_id.str.startswith("LIT-X019")]
    add("Q15_x019_pair_ties", x019.absolute_delta.eq(0).all(), int(x019.absolute_delta.eq(0).sum()), "8")
    add("Q16_attempt_ledger", len(attempts) == 4 and attempts.scientific_change.astype(str).str.lower().eq("false").all(), len(attempts), "4 non-scientific attempts")
    report = LAB / "results" / "R09-20260723-PRM100_THIRD_WAVE_FULL58_V128_SIX_OUTPUT_EXECUTION_AND_XONLY_REVIEW.md"
    figure = LAB / "reports" / "figures" / "PRM100_full58_xonly_review.png"
    add("Q17_report_figure", report.exists() and figure.exists() and figure.stat().st_size > 10000, figure.stat().st_size if figure.exists() else 0, ">10000")
    bad = [r.path for r in manifest.itertuples(index=False) if not (ROOT / r.path).exists() or digest(ROOT / r.path) != r.sha256]
    add("Q18_manifest", not bad, len(manifest) - len(bad), len(manifest))
    official = {
        ROOT / "AI_START_HERE.md": "PRM-100 / RUN-245 / DEC-278 / CHG-265 / LAB-CHG-237",
        ROOT / "outputs" / "URP4-1_ROADMAP.md": "PRM-100 complete",
        ROOT / "outputs" / "URP4-1_ROADMAP_LOG.md": "R09-20260723-PRM100",
        ROOT / "outputs" / "URP4-1_CHANGELOG.md": "CHG-265",
        ROOT / "outputs" / "URP4-1_PROFESSOR_PROJECT_ROADMAP_20260629.md": "11.42 Implementation update",
        LAB / "runlog.md": "RUN-245",
        LAB / "decision_log.md": "DEC-278",
        LAB / "changelog.md": "LAB-CHG-237",
        LAB / "results" / "R09_blackbox_decision_register_20260703.md": "R09-BB-1142",
    }
    for n, (path, token) in enumerate(official.items(), start=19):
        add(f"Q{n:02d}_official", token in path.read_text(encoding="utf-8"), token, token)
    obsidian = {
        VAULT / "50_Projects" / "URP4-1.md": "LOG-20260723-069",
        VAULT / "40_Devices" / "✅ TODO.md": "PRM101-XREG-V03-THIRD-WAVE-CONSOLIDATION-NO-Y",
        VAULT / "50_Projects" / "📊 Projects Dashboard.md": "PRM-100 full58 x-only census PASS",
        VAULT / "50_Projects" / "🧵 Session Ledger" / "SES-20260710-CODEX-002 — URP4-1 descriptor validation control tower.md": "PRM-100 third-wave full58 x-only census",
    }
    for n, (path, token) in enumerate(obsidian.items(), start=28):
        add(f"Q{n:02d}_obsidian", token in path.read_text(encoding="utf-8"), token, token)
    competitors: list[int] = []
    ancestors = {p.pid for p in psutil.Process(os.getpid()).parents()}
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            if proc.pid != os.getpid() and proc.pid not in ancestors and "python" in (proc.info["name"] or "").lower():
                competitors.append(proc.pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    add("Q32_no_competing_python", not competitors, competitors, [])

    out = pd.DataFrame(checks)
    out.to_csv(REPORTS / "PRM100_postmerge_sync_QA.csv", index=False, encoding="utf-8-sig")
    failed = out.loc[out.status.ne("PASS"), "check_id"].tolist()
    final = {"status": "PASS" if not failed else "FAIL", "checks": f"{len(out) - len(failed)}/{len(out)}", "failed": failed, "execution_performed": True, "y_fit_selection_promotion": "0/0/0/0"}
    (REPORTS / "PRM100_postmerge_sync_QA_summary.json").write_text(json.dumps(final, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(final, indent=2))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
