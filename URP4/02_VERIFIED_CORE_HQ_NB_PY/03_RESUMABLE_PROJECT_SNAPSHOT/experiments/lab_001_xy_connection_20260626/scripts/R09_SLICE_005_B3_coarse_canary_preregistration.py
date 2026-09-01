"""Freeze PRM-047 live-hash authority for exactly two B3 coarse canary attempts."""

from __future__ import annotations

import hashlib
import json
import platform
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import psutil

import T3P_mesh_native_grouped_evaluation_preregistration_no_fit as protected_engine


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
FACTORY = LAB / "factories" / "R09-SLICE-005"
CONTRACTS = FACTORY / "contracts"
REPORTS = FACTORY / "reports"
MERGE = FACTORY / "merge"
WORKER = LAB / "scripts" / "R09_SLICE_005_B3_coarse_canary_worker.py"
PARENT = CONTRACTS / "R09-SLICE-005_STRICT_CONVERGENCE_PREREGISTRATION_NOEXEC_20260721.json"
CONTROL = REPORTS / "R09-SLICE-005_control_summary_20260721.json"
SYNC = REPORTS / "R09-SLICE-005_official_sync_summary_20260721.json"
KST = timezone(timedelta(hours=9))


def now_kst() -> str:
    return datetime.now(KST).isoformat(timespec="seconds")


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1024*1024), b""):
            h.update(b)
    return h.hexdigest()


def asset(path: Path) -> dict:
    return {"path":rel(path), "bytes":path.stat().st_size, "sha256":sha(path)}


def write_csv(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, encoding="utf-8-sig", lineterminator="\n")


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8")


