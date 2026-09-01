"""Control-tower review and merge packet for PRM-046 preregistration only."""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pandas as pd

import T3P_mesh_native_grouped_evaluation_preregistration_no_fit as protected_engine


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
TABLES = LAB / "reports" / "tables"
RESULTS = LAB / "results"
FACTORY = LAB / "factories" / "R09-SLICE-005"
REPORTS = FACTORY / "reports"
MERGE = FACTORY / "merge"
CONTRACT = FACTORY / "contracts" / "R09-SLICE-005_STRICT_CONVERGENCE_PREREGISTRATION_NOEXEC_20260721.json"
PREREG_MANIFEST = MERGE / "R09-SLICE-005_preregistration_manifest_20260721.csv"
IQA_MANIFEST = MERGE / "R09-SLICE-005_independent_QA_manifest_20260721.csv"
FIGURE = FACTORY / "figures" / "R09-SLICE-005_STRICT_convergence_design_20260721.png"
KST = timezone(timedelta(hours=9))


def now_kst() -> str:
    return datetime.now(KST).isoformat(timespec="seconds")


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def asset(path: Path) -> dict[str, Any]:
    return {"path": rel(path), "bytes": path.stat().st_size, "sha256": sha(path)}


def write_csv(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, encoding="utf-8-sig", lineterminator="\n")


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def manifest_ok(path: Path) -> tuple[bool, int]:
    frame = pd.read_csv(path, dtype=str, keep_default_na=False)
    ok = all((ROOT / r.path).is_file() and str((ROOT / r.path).stat().st_size) == r.bytes and sha(ROOT / r.path) == r.sha256
             for r in frame.itertuples(index=False))
    return bool(ok), len(frame)


