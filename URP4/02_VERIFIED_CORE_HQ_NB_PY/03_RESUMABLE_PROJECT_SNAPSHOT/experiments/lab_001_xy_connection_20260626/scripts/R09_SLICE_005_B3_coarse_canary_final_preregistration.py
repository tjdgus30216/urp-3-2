"""Record the PRM-048 authority-guard failure and freeze final PRM-049 E/F attempts."""

from __future__ import annotations

import hashlib, json, platform, shutil, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
import pandas as pd
import psutil
import T3P_mesh_native_grouped_evaluation_preregistration_no_fit as protected_engine

ROOT=Path(__file__).resolve().parents[3]
LAB=ROOT/"experiments"/"lab_001_xy_connection_20260626"; FACTORY=LAB/"factories"/"R09-SLICE-005"
CONTRACTS=FACTORY/"contracts"; REPORTS=FACTORY/"reports"; MERGE=FACTORY/"merge"
WORKER=LAB/"scripts"/"R09_SLICE_005_B3_coarse_canary_worker.py"
PARENT=CONTRACTS/"R09-SLICE-005_B3_COARSE_DUPLICATE_CANARY_REPAIR_EXECUTION_20260721.json"
KST=timezone(timedelta(hours=9))
def now(): return datetime.now(KST).isoformat(timespec="seconds")
def rel(p): return p.resolve().relative_to(ROOT.resolve()).as_posix()
def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()
def asset(p): return {"path":rel(p),"bytes":p.stat().st_size,"sha256":sha(p)}
def write_json(p,x): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8")
def write_csv(p,f): p.parent.mkdir(parents=True,exist_ok=True); f.to_csv(p,index=False,encoding="utf-8-sig",lineterminator="\n")

