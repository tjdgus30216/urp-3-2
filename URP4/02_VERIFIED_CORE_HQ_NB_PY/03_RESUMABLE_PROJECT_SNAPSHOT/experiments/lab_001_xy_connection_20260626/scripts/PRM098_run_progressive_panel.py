from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd

ROOT=Path(__file__).resolve().parents[3]; LAB=ROOT/"experiments"/"lab_001_xy_connection_20260626"; TABLES=LAB/"reports"/"tables"; FACTORY=LAB/"factories"/"PRM-098"; REPORTS=FACTORY/"reports"
GROUPS=["LIT-X006","LIT-X008","LIT-X019","LIT-X024","LIT-X028","LIT-X031"]; MODELS=["B3","C1","L1","F1","T8","T9"]; RESOLUTIONS=["V064","V096","V128","V192"]


def sha256(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()


def valid_done(path:Path,mask_hash:str,runner_hash:str,library_hash:str):
    if not path.exists():return False,None
    try:m=json.loads(path.read_text(encoding="utf-8"))
    except Exception:return False,None
    return m.get("status")=="passed" and m.get("mask_sha256")==mask_hash and m.get("runner_sha256")==runner_hash and m.get("formula_library_sha256")==library_hash,m


def main():
    if json.loads((REPORTS/"PRM098_V064_cost_canary_summary.json").read_text(encoding="utf-8"))["groups_passed"]!="6/6":raise SystemExit("cost canary not passed")
    if not json.loads((REPORTS/"PRM098_C1_mask_alias_audit_summary.json").read_text(encoding="utf-8"))["panel_continuation_authorized"]:raise SystemExit("C1 mask audit not cleared")
    registry=pd.read_csv(TABLES/"PRM098_input_mask_source_registry.csv",dtype=str,keep_default_na=False); limits=pd.read_csv(TABLES/"PRM097_resource_stop_policy.csv").set_index("candidate_group_id")
    runner=LAB/"scripts"/"PRM098_run_cell.py"; library=LAB/"scripts"/"PRM098_third_wave_formula_library.py"; rh=sha256(runner); lh=sha256(library)
    rows=[]; group_state={g:"PASS" for g in GROUPS}; started=time.perf_counter()
    for resolution in RESOLUTIONS:
        for group in GROUPS:
            for model in MODELS:
                if group_state[group]!="PASS":
                    rows.append({"candidate_group_id":group,"model_id":model,"resolution_id":resolution,"status":"not_run_group_hold","action":"skipped","runtime_s":"","peak_rss_gib":"","returncode":"","reason":"earlier cell/resource failure"});continue
                asset=registry.loc[(registry.model_id==model)&(registry.resolution_id==resolution)]
                if len(asset)!=1 or asset.iloc[0].asset_role!="reuse_existing_mask" or str(asset.iloc[0].hash_pass).lower()!="true":
                    group_state[group]="HOLD"; rows.append({"candidate_group_id":group,"model_id":model,"resolution_id":resolution,"status":"asset_fail","action":"blocked","runtime_s":"","peak_rss_gib":"","returncode":"","reason":"missing/unverified mask"});continue
                done=FACTORY/"intermediate"/group/model/resolution/"done.json"; valid,meta=valid_done(done,asset.iloc[0].expected_sha256,rh,lh)
                if valid:
                    rows.append({"candidate_group_id":group,"model_id":model,"resolution_id":resolution,"status":"passed","action":"reused_hash_valid_done","runtime_s":meta["runtime_s"],"peak_rss_gib":meta["peak_rss_gib"],"returncode":0,"reason":""});continue
                cmd=[sys.executable,str(runner),"--group",group,"--model",model,"--resolution",resolution]; t=time.perf_counter()
                try:
                    run=subprocess.run(cmd,capture_output=True,text=True,timeout=float(limits.loc[group,"max_seconds_per_cell"])+30)
                    if run.returncode==0:
                        meta=json.loads(done.read_text(encoding="utf-8")); status="passed"; reason=""
                    else: status="failed"; reason=(run.stderr or run.stdout)[-1000:]; meta={}; group_state[group]="HOLD"
                    rows.append({"candidate_group_id":group,"model_id":model,"resolution_id":resolution,"status":status,"action":"executed","runtime_s":meta.get("runtime_s",time.perf_counter()-t),"peak_rss_gib":meta.get("peak_rss_gib",""),"returncode":run.returncode,"reason":reason})
                except subprocess.TimeoutExpired:
                    group_state[group]="HOLD"; rows.append({"candidate_group_id":group,"model_id":model,"resolution_id":resolution,"status":"timeout","action":"executed","runtime_s":time.perf_counter()-t,"peak_rss_gib":"","returncode":"","reason":"subprocess timeout"})
                print(f"{resolution} {group} {model}: {rows[-1]['status']}",flush=True)
        pd.DataFrame(rows).to_csv(REPORTS/"PRM098_progressive_panel_execution_ledger.partial.csv",index=False,encoding="utf-8-sig",lineterminator="\n")
    ledger=pd.DataFrame(rows); ledger.to_csv(REPORTS/"PRM098_progressive_panel_execution_ledger.csv",index=False,encoding="utf-8-sig",lineterminator="\n")
    partial=REPORTS/"PRM098_progressive_panel_execution_ledger.partial.csv"; partial.unlink(missing_ok=True)
    values=[]
    for row in ledger.loc[ledger.status.eq("passed")].itertuples():
        path=FACTORY/"intermediate"/row.candidate_group_id/row.model_id/row.resolution_id/"values.csv"
        values.append(pd.read_csv(path,dtype=str,keep_default_na=False))
    merged=pd.concat(values,ignore_index=True) if values else pd.DataFrame(); merged.to_csv(REPORTS/"PRM098_representative_panel_values_long.csv",index=False,encoding="utf-8-sig",lineterminator="\n")
    summary={"status":"PASS" if all(x=="PASS" for x in group_state.values()) else "PARTIAL","cells_passed":f"{ledger.status.eq('passed').sum()}/{len(ledger)}","executed":int(ledger.action.eq('executed').sum()),"reused":int(ledger.action.eq('reused_hash_valid_done').sum()),"group_state":group_state,"value_or_artifact_rows":len(merged),"wall_s":time.perf_counter()-started}
    (REPORTS/"PRM098_progressive_panel_summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8");print(json.dumps(summary))


if __name__=="__main__":main()
