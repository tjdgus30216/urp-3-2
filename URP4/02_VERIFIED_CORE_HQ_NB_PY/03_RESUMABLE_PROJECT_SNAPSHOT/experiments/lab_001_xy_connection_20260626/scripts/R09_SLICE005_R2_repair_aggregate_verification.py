from __future__ import annotations

import csv
import hashlib
import json
import math
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(r"C:\Users\chuck\URP4-1_FACTORY\R09_SLICE005_20260721")
KST = timezone(timedelta(hours=9))
CONTRACT = ROOT / "contracts/PRM-050_R09-SLICE-005_LABPC_EXECUTION.json"
JOB_MATRIX = ROOT / "config/pending_32_job_matrix.csv"
REPORTS = ROOT / "results/reports"

OUTPUT_MATRIX = REPORTS / "all40_descriptor_scalar_matrix.csv"
OUTPUT_SUMMARY = REPORTS / "verification_summary.json"
OUTPUT_INPUT_HASHES = REPORTS / "aggregate_repair_input_hash_manifest.csv"
OUTPUT_QA = REPORTS / "aggregate_repair_QA.csv"

FIELDS = [
    "execution_cell_id",
    "model_id",
    "config_id",
    "config_role",
    "pixel_width",
    "slice_count",
    "slice_spacing_mm",
    "formula_id",
    "descriptor",
    "population_id",
    "statistic",
    "unit",
    "value",
    "population_n",
    "state",
    "scientific_state",
    "config_sha256",
    "source_role",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_csv_atomic(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temp, path)


def write_json_atomic(path: Path, payload: dict) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temp, path)


def safe_job_name(job_id: str) -> str:
    return job_id.replace("::", "__")


def passed_attempt(job_id: str) -> Path:
    runtime = ROOT / "results/runtime" / safe_job_name(job_id)
    for attempt in sorted(runtime.glob("attempt*")):
        complete_path = attempt / "complete.json"
        if complete_path.is_file():
            complete = json.loads(complete_path.read_text(encoding="utf-8"))
            if complete.get("status") == "passed":
                return attempt
    raise RuntimeError(f"No passed attempt: {job_id}")


def finite_nine(path: Path) -> list[dict[str, str]]:
    rows = read_csv(path)
    if len(rows) != 9:
        raise RuntimeError(f"Expected 9 descriptor rows, got {len(rows)}: {path}")
    if not all(math.isfinite(float(row["value"])) for row in rows):
        raise RuntimeError(f"Non-finite descriptor value: {path}")
    return rows


