from __future__ import annotations
from collections import defaultdict
from pathlib import Path
import numpy as np,pandas as pd
R=Path(__file__).resolve().parents[3];T=R/'experiments/lab_001_xy_connection_20260626/reports/tables';F=R/'experiments/lab_001_xy_connection_20260626/factories/PRM-129';F.mkdir(parents=True,exist_ok=True)
def graph(nodes,pairs):
 a=defaultdict(set)
 for l,r in pairs:a[l].add(r);a[r].add(l)
 seen=set();m={}
 for root in sorted(nodes):
  if root in seen:continue
  s=[root];seen.add(root);g=[]
  while s:
   z=s.pop();g.append(z)
   for q in a[z]:
    if q not in seen:seen.add(q);s.append(q)
  for z in g:m[z]=g
 return m,{z:len(a[z]) for z in nodes}
def main():
 p=pd.read_csv(T/'PRM127_xreg_v1_6_candidate_bank.csv');pv=pd.read_csv(T/'PRM127_xreg_v1_6_values_long.csv');pe=pd.read_csv(T/'PRM127_unified_redundancy_edge_registry.csv');c=pd.read_csv(T/'PRM128_overlay_phase_cross_correlation_candidate_registry.csv');cv=pd.read_csv(T/'PRM128_overlay_phase_cross_correlation_values_long.csv');i=pd.read_csv(T/'PRM128_overlay_phase_cross_correlation_internal_redundancy.csv');ids=sorted(c.candidate_id);hi=i[i.relation.eq('high_redundancy')];add=pd.DataFrame([dict(edge_id=f'U129-EDGE-{n:03d}',left_candidate_id=r.left_candidate_id,right_candidate_id=r.right_candidate_id,relation='high_redundancy',edge_source='PRM128_xonly',metric_note='no representative',selection_rule=False) for n,r in enumerate(hi.itertuples(index=False),start=96)]);e=pd.concat([pe,add.reindex(columns=pe.columns)],ignore_index=True);m,d=graph(p.candidate_id.tolist()+ids,[(r.left_candidate_id,r.right_candidate_id) for r in e.itertuples(index=False)]);old=p.set_index('candidate_id').unified_block_id.to_dict();bid={};groups=[]
 for g in {tuple(sorted(x)) for x in m.values()}:
  h={old[z] for z in g if z in old}
  if not any(z in ids for z in g) and len(h)==1:
   for z in g:bid[z]=next(iter(h))
  else:groups.append(g)
 for n,g in enumerate(sorted(groups),1):
  for z in g:bid[z]=f'U129-BLK-{n:03d}'
 b=p.copy();b['predecessor_unified_block_id']=b.unified_block_id;b['bank_version']='XREG-v1.7-TECHNICAL';b['unified_block_id']=b.candidate_id.map(bid);b['unified_block_member_count']=b.candidate_id.map(lambda z:len(m[z]));b['unified_edge_degree']=b.candidate_id.map(d);cols=b.columns.tolist();src=c.set_index('candidate_id');rows=[]
 for z in ids:
  s=src.loc[z];a=cv[cv.candidate_id.eq(z)].value.to_numpy(float);rows.append(dict(bank_version='XREG-v1.7-TECHNICAL',candidate_id=z,candidate_group_id=s.candidate_group_id,descriptor_family=s.descriptor_family,output_name=s.output_name,unit=s.unit,source_population=s.source_population,aggregation_formula=s.aggregation_formula,applicable_family=s.applicable_family,direct_or_derived=s.direct_or_derived,source_bank='PRM128_overlay_phase_cross_correlation_batch',source_value_table='PRM128_overlay_phase_cross_correlation_values_long.csv',technical_role='batch_BC_candidate',qualification_status='full58_raw_table_batch_not_selected',confidence_status='confirmed_raw_table_lineage',later_evaluation_role='batch_BC_unselected_block_aware',active_feature=False,promoted=False,y_evidence=False,notes='PRM128 no y',model_count=58,finite_count=len(a),unique_count=len(np.unique(a)),unified_block_id=bid[z],unified_block_member_count=len(m[z]),unified_edge_degree=d[z],operational_grade=s.operational_grade,literature_anchor=s.literature_anchor,anchor_scope=s.anchor_scope,predecessor_unified_block_id=pd.NA))
 b=pd.concat([b,pd.DataFrame(rows).reindex(columns=cols)],ignore_index=True);v=pd.concat([pv.assign(bank_version='XREG-v1.7-TECHNICAL'),cv.assign(bank_version='XREG-v1.7-TECHNICAL',finite=True,source_bank='PRM128_overlay_phase_cross_correlation_batch')[['bank_version','model_id','model_family','candidate_id','value','finite','source_bank']]],ignore_index=True);w=v.pivot(index=['model_id','model_family'],columns='candidate_id',values='value').reindex(columns=b.candidate_id.tolist()).reset_index();
 b.to_csv(T/'PRM129_xreg_v1_7_candidate_bank.csv',index=False,encoding='utf-8-sig');v.to_csv(T/'PRM129_xreg_v1_7_values_long.csv',index=False,encoding='utf-8-sig');w.to_csv(T/'PRM129_xreg_v1_7_values_wide.csv',index=False,encoding='utf-8-sig');e.to_csv(T/'PRM129_unified_redundancy_edge_registry.csv',index=False,encoding='utf-8-sig');q=pd.DataFrame([dict(check_id='P129-01',status='PASS' if len(b)==401 and len(v)==23258 and v.value.notna().sum()==23256 and len(e)==96 and len(set(bid.values()))==322 else 'FAIL',detail='scope')]);q.to_csv(F/'PRM129_producer_QA.csv',index=False,encoding='utf-8-sig');print(q.to_dict('records'))
 if not q.status.eq('PASS').all():raise SystemExit(1)
if __name__=='__main__':main()