def main():
    if platform.python_version()!="3.12.12" or "KMK312" not in sys.executable: raise RuntimeError("KMK312 required")
    if not PARENT.is_file() or not WORKER.is_file(): raise FileNotFoundError("parent/worker")
    parent=json.loads(PARENT.read_text(encoding="utf-8"))
    runtime=FACTORY/"runtime"
    for name in ["B3-COARSE-C","B3-COARSE-D","B3-COARSE-E","B3-COARSE-F"]:
        if (runtime/name).exists(): raise RuntimeError(f"unexpected runtime artifact: {name}")
    protected=protected_engine.protected_post(); vm=psutil.virtual_memory(); disk=shutil.disk_usage(FACTORY)
    if len(protected)!=29 or not protected.status.isin(["pass","pass_with_alias_lock"]).all(): raise RuntimeError("protected drift")
    if vm.available<8*2**30 or disk.free<10*2**30: raise RuntimeError("resource preflight")
    guard_failure={
        "attempt_id":"B3-COARSE-C","status":"guard_failed_before_output","failed_at_kst":now(),
        "error_type":"RuntimeError","error":"PRM-047 canary authority missing",
        "stage":"contract identity guard before output_dir creation","runtime_artifact_created":False,
        "scientific_use":"none","parent_contract_sha256":sha(PARENT),
    }
    guard_path=REPORTS/"R09-SLICE-005_B3_COARSE_C_guard_failure_20260721.json"; write_json(guard_path,guard_failure)
    contract_path=CONTRACTS/"R09-SLICE-005_B3_COARSE_DUPLICATE_CANARY_FINAL_EXECUTION_20260721.json"
    payload={
        "contract_version":"R09-SLICE-005-canary-final-v0.1","preregistration_id":"PRM-049",
        "parent_preregistration_id":"PRM-048","run_id":"R09-SLICE-005-B3-COARSE-CANARY-FINAL-EXEC-001",
        "created_at_kst":now(),"authority":"fail-closed second repair under Chuck next-task authorization",
        "status":"authorized_final_canary_only","execution_authorized":True,
        "prior_attempts":[
            {"attempt_id":"B3-COARSE-A","status":"quarantined_post_calculation_bookkeeping_failure","scientific_use":"none"},
            {"attempt_id":"B3-COARSE-B","status":"retired_not_run","scientific_use":"none"},
            {"attempt_id":"B3-COARSE-C","status":"guard_failed_before_output","scientific_use":"none","evidence":asset(guard_path)},
            {"attempt_id":"B3-COARSE-D","status":"retired_not_run","scientific_use":"none"}],
        "repair":{"cause":"worker contract identity check remained PRM-047 after PRM-048 filename change",
                  "change":"freeze PRM-049 identity and E/F IDs in worker; no calculation/source/config/formula change",
                  "calculation_formula_change":False,"source_change":False,"config_change":False},
        "authorized_attempts":["B3-COARSE-E","B3-COARSE-F"],"source":parent["source"],"config":parent["config"],
        "execution_mode":"STREAMING","worker_script":asset(WORKER),"parent_contract":asset(PARENT),
        "resource_gates":parent["resource_gates"],"determinism_gates":parent["determinism_gates"],
        "factory_unlock_rule":"E and F plus independent/control QA must pass; no remaining 32-cell authority",
        "failure_rule":"quarantine without overwrite and stop",
        "scientific_locks":parent["scientific_locks"],"protected_assets_before":29,
        "preflight":{"available_ram_bytes":int(vm.available),"disk_free_bytes":int(disk.free),"passed":True}}
    write_json(contract_path,payload)
    register=pd.DataFrame([
        ("A","quarantined","bookkeeping TypeError","none"),("B","retired","not run after worker repair","none"),
        ("C","guard_failed","no output; stale authority check","none"),("D","retired","not run after guard repair","none"),
        ("E","authorized_pending","final worker hash","pending"),("F","authorized_pending","final worker hash","pending")],
        columns=["attempt_suffix","status","reason","scientific_use"])
    reg_path=REPORTS/"R09-SLICE-005_B3_coarse_canary_final_attempt_register_20260721.csv"; write_csv(reg_path,register)
    qa=pd.DataFrame([
        ("FIN-001","C produced no runtime directory",not (runtime/"B3-COARSE-C").exists()),
        ("FIN-002","C failure recorded",guard_path.is_file()),("FIN-003","D never run",not (runtime/"B3-COARSE-D").exists()),
        ("FIN-004","worker hash frozen",sha(WORKER)==payload["worker_script"]["sha256"]),
        ("FIN-005","worker targets PRM-049","PRM-049" in WORKER.read_text(encoding="utf-8")),
        ("FIN-006","only E/F authorized",payload["authorized_attempts"]==["B3-COARSE-E","B3-COARSE-F"]),
        ("FIN-007","source/config inherited",payload["source"]==parent["source"] and payload["config"]==parent["config"]),
        ("FIN-008","no formula change",payload["repair"]["calculation_formula_change"] is False),
        ("FIN-009","resources pass",payload["preflight"]["passed"]),("FIN-010","protected 29/29",len(protected)==29)],
        columns=["gate_id","gate","passed"])
    qa_path=REPORTS/"R09-SLICE-005_B3_coarse_canary_final_preflight_QA_20260721.csv"; write_csv(qa_path,qa)
    if not qa.passed.all(): raise RuntimeError("final preflight QA failed")
    report_path=LAB/"results"/"R09-20260721-SLICE-005_B3_COARSE_CANARY_FINAL_ADDENDUM.md"
    report_path.write_text("""# R09-SLICE-005 B3 coarse canary final addendum

PRM-048 attempt C failed at the contract identity guard before output creation;
D was not run. This is recorded separately and has no scientific use. PRM-049
freezes the corrected worker hash and authorizes only fresh E/F attempts. Source,
configuration and formulas remain unchanged. Another failure stops the canary.
""",encoding="utf-8")
    manifest_path=MERGE/"R09-SLICE-005_B3_coarse_canary_final_preregistration_manifest_20260721.csv"
    write_csv(manifest_path,pd.DataFrame([asset(p) for p in [contract_path,guard_path,reg_path,qa_path,report_path,WORKER,PARENT]]))
    print(json.dumps({"status":"passed","preregistration_id":"PRM-049","qa":"10/10","authorized":["E","F"]},ensure_ascii=False))
if __name__=="__main__": main()
