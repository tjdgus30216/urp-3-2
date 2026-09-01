from __future__ import annotations
import json
from pathlib import Path
import numpy as np,pandas as pd
R=Path(__file__).resolve().parents[3];T=R/'experiments/lab_001_xy_connection_20260626/reports/tables';O=R/'experiments/lab_001_xy_connection_20260626/factories/PRM-143/reports';O.mkdir(parents=True,exist_ok=True)
def c(batch,cons,ver,prior,pver):
 g=pd.read_csv(T/f'PRM{batch}_candidate_registry.csv');v=pd.read_csv(T/f'PRM{batch}_values_long.csv');b=pd.read_csv(T/f'PRM{cons}_xreg_{ver}_candidate_bank.csv');bv=pd.read_csv(T/f'PRM{cons}_xreg_{ver}_values_long.csv');p=pd.read_csv(T/f'PRM{prior}_xreg_{pver}_values_long.csv');old=bv[bv.candidate_id.isin(p.candidate_id)].sort_values(['model_id','candidate_id']).reset_index(drop=True);ref=p.sort_values(['model_id','candidate_id']).reset_index(drop=True);new=bv[bv.candidate_id.isin(g.candidate_id)].sort_values(['model_id','candidate_id']).reset_index(drop=True);nref=v.sort_values(['model_id','candidate_id']).reset_index(drop=True);return dict(batch=batch,candidates=len(g),finite=int(np.isfinite(v.value).sum()),bank=len(b),values=len(bv),blocks=b.unified_block_id.nunique(),replay_prior=bool(len(old)==len(ref) and np.allclose(old.value,ref.value,rtol=1e-12,atol=1e-12,equal_nan=True)),replay_cohort=bool(len(new)==len(nref) and np.allclose(new.value,nref.value,rtol=1e-12,atol=1e-12)),no_y=bool(b.y_evidence.astype(str).str.lower().eq('false').all() and not b.active_feature.any() and not b.promoted.any()))
def main():
 r=[c(138,139,'v2_2',137,'v2_1'),c(140,141,'v2_3',139,'v2_2'),c(142,143,'v2_4',141,'v2_3')];ok=all(x['finite']==x['candidates']*58 and x['replay_prior'] and x['replay_cohort'] and x['no_y'] for x in r);q=pd.DataFrame(r);q['status']='PASS' if ok else 'FAIL';q.to_csv(O/'PRM138_143_independent_QA.csv',index=False,encoding='utf-8-sig');s={'status':'PASS' if ok else 'FAIL','cycles':3,'checks':'3/3' if ok else 'failed','final_bank':r[-1]['bank'],'final_values':r[-1]['values'],'performance_y_read':0};(O/'PRM138_143_independent_QA_summary.json').write_text(json.dumps(s,indent=2),encoding='utf8');print(json.dumps(s));
 if not ok:raise SystemExit(1)
if __name__=='__main__':main()
