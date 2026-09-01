from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np,pandas as pd
from scipy.stats import pearsonr,spearmanr
ROOT=Path(__file__).resolve().parents[3];LAB=ROOT/'experiments'/'lab_001_xy_connection_20260626';T=LAB/'reports'/'tables';F=LAB/'factories'/'PRM-118';C=F/'contracts'/'PRM-118_SLICE_COMPONENT_FILTER_SENSITIVITY_BC_BATCH_CONTRACT_20260723.json'
def h(p):
 d=hashlib.sha256()
 with p.open('rb') as f:
  for x in iter(lambda:f.read(1048576),b''):d.update(x)
 return d.hexdigest()
def met(raw,kept):
 d=raw-kept;q=d/np.maximum(raw,1);lag=0. if np.std(q[:-1])<1e-12 or np.std(q[1:])<1e-12 else float(np.corrcoef(q[:-1],q[1:])[0,1]);mad=lambda x:float(np.median(np.abs(x-np.median(x))));return {'raw_component_count_mean':float(raw.mean()),'raw_component_count_population_std':float(raw.std(ddof=0)),'raw_component_count_q10':float(np.quantile(raw,.1)),'raw_component_count_q90':float(np.quantile(raw,.9)),'raw_component_count_iqr':float(np.quantile(raw,.75)-np.quantile(raw,.25)),'raw_component_count_mad':mad(raw),'filter_removed_component_delta_mean':float(d.mean()),'filter_removed_component_delta_population_std':float(d.std(ddof=0)),'filter_removed_component_fraction_mean':float(q.mean()),'filter_removed_component_fraction_q90':float(np.quantile(q,.9)),'filter_removed_component_fraction_lag1_autocorr':lag}
def rel(a,b):
 m=np.isfinite(a)&np.isfinite(b);a,b=a[m],b[m]
 if len(a)!=58:return {'common_models':len(a),'relation':'insufficient_common_coverage','pearson':np.nan,'spearman':np.nan,'normalized_L2_residual':np.nan}
 if len(np.unique(a))<3 or len(np.unique(b))<3:return {'common_models':58,'relation':'degenerate_nonvarying_reference_or_candidate','pearson':np.nan,'spearman':np.nan,'normalized_L2_residual':np.nan}
 if np.allclose(a,b,rtol=1e-10,atol=1e-12):return {'common_models':58,'relation':'exact_duplicate','pearson':1.,'spearman':1.,'normalized_L2_residual':0.}
 s=np.dot(a,b)/np.dot(a,a);r=float(np.linalg.norm(b-s*a)/max(np.linalg.norm(b),1e-30));p,q=float(pearsonr(a,b).statistic),float(spearmanr(a,b).statistic);z='proportional_duplicate' if r<=1e-6 else ('high_redundancy' if abs(p)>=.98 and abs(q)>=.98 else 'distinct_or_unresolved');return {'common_models':58,'relation':z,'pearson':p,'spearman':q,'normalized_L2_residual':r}
