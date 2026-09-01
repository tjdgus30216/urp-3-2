from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
TABLES = LAB / "reports" / "tables"
FACTORY99 = LAB / "factories" / "PRM-099"
FACTORY100 = LAB / "factories" / "PRM-100"
REPORTS = FACTORY100 / "reports"
OUTPUTS = [
    "LIT-X019::solid_void_chord_q50_geomean_ratio", "LIT-X019::solid_void_chord_x_q50_ratio",
    "LIT-X019::solid_void_chord_y_q50_ratio", "LIT-X019::solid_void_chord_z_q50_ratio",
    "LIT-X024::ect_abs_auc_direction_mean_per_mm3", "LIT-X024::ect_total_variation_direction_mean_per_mm3",
]


def digest(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()


def variable(x: np.ndarray) -> bool:
    x=x[np.isfinite(x)]
    return len(x)>=3 and len(np.unique(x))>=3 and np.max(x)-np.min(x)>1e-10*max(1.,np.max(np.abs(x)))


def label(a: np.ndarray,b: np.ndarray) -> str:
    common=np.isfinite(a)&np.isfinite(b)
    a,b=a[common],b[common]
    if len(a)!=58: return "insufficient_common_coverage"
    if not variable(a) or not variable(b): return "degenerate_nonvarying_reference_or_candidate"
    if np.allclose(a,b,rtol=1e-10,atol=1e-12): return "exact_duplicate"
    slope=np.dot(a,b)/np.dot(a,a); resid=np.linalg.norm(b-slope*a)/max(np.linalg.norm(b),1e-30)
    p=float(pearsonr(a,b).statistic); s=float(spearmanr(a,b).statistic)
    if resid<=1e-6 and abs(slope)>1e-12: return "proportional_duplicate"
    if abs(p)>=.98 and abs(s)>=.98: return "high_redundancy"
    return "distinct_or_unresolved"


def main() -> None:
    values=pd.read_csv(TABLES/'PRM099_third_wave_full58_six_values_long.csv')
    wide=values.pivot(index='model_id',columns='candidate_id',values='value').sort_index()
    xreg=pd.read_csv(TABLES/'PRM096_xreg_v0_2_values_long.csv')
    assets=pd.read_csv(TABLES/'PRM099_full58_V128_asset_registry.csv')
    ledger=pd.read_csv(FACTORY100/'reports'/'PRM100_execution_ledger.csv')
    permit=json.loads((FACTORY99/'authorizations'/'PRM-100_THIRD_WAVE_FULL58_V128_EXECUTION_PERMIT_20260723.json').read_text(encoding='utf-8'))
    route=pd.read_csv(TABLES/'PRM100_full58_technical_route.csv')

    merge_rows=[]
    marker_rows=[]
    for model in sorted(wide.index):
        cell=pd.read_csv(FACTORY99/'intermediate'/model/'values.csv').sort_values('candidate_id').reset_index(drop=True)
        merged=values[values.model_id.eq(model)].sort_values('candidate_id').reset_index(drop=True)
        same=len(cell)==6 and cell.candidate_id.tolist()==merged.candidate_id.tolist() and np.allclose(cell.value,merged.value,rtol=1e-12,atol=1e-14)
        merge_rows.append({'model_id':model,'status':'PASS' if same else 'FAIL'})
        marker=json.loads((FACTORY99/'intermediate'/model/'done.json').read_text(encoding='utf-8'))
        expected=assets.set_index('model_id').loc[model,'expected_mask_sha256']
        marker_rows.append({'model_id':model,'status':'PASS' if marker.get('status')=='passed' and marker.get('output_roster')==OUTPUTS and marker.get('mask_sha256')==expected and (FACTORY99/'intermediate'/model/'ECT_curve_26x129.npz').is_file() else 'FAIL'})
    merge_df=pd.DataFrame(merge_rows); marker_df=pd.DataFrame(marker_rows)
    merge_df.to_csv(REPORTS/'PRM100_independent_merge_replay.csv',index=False,encoding='utf-8-sig')
    marker_df.to_csv(REPORTS/'PRM100_independent_marker_replay.csv',index=False,encoding='utf-8-sig')

    parent_rows=[]
    x004=xreg[xreg.candidate_id.eq('LIT-X004::chi_solid_26_per_mm3')].set_index('model_id')
    ect_rows=[]
    for model in wide.index:
        one=xreg[xreg.model_id.eq(model)].set_index('candidate_id')
        r={a:float(one.loc[f'LIT-X001::solid_chord_{a}_q50_mm','value'])/float(one.loc[f'LIT-X016::void_chord_{a}_q50_mm','value']) for a in 'xyz'}
        exp={'LIT-X019::solid_void_chord_q50_geomean_ratio':float(math.exp(np.mean(np.log(list(r.values()))))),**{f'LIT-X019::solid_void_chord_{a}_q50_ratio':r[a] for a in 'xyz'}}
        for cid,val in exp.items():
            error=abs(val-float(wide.loc[model,cid])); parent_rows.append({'model_id':model,'candidate_id':cid,'abs_error':error,'status':'PASS' if error<=1e-12 else 'FAIL'})
        marker=json.loads((FACTORY99/'intermediate'/model/'done.json').read_text(encoding='utf-8'))
        error=abs(float(marker['diagnostic_final_chi'])-float(x004.loc[model,'value']))
        ect_rows.append({'model_id':model,'abs_error':error,'status':'PASS' if error<=1e-12 else 'FAIL'})
    parent=pd.DataFrame(parent_rows); ect=pd.DataFrame(ect_rows)
    parent.to_csv(REPORTS/'PRM100_independent_parent_replay.csv',index=False,encoding='utf-8-sig')
    ect.to_csv(REPORTS/'PRM100_independent_ECT_lineage_replay.csv',index=False,encoding='utf-8-sig')

    claimed=pd.read_csv(TABLES/'PRM100_full58_vs_XREG_redundancy.csv')
    rel_rows=[]
    for row in claimed.itertuples(index=False):
        a=wide[row.candidate_id].to_numpy(float)
        b=xreg[xreg.candidate_id.eq(row.existing_candidate_id)].set_index('model_id').loc[wide.index,'value'].to_numpy(float)
        actual=label(a,b)
        rel_rows.append({'candidate_id':row.candidate_id,'existing_candidate_id':row.existing_candidate_id,'expected_relation':row.relation,'replayed_relation':actual,'status':'PASS' if actual==row.relation else 'FAIL'})
    rel=pd.DataFrame(rel_rows); rel.to_csv(REPORTS/'PRM100_independent_crossbank_relation_replay.csv',index=False,encoding='utf-8-sig')

    claimed_int=pd.read_csv(TABLES/'PRM100_internal_six_redundancy.csv')
    int_rows=[]
    for row in claimed_int.itertuples(index=False):
        actual=label(wide[row.left_candidate_id].to_numpy(float),wide[row.right_candidate_id].to_numpy(float))
        int_rows.append({'left_candidate_id':row.left_candidate_id,'right_candidate_id':row.right_candidate_id,'expected_relation':row.relation,'replayed_relation':actual,'status':'PASS' if actual==row.relation else 'FAIL'})
    internal=pd.DataFrame(int_rows); internal.to_csv(REPORTS/'PRM100_independent_internal_relation_replay.csv',index=False,encoding='utf-8-sig')

    checks=[]
    def add(i,ok,d): checks.append({'check_id':i,'status':'PASS' if ok else 'FAIL','detail':d})
    add('I100-01',len(values)==348,'348 values')
    add('I100-02',values.model_id.nunique()==58 and set(values.candidate_id)==set(OUTPUTS),'58x6 scope')
    add('I100-03',np.isfinite(values.value).all(),'all finite')
    add('I100-04',len(ledger)==58 and ledger.status.eq('passed').all(),'58 atomic cells')
    add('I100-05',len(merge_df)==58 and merge_df.status.eq('PASS').all(),'58 merged cell replays')
    add('I100-06',len(marker_df)==58 and marker_df.status.eq('PASS').all(),'58 marker/artifact replays')
    add('I100-07',len(parent)==232 and parent.status.eq('PASS').all(),'232 X019 parent replays')
    add('I100-08',len(ect)==58 and ect.status.eq('PASS').all(),'58 X024 endpoint lineages')
    add('I100-09',len(rel)==648 and rel.status.eq('PASS').all(),'648 crossbank relation replays')
    add('I100-10',len(internal)==15 and internal.status.eq('PASS').all(),'15 internal relation replays')
    add('I100-11',claimed.relation.eq('high_redundancy').sum()==2,'two full58 high redundancy edges')
    add('I100-12',route.active_feature.astype(str).str.lower().eq('false').all() and route.promoted.astype(str).str.lower().eq('false').all(),'no promotion')
    add('I100-13',permit['expected_values']==348 and permit['execution_authorized'] is True,'permit scope')
    add('I100-14',all(v==0 for v in permit['locks'].values()),'scientific locks zero')
    output=pd.DataFrame(checks); output.to_csv(REPORTS/'PRM100_independent_QA.csv',index=False,encoding='utf-8-sig')
    summary={'status':'PASS' if output.status.eq('PASS').all() else 'FAIL','checks':f"{int(output.status.eq('PASS').sum())}/{len(output)}",'execution_performed':True,'y_fit_selection_promotion':'0/0/0/0'}
    (REPORTS/'PRM100_independent_QA_summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))
    if summary['status']!='PASS':raise SystemExit(1)


if __name__=='__main__':main()
