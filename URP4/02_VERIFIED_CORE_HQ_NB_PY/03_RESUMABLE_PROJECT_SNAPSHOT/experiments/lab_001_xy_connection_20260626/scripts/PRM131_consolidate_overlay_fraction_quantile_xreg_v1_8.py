from __future__ import annotations
from collections import defaultdict
from pathlib import Path
import numpy as np,pandas as pd
R=Path(__file__).resolve().parents[3];T=R/'experiments/lab_001_xy_connection_20260626/reports/tables';F=R/'experiments/lab_001_xy_connection_20260626/factories/PRM-131';F.mkdir(parents=True,exist_ok=True)
def main():
 p=pd.read_csv(T/'PRM129_xreg_v1_7_candidate_bank.csv');pv=pd.read_csv(T/'PRM129_xreg_v1_7_values_long.csv');pe=pd.read_csv(T/'PRM129_unified_redundancy_edge_registry.csv');c=pd.read_csv(T/'PRM130_overlay_fraction_quantile_candidate_registry.csv');cv=pd.read_csv(T/'PRM130_overlay_fraction_quantile_values_long.csv');x=pd.read_csv(T/'PRM130_overlay_fraction_quantile_vs_XREG_v1_7_redundancy.csv');i=pd.read_csv(T/'PRM130_overlay_fraction_quantile_internal_redundancy.csv');ids=sorted(c.candidate_id);pairs=[(r.candidate_id,r.existing_candidate_id) for r in x[x.relation.eq('high_redundancy')].itertuples(index=False)]+[(r.left_candidate_id,r.right_candidate_id) for r in i[i.relation.eq('high_redundancy')].itertuples(index=False)];add=pd.DataFrame([dict(edge_id=f'U131-EDGE-{n:03d}',left_candidate_id=a,right_candidate_id=b,relation='high_redundancy',edge_source='PRM130_xonly',metric_note='no representative',selection_rule=False) for n,(a,b) in enumerate(pairs,start=97)]);e=pd.concat([pe,add.reindex(columns=pe.columns)],ignore_index=True);a=defaultdict(set)
 for q in e.itertuples(index=False):a[q.left_candidate_id].add(q.right_candidate_id);a[q.right_candidate_id].add(q.left_candidate_id)
 mem={};seen=set()
 for root in sorted(p.candidate_id.tolist()+ids):
  if root in seen:continue
  s=[root];seen.add(root);g=[]
  while s:
   z=s.pop();g.append(z)
   for h in a[z]:
    if h not in seen:seen.add(h);s.append(h)
  for z in g:mem[z]=g
 old=p.set_index('candidate_id').unified_block_id.to_dict();bid={};new=[]
 for g in {tuple(sorted(v)) for v in mem.values()}:
  h={old[z] for z in g if z in old}
  if not any(z in ids for z in g) and len(h)==1:
   for z in g:bid[z]=next(iter(h))
  else:new.append(g)
 for n,g in enumerate(sorted(new),1):
  for z in g:bid[z]=f'U131-BLK-{n:03d}'
 b=p.copy();b['predecessor_unified_block_id']=b.unified_block_id;b['bank_version']='XREG-v1.8-TECHNICAL';b['unified_block_id']=b.candidate_id.map(bid);b['unified_block_member_count']=b.candidate_id.map(lambda z:len(mem[z]));b['unified_edge_degree']=b.candidate_id.map(lambda z:len(a[z]));cols=b.columns.tolist();src=c.set_index('candidate_id');rows=[]
 for z in ids:
  s=src.loc[z];q=cv[cv.candidate_id.eq(z)].value.to_numpy(float);rows.append(dict(bank_version='XREG-v1.8-TECHNICAL',candidate_id=z,candidate_group_id=s.candidate_group_id,descriptor_family=s.descriptor_family,output_name=s.output_name,unit=s.unit,source_population=s.source_population,aggregation_formula=s.aggregation_formula,applicable_family=s.applicable_family,direct_or_derived=s.direct_or_derived,source_bank='PRM130_overlay_fraction_quantile_batch',source_value_table='PRM130_overlay_fraction_quantile_values_long.csv',technical_role='batch_BC_candidate',qualification_status='full58_raw_table_batch_not_selected',confidence_status='confirmed_raw_table_lineage',later_evaluation_role='batch_BC_unselected_block_aware',active_feature=False,promoted=False,y_evidence=False,notes='PRM130 no y',model_count=58,finite_count=len(q),unique_count=len(np.unique(q)),unified_block_id=bid[z],unified_block_member_count=len(mem[z]),unified_edge_degree=len(a[z]),operational_grade=s.operational_grade,literature_anchor=s.literature_anchor,anchor_scope=s.anchor_scope,predecessor_unified_block_id=pd.NA))
 b=pd.concat([b,pd.DataFrame(rows).reindex(columns=cols)],ignore_index=True);v=pd.concat([pv.assign(bank_version='XREG-v1.8-TECHNICAL'),cv.assign(bank_version='XREG-v1.8-TECHNICAL',finite=True,source_bank='PRM130_overlay_fraction_quantile_batch')[['bank_version','model_id','model_family','candidate_id','value','finite','source_bank']]],ignore_index=True);w=v.pivot(index=['model_id','model_family'],columns='candidate_id',values='value').reindex(columns=b.candidate_id.tolist()).reset_index();b.to_csv(T/'PRM131_xreg_v1_8_candidate_bank.csv',index=False,encoding='utf-8-sig');v.to_csv(T/'PRM131_xreg_v1_8_values_long.csv',index=False,encoding='utf-8-sig');w.to_csv(T/'PRM131_xreg_v1_8_values_wide.csv',index=False,encoding='utf-8-sig');e.to_csv(T/'PRM131_unified_redundancy_edge_registry.csv',index=False,encoding='utf-8-sig');blocks=b[['candidate_id','unified_block_id','unified_block_member_count','unified_edge_degree']].copy();blocks['representative_selected']=False;blocks['block_policy']=np.where(blocks.unified_block_member_count.eq(1),'standalone technical candidate; no selection','x-only graph block; no representative');blocks.to_csv(T/'PRM131_unified_redundancy_block_registry.csv',index=False,encoding='utf-8-sig');pol=blocks[blocks.candidate_id.isin(ids)].copy();pol['selection_status']='not_selected';pol.to_csv(T/'PRM131_overlay_fraction_quantile_cohort_block_policy.csv',index=False,encoding='utf-8-sig');oldv=v[v.candidate_id.isin(p.candidate_id)].sort_values(['model_id','candidate_id']).reset_index(drop=True);newv=v[v.candidate_id.isin(ids)].sort_values(['model_id','candidate_id']).reset_index(drop=True);ok=np.allclose(oldv.value,pv.sort_values(['model_id','candidate_id']).value,rtol=1e-12,atol=1e-12,equal_nan=True) and np.allclose(newv.value,cv.sort_values(['model_id','candidate_id']).value,rtol=1e-12,atol=1e-12);qa=pd.DataFrame([dict(check_id='I131-01',status='PASS' if len(b)==416 and len(v)==24128 and v.value.notna().sum()==24126 and len(e)==102 and ok and not b.active_feature.any() and not b.promoted.any() else 'FAIL',detail=f'blocks={b.unified_block_id.nunique()},replay={ok}')]);qa.to_csv(F/'PRM131_independent_QA.csv',index=False,encoding='utf-8-sig');print(qa.to_dict('records'))
 if not qa.status.eq('PASS').all():raise SystemExit(1)
if __name__=='__main__':main()
