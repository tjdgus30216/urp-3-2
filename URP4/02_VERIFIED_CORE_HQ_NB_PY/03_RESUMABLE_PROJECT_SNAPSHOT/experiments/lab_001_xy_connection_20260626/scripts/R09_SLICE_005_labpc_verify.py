from __future__ import annotations

import csv
import json
import math
from pathlib import Path

from R09_SLICE_005_labpc_common import (
    atomic_json,
    now_kst,
    package_root,
    read_csv,
    read_json,
    safe_job_name,
    sha256,
    write_csv,
)


ROOT = package_root()
CONTRACT_PATH = ROOT / "contracts/PRM-050_R09-SLICE-005_LABPC_EXECUTION.json"
MATRIX_PATH = ROOT / "config/pending_32_job_matrix.csv"


def passed_attempt(job_id: str) -> Path | None:
    root = ROOT / "results/runtime" / safe_job_name(job_id)
    if not root.exists():
        return None
    for attempt in sorted(root.glob("attempt*")):
        complete = attempt / "complete.json"
        if complete.is_file():
            try:
                if read_json(complete).get("status") == "passed":
                    return attempt
            except Exception:
                pass
    return None


def main() -> None:
    contract = read_json(CONTRACT_PATH)
    jobs = read_csv(MATRIX_PATH)
    job_rows: list[dict] = []
    scalar_rows: list[dict] = []
    table_rows: list[dict] = []
    for job in jobs:
        job_id = job["execution_cell_id"]
        attempt = passed_attempt(job_id)
        checks = {
            "passed_attempt": attempt is not None,
            "complete_gates": False,
            "table_manifest_hash": False,
            "five_tables": False,
            "table_hashes": False,
            "scalar_rows": False,
            "png_cleanup": False,
            "readback": False,
        }
        if attempt is not None:
            complete = read_json(attempt / "complete.json")
            checks["complete_gates"] = all(bool(value) for value in complete["gates"].values())
            manifest_path = ROOT / complete["table_manifest"]
            checks["table_manifest_hash"] = sha256(manifest_path) == complete["table_manifest_sha256"]
            manifest = read_csv(manifest_path)
            checks["five_tables"] = len(manifest) == 5
            hash_flags = []
            for row in manifest:
                path = ROOT / row["path"]
                ok = path.is_file() and path.stat().st_size == int(row["bytes"]) and sha256(path) == row["sha256"]
                hash_flags.append(ok)
                table_rows.append({"execution_cell_id": job_id, "path": row["path"], "hash_ok": ok})
            checks["table_hashes"] = len(hash_flags) == 5 and all(hash_flags)
            descriptor_path = attempt / "tables/descriptor_result.csv"
            descriptors = read_csv(descriptor_path)
            finite = all(math.isfinite(float(row["value"])) for row in descriptors)
            checks["scalar_rows"] = len(descriptors) == 9 and finite
            checks["png_cleanup"] = complete["qa"]["remaining_png"] == 0 and complete["qa"]["png_created"] == complete["qa"]["png_deleted"]
            checks["readback"] = complete["qa"]["readback_mismatch_sum"] == 0
            for row in descriptors:
                scalar_rows.append(
                    {
                        "execution_cell_id": job_id,
                        "model_id": job["model_id"],
                        "config_id": job["config_id"],
                        "config_role": job["config_role"],
                        "pixel_width": job["pixel_width"],
                        "slice_count": job["slice_count"],
                        "slice_spacing_mm": job["slice_spacing_mm"],
                        **row,
                        "source_role": "new_labpc_cell",
                    }
                )
        job_rows.append(
            {
                "execution_cell_id": job_id,
                "model_id": job["model_id"],
                "config_id": job["config_id"],
                "passed_attempt": attempt.name if attempt else "",
                **checks,
                "all_passed": all(checks.values()),
            }
        )

    for model_id, baseline in contract["baselines"].items():
        descriptors = read_csv(ROOT / baseline["descriptor_path"])
        for row in descriptors:
            scalar_rows.append(
                {
                    "execution_cell_id": f"STRICT-CV::{model_id}::CFG-P1000-S0801",
                    "model_id": model_id,
                    "config_id": "CFG-P1000-S0801",
                    "config_role": "canonical_reuse",
                    "pixel_width": "1000",
                    "slice_count": "801",
                    "slice_spacing_mm": "0.05",
                    **row,
                    "source_role": "frozen_RUN139_reuse",
                }
            )

    reports = ROOT / "results/reports"
    reports.mkdir(parents=True, exist_ok=True)
    write_csv(reports / "cell_verification.csv", list(job_rows[0].keys()), job_rows)
    write_csv(reports / "table_hash_verification.csv", ["execution_cell_id", "path", "hash_ok"], table_rows)
    scalar_fields = list(scalar_rows[0].keys())
    write_csv(reports / "all40_descriptor_scalar_matrix.csv", scalar_fields, scalar_rows)
    passed_jobs = sum(bool(row["all_passed"]) for row in job_rows)
    summary = {
        "run_id": "R09-SLICE-005-LABPC-VERIFY-001",
        "created_at_kst": now_kst(),
        "status": "passed" if passed_jobs == 32 else "failed_or_incomplete",
        "new_cells_passed": f"{passed_jobs}/32",
        "frozen_baselines_included": "8/8",
        "all40_scalar_rows": len(scalar_rows),
        "new_table_hash_rows": len(table_rows),
        "scientific_convergence_decision": "not performed; return to control tower",
        "feature_or_model_claim": "prohibited",
    }
    atomic_json(reports / "verification_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False))
    if summary["status"] != "passed":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
