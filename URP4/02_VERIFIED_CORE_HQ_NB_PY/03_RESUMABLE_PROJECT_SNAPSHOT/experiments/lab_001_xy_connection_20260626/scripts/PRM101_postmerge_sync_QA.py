from __future__ import annotations
import hashlib,json
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[3]; LAB=ROOT/"experiments"/"lab_001_xy_connection_20260626"; F=LAB/"factories"/"PRM-101"; T=LAB/"reports"/"tables"; V=Path(r"G:\내 드라이브\Obsidian\Nexus_vault")
def sha(p:Path)->str:
 h=hashlib.sha256();
 with p.open("rb") as f:
  for c in iter(lambda:f.read(1024*1024),b""):h.update(c)
 return h.hexdigest()
def main()->None:
 q=[]
 def add(k,o,e):q.append({"check_id":k,"status":"PASS" if o else "FAIL","observed":str(o),"expected":e})
 s=json.loads((F/"reports"/"PRM101_consolidation_summary.json").read_text(encoding="utf-8")); iq=json.loads((F/"reports"/"PRM101_independent_QA_summary.json").read_text(encoding="utf-8")); b=pd.read_csv(T/"PRM101_xreg_v0_3_candidate_bank.csv");v=pd.read_csv(T/"PRM101_xreg_v0_3_values_long.csv");bl=pd.read_csv(T/"PRM101_unified_redundancy_block_registry.csv");e=pd.read_csv(T/"PRM101_unified_redundancy_edge_registry.csv");p=pd.read_csv(T/"PRM101_third_wave_block_policy.csv");m=pd.read_csv(F/"reports"/"PRM101_output_manifest.csv")
 add("Q01_summary",s.get("status")=="PASS" and s.get("candidates")==114,"PASS/114"); add("Q02_producer",len(pd.read_csv(F/"reports"/"PRM101_producer_QA.csv"))==10,"10");add("Q03_independent",iq.get("checks")=="20/20","20/20");add("Q04_bank",len(b)==114 and b.candidate_id.nunique()==114,"114");add("Q05_values",len(v)==6612 and v.loc[v.candidate_id.str.startswith(("LIT-X019","LIT-X024")),"value"].notna().all(),"6612 plus six finite");add("Q06_blocks_edges",bl.unified_block_id.nunique()==94 and len(e)==25,"94/25");add("Q07_policy",len(p)==6 and p.selection_status.eq("not_selected").all(),"6 unselected");add("Q08_locks",not b.active_feature.any() and not b.promoted.any() and b.y_evidence.astype(str).str.lower().eq("false").all(),"all false")
 for i,(path,token) in enumerate({ROOT/"AI_START_HERE.md":"PRM-101 / RUN-246",ROOT/"outputs"/"URP4-1_ROADMAP.md":"PRM-101 complete",ROOT/"outputs"/"URP4-1_ROADMAP_LOG.md":"R09-20260723-PRM101",ROOT/"outputs"/"URP4-1_CHANGELOG.md":"CHG-266",LAB/"runlog.md":"RUN-246",LAB/"decision_log.md":"DEC-279",LAB/"changelog.md":"LAB-CHG-238",LAB/"results"/"R09_blackbox_decision_register_20260703.md":"R09-BB-1147",V/"50_Projects"/"URP4-1.md":"LOG-20260723-070",V/"40_Devices"/"✅ TODO.md":"PRM102-FOURTH-WAVE-ROUTE-PREREGISTRATION-NO-Y"}.items(),9):add(f"Q{i:02d}_sync",token in path.read_text(encoding="utf-8"),token)
 bad=[r.path for r in m.itertuples(index=False) if not (ROOT/r.path).exists() or sha(ROOT/r.path)!=r.sha256];add("Q19_manifest",not bad,f"bad={len(bad)}")
 out=pd.DataFrame(q);out.to_csv(F/"reports"/"PRM101_postmerge_sync_QA.csv",index=False,encoding="utf-8-sig");failed=out.loc[out.status.ne("PASS"),"check_id"].tolist();fin={"status":"PASS" if not failed else "FAIL","checks":f"{len(out)-len(failed)}/{len(out)}","failed":failed,"y_fit_selection_promotion":"0/0/0/0"};(F/"reports"/"PRM101_postmerge_sync_QA_summary.json").write_text(json.dumps(fin,indent=2)+"\n",encoding="utf-8");print(json.dumps(fin,indent=2));
 if failed:raise SystemExit(1)
if __name__=="__main__":main()
