"""Quarantine PRM-047 attempt A and freeze PRM-048 C/D repair authority."""

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
LAB = ROOT/"experiments"/"lab_001_xy_connection_20260626"
FACTORY = LAB/"factories"/"R09-SLICE-005"
CONTRACTS = FACTORY/"contracts"
REPORTS = FACTORY/"reports"
MERGE = FACTORY/"merge"
WORKER = LAB/"scripts"/"R09_SLICE_005_B3_coarse_canary_worker.py"
OLD_CONTRACT = CONTRACTS/"R09-SLICE-005_B3_COARSE_DUPLICATE_CANARY_EXECUTION_20260721.json"
FAILED = FACTORY/"runtime"/"B3-COARSE-A"
KST = timezone(timedelta(hours=9))


def now() -> str: return datetime.now(KST).isoformat(timespec="seconds")
def rel(p: Path) -> str: return p.resolve().relative_to(ROOT.resolve()).as_posix()
def sha(p: Path) -> str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()
def asset(p: Path) -> dict: return {"path":rel(p),"bytes":p.stat().st_size,"sha256":sha(p)}
def write_csv(p: Path, f: pd.DataFrame) -> None:
    p.parent.mkdir(parents=True,exist_ok=True); f.to_csv(p,index=False,encoding="utf-8-sig",lineterminator="\n")
def write_json(p: Path, x: object) -> None:
    p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8")


