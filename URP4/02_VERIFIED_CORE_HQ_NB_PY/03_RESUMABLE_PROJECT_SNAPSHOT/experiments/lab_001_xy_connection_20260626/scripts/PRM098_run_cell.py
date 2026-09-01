from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import threading
import time
from pathlib import Path

import numpy as np
import pandas as pd
import psutil

ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
TABLES = LAB / "reports" / "tables"
FACTORY = LAB / "factories" / "PRM-098"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from PRM098_third_wave_formula_library import compute_group  # noqa: E402


def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()


class PeakMonitor:
    def __init__(self): self.stop=threading.Event(); self.peak=0; self.thread=threading.Thread(target=self._run,daemon=True)
    def _run(self):
        proc=psutil.Process(os.getpid())
        while not self.stop.is_set():
            try: self.peak=max(self.peak,proc.memory_info().rss)
            except psutil.Error: pass
            self.stop.wait(.02)
    def __enter__(self): self.thread.start(); return self
    def __exit__(self,*_): self.stop.set(); self.thread.join(); self._run_once()
    def _run_once(self):
        try:self.peak=max(self.peak,psutil.Process(os.getpid()).memory_info().rss)
        except psutil.Error:pass


def atomic_csv(frame: pd.DataFrame, path: Path):
    tmp=path.with_suffix(path.suffix+".tmp"); frame.to_csv(tmp,index=False,encoding="utf-8-sig",lineterminator="\n"); os.replace(tmp,path)


def atomic_json(payload: dict, path: Path):
    tmp=path.with_suffix(path.suffix+".tmp"); tmp.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); os.replace(tmp,path)


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--group",required=True); ap.add_argument("--model",required=True); ap.add_argument("--resolution",required=True); args=ap.parse_args()
    permit_path=FACTORY/"contracts"/"PRM-098_BOUNDED_EXECUTION_PERMIT_20260723.json"; permit=json.loads(permit_path.read_text(encoding="utf-8"))
    if permit["status"]!="authorized_bounded_progressive_execution": raise SystemExit("permit inactive")
    registry=pd.read_csv(TABLES/"PRM098_input_mask_source_registry.csv",dtype=str,keep_default_na=False)
    hit=registry.loc[registry.model_id.eq(args.model)&registry.resolution_id.eq(args.resolution)]
    if len(hit)!=1: raise SystemExit("asset registry row is not unique")
    row=hit.iloc[0]
    if row.asset_role!="reuse_existing_mask": raise SystemExit("requested resolution mask has not been materialized/registered")
    mask_path=ROOT/row.asset_path
    if sha256(mask_path)!=row.expected_sha256: raise SystemExit("mask hash mismatch")
    resources=pd.read_csv(TABLES/"PRM097_resource_stop_policy.csv")
    resource=resources.loc[resources.candidate_group_id.eq(args.group)].iloc[0]
    outdir=FACTORY/"intermediate"/args.group/args.model/args.resolution; outdir.mkdir(parents=True,exist_ok=True)
    with np.load(mask_path) as z: volume=z["volume"].astype(bool,copy=False); pitch=float(z["pitch_mm"])
    start=time.perf_counter()
    with PeakMonitor() as monitor:
        result=compute_group(args.group,volume,pitch,max_seconds=float(resource.max_seconds_per_cell))
    elapsed=time.perf_counter()-start
    artifact_paths={}
    for name,array in result.artifacts.items():
        artifact=outdir/(name+".npz"); np.savez_compressed(artifact,value=array); artifact_paths[name]=str(artifact.relative_to(ROOT))
    output_rows=[{"candidate_id":k,"value":v,"artifact_path":"","model_id":args.model,"resolution_id":args.resolution,"candidate_group_id":args.group} for k,v in result.outputs.items()]
    if args.group=="LIT-X024": output_rows.append({"candidate_id":"LIT-X024::ECT_curve_26x129","value":"","artifact_path":artifact_paths["ECT_curve_26x129"],"model_id":args.model,"resolution_id":args.resolution,"candidate_group_id":args.group})
    values=pd.DataFrame(output_rows)
    atomic_csv(values,outdir/"values.csv")
    meta={"status":"passed","group":args.group,"model_id":args.model,"resolution_id":args.resolution,"mask_path":row.asset_path,"mask_sha256":row.expected_sha256,"permit_sha256":sha256(permit_path),"runner_sha256":sha256(Path(__file__)),"formula_library_sha256":sha256(Path(__file__).with_name("PRM098_third_wave_formula_library.py")),"output_count":len(values),"runtime_s":elapsed,"peak_rss_gib":monitor.peak/1024**3,"wall_limit_s":float(resource.max_seconds_per_cell),"memory_limit_gib":float(resource.max_rss_gib),"within_wall_limit":elapsed<=float(resource.max_seconds_per_cell),"within_memory_limit":monitor.peak/1024**3<=float(resource.max_rss_gib),"diagnostics":result.diagnostics,"artifacts":artifact_paths}
    if not meta["within_wall_limit"] or not meta["within_memory_limit"]: meta["status"]="resource_stop"
    atomic_json(meta,outdir/"done.json")
    print(json.dumps(meta,ensure_ascii=False))
    if meta["status"]!="passed": raise SystemExit(2)


if __name__=="__main__": main()
