from __future__ import annotations
from collections import defaultdict
from pathlib import Path
import json
import numpy as np,pandas as pd
from scipy.stats import pearsonr,spearmanr,skew,kurtosis
R=Path(__file__).resolve().parents[3];T=R/'experiments/lab_001_xy_connection_20260626/reports/tables';F=R/'experiments/lab_001_xy_connection_20260626/factories';
def rel(a,b):
 if len(np.unique(a))<3 or len(np.unique(b))<3:return 'degenerate'
 p=float(pearsonr(a,b).statistic);s=float(spearmanr(a,b).statistic);return 'high_redundancy' if abs(p)>=.98 and abs(s)>=.98 else 'distinct'
def stats(a):
 return {'skewness':float(skew(a)),'excess_kurtosis':float(kurtosis(a)),'coefficient_variation':float(np.std(a)/max(abs(np.mean(a)),1e-12)),'q95_q05_span':float(np.quantile(a,.95)-np.quantile(a,.05)),'normalized_total_variation':float(np.mean(np.abs(np.diff(a)))/max(abs(np.mean(a)),1e-12)),'zero_fraction':float(np.mean(a==0))}
def comp(nodes,edges):
 a=defaultdict(set)
 for l,r in edges:a[l].add(r);a[r].add(l)
 seen=set();m={}
 for root in sorted(nodes):
  if root in seen:continue
  s=[root];seen.add(root);g=[]
  while s:
   z=s.pop();g.append(z)
   for q in a[z]:
    if q not in seen:seen.add(q);s.append(q)
  for z in g:m[z]=g
 return m,a
