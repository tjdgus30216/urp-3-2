from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import pearsonr,spearmanr
ROOT=Path(__file__).resolve().parents[3]; LAB=ROOT/"experiments"/"lab_001_xy_connection_20260626"; T=LAB/"reports"/"tables"; F=LAB/"factories"/"PRM-102"; C=F/"contracts"/"PRM-102_BC_RAW_TABLE_BATCH_CONTRACT_20260723.json"
def sha(p:Path)->str:
 h=hashlib.sha256()
 with p.open("rb") as f:
  for x in iter(lambda:f.read(1048576),b""):h.update(x)
 return h.hexdigest()
def stat(a):
 a=np.asarray(a,float); q=np.quantile(a,[.1,.25,.5,.75,.9]); med=q[2]
 return {"mean":float(a.mean()),"population_std":float(a.std()),"q10":float(q[0]),"q50":float(q[2]),"q90":float(q[4]),"iqr":float(q[3]-q[1]),"mad":float(np.median(np.abs(a-med)))}
def ntv(a):
 a=np.asarray(a,float); return float(np.abs(np.diff(a)).mean()/max(np.abs(a).mean(),1e-12))
def ac1(a):
 a=np.asarray(a,float)
 return 0.0 if a.std()<=1e-12 else float(np.corrcoef(a[:-1],a[1:])[0,1])
def variable(a):
 a=a[np.isfinite(a)]; return len(a)>=3 and len(np.unique(a))>=3 and (a.max()-a.min())>1e-10*max(1.,np.max(np.abs(a)))
def relation(a,b):
 m=np.isfinite(a)&np.isfinite(b); a,b=a[m],b[m]
 if len(a)!=58:return {"common_models":len(a),"relation":"insufficient_common_coverage","pearson":np.nan,"spearman":np.nan,"normalized_L2_residual":np.nan}
 if not variable(a) or not variable(b):return {"common_models":58,"relation":"degenerate_nonvarying_reference_or_candidate","pearson":np.nan,"spearman":np.nan,"normalized_L2_residual":np.nan}
 if np.allclose(a,b,rtol=1e-10,atol=1e-12):return {"common_models":58,"relation":"exact_duplicate","pearson":1.,"spearman":1.,"normalized_L2_residual":0.}
 slope=float(np.dot(a,b)/np.dot(a,a)); resid=float(np.linalg.norm(b-slope*a)/max(np.linalg.norm(b),1e-30)); p=float(pearsonr(a,b).statistic);s=float(spearmanr(a,b).statistic)
 rel="proportional_duplicate" if resid<=1e-6 and abs(slope)>1e-12 else ("high_redundancy" if abs(p)>=.98 and abs(s)>=.98 else "distinct_or_unresolved")
 return {"common_models":58,"relation":rel,"pearson":p,"spearman":s,"normalized_L2_residual":resid}
