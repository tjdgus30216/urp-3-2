from __future__ import annotations
import json,hashlib
from pathlib import Path
from collections import defaultdict
import pandas as pd,numpy as np
R=Path(__file__).resolve().parents[3];T=R/'experiments/lab_001_xy_connection_20260626/reports/tables';F=R/'experiments/lab_001_xy_connection_20260626/factories/PRM-123';F.mkdir(parents=True,exist_ok=True)
def graph(nodes,pairs):
 a=defaultdict(set)
 for l,r in pairs:a[l].add(r);a[r].add(l)
 seen=set();m={}
 for root in sorted(nodes):
  if root in seen:continue
  s=[root];seen.add(root);g=[]
  while s:
   x=s.pop();g.append(x)
   for y in a[x]:
    if y not in seen:seen.add(y);s.append(y)
  for x in g:m[x]=g
 return m,{x:len(a[x]) for x in nodes}
def main():
 p=pd.read_csv(T/'PRM121_xreg_v1_3_candidate_bank.csv');pv=pd.read_csv(T/'PRM121_xreg_v1_3_values_long.csv');pe=pd.read_csv(T/'PRM121_unified_redundancy_edge_registry.csv');pb=pd.read_csv(T/'PRM121_unified_redundancy_block_registry.csv');c=pd.read_csv(T/'PRM122_profile_jump_and_turn_candidate_registry.csv');cv=pd.read_csv(T/'PRM122_profile_jump_and_turn_values_long.csv');x=pd.read_csv(T/'PRM122_profile_jump_and_turn_vs_XREG_v1_3_redundancy.csv');i=pd.read_csv(T/'PRM122_profile_jump_and_turn_internal_redundancy.csv'); ids=sorted(c.candidate_id);a=x[x.relation.eq('high_redundancy')];b=i[i.relation.eq('high_redundancy')];add=pd.DataFrame([{'edge_id':f'U123-EDGE-{n:03d}','left_candidate_id':l,'right_candidate_id':r,'relation':'high_redundancy','edge_source':'PRM122_xonly','metric_note':'no representative','selection_rule':False} for n,(l,r) in enumerate([(r.candidate_id,r.existing_candidate_id) for r in a.itertuples(index=False)]+[(r.left_candidate_id,r.right_candidate_id) for r in b.itertuples(index=False)],77)])
 mem,deg=graph(p.candidate_id.tolist()+ids,[(r.left_candidate_id,r.right_candidate_id) for r in pe.itertuples(index=False)]+[(r.left_candidate_id,r.right_candidate_id) for r in add.itertuples(index=False)]);old=p.set_index('candidate_id').unified_block_id.to_dict();bid={};chg=[]
 for g in {tuple(v) for v in mem.values()}:
  inh={old[z] for z in g if z in old};new=any(z in ids for z in g);q=next(iter(inh)) if not new and len(inh)==1 else '';chg+=[] if q else [list(g)]
  for z in g:bid[z]=q
 for n,g in enumerate(sorted(chg,key=lambda q:tuple(q)),1):
  for z in g:bid[z]=f'U123-BLK-{n:03d}'
 bank=p.copy();bank['predecessor_unified_block_id']=bank.unified_block_id;bank['bank_version']='XREG-v1.4-TECHNICAL';bank['unified_block_id']=bank.candidate_id.map(bid);bank['unified_block_member_count']=bank.candidate_id.map(lambda z:len(mem[z]));bank['unified_edge_degree']=bank.candidate_id.map(deg);cols=bank.columns.tolist();src=c.set_index('candidate_id');rows=[]
 for z in ids:
  s=src.loc[z];v=cv[cv.candidate_id.eq(z)].value.to_numpy(float);rows.append({'bank_version':'XREG-v1.4-TECHNICAL','candidate_id':z,'candidate_group_id':s.candidate_group_id,'descriptor_family':s.descriptor_family,'output_name':s.output_name,'unit':s.unit,'source_population':s.source_population,'aggregation_formula':s.aggregation_formula,'applicable_family':s.applicable_family,'direct_or_derived':s.direct_or_derived,'source_bank':'PRM122_profile_jump_and_turn_batch','source_value_table':'PRM122_profile_jump_and_turn_values_long.csv','technical_role':'batch_BC_candidate','qualification_status':'full58_raw_table_batch_not_selected','confidence_status':'confirmed_raw_table_lineage','later_evaluation_role':'batch_BC_unselected_block_aware','active_feature':False,'promoted':False,'y_evidence':False,'notes':'PRM122 no y','model_count':58,'finite_count':len(v),'unique_count':len(np.unique(v)),'unified_block_id':bid[z],'unified_block_member_count':len(mem[z]),'unified_edge_degree':deg[z],'operational_grade':s.operational_grade,'literature_anchor':s.literature_anchor,'anchor_scope':s.anchor_scope,'predecessor_unified_block_id':pd.NA})
 bank=pd.concat([bank,pd.DataFrame(rows).reindex(columns=cols)],ignore_index=True);vals=pd.concat([pv.assign(bank_version='XREG-v1.4-TECHNICAL'),cv.assign(bank_version='XREG-v1.4-TECHNICAL',finite=True,source_bank='PRM122_profile_jump_and_turn_batch')[['bank_version','model_id','model_family','candidate_id','value','finite','source_bank']]],ignore_index=True);wide=vals.pivot(index=['model_id','model_family'],columns='candidate_id',values='value').reindex(columns=bank.candidate_id.tolist()).reset_index();edges=pd.concat([pe,add.reindex(columns=pe.columns)],ignore_index=True)
 bank.to_csv(T/'PRM123_xreg_v1_4_candidate_bank.csv',index=False,encoding='utf-8-sig');vals.to_csv(T/'PRM123_xreg_v1_4_values_long.csv',index=False,encoding='utf-8-sig');wide.to_csv(T/'PRM123_xreg_v1_4_values_wide.csv',index=False,encoding='utf-8-sig');edges.to_csv(T/'PRM123_unified_redundancy_edge_registry.csv',index=False,encoding='utf-8-sig');q=pd.DataFrame([{'check_id':'P123-01','status':'PASS' if len(bank)==347 and len(vals)==20126 and vals.value.notna().sum()==20124 and len(edges)==86 and len(set(bid.values()))==278 and sum(bid[z]!=v for z,v in old.items())==2 else 'FAIL','detail':'scope'}]);q.to_csv(F/'PRM123_producer_QA.csv',index=False);print(q.to_dict('records')); 
 if not q.status.eq('PASS').all():raise SystemExit(1)
if __name__=='__main__':main()
