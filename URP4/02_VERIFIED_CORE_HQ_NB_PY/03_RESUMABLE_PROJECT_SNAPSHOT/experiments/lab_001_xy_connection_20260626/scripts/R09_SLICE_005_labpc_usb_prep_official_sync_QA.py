from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import T3P_mesh_native_grouped_evaluation_preregistration_no_fit as protected_engine


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments/lab_001_xy_connection_20260626"
FACTORY = LAB / "factories/R09-SLICE-005"
PACKAGE = ROOT / "outputs/URP4-1_R09_SLICE005_LABPC_FACTORY_USB_20260721"
VAULT = Path(r"G:/내 드라이브/Obsidian/Nexus_vault")
sys.path.insert(0, str(PACKAGE / "factory"))
from R09_SLICE_005_labpc_common import verify_manifest


def contains(path: Path, token: str) -> bool:
    return path.is_file() and token in path.read_text(encoding="utf-8-sig")


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["gate_id", "passed"])
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    manifest_rows, manifest_ok = verify_manifest(PACKAGE, PACKAGE / "PACKAGE_MANIFEST.csv")
    protected = protected_engine.protected_post()
    files = {
        "run": LAB / "runlog.md",
        "dec": LAB / "decision_log.md",
        "labchg": LAB / "changelog.md",
        "chg": ROOT / "outputs/URP4-1_CHANGELOG.md",
        "rlog": ROOT / "outputs/URP4-1_ROADMAP_LOG.md",
        "road": ROOT / "outputs/URP4-1_ROADMAP.md",
        "start": ROOT / "AI_START_HERE.md",
        "bb": LAB / "results/R09_blackbox_decision_register_20260703.md",
        "project": VAULT / "50_Projects/URP4-1.md",
        "todo": VAULT / "40_Devices/✅ TODO.md",
        "dash": VAULT / "50_Projects/📊 Projects Dashboard.md",
        "atlas": VAULT / "50_Projects/Codex Session Atlas.md",
        "ledger": VAULT / "50_Projects/🧵 Session Ledger/SES-20260710-CODEX-002 — URP4-1 descriptor validation control tower.md",
    }
    checks = [
        ("SYNC-001", contains(files["run"], "## RUN-195")),
        ("SYNC-002", contains(files["dec"], "## DEC-227")),
        ("SYNC-003", contains(files["labchg"], "## LAB-CHG-186")),
        ("SYNC-004", contains(files["chg"], "## CHG-214")),
        ("SYNC-005", contains(files["rlog"], "R09-20260721-SLICE-005-LABPC-PREP")),
        ("SYNC-006", contains(files["road"], "LabPC USB factory prepared")),
        ("SYNC-007", contains(files["start"], "PRM-050 / RUN-195")),
        ("SYNC-008", contains(files["bb"], "## R09-BB-684")),
        ("SYNC-009", contains(files["bb"], "## R09-BB-692")),
        ("SYNC-010", contains(files["project"], "LOG-20260721-012")),
        ("SYNC-011", contains(files["todo"], "factory-prep checkpoint")),
        ("SYNC-012", contains(files["dash"], "PRM-050 LabPC USB factory ready")),
        ("SYNC-013", contains(files["atlas"], "LabPC USB factory checkpoint")),
        ("SYNC-014", contains(files["ledger"], "LabPC USB factory preparation")),
        ("SYNC-015", (PACKAGE / "contracts/PRM-050_R09-SLICE-005_LABPC_EXECUTION.json").is_file()),
        ("SYNC-016", (PACKAGE / "config/pending_32_job_matrix.csv").is_file()),
        ("SYNC-017", len(list((PACKAGE / "assets/stl").glob("*.stl"))) == 8),
        ("SYNC-018", len(list((PACKAGE / "baseline").glob("*/tables/descriptor_result.csv"))) == 8),
        ("SYNC-019", len(manifest_rows) == 160),
        ("SYNC-020", manifest_ok),
        ("SYNC-021", len(list((PACKAGE / "preflight").rglob("*.*"))) == 0),
        ("SYNC-022", len(list((PACKAGE / "results").rglob("*.*"))) == 0),
        ("SYNC-023", contains(PACKAGE / "README_FIRST.md", "02_RUN_OR_RESUME_FACTORY.cmd")),
        ("SYNC-024", all((PACKAGE / name).is_file() for name in ["00_DOCTOR_FIRST.cmd", "01_INSTALL_LOCAL_FACTORY.cmd", "02_RUN_OR_RESUME_FACTORY.cmd", "03_CHECK_STATUS_AND_VERIFY.cmd", "04_COLLECT_RESULTS_TO_USB.cmd"])),
        ("SYNC-025", contains(FACTORY / "reports/R09-SLICE-005_LABPC_USB_factory_preparation_QA_20260721.csv", "USBQA-024")),
        ("SYNC-026", contains(LAB / "results/R09-20260721-SLICE-005_LABPC_USB_FACTORY_PREPARATION.md", "actual cells run     0 / 32")),
        ("SYNC-027", contains(FACTORY / "merge/MERGE_PACKET_R09-SLICE-005_LABPC_USB_PREP.md", "ready_for_usb_copy")),
        ("SYNC-028", len(protected) == 29),
        ("SYNC-029", len(protected) == 29 and protected.status.isin(["pass", "pass_with_alias_lock"]).all()),
        ("SYNC-030", contains(files["start"], "actual jobs `0/32`")),
    ]
    rows = [{"gate_id": gate, "passed": bool(passed)} for gate, passed in checks]
    report = FACTORY / "reports/R09-SLICE-005_LABPC_USB_factory_official_sync_QA_20260721.csv"
    write_csv(report, rows)
    summary = {
        "run_id": "R09-SLICE-005-LABPC-USB-PREP-SYNC-001",
        "created_at_kst": datetime.now(timezone(timedelta(hours=9))).isoformat(timespec="seconds"),
        "status": "passed" if all(value for _, value in checks) else "failed",
        "qa": f"{sum(value for _, value in checks)}/{len(checks)}",
        "protected": f"{len(protected)}/29",
        "package_manifest": f"{len(manifest_rows)}/160",
        "actual_cells": "0/32",
        "usb_copy": "pending_no_removable_drive",
    }
    path = FACTORY / "reports/R09-SLICE-005_LABPC_USB_factory_official_sync_summary_20260721.json"
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    if summary["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
