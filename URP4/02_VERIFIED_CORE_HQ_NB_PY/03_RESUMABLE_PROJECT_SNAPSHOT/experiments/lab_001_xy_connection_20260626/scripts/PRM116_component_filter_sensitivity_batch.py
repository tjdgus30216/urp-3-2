from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import pearsonr,spearmanr
ROOT=Path(__file__).resolve().parents[3];LAB=ROOT/'experiments'/'lab_001_xy_connection_20260626';TABLES=LAB/'reports'/'tables';FACTORY=LAB/'factories'/'PRM-116';CONTRACT=FACTORY/'contracts'/'PRM-116_COMPONENT_FILTER_SENSITIVITY_BC_BATCH_CONTRACT_20260723.json'
def sha256(path):
 d=hashlib.sha256()
 with path.open('rb') as h:
  for c in iter(lambda:h.read(1048576),b''):d.update(c)
 return d.hexdigest()
def mad(x):return float(np.median(np.abs(x-np.median(x))))
def lag1(x):
 if np.std(x[:-1])<=1e-12 or np.std(x[1:])<=1e-12:return 0.
 return float(np.corrcoef(x[:-1],x[1:])[0,1])
def metrics(raw,kept):
 d=raw-kept;f=d/np.maximum(raw,1)
 return {'raw_component_count_mean':float(raw.mean()),'raw_component_count_population_std':float(raw.std(ddof=0)),'raw_component_count_q10':float(np.quantile(raw,.10)),'raw_component_count_q90':float(np.quantile(raw,.90)),'raw_component_count_iqr':float(np.quantile(raw,.75)-np.quantile(raw,.25)),'raw_component_count_mad':mad(raw),'filter_removed_component_delta_mean':float(d.mean()),'filter_removed_component_delta_population_std':float(d.std(ddof=0)),'filter_removed_component_fraction_mean':float(f.mean()),'filter_removed_component_fraction_q90':float(np.quantile(f,.90)),'filter_removed_component_fraction_lag1_autocorr':lag1(f)}
def var(x):x=x[np.isfinite(x)];return len(x)>=3 and len(np.unique(x))>=3 and x.max()-x.min()>1e-10*max(1.,np.abs(x).max())
def rel(a,b):
 common=np.isfinite(a)&np.isfinite(b);a,b=a[common],b[common]
 if len(a)!=58:return {'common_models':len(a),'relation':'insufficient_common_coverage','pearson':np.nan,'spearman':np.nan,'normalized_L2_residual':np.nan}
 if not var(a) or not var(b):return {'common_models':58,'relation':'degenerate_nonvarying_reference_or_candidate','pearson':np.nan,'spearman':np.nan,'normalized_L2_residual':np.nan}
 if np.allclose(a,b,rtol=1e-10,atol=1e-12):return {'common_models':58,'relation':'exact_duplicate','pearson':1.,'spearman':1.,'normalized_L2_residual':0.}
 s=np.dot(a,b)/np.dot(a,a);r=float(np.linalg.norm(b-s*a)/max(np.linalg.norm(b),1e-30));p,q=float(pearsonr(a,b).statistic),float(spearmanr(a,b).statistic);k='proportional_duplicate' if r<=1e-6 and abs(s)>1e-12 else ('high_redundancy' if abs(p)>=.98 and abs(q)>=.98 else 'distinct_or_unresolved');return {'common_models':58,'relation':k,'pearson':p,'spearman':q,'normalized_L2_residual':r}
