from __future__ import annotations
import numpy as np,pandas as pd
from pathlib import Path
from scipy.stats import pearsonr,spearmanr
R=Path(__file__).resolve().parents[3];T=R/'experiments/lab_001_xy_connection_20260626/reports/tables';F=R/'experiments/lab_001_xy_connection_20260626/factories/PRM-130';F.mkdir(parents=True,exist_ok=True)
def rel(a,b):
 m=np.isfinite(a)&np.isfinite(b);a,b=a[m],b[m]
 if len(a)!=58:return dict(common_models=len(a),relation='insufficient_common_coverage',pearson=np.nan,spearman=np.nan)
 if len(np.unique(a))<3 or len(np.unique(b))<3:return dict(common_models=58,relation='degenerate_nonvarying_reference_or_candidate',pearson=np.nan,spearman=np.nan)
 p=float(pearsonr(a,b).statistic);s=float(spearmanr(a,b).statistic);return dict(common_models=58,relation='high_redundancy' if abs(p)>=.98 and abs(s)>=.98 else 'distinct_or_unresolved',pearson=p,spearman=s)
def main():
 x=pd.read_csv(T/'PRM129_xreg_v1_7_values_long.csv');models=sorted(x.model_id.unique());fam=x[['model_id','model_family']].drop_duplicates().set_index('model_id').model_family.to_dict();rows=[];meta={}
 for m in models:
  d=pd.read_csv(R/f'.tmp/t4rs4/P1000_S801/{m}/tables/overlay_pixel_readback.csv').sort_values('pair_index');u=np.maximum(d.union_pixel_count.to_numpy(float),1.);p={'red':d.red_pixel_count.to_numpy(float)/u,'blue':d.blue_pixel_count.to_numpy(float)/u,'purple':d.purple_pixel_count.to_numpy(float)/u}
  for phase,a in p.items():
   for stat,v in {'q10':np.quantile(a,.1),'q50':np.quantile(a,.5),'q90':np.quantile(a,.9),'iqr':np.quantile(a,.75)-np.quantile(a,.25),'range':a.max()-a.min()}.items():
    cid=f'RAW-X056::{phase}_fraction_{stat}';grade='B' if stat in ['q10','q50','q90'] else 'C';rows.append(dict(model_id=m,model_family=fam[m],candidate_id=cid,value=float(v),operational_grade=grade));meta.setdefault(cid,dict(candidate_id=cid,candidate_group_id='RAW-X056',descriptor_family='overlay_phase_fraction_distribution',output_name=cid.split('::')[1],unit='dimensionless_fraction',source_population='800-pair verified red/blue/purple overlay fractions',aggregation_formula='profile quantile, IQR, or range of each overlay colour fraction',applicable_family='B|C|F|L|T',direct_or_derived='derived_statistic_from_verified_SLICE004_profile',source_bank='PRM130_overlay_fraction_quantile_batch',source_value_table='PRM130_overlay_fraction_quantile_values_long.csv',technical_role='batch_BC_candidate',qualification_status='full58_raw_table_batch_not_selected',confidence_status='confirmed_raw_table_lineage',later_evaluation_role='batch_BC_unselected_block_aware',active_feature=False,promoted=False,y_evidence=False,notes='PRM130 no y',operational_grade=grade,literature_anchor='LIT-X035',anchor_scope='2D overlay phase distribution only'))
 v=pd.DataFrame(rows);g=pd.DataFrame(meta.values()).sort_values('candidate_id');ids=g.candidate_id.tolist();w=v.pivot(index='model_id',columns='candidate_id',values='value').reindex(index=models,columns=ids);old={z:q.set_index('model_id').reindex(models).value.to_numpy(float) for z,q in x.groupby('candidate_id')};cross=pd.DataFrame([dict(candidate_id=z,existing_candidate_id=o,**rel(w[z].to_numpy(float),a),evidence_scope='full58_x_only',selection_effect='none') for z in ids for o,a in old.items()]);inter=pd.DataFrame([dict(left_candidate_id=a,right_candidate_id=b,**rel(w[a].to_numpy(float),w[b].to_numpy(float)),evidence_scope='full58_x_only',selection_effect='none') for n,a in enumerate(ids) for b in ids[n+1:]])
 for n,d in {'candidate_registry':g,'values_long':v,'values_wide':w.reset_index(),'vs_XREG_v1_7_redundancy':cross,'internal_redundancy':inter}.items():d.to_csv(T/f'PRM130_overlay_fraction_quantile_{n}.csv',index=False,encoding='utf-8-sig')
 q=pd.DataFrame([dict(check_id='P130-01',status='PASS' if len(g)==15 and len(v)==870 and np.isfinite(v.value).all() and len(cross)==15*401 and len(inter)==105 else 'FAIL',detail='scope')]);q.to_csv(F/'PRM130_producer_QA.csv',index=False,encoding='utf-8-sig');print(q.to_dict('records'))
 if not q.status.eq('PASS').all():raise SystemExit(1)
if __name__=='__main__':main()
