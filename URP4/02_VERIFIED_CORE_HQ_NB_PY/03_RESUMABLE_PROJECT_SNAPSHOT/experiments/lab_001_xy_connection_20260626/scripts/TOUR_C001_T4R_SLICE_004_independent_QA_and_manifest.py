from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
FACTORY = LAB / "factories" / "TOUR-C001"
REPORTS = FACTORY / "analysis_factory" / "reports"
FROZEN = FACTORY / "analysis_factory" / "frozen"
CONTRACT = FACTORY / "contracts" / "TOUR-C001_T4R_SLICE_004_ALL58_SOURCE_MATCHED_EXACT_EXTRACTION_20260720.json"
EXECUTION_SCRIPT = LAB / "scripts" / "TOUR_C001_T4R_SLICE_004_all58_source_matched_exact_extraction.py"
PRIOR_PROTECTED = REPORTS / "TOUR-C001-T4R-SLICE-003A_protected_asset_verification.csv"
WORK = ROOT / ".tmp" / "t4rs4" / "P1000_S801"
RUN_ID = "TOUR-C001-T4R-SLICE-004"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False, encoding="utf-8-sig")


def protected_verification() -> tuple[Path, list[dict]]:
    prior = pd.read_csv(PRIOR_PROTECTED, dtype=str, keep_default_na=False)
    rows: list[dict] = []
    for item in prior.itertuples(index=False):
        path = ROOT / item.path
        if item.guard_kind == "site_git_state":
            actual_hash = subprocess.check_output(
                ["git", "-C", str(path), "rev-parse", "HEAD"], text=True
            ).strip()
            actual_size = ""
        elif item.guard_kind == "site_git_status":
            status_bytes = subprocess.check_output(
                ["git", "-C", str(path), "status", "--porcelain"]
            )
            actual_hash = hashlib.sha256(status_bytes).hexdigest()
            actual_size = ""
        else:
            actual_hash = sha256(path) if path.is_file() else "missing"
            actual_size = str(path.stat().st_size) if path.is_file() else "missing"
        expected_hash = item.actual_sha256
        expected_size = item.actual_size_bytes
        status = "unchanged" if actual_hash == expected_hash and actual_size == expected_size else "changed_or_missing"
        rows.append(
            {
                "guard_kind": item.guard_kind,
                "path": item.path,
                "source_alias": item.source_alias,
                "expected_sha256_from_SLICE003A": expected_hash,
                "actual_sha256": actual_hash,
                "expected_size_bytes": expected_size,
                "actual_size_bytes": actual_size,
                "verification_status": status,
            }
        )
    output = REPORTS / f"{RUN_ID}_protected_asset_verification.csv"
    write_csv(output, rows)
    return output, rows