def main():
 c=json.loads(C.read_text(encoding="utf-8"))
 for x in c["inputs"]:
  if sha(ROOT/x["path"])!=x["sha256"]:raise RuntimeError(f"input hash mismatch: {x['path']}")
 manifest=pd.read_csv(ROOT/c["inputs"][0]["path"]); xreg=pd.read_csv(T/"PRM101_xreg_v0_3_values_long.csv"); models=sorted(xreg.model_id.unique()); fam=xreg[["model_id","model_family"]].drop_duplicates().set_index("model_id").model_family.to_dict()
 hashes=dict(zip(manifest.path,manifest.sha256)); needed=[]
 for m in models:
  for name in ["slice_pixel_readback.csv","overlay_component_population.csv"]:needed.append(f".tmp/t4rs4/P1000_S801/{m}/tables/{name}")
 if len(needed)!=116 or any(k not in hashes for k in needed):raise RuntimeError("raw-manifest coverage mismatch")
 for k in needed:
  if not (ROOT/k).exists() or sha(ROOT/k)!=hashes[k]:raise RuntimeError(f"raw table hash mismatch: {k}")
 meta={}; rows=[]
 def put(model,cid,value,grade,unit,pop,formula,source,anchor):
  rows.append({"model_id":model,"model_family":fam[model],"candidate_id":cid,"value":float(value),"operational_grade":grade})
  meta.setdefault(cid,{"candidate_id":cid,"candidate_group_id":"RAW-X034" if cid.startswith("RAW-X034") else "RAW-X035","descriptor_family":"slice_profile_distribution" if cid.startswith("RAW-X034") else "overlay_component_distribution","operational_grade":grade,"unit":unit,"source_population":pop,"aggregation_formula":formula,"source_table":source,"literature_anchor":anchor,"anchor_scope":"component/population distribution analogue only; not a full 3D estimator" if anchor else "raw-table statistic","applicable_family":"B|C|F|L|T","technical_status":"batch_BC_unselected","active_feature":False,"promoted":False,"y_evidence":False})
 for m in models:
  base=ROOT/f".tmp/t4rs4/P1000_S801/{m}/tables"; sl=pd.read_csv(base/"slice_pixel_readback.csv").sort_values("slice_index"); ov=pd.read_csv(base/"overlay_component_population.csv"); ov=ov[ov.kept_by_min2.astype(bool)].copy()
  for prefix,a,unit,pop,src in [("RAW-X034::slice_material_area",sl.material_area_mm2,"mm2","801-slice material-area profile","slice_pixel_readback.csv"),("RAW-X034::slice_component_count",sl.component_count_min2,"count","801-slice connected-component-count profile","slice_pixel_readback.csv")]:
   for k,v in stat(a).items():put(m,f"{prefix}_{k}",v,"B",unit,pop,f"population {k} (ddof=0 for std)",src,"LIT-X033")
   put(m,f"{prefix}_lag1_autocorr",ac1(a),"C","dimensionless",pop,"lag-1 Pearson autocorrelation; constant-profile fallback=0",src,"LIT-X033")
   put(m,f"{prefix}_normalized_total_variation",ntv(a),"C","dimensionless",pop,"mean absolute adjacent step / mean absolute profile value",src,"LIT-X033")
  area=ov.area_mm2.to_numpy(float)
  for k,v in stat(area).items():put(m,f"RAW-X035::overlay_component_area_{k}",v,"B","mm2","all kept overlay connected-component areas across 800 layer pairs",f"population {k} (ddof=0 for std)","overlay_component_population.csv","LIT-X033")
  per=ov.groupby("pair_index").agg(component_count=("component_index","size"),total_area_mm2=("area_mm2","sum")).sort_index()
  for k in ["mean","q50"]:put(m,f"RAW-X035::overlay_pair_component_count_{k}",stat(per.component_count)[k],"B","count","800-pair overlay component-count profile",f"population {k}","overlay_component_population.csv","LIT-X033")
  put(m,"RAW-X035::overlay_pair_total_area_lag1_autocorr",ac1(per.total_area_mm2),"C","dimensionless","800-pair total-overlay-area profile","lag-1 Pearson autocorrelation; constant-profile fallback=0","overlay_component_population.csv","LIT-X033")
  put(m,"RAW-X035::overlay_pair_total_area_normalized_total_variation",ntv(per.total_area_mm2),"C","dimensionless","800-pair total-overlay-area profile","mean absolute adjacent step / mean absolute profile value","overlay_component_population.csv","LIT-X033")
 vals=pd.DataFrame(rows); reg=pd.DataFrame(meta.values()).sort_values("candidate_id").reset_index(drop=True); ids=reg.candidate_id.tolist()
 if len(ids)!=29 or len(vals)!=58*29 or not np.isfinite(vals.value).all():raise RuntimeError(f"batch scope failure: {len(ids)} candidates {len(vals)} values")
 wide=vals.pivot(index="model_id",columns="candidate_id",values="value").reindex(index=models,columns=ids)
 cov=[]
 for cid in ids:
  a=wide[cid].to_numpy(float);cov.append({"candidate_id":cid,"finite_count":int(np.isfinite(a).sum()),"unique_count":int(np.unique(a).size),"population_std":float(a.std()),"iqr":float(np.quantile(a,.75)-np.quantile(a,.25)),"operational_grade":reg.set_index("candidate_id").loc[cid,"operational_grade"],"technical_status":"batch_BC_unselected"})
 rel=[]
 for cid in ids:
  a=wide[cid].to_numpy(float)
  for eid in sorted(xreg.candidate_id.unique()):
   b=xreg[xreg.candidate_id.eq(eid)].set_index("model_id").reindex(models).value.to_numpy(float);rel.append({"candidate_id":cid,"existing_candidate_id":eid,**relation(a,b),"evidence_scope":"full58_xonly","selection_effect":"none"})
 internal=[]
 for i,l in enumerate(ids):
  for r in ids[i+1:]:internal.append({"left_candidate_id":l,"right_candidate_id":r,**relation(wide[l].to_numpy(float),wide[r].to_numpy(float),),"evidence_scope":"full58_xonly","selection_effect":"none"})
 pairs=[]
 for a,b,label in [("T8","T9","T8_T9"),("T5","T6","T5_T6")]:
  for cid in ids:
   va,vb=wide.loc[a,cid],wide.loc[b,cid];pairs.append({"pair_id":label,"candidate_id":cid,"absolute_delta":abs(va-vb),"relative_delta":abs(va-vb)/max(abs(va),abs(vb),1e-12),"diagnostic_only":True})
 T.mkdir(parents=True,exist_ok=True);F.joinpath("reports").mkdir(parents=True,exist_ok=True)
 reg.to_csv(T/"PRM102_BC_raw_table_candidate_registry.csv",index=False,encoding="utf-8-sig"); vals.to_csv(T/"PRM102_BC_raw_table_values_long.csv",index=False,encoding="utf-8-sig",float_format="%.17g");wide.reset_index().to_csv(T/"PRM102_BC_raw_table_values_wide.csv",index=False,encoding="utf-8-sig",float_format="%.17g");pd.DataFrame(cov).to_csv(T/"PRM102_BC_coverage_variation.csv",index=False,encoding="utf-8-sig");pd.DataFrame(rel).to_csv(T/"PRM102_BC_vs_XREG_v0_3_redundancy.csv",index=False,encoding="utf-8-sig");pd.DataFrame(internal).to_csv(T/"PRM102_BC_internal_redundancy.csv",index=False,encoding="utf-8-sig");pd.DataFrame(pairs).to_csv(T/"PRM102_BC_collision_diagnostic.csv",index=False,encoding="utf-8-sig")
 qa=[("P102-01",len(models)==58,"58 models"),("P102-02",len(needed)==116,"116 hash-verified raw files"),("P102-03",len(ids)==29,"29 candidates"),("P102-04",len(vals)==1682 and np.isfinite(vals.value).all(),"1682 finite values"),("P102-05",len(rel)==29*114,"3306 crossbank relations"),("P102-06",len(internal)==406,"406 internal relations"),("P102-07",len(pairs)==58,"two collision pairs x29"),("P102-08",not reg.active_feature.any() and not reg.promoted.any() and not reg.y_evidence.any(),"no selection/y")]
 q=pd.DataFrame([{"check_id":i,"status":"PASS" if ok else "FAIL","detail":d} for i,ok,d in qa]);q.to_csv(F/"reports"/"PRM102_producer_QA.csv",index=False,encoding="utf-8-sig");s={"status":"PASS" if q.status.eq("PASS").all() else "FAIL","checks":f"{q.status.eq('PASS').sum()}/{len(q)}","models":58,"candidates":29,"values":1682,"y_fit_selection_promotion":"0/0/0/0"};(F/"reports"/"PRM102_batch_summary.json").write_text(json.dumps(s,indent=2)+"\n",encoding="utf-8");print(json.dumps(s,indent=2));
 if s["status"]!="PASS":raise SystemExit(1)
if __name__=="__main__":main()
