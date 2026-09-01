from __future__ import annotations
from collections import defaultdict
from pathlib import Path
import numpy as np,pandas as pd
R=Path(__file__).resolve().parents[3];T=R/'experiments/lab_001_xy_connection_20260626/reports/tables';F=R/'experiments/lab_001_xy_connection_20260626/factories/PRM-127';F.mkdir(parents=True,exist_ok=True)
def graph(nodes,pairs):
 a=defaultdict(set)
 for l,r in pairs:a[l].add(r);a[r].add(l)
 seen=set();mem={}
 for root in sorted(nodes):
  if root in seen:continue
  stack=[root];seen.add(root);group=[]
  while stack:
   z=stack.pop();group.append(z)
   for n in a[z]:
    if n not in seen:seen.add(n);stack.append(n)
  for z in group:mem[z]=group
 return mem,{z:len(a[z]) for z in nodes}
def main():
 p=pd.read_csv(T/'PRM125_xreg_v1_5_candidate_bank.csv');pv=pd.read_csv(T/'PRM125_xreg_v1_5_values_long.csv');pe=pd.read_csv(T/'PRM125_unified_redundancy_edge_registry.csv');c=pd.read_csv(T/'PRM126_overlay_component_density_candidate_registry.csv');cv=pd.read_csv(T/'PRM126_overlay_component_density_values_long.csv');i=pd.read_csv(T/'PRM126_overlay_component_density_internal_redundancy.csv');ids=sorted(c.candidate_id);hi=i[i.relation.eq('high_redundancy')];add=pd.DataFrame([dict(edge_id=f'U127-EDGE-{n:03d}',left_candidate_id=r.left_candidate_id,right_candidate_id=r.right_candidate_id,relation='high_redundancy',edge_source='PRM126_xonly',metric_note='no representative',selection_rule=False) for n,r in enumerate(hi.itertuples(index=False),start=89)]);edges=pd.concat([pe,add.reindex(columns=pe.columns)],ignore_index=True);mem,deg=graph(p.candidate_id.tolist()+ids,[(r.left_candidate_id,r.right_candidate_id) for r in edges.itertuples(index=False)]);old=p.set_index('candidate_id').unified_block_id.to_dict();bid={};groups=[]
 for g in {tuple(sorted(x)) for x in mem.values()}:
  inherited={old[z] for z in g if z in old}
  if not any(z in ids for z in g) and len(inherited)==1:
   for z in g:bid[z]=next(iter(inherited))
  else:groups.append(g)
 for n,g in enumerate(sorted(groups),1):
  for z in g:bid[z]=f'U127-BLK-{n:03d}'
 b=p.copy();b['predecessor_unified_block_id']=b.unified_block_id;b['bank_version']='XREG-v1.6-TECHNICAL';b['unified_block_id']=b.candidate_id.map(bid);b['unified_block_member_count']=b.candidate_id.map(lambda z:len(mem[z]));b['unified_edge_degree']=b.candidate_id.map(deg);cols=b.columns.tolist();src=c.set_index('candidate_id');rows=[]
 for z in ids:
  s=src.loc[z];v=cv[cv.candidate_id.eq(z)].value.to_numpy(float);rows.append(dict(bank_version='XREG-v1.6-TECHNICAL',candidate_id=z,candidate_group_id=s.candidate_group_id,descriptor_family=s.descriptor_family,output_name=s.output_name,unit=s.unit,source_population=s.source_population,aggregation_formula=s.aggregation_formula,applicable_family=s.applicable_family,direct_or_derived=s.direct_or_derived,source_bank='PRM126_overlay_component_density_batch',source_value_table='PRM126_overlay_component_density_values_long.csv',technical_role='batch_BC_candidate',qualification_status='full58_raw_table_batch_not_selected',confidence_status='confirmed_raw_table_lineage',later_evaluation_role='batch_BC_unselected_block_aware',active_feature=False,promoted=False,y_evidence=False,notes='PRM126 no y',model_count=58,finite_count=len(v),unique_count=len(np.unique(v)),unified_block_id=bid[z],unified_block_member_count=len(mem[z]),unified_edge_degree=deg[z],operational_grade=s.operational_grade,literature_anchor=s.literature_anchor,anchor_scope=s.anchor_scope,predecessor_unified_block_id=pd.NA))
 b=pd.concat([b,pd.DataFrame(rows).reindex(columns=cols)],ignore_index=True);v=pd.concat([pv.assign(bank_version='XREG-v1.6-TECHNICAL'),cv.assign(bank_version='XREG-v1.6-TECHNICAL',finite=True,source_bank='PRM126_overlay_component_density_batch')[['bank_version','model_id','model_family','candidate_id','value','finite','source_bank']]],ignore_index=True);w=v.pivot(index=['model_id','model_family'],columns='candidate_id',values='value').reindex(columns=b.candidate_id.tolist()).reset_index();
 for n,d in {'candidate_bank':b,'values_long':v,'values_wide':w,'unified_redundancy_edge_registry':edges}.items():d.to_csv(T/f'PRM127_xreg_v1_6_{n}.csv' if n in ['candidate_bank','values_long','values_wide'] else T/'PRM127_unified_redundancy_edge_registry.csv',index=False,encoding='utf-8-sig')
 qa=pd.DataFrame([dict(check_id='P127-01',status='PASS' if len(b)==389 and len(v)==22562 and v.value.notna().sum()==22560 and len(edges)==95 else 'FAIL',detail=f'blocks={len(set(bid.values()))}')]);qa.to_csv(F/'PRM127_producer_QA.csv',index=False,encoding='utf-8-sig');print(qa.to_dict('records'))
 if not qa.status.eq('PASS').all():raise SystemExit(1)
if __name__=='__main__':main()