def main() -> None:
    if platform.python_version() != "3.12.12" or "KMK312" not in sys.executable:
        raise RuntimeError(f"KMK312 Python 3.12.12 required: {sys.executable} / {platform.python_version()}")

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    expected_models = [item["model_id"] for item in contract["fixed_geometry"]]
    candidate_path = FROZEN / f"{RUN_ID}_all58_direct_legacy_candidate_values.csv"
    selected_path = FROZEN / f"{RUN_ID}_all58_selected_rescue_signals.csv"
    summary_path = REPORTS / f"{RUN_ID}_execution_summary.json"
    model_qa_path = REPORTS / f"{RUN_ID}_model_execution_QA.csv"
    candidates = pd.read_csv(candidate_path)
    selected = pd.read_csv(selected_path)
    model_qa = pd.read_csv(model_qa_path)
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    completes: list[dict] = []
    per_model_files: list[Path] = []
    for model_id in expected_models:
        model_dir = WORK / model_id
        complete_path = model_dir / "complete.json"
        if not complete_path.is_file():
            raise RuntimeError(f"missing complete packet: {model_id}")
        packet = json.loads(complete_path.read_text(encoding="utf-8"))
        completes.append(packet)
        retained = [path for path in model_dir.rglob("*") if path.is_file()]
        per_model_files.extend(retained)

    gates: list[dict] = []

    def gate(test_id: str, passed: bool, details: str) -> None:
        gates.append({"test_id": test_id, "passed": bool(passed), "details": details})

    execution_hash = sha256(EXECUTION_SCRIPT)
    gate("environment_KMK312_python312", True, f"{sys.executable}; {platform.python_version()}")
    gate("execution_code_hash_gate", execution_hash == contract["execution_code"]["sha256"], execution_hash)
    parent_checks = [sha256(ROOT / item["path"]) == item["sha256"] for item in contract["parent_evidence"]]
    gate("contract_parent_evidence_hashes", all(parent_checks), f"{sum(parent_checks)}/{len(parent_checks)}")
    geometry_checks = [sha256(ROOT / item["path"]) == item["sha256"] for item in contract["fixed_geometry"]]
    gate("canonical_N40_geometry_hashes", all(geometry_checks), f"{sum(geometry_checks)}/{len(geometry_checks)}")
    gate("complete_packets", len(completes) == 58 and {x["model_id"] for x in completes} == set(expected_models), f"{len(completes)}/58")
    gate("per_model_slice_rows", all(int(x["slice_rows"]) == 801 for x in completes), f"sum={sum(int(x['slice_rows']) for x in completes)}")
    gate("per_model_overlay_rows", all(int(x["overlay_rows"]) == 800 for x in completes), f"sum={sum(int(x['overlay_rows']) for x in completes)}")
    gate("per_model_candidate_rows", all(int(x["candidate_rows"]) == 40 for x in completes), f"sum={sum(int(x['candidate_rows']) for x in completes)}")
    gate("saved_PNG_readback", sum(int(x["readback_mismatch_sum"]) for x in completes) == 0, "mismatch=0")
    gate("transient_PNG_deleted", all(int(x["transient_png_remaining"]) == 0 for x in completes), f"deleted={sum(int(x['transient_png_deleted']) for x in completes)}; remaining=0")
    gate("audit_PNG_retained", sum(int(x["audit_png_retained"]) for x in completes) == 348, f"retained={sum(int(x['audit_png_retained']) for x in completes)}")
    gate("aggregate_candidate_census", candidates.shape[0] == 2320 and candidates["candidate_id"].nunique() == 40 and candidates["model_id"].nunique() == 58, f"rows={len(candidates)}; candidates={candidates['candidate_id'].nunique()}; models={candidates['model_id'].nunique()}")
    finite = np.isfinite(pd.to_numeric(candidates["value"], errors="coerce").to_numpy()).sum()
    gate("candidate_finite_missing_explicit", finite == 2320, f"finite={finite}; missing={2320-finite}")
    gate("selected_signal_census", selected.shape[0] == 232 and selected["model_id"].nunique() == 58, f"rows={len(selected)}")
    gate("aggregate_summary_counts", summary["slice_rows"] == 46458 and summary["overlay_rows"] == 46400 and summary["candidate_rows"] == 2320, json.dumps(summary, ensure_ascii=False))
    accepted_status = model_qa["status"].astype(str).isin(["passed", "passed_reused"])
    gate("model_QA_all_pass", len(model_qa) == 58 and accepted_status.all(), f"rows={len(model_qa)}; accepted={int(accepted_status.sum())}")
    gate("scientific_scope_boundary", summary["performance_y_access"] == 0 and summary["predictive_fits"] == 0 and summary["feature_promotions"] == 0, "y=0; fits=0; promotions=0")

    protected_path, protected_rows = protected_verification()
    protected_ok = all(row["verification_status"] == "unchanged" for row in protected_rows)
    gate("protected_assets_unchanged", protected_ok and len(protected_rows) == 29, f"{sum(row['verification_status']=='unchanged' for row in protected_rows)}/{len(protected_rows)}")
    processes = subprocess.run(
        ["powershell", "-NoProfile", "-Command", f"@(Get-Process python -ErrorAction SilentlyContinue | Where-Object {{$_.Path -like '*KMK312*' -and $_.Id -ne {os.getpid()}}}).Count"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    gate("no_KMK312_worker_remaining", processes == "0", f"process_count={processes}")

    qa_path = REPORTS / f"{RUN_ID}_independent_QA.csv"
    write_csv(qa_path, gates)
    if not all(row["passed"] for row in gates):
        failed = [row["test_id"] for row in gates if not row["passed"]]
        raise RuntimeError(f"independent QA failed: {failed}")

    fixed_outputs = [
        CONTRACT,
        EXECUTION_SCRIPT,
        candidate_path,
        selected_path,
        summary_path,
        model_qa_path,
        REPORTS / f"{RUN_ID}_reuse_audit.csv",
        REPORTS / f"{RUN_ID}_runtime_reference.csv",
        REPORTS / f"{RUN_ID}_runtime_estimate.json",
        REPORTS / f"{RUN_ID}_shard_manifest.csv",
        REPORTS / f"{RUN_ID}_live_status.csv",
        REPORTS / f"{RUN_ID}_attempt_history.csv",
        protected_path,
        qa_path,
        LAB / "results" / "R09-20260720-TOUR-C001_T4R_SLICE_004_ALL58_SOURCE_MATCHED_EXACT_EXTRACTION_REPORT_20260720.md",
        Path(__file__),
    ]
    manifest_targets = sorted({path.resolve() for path in [*fixed_outputs, *per_model_files]})
    manifest_path = REPORTS / f"{RUN_ID}_output_manifest.csv"
    manifest_rows = [
        {"path": rel(path), "bytes": path.stat().st_size, "sha256": sha256(path), "manifest_status": "present_hash_frozen"}
        for path in manifest_targets
    ]
    write_csv(manifest_path, manifest_rows)
    print(json.dumps({"qa_passed": len(gates), "qa_failed": 0, "manifest_files": len(manifest_rows), "manifest_path": rel(manifest_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
