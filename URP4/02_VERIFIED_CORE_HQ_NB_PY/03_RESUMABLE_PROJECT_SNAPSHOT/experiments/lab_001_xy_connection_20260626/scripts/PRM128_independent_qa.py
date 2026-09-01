from __future__ import annotations
import json
from pathlib import Path
import numpy as np,pandas as pd
from scipy.stats import pearsonr,spearmanr
R=Path(__file__).resolve().parents[3];T=R/'experiments/lab_001_xy_connection_20260626/reports/tables';O=R/'experiments/lab_001_xy_connection_20260626/factories/PRM-128/reports';O.mkdir(parents=True,exist_ok=True)
def c(a,b,k):return 0. if np.std(a)==0 or np.std(b)==0 else float(pearsonr(a,b).statistic if k=='pearson' else spearmanr(a,b).statistic)
def main():
 g=pd.read_csv(T/'PRM128_overlay_phase_cross_correlation_candidate_registry.csv');v=pd.read_csv(T/'PRM128_overlay_phase_cross_correlation_values_long.csv');models=sorted(v.model_id.unique());errs=[]
 for m in models:
  d=pd.read_csv(R/f'.tmp/t4rs4/P1000_S801/{m}/tables/overlay_pixel_readback.csv').sort_values('pair_index');u=np.maximum(d.union_pixel_count.to_numpy(float),1.);z={'red':d.red_pixel_count.to_numpy(float)/u,'blue':d.blue_pixel_count.to_numpy(float)/u,'purple':d.purple_pixel_count.to_numpy(float)/u};obs=v[v.model_id.eq(m)].set_index('candidate_id').value.to_dict()
  for a,b in [('red','blue'),('red','purple'),('blue','purple')]:
   for lag in [0,1]:
    x,y=(z[a],z[b]) if lag==0 else (z[a][:-1],z[b][1:])
    for k in ['pearson','spearman']:errs.append(abs(c(x,y,k)-obs[f'RAW-X055::{a}_{b}_lag{lag}_{k}_correlation']))
 locks=g.y_evidence.eq(False).all() and not g.active_feature.any() and not g.promoted.any();checks=[('I128-01',len(g)==12 and len(models)==58,'12 candidates/58 models'),('I128-02',len(v)==696 and np.isfinite(v.value).all(),'finite values'),('I128-03',max(errs)<=1e-12,f'replay max={max(errs):.2e}'),('I128-04',all((R/f'.tmp/t4rs4/P1000_S801/{m}/tables/overlay_pixel_readback.csv').is_file() for m in models),'sources'),('I128-05',locks,'no-y lock')];q=pd.DataFrame([dict(check_id=a,status='PASS' if b else 'FAIL',detail=c) for a,b,c in checks]);q.to_csv(O/'PRM128_independent_QA.csv',index=False,encoding='utf-8-sig');s={'status':'PASS' if q.status.eq('PASS').all() else 'FAIL','checks':f"{q.status.eq('PASS').sum()}/{len(q)}",'max_replay_error':max(errs),'performance_y_read':0};(O/'PRM128_independent_QA_summary.json').write_text(json.dumps(s,indent=2),encoding='utf8');print(json.dumps(s));
 if s['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
