from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
REPORTS = LAB / "factories" / "TOUR-C001" / "analysis_factory" / "reports"
FIGURES = LAB / "factories" / "TOUR-C001" / "analysis_factory" / "figures"
OUT = LAB / "reports" / "tables"
OBSIDIAN = Path(r"G:\내 드라이브\Obsidian\Nexus_vault")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


checks: list[tuple[str, bool, str]] = []


def check(check_id: str, condition: bool, evidence: str) -> None:
    checks.append((check_id, bool(condition), evidence))


summary = json.loads(read(REPORTS / "PRM070_SLICE005_summary.json"))
independent = json.loads(read(REPORTS / "PRM070_SLICE005_independent_control_summary.json"))
policy = csv_rows(REPORTS / "PRM070_SLICE005_descriptor_reference_policy.csv")

check("Q01", summary["status"] == "passed_y_blind_convergence_review", "main status")
check("Q02", summary["decision"] == "retain_reference_for_supported_descriptors_only", "main decision")
check("Q03", summary["reference_config"] == "CFG-P1000-S0801", "reference config")
check("Q04", summary["descriptor_reference_retained"] == 8, "8 retained")
check("Q05", summary["descriptor_reference_hold"] == 1, "1 held")
check("Q06", summary["performance_y_read"] == 0, "no y read")
check("Q07", summary["model_fit"] == 0, "no fit")
check("Q08", summary["feature_promotion"] == 0, "no promotion")
check("Q09", len(policy) == 9, "9 policy rows")
held = [row for row in policy if row.get("decision") == "reference_hold_for_descriptor"]
check("Q10", len(held) == 1 and held[0].get("scalar_key") == "XRV1-F005::mean", "raw F005 only hold")
check("Q11", independent["status"] == "passed_independent_control", "independent status")
check("Q12", independent["independent_QA"] == "24/24", "independent 24/24")
check("Q13", independent["control_QA"] == "12/12", "control 12/12")
check("Q14", independent["F005_per_mm_diagnostic"]["status"] == "post_result_exploratory_no_promotion", "F005 diagnostic boundary")
check("Q15", independent["T8_T9_order_breaks"] == 8, "T8/T9 8 breaks")

for offset, name in enumerate(
    [
        "PRM070_SLICE005_fine_SRD_heatmap.png",
        "PRM070_SLICE005_descriptor_convergence_summary.png",
        "PRM070_SLICE005_T8_T9_separation.png",
    ],
    start=16,
):
    path = FIGURES / name
    check(f"Q{offset:02d}", path.is_file() and path.stat().st_size > 0, name)

sync_files = {
    "run": LAB / "runlog.md",
    "decision": LAB / "decision_log.md",
    "lab_chg": LAB / "changelog.md",
    "chg": ROOT / "outputs" / "URP4-1_CHANGELOG.md",
    "roadmap_log": ROOT / "outputs" / "URP4-1_ROADMAP_LOG.md",
    "roadmap": ROOT / "outputs" / "URP4-1_ROADMAP.md",
    "ai": ROOT / "AI_START_HERE.md",
    "professor": ROOT / "outputs" / "URP4-1_PROFESSOR_PROJECT_ROADMAP_20260629.md",
    "blackbox": LAB / "results" / "R09_blackbox_decision_register_20260703.md",
    "merge": LAB / "results" / "PRM070_MERGE_PACKET.md",
}

expected = {
    "run": "RUN-215",
    "decision": "DEC-247",
    "lab_chg": "LAB-CHG-206",
    "chg": "CHG-234",
    "roadmap_log": "R09-20260722-PRM070",
    "roadmap": "PRM-070 SLICE convergence review merged",
    "ai": "PRM-070 SLICE convergence policy merged",
    "professor": "11.12 Implementation update",
    "blackbox": "R09-BB-861",
    "merge": "PRM-070 merge packet",
}
for offset, (key, token) in enumerate(expected.items(), start=19):
    check(f"Q{offset:02d}", token in read(sync_files[key]), f"{key}: {token}")

dual = csv_rows(LAB / "reports" / "tables" / "R09-20260721_dual_track_next_action_queue.csv")
prof = csv_rows(LAB / "reports" / "tables" / "R09-20260721_professor_directive_parallel_action_queue.csv")
slice_q = csv_rows(LAB / "reports" / "tables" / "R09-SLICE-005_next_action_queue_20260721.csv")
check("Q29", any(r["track_id"] == "STRICT" and r["order"] == "4" and r["status"] == "completed" for r in dual), "dual STRICT order4 complete")
check("Q30", any(r["track_id"] == "STRICT-F005" and r["status"] == "pending" for r in dual), "dual F005 pending")
check("Q31", any(r["lane"] == "SLICE-CONTROL" and r["status"] == "completed" for r in prof), "professor SLICE control complete")
check("Q32", any(r["lane"] == "SLICE-F005" and r["status"] == "pending" for r in prof), "professor F005 pending")
check("Q33", sum(r["status"] == "completed" for r in slice_q) == 6 and any(r["queue_id"] == "SLICE005-Q07" for r in slice_q), "slice queue reconciled")

obsidian_checks = [
    (OBSIDIAN / "50_Projects" / "URP4-1.md", "LOG-20260722-032"),
    (OBSIDIAN / "40_Devices" / "✅ TODO.md", "TODO-20260722-URP4-1-F005-PER-MM-PREREG"),
    (OBSIDIAN / "50_Projects" / "📊 Projects Dashboard.md", "PRM-070 SLICE convergence"),
]
for offset, (path, token) in enumerate(obsidian_checks, start=34):
    check(f"Q{offset:02d}", path.is_file() and token in read(path), f"Obsidian {token}")

OUT.mkdir(parents=True, exist_ok=True)
qa_path = OUT / "PRM070_SLICE005_postmerge_sync_QA.csv"
with qa_path.open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.writer(handle)
    writer.writerow(["check_id", "status", "evidence"])
    for check_id, passed, evidence in checks:
        writer.writerow([check_id, "PASS" if passed else "FAIL", evidence])

passed = sum(item[1] for item in checks)
result = {
    "status": "passed" if passed == len(checks) else "failed",
    "passed": passed,
    "total": len(checks),
    "next_task": "FS4-P1-RUN-BOUNDED-4METHOD" if passed == len(checks) else "repair_postmerge_sync",
    "performance_y_read_in_prm070": 0,
    "model_fit_in_prm070": 0,
    "feature_promotion_in_prm070": 0,
}
(OUT / "PRM070_SLICE005_postmerge_sync_summary.json").write_text(
    json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
)
print(json.dumps(result, ensure_ascii=False))
if result["status"] != "passed":
    raise SystemExit(1)
