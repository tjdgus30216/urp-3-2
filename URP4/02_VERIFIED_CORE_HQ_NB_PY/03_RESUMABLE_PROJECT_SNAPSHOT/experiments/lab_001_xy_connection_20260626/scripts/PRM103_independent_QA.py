from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[3];LAB=ROOT/"experiments"/"lab_001_xy_connection_20260626";T=LAB/"reports"/"tables";F=LAB/"factories"/"PRM-103";C=F/"contracts"/"PRM-103_XREG_V0_4_BC_COHORT_CONSOLIDATION_CONTRACT_20260723.json"
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for x in iter(lambda:f.read(1048576),b""):h.update(x)
 return h.hexdigest()
def main():
 c=json.loads(C.read_text(encoding="utf-8"));q=[]
 def add(k,ok,d):q.append({"check_id":k,"status":"PASS" if ok else "FAIL","detail":d})
 for i,x in enumerate(c["inputs"],1):add(f"I103-{i:02d}_source_hash",sha(ROOT/x["path"])==x["sha256"],x["path"])
 b=pd.read_csv(T/"PRM103_xreg_v0_4_candidate_bank.csv");v=pd.read_csv(T/"PRM103_xreg_v0_4_values_long.csv");w=pd.read_csv(T/"PRM103_xreg_v0_4_values_wide.csv");e=pd.read_csv(T/"PRM103_unified_redundancy_edge_registry.csv");bl=pd.read_csv(T/"PRM103_unified_redundancy_block_registry.csv");p=pd.read_csv(T/"PRM103_BC_cohort_block_policy.csv");old=pd.read_csv(T/"PRM101_xreg_v0_3_values_long.csv");new=pd.read_csv(T/"PRM102_BC_raw_table_values_long.csv")
 add("I103-09_scope",len(b)==143 and b.candidate_id.nunique()==143 and len(v)==8294 and v.model_id.nunique()==58,"143/8294/58");add("I103-10_missingness",v.value.notna().sum()==8292 and v[v.candidate_id.str.startswith(("RAW-X034","RAW-X035"))].value.notna().all(),"2 inherited only");
 oldpart=v[~v.candidate_id.str.startswith(("RAW-X034","RAW-X035"))].copy();oldpart["bank_version"]="XREG-v0.3-TECHNICAL";cols=["bank_version","model_id","model_family","candidate_id","value","finite","source_bank"];oldpart=oldpart.sort_values(cols[:4]).reset_index(drop=True);old=old.sort_values(cols[:4]).reset_index(drop=True);add("I103-11_prior_replay",oldpart[cols[:-3]+["value"]].shape==old[cols[:-3]+["value"]].shape and np.allclose(oldpart.value,old.value,rtol=1e-14,atol=2e-15,equal_nan=True),"v0.3 value replay")
 newpart=v[v.candidate_id.str.startswith(("RAW-X034","RAW-X035"))][["model_id","candidate_id","value"]].sort_values(["model_id","candidate_id"]).reset_index(drop=True);new0=new[["model_id","candidate_id","value"]].sort_values(["model_id","candidate_id"]).reset_index(drop=True);add("I103-12_new_replay",newpart[["model_id","candidate_id"]].equals(new0[["model_id","candidate_id"]]) and np.allclose(newpart.value,new0.value,rtol=1e-14,atol=2e-15),"PRM102 values replay")
 rebuilt=v.pivot(index=["model_id","model_family"],columns="candidate_id",values="value").reindex(columns=b.candidate_id.tolist()).reset_index();add("I103-13_wide",w.shape==(58,145) and rebuilt.columns.tolist()==w.columns.tolist() and np.allclose(rebuilt.iloc[:,2:].to_numpy(float),w.iloc[:,2:].to_numpy(float),rtol=1e-14,atol=2e-15,equal_nan=True),"wide replay")
 pair_blocks=bl[bl.unified_block_id.isin(["U103-BLK-095","U103-BLK-096"])];add("I103-14_blocks",bl.unified_block_id.nunique()==121 and len(bl)==143 and len(pair_blocks)==4 and pair_blocks.unified_block_member_count.eq(2).all(),"121 blocks/two 2-member");add("I103-15_edges",len(e)==27 and set(e.tail(2).edge_id)=={"U103-EDGE-026","U103-EDGE-027"},"27 edges");add("I103-16_policy",len(p)==29 and p.selection_status.eq("not_selected").all(),"29 unselected");add("I103-17_locks",not b.active_feature.any() and not b.promoted.any() and b.y_evidence.astype(str).str.lower().eq("false").all(),"no y/selection")
 out=pd.DataFrame(q);F.joinpath("reports").mkdir(parents=True,exist_ok=True);out.to_csv(F/"reports"/"PRM103_independent_QA.csv",index=False,encoding="utf-8-sig");bad=out.loc[out.status.ne("PASS"),"check_id"].tolist();s={"status":"PASS" if not bad else "FAIL","checks":f"{len(out)-len(bad)}/{len(out)}","failed":bad,"y_fit_selection_promotion":"0/0/0/0"};(F/"reports"/"PRM103_independent_QA_summary.json").write_text(json.dumps(s,indent=2)+"\n",encoding="utf-8");print(json.dumps(s,indent=2));
 if bad:raise SystemExit(1)
if __name__=="__main__":main()
