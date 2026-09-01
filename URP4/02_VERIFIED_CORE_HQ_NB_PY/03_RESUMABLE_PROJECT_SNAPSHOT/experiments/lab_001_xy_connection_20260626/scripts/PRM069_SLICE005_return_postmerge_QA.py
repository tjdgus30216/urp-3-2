from __future__ import annotations

import csv
import hashlib
import json
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments/lab_001_xy_connection_20260626"
FACTORY = LAB / "factories/TOUR-C001"
REPORTS = FACTORY / "analysis_factory/reports"
RESULTS = LAB / "results"
KST = timezone(timedelta(hours=9))
ZIP = Path(r"G:\내 드라이브\labfactory\returned_results\R09_SLICE005_LABPC_RESULTS_Legion5_2026-07-22T010629_941+0900.zip")
MANIFEST = ZIP.with_suffix(".manifest.csv")
SHA = "5f68795816fe20151796ac50cbe3f8accf609fa252879c0922105b2b55b26e42"

FILES = {
    "run": LAB / "runlog.md",
    "dec": LAB / "decision_log.md",
    "labchg": LAB / "changelog.md",
    "chg": ROOT / "outputs/URP4-1_CHANGELOG.md",
    "roadlog": ROOT / "outputs/URP4-1_ROADMAP_LOG.md",
    "road": ROOT / "outputs/URP4-1_ROADMAP.md",
    "start": ROOT / "AI_START_HERE.md",
    "prof": ROOT / "outputs/URP4-1_PROFESSOR_PROJECT_ROADMAP_20260629.md",
    "bb": RESULTS / "R09_blackbox_decision_register_20260703.md",
    "obs": Path(r"G:\내 드라이브\Obsidian\Nexus_vault\50_Projects\URP4-1.md"),
    "todo": Path(r"G:\내 드라이브\Obsidian\Nexus_vault\40_Devices\✅ TODO.md"),
    "dash": Path(r"G:\내 드라이브\Obsidian\Nexus_vault\50_Projects\📊 Projects Dashboard.md"),
    "atlas": Path(r"G:\내 드라이브\Obsidian\Nexus_vault\50_Projects\Codex Session Atlas.md"),
    "ledger": Path(r"G:\내 드라이브\Obsidian\Nexus_vault\50_Projects\🧵 Session Ledger\SES-20260710-CODEX-002 — URP4-1 descriptor validation control tower.md"),
}


