from __future__ import annotations

"""Execute the already-authorized PRM-100 cells, but never merge them."""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
FACTORY99 = LAB / "factories" / "PRM-099"
FACTORY100 = LAB / "factories" / "PRM-100"
REPORTS = FACTORY100 / "reports"
RUNNER = LAB / "scripts" / "PRM099_third_wave_full58_runner.py"
CONFIG = FACTORY99 / "contracts" / "PRM099_FULL58_SIX_OUTPUT_CONFIG_20260723.json"
CONTRACT = FACTORY99 / "contracts" / "PRM-099_FULL58_PERMIT_DECISION_CONTRACT_20260723.json"
PERMIT = FACTORY99 / "authorizations" / "PRM-100_THIRD_WAVE_FULL58_V128_EXECUTION_PERMIT_20260723.json"


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    doctor = subprocess.run([sys.executable, str(RUNNER), "doctor", "--config", str(CONFIG), "--contract", str(CONTRACT), "--permit", str(PERMIT)], capture_output=True, text=True, check=False)
    if doctor.returncode != 0:
        raise SystemExit(f"fresh doctor failed: {doctor.stderr[-400:]}")
    doctor_payload = json.loads(doctor.stdout)
    if doctor_payload.get("competing_python_processes"):
        raise SystemExit("fresh doctor found competing Python")
    rows = []
    for index, cell in enumerate(config["cells"], start=1):
        started = datetime.now(ZoneInfo("Asia/Seoul")).isoformat()
        command = [sys.executable, str(RUNNER), "run-cell", "--model", cell["model_id"], "--config", str(CONFIG), "--contract", str(CONTRACT), "--permit", str(PERMIT)]
        result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=45)
        payload = {}
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            pass
        status = payload.get("status", "failed")
        row = {
            "sequence": index, "model_id": cell["model_id"], "model_family": cell["model_family"],
            "started_at_kst": started, "returncode": result.returncode, "status": status,
            "runtime_s": payload.get("runtime_s", ""), "output_count": payload.get("output_count", ""),
            "peak_rss_gib": payload.get("peak_rss_gib", ""), "stderr_tail": result.stderr[-400:],
        }
        rows.append(row)
        pd.DataFrame(rows).to_csv(REPORTS / "PRM100_execution_ledger.csv", index=False, encoding="utf-8-sig")
        if result.returncode != 0 or status not in {"passed", "reused"}:
            atomic_json(REPORTS / "PRM100_execution_summary.json", {
                "status": "STOP", "completed": f"{sum(r['status'] in {'passed','reused'} for r in rows)}/58",
                "failed_model": cell["model_id"], "execution_performed": True, "merge_performed": False,
            })
            raise SystemExit(f"cell failed: {cell['model_id']}: {result.stderr[-400:]}")
    atomic_json(REPORTS / "PRM100_execution_summary.json", {
        "status": "PASS", "completed": "58/58", "execution_performed": True, "merge_performed": False,
        "expected_values_after_future_merge": 348, "doctor": doctor_payload,
    })
    print((REPORTS / "PRM100_execution_summary.json").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
