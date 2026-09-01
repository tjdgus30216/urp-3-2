from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[3];LAB=ROOT/"experiments"/"lab_001_xy_connection_20260626";T=LAB/"reports"/"tables";F=LAB/"factories"/"PRM-102";C=F/"contracts"/"PRM-102_BC_RAW_TABLE_BATCH_CONTRACT_20260723.json"
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for x in iter(lambda:f.read(1048576),b""):h.update(x)
 return h.hexdigest()
def main():
 c=json.loads(C.read_text(encoding="utf-8"));q=[]
 def add(k,ok,detail):q.append({"check_id":k,"status":"PASS" if ok else "FAIL","detail":detail})
 for i,x in enumerate(c["inputs"],1):add(f"I102-{i:02d}_contract",sha(ROOT/x["path"])==x["sha256"],x["path"])
 mf=pd.read_csv(ROOT/c["inputs"][0]["path"]);h=dict(zip(mf.path,mf.sha256));xreg=pd.read_csv(T/"PRM101_xreg_v0_3_values_long.csv");models=sorted(xreg.model_id.unique());need=[f".tmp/t4rs4/P1000_S801/{m}/tables/{n}" for m in models for n in ["slice_pixel_readback.csv","overlay_component_population.csv"]];add("I102-05_raw_hashes",len(need)==116 and all(k in h and (ROOT/k).exists() and sha(ROOT/k)==h[k] for k in need),"116 raw tables")
 reg=pd.read_csv(T/"PRM102_BC_raw_table_candidate_registry.csv");v=pd.read_csv(T/"PRM102_BC_raw_table_values_long.csv");wide=pd.read_csv(T/"PRM102_BC_raw_table_values_wide.csv");cross=pd.read_csv(T/"PRM102_BC_vs_XREG_v0_3_redundancy.csv");intr=pd.read_csv(T/"PRM102_BC_internal_redundancy.csv");pair=pd.read_csv(T/"PRM102_BC_collision_diagnostic.csv")
 add("I102-06_registry",len(reg)==29 and reg.operational_grade.value_counts().to_dict()=={"B":23,"C":6},"29: B23/C6");add("I102-07_values",len(v)==1682 and v.model_id.nunique()==58 and v.candidate_id.nunique()==29 and np.isfinite(v.value).all(),"1682 finite");add("I102-08_wide",wide.shape==(58,30) and wide.iloc[:,1:].notna().all().all(),"58x29");add("I102-09_relations",len(cross)==3306 and len(intr)==406 and len(pair)==58,"3306/406/58")
 for m in ["B3","T8"]:
  sl=pd.read_csv(ROOT/f".tmp/t4rs4/P1000_S801/{m}/tables/slice_pixel_readback.csv").sort_values("slice_index");ov=pd.read_csv(ROOT/f".tmp/t4rs4/P1000_S801/{m}/tables/overlay_component_population.csv");ov=ov[ov.kept_by_min2.astype(bool)]
  checks={"RAW-X034::slice_material_area_mean":sl.material_area_mm2.mean(),"RAW-X034::slice_component_count_q50":np.quantile(sl.component_count_min2,.5),"RAW-X034::slice_material_area_normalized_total_variation":np.abs(np.diff(sl.material_area_mm2)).mean()/max(np.abs(sl.material_area_mm2).mean(),1e-12),"RAW-X035::overlay_component_area_mad":np.median(np.abs(ov.area_mm2-np.median(ov.area_mm2))),"RAW-X035::overlay_pair_component_count_mean":ov.groupby("pair_index").component_index.size().mean()}
  out=v[v.model_id.eq(m)].set_index("candidate_id").value
  add(f"I102-{m}_formula_replay",all(abs(out[k]-z)<=1e-12 for k,z in checks.items()),f"{m} 5 independent replays")
 add("I102-12_locks",not reg.active_feature.any() and not reg.promoted.any() and reg.y_evidence.astype(str).str.lower().eq("false").all(),"no y/selection")
 out=pd.DataFrame(q);F.joinpath("reports").mkdir(parents=True,exist_ok=True);out.to_csv(F/"reports"/"PRM102_independent_QA.csv",index=False,encoding="utf-8-sig");bad=out.loc[out.status.ne("PASS"),"check_id"].tolist();s={"status":"PASS" if not bad else "FAIL","checks":f"{len(out)-len(bad)}/{len(out)}","failed":bad,"y_fit_selection_promotion":"0/0/0/0"};(F/"reports"/"PRM102_independent_QA_summary.json").write_text(json.dumps(s,indent=2)+"\n",encoding="utf-8");print(json.dumps(s,indent=2));
 if bad:raise SystemExit(1)
if __name__=="__main__":main()