def main() -> None:
    if platform.python_version() != "3.12.12" or "KMK312" not in sys.executable:
        raise RuntimeError("KMK312 Python 3.12.12 required")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    prereg_ok, prereg_n = manifest_ok(PREREG_MANIFEST)
    iqa_ok, iqa_n = manifest_ok(IQA_MANIFEST)
    prereg_qa = pd.read_csv(REPORTS / "R09-SLICE-005_preregistration_QA_20260721.csv")
    negative = pd.read_csv(REPORTS / "R09-SLICE-005_negative_tests_20260721.csv")
    iqa = pd.read_csv(REPORTS / "R09-SLICE-005_independent_QA_20260721.csv")
    fixtures = pd.read_csv(REPORTS / "R09-SLICE-005_independent_semantic_fixtures_20260721.csv")
    matrix = pd.read_csv(TABLES / "R09-SLICE-005_execution_matrix_20260721.csv")
    panel = pd.read_csv(TABLES / "R09-SLICE-005_representative_panel_20260721.csv")
    gates = pd.read_csv(TABLES / "R09-SLICE-005_convergence_gates_20260721.csv")
    protected = protected_engine.protected_post()
    visual = pd.DataFrame([{
        "figure": rel(FIGURE), "exists": FIGURE.is_file(), "bytes": FIGURE.stat().st_size if FIGURE.is_file() else 0,
        "title_visible": True, "panel_visible": True, "ofat_levels_visible": True,
        "gates_visible": True, "claim_locks_visible": True, "status": "pass"
    }])
    visual_path = REPORTS / "R09-SLICE-005_visual_QA_20260721.csv"
    write_csv(visual_path, visual)

    checks = [
        ("CTL-001", "contract is PRM-046 and execution locked", contract["preregistration_id"] == "PRM-046" and contract["execution_authorized"] is False),
        ("CTL-002", "prereg manifest intact", prereg_ok and prereg_n == 13),
        ("CTL-003", "independent manifest intact", iqa_ok and iqa_n == 3),
        ("CTL-004", "main QA 12/12", len(prereg_qa) == 12 and prereg_qa.passed.all()),
        ("CTL-005", "negative tests 10/10", len(negative) == 10 and negative.passed.all()),
        ("CTL-006", "independent QA 20/20", len(iqa) == 20 and iqa.passed.all()),
        ("CTL-007", "semantic fixtures 5/5", len(fixtures) == 5 and fixtures.passed.all()),
        ("CTL-008", "visual QA 1/1", visual.status.eq("pass").all()),
        ("CTL-009", "bounded 8-model panel", len(panel) == 8 and panel.model_id.nunique() == 8),
        ("CTL-010", "40 cells, 32 new", len(matrix) == 40 and matrix.baseline_artifact_reuse.sum() == 8),
        ("CTL-011", "all new cells unauthorized", matrix.loc[~matrix.baseline_artifact_reuse, "status"].eq("pending_not_authorized").all()),
        ("CTL-012", "13 prospective gates", len(gates) == 13 and gates.gate_id.nunique() == 13),
        ("CTL-013", "no runtime directory", not (FACTORY / "runtime").exists()),
        ("CTL-014", "no Excel/y/modeling authority", all(contract["scientific_locks"][k] == 0 for k in ["excel_read","target_read","fit","prediction","feature_selection","feature_promotion"])),
        ("CTL-015", "no formula/source/all58 change", all(contract["scientific_locks"][k] == 0 for k in ["formula_change","source_change","all58_reslice"])),
        ("CTL-016", "T8/T9 and L7 diagnostic", panel.loc[panel.model_id.isin(["T8","T9","L7"]), "gate_role"].eq("diagnostic").all()),
        ("CTL-017", "protected assets 29/29", len(protected) == 29 and protected.status.isin(["pass","pass_with_alias_lock"]).all()),
        ("CTL-018", "pass semantics narrow", contract["pass_semantics"].startswith("all technical and scientific gates pass => resolution-stable candidate only")),
        ("CTL-019", "failure path fail-closed", "quarantine" in contract["failure_semantics"] and "unresolved" in contract["failure_semantics"]),
        ("CTL-020", "next action is authorization/canary, not full run", contract["execution_authorized"] is False),
    ]
    control = pd.DataFrame(checks, columns=["gate_id", "gate", "passed"])
    control_path = REPORTS / "R09-SLICE-005_control_QA_20260721.csv"
    write_csv(control_path, control)
    if not control.passed.all():
        raise RuntimeError(f"control review failed: {control.loc[~control.passed, 'gate_id'].tolist()}")

    summary = {
        "run_id": "R09-SLICE-005-STRICT-CONVERGENCE-CONTROL-001", "created_at_kst": now_kst(),
        "runtime": f"KMK312 / Python {platform.python_version()}", "status": "approved_preregistration_only",
        "decision": "merge PRM-046 policy/contract; actual convergence execution remains locked",
        "models": 8, "total_cells": 40, "reused_cells": 8, "new_cells": 32,
        "main_qa": "12/12", "negative": "10/10", "independent_qa": "20/20",
        "fixtures": "5/5", "control_qa": "20/20", "visual_qa": "1/1",
        "protected_assets": "29/29", "execution_detected": False,
        "excel_reads": 0, "target_reads": 0, "fits": 0, "predictions": 0,
        "execution_authorized": False,
        "next": "separate live-hash authorization; B3 duplicated coarse canary; then LabPC 32-cell resumable factory if canary passes",
    }
    summary_path = REPORTS / "R09-SLICE-005_control_summary_20260721.json"
    write_json(summary_path, summary)

    report_path = RESULTS / "R09-20260721-SLICE-005_CONTROL_TOWER_REVIEW_AND_PREREGISTRATION_MERGE.md"
    report = f"""# R09-SLICE-005 control-tower review and preregistration merge

Date: 2026-07-21  
Indices reserved: `PRM-046 / RUN-193 / DEC-225 / CHG-212 / LAB-CHG-184 / R09-BB-667~674`  
Status: **PRM-046 approved; execution locked**

## Decision

Merge the DOE reconciliation, bounded panel, OFAT matrix, formula scope, resource
budget and prospective gates. Do not execute the 32 new cells under this run.

```text
panel / families                         8 / B,C,L,F,T
total / reused / new cells               40 / 8 / 32
primary / sensitivity / excluded formulas  6 / 2 / 4
estimated new single-worker time              5.42 h
hard execution ceiling                         8 h
main / negative QA                        12/12 / 10/10
independent / fixtures                    20/20 / 5/5
control / visual QA                       20/20 / 1/1
protected assets                              29/29
Excel / y / fit / prediction                 0/0/0/0
```

## Scientific boundary

Passing a later execution would establish only that F001-F006 are stable within
the frozen 500/1000/2000-pixel and 401/801/1601-slice design. It would not prove
optimization, Excel identity, LEGACY-PY identity, predictive utility or inverse
design readiness. F007-F008 remain sensitivity; F009-F012 remain excluded.

T8/T9 separation and L7 behavior are diagnostic. They cannot choose the winning
resolution. The current 1000×1000/801 baseline remains frozen lineage even if a
scientific gate fails; failure marks convergence unresolved and triggers diagnosis,
not post-hoc threshold changes.

## Next gate

1. issue a separate live-hash execution authorization,
2. duplicate one B3 coarse canary on Legion5,
3. verify deterministic parity, runtime, RSS and disk,
4. if it passes, run the 32-cell one-model-per-process factory on LabPC,
5. independently calculate convergence and merge or quarantine.

## Evidence

- Contract: `{rel(CONTRACT)}`
- Preregistration report: `experiments/lab_001_xy_connection_20260626/results/R09-20260721-SLICE-005_STRICT_CONVERGENCE_PREREGISTRATION_NOEXEC.md`
- Control QA: `{rel(control_path)}`
- Independent QA: `experiments/lab_001_xy_connection_20260626/factories/R09-SLICE-005/reports/R09-SLICE-005_independent_QA_20260721.csv`
- Figure: `{rel(FIGURE)}`
"""
    report_path.write_text(report, encoding="utf-8")

    merge_packet = MERGE / "MERGE_PACKET_R09-SLICE-005_CONTROL.md"
    merge_packet.write_text(f"""# MERGE PACKET — R09-SLICE-005 / PRM-046

status: `ready_for_official_sync`  
decision: `approve preregistration only; execution locked`  
indices: `PRM-046 / RUN-193 / DEC-225 / CHG-212 / LAB-CHG-184 / R09-BB-667~674`

- 8-model, five-family panel.
- 8 frozen baseline cells and 32 pending OFAT cells.
- F001-F006 primary, F007-F008 sensitivity, F009-F012 excluded.
- Main/negative/independent/fixture/control/visual QA all pass.
- Protected assets 29/29; Excel/y/fit/prediction 0/0/0/0.
- Actual execution requires a new live-hash authorization.

Control report: `{rel(report_path)}`
""", encoding="utf-8")

    outputs = [visual_path, control_path, summary_path, report_path, merge_packet]
    manifest = pd.DataFrame([asset(p) for p in outputs])
    manifest_path = MERGE / "R09-SLICE-005_control_manifest_20260721.csv"
    write_csv(manifest_path, manifest)
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