def normalize(base: dict, descriptor: dict, source_role: str) -> dict[str, str]:
    merged = {field: "" for field in FIELDS}
    merged.update({key: str(value) for key, value in base.items() if key in merged})
    merged.update({key: str(value) for key, value in descriptor.items() if key in merged})
    merged["source_role"] = source_role
    return merged


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    jobs = read_csv(JOB_MATRIX)
    if len(jobs) != 32:
        raise RuntimeError(f"Expected 32 job rows, got {len(jobs)}")

    cell_verification = read_csv(REPORTS / "cell_verification.csv")
    table_verification = read_csv(REPORTS / "table_hash_verification.csv")
    if len(cell_verification) != 32 or not all(row["all_passed"].lower() == "true" for row in cell_verification):
        raise RuntimeError("32/32 cell verification is not passed")
    if len(table_verification) != 160 or not all(row["hash_ok"].lower() == "true" for row in table_verification):
        raise RuntimeError("160/160 table hash verification is not passed")

    aggregate_rows: list[dict[str, str]] = []
    hash_rows: list[dict[str, str]] = []
    for job in jobs:
        attempt = passed_attempt(job["execution_cell_id"])
        descriptor_path = attempt / "tables/descriptor_result.csv"
        descriptors = finite_nine(descriptor_path)
        hash_rows.append(
            {
                "source_role": "new_labpc_cell",
                "identity": job["execution_cell_id"],
                "path": str(descriptor_path),
                "bytes": str(descriptor_path.stat().st_size),
                "sha256": sha256(descriptor_path),
            }
        )
        base = {
            "execution_cell_id": job["execution_cell_id"],
            "model_id": job["model_id"],
            "config_id": job["config_id"],
            "config_role": job["config_role"],
            "pixel_width": job["pixel_width"],
            "slice_count": job["slice_count"],
            "slice_spacing_mm": job["slice_spacing_mm"],
        }
        aggregate_rows.extend(normalize(base, row, "new_labpc_cell") for row in descriptors)

    baselines = contract["baselines"]
    if len(baselines) != 8:
        raise RuntimeError(f"Expected 8 baselines, got {len(baselines)}")
    for model_id, baseline in baselines.items():
        descriptor_path = ROOT / baseline["descriptor_path"]
        descriptors = finite_nine(descriptor_path)
        hash_rows.append(
            {
                "source_role": "frozen_RUN139_reuse",
                "identity": model_id,
                "path": str(descriptor_path),
                "bytes": str(descriptor_path.stat().st_size),
                "sha256": sha256(descriptor_path),
            }
        )
        base = {
            "execution_cell_id": f"STRICT-CV::{model_id}::CFG-P1000-S0801",
            "model_id": model_id,
            "config_id": "CFG-P1000-S0801",
            "config_role": "canonical_reuse",
            "pixel_width": "1000",
            "slice_count": "801",
            "slice_spacing_mm": "0.05",
        }
        aggregate_rows.extend(normalize(base, row, "frozen_RUN139_reuse") for row in descriptors)

    if len(aggregate_rows) != 360:
        raise RuntimeError(f"Expected 360 scalar rows, got {len(aggregate_rows)}")
    if {row["source_role"] for row in aggregate_rows} != {"new_labpc_cell", "frozen_RUN139_reuse"}:
        raise RuntimeError("Source-role partition is incomplete")
    if sum(row["source_role"] == "new_labpc_cell" for row in aggregate_rows) != 288:
        raise RuntimeError("New-cell scalar row count is not 288")
    if sum(row["source_role"] == "frozen_RUN139_reuse" for row in aggregate_rows) != 72:
        raise RuntimeError("Frozen-baseline scalar row count is not 72")

    write_csv_atomic(OUTPUT_MATRIX, FIELDS, aggregate_rows)
    write_csv_atomic(OUTPUT_INPUT_HASHES, ["source_role", "identity", "path", "bytes", "sha256"], hash_rows)

    qa_rows = [
        {"qa_id": "RQA01", "check": "new cells", "observed": 32, "expected": 32, "passed": True},
        {"qa_id": "RQA02", "check": "frozen baselines", "observed": 8, "expected": 8, "passed": True},
        {"qa_id": "RQA03", "check": "cell verification", "observed": 32, "expected": 32, "passed": True},
        {"qa_id": "RQA04", "check": "table hashes", "observed": 160, "expected": 160, "passed": True},
        {"qa_id": "RQA05", "check": "new scalar rows", "observed": 288, "expected": 288, "passed": True},
        {"qa_id": "RQA06", "check": "baseline scalar rows", "observed": 72, "expected": 72, "passed": True},
        {"qa_id": "RQA07", "check": "combined scalar rows", "observed": 360, "expected": 360, "passed": True},
        {"qa_id": "RQA08", "check": "union schema fields", "observed": len(FIELDS), "expected": 18, "passed": len(FIELDS) == 18},
        {"qa_id": "RQA09", "check": "input hash rows", "observed": len(hash_rows), "expected": 40, "passed": len(hash_rows) == 40},
    ]
    write_csv_atomic(OUTPUT_QA, ["qa_id", "check", "observed", "expected", "passed"], qa_rows)
    summary = {
        "run_id": "R09-SLICE-005-LABPC-VERIFY-001-R2-UNION-SCHEMA-REPAIR",
        "created_at_kst": datetime.now(KST).isoformat(timespec="seconds"),
        "status": "passed",
        "new_cells_passed": "32/32",
        "frozen_baselines_included": "8/8",
        "all40_scalar_rows": 360,
        "new_table_hash_rows": 160,
        "aggregate_schema_fields": len(FIELDS),
        "repair_reason": "New-cell descriptor rows use scientific_state/config_sha256 while frozen baselines use population_id/state; union schema prevents DictWriter field rejection.",
        "raw_descriptor_files_modified": 0,
        "scientific_convergence_decision": "not performed; return to control tower",
        "feature_or_model_claim": "prohibited",
    }
    write_json_atomic(OUTPUT_SUMMARY, summary)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
