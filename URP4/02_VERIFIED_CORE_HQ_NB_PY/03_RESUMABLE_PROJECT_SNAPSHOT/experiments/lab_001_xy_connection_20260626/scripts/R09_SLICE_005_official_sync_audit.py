"""Verify global PRM-046 index/status synchronization after control merge."""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

import T3P_mesh_native_grouped_evaluation_preregistration_no_fit as protected_engine


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
FACTORY = LAB / "factories" / "R09-SLICE-005"
REPORTS = FACTORY / "reports"
KST = timezone(timedelta(hours=9))
VAULT = Path("G:/내 드라이브/Obsidian/Nexus_vault")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def manifest_ok(path: Path) -> bool:
    frame = pd.read_csv(path, dtype=str, keep_default_na=False)
    return all((ROOT/r.path).is_file() and str((ROOT/r.path).stat().st_size) == r.bytes and sha(ROOT/r.path) == r.sha256
               for r in frame.itertuples(index=False))


def main() -> None:
    if platform.python_version() != "3.12.12" or "KMK312" not in sys.executable:
        raise RuntimeError("KMK312 Python 3.12.12 required")
    runlog = read(LAB/"runlog.md")
    decisions = read(LAB/"decision_log.md")
    labchg = read(LAB/"changelog.md")
    chg = read(ROOT/"outputs"/"URP4-1_CHANGELOG.md")
    roadlog = read(ROOT/"outputs"/"URP4-1_ROADMAP_LOG.md")
    roadmap = read(ROOT/"outputs"/"URP4-1_ROADMAP.md")
    start = read(ROOT/"AI_START_HERE.md")
    bb = read(LAB/"results"/"R09_blackbox_decision_register_20260703.md")
    obs = read(VAULT/"50_Projects"/"URP4-1.md")
    todo = read(VAULT/"40_Devices"/"✅ TODO.md")
    dashboard = read(VAULT/"50_Projects"/"📊 Projects Dashboard.md")
    contract = json.loads(read(FACTORY/"contracts"/"R09-SLICE-005_STRICT_CONVERGENCE_PREREGISTRATION_NOEXEC_20260721.json"))
    control = json.loads(read(REPORTS/"R09-SLICE-005_control_summary_20260721.json"))
    protected = protected_engine.protected_post()
    checks = [
        ("SYNC-001", "RUN-193 unique", runlog.count("## RUN-193 |") == 1),
        ("SYNC-002", "DEC-225 unique", decisions.count("## DEC-225 |") == 1),
        ("SYNC-003", "LAB-CHG-184 unique", labchg.count("## LAB-CHG-184 |") == 1),
        ("SYNC-004", "CHG-212 unique", chg.count("## CHG-212 |") == 1),
        ("SYNC-005", "BB-667 unique", bb.count("## R09-BB-667 |") == 1),
        ("SYNC-006", "BB-668 unique", bb.count("## R09-BB-668 |") == 1),
        ("SYNC-007", "BB-669 unique", bb.count("## R09-BB-669 |") == 1),
        ("SYNC-008", "BB-670 unique", bb.count("## R09-BB-670 |") == 1),
        ("SYNC-009", "BB-671 unique", bb.count("## R09-BB-671 |") == 1),
        ("SYNC-010", "BB-672 unique", bb.count("## R09-BB-672 |") == 1),
        ("SYNC-011", "BB-673 unique", bb.count("## R09-BB-673 |") == 1),
        ("SYNC-012", "BB-674 unique", bb.count("## R09-BB-674 |") == 1),
        ("SYNC-013", "roadmap log points PRM046", "R09-20260721-SLICE-005" in roadlog and "PRM-046 / RUN-193" in roadlog),
        ("SYNC-014", "roadmap current pointer", "STRICT convergence preregistered / 2026-07-21" in roadmap),
        ("SYNC-015", "AI latest handoff", "AUTHORITATIVE LATEST HANDOFF — R09-SLICE-005" in start),
        ("SYNC-016", "AI indices", "PRM-046 / RUN-193 / DEC-225 / CHG-212 / LAB-CHG-184 / R09-BB-667~674" in start),
        ("SYNC-017", "Obsidian current override", "STRICT convergence preregistered, execution locked" in obs),
        ("SYNC-018", "Obsidian log 010", "LOG-20260721-010" in obs),
        ("SYNC-019", "TODO prereg completed", "[x] **TODO-20260721-URP4-1-STRICT-SLICE-DOE-RUN139-RECONCILIATION-PREREG**" in todo),
        ("SYNC-020", "TODO execution pending", "[ ] **TODO-20260721-URP4-1-STRICT-SLICE-005-CANARY-AND-LABPC-EXECUTION**" in todo),
        ("SYNC-021", "dashboard current", "STRICT PRM-046 merged" in dashboard),
        ("SYNC-022", "contract execution locked", contract["execution_authorized"] is False),
        ("SYNC-023", "control status narrow", control["status"] == "approved_preregistration_only"),
        ("SYNC-024", "no runtime directory", not (FACTORY/"runtime").exists()),
        ("SYNC-025", "prereg manifest intact", manifest_ok(FACTORY/"merge"/"R09-SLICE-005_preregistration_manifest_20260721.csv")),
        ("SYNC-026", "independent manifest intact", manifest_ok(FACTORY/"merge"/"R09-SLICE-005_independent_QA_manifest_20260721.csv")),
        ("SYNC-027", "control manifest intact before packet update", manifest_ok(FACTORY/"merge"/"R09-SLICE-005_control_manifest_20260721.csv")),
        ("SYNC-028", "protected assets 29/29", len(protected) == 29 and protected.status.isin(["pass","pass_with_alias_lock"]).all()),
        ("SYNC-029", "no execution in control", control["execution_detected"] is False and control["excel_reads"] == 0 and control["target_reads"] == 0),
        ("SYNC-030", "next action canary first", "B3 duplicated coarse canary" in control["next"]),
    ]
    frame = pd.DataFrame(checks, columns=["gate_id","gate","passed"])
    path = REPORTS/"R09-SLICE-005_official_sync_QA_20260721.csv"
    frame.to_csv(path, index=False, encoding="utf-8-sig", lineterminator="\n")
    if not frame.passed.all():
        raise RuntimeError(f"sync audit failed: {frame.loc[~frame.passed,'gate_id'].tolist()}")
    payload = {"run_id":"R09-SLICE-005-OFFICIAL-SYNC-001", "created_at_kst":datetime.now(KST).isoformat(timespec="seconds"),
               "runtime":f"KMK312 / Python {platform.python_version()}", "status":"passed",
               "qa":f"{int(frame.passed.sum())}/{len(frame)}", "indices":"PRM-046/RUN-193/DEC-225/CHG-212/LAB-CHG-184/R09-BB-667~674",
               "protected_assets":"29/29", "execution_authorized":False}
    summary = REPORTS/"R09-SLICE-005_official_sync_summary_20260721.json"
    summary.write_text(json.dumps(payload, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
