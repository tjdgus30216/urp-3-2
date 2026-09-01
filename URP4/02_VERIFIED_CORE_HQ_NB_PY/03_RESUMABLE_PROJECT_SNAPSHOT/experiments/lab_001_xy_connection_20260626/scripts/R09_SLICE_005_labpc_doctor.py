from __future__ import annotations

import argparse
import importlib
import json
import os
import platform
import shutil
import socket
import sys
from pathlib import Path

import psutil

from R09_SLICE_005_labpc_common import (
    atomic_json,
    now_kst,
    package_root,
    read_csv,
    read_json,
    sha256,
    verify_manifest,
    write_csv,
)


ROOT = package_root()
CONTRACT_PATH = ROOT / "contracts/PRM-050_R09-SLICE-005_LABPC_EXECUTION.json"
MANIFEST_PATH = ROOT / "PACKAGE_MANIFEST.csv"
MATRIX_PATH = ROOT / "config/pending_32_job_matrix.csv"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--authorize", action="store_true")
    args = parser.parse_args()
    contract = read_json(CONTRACT_PATH)
    manifest_rows, manifest_ok = verify_manifest(ROOT, MANIFEST_PATH)
    jobs = read_csv(MATRIX_PATH)
    disk = shutil.disk_usage(ROOT)
    memory = psutil.virtual_memory()
    imports: dict[str, bool] = {}
    for name in ["numpy", "pandas", "PIL", "cv2", "psutil"]:
        try:
            importlib.import_module(name)
            imports[name] = True
        except Exception:
            imports[name] = False

    source_checks = []
    for model_id, metadata in contract["sources"].items():
        source = ROOT / metadata["path"]
        source_checks.append(
            source.is_file() and source.stat().st_size == metadata["bytes"]
            and sha256(source) == metadata["sha256"]
        )
    baseline_checks = []
    for model_id, metadata in contract["baselines"].items():
        path = ROOT / metadata["descriptor_path"]
        baseline_checks.append(path.is_file() and sha256(path) == metadata["descriptor_sha256"])

    code_checks = []
    for name, expected in contract["code_hashes"].items():
        path = ROOT / f"factory/R09_SLICE_005_labpc_{name}.py"
        code_checks.append(path.is_file() and sha256(path) == expected)

    checks = [
        ("DOC-001", "Python 3.12.12", platform.python_version() == "3.12.12"),
        ("DOC-002", "KMK312 executable identity", "KMK312" in str(Path(sys.executable))),
        ("DOC-003", "required imports", all(imports.values())),
        ("DOC-004", "static contract PRM-050", contract.get("preregistration_id") == "PRM-050"),
        ("DOC-005", "execution condition enabled", contract.get("execution_authorized") is True),
        ("DOC-006", "immutable package manifest", manifest_ok),
        ("DOC-007", "32 pending jobs exact", len(jobs) == 32 and len({row["execution_cell_id"] for row in jobs}) == 32),
        ("DOC-008", "8 canonical sources exact", len(source_checks) == 8 and all(source_checks)),
        ("DOC-009", "8 frozen baseline descriptors exact", len(baseline_checks) == 8 and all(baseline_checks)),
        ("DOC-010", "factory code hashes exact", len(code_checks) == len(contract["code_hashes"]) and all(code_checks)),
        ("DOC-011", "available RAM gate", memory.available >= contract["resource_gates"]["minimum_available_ram_bytes"]),
        ("DOC-012", "free local disk gate", disk.free >= contract["resource_gates"]["minimum_free_disk_bytes"]),
        ("DOC-013", "result root writable", os.access(ROOT, os.W_OK)),
        ("DOC-014", "baseline recompute prohibited", contract["scientific_locks"]["baseline_recompute"] == 0),
        ("DOC-015", "Excel/y/modeling locked", all(contract["scientific_locks"][key] == 0 for key in ("excel_read", "target_read", "fit", "prediction", "feature_selection"))),
    ]
    rows = [
        {"gate_id": gate_id, "gate": gate, "passed": bool(passed)}
        for gate_id, gate, passed in checks
    ]
    preflight = ROOT / "preflight"
    preflight.mkdir(parents=True, exist_ok=True)
    write_csv(preflight / "doctor_QA.csv", ["gate_id", "gate", "passed"], rows)
    report = {
        "run_id": "R09-SLICE-005-LABPC-DOCTOR-001",
        "created_at_kst": now_kst(),
        "status": "passed" if all(value for _, _, value in checks) else "failed",
        "qa": f"{sum(bool(value) for _, _, value in checks)}/{len(checks)}",
        "hostname": socket.gethostname(),
        "python": platform.python_version(),
        "executable": str(Path(sys.executable).resolve()),
        "available_ram_gib": memory.available / 2**30,
        "total_ram_gib": memory.total / 2**30,
        "free_disk_gib": disk.free / 2**30,
        "package_root": str(ROOT),
        "imports": imports,
        "manifest_rows": len(manifest_rows),
        "jobs": len(jobs),
        "authorization_requested": args.authorize,
    }
    atomic_json(preflight / "doctor_report.json", report)
    if report["status"] != "passed":
        print(json.dumps(report, ensure_ascii=False))
        raise SystemExit(1)
    if args.authorize:
        atomic_json(
            preflight / "runtime_authorization.json",
            {
                "authorization_id": "PRM-050-LIVE-AUTH-001",
                "created_at_kst": now_kst(),
                "status": "passed_and_authorized",
                "hostname": socket.gethostname(),
                "python": platform.python_version(),
                "executable": str(Path(sys.executable).resolve()),
                "static_contract_sha256": sha256(CONTRACT_PATH),
                "package_manifest_sha256": sha256(MANIFEST_PATH),
                "doctor_report_sha256": sha256(preflight / "doctor_report.json"),
                "job_count": 32,
                "execution_scope": "pending 32 cells only; one model per process; max two immutable attempts",
            },
        )
        report["runtime_authorization"] = "created"
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
