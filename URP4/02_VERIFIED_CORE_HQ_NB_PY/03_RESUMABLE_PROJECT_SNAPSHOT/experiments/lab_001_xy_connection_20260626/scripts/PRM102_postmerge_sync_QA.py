from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[3];LAB=ROOT/"experiments"/"lab_001_xy_connection_20260626";F=LAB/"factories"/"PRM-102";T=LAB/"reports"/"tables";V=Path(r"G:\내 드라이브\Obsidian\Nexus_vault")
def main():
 q=[]
 def add(k,ok):q.append({"check_id":k,"status":"PASS" if ok else "FAIL"})
 s=json.loads((F/"reports"/"PRM102_batch_summary.json").read_text(encoding="utf-8"));i=json.loads((F/"reports"/"PRM102_independent_QA_summary.json").read_text(encoding="utf-8"));r=pd.read_csv(T/"PRM102_BC_raw_table_candidate_registry.csv");v=pd.read_csv(T/"PRM102_BC_raw_table_values_long.csv");x=pd.read_csv(T/"PRM102_BC_vs_XREG_v0_3_redundancy.csv");z=pd.read_csv(T/"PRM102_BC_internal_redundancy.csv")
 add("Q01_summary",s.get("checks")=="8/8");add("Q02_independent",i.get("checks")=="12/12");add("Q03_scope",len(r)==29 and len(v)==1682 and v.value.notna().all());add("Q04_grades",r.operational_grade.value_counts().to_dict()=={"B":23,"C":6});add("Q05_relations",len(x)==3306 and x.relation.eq("high_redundancy").sum()==0 and len(z)==406 and z.relation.eq("high_redundancy").sum()==2);add("Q06_locks",not r.active_feature.any() and not r.promoted.any() and r.y_evidence.astype(str).str.lower().eq("false").all())
 refs={ROOT/"AI_START_HERE.md":"PRM-102 / RUN-247",ROOT/"outputs"/"URP4-1_ROADMAP_LOG.md":"R09-20260723-PRM102",ROOT/"outputs"/"URP4-1_CHANGELOG.md":"CHG-267",LAB/"decision_log.md":"DEC-280",LAB/"results"/"R09_blackbox_decision_register_20260703.md":"R09-BB-1153",V/"50_Projects"/"URP4-1.md":"LOG-20260723-071"}
 for n,(p,t) in enumerate(refs.items(),7):add(f"Q{n:02d}_sync",t in p.read_text(encoding="utf-8"))
 out=pd.DataFrame(q);out.to_csv(F/"reports"/"PRM102_postmerge_sync_QA.csv",index=False,encoding="utf-8-sig");bad=out.loc[out.status.ne("PASS"),"check_id"].tolist();fin={"status":"PASS" if not bad else "FAIL","checks":f"{len(out)-len(bad)}/{len(out)}","failed":bad,"y_fit_selection_promotion":"0/0/0/0"};(F/"reports"/"PRM102_postmerge_sync_QA_summary.json").write_text(json.dumps(fin,indent=2)+"\n",encoding="utf-8");print(json.dumps(fin,indent=2));
 if bad:raise SystemExit(1)
if __name__=="__main__":main()
