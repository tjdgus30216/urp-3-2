from __future__ import annotations
import hashlib
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[3]
LAB=ROOT/"experiments"/"lab_001_xy_connection_20260626"
FACTORY=LAB/"factories"/"PRM-101"
OUT=FACTORY/"reports"/"PRM101_output_manifest.csv"
def digest(p: Path)->str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()
def main()->None:
    fs={p for p in FACTORY.rglob("*") if p.is_file() and p.name not in {OUT.name,"PRM101_postmerge_sync_QA.csv","PRM101_postmerge_sync_QA_summary.json"}}
    fs|=set((LAB/"scripts").glob("PRM101_*.py")); fs|=set((LAB/"reports"/"tables").glob("PRM101_*.csv"))
    fs|={LAB/"results"/"R09-20260723-PRM101_XREG_V0_3_THIRD_WAVE_FULL58_CONSOLIDATION_AND_BLOCK_POLICY_NO_Y.md",LAB/"runlog.md",LAB/"decision_log.md",LAB/"changelog.md",LAB/"results"/"R09_blackbox_decision_register_20260703.md",ROOT/"AI_START_HERE.md",ROOT/"outputs"/"URP4-1_ROADMAP.md",ROOT/"outputs"/"URP4-1_ROADMAP_LOG.md",ROOT/"outputs"/"URP4-1_CHANGELOG.md",ROOT/"outputs"/"URP4-1_PROFESSOR_PROJECT_ROADMAP_20260629.md"}
    rows=[{"path":str(p.relative_to(ROOT)),"size_bytes":p.stat().st_size,"sha256":digest(p)} for p in sorted((p for p in fs if p.exists()),key=lambda x:str(x).lower())]
    pd.DataFrame(rows).to_csv(OUT,index=False,encoding="utf-8-sig"); print(f"manifest_rows={len(rows)}")
if __name__=="__main__": main()
