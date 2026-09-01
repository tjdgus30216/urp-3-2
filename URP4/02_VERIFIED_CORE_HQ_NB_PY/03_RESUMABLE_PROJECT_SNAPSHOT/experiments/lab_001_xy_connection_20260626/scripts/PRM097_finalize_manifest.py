from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
TABLES = LAB / "reports" / "tables"
FACTORY = LAB / "factories" / "PRM-097"
MANIFESTS = FACTORY / "manifests"
REPORTS = FACTORY / "reports"
OBSIDIAN = Path(r"G:\내 드라이브\Obsidian\Nexus_vault")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    MANIFESTS.mkdir(parents=True, exist_ok=True)
    summary = {
        "work_id": "PRM-097",
        "status": "PASS",
        "indices": "RUN-242 / DEC-275 / CHG-262 / LAB-CHG-234 / R09-BB-1103~1113 / LOG-20260723-066",
        "candidate_groups": 6,
        "output_schema_rows": 72,
        "formula_contracts": 17,
        "synthetic_fixtures": 22,
        "representative_panel_cells_not_executed": 36,
        "resolution_rows_not_executed": 24,
        "producer_QA": "15/15",
        "independent_QA": "20/20",
        "negative_fixture_QA": "10/10",
        "candidate_calculation_full58_y_fit_selection_promotion": "0/0/0/0/0/0",
        "next_work": "PRM-098_BOUNDED_THIRD_WAVE_SYNTHETIC_TRUTH_COST_CANARY_AND_REPRESENTATIVE_PANEL",
    }
    summary_path = REPORTS / "PRM097_technical_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    local_files = [
        ROOT / "AI_START_HERE.md",
        ROOT / "outputs" / "URP4-1_ROADMAP.md",
        ROOT / "outputs" / "URP4-1_ROADMAP_LOG.md",
        ROOT / "outputs" / "URP4-1_CHANGELOG.md",
        ROOT / "outputs" / "URP4-1_PROFESSOR_PROJECT_ROADMAP_20260629.md",
        LAB / "runlog.md", LAB / "decision_log.md", LAB / "changelog.md",
        LAB / "results" / "R09_blackbox_decision_register_20260703.md",
        LAB / "results" / "R09-20260723-PRM097_THIRD_WAVE_FORMULA_AND_SYNTHETIC_TRUTH_PREREGISTRATION_NO_EXECUTION.md",
        LAB / "reports" / "figures" / "PRM097_third_wave_preregistration_map.png",
        LAB / "scripts" / "PRM097_freeze_third_wave_formula_contracts.py",
        LAB / "scripts" / "PRM097_independent_QA.py",
        LAB / "scripts" / "PRM097_make_preregistration_figure.py",
        LAB / "scripts" / "PRM097_finalize_manifest.py",
        LAB / "scripts" / "PRM097_postmerge_sync_QA.py",
        FACTORY / "contracts" / "PRM-097_THIRD_WAVE_FORMULA_TEST_CONTRACT_20260723.json",
        summary_path,
    ]
    local_files += sorted(TABLES.glob("PRM097_*.csv"))
    local_files += sorted(REPORTS.glob("PRM097_*.csv"))
    local_files += sorted(REPORTS.glob("PRM097_*.json"))
    external_files = [
        OBSIDIAN / "50_Projects" / "URP4-1.md",
        OBSIDIAN / "40_Devices" / "✅ TODO.md",
        OBSIDIAN / "50_Projects" / "📊 Projects Dashboard.md",
        OBSIDIAN / "50_Projects" / "🧵 Session Ledger" / "SES-20260710-CODEX-002 — URP4-1 descriptor validation control tower.md",
    ]
    unique = []
    seen = set()
    for p in local_files + external_files:
        key = str(p)
        if key not in seen:
            unique.append(p); seen.add(key)
    rows = []
    for p in unique:
        rows.append({
            "path": str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p),
            "exists": p.exists(),
            "size_bytes": p.stat().st_size if p.exists() else -1,
            "sha256": sha256(p) if p.exists() else "",
            "scope": "workspace" if p.is_relative_to(ROOT) else "obsidian_sync",
        })
    out = pd.DataFrame(rows).sort_values(["scope", "path"])
    out.to_csv(MANIFESTS / "PRM097_changed_file_manifest.csv", index=False, encoding="utf-8-sig", lineterminator="\n")
    print(json.dumps({"manifest_rows": len(out), "existing": int(out.exists.sum())}))


if __name__ == "__main__":
    main()
