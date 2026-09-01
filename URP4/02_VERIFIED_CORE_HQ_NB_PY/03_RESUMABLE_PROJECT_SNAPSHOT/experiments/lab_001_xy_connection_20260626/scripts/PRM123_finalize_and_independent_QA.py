from __future__ import annotations
from pathlib import Path
from collections import defaultdict
import numpy as np,pandas as pd,json
R=Path(__file__).resolve().parents[3];T=R/'experiments/lab_001_xy_connection_20260626/reports/tables';F=R/'experiments/lab_001_xy_connection_20260626/factories/PRM-123';F.mkdir(parents=True,exist_ok=True)
def comp(nodes,edges):
 a=defaultdict(set)
 for l,r in edges:a[l].add(r);a[r].add(l)
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
 prior=pd.read_csv(T/'PRM121_xreg_v1_3_candidate_bank.csv');pv=pd.read_csv(T/'PRM121_xreg_v1_3_values_long.csv');co=pd.read_csv(T/'PRM122_profile_jump_and_turn_candidate_registry.csv');cv=pd.read_csv(T/'PRM122_profile_jump_and_turn_values_long.csv');bank=pd.read_csv(T/'PRM123_xreg_v1_4_candidate_bank.csv');vals=pd.read_csv(T/'PRM123_xreg_v1_4_values_long.csv');edges=pd.read_csv(T/'PRM123_unified_redundancy_edge_registry.csv');mem,deg=comp(bank.candidate_id.tolist(),[(r.left_candidate_id,r.right_candidate_id) for r in edges.itertuples(index=False)]);bid=bank.set_index('candidate_id').unified_block_id.to_dict();blocks=bank[['candidate_id','candidate_group_id','descriptor_family','source_bank','technical_role','later_evaluation_role','unified_block_id','unified_block_member_count','unified_edge_degree']].copy();blocks['representative_selected']=False;blocks['block_policy']=blocks.unified_block_member_count.map(lambda n:'standalone technical candidate; no selection' if n==1 else 'x-only graph block; no representative');blocks.to_csv(T/'PRM123_unified_redundancy_block_registry.csv',index=False,encoding='utf-8-sig');policy=blocks[blocks.candidate_id.isin(co.candidate_id)][['candidate_id','unified_block_id','unified_block_member_count']].copy();policy['selection_status']='not_selected';policy.to_csv(T/'PRM123_profile_jump_turn_cohort_block_policy.csv',index=False,encoding='utf-8-sig');old=vals[vals.candidate_id.isin(prior.candidate_id)].sort_values(['model_id','candidate_id']).reset_index(drop=True);oref=pv.sort_values(['model_id','candidate_id']).reset_index(drop=True);new=vals[vals.candidate_id.isin(co.candidate_id)].sort_values(['model_id','candidate_id']).reset_index(drop=True);nref=cv.sort_values(['model_id','candidate_id']).reset_index(drop=True);oldok=len(old)==len(oref) and np.allclose(old.value,oref.value,rtol=1e-12,atol=1e-12,equal_nan=True);newok=len(new)==len(nref) and np.allclose(new.value,nref.value,rtol=1e-12,atol=1e-12);closed=all(bid[r.left_candidate_id]==bid[r.right_candidate_id] for r in edges.itertuples(index=False));locks=not bank.active_feature.any() and not bank.promoted.any() and bank.y_evidence.astype(str).str.lower().eq('false').all();checks=[('I123-01',len(bank)==347 and bank.candidate_id.nunique()==347,'347 candidates'),('I123-02',len(vals)==20126 and vals.value.notna().sum()==20124,'20126 values'),('I123-03',oldok,'prior replay'),('I123-04',newok,'cohort replay'),('I123-05',len(edges)==86 and closed,'86 closed edges'),('I123-06',len(blocks)==347 and blocks.unified_block_id.nunique()==278,'278 blocks'),('I123-07',len(policy)==24 and policy.selection_status.eq('not_selected').all(),'policy'),('I123-08',locks,'no y/selection/promotion')];q=pd.DataFrame([{'check_id':i,'status':'PASS' if ok else 'FAIL','detail':d} for i,ok,d in checks]);q.to_csv(F/'PRM123_independent_QA.csv',index=False,encoding='utf-8-sig');out={'status':'PASS' if q.status.eq('PASS').all() else 'FAIL','checks':f"{q.status.eq('PASS').sum()}/{len(q)}",'predecessor_replay':bool(oldok),'cohort_replay':bool(newok),'performance_y_read':0};(F/'PRM123_independent_QA_summary.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));
 if out['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
