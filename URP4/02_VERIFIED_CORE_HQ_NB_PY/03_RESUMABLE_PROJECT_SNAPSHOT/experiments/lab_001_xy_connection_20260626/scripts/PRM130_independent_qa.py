from __future__ import annotations
import json
from pathlib import Path
import numpy as np,pandas as pd
R=Path(__file__).resolve().parents[3];T=R/'experiments/lab_001_xy_connection_20260626/reports/tables';O=R/'experiments/lab_001_xy_connection_20260626/factories/PRM-130/reports';O.mkdir(parents=True,exist_ok=True)
def main():
 g=pd.read_csv(T/'PRM130_overlay_fraction_quantile_candidate_registry.csv');v=pd.read_csv(T/'PRM130_overlay_fraction_quantile_values_long.csv');errs=[]
 for m in sorted(v.model_id.unique()):
  d=pd.read_csv(R/f'.tmp/t4rs4/P1000_S801/{m}/tables/overlay_pixel_readback.csv').sort_values('pair_index');u=np.maximum(d.union_pixel_count.to_numpy(float),1.);p={'red':d.red_pixel_count.to_numpy(float)/u,'blue':d.blue_pixel_count.to_numpy(float)/u,'purple':d.purple_pixel_count.to_numpy(float)/u};o=v[v.model_id.eq(m)].set_index('candidate_id').value.to_dict()
  for n,a in p.items():
   for s,z in {'q10':np.quantile(a,.1),'q50':np.quantile(a,.5),'q90':np.quantile(a,.9),'iqr':np.quantile(a,.75)-np.quantile(a,.25),'range':a.max()-a.min()}.items():errs.append(abs(z-o[f'RAW-X056::{n}_fraction_{s}']))
 locks=g.y_evidence.eq(False).all() and not g.active_feature.any() and not g.promoted.any();q=pd.DataFrame([dict(check_id='I130-01',status='PASS' if len(g)==15 and len(v)==870 and np.isfinite(v.value).all() else 'FAIL',detail='scope'),dict(check_id='I130-02',status='PASS' if max(errs)<=1e-12 else 'FAIL',detail=f'max replay={max(errs):.2e}'),dict(check_id='I130-03',status='PASS' if locks else 'FAIL',detail='no-y lock')]);q.to_csv(O/'PRM130_independent_QA.csv',index=False,encoding='utf-8-sig');s={'status':'PASS' if q.status.eq('PASS').all() else 'FAIL','checks':f"{q.status.eq('PASS').sum()}/{len(q)}",'max_replay_error':max(errs),'performance_y_read':0};(O/'PRM130_independent_QA_summary.json').write_text(json.dumps(s,indent=2),encoding='utf8');print(json.dumps(s));
 if s['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
