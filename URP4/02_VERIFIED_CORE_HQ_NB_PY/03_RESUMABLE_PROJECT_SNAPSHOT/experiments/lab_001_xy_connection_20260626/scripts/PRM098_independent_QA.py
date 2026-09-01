from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[3];LAB=ROOT/"experiments"/"lab_001_xy_connection_20260626";TABLES=LAB/"reports"/"tables";FACTORY=LAB/"factories"/"PRM-098";REPORTS=FACTORY/"reports"
sys.path.insert(0,str(Path(__file__).resolve().parent))
from PRM098_third_wave_formula_library import ect_outputs,ect_outputs_skimage_reference  # noqa:E402


def sha256(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()


def main():
    permit=json.loads((FACTORY/"contracts"/"PRM-098_BOUNDED_EXECUTION_PERMIT_20260723.json").read_text(encoding="utf-8"));registry=pd.read_csv(TABLES/"PRM098_input_mask_source_registry.csv",dtype=str,keep_default_na=False);ledger=pd.read_csv(REPORTS/"PRM098_progressive_panel_execution_ledger.csv",dtype=str,keep_default_na=False);values=pd.read_csv(REPORTS/"PRM098_representative_panel_values_long.csv",dtype=str,keep_default_na=False);schema=pd.read_csv(TABLES/"PRM097_candidate_output_schema.csv",dtype=str,keep_default_na=False);synthetic=pd.read_csv(REPORTS/"PRM098_synthetic_truth_results.csv");controls=pd.read_csv(TABLES/"PRM098_analytic_identity_controls.csv");routes=pd.read_csv(TABLES/"PRM098_group_technical_route.csv");resolution=pd.read_csv(TABLES/"PRM098_output_resolution_gate.csv",dtype=str,keep_default_na=False)
    runner_hash=sha256(LAB/"scripts"/"PRM098_run_cell.py");library_hash=sha256(LAB/"scripts"/"PRM098_third_wave_formula_library.py")
    done_meta=[]
    for row in ledger.loc[ledger.status.eq("passed")].itertuples(): done_meta.append(json.loads((FACTORY/"intermediate"/row.candidate_group_id/row.model_id/row.resolution_id/"done.json").read_text(encoding="utf-8")))
    old=pd.read_csv(TABLES/"PRM082_full58_all89_values_long.csv",dtype=str,keep_default_na=False);old["v"]=pd.to_numeric(old.value,errors="coerce");new=values.loc[values.artifact_path.eq("")].copy();new["v"]=pd.to_numeric(new.value,errors="coerce");v128=new.loc[new.resolution_id.eq("V128")]
    lineage=[]
    for model in ["B3","C1","L1","F1","T8","T9"]:
        # X019 exact replay from immutable X001/X016 parents.
        ratios=[]
        for axis in "xyz":
            for stat in ["mean","q50"]:
                a=float(old.loc[(old.model_id==model)&(old.candidate_id==f"LIT-X001::solid_chord_{axis}_{stat}_mm"),"v"].iloc[0]);b=float(old.loc[(old.model_id==model)&(old.candidate_id==f"LIT-X016::void_chord_{axis}_{stat}_mm"),"v"].iloc[0]);expected=a/b;cid=f"LIT-X019::solid_void_chord_{axis}_{stat}_ratio";observed=float(v128.loc[(v128.model_id==model)&(v128.candidate_id==cid),"v"].iloc[0]);lineage.append({"control":"X019_parent_ratio","model_id":model,"candidate_id":cid,"expected":expected,"observed":observed,"error":abs(expected-observed)})
                if stat=="q50":ratios.append(expected)
        cid="LIT-X019::solid_void_chord_q50_geomean_ratio";expected=float(math.exp(np.mean(np.log(ratios))));observed=float(v128.loc[(v128.model_id==model)&(v128.candidate_id==cid),"v"].iloc[0]);lineage.append({"control":"X019_parent_geomean","model_id":model,"candidate_id":cid,"expected":expected,"observed":observed,"error":abs(expected-observed)})
        # X024 final trace against existing X004 solid Euler density.
        cid="LIT-X024::ect_final_chi_solid_density_trace_per_mm3";expected=float(old.loc[(old.model_id==model)&(old.candidate_id=="LIT-X004::chi_solid_26_per_mm3"),"v"].iloc[0]);observed=float(v128.loc[(v128.model_id==model)&(v128.candidate_id==cid),"v"].iloc[0]);lineage.append({"control":"X024_final_equals_X004","model_id":model,"candidate_id":cid,"expected":expected,"observed":observed,"error":abs(expected-observed)})
        # X031 l=2 addition-theorem identities from existing X005 fabric tensor.
        def ov(cid):return float(old.loc[(old.model_id==model)&(old.candidate_id==cid),"v"].iloc[0])
        A=np.array([[ov("LIT-X005::A_xx"),ov("LIT-X005::A_xy"),ov("LIT-X005::A_xz")],[ov("LIT-X005::A_xy"),ov("LIT-X005::A_yy"),ov("LIT-X005::A_yz")],[ov("LIT-X005::A_xz"),ov("LIT-X005::A_yz"),ov("LIT-X005::A_zz")]])
        for cid,expected in [("LIT-X031::surface_normal_H2",1.5*float(np.sum(A*A))-.5),("LIT-X031::surface_normal_Q2_z",1.5*A[2,2]-.5)]:
            observed=float(v128.loc[(v128.model_id==model)&(v128.candidate_id==cid),"v"].iloc[0]);lineage.append({"control":"X031_l2_fabric_identity","model_id":model,"candidate_id":cid,"expected":expected,"observed":observed,"error":abs(expected-observed)})
    lineage=pd.DataFrame(lineage);lineage["tolerance"]=np.where(lineage.control.eq("X031_l2_fabric_identity"),1e-10,1e-12);lineage["status"]=np.where(lineage.error<=lineage.tolerance,"PASS","FAIL");lineage.to_csv(REPORTS/"PRM098_independent_lineage_replay.csv",index=False,encoding="utf-8-sig",lineterminator="\n")

    # Independent ECT full-curve replay: optimized cubical birth counts vs skimage Euler at every direction/height.
    rng=np.random.default_rng(98); fixtures=[rng.random((12,12,12))<.2,np.pad(np.ones((6,6,6),bool),3),np.zeros((12,12,12),bool)];ect_rows=[]
    for i,mask in enumerate(fixtures):
        a=ect_outputs(mask,40/mask.shape[0]);b=ect_outputs_skimage_reference(mask,40/mask.shape[0]);curve_error=float(np.max(np.abs(a.artifacts["ECT_curve_26x129"]-b.artifacts["ECT_curve_26x129"])));scalar_error=max(abs(a.outputs[k]-b.outputs[k]) for k in a.outputs);ect_rows.append({"fixture":i,"curve_points":26*129,"max_curve_error":curve_error,"max_scalar_error":scalar_error,"status":"PASS" if curve_error<=1e-15 and scalar_error<=1e-15 else "FAIL"})
    ect=pd.DataFrame(ect_rows);ect.to_csv(REPORTS/"PRM098_independent_ECT_curve_replay.csv",index=False,encoding="utf-8-sig",lineterminator="\n")

    checks={
        "permit_active":permit["status"]=="authorized_bounded_progressive_execution",
        "asset_registry_24_hash_pass":len(registry)==24 and registry.hash_pass.str.lower().eq("true").all() and all(sha256(ROOT/r.asset_path)==r.expected_sha256 for r in registry.itertuples()),
        "synthetic_22_of_22":len(synthetic)==22 and synthetic.status.eq("PASS").all(),
        "panel_144_declared":len(ledger)==144,
        "panel_139_passed":ledger.status.eq("passed").sum()==139,
        "x006_timeout_and_four_skips":ledger.status.eq("timeout").sum()==1 and ledger.status.eq("not_run_group_hold").sum()==4,
        "all_passed_done_hash_bound":len(done_meta)==139 and all(m["runner_sha256"]==runner_hash and m["formula_library_sha256"]==library_hash for m in done_meta),
        "all_passed_mask_hash_bound":all(m["mask_sha256"]==registry.loc[(registry.model_id==m["model_id"])&(registry.resolution_id==m["resolution_id"]),"expected_sha256"].iloc[0] for m in done_meta),
        "output_rows_1658":len(values)==1658,
        "candidate_ids_subset_schema":set(values.candidate_id)<=set(schema.candidate_id),
        "analytic_controls_204":len(controls)==204 and controls.status.eq("PASS").all(),
        "lineage_replay_60":len(lineage)==60 and lineage.status.eq("PASS").all(),
        "ECT_full_curve_replay_10062_points":len(ect)==3 and ect.status.eq("PASS").all(),
        "six_group_routes":len(routes)==6 and routes.candidate_group_id.nunique()==6,
        "no_feature_selected":routes.feature_selected.astype(str).str.lower().eq("false").all(),
        "no_feature_promoted":routes.feature_promoted.astype(str).str.lower().eq("false").all(),
        "no_y":routes.y_used.astype(str).str.lower().eq("false").all(),
        "technical_passes_exactly_six":resolution.loc[resolution.preregistered_role.isin(["BCL_specialist_candidate_FT_sensitivity","technical_candidate","derived_sensitivity_candidate"]),"frozen_gate_pass"].str.lower().eq("true").sum()==6,
        "X028_negative_control_only":routes.loc[routes.candidate_group_id.eq("LIT-X028"),"route"].iloc[0]=="negative_control_completed_no_promotion",
        "X006_resource_hold":routes.loc[routes.candidate_group_id.eq("LIT-X006"),"route"].iloc[0]=="hold_resource_cost",
        "full58_lock":permit["locks"]["full58"]==0,
        "y_fit_selection_promotion_locks":all(permit["locks"][k]==0 for k in ["performance_y_read","model_fit","feature_selection","feature_promotion"]),
    }
    qa=pd.DataFrame([{"check_id":f"IQA-{i:02d}","check":k,"status":"PASS" if v else "FAIL"} for i,(k,v) in enumerate(checks.items(),1)]);qa.to_csv(REPORTS/"PRM098_independent_QA.csv",index=False,encoding="utf-8-sig",lineterminator="\n")
    summary={"status":"PASS" if qa.status.eq("PASS").all() else "FAIL","checks":f"{qa.status.eq('PASS').sum()}/{len(qa)}","lineage":f"{lineage.status.eq('PASS').sum()}/{len(lineage)}","ECT_curve_points":26*129*3,"analytic_controls":f"{controls.status.eq('PASS').sum()}/{len(controls)}"};(REPORTS/"PRM098_independent_QA_summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8");print(json.dumps(summary))
    if summary["status"]!="PASS":print(qa.loc[qa.status.eq("FAIL")].to_string(index=False));raise SystemExit(1)


if __name__=="__main__":main()
