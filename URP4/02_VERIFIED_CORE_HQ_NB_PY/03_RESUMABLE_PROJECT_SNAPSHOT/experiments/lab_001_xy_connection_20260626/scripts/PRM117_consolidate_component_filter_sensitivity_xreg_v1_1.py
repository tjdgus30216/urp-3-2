from __future__ import annotations
import hashlib,json
from collections import defaultdict
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[3];LAB=ROOT/'experiments'/'lab_001_xy_connection_20260626';TABLES=LAB/'reports'/'tables';FACTORY=LAB/'factories'/'PRM-117';CONTRACT=FACTORY/'contracts'/'PRM-117_XREG_V1_1_COMPONENT_FILTER_SENSITIVITY_CONSOLIDATION_CONTRACT_20260723.json'
def sha256(p):
 d=hashlib.sha256()
 with p.open('rb') as h:
  for c in iter(lambda:h.read(1048576),b''):d.update(c)
 return d.hexdigest()
def components(nodes,pairs):
 a=defaultdict(set)
 for l,r in pairs:a[l].add(r);a[r].add(l)
 seen=set();gmap={}
 for root in sorted(nodes):
  if root in seen:continue
  s=[root];seen.add(root);g=[]
  while s:
   x=s.pop();g.append(x)
   for y in sorted(a[x]):
    if y not in seen:seen.add(y);s.append(y)
  for x in g:gmap[x]=sorted(g)
 return gmap,{x:len(a[x]) for x in nodes}
