from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np,pandas as pd
from scipy.stats import pearsonr,spearmanr
ROOT=Path(__file__).resolve().parents[3];LAB=ROOT/'experiments'/'lab_001_xy_connection_20260626';T=LAB/'reports'/'tables';F=LAB/'factories'/'PRM-122';C=F/'contracts'/'PRM-122_PROFILE_JUMP_AND_TURN_BC_BATCH_CONTRACT_20260723.json'
def h(p):
 d=hashlib.sha256()
 with p.open('rb') as f:
  for x in iter(lambda:f.read(1048576),b''):d.update(x)
 return d.hexdigest()
def metrics(x):
 x=np.asarray(x,float); d=np.diff(x); scale=max(float(np.mean(np.abs(x))),1e-30); q=np.abs(d)/scale; s=np.sign(d); valid=(s[:-1]!=0)&(s[1:]!=0); turns=0. if not valid.any() else float(np.mean(s[:-1][valid]!=s[1:][valid]));return {'normalized_rms_adjacent_gradient':float(np.sqrt(np.mean((d/scale)**2))),'normalized_q90_adjacent_jump':float(np.quantile(q,.9)),'normalized_max_adjacent_jump':float(q.max()),'adjacent_gradient_turn_rate':turns}
def var(x):
 x=x[np.isfinite(x)];return len(x)>=3 and len(np.unique(x))>=3 and x.max()-x.min()>1e-10*max(1.,abs(x).max())
def rel(a,b):
 m=np.isfinite(a)&np.isfinite(b);a,b=a[m],b[m]
 if len(a)!=58:return {'common_models':len(a),'relation':'insufficient_common_coverage','pearson':np.nan,'spearman':np.nan,'normalized_L2_residual':np.nan}
 if not var(a) or not var(b):return {'common_models':58,'relation':'degenerate_nonvarying_reference_or_candidate','pearson':np.nan,'spearman':np.nan,'normalized_L2_residual':np.nan}
 if np.allclose(a,b,rtol=1e-10,atol=1e-12):return {'common_models':58,'relation':'exact_duplicate','pearson':1.,'spearman':1.,'normalized_L2_residual':0.}
 k=np.dot(a,b)/np.dot(a,a);r=float(np.linalg.norm(b-k*a)/max(np.linalg.norm(b),1e-30));p,s=float(pearsonr(a,b).statistic),float(spearmanr(a,b).statistic);z='proportional_duplicate' if r<=1e-6 else ('high_redundancy' if abs(p)>=.98 and abs(s)>=.98 else 'distinct_or_unresolved');return {'common_models':58,'relation':z,'pearson':p,'spearman':s,'normalized_L2_residual':r}
