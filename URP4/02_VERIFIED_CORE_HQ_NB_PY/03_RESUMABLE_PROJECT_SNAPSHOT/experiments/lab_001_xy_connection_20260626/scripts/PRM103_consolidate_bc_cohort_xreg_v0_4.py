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
 c=json.loads(C.read_text(encoding="utf-8"));
 for x in c["inputs"]:
  if sha(ROOT/x["path"])!=x["sha256"]:raise RuntimeError(f"input hash mismatch: {x['path']}")
 bank0=pd.read_csv(T/"PRM101_xreg_v0_3_candidate_bank.csv"); val0=pd.read_csv(T/"PRM101_xreg_v0_3_values_long.csv"); edge0=pd.read_csv(T/"PRM101_unified_redundancy_edge_registry.csv");block0=pd.read_csv(T/"PRM101_unified_redundancy_block_registry.csv");reg=pd.read_csv(T/"PRM102_BC_raw_table_candidate_registry.csv");newv=pd.read_csv(T/"PRM102_BC_raw_table_values_long.csv");internal=pd.read_csv(T/"PRM102_BC_internal_redundancy.csv")
 ids=sorted(reg.candidate_id);pair_rows=internal[internal.relation.eq("high_redundancy")];
 if len(ids)!=29 or len(newv)!=1682 or len(pair_rows)!=2:raise RuntimeError("PRM102 source scope mismatch")
 pairs=[tuple(sorted([r.left_candidate_id,r.right_candidate_id])) for r in pair_rows.itertuples(index=False)];pairs=sorted(pairs);paired={x for p in pairs for x in p};bid={pairs[0][0]:"U103-BLK-095",pairs[0][1]:"U103-BLK-095",pairs[1][0]:"U103-BLK-096",pairs[1][1]:"U103-BLK-096"};n=97
 for cid in ids:
  if cid not in bid:bid[cid]=f"U103-BLK-{n:03d}";n+=1
 old=bank0.copy();old["bank_version"]="XREG-v0.4-TECHNICAL";old["operational_grade"]="legacy_pregrade";old["literature_anchor"]="prior_registry";old["anchor_scope"]="prior_registry"
 bcols=list(old.columns); rows=[]
 for r in reg.itertuples(index=False):
  a=newv[newv.candidate_id.eq(r.candidate_id)].value.to_numpy(float); members=2 if r.candidate_id in paired else 1; degree=1 if r.candidate_id in paired else 0
  rows.append({"bank_version":"XREG-v0.4-TECHNICAL","candidate_id":r.candidate_id,"candidate_group_id":r.candidate_group_id,"descriptor_family":r.descriptor_family,"output_name":r.candidate_id.split("::",1)[1],"unit":r.unit,"source_population":r.source_population,"aggregation_formula":r.aggregation_formula,"applicable_family":r.applicable_family,"direct_or_derived":"direct_from_verified_SLICE004_raw_table" if r.operational_grade=="B" else "derived_from_verified_SLICE004_profile","source_bank":"PRM102_BC_raw_table_batch","source_value_table":"PRM102_BC_raw_table_values_long.csv","technical_role":"batch_BC_candidate","qualification_status":"full58_raw_table_batch_not_selected","confidence_status":"confirmed_raw_table_lineage","later_evaluation_role":"batch_BC_unselected_block_aware","active_feature":False,"promoted":False,"y_evidence":False,"notes":"PRM102 B/C batch; no y, selection or promotion","model_count":58,"finite_count":int(np.isfinite(a).sum()),"unique_count":int(np.unique(a).size),"unified_block_id":bid[r.candidate_id],"unified_block_member_count":members,"unified_edge_degree":degree,"operational_grade":r.operational_grade,"literature_anchor":r.literature_anchor,"anchor_scope":r.anchor_scope})
 bank=pd.concat([old,pd.DataFrame(rows).reindex(columns=bcols)],ignore_index=True)
 prior=val0.copy();prior["bank_version"]="XREG-v0.4-TECHNICAL"; fam=prior[["model_id","model_family"]].drop_duplicates().set_index("model_id").model_family.to_dict(); newout=newv.assign(bank_version="XREG-v0.4-TECHNICAL",model_family=newv.model_id.map(fam),finite=True,source_bank="PRM102_BC_raw_table_batch")[["bank_version","model_id","model_family","candidate_id","value","finite","source_bank"]];vals=pd.concat([prior,newout],ignore_index=True)
 order=bank.candidate_id.tolist();wide=vals.pivot(index=["model_id","model_family"],columns="candidate_id",values="value").reindex(columns=order).reset_index()
 edges=pd.concat([edge0,pd.DataFrame([{"edge_id":"U103-EDGE-026","left_candidate_id":pairs[0][0],"right_candidate_id":pairs[0][1],"relation":"high_redundancy","edge_source":"PRM102_BC_internal_full58","metric_note":"slice/overlay component-count mean block; no representative selected","selection_rule":False},{"edge_id":"U103-EDGE-027","left_candidate_id":pairs[1][0],"right_candidate_id":pairs[1][1],"relation":"high_redundancy","edge_source":"PRM102_BC_internal_full58","metric_note":"slice/overlay component-count q50 block; no representative selected","selection_rule":False}])],ignore_index=True)
 blocks=block0.copy()
 lookup=reg.set_index("candidate_id")
 for cid in ids:
  r=lookup.loc[cid]; members=2 if cid in paired else 1;degree=1 if cid in paired else 0;policy="no selection; later block-aware comparison only" if cid in paired else "standalone technical candidate; no selection in PRM103"
  blocks.loc[len(blocks)]={"unified_block_id":bid[cid],"candidate_id":cid,"candidate_group_id":r.candidate_group_id,"descriptor_family":r.descriptor_family,"source_bank":"PRM102_BC_raw_table_batch","technical_role":"batch_BC_candidate","later_evaluation_role":"batch_BC_unselected_block_aware","unified_block_member_count":members,"unified_edge_degree":degree,"representative_selected":False,"block_policy":policy}
 pol=pd.DataFrame([{"candidate_id":cid,"operational_grade":lookup.loc[cid,"operational_grade"],"unified_block_id":bid[cid],"block_status":"two_member_redundancy_block" if cid in paired else "singleton","selection_status":"not_selected","next_allowed_action":"future no-y batch or separately authorized block-aware grouped-y protocol"} for cid in ids])
 qa=[]
 def q(k,ok,d):qa.append({"check_id":k,"status":"PASS" if ok else "FAIL","detail":d})
 q("P103-01",len(bank)==143 and bank.candidate_id.nunique()==143,"143 candidates");q("P103-02",len(vals)==8294 and vals.value.notna().sum()==8292,"8294 values, two inherited NA");q("P103-03",wide.shape==(58,145),"58x143 wide");q("P103-04",blocks.unified_block_id.nunique()==121 and len(blocks)==143,"121 blocks");q("P103-05",len(edges)==27 and edges.edge_id.nunique()==27,"27 edges");q("P103-06",len(pol)==29 and pol.selection_status.eq("not_selected").all(),"29 unselected");q("P103-07",not bank.active_feature.any() and not bank.promoted.any() and bank.y_evidence.astype(str).str.lower().eq("false").all(),"locks remain");q("P103-08",set(edges.tail(2).edge_id)=={"U103-EDGE-026","U103-EDGE-027"},"two new edges")
 if not all(x["status"]=="PASS" for x in qa):raise RuntimeError(qa)
 T.mkdir(parents=True,exist_ok=True);F.joinpath("reports").mkdir(parents=True,exist_ok=True)
 bank.to_csv(T/"PRM103_xreg_v0_4_candidate_bank.csv",index=False,encoding="utf-8-sig");vals.to_csv(T/"PRM103_xreg_v0_4_values_long.csv",index=False,encoding="utf-8-sig",float_format="%.17g");wide.to_csv(T/"PRM103_xreg_v0_4_values_wide.csv",index=False,encoding="utf-8-sig",float_format="%.17g");edges.to_csv(T/"PRM103_unified_redundancy_edge_registry.csv",index=False,encoding="utf-8-sig");blocks.to_csv(T/"PRM103_unified_redundancy_block_registry.csv",index=False,encoding="utf-8-sig");pol.to_csv(T/"PRM103_BC_cohort_block_policy.csv",index=False,encoding="utf-8-sig");pd.DataFrame(qa).to_csv(F/"reports"/"PRM103_producer_QA.csv",index=False,encoding="utf-8-sig");s={"status":"PASS","checks":"8/8","candidates":143,"values":8294,"blocks":121,"edges":27,"y_fit_selection_promotion":"0/0/0/0"};(F/"reports"/"PRM103_summary.json").write_text(json.dumps(s,indent=2)+"\n",encoding="utf-8");print(json.dumps(s,indent=2))
if __name__=="__main__":main()