def main():
 c=json.loads(CONTRACT.read_text(encoding='utf-8'));e=c['expected']
 for x in c['inputs']:
  if sha256(ROOT/x['path'])!=x['sha256']:raise RuntimeError(f"input hash mismatch: {x['path']}")
 prior=pd.read_csv(TABLES/'PRM115_xreg_v1_0_candidate_bank.csv');pval=pd.read_csv(TABLES/'PRM115_xreg_v1_0_values_long.csv');pedges=pd.read_csv(TABLES/'PRM115_unified_redundancy_edge_registry.csv');pblocks=pd.read_csv(TABLES/'PRM115_unified_redundancy_block_registry.csv');co=pd.read_csv(TABLES/'PRM116_component_filter_sensitivity_candidate_registry.csv');cval=pd.read_csv(TABLES/'PRM116_component_filter_sensitivity_values_long.csv');cross=pd.read_csv(TABLES/'PRM116_component_filter_sensitivity_vs_XREG_v1_0_redundancy.csv');ids=sorted(co.candidate_id);oldids=prior.candidate_id.tolist();sel=cross[cross.relation.eq('high_redundancy')].sort_values(['candidate_id','existing_candidate_id'])
 if len(oldids)!=277 or len(ids)!=11 or set(ids)&set(oldids) or len(pval)!=16066 or len(cval)!=638 or not np.isfinite(cval.value).all() or len(pedges)!=60 or len(sel)!=5:raise RuntimeError('scope mismatch')
 add=pd.DataFrame([{'edge_id':f'U117-EDGE-{n:03d}','left_candidate_id':r.candidate_id,'right_candidate_id':r.existing_candidate_id,'relation':r.relation,'edge_source':'PRM116_component_filter_sensitivity_crossbank_full58','metric_note':f'Pearson={r.pearson:.6f}; Spearman={r.spearman:.6f}; residual={r.normalized_L2_residual:.3e}; no representative','selection_rule':False} for n,r in enumerate(sel.itertuples(index=False),61)])
 pairs=[(r.left_candidate_id,r.right_candidate_id) for r in pedges.itertuples(index=False)]+[(r.left_candidate_id,r.right_candidate_id) for r in add.itertuples(index=False)];groups,degree=components(oldids+ids,pairs);oldblock=prior.set_index('candidate_id').unified_block_id.to_dict();bid={};changed=[]
 for group in {tuple(v) for v in groups.values()}:
  inherited={oldblock[x] for x in group if x in oldblock};hasnew=any(x in ids for x in group)
  if not hasnew and len(inherited)==1:assigned=next(iter(inherited))
  else:assigned='';changed.append(sorted(group))
  for x in group:bid[x]=assigned
 for n,g in enumerate(sorted(changed,key=lambda x:tuple(x)),1):
  for x in g:bid[x]=f'U117-BLK-{n:03d}'
 if len(changed)!=11 or len(set(bid.values()))!=235:raise RuntimeError('graph projection mismatch')
 bank=prior.copy();bank['predecessor_unified_block_id']=bank.unified_block_id;bank['bank_version']='XREG-v1.1-TECHNICAL';bank['unified_block_id']=bank.candidate_id.map(bid);bank['unified_block_member_count']=bank.candidate_id.map(lambda x:len(groups[x]));bank['unified_edge_degree']=bank.candidate_id.map(degree);cols=bank.columns.tolist();src=co.set_index('candidate_id');rows=[]
 for cid in ids:
  s=src.loc[cid];v=cval.loc[cval.candidate_id.eq(cid),'value'].to_numpy(float);rows.append({'bank_version':'XREG-v1.1-TECHNICAL','candidate_id':cid,'candidate_group_id':s.candidate_group_id,'descriptor_family':s.descriptor_family,'output_name':s.output_name,'unit':s.unit,'source_population':s.source_population,'aggregation_formula':s.aggregation_formula,'applicable_family':s.applicable_family,'direct_or_derived':s.direct_or_derived,'source_bank':'PRM116_component_filter_sensitivity_batch','source_value_table':'PRM116_component_filter_sensitivity_values_long.csv','technical_role':'batch_BC_candidate','qualification_status':'full58_raw_table_batch_not_selected','confidence_status':'confirmed_raw_table_lineage','later_evaluation_role':'batch_BC_unselected_block_aware','active_feature':False,'promoted':False,'y_evidence':False,'notes':'PRM116 component filter sensitivity cohort; no y, selection or promotion','model_count':58,'finite_count':int(np.isfinite(v).sum()),'unique_count':int(np.unique(v).size),'unified_block_id':bid[cid],'unified_block_member_count':len(groups[cid]),'unified_edge_degree':degree[cid],'operational_grade':s.operational_grade,'literature_anchor':s.literature_anchor,'anchor_scope':s.anchor_scope,'predecessor_unified_block_id':pd.NA})
 bank=pd.concat([bank,pd.DataFrame(rows).reindex(columns=cols)],ignore_index=True);values=pd.concat([pval.assign(bank_version='XREG-v1.1-TECHNICAL'),cval.assign(bank_version='XREG-v1.1-TECHNICAL',finite=True,source_bank='PRM116_component_filter_sensitivity_batch')[['bank_version','model_id','model_family','candidate_id','value','finite','source_bank']]],ignore_index=True);wide=values.pivot(index=['model_id','model_family'],columns='candidate_id',values='value').reindex(columns=bank.candidate_id.tolist()).reset_index();edges=pd.concat([pedges,add.reindex(columns=pedges.columns)],ignore_index=True)
 lookup=bank.set_index('candidate_id');old=pblocks.copy();old['predecessor_unified_block_id']=old.unified_block_id;old['unified_block_id']=old.candidate_id.map(bid);old['unified_block_member_count']=old.candidate_id.map(lambda x:len(groups[x]));old['unified_edge_degree']=old.candidate_id.map(degree);old['new_in_PRM117']=False;new=[]
 for cid in ids:
  s=src.loc[cid];g=groups[cid];new.append({'unified_block_id':bid[cid],'predecessor_unified_block_id':pd.NA,'candidate_id':cid,'candidate_group_id':s.candidate_group_id,'descriptor_family':s.descriptor_family,'source_bank':'PRM116_component_filter_sensitivity_batch','technical_role':'batch_BC_candidate','later_evaluation_role':'batch_BC_unselected_block_aware','unified_block_member_count':len(g),'unified_edge_degree':degree[cid],'representative_selected':False,'block_policy':'standalone technical candidate; no selection in PRM117' if len(g)==1 else 'high x-only block; no representative selected','new_in_PRM107':False,'new_in_PRM109':False,'new_in_PRM111':False,'new_in_PRM113':False,'new_in_PRM115':False,'new_in_PRM117':True})
 blocks=pd.concat([old,pd.DataFrame(new).reindex(columns=old.columns)],ignore_index=True);policy=pd.DataFrame([{'candidate_id':cid,'operational_grade':src.loc[cid,'operational_grade'],'unified_block_id':bid[cid],'block_status':'crossbank_high_redundancy_block' if any(x in oldblock for x in groups[cid]) else 'singleton','block_member_count':len(groups[cid]),'selection_status':'not_selected','next_allowed_action':'future no-y batch or separately authorised block-aware grouped-y protocol'} for cid in ids])
 checks=[('P117-01',len(bank)==288 and bank.candidate_id.nunique()==288,'288 candidates'),('P117-02',len(values)==16704 and int(values.value.notna().sum())==16702,'16,704 values and two inherited NA'),('P117-03',wide.shape==(58,290),'58x288 wide matrix'),('P117-04',len(blocks)==288 and blocks.unified_block_id.nunique()==235,'235 graph blocks'),('P117-05',len(edges)==65 and edges.edge_id.nunique()==65,'65 edges'),('P117-06',len(add)==5 and add.relation.eq('high_redundancy').all(),'five declared PRM116 high relations'),('P117-07',len(policy)==11 and policy.block_status.value_counts().to_dict()=={'crossbank_high_redundancy_block':4,'singleton':7},'11-candidate policy'),('P117-08',not bank.active_feature.any() and not bank.promoted.any() and bank.y_evidence.astype(str).str.lower().eq('false').all(),'bank locks remain')];qa=pd.DataFrame([{'check_id':i,'status':'PASS' if ok else 'FAIL','detail':d} for i,ok,d in checks]);
 if not qa.status.eq('PASS').all():raise RuntimeError(qa.to_dict(orient='records'))
 (FACTORY/'reports').mkdir(parents=True,exist_ok=True)
 for s,f in {'candidate_bank':bank,'values_long':values,'values_wide':wide}.items():f.to_csv(TABLES/f'PRM117_xreg_v1_1_{s}.csv',index=False,encoding='utf-8-sig',float_format='%.17g')
 edges.to_csv(TABLES/'PRM117_unified_redundancy_edge_registry.csv',index=False,encoding='utf-8-sig');blocks.to_csv(TABLES/'PRM117_unified_redundancy_block_registry.csv',index=False,encoding='utf-8-sig');policy.to_csv(TABLES/'PRM117_component_filter_sensitivity_cohort_block_policy.csv',index=False,encoding='utf-8-sig');qa.to_csv(FACTORY/'reports'/'PRM117_producer_QA.csv',index=False,encoding='utf-8-sig');summary={'status':'PASS','checks':'8/8','candidates':288,'values':16704,'finite_values':16702,'blocks':235,'edges':65,'y_fit_selection_promotion':'0/0/0/0'};(FACTORY/'reports'/'PRM117_summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
