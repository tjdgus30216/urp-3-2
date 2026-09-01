from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import pearsonr,spearmanr

ROOT=Path(__file__).resolve().parents[3]; LAB=ROOT/'experiments'/'lab_001_xy_connection_20260626'; TABLES=LAB/'reports'/'tables'; FACTORY=LAB/'factories'/'PRM-114'; CONTRACT=FACTORY/'contracts'/'PRM-114_OVERLAY_COMPONENT_INEQUALITY_CONCENTRATION_BC_BATCH_CONTRACT_20260723.json'
def sha256(path):
 d=hashlib.sha256()
 with path.open('rb') as h:
  for c in iter(lambda:h.read(1048576),b''):d.update(c)
 return d.hexdigest()
def area_stats(x):
 x=np.sort(np.asarray(x,float)); n=len(x); total=x.sum(); p=x/total
 return {'component_area_q95_mm2':float(np.quantile(x,.95)),'component_area_q99_mm2':float(np.quantile(x,.99)),'component_area_gini':float(np.dot(2*np.arange(1,n+1)-n-1,x)/(n*total)),'component_area_normalized_entropy':float(-np.dot(p,np.log(p))/np.log(n)),'component_area_hhi':float(np.dot(p,p)),'component_area_cv':float(x.std(ddof=0)/x.mean())}
def pair_stats(df):
 shares=df.groupby('pair_index').area_mm2.apply(lambda s:float(s.max()/s.sum())).to_numpy(float)
 return {'pair_largest_component_share_mean':float(shares.mean()),'pair_largest_component_share_population_std':float(shares.std(ddof=0)),'pair_largest_component_share_q10':float(np.quantile(shares,.10)),'pair_largest_component_share_q50':float(np.quantile(shares,.50)),'pair_largest_component_share_q90':float(np.quantile(shares,.90)),'pair_largest_component_share_iqr':float(np.quantile(shares,.75)-np.quantile(shares,.25))}
def variable(x):
 x=x[np.isfinite(x)];return len(x)>=3 and len(np.unique(x))>=3 and x.max()-x.min()>1e-10*max(1.,np.abs(x).max())
def relation(a,b):
 common=np.isfinite(a)&np.isfinite(b); a,b=a[common],b[common]
 if len(a)!=58:return {'common_models':len(a),'relation':'insufficient_common_coverage','pearson':np.nan,'spearman':np.nan,'normalized_L2_residual':np.nan}
 if not variable(a) or not variable(b):return {'common_models':58,'relation':'degenerate_nonvarying_reference_or_candidate','pearson':np.nan,'spearman':np.nan,'normalized_L2_residual':np.nan}
 if np.allclose(a,b,rtol=1e-10,atol=1e-12):return {'common_models':58,'relation':'exact_duplicate','pearson':1.,'spearman':1.,'normalized_L2_residual':0.}
 slope=np.dot(a,b)/np.dot(a,a);res=float(np.linalg.norm(b-slope*a)/max(np.linalg.norm(b),1e-30));pe,sp=float(pearsonr(a,b).statistic),float(spearmanr(a,b).statistic); kind='proportional_duplicate' if res<=1e-6 and abs(slope)>1e-12 else ('high_redundancy' if abs(pe)>=.98 and abs(sp)>=.98 else 'distinct_or_unresolved');return {'common_models':58,'relation':kind,'pearson':pe,'spearman':sp,'normalized_L2_residual':res}
