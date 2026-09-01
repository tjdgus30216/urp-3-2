from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT=Path(__file__).resolve().parents[3]; LAB=ROOT/"experiments"/"lab_001_xy_connection_20260626"; TABLES=LAB/"reports"/"tables"; FACTORY=LAB/"factories"/"PRM-098"; REPORTS=FACTORY/"reports"
TECH_ROLES={"BCL_specialist_candidate_FT_sensitivity","technical_candidate","derived_sensitivity_candidate"}


def srd(a,b):
    if not(np.isfinite(a) and np.isfinite(b)):return math.nan
    d=abs(a)+abs(b);return 0.0 if d==0 else 200*abs(a-b)/d


def rho(a,b):
    a=np.asarray(a,float);b=np.asarray(b,float);f=np.isfinite(a)&np.isfinite(b);a=a[f];b=b[f]
    return float(spearmanr(a,b).statistic) if len(a)>=3 and len(np.unique(a))>=2 and len(np.unique(b))>=2 else math.nan


def top2(ids,a,b):
    ids=np.asarray(ids);a=np.asarray(a,float);b=np.asarray(b,float);f=np.isfinite(a)&np.isfinite(b);ids=ids[f];a=a[f];b=b[f]
    if len(ids)<2 or len(np.unique(a))<2 or len(np.unique(b))<2:return math.nan
    return len(set(ids[np.argsort(a)[-2:]])&set(ids[np.argsort(b)[-2:]]))/2