def main():
 c=json.loads(C.read_text(encoding='utf8'))
 for x in c['inputs']:
  if h(ROOT/x['path'])!=x['sha256']:raise RuntimeError('hash')
 man=pd.read_csv(ROOT/c['inputs'][0]['path']);xreg=pd.read_csv(ROOT/c['inputs'][2]['path']);models=sorted(xreg.model_id.unique());fam=xreg[['model_id','model_family']].drop_duplicates().set_index('model_id').model_family.to_dict();frozen=dict(zip(man.path,man.sha256));paths=[f'.tmp/t4rs4/P1000_S801/{m}/tables/slice_pixel_readback.csv' for m in models]
 if len(models)!=58 or xreg.candidate_id.nunique()!=288 or any(p not in frozen or h(ROOT/p)!=frozen[p] for p in paths):raise RuntimeError('scope')
 grades={k:('B' if i<8 else 'C') for i,k in enumerate(next(iter([met(np.arange(1,5),np.arange(1,5))])).keys())};R=[];M={}
 for m in models:
  d=pd.read_csv(ROOT/f'.tmp/t4rs4/P1000_S801/{m}/tables/slice_pixel_readback.csv').sort_values('slice_index');raw=d.component_count_raw.to_numpy(float);keep=d.component_count_min2.to_numpy(float)
  if len(d)!=801 or not np.all(raw>=keep):raise RuntimeError('source')
  for n,v in met(raw,keep).items():
   cid=f'RAW-X050::{n}';g=grades[n];R.append({'model_id':m,'model_family':fam[m],'candidate_id':cid,'value':v,'operational_grade':g});M.setdefault(cid,{'candidate_id':cid,'candidate_group_id':'RAW-X050','descriptor_family':'slice_component_filter_sensitivity','output_name':n,'unit':'count' if ('count' in n or 'delta' in n) else 'dimensionless','source_population':'801-slice component_count_raw and component_count_min2 profiles','aggregation_formula':'population raw-count statistic, raw-minus-min2 delta statistic, or normalized removed-fraction statistic','applicable_family':'B|C|F|L|T','direct_or_derived':'direct_statistic_from_verified_SLICE004_profile' if g=='B' else 'derived_filter_sensitivity_from_verified_SLICE004_profile','source_bank':'PRM118_slice_component_filter_sensitivity_batch','source_value_table':'PRM118_slice_component_filter_sensitivity_values_long.csv','technical_role':'batch_BC_candidate','qualification_status':'full58_raw_table_batch_not_selected','confidence_status':'confirmed_raw_table_lineage','later_evaluation_role':'batch_BC_unselected_block_aware','active_feature':False,'promoted':False,'y_evidence':False,'notes':'PRM118 slice raw-vs-min2 filter sensitivity; no y','operational_grade':g,'literature_anchor':'LIT-X034','anchor_scope':'2D slice connected-component threshold statistic only'})
 V=pd.DataFrame(R);G=pd.DataFrame(M.values()).sort_values('candidate_id');ids=G.candidate_id.tolist();W=V.pivot(index='model_id',columns='candidate_id',values='value').reindex(index=models,columns=ids)
 old={z:g.set_index('model_id').reindex(models).value.to_numpy(float) for z,g in xreg.groupby('candidate_id')};cross=pd.DataFrame([{'candidate_id':z,'existing_candidate_id':o,**rel(W[z].to_numpy(float),v),'evidence_scope':'full58_x_only','selection_effect':'none'} for z in ids for o,v in old.items()]);internal=pd.DataFrame([{'left_candidate_id':a,'right_candidate_id':b,**rel(W[a].to_numpy(float),W[b].to_numpy(float)),'evidence_scope':'full58_x_only','selection_effect':'none'} for i,a in enumerate(ids) for b in ids[i+1:]]);coll=pd.DataFrame([{'pair_id':p,'candidate_id':z,'absolute_delta':abs(float(W.loc[a,z])-float(W.loc[b,z]))} for a,b,p in [('T8','T9','T8_T9'),('T5','T6','T5_T6')] for z in ids])
 if len(ids)!=11 or len(V)!=638 or not np.isfinite(V.value).all() or len(cross)!=3168 or len(internal)!=55:raise RuntimeError('outputs')
 for s,d in {'candidate_registry':G,'values_long':V,'values_wide':W.reset_index(),'vs_XREG_v1_1_redundancy':cross,'internal_redundancy':internal,'collision_diagnostic':coll}.items():d.to_csv(T/f'PRM118_slice_component_filter_sensitivity_{s}.csv',index=False,encoding='utf-8-sig',float_format='%.17g')
 qa=pd.DataFrame([{'check_id':f'P118-{i:02d}','status':'PASS','detail':d} for i,d in enumerate(['58 models','58 sources','11 candidates','638 finite','3168 crossbank','55 internal','22 collisions','no y locks'],1)]);(F/'reports').mkdir(parents=True,exist_ok=True);qa.to_csv(F/'reports'/'PRM118_producer_QA.csv',index=False,encoding='utf-8-sig');out={'status':'PASS','checks':'8/8','models':58,'candidates':11,'values':638,'y_fit_selection_promotion':'0/0/0/0'};(F/'reports'/'PRM118_batch_summary.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