def main():
 contract=json.loads(CONTRACT.read_text(encoding='utf-8'))
 for item in contract['inputs']:
  if sha256(ROOT/item['path'])!=item['sha256']:raise RuntimeError(f"input hash mismatch: {item['path']}")
 manifest=pd.read_csv(ROOT/contract['inputs'][0]['path']); xreg=pd.read_csv(ROOT/contract['inputs'][2]['path']);models=sorted(xreg.model_id.unique());family=xreg[['model_id','model_family']].drop_duplicates().set_index('model_id').model_family.to_dict();frozen=dict(zip(manifest.path,manifest.sha256))
 if len(models)!=58 or xreg.candidate_id.nunique()!=265:raise RuntimeError('XREG-v0.9 scope mismatch')
 raw=[f'.tmp/t4rs4/P1000_S801/{m}/tables/overlay_component_population.csv' for m in models]
 if any(p not in frozen or sha256(ROOT/p)!=frozen[p] for p in raw):raise RuntimeError('raw source hash/coverage mismatch')
 records=[];meta={};grades={'component_area_q95_mm2':'B','component_area_q99_mm2':'B','component_area_gini':'C','component_area_normalized_entropy':'C','component_area_hhi':'C','component_area_cv':'C','pair_largest_component_share_mean':'B','pair_largest_component_share_population_std':'B','pair_largest_component_share_q10':'C','pair_largest_component_share_q50':'B','pair_largest_component_share_q90':'C','pair_largest_component_share_iqr':'C'}
 units={k:('mm2' if 'area_q' in k else 'dimensionless') for k in grades}
 for model in models:
  df=pd.read_csv(ROOT/f'.tmp/t4rs4/P1000_S801/{model}/tables/overlay_component_population.csv');df=df[df.kept_by_min2.astype(bool)].copy()
  if len(df)<2 or not (df.area_mm2>0).all() or df.pair_index.nunique()!=800:raise RuntimeError(f'component population mismatch: {model}')
  metrics=area_stats(df.area_mm2.to_numpy(float))|pair_stats(df)
  for name,value in metrics.items():
   cid=f'RAW-X048::{name}';grade=grades[name];records.append({'model_id':model,'model_family':family[model],'candidate_id':cid,'value':value,'operational_grade':grade})
   meta.setdefault(cid,{'candidate_id':cid,'candidate_group_id':'RAW-X048','descriptor_family':'overlay_component_inequality_concentration','output_name':name,'unit':units[name],'source_population':'all kept overlay connected-component areas across 800 layer pairs' if name.startswith('component_area') else '800 pairwise largest kept-component area shares','aggregation_formula':('population q95/q99; Gini; normalized Shannon entropy; HHI; or population CV' if name.startswith('component_area') else 'population statistic across max(component area)/sum(component area) for each pair'),'applicable_family':'B|C|F|L|T','direct_or_derived':'direct_statistic_from_verified_SLICE004_component_table' if grade=='B' else 'derived_normalized_concentration_from_verified_SLICE004_component_table','source_bank':'PRM114_overlay_component_inequality_concentration_batch','source_value_table':'PRM114_overlay_component_inequality_concentration_values_long.csv','technical_role':'batch_BC_candidate','qualification_status':'full58_raw_table_batch_not_selected','confidence_status':'confirmed_raw_table_lineage','later_evaluation_role':'batch_BC_unselected_block_aware','active_feature':False,'promoted':False,'y_evidence':False,'notes':'PRM114 component inequality/concentration batch; no y, selection, mask or slicing','operational_grade':grade,'literature_anchor':'LIT-X035','anchor_scope':'connected-component area distribution statistic only; not a full 3D topology estimator'})
 values=pd.DataFrame(records);registry=pd.DataFrame(meta.values()).sort_values('candidate_id').reset_index(drop=True);ids=registry.candidate_id.tolist()
 if len(ids)!=12 or len(values)!=696 or not np.isfinite(values.value).all() or (registry.operational_grade=='B').sum()!=5 or (registry.operational_grade=='C').sum()!=7:raise RuntimeError('candidate/value/grade scope mismatch')
 wide=values.pivot(index='model_id',columns='candidate_id',values='value').reindex(index=models,columns=ids);coverage=pd.DataFrame([{'candidate_id':c,'finite_count':58,'missing_count':0,'unique_count':int(wide[c].nunique()),'population_std_across_models':float(wide[c].std(ddof=0)),'iqr_across_models':float(np.quantile(wide[c],.75)-np.quantile(wide[c],.25)),'operational_grade':registry.set_index('candidate_id').loc[c,'operational_grade'],'technical_status':'batch_BC_unselected'} for c in ids]);old={c:g.set_index('model_id').reindex(models).value.to_numpy(float) for c,g in xreg.groupby('candidate_id')};cross=pd.DataFrame([{'candidate_id':c,'existing_candidate_id':o,**relation(wide[c].to_numpy(float),v),'evidence_scope':'full58_x_only','selection_effect':'none'} for c in ids for o,v in sorted(old.items())]);internal=pd.DataFrame([{'left_candidate_id':a,'right_candidate_id':b,**relation(wide[a].to_numpy(float),wide[b].to_numpy(float)),'evidence_scope':'full58_x_only','selection_effect':'none'} for i,a in enumerate(ids) for b in ids[i+1:]]);collision=pd.DataFrame([{'pair_id':pair,'candidate_id':c,'absolute_delta':abs(float(wide.loc[l,c])-float(wide.loc[r,c])),'relative_delta':abs(float(wide.loc[l,c])-float(wide.loc[r,c]))/max(abs(float(wide.loc[l,c])),abs(float(wide.loc[r,c])),1e-12),'diagnostic_only':True} for l,r,pair in [('T8','T9','T8_T9'),('T5','T6','T5_T6')] for c in ids])
 for suffix,frame in {'candidate_registry':registry,'values_long':values,'values_wide':wide.reset_index(),'coverage_variation':coverage,'vs_XREG_v0_9_redundancy':cross,'internal_redundancy':internal,'collision_diagnostic':collision}.items():frame.to_csv(TABLES/f'PRM114_overlay_component_inequality_concentration_{suffix}.csv',index=False,encoding='utf-8-sig',float_format='%.17g')
 checks=[('P114-01',len(models)==58,'58 XREG-v0.9 models'),('P114-02',len(raw)==58,'58 hash-verified component sources'),('P114-03',len(ids)==12,'12 candidates'),('P114-04',len(values)==696 and np.isfinite(values.value).all(),'696 finite values'),('P114-05',len(cross)==12*265,'3,180 crossbank relations'),('P114-06',len(internal)==66,'66 internal relations'),('P114-07',len(collision)==24,'two collision pairs x 12'),('P114-08',not registry[['active_feature','promoted','y_evidence']].any().any() and all(v==0 for v in contract['locks'].values()),'no y, selection or promotion and locks intact')];qa=pd.DataFrame([{'check_id':i,'status':'PASS' if ok else 'FAIL','detail':d} for i,ok,d in checks]);(FACTORY/'reports').mkdir(parents=True,exist_ok=True);qa.to_csv(FACTORY/'reports'/'PRM114_producer_QA.csv',index=False,encoding='utf-8-sig');summary={'status':'PASS' if qa.status.eq('PASS').all() else 'FAIL','checks':f"{qa.status.eq('PASS').sum()}/{len(qa)}",'models':58,'candidates':12,'grade_B':5,'grade_C':7,'values':696,'y_fit_selection_promotion':'0/0/0/0'};(FACTORY/'reports'/'PRM114_batch_summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,indent=2));
 if summary['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
