from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd

ROOT=Path(__file__).resolve().parents[3]
LAB=ROOT/"experiments"/"lab_001_xy_connection_20260626"
FACTORY=LAB/"factories"/"PRM-098"; REPORTS=FACTORY/"reports"; TABLES=LAB/"reports"/"tables"
GROUPS=["LIT-X006","LIT-X008","LIT-X019","LIT-X024","LIT-X028","LIT-X031"]


def main():
    truth=pd.read_csv(REPORTS/"PRM098_synthetic_group_gate.csv")
    limits=pd.read_csv(TABLES/"PRM097_resource_stop_policy.csv").set_index("candidate_group_id")
    rows=[]
    for group in GROUPS:
        if truth.loc[truth.candidate_group_id.eq(group),"group_gate"].iloc[0]!="PASS":
            rows.append({"candidate_group_id":group,"model_id":"B3","resolution_id":"V064","status":"not_run_synthetic_hold","returncode":"","runtime_s":"","peak_rss_gib":"","stdout_tail":""}); continue
        cmd=[sys.executable,str(LAB/"scripts"/"PRM098_run_cell.py"),"--group",group,"--model","B3","--resolution","V064"]
        t=time.perf_counter()
        try:
            run=subprocess.run(cmd,capture_output=True,text=True,timeout=float(limits.loc[group,"max_seconds_per_cell"])+30)
            status="passed" if run.returncode==0 else "failed"
            meta_path=FACTORY/"intermediate"/group/"B3"/"V064"/"done.json"
            meta=json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
            rows.append({"candidate_group_id":group,"model_id":"B3","resolution_id":"V064","status":status,"returncode":run.returncode,"runtime_s":meta.get("runtime_s",time.perf_counter()-t),"peak_rss_gib":meta.get("peak_rss_gib",""),"stdout_tail":run.stdout[-1000:]})
        except subprocess.TimeoutExpired:
            rows.append({"candidate_group_id":group,"model_id":"B3","resolution_id":"V064","status":"timeout","returncode":"","runtime_s":time.perf_counter()-t,"peak_rss_gib":"","stdout_tail":"subprocess timeout"})
    result=pd.DataFrame(rows); result["group_gate"]=result.status.map(lambda x:"PASS" if x=="passed" else "HOLD")
    result.to_csv(REPORTS/"PRM098_V064_cost_canary.csv",index=False,encoding="utf-8-sig",lineterminator="\n")
    summary={"status":"PASS" if result.group_gate.eq("PASS").all() else "PARTIAL","groups_passed":f"{result.group_gate.eq('PASS').sum()}/{len(result)}","total_runtime_s":float(pd.to_numeric(result.runtime_s,errors="coerce").sum())}
    (REPORTS/"PRM098_V064_cost_canary_summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary)); print(result[["candidate_group_id","status","runtime_s","peak_rss_gib"]].to_string(index=False))


if __name__=="__main__":main()