def main():
 c=json.loads(C.read_text());
 for x in c['inputs']:
  if h(ROOT/x['path'])!=x['sha256']:raise RuntimeError('hash')
 man=pd.read_csv(ROOT/c['inputs'][0]['path']);bank=pd.read_csv(ROOT/c['inputs'][1]['path']);xreg=pd.read_csv(ROOT/c['inputs'][2]['path']);models=sorted(xreg.model_id.unique());fam=xreg[['model_id','model_family']].drop_duplicates().set_index('model_id').model_family.to_dict(); frozen=dict(zip(man.path,man.sha256));profiles={'slice_material_area':('slice_pixel_readback.csv','material_area_mm2'),'slice_component_count':('slice_pixel_readback.csv','component_count_min2'),'overlay_union_pixel_count':('overlay_pixel_readback.csv','union_pixel_count'),'overlay_red_pixel_count':('overlay_pixel_readback.csv','red_pixel_count'),'overlay_blue_pixel_count':('overlay_pixel_readback.csv','blue_pixel_count'),'overlay_purple_pixel_count':('overlay_pixel_readback.csv','purple_pixel_count')}
 paths=[f'.tmp/t4rs4/P1000_S801/{m}/tables/{f}' for m in models for f,_ in profiles.values()]
 if len(models)!=58 or bank.candidate_id.nunique()!=323 or any(p not in frozen or h(ROOT/p)!=frozen[p] for p in paths):raise RuntimeError('scope')
 R=[];M={}
 for m in models:
  cache={f:pd.read_csv(ROOT/f'.tmp/t4rs4/P1000_S801/{m}/tables/{f}') for f,_ in profiles.values()}
  for prefix,(file,col) in profiles.items():
   d=cache[file].sort_values('slice_index' if file.startswith('slice') else 'pair_index')[col].to_numpy(float)
   if len(d)!=(801 if file.startswith('slice') else 800):raise RuntimeError('profile')
   for name,value in metrics(d).items():
    cid=f'RAW-X052::{prefix}_{name}';g='C' if name=='adjacent_gradient_turn_rate' else 'B';R.append({'model_id':m,'model_family':fam[m],'candidate_id':cid,'value':value,'operational_grade':g});M.setdefault(cid,{'candidate_id':cid,'candidate_group_id':'RAW-X052','descriptor_family':'ordered_profile_jump_turn','output_name':f'{prefix}_{name}','unit':'dimensionless','source_population':'ordered 801-slice or 800-overlay-pair verified profile','aggregation_formula':'normalized RMS/q90/max adjacent jump or nonzero adjacent-gradient sign-turn rate','applicable_family':'B|C|F|L|T','direct_or_derived':'direct_statistic_from_verified_SLICE004_profile' if g=='B' else 'derived_profile_turn_statistic_from_verified_SLICE004_profile','source_bank':'PRM122_profile_jump_and_turn_batch','source_value_table':'PRM122_profile_jump_and_turn_values_long.csv','technical_role':'batch_BC_candidate','qualification_status':'full58_raw_table_batch_not_selected','confidence_status':'confirmed_raw_table_lineage','later_evaluation_role':'batch_BC_unselected_block_aware','active_feature':False,'promoted':False,'y_evidence':False,'notes':'PRM122 ordered profile jump/turn batch; no y','operational_grade':g,'literature_anchor':'LIT-X023','anchor_scope':'ordered 2D slice/overlay profile continuity only'})
 V=pd.DataFrame(R);G=pd.DataFrame(M.values()).sort_values('candidate_id');ids=G.candidate_id.tolist()
 if len(ids)!=24 or len(V)!=1392 or not np.isfinite(V.value).all() or (G.operational_grade=='B').sum()!=18 or (G.operational_grade=='C').sum()!=6:raise RuntimeError('candidate')
 W=V.pivot(index='model_id',columns='candidate_id',values='value').reindex(index=models,columns=ids);cov=pd.DataFrame([{'candidate_id':z,'finite_count':58,'missing_count':0,'unique_count':int(W[z].nunique()),'population_std_across_models':float(W[z].std(ddof=0)),'iqr_across_models':float(np.quantile(W[z],.75)-np.quantile(W[z],.25)),'operational_grade':G.set_index('candidate_id').loc[z,'operational_grade'],'technical_status':'batch_BC_unselected'} for z in ids]); old={z:g.set_index('model_id').reindex(models).value.to_numpy(float) for z,g in xreg.groupby('candidate_id')};cross=pd.DataFrame([{'candidate_id':z,'existing_candidate_id':o,**rel(W[z].to_numpy(float),v),'evidence_scope':'full58_x_only','selection_effect':'none'} for z in ids for o,v in old.items()]);internal=pd.DataFrame([{'left_candidate_id':a,'right_candidate_id':b,**rel(W[a].to_numpy(float),W[b].to_numpy(float)),'evidence_scope':'full58_x_only','selection_effect':'none'} for i,a in enumerate(ids) for b in ids[i+1:]]);collision=pd.DataFrame([{'pair_id':p,'candidate_id':z,'absolute_delta':abs(float(W.loc[a,z])-float(W.loc[b,z])),'relative_delta':abs(float(W.loc[a,z])-float(W.loc[b,z]))/max(abs(float(W.loc[a,z])),abs(float(W.loc[b,z])),1e-12),'diagnostic_only':True} for a,b,p in [('T8','T9','T8_T9'),('T5','T6','T5_T6')] for z in ids])
 for s,d in {'candidate_registry':G,'values_long':V,'values_wide':W.reset_index(),'coverage_variation':cov,'vs_XREG_v1_3_redundancy':cross,'internal_redundancy':internal,'collision_diagnostic':collision}.items():d.to_csv(T/f'PRM122_profile_jump_and_turn_{s}.csv',index=False,encoding='utf-8-sig',float_format='%.17g')
 locks=not G[['active_feature','promoted','y_evidence']].any().any() and all(v==0 for v in c['locks'].values());checks=[('P122-01',len(models)==58,'58 models'),('P122-02',len(set(paths))==116,'116 unique frozen sources'),('P122-03',len(ids)==24,'24 candidates'),('P122-04',len(V)==1392 and np.isfinite(V.value).all(),'1392 finite'),('P122-05',len(cross)==7752,'7752 cross'),('P122-06',len(internal)==276,'276 internal'),('P122-07',len(collision)==48,'48 collision'),('P122-08',locks,'locks')];q=pd.DataFrame([{'check_id':i,'status':'PASS' if ok else 'FAIL','detail':d} for i,ok,d in checks]);(F/'reports').mkdir(parents=True,exist_ok=True);q.to_csv(F/'reports'/'PRM122_producer_QA.csv',index=False,encoding='utf-8-sig');out={'status':'PASS' if q.status.eq('PASS').all() else 'FAIL','checks':f"{q.status.eq('PASS').sum()}/{len(q)}",'models':58,'candidates':24,'grade_B':18,'grade_C':6,'values':1392,'y_fit_selection_promotion':'0/0/0/0'};(F/'reports'/'PRM122_batch_summary.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));
 if out['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