def main() -> None:
    if platform.python_version() != "3.12.12" or "KMK312" not in sys.executable:
        raise RuntimeError("KMK312 Python 3.12.12 required")
    for p in [PARENT, CONTROL, SYNC, WORKER]:
        if not p.is_file():
            raise FileNotFoundError(p)
    parent = json.loads(PARENT.read_text(encoding="utf-8"))
    control = json.loads(CONTROL.read_text(encoding="utf-8"))
    sync = json.loads(SYNC.read_text(encoding="utf-8"))
    if parent["preregistration_id"] != "PRM-046" or parent["execution_authorized"]:
        raise RuntimeError("PRM-046 state drift")
    if control["status"] != "approved_preregistration_only" or sync["status"] != "passed":
        raise RuntimeError("PRM-046 control/sync prerequisite failed")
    runtime_dir = FACTORY / "runtime"
    if runtime_dir.exists():
        raise RuntimeError("R09-SLICE-005 runtime already exists; audit before new authority")
    source = LAB / "data" / "processed" / "n40_all58_20260715" / "stl" / "B3__a272cdb922__N40.stl"
    expected_source_sha = "beb368e9c9945669cc202046802bd24ec15e70b61cd472ce061e2e482ba70afc"
    if sha(source) != expected_source_sha:
        raise RuntimeError("B3 source hash drift")
    vm = psutil.virtual_memory()
    disk = shutil.disk_usage(FACTORY)
    active = []
    for proc in psutil.process_iter(["pid","name","cmdline"]):
        try:
            cmd = " ".join(proc.info.get("cmdline") or [])
            name = str(proc.info.get("name") or "").lower()
            if (proc.info.get("pid") != __import__("os").getpid()
                    and name.startswith("python")
                    and "R09_SLICE_005_B3_coarse_canary_worker.py" in cmd):
                active.append(proc.info.get("pid"))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    preflight = {
        "memory_percent": float(vm.percent), "available_ram_bytes": int(vm.available),
        "disk_free_bytes": int(disk.free), "active_slice005_processes": active,
        "minimum_available_ram_bytes": 8*2**30, "minimum_disk_free_bytes": 10*2**30,
    }
    preflight["passed"] = vm.available >= 8*2**30 and disk.free >= 10*2**30 and not active
    if not preflight["passed"]:
        raise RuntimeError(f"resource/process preflight failed: {preflight}")
    protected = protected_engine.protected_post()
    if len(protected) != 29 or not protected.status.isin(["pass","pass_with_alias_lock"]).all():
        raise RuntimeError("protected asset preflight failed")

    contract_path = CONTRACTS / "R09-SLICE-005_B3_COARSE_DUPLICATE_CANARY_EXECUTION_20260721.json"
    config = {
        "axis":"z", "physical_size_mm":40.0, "slice_count":801, "slice_spacing_mm":0.05,
        "pixel_width":500, "pixel_height":500, "area_per_pixel_mm2":0.0064,
        "length_per_pixel_mm":0.08, "connectivity":8, "min_component_pixels":2,
        "endpoint_nudge_mm":1e-6, "png_compress_level":1,
    }
    payload = {
        "contract_version":"R09-SLICE-005-canary-v0.1", "preregistration_id":"PRM-047",
        "parent_preregistration_id":"PRM-046", "run_id":"R09-SLICE-005-B3-COARSE-CANARY-EXEC-001",
        "created_at_kst":now_kst(), "authority":"Chuck '다음 작업 ㄱㄱ' on 2026-07-21",
        "status":"authorized_canary_only", "execution_authorized":True,
        "authorized_attempts":["B3-COARSE-A","B3-COARSE-B"],
        "source":{"path":rel(source),"sha256":expected_source_sha}, "config":config,
        "execution_mode":"STREAMING", "worker_script":asset(WORKER),
        "parent_contract":asset(PARENT), "control_summary":asset(CONTROL), "sync_summary":asset(SYNC),
        "preflight":preflight,
        "resource_gates":{"per_attempt_seconds":900, "peak_rss_bytes":8*2**30,
                          "per_attempt_output_bytes":2*2**30, "total_output_bytes":5*2**30},
        "determinism_gates":{"primitive_table_sha_exact":True, "scalar_key_exact":True,
                             "scalar_max_abs_delta":1e-12, "qa_json_semantic_exact":True,
                             "readback_mismatch_sum":0, "png_remaining":0},
        "factory_unlock_rule":"both attempts and independent/control QA must pass; this contract never authorizes the remaining 32 cells",
        "failure_rule":"quarantine failed/partial attempt; do not overwrite or start full factory",
        "scientific_locks":{"excel_read":0,"target_read":0,"fit":0,"prediction":0,"feature_selection":0,
                            "formula_change":0,"source_change":0,"baseline_recompute":0,"other_models":0,"full_factory":0},
        "protected_assets_before":29,
    }
    write_json(contract_path, payload)
    checks = pd.DataFrame([
        ("PRE-001","PRM-046 frozen and control/sync passed",True),
        ("PRE-002","worker hash frozen",sha(WORKER)==payload["worker_script"]["sha256"]),
        ("PRE-003","B3 source exact",sha(source)==expected_source_sha),
        ("PRE-004","config is exactly 500x500/801/0.05",config["pixel_width"]==500 and config["slice_count"]==801 and config["slice_spacing_mm"]==0.05),
        ("PRE-005","only two attempts authorized",payload["authorized_attempts"]==["B3-COARSE-A","B3-COARSE-B"]),
        ("PRE-006","STREAMING required",payload["execution_mode"]=="STREAMING"),
        ("PRE-007","resource preflight",preflight["passed"]),
        ("PRE-008","protected 29/29",len(protected)==29),
        ("PRE-009","no Excel/y/modeling",all(payload["scientific_locks"][k]==0 for k in ["excel_read","target_read","fit","prediction","feature_selection"])),
        ("PRE-010","full factory remains locked",payload["scientific_locks"]["full_factory"]==0),
    ], columns=["gate_id","gate","passed"])
    qa_path = REPORTS / "R09-SLICE-005_B3_coarse_canary_preflight_QA_20260721.csv"
    write_csv(qa_path, checks)
    if not checks.passed.all():
        raise RuntimeError("PRM-047 preflight QA failed")
    report_path = LAB / "results" / "R09-20260721-SLICE-005_B3_COARSE_CANARY_EXECUTION_ADDENDUM.md"
    report_path.write_text(f"""# R09-SLICE-005 B3 coarse duplicate canary execution addendum

Date: 2026-07-21  
Contract: `PRM-047`  
Status: **exactly two B3 coarse attempts authorized**

Authorized configuration:

```text
B3 canonical N40 SHA: {expected_source_sha}
500×500 pixels / 801 slices / 0.05 mm / z
area per pixel: 0.0064 mm²
CC8 / min 2 / endpoint nudge 1e-6 mm
STREAMING saved-PNG readback then immediate deletion
attempts: B3-COARSE-A and B3-COARSE-B only
```

Both attempts must independently pass technical/resource gates and produce exact
primitive-table hashes. Nine scalar keys must match with maximum absolute delta
`<=1e-12`. Any failure quarantines the canary and keeps the 32-cell factory locked.

This addendum reads no Excel or y and authorizes no fit, formula change, baseline
recomputation, other model, or full factory execution.
""", encoding="utf-8")
    manifest = pd.DataFrame([asset(p) for p in [contract_path,qa_path,report_path,WORKER]])
    manifest_path = MERGE / "R09-SLICE-005_B3_coarse_canary_preregistration_manifest_20260721.csv"
    write_csv(manifest_path,manifest)
    print(json.dumps({"status":"passed","preregistration_id":"PRM-047","preflight":"10/10",
                      "available_ram_gib":round(vm.available/2**30,2),"disk_free_gib":round(disk.free/2**30,2),
                      "authorized_attempts":payload["authorized_attempts"]},ensure_ascii=False))


if __name__ == "__main__":
    main()