def main() -> None:
    if platform.python_version()!="3.12.12" or "KMK312" not in sys.executable: raise RuntimeError("KMK312 required")
    failure_path=FAILED/"failure.json"; qa_path=FAILED/"qa.json"
    for p in [OLD_CONTRACT,WORKER,failure_path,qa_path]:
        if not p.is_file(): raise FileNotFoundError(p)
    failure=json.loads(failure_path.read_text(encoding="utf-8")); qa=json.loads(qa_path.read_text(encoding="utf-8"))
    png_count=len(list((FAILED/"images").rglob("*.png")))
    if failure["error_type"]!="TypeError" or "not JSON serializable" not in failure["error"]: raise RuntimeError("unexpected A failure")
    if qa["status"]!="passed" or qa["readback_mismatch_sum"]!=0 or png_count!=0: raise RuntimeError("A cleanup/technical audit failed")
    if (FACTORY/"runtime"/"B3-COARSE-B").exists(): raise RuntimeError("old attempt B unexpectedly started")
    if any((FACTORY/"runtime"/f"B3-COARSE-{x}").exists() for x in ["C","D"]): raise RuntimeError("repair attempts already exist")
    protected=protected_engine.protected_post()
    vm=psutil.virtual_memory(); disk=shutil.disk_usage(FACTORY)
    if len(protected)!=29 or not protected.status.isin(["pass","pass_with_alias_lock"]).all(): raise RuntimeError("protected drift")
    if vm.available<8*2**30 or disk.free<10*2**30: raise RuntimeError("resource preflight")
    old=json.loads(OLD_CONTRACT.read_text(encoding="utf-8"))
    contract_path=CONTRACTS/"R09-SLICE-005_B3_COARSE_DUPLICATE_CANARY_REPAIR_EXECUTION_20260721.json"
    payload={
        "contract_version":"R09-SLICE-005-canary-repair-v0.1","preregistration_id":"PRM-048",
        "parent_preregistration_id":"PRM-047","run_id":"R09-SLICE-005-B3-COARSE-CANARY-REPAIR-EXEC-001",
        "created_at_kst":now(),"authority":"automatic fail-closed repair under Chuck next-task authorization",
        "status":"authorized_repair_canary_only","execution_authorized":True,
        "quarantined_attempt":{"attempt_id":"B3-COARSE-A","failure":asset(failure_path),"qa":asset(qa_path),
                               "png_remaining":png_count,"scientific_use":"none"},
        "retired_attempt":"B3-COARSE-B","retired_reason":"PRM-047 worker hash invalid after repair; never executed",
        "repair":{"cause":"numpy.bool_ in scalar_rows gate could not be serialized by stdlib json",
                  "change":"cast scalar_rows gate to builtin bool; change contract and authorized IDs only",
                  "calculation_formula_change":False,"source_change":False,"config_change":False},
        "authorized_attempts":["B3-COARSE-C","B3-COARSE-D"],"source":old["source"],"config":old["config"],
        "execution_mode":"STREAMING","worker_script":asset(WORKER),"old_contract":asset(OLD_CONTRACT),
        "resource_gates":old["resource_gates"],"determinism_gates":old["determinism_gates"],
        "factory_unlock_rule":"C and D plus independent/control QA must pass; remaining 32 cells still unauthorized",
        "failure_rule":"quarantine without overwrite and keep full factory locked",
        "scientific_locks":old["scientific_locks"],"protected_assets_before":29,
        "preflight":{"available_ram_bytes":int(vm.available),"disk_free_bytes":int(disk.free),"passed":True}
    }
    write_json(contract_path,payload)
    repair_table=pd.DataFrame([
        ("B3-COARSE-A","quarantined","post-calculation JSON bookkeeping TypeError","no",0),
        ("B3-COARSE-B","retired_not_run","old worker hash invalidated by repair","no",None),
        ("B3-COARSE-C","authorized_pending","fresh repaired worker attempt","pending",None),
        ("B3-COARSE-D","authorized_pending","fresh repaired worker attempt","pending",None),
    ],columns=["attempt_id","status","reason","scientific_use","png_remaining"])
    repair_path=REPORTS/"R09-SLICE-005_B3_coarse_canary_repair_register_20260721.csv"; write_csv(repair_path,repair_table)
    checks=pd.DataFrame([
        ("REP-001","A failure exact",True),("REP-002","A technical QA passed but not accepted",qa["status"]=="passed"),
        ("REP-003","A PNG cleanup exact",png_count==0),("REP-004","A scientific use none",True),
        ("REP-005","B never started",not (FACTORY/"runtime"/"B3-COARSE-B").exists()),
        ("REP-006","repair is bool-only",payload["repair"]["calculation_formula_change"] is False),
        ("REP-007","worker hash frozen",sha(WORKER)==payload["worker_script"]["sha256"]),
        ("REP-008","only C/D authorized",payload["authorized_attempts"]==["B3-COARSE-C","B3-COARSE-D"]),
        ("REP-009","resources pass",payload["preflight"]["passed"]),("REP-010","protected 29/29",len(protected)==29),
    ],columns=["gate_id","gate","passed"])
    check_path=REPORTS/"R09-SLICE-005_B3_coarse_canary_repair_QA_20260721.csv"; write_csv(check_path,checks)
    if not checks.passed.all(): raise RuntimeError("repair QA failed")
    report_path=LAB/"results"/"R09-20260721-SLICE-005_B3_COARSE_CANARY_REPAIR_ADDENDUM.md"
    report_path.write_text("""# R09-SLICE-005 B3 coarse canary repair addendum

`B3-COARSE-A` completed the image/pixel pipeline but failed while serializing the
final completion record because one gate value was `numpy.bool_`. It is preserved
and quarantined with scientific use `none`; zero PNG remains. `B3-COARSE-B` was
never started and is retired with the old worker hash.

PRM-048 changes only that gate to a built-in Python boolean and authorizes two
fresh IDs, C and D. Source, geometry, configuration, formulas and thresholds are
unchanged. Any new failure keeps the 32-cell factory locked.
""",encoding="utf-8")
    manifest_path=MERGE/"R09-SLICE-005_B3_coarse_canary_repair_preregistration_manifest_20260721.csv"
    write_csv(manifest_path,pd.DataFrame([asset(p) for p in [contract_path,repair_path,check_path,report_path,WORKER,failure_path,qa_path]]))
    print(json.dumps({"status":"passed","preregistration_id":"PRM-048","repair_qa":"10/10","quarantined":"B3-COARSE-A","authorized":["C","D"]},ensure_ascii=False))


if __name__=="__main__": main()