def main():
 c=json.loads(CONTRACT.read_text(encoding='utf-8'))
 for x in c['inputs']:
  if sha256(ROOT/x['path'])!=x['sha256']:raise RuntimeError(f"input hash mismatch: {x['path']}")
 manifest=pd.read_csv(ROOT/c['inputs'][0]['path']);xreg=pd.read_csv(ROOT/c['inputs'][2]['path']);models=sorted(xreg.model_id.unique());family=xreg[['model_id','model_family']].drop_duplicates().set_index('model_id').model_family.to_dict();frozen=dict(zip(manifest.path,manifest.sha256));rawpaths=[f'.tmp/t4rs4/P1000_S801/{m}/tables/overlay_pixel_readback.csv' for m in models]
 if len(models)!=58 or xreg.candidate_id.nunique()!=277 or any(p not in frozen or sha256(ROOT/p)!=frozen[p] for p in rawpaths):raise RuntimeError('frozen scope mismatch')
 grades={'raw_component_count_mean':'B','raw_component_count_population_std':'B','raw_component_count_q10':'B','raw_component_count_q90':'B','raw_component_count_iqr':'B','raw_component_count_mad':'B','filter_removed_component_delta_mean':'B','filter_removed_component_delta_population_std':'B','filter_removed_component_fraction_mean':'C','filter_removed_component_fraction_q90':'C','filter_removed_component_fraction_lag1_autocorr':'C'};records=[];meta={}
 for m in models:
  d=pd.read_csv(ROOT/f'.tmp/t4rs4/P1000_S801/{m}/tables/overlay_pixel_readback.csv').sort_values('pair_index');raw=d.component_count_raw.to_numpy(float);kept=d.component_count_min2.to_numpy(float)
  if len(d)!=800 or not np.all(raw>=kept) or not np.all(kept>=0):raise RuntimeError(f'component profile mismatch: {m}')
  for name,value in metrics(raw,kept).items():
   cid=f'RAW-X049::{name}';g=grades[name];records.append({'model_id':m,'model_family':family[m],'candidate_id':cid,'value':value,'operational_grade':g});meta.setdefault(cid,{'candidate_id':cid,'candidate_group_id':'RAW-X049','descriptor_family':'overlay_component_filter_sensitivity','output_name':name,'unit':'count' if ('count' in name or 'delta' in name) else 'dimensionless','source_population':'800-pair overlay component_count_raw and component_count_min2 profiles','aggregation_formula':'population raw-count statistic, raw-minus-min2 delta statistic, or normalized removed-fraction statistic','applicable_family':'B|C|F|L|T','direct_or_derived':'direct_statistic_from_verified_SLICE004_profile' if g=='B' else 'derived_filter_sensitivity_from_verified_SLICE004_profile','source_bank':'PRM116_component_filter_sensitivity_batch','source_value_table':'PRM116_component_filter_sensitivity_values_long.csv','technical_role':'batch_BC_candidate','qualification_status':'full58_raw_table_batch_not_selected','confidence_status':'confirmed_raw_table_lineage','later_evaluation_role':'batch_BC_unselected_block_aware','active_feature':False,'promoted':False,'y_evidence':False,'notes':'PRM116 raw-vs-min2 component-filter sensitivity batch; no y, selection, mask or slicing','operational_grade':g,'literature_anchor':'LIT-X035','anchor_scope':'2D overlay connected-component and threshold-sensitivity statistic only; not a full 3D topology estimator'})
 values=pd.DataFrame(records);reg=pd.DataFrame(meta.values()).sort_values('candidate_id').reset_index(drop=True);ids=reg.candidate_id.tolist()
 if len(ids)!=11 or len(values)!=638 or not np.isfinite(values.value).all() or (reg.operational_grade=='B').sum()!=8 or (reg.operational_grade=='C').sum()!=3:raise RuntimeError('candidate scope mismatch')
 wide=values.pivot(index='model_id',columns='candidate_id',values='value').reindex(index=models,columns=ids);cover=pd.DataFrame([{'candidate_id':z,'finite_count':58,'missing_count':0,'unique_count':int(wide[z].nunique()),'population_std_across_models':float(wide[z].std(ddof=0)),'iqr_across_models':float(np.quantile(wide[z],.75)-np.quantile(wide[z],.25)),'operational_grade':reg.set_index('candidate_id').loc[z,'operational_grade'],'technical_status':'batch_BC_unselected'} for z in ids]);old={z:g.set_index('model_id').reindex(models).value.to_numpy(float) for z,g in xreg.groupby('candidate_id')};cross=pd.DataFrame([{'candidate_id':z,'existing_candidate_id':o,**rel(wide[z].to_numpy(float),v),'evidence_scope':'full58_x_only','selection_effect':'none'} for z in ids for o,v in sorted(old.items())]);internal=pd.DataFrame([{'left_candidate_id':a,'right_candidate_id':b,**rel(wide[a].to_numpy(float),wide[b].to_numpy(float)),'evidence_scope':'full58_x_only','selection_effect':'none'} for i,a in enumerate(ids) for b in ids[i+1:]]);collision=pd.DataFrame([{'pair_id':p,'candidate_id':z,'absolute_delta':abs(float(wide.loc[a,z])-float(wide.loc[b,z])),'relative_delta':abs(float(wide.loc[a,z])-float(wide.loc[b,z]))/max(abs(float(wide.loc[a,z])),abs(float(wide.loc[b,z])),1e-12),'diagnostic_only':True} for a,b,p in [('T8','T9','T8_T9'),('T5','T6','T5_T6')] for z in ids])
 for suffix,frame in {'candidate_registry':reg,'values_long':values,'values_wide':wide.reset_index(),'coverage_variation':cover,'vs_XREG_v1_0_redundancy':cross,'internal_redundancy':internal,'collision_diagnostic':collision}.items():frame.to_csv(TABLES/f'PRM116_component_filter_sensitivity_{suffix}.csv',index=False,encoding='utf-8-sig',float_format='%.17g')
 checks=[('P116-01',len(models)==58,'58 XREG-v1.0 models'),('P116-02',len(rawpaths)==58,'58 hash-verified overlay sources'),('P116-03',len(ids)==11,'11 candidates'),('P116-04',len(values)==638 and np.isfinite(values.value).all(),'638 finite values'),('P116-05',len(cross)==3047,'3,047 crossbank relations'),('P116-06',len(internal)==55,'55 internal relations'),('P116-07',len(collision)==22,'two collision pairs x 11'),('P116-08',not reg[['active_feature','promoted','y_evidence']].any().any() and all(v==0 for v in c['locks'].values()),'no y, selection or promotion and locks intact')];qa=pd.DataFrame([{'check_id':i,'status':'PASS' if ok else 'FAIL','detail':d} for i,ok,d in checks]);(FACTORY/'reports').mkdir(parents=True,exist_ok=True);qa.to_csv(FACTORY/'reports'/'PRM116_producer_QA.csv',index=False,encoding='utf-8-sig');summary={'status':'PASS' if qa.status.eq('PASS').all() else 'FAIL','checks':f"{qa.status.eq('PASS').sum()}/{len(qa)}",'models':58,'candidates':11,'grade_B':8,'grade_C':3,'values':638,'y_fit_selection_promotion':'0/0/0/0'};(FACTORY/'reports'/'PRM116_batch_summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,indent=2));
 if summary['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