def main():
    values=pd.read_csv(REPORTS/"PRM098_representative_panel_values_long.csv",dtype=str,keep_default_na=False); schema=pd.read_csv(TABLES/"PRM097_candidate_output_schema.csv",dtype=str,keep_default_na=False)
    values["numeric_value"]=pd.to_numeric(values.value,errors="coerce"); scalar=values.loc[values.artifact_path.eq("")].merge(schema[["candidate_id","preregistered_role","unit"]],on="candidate_id",how="left")
    policy=pd.DataFrame([{
        "policy_id":"P098-R01","fine_pair":"V128_vs_V192","median_srd_percent_max":5.0,"q90_srd_percent_max":10.0,"strict_pair_srd_percent_max":5.0,"strict_count_required":6,"panel_model_count":6,"spearman_min":.90,"top2_overlap_min":.80,"interpretation":"retain frozen absolute >=6 condition; with six registered models this is conservative 6/6, not a relaxed threshold","post_result_threshold_change":False,
    }]); policy.to_csv(TABLES/"PRM098_resolution_gate_interpretation.csv",index=False,encoding="utf-8-sig",lineterminator="\n")
    pivot=scalar.pivot_table(index=["candidate_group_id","candidate_id","preregistered_role","unit","model_id"],columns="resolution_id",values="numeric_value",aggfunc="first").reset_index();pivot.columns.name=None
    details=[];summaries=[]
    for (group,candidate,role,unit),g in pivot.groupby(["candidate_group_id","candidate_id","preregistered_role","unit"],sort=True):
        for model in ["B3","C1","L1","F1","T8","T9"]:
            row=g.loc[g.model_id.eq(model)]; a=float(row.V128.iloc[0]) if len(row) and "V128" in row and pd.notna(row.V128.iloc[0]) else math.nan; b=float(row.V192.iloc[0]) if len(row) and "V192" in row and pd.notna(row.V192.iloc[0]) else math.nan
            details.append({"candidate_group_id":group,"candidate_id":candidate,"preregistered_role":role,"model_id":model,"V128":a,"V192":b,"srd_percent":srd(a,b),"strict_pair":srd(a,b)<=5 if np.isfinite(srd(a,b)) else False})
        d=pd.DataFrame(details[-6:]); finite=d.loc[np.isfinite(d.srd_percent)]; ids=d.model_id.to_numpy(); va=d.V128.to_numpy(float); vb=d.V192.to_numpy(float); med=float(finite.srd_percent.median()) if len(finite) else math.nan;q90=float(np.quantile(finite.srd_percent,.9)) if len(finite) else math.nan;sp=rho(va,vb);ov=top2(ids,va,vb);strict=int(d.strict_pair.sum())
        complete=len(finite)==6; gate=complete and med<=5 and q90<=10 and strict>=6 and np.isfinite(sp) and sp>=.9 and np.isfinite(ov) and ov>=.8
        if group=="LIT-X006": state="hold_resource_stop_not_evaluable"
        elif role in TECH_ROLES: state="likely_resolution_qualified_not_selected" if gate else "hold_resolution_unresolved"
        else: state="diagnostic_or_negative_control_only"
        summaries.append({"candidate_group_id":group,"candidate_id":candidate,"preregistered_role":role,"unit":unit,"finite_pairs":len(finite),"median_srd_percent":med,"q90_srd_percent":q90,"strict_models":strict,"spearman_V128_V192":sp,"top2_overlap":ov,"frozen_gate_pass":gate,"technical_state":state})
    detail=pd.DataFrame(details);summary=pd.DataFrame(summaries);detail.to_csv(TABLES/"PRM098_V128_V192_resolution_detail.csv",index=False,encoding="utf-8-sig",lineterminator="\n");summary.to_csv(TABLES/"PRM098_output_resolution_gate.csv",index=False,encoding="utf-8-sig",lineterminator="\n")

    # Coverage/variation and hard analytic controls.
    coverage=scalar.groupby(["candidate_group_id","candidate_id","preregistered_role","resolution_id"]).numeric_value.agg(finite=lambda s:int(np.isfinite(s).sum()),unique=lambda s:int(pd.Series(s[np.isfinite(s)]).nunique()),minimum="min",maximum="max").reset_index();coverage.to_csv(TABLES/"PRM098_panel_coverage_variation.csv",index=False,encoding="utf-8-sig",lineterminator="\n")
    controls=[]
    existing=pd.read_csv(TABLES/"PRM082_full58_all89_values_long.csv",dtype=str,keep_default_na=False);existing["v"]=pd.to_numeric(existing.value,errors="coerce")
    v128=scalar.loc[scalar.resolution_id.eq("V128")]
    for axis in "xyz":
        for lag,tag in [(2.5,"2p5"),(10.0,"10")]:
            new_id=f"LIT-X028::binary_glcm_{axis}_{tag}mm_P11"; old_id=f"LIT-X002::S2_{axis}_r{str(lag).replace('.', 'p')}_probability"
            for model in ["B3","C1","L1","F1","T8","T9"]:
                new=float(v128.loc[(v128.candidate_id==new_id)&(v128.model_id==model),"numeric_value"].iloc[0]);old=float(existing.loc[(existing.candidate_id==old_id)&(existing.model_id==model),"v"].iloc[0]);controls.append({"control":"X028_P11_equals_X002_S2","model_id":model,"axis":axis,"lag_mm":lag,"error":abs(new-old),"status":"PASS" if abs(new-old)<=1e-14 else "FAIL"})
    for row in scalar.loc[scalar.candidate_group_id.eq("LIT-X008")].groupby(["model_id","resolution_id"]):
        (_, _),g=row;b=float(g.loc[g.candidate_id.str.endswith("bottleneck_q10_over_q50"),"numeric_value"].iloc[0]);c=float(g.loc[g.candidate_id.str.endswith("constriction_index_one_minus_q10_q50"),"numeric_value"].iloc[0]);controls.append({"control":"X008_constriction_equals_one_minus_bottleneck","model_id":g.model_id.iloc[0],"axis":"","lag_mm":"","error":abs(c-(1-b)),"status":"PASS" if abs(c-(1-b))<=1e-14 else "FAIL"})
    for (model,res),g in scalar.loc[scalar.candidate_group_id.eq("LIT-X028")].groupby(["model_id","resolution_id"]):
        for axis in "xyz":
            for tag in ["2p5mm","10mm"]:
                c=float(g.loc[g.candidate_id.eq(f"LIT-X028::binary_glcm_{axis}_{tag}_contrast"),"numeric_value"].iloc[0]);h=float(g.loc[g.candidate_id.eq(f"LIT-X028::binary_glcm_{axis}_{tag}_homogeneity"),"numeric_value"].iloc[0]);e=abs(h-(1-c/2));controls.append({"control":"X028_homogeneity_affine_identity","model_id":model,"axis":axis,"lag_mm":tag,"error":e,"status":"PASS" if e<=1e-14 else "FAIL"})
    controls=pd.DataFrame(controls);controls.to_csv(TABLES/"PRM098_analytic_identity_controls.csv",index=False,encoding="utf-8-sig",lineterminator="\n")

    pair=[]
    for res in ["V064","V096","V128","V192"]:
        g=scalar.loc[scalar.resolution_id.eq(res)]
        for group in g.candidate_group_id.unique():
            gg=g.loc[g.candidate_group_id.eq(group)];a=gg.loc[gg.model_id.eq("T8")].set_index("candidate_id").numeric_value;b=gg.loc[gg.model_id.eq("T9")].set_index("candidate_id").numeric_value;common=a.index.intersection(b.index)
            for candidate in common: pair.append({"candidate_group_id":group,"candidate_id":candidate,"resolution_id":res,"T8":a[candidate],"T9":b[candidate],"absolute_delta":abs(a[candidate]-b[candidate]),"srd_percent":srd(a[candidate],b[candidate]),"nonzero_delta":abs(a[candidate]-b[candidate])>1e-14})
    pair=pd.DataFrame(pair);pair.to_csv(TABLES/"PRM098_T8_T9_pair_diagnostic.csv",index=False,encoding="utf-8-sig",lineterminator="\n")

    group_rows=[]
    for group,g in summary.groupby("candidate_group_id"):
        tech=g.loc[g.preregistered_role.isin(TECH_ROLES)]; resource_hold=group=="LIT-X006"; passed=int(tech.frozen_gate_pass.sum());total=len(tech)
        if group=="LIT-X028": route="negative_control_completed_no_promotion"
        elif resource_hold: route="hold_resource_cost"
        elif passed>0: route="partial_likely_outputs_not_selected" if passed<total else "all_technical_outputs_likely_not_selected"
        else: route="hold_no_output_passed_resolution_gate"
        group_rows.append({"candidate_group_id":group,"technical_outputs":total,"resolution_passed_outputs":passed,"resolution_failed_outputs":total-passed,"resource_hold":resource_hold,"route":route,"feature_selected":False,"feature_promoted":False,"y_used":False})
    groups=pd.DataFrame(group_rows);groups.to_csv(TABLES/"PRM098_group_technical_route.csv",index=False,encoding="utf-8-sig",lineterminator="\n")
    result={"status":"PASS_WITH_HOLDS","scalar_outputs":int(summary.shape[0]),"technical_outputs":int(summary.preregistered_role.isin(TECH_ROLES).sum()),"technical_resolution_passes":int(summary.loc[summary.preregistered_role.isin(TECH_ROLES),"frozen_gate_pass"].sum()),"analytic_controls":f"{controls.status.eq('PASS').sum()}/{len(controls)}","group_routes":dict(zip(groups.candidate_group_id,groups.route)),"y_fit_selection_promotion":"0/0/0/0"}
    (REPORTS/"PRM098_technical_gate_summary.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8");print(json.dumps(result));print(groups.to_string(index=False))


if __name__=="__main__":main()
