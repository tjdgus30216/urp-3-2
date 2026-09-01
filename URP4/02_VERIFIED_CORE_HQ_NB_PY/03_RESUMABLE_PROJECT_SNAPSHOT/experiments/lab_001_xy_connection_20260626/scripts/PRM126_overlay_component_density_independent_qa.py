from __future__ import annotations
import json
from pathlib import Path
import numpy as np,pandas as pd
R=Path(__file__).resolve().parents[3];T=R/'experiments/lab_001_xy_connection_20260626/reports/tables';O=R/'experiments/lab_001_xy_connection_20260626/factories/PRM-126/reports';O.mkdir(parents=True,exist_ok=True)
def one(model):
 d=pd.read_csv(R/f'.tmp/t4rs4/P1000_S801/{model}/tables/overlay_pixel_readback.csv').sort_values('pair_index');a=np.maximum(d.union_pixel_count.to_numpy(float),1.);raw=d.component_count_raw.to_numpy(float);kept=d.component_count_min2.to_numpy(float);p={'raw_component_density_per_mpx':1e6*raw/a,'kept_component_density_per_mpx':1e6*kept/a,'removed_component_density_per_mpx':1e6*(raw-kept)/a,'raw_to_kept_component_ratio':raw/np.maximum(kept,1.)};out={}
 for n,x in p.items():
  for s,z in {'mean':x.mean(),'population_std':x.std(ddof=0),'q10':np.quantile(x,.1),'q50':np.quantile(x,.5),'q90':np.quantile(x,.9),'iqr':np.quantile(x,.75)-np.quantile(x,.25)}.items():out[f'RAW-X054::{n}_{s}']=float(z)
 return out
def main():
 g=pd.read_csv(T/'PRM126_overlay_component_density_candidate_registry.csv');v=pd.read_csv(T/'PRM126_overlay_component_density_values_long.csv');x=pd.read_csv(T/'PRM126_overlay_component_density_vs_XREG_v1_5_redundancy.csv');i=pd.read_csv(T/'PRM126_overlay_component_density_internal_redundancy.csv');c=pd.read_csv(T/'PRM126_overlay_component_density_collision_diagnostic.csv');models=sorted(v.model_id.unique());errs=[]
 for m in models:
  a=one(m);b=v[v.model_id.eq(m)].set_index('candidate_id').value.to_dict();errs.extend(abs(a[k]-b[k]) for k in a)
 locks=g.y_evidence.eq(False).all() and not g.active_feature.any() and not g.promoted.any();checks=[('I126-01',len(g)==24 and len(models)==58,'24 candidates / 58 models'),('I126-02',len(v)==1392 and np.isfinite(v.value).all(),'all finite'),('I126-03',g.operational_grade.value_counts().to_dict()=={'B':18,'C':6},'B18/C6'),('I126-04',max(errs)<=1e-12,f'direct replay max={max(errs):.3e}'),('I126-05',all((R/f'.tmp/t4rs4/P1000_S801/{m}/tables/overlay_pixel_readback.csv').is_file() for m in models),'58 frozen sources'),('I126-06',len(x)==8760 and len(i)==276,'x-only relation scope'),('I126-07',len(c)==48 and (c.absolute_delta>=0).all(),'collision diagnostics'),('I126-08',locks,'no-y/no-promotion flags')];qa=pd.DataFrame([dict(check_id=k,status='PASS' if ok else 'FAIL',detail=d) for k,ok,d in checks]);qa.to_csv(O/'PRM126_independent_QA.csv',index=False,encoding='utf-8-sig');summary={'status':'PASS' if qa.status.eq('PASS').all() else 'FAIL','checks':f"{qa.status.eq('PASS').sum()}/{len(qa)}",'max_replay_error':max(errs),'performance_y_read':0};(O/'PRM126_independent_QA_summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf8');print(json.dumps(summary));
 if summary['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