def wave(prm,group,kind,bank,values,edges,version):
 models=sorted(values.model_id.unique());fam=values[['model_id','model_family']].drop_duplicates().set_index('model_id').model_family.to_dict();rows=[];meta={}
 for m in models:
  sp=R/f'.tmp/t4rs4/P1000_S801/{m}/tables';sl=pd.read_csv(sp/'slice_pixel_readback.csv').sort_values('slice_index');ov=pd.read_csv(sp/'overlay_pixel_readback.csv').sort_values('pair_index')
  if kind=='slice': profiles={'slice_material_fraction':sl.material_pixel_count.to_numpy(float)/1e6,'slice_component_raw_count':sl.component_count_raw.to_numpy(float)}
  elif kind=='overlay_count': profiles={'overlay_component_raw_count':ov.component_count_raw.to_numpy(float),'overlay_component_kept_count':ov.component_count_min2.to_numpy(float)}
  elif kind=='raw_component_area':
   cp=pd.read_csv(sp/'overlay_component_population.csv');profiles={'all_component_area':cp.area_mm2.to_numpy(float),'kept_component_area':cp.loc[cp.kept_by_min2.astype(bool),'area_mm2'].to_numpy(float)}
  elif kind=='slice_density':
   px=np.maximum(sl.material_pixel_count.to_numpy(float),1.);profiles={'slice_raw_component_density':1e6*sl.component_count_raw.to_numpy(float)/px,'slice_kept_component_density':1e6*sl.component_count_min2.to_numpy(float)/px}
  elif kind=='pair_area':
   cp=pd.read_csv(sp/'overlay_component_population.csv');grp=cp.groupby('pair_index').area_mm2;profiles={'pair_component_area_median':grp.median().to_numpy(float),'pair_component_area_q90':grp.quantile(.9).to_numpy(float),'pair_component_area_max':grp.max().to_numpy(float)}
  elif kind=='slice_piece_area':
   px=sl.material_area_mm2.to_numpy(float);profiles={'slice_raw_mean_piece_area':px/np.maximum(sl.component_count_raw.to_numpy(float),1.),'slice_kept_mean_piece_area':px/np.maximum(sl.component_count_min2.to_numpy(float),1.)}
  elif kind=='phase_balance_shape':
   u=np.maximum(ov.union_pixel_count.to_numpy(float),1.);red=ov.red_pixel_count.to_numpy(float);blue=ov.blue_pixel_count.to_numpy(float);purple=ov.purple_pixel_count.to_numpy(float);profiles={'red_blue_absolute_balance':np.abs(red-blue)/np.maximum(red+blue,1.),'red_blue_signed_balance':(red-blue)/np.maximum(red+blue,1.),'purple_share':purple/u}
  elif kind=='pair_inequality_shape':
   cp=pd.read_csv(sp/'overlay_component_population.csv');profiles={'pair_area_gini':[],'pair_effective_count':[],'pair_top1_share':[]}
   for _,q in cp.groupby('pair_index'):
    a=np.sort(q.area_mm2.to_numpy(float));n=len(a);profiles['pair_area_gini'].append(float((2*np.arange(1,n+1)-n-1).dot(a)/(n*a.sum())) if a.sum()>0 else 0.);profiles['pair_effective_count'].append(float(a.sum()**2/max((a*a).sum(),1e-12)));profiles['pair_top1_share'].append(float(a[-1]/max(a.sum(),1e-12)))
   profiles={k:np.asarray(v,float) for k,v in profiles.items()}
  else:
   u=np.maximum(ov.union_pixel_count.to_numpy(float),1.);profiles={'red_fraction':ov.red_pixel_count.to_numpy(float)/u,'blue_fraction':ov.blue_pixel_count.to_numpy(float)/u,'purple_fraction':ov.purple_pixel_count.to_numpy(float)/u}
  for name,a in profiles.items():
   ss=stats(a)
   if kind=='phase': ss={'mean_abs_adjacent_change':float(np.mean(abs(np.diff(a)))),'rms_adjacent_change':float(np.sqrt(np.mean(np.diff(a)**2))),'q95_q05_span':ss['q95_q05_span'],'coefficient_variation':ss['coefficient_variation']}
   for k,z in ss.items():
    cid=f'{group}::{name}_{k}';rows.append(dict(model_id=m,model_family=fam[m],candidate_id=cid,value=z,operational_grade='B' if k in ['q95_q05_span','coefficient_variation'] else 'C'));meta.setdefault(cid,dict(candidate_id=cid,candidate_group_id=group,descriptor_family=f'{kind}_profile_shape',output_name=cid.split('::')[1],unit='dimensionless' if 'area' not in name else 'mm2',source_population='verified SLICE-004 overlay component table' if kind in ['raw_component_area','pair_area'] else 'verified SLICE-004 pixel readback profile',aggregation_formula='profile shape statistic from frozen raw table',applicable_family='B|C|F|L|T',direct_or_derived='derived_statistic_from_verified_SLICE004_profile',source_bank=f'PRM{prm}_batch_autopilot',source_value_table=f'PRM{prm}_values_long.csv',technical_role='batch_BC_candidate',qualification_status='full58_raw_table_batch_not_selected',confidence_status='confirmed_raw_table_lineage',later_evaluation_role='batch_BC_unselected_block_aware',active_feature=False,promoted=False,y_evidence=False,notes=f'PRM{prm} no y',operational_grade='B' if k in ['q95_q05_span','coefficient_variation'] else 'C',literature_anchor='LIT-X035',anchor_scope='2D profile summary only'))
 v=pd.DataFrame(rows);g=pd.DataFrame(meta.values()).sort_values('candidate_id');ids=g.candidate_id.tolist();w=v.pivot(index='model_id',columns='candidate_id',values='value').reindex(index=models,columns=ids);old={z:q.set_index('model_id').reindex(models).value.to_numpy(float) for z,q in values.groupby('candidate_id')};cross=[]
 for z in ids:
  for o,a in old.items():
   r=rel(w[z].to_numpy(float),a)
   if r=='high_redundancy':cross.append((z,o))
 inter=[]
 for n,a in enumerate(ids):
  for b in ids[n+1:]:
   if rel(w[a].to_numpy(float),w[b].to_numpy(float))=='high_redundancy':inter.append((a,b))
 for n,d in {'candidate_registry':g,'values_long':v,'values_wide':w.reset_index(),'cross_high_edges':pd.DataFrame(cross,columns=['candidate_id','existing_candidate_id']),'internal_high_edges':pd.DataFrame(inter,columns=['left_candidate_id','right_candidate_id'])}.items():d.to_csv(T/f'PRM{prm}_{n}.csv',index=False,encoding='utf-8-sig')
 add=pd.DataFrame([dict(edge_id=f'U{prm+1}-EDGE-{len(edges)+n+1:03d}',left_candidate_id=a,right_candidate_id=b,relation='high_redundancy',edge_source=f'PRM{prm}_xonly',metric_note='no representative',selection_rule=False) for n,(a,b) in enumerate(cross+inter)]);ne=pd.concat([edges,add.reindex(columns=edges.columns)],ignore_index=True);members,adj=comp(bank.candidate_id.tolist()+ids,[(r.left_candidate_id,r.right_candidate_id) for r in ne.itertuples(index=False)]);oldbid=bank.set_index('candidate_id').unified_block_id.to_dict();bid={};new=[]
 for gg in {tuple(sorted(x)) for x in members.values()}:
  h={oldbid[z] for z in gg if z in oldbid}
  if not any(z in ids for z in gg) and len(h)==1:
   for z in gg:bid[z]=next(iter(h))
  else:new.append(gg)
 for n,gg in enumerate(sorted(new),1):
  for z in gg:bid[z]=f'U{prm+1}-BLK-{n:03d}'
 nb=bank.copy();nb['predecessor_unified_block_id']=nb.unified_block_id;nb['bank_version']=version;nb['unified_block_id']=nb.candidate_id.map(bid);nb['unified_block_member_count']=nb.candidate_id.map(lambda z:len(members[z]));nb['unified_edge_degree']=nb.candidate_id.map(lambda z:len(adj[z]));cols=nb.columns.tolist();src=g.set_index('candidate_id');adds=[]
 for z in ids:
  s=src.loc[z];adds.append({**s.to_dict(),'candidate_id':z,'bank_version':version,'model_count':58,'finite_count':58,'unique_count':len(np.unique(w[z])),'unified_block_id':bid[z],'unified_block_member_count':len(members[z]),'unified_edge_degree':len(adj[z]),'predecessor_unified_block_id':pd.NA})
 nb=pd.concat([nb,pd.DataFrame(adds).reindex(columns=cols)],ignore_index=True);nv=pd.concat([values.assign(bank_version=version),v.assign(bank_version=version,finite=True,source_bank=f'PRM{prm}_batch_autopilot')[['bank_version','model_id','model_family','candidate_id','value','finite','source_bank']]],ignore_index=True);wide=nv.pivot(index=['model_id','model_family'],columns='candidate_id',values='value').reindex(columns=nb.candidate_id.tolist()).reset_index();cp=prm+1
 key=version.split('-')[1].replace('.', '_');nb.to_csv(T/f'PRM{cp}_xreg_{key}_candidate_bank.csv',index=False,encoding='utf-8-sig');nv.to_csv(T/f'PRM{cp}_xreg_{key}_values_long.csv',index=False,encoding='utf-8-sig');ne.to_csv(T/f'PRM{cp}_unified_redundancy_edge_registry.csv',index=False,encoding='utf-8-sig');blocks=nb[['candidate_id','unified_block_id','unified_block_member_count','unified_edge_degree']].copy();blocks['representative_selected']=False;blocks['block_policy']=np.where(blocks.unified_block_member_count.eq(1),'standalone technical candidate; no selection','x-only graph block; no representative');blocks.to_csv(T/f'PRM{cp}_unified_redundancy_block_registry.csv',index=False,encoding='utf-8-sig');qa={'prm_batch':prm,'candidates':len(g),'finite':int(np.isfinite(v.value).sum()),'cross_high':len(cross),'internal_high':len(inter),'prm_consolidation':cp,'bank_candidates':len(nb),'bank_values':len(nv),'bank_blocks':nb.unified_block_id.nunique(),'bank_edges':len(ne),'no_y':bool(nb.y_evidence.astype(str).str.lower().eq('false').all())};(F/f'PRM-{prm:03d}').mkdir(parents=True,exist_ok=True);(F/f'PRM-{prm:03d}'/'autopilot_QA.json').write_text(json.dumps(qa,indent=2),encoding='utf8');return nb,nv,ne,qa
def main():
 b=pd.read_csv(T/'PRM131_xreg_v1_8_candidate_bank.csv');v=pd.read_csv(T/'PRM131_xreg_v1_8_values_long.csv');e=pd.read_csv(T/'PRM131_unified_redundancy_edge_registry.csv');out=[]
 for prm,grp,kind,ver in [(132,'RAW-X057','slice','XREG-v1.9-TECHNICAL'),(134,'RAW-X058','overlay_count','XREG-v2.0-TECHNICAL'),(136,'RAW-X059','phase','XREG-v2.1-TECHNICAL')]: b,v,e,q=wave(prm,grp,kind,b,v,e,ver);out.append(q)
 (F/'PRM-132'/'PRM132_137_AUTOPILOT_SUMMARY.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
