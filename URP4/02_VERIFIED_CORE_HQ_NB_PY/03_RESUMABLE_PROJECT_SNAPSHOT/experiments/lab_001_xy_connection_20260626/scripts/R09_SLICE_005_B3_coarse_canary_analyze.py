"""Analyze PRM-049 E/F canary parity and preserve prior failed attempts."""
from __future__ import annotations
import hashlib,json,platform,sys
from datetime import datetime,timedelta,timezone
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import T3P_mesh_native_grouped_evaluation_preregistration_no_fit as protected_engine

ROOT=Path(__file__).resolve().parents[3]; LAB=ROOT/"experiments"/"lab_001_xy_connection_20260626"
FACTORY=LAB/"factories"/"R09-SLICE-005"; RUNTIME=FACTORY/"runtime"; REPORTS=FACTORY/"reports"; FIGURES=FACTORY/"figures"; MERGE=FACTORY/"merge"
TABLES=LAB/"reports"/"tables"; RESULTS=LAB/"results"; KST=timezone(timedelta(hours=9))
CONTRACT=FACTORY/"contracts"/"R09-SLICE-005_B3_COARSE_DUPLICATE_CANARY_FINAL_EXECUTION_20260721.json"
def now(): return datetime.now(KST).isoformat(timespec="seconds")
def rel(p): return p.resolve().relative_to(ROOT.resolve()).as_posix()
def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()
def asset(p):return {"path":rel(p),"bytes":p.stat().st_size,"sha256":sha(p)}
def write_csv(p,f):p.parent.mkdir(parents=True,exist_ok=True);f.to_csv(p,index=False,encoding="utf-8-sig",lineterminator="\n")
def write_json(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8")

def main():
    if platform.python_version()!="3.12.12" or "KMK312" not in sys.executable:raise RuntimeError("KMK312 required")
    contract=json.loads(CONTRACT.read_text(encoding="utf-8")); dirs={x:RUNTIME/f"B3-COARSE-{x}" for x in ["E","F"]}
    comp={x:json.loads((p/"complete.json").read_text(encoding="utf-8")) for x,p in dirs.items()}
    if any(c["status"]!="passed" for c in comp.values()):raise RuntimeError("E/F not passed")
    files=["slice_pixel_count_table.csv","overlay_pixel_table.csv","slice_component_table.csv","overlay_component_table.csv","descriptor_result.csv"]
    parity=[]
    for f in files:
        pe=dirs["E"]/"tables"/f; pf=dirs["F"]/"tables"/f
        fe=pd.read_csv(pe); ff=pd.read_csv(pf)
        parity.append({"table":f,"rows_E":len(fe),"rows_F":len(ff),"columns_exact":fe.columns.tolist()==ff.columns.tolist(),
                       "sha_E":sha(pe),"sha_F":sha(pf),"sha_exact":sha(pe)==sha(pf),"status":"pass" if sha(pe)==sha(pf) else "fail"})
    parity_df=pd.DataFrame(parity); parity_path=TABLES/"R09-SLICE-005_B3_coarse_canary_table_parity_20260721.csv";write_csv(parity_path,parity_df)
    se=pd.read_csv(dirs["E"]/"tables"/"descriptor_result.csv");sf=pd.read_csv(dirs["F"]/"tables"/"descriptor_result.csv")
    keys=["model_id","formula_id","descriptor","statistic","unit","population_n","scientific_state","config_sha256"]
    merged=se.merge(sf,on=keys,suffixes=("_E","_F"),how="outer",indicator=True)
    merged["abs_delta"]=(merged.value_E-merged.value_F).abs();merged["within_1e12"]=merged.abs_delta.le(1e-12)&merged._merge.eq("both")
    scalar_path=TABLES/"R09-SLICE-005_B3_coarse_canary_scalar_parity_20260721.csv";write_csv(scalar_path,merged)
    resources=pd.DataFrame([{"attempt":x,"runtime_seconds":c["runtime_seconds"],"peak_rss_gib":c["resource"]["peak_rss_gib"],
                             "peak_system_memory_percent":c["resource"]["peak_system_memory_percent"],"output_mib":c["resource"]["output_bytes"]/2**20,
                             "png_created":c["qa"]["png_created"],"png_deleted":c["qa"]["png_deleted"],"remaining_png":c["qa"]["remaining_png"],
                             "readback_mismatch_sum":c["qa"]["readback_mismatch_sum"],"all_worker_gates":all(c["gates"].values())} for x,c in comp.items()])
    resource_path=TABLES/"R09-SLICE-005_B3_coarse_canary_resource_summary_20260721.csv";write_csv(resource_path,resources)
    attempts=pd.DataFrame([
        ("B3-COARSE-A","quarantined","post-calculation JSON serialization defect","none",True,0),
        ("B3-COARSE-B","retired_not_run","worker hash changed after defect repair","none",False,None),
        ("B3-COARSE-C","guard_failed_before_output","stale contract identity guard","none",False,None),
        ("B3-COARSE-D","retired_not_run","worker hash changed after guard repair","none",False,None),
        ("B3-COARSE-E","passed","PRM-049 final worker","canary_evidence",True,0),
        ("B3-COARSE-F","passed","PRM-049 final worker","canary_evidence",True,0)],
        columns=["attempt_id","status","reason","scientific_use","runtime_artifact_present","png_remaining"])
    attempt_path=TABLES/"R09-SLICE-005_B3_coarse_canary_attempt_ledger_20260721.csv";write_csv(attempt_path,attempts)
    protected=protected_engine.protected_post()
    qa=pd.DataFrame([
        ("EXE-001","PRM-049 exact",contract["preregistration_id"]=="PRM-049"),("EXE-002","E/F complete pass",all(c["status"]=="passed" for c in comp.values())),
        ("EXE-003","five table hashes exact",len(parity_df)==5 and parity_df.sha_exact.all()),("EXE-004","nine scalar keys exact",len(merged)==9 and merged._merge.eq("both").all()),
        ("EXE-005","scalar max delta <=1e-12",float(merged.abs_delta.max())<=1e-12),("EXE-006","E technical gate",all(comp["E"]["gates"].values())),
        ("EXE-007","F technical gate",all(comp["F"]["gates"].values())),("EXE-008","readback zero",resources.readback_mismatch_sum.eq(0).all()),
        ("EXE-009","PNG accounting exact",((resources.png_created==1601)&(resources.png_deleted==1601)&(resources.remaining_png==0)).all()),
        ("EXE-010","runtime under 900 s",resources.runtime_seconds.le(900).all()),("EXE-011","RSS under 8 GiB",resources.peak_rss_gib.le(8).all()),
        ("EXE-012","output under 2 GiB each",resources.output_mib.le(2048).all()),("EXE-013","prior failures explicitly non-scientific",attempts.loc[attempts.attempt_id.isin(["B3-COARSE-A","B3-COARSE-C"]),"scientific_use"].eq("none").all()),
        ("EXE-014","no B/D output",not (RUNTIME/"B3-COARSE-B").exists() and not (RUNTIME/"B3-COARSE-D").exists()),
        ("EXE-015","protected 29/29",len(protected)==29 and protected.status.isin(["pass","pass_with_alias_lock"]).all()),
        ("EXE-016","full factory still unauthorized",contract["scientific_locks"]["full_factory"]==0)],columns=["gate_id","gate","passed"])
    qa_path=REPORTS/"R09-SLICE-005_B3_coarse_canary_execution_QA_20260721.csv";write_csv(qa_path,qa)
    if not qa.passed.all():raise RuntimeError(f"execution QA failed {qa.loc[~qa.passed,'gate_id'].tolist()}")
    fig,axes=plt.subplots(1,3,figsize=(12.5,4));colors=["#2563eb","#16a34a"]
    axes[0].bar(resources.attempt,resources.runtime_seconds,color=colors);axes[0].set_title("Runtime");axes[0].set_ylabel("seconds")
    axes[1].bar(resources.attempt,resources.peak_rss_gib,color=colors);axes[1].set_title("Peak RSS");axes[1].set_ylabel("GiB")
    axes[2].bar(resources.attempt,resources.output_mib,color=colors);axes[2].set_title("Retained output");axes[2].set_ylabel("MiB")
    fig.suptitle("B3 500×500×801 duplicate STREAMING canary — E/F",fontsize=14,weight="bold")
    fig.text(.5,.01,"5/5 table SHA exact · 9/9 scalars exact · 1601/1601 PNG deleted per attempt",ha="center",color="#166534")
    fig.tight_layout(rect=[0,.05,1,.93]);figure=FIGURES/"R09-SLICE-005_B3_coarse_canary_resource_parity_20260721.png";fig.savefig(figure,dpi=180,bbox_inches="tight");plt.close(fig)
    summary={"run_id":"R09-SLICE-005-B3-COARSE-CANARY-001","created_at_kst":now(),"status":"passed",
             "accepted_attempts":["B3-COARSE-E","B3-COARSE-F"],"quarantined_attempts":["B3-COARSE-A","B3-COARSE-C"],
             "table_sha_parity":"5/5","scalar_parity":"9/9","scalar_max_abs_delta":float(merged.abs_delta.max()),
             "runtime_seconds_E":float(resources.loc[resources.attempt.eq("E"),"runtime_seconds"].iloc[0]),
             "runtime_seconds_F":float(resources.loc[resources.attempt.eq("F"),"runtime_seconds"].iloc[0]),
             "peak_rss_gib_max":float(resources.peak_rss_gib.max()),"output_mib_each":float(resources.output_mib.max()),
             "png_created_deleted_each":"1601/1601","readback_mismatch_sum":0,"execution_qa":"16/16","protected_assets":"29/29",
             "full_factory_authorized":False,"next":"independent primitive/scalar replay then control review"}
    summary_path=REPORTS/"R09-SLICE-005_B3_coarse_canary_execution_summary_20260721.json";write_json(summary_path,summary)
    report_path=RESULTS/"R09-20260721-SLICE-005_B3_COARSE_DUPLICATE_CANARY_RESULT.md"
    report_path.write_text(f"""# R09-SLICE-005 B3 coarse duplicate canary result

## Outcome

Final PRM-049 attempts E and F both passed. All five retained CSVs have identical
SHA-256 and all nine F001-F008 scalar rows are exact (`max abs delta = {summary['scalar_max_abs_delta']}`).

```text
runtime E/F: {summary['runtime_seconds_E']:.3f} / {summary['runtime_seconds_F']:.3f} s
peak RSS max: {summary['peak_rss_gib_max']:.3f} GiB
retained output each: {summary['output_mib_each']:.3f} MiB
PNG per attempt: 1601 created / 1601 deleted / 0 remaining
readback mismatch: 0
```

A and C remain quarantined with scientific use none; B and D were never run.
The canary supports deterministic/resource readiness only. It does not establish
pixel convergence and does not authorize the remaining 32 cells.
""",encoding="utf-8")
    outputs=[parity_path,scalar_path,resource_path,attempt_path,qa_path,figure,summary_path,report_path]
    manifest_path=MERGE/"R09-SLICE-005_B3_coarse_canary_execution_manifest_20260721.csv";write_csv(manifest_path,pd.DataFrame([asset(p) for p in outputs]))
    print(json.dumps(summary,ensure_ascii=False))
if __name__=="__main__":main()
