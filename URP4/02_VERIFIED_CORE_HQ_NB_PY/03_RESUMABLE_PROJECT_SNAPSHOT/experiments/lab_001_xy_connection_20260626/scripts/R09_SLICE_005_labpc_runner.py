from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
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
AUTH_PATH = ROOT / "preflight/runtime_authorization.json"
MANIFEST_PATH = ROOT / "PACKAGE_MANIFEST.csv"
WORKER_PATH = ROOT / "factory/R09_SLICE_005_labpc_worker.py"


def attempt_state(path: Path) -> str:
    complete = path / "complete.json"
    if complete.is_file():
        try:
            return "passed" if read_json(complete).get("status") == "passed" else "failed"
        except Exception:
            return "corrupt"
    if (path / "failure.json").is_file():
        return "failed"
    return "partial"


def job_state(job_id: str, max_attempts: int) -> dict:
    job_root = ROOT / "results/runtime" / safe_job_name(job_id)
    attempts = sorted(job_root.glob("attempt*")) if job_root.exists() else []
    states = [attempt_state(path) for path in attempts]
    passed = any(state == "passed" for state in states)
    if passed:
        status = "passed"
    elif len(attempts) >= max_attempts:
        status = "quarantined"
    elif attempts:
        status = "retry_pending"
    else:
        status = "pending"
    return {
        "job_id": job_id,
        "status": status,
        "attempt_count": len(attempts),
        "attempt_states": "|".join(states),
        "next_attempt": len(attempts) + 1,
    }


def write_ledger(jobs: list[dict], max_attempts: int) -> list[dict]:
    rows = []
    for order, job in enumerate(jobs, start=1):
        state = job_state(job["execution_cell_id"], max_attempts)
        rows.append(
            {
                "execution_order": order,
                "execution_cell_id": job["execution_cell_id"],
                "model_id": job["model_id"],
                "config_id": job["config_id"],
                "status": state["status"],
                "attempt_count": state["attempt_count"],
                "attempt_states": state["attempt_states"],
            }
        )
    write_csv(
        ROOT / "results/factory_state_ledger.csv",
        ["execution_order", "execution_cell_id", "model_id", "config_id", "status", "attempt_count", "attempt_states"],
        rows,
    )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--status-only", action="store_true")
    args = parser.parse_args()
    contract = read_json(CONTRACT_PATH)
    authorization = read_json(AUTH_PATH)
    if authorization.get("status") != "passed_and_authorized":
        raise RuntimeError("run doctor --authorize before factory execution")
    if authorization["static_contract_sha256"] != sha256(CONTRACT_PATH):
        raise RuntimeError("contract drift after live authorization")
    if authorization["package_manifest_sha256"] != sha256(MANIFEST_PATH):
        raise RuntimeError("package drift after live authorization")
    if sha256(Path(__file__).resolve()) != contract["code_hashes"]["runner"]:
        raise RuntimeError("runner hash drift")
    jobs = read_csv(MATRIX_PATH)
    max_attempts = int(contract["max_attempts_per_cell"])
    ledger = write_ledger(jobs, max_attempts)
    if args.status_only:
        counts = {status: sum(row["status"] == status for row in ledger) for status in ["passed", "pending", "retry_pending", "quarantined"]}
        print(json.dumps(counts, ensure_ascii=False))
        return

    started = now_kst()
    started_clock = time.monotonic()
    hard_seconds = float(contract["resource_gates"]["factory_hard_seconds"])
    logs = ROOT / "results/logs"
    logs.mkdir(parents=True, exist_ok=True)
    executed = 0
    for job in jobs:
        if time.monotonic() - started_clock >= hard_seconds:
            break
        job_id = job["execution_cell_id"]
        state = job_state(job_id, max_attempts)
        if state["status"] in {"passed", "quarantined"}:
            continue
        attempt = int(state["next_attempt"])
        command = [
            sys.executable,
            str(WORKER_PATH),
            "--job-id",
            job_id,
            "--attempt",
            str(attempt),
        ]
        print(f"[{now_kst()}] START {job_id} attempt{attempt:02d}", flush=True)
        process = subprocess.run(command, text=True, capture_output=True)
        log_path = logs / f"{safe_job_name(job_id)}__attempt{attempt:02d}.log"
        log_path.write_text(
            f"COMMAND: {command}\nRETURN_CODE: {process.returncode}\n\nSTDOUT\n{process.stdout}\n\nSTDERR\n{process.stderr}\n",
            encoding="utf-8",
        )
        executed += 1
        print(f"[{now_kst()}] END   {job_id} attempt{attempt:02d} rc={process.returncode}", flush=True)
        write_ledger(jobs, max_attempts)

    ledger = write_ledger(jobs, max_attempts)
    counts = {status: sum(row["status"] == status for row in ledger) for status in ["passed", "pending", "retry_pending", "quarantined"]}
    summary = {
        "run_id": "R09-SLICE-005-LABPC-FACTORY-EXEC-001",
        "started_at_kst": started,
        "completed_at_kst": now_kst(),
        "status": "passed" if counts["passed"] == 32 else "partial_or_failed",
        "counts": counts,
        "worker_processes_launched_this_session": executed,
        "resume_safe": True,
        "full_scientific_review": "not performed on LabPC",
    }
    atomic_json(ROOT / "results/factory_run_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False))
    if summary["status"] != "passed":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
