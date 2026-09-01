from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import T3P_mesh_native_grouped_evaluation_preregistration_no_fit as protected_engine


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments/lab_001_xy_connection_20260626"
FACTORY = LAB / "factories/R09-SLICE-005"
REPORTS = FACTORY / "reports"
MERGE = FACTORY / "merge"
VAULT = Path(r"G:/내 드라이브/Obsidian/Nexus_vault")


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def contains(path: Path, token: str) -> bool:
    return path.exists() and token in path.read_text(encoding="utf-8-sig")


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def main() -> None:
    execution = json.loads((REPORTS / "R09-SLICE-005_B3_coarse_canary_execution_summary_20260721.json").read_text(encoding="utf-8"))
    independent = json.loads((REPORTS / "R09-SLICE-005_B3_coarse_canary_independent_QA_summary_20260721.json").read_text(encoding="utf-8"))
    control = json.loads((REPORTS / "R09-SLICE-005_B3_coarse_canary_control_summary_20260721.json").read_text(encoding="utf-8"))
    protected = protected_engine.protected_post()

    files = {
        "runlog": LAB / "runlog.md",
        "decision": LAB / "decision_log.md",
        "lab_changelog": LAB / "changelog.md",
        "changelog": ROOT / "outputs/URP4-1_CHANGELOG.md",
        "roadmap_log": ROOT / "outputs/URP4-1_ROADMAP_LOG.md",
        "roadmap": ROOT / "outputs/URP4-1_ROADMAP.md",
        "start": ROOT / "AI_START_HERE.md",
        "blackbox": LAB / "results/R09_blackbox_decision_register_20260703.md",
        "project": VAULT / "50_Projects/URP4-1.md",
        "todo": VAULT / "40_Devices/✅ TODO.md",
        "dashboard": VAULT / "50_Projects/📊 Projects Dashboard.md",
        "atlas": VAULT / "50_Projects/Codex Session Atlas.md",
        "ledger": VAULT / "50_Projects/🧵 Session Ledger/SES-20260710-CODEX-002 — URP4-1 descriptor validation control tower.md",
    }
    checks = [
        ("SYNC-001", contains(files["runlog"], "## RUN-194")),
        ("SYNC-002", contains(files["decision"], "## DEC-226")),
        ("SYNC-003", contains(files["lab_changelog"], "## LAB-CHG-185")),
        ("SYNC-004", contains(files["changelog"], "## CHG-213")),
        ("SYNC-005", contains(files["roadmap_log"], "R09-20260721-SLICE-005-CANARY")),
        ("SYNC-006", contains(files["roadmap"], "B3 STREAMING canary passed")),
        ("SYNC-007", contains(files["start"], "RUN-194")),
        ("SYNC-008", contains(files["blackbox"], "## R09-BB-675")),
        ("SYNC-009", contains(files["blackbox"], "## R09-BB-683")),
        ("SYNC-010", contains(files["project"], "LOG-20260721-011")),
        ("SYNC-011", contains(files["todo"], "RUN-194 / DEC-226")),
        ("SYNC-012", contains(files["dashboard"], "STRICT B3 duplicate canary PASS (RUN-194)")),
        ("SYNC-013", contains(files["atlas"], "R09-SLICE-005 canary checkpoint")),
        ("SYNC-014", contains(files["ledger"], "R09-SLICE-005 B3 duplicate canary")),
        ("SYNC-015", execution["status"] == "passed"),
        ("SYNC-016", independent["status"] == "passed"),
        ("SYNC-017", control["status"] == "passed"),
        ("SYNC-018", control["control_qa"] == "28/28"),
        ("SYNC-019", execution["accepted_attempts"] == ["B3-COARSE-E", "B3-COARSE-F"]),
        ("SYNC-020", execution["quarantined_attempts"] == ["B3-COARSE-A", "B3-COARSE-C"]),
        ("SYNC-021", execution["table_sha_parity"] == "5/5"),
        ("SYNC-022", execution["scalar_parity"] == "9/9"),
        ("SYNC-023", independent["max_abs_delta"] <= 1e-12),
        ("SYNC-024", execution["png_created_deleted_each"] == "1601/1601"),
        ("SYNC-025", execution["readback_mismatch_sum"] == 0),
        ("SYNC-026", control["full_factory_authorized"] is False),
        ("SYNC-027", contains(files["roadmap"], "32 pending cells executed                         0")),
        ("SYNC-028", contains(files["todo"], "TODO stays open") or contains(files["todo"], "TODO stays open.")),
        ("SYNC-029", len(protected) == 29),
        ("SYNC-030", len(protected) == 29 and protected.status.isin(["pass", "pass_with_alias_lock"]).all()),
    ]
    rows = [{"gate_id": gate, "passed": bool(passed)} for gate, passed in checks]
    qa_path = REPORTS / "R09-SLICE-005_B3_coarse_canary_official_sync_QA_20260721.csv"
    write_csv(qa_path, ["gate_id", "passed"], rows)
    passed = all(value for _, value in checks)
    summary = {
        "run_id": "R09-SLICE-005-B3-COARSE-CANARY-OFFICIAL-SYNC-001",
        "created_at_kst": datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds"),
        "status": "passed" if passed else "failed",
        "official_sync_qa": f"{sum(value for _, value in checks)}/{len(checks)}",
        "protected_assets": f"{len(protected)}/29",
        "latest_indices": "PRM-049 / RUN-194 / DEC-226 / CHG-213 / LAB-CHG-185 / R09-BB-675~683",
        "full_factory_authorized": False,
    }
    summary_path = REPORTS / "R09-SLICE-005_B3_coarse_canary_official_sync_summary_20260721.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest_path = MERGE / "R09-SLICE-005_B3_coarse_canary_official_sync_manifest_20260721.csv"
    manifest_files = list(files.values()) + [qa_path, summary_path]
    write_csv(
        manifest_path,
        ["path", "bytes", "sha256"],
        [{"path": rel(path), "bytes": path.stat().st_size, "sha256": sha(path)} for path in manifest_files],
    )
    print(json.dumps(summary, ensure_ascii=False))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