def text(name: str) -> str:
    return FILES[name].read_text(encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def main() -> None:
    contract = json.loads((FACTORY / "contracts/PRM-069_SLICE005_RETURN_INTAKE_20260722.json").read_text(encoding="utf-8"))
    producer = rows(REPORTS / "PRM069_SLICE005_return_producer_QA.csv")
    readback = rows(REPORTS / "PRM069_SLICE005_return_archive_readback_QA.csv")
    next_actions = rows(REPORTS / "PRM069_SLICE005_return_next_action_contract.csv")
    artifacts = rows(REPORTS / "PRM069_SLICE005_return_artifact_registry.csv")
    dual = rows(LAB / "reports/tables/R09-20260721_dual_track_next_action_queue.csv")
    professor = rows(LAB / "reports/tables/R09-20260721_professor_directive_parallel_action_queue.csv")
    manifest = rows(MANIFEST)[0]
    with zipfile.ZipFile(ZIP) as archive:
        corrupt = archive.testzip()
        summary = json.loads(archive.read("results/reports/verification_summary.json").decode("utf-8"))
        matrix = list(csv.DictReader(archive.read("results/reports/all40_descriptor_scalar_matrix.csv").decode("utf-8-sig").splitlines()))

    qa: list[dict] = []

    def add(qid: str, check: str, observed, expected, passed: bool) -> None:
        qa.append({"qa_id": qid, "check": check, "observed": observed, "expected": expected, "passed": bool(passed)})

    add("PM01", "RUN-214", text("run").count("## RUN-214 |"), 1, text("run").count("## RUN-214 |") == 1)
    add("PM02", "DEC-246", text("dec").count("## DEC-246 |"), 1, text("dec").count("## DEC-246 |") == 1)
    add("PM03", "LAB-CHG-205", text("labchg").count("## LAB-CHG-205 |"), 1, text("labchg").count("## LAB-CHG-205 |") == 1)
    add("PM04", "CHG-233", text("chg").count("## CHG-233 —"), 1, text("chg").count("## CHG-233 —") == 1)
    add("PM05", "roadmap log", text("roadlog").count("## R09-20260722-PRM069 |"), 1, text("roadlog").count("## R09-20260722-PRM069 |") == 1)
    add("PM06", "roadmap pointer", text("road").count("PRM-069 SLICE-005 return technically frozen"), 1, text("road").count("PRM-069 SLICE-005 return technically frozen") == 1)
    add("PM07", "AI_START", text("start").count("PRM-069 SLICE-005 return technically accepted"), 1, text("start").count("PRM-069 SLICE-005 return technically accepted") == 1)
    add("PM08", "professor roadmap", text("prof").count("## 11.11 Implementation update"), 1, text("prof").count("## 11.11 Implementation update") == 1)
    ids = [f"R09-BB-{i}" for i in range(842, 851)]
    add("PM09", "blackbox IDs", sum(text("bb").count(f"## {i} |") for i in ids), 9, all(text("bb").count(f"## {i} |") == 1 for i in ids))
    add("PM10", "contract status", contract["status"], "technical intake pass", contract["status"].startswith("technical_intake_passed"))
    add("PM11", "report", (RESULTS / "R09-20260722-PRM069_SLICE005_RETURN_INTAKE_AUDIT.md").is_file(), True, (RESULTS / "R09-20260722-PRM069_SLICE005_RETURN_INTAKE_AUDIT.md").is_file())
    add("PM12", "artifact rows", len(artifacts), 2, len(artifacts) == 2)
    add("PM13", "producer QA", sum(row["passed"].lower() == "true" for row in producer), 24, len(producer) == 24 and all(row["passed"].lower() == "true" for row in producer))
    add("PM14", "archive readback QA", sum(row["passed"].lower() == "true" for row in readback), 12, len(readback) == 12 and all(row["passed"].lower() == "true" for row in readback))
    add("PM15", "next-action rows", len(next_actions), 3, len(next_actions) == 3)
    add("PM16", "ZIP exists", ZIP.is_file(), True, ZIP.is_file())
    actual_sha = sha256(ZIP)
    add("PM17", "ZIP hash", actual_sha, SHA, actual_sha == SHA)
    add("PM18", "ZIP CRC", corrupt or "none", "none", corrupt is None)
    add("PM19", "manifest hash", manifest["sha256"], SHA, manifest["sha256"] == SHA)
    add("PM20", "summary cells", summary["new_cells_passed"], "32/32", summary["new_cells_passed"] == "32/32")
    add("PM21", "matrix rows", len(matrix), 360, len(matrix) == 360)
    strict3 = next(row for row in dual if row["track_id"] == "STRICT" and row["order"] == "3")
    strict4 = next(row for row in dual if row["track_id"] == "STRICT" and row["order"] == "4")
    nb = next(row for row in dual if row["track_id"] == "NB-DEV")
    add("PM22", "STRICT return status", strict3["status"], "completed_technical_intake", strict3["status"] == "completed_technical_intake")
    add("PM23", "STRICT review status", strict4["status"], "next", strict4["status"] == "next")
    add("PM24", "NB-DEV status", nb["status"], "unblocked_pending_priority", nb["status"] == "unblocked_pending_priority")
    labrun = next(row for row in professor if row["lane"] == "LAB-RUN")
    add("PM25", "professor LAB-RUN", labrun["status"], "completed technical intake", labrun["status"] == "completed_technical_intake_scientific_review_pending")
    add("PM26", "Obsidian project", text("obs").count("### LOG-20260722-031 —"), 1, text("obs").count("### LOG-20260722-031 —") == 1)
    add("PM27", "Obsidian intake TODO", "[x] **TODO-20260722-URP4-1-SLICE005-IMMUTABLE-INTAKE**" in text("todo"), True, "[x] **TODO-20260722-URP4-1-SLICE005-IMMUTABLE-INTAKE**" in text("todo"))
    add("PM28", "Obsidian convergence TODO", text("todo").count("**TODO-20260722-URP4-1-SLICE005-CONVERGENCE-CONTROL-REVIEW**"), 1, text("todo").count("**TODO-20260722-URP4-1-SLICE005-CONVERGENCE-CONTROL-REVIEW**") == 1)
    add("PM29", "Obsidian dashboard", "PRM-069 SLICE return frozen" in text("dash"), True, "PRM-069 SLICE return frozen" in text("dash"))
    add("PM30", "Obsidian Atlas", text("atlas").count("## 2026-07-22 URP4-1 PRM-069 SLICE return checkpoint"), 1, text("atlas").count("## 2026-07-22 URP4-1 PRM-069 SLICE return checkpoint") == 1)
    add("PM31", "Obsidian Ledger", text("ledger").count("## 2026-07-22 checkpoint — PRM-069 SLICE-005 technical return intake"), 1, text("ledger").count("## 2026-07-22 checkpoint — PRM-069 SLICE-005 technical return intake") == 1)
    add("PM32", "scientific boundary", contract["scientific_convergence_decision"], "pending", contract["scientific_convergence_decision"] == "pending" and contract["performance_y_read"] == 0 and contract["model_fit"] == 0)

    output = REPORTS / "PRM069_SLICE005_return_postmerge_sync_QA.csv"
    with output.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["qa_id", "check", "observed", "expected", "passed"])
        writer.writeheader()
        writer.writerows(qa)
    if not all(row["passed"] for row in qa):
        print(json.dumps([row for row in qa if not row["passed"]], indent=2, ensure_ascii=False))
        raise RuntimeError("PRM069 postmerge QA failed")
    summary_out = {
        "run_id": "PRM069-SLICE005-RETURN-POSTMERGE-QA-001",
        "completed_at_kst": datetime.now(KST).isoformat(timespec="seconds"),
        "status": "passed_postmerge_sync_technical_intake_scientific_pending",
        "postmerge_QA": "32/32",
        "indices": "PRM-069/RUN-214/DEC-246/CHG-233/LAB-CHG-205/R09-BB-842~850",
        "next_task": "SLICE005-CONVERGENCE-CONTROL-REVIEW",
    }
    (REPORTS / "PRM069_SLICE005_return_postmerge_sync_QA_summary.json").write_text(json.dumps(summary_out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary_out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
