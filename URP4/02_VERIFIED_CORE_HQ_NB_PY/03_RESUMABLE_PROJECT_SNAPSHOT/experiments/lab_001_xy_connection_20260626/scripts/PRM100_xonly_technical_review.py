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
PERMIT = FACTORY99 / "authorizations" / "PRM-100_THIRD_WAVE_FULL58_V128_EXECUTION_PERMIT_20260723.json"
OUTPUTS = [
    "LIT-X019::solid_void_chord_q50_geomean_ratio",
    "LIT-X019::solid_void_chord_x_q50_ratio",
    "LIT-X019::solid_void_chord_y_q50_ratio",
    "LIT-X019::solid_void_chord_z_q50_ratio",
    "LIT-X024::ect_abs_auc_direction_mean_per_mm3",
    "LIT-X024::ect_total_variation_direction_mean_per_mm3",
]
EXACT_RTOL, EXACT_ATOL, PROP_RESIDUAL, HIGH = 1e-10, 1e-12, 1e-6, 0.98


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def variable(values: np.ndarray) -> bool:
    v = values[np.isfinite(values)]
    return len(v) >= 3 and len(np.unique(v)) >= 3 and (np.max(v) - np.min(v)) > 1e-10 * max(1.0, np.max(np.abs(v)))


def classify(left: np.ndarray, right: np.ndarray) -> dict:
    common = np.isfinite(left) & np.isfinite(right)
    a, b = left[common], right[common]
    av, bv = variable(a), variable(b)
    if len(a) != 58:
        relation, slope, residual, pearson, spearman = "insufficient_common_coverage", np.nan, np.nan, np.nan, np.nan
    elif not av or not bv:
        relation, slope, residual, pearson, spearman = "degenerate_nonvarying_reference_or_candidate", np.nan, np.nan, np.nan, np.nan
    elif np.allclose(a, b, rtol=EXACT_RTOL, atol=EXACT_ATOL):
        relation, slope, residual = "exact_duplicate", 1.0, 0.0
        pearson, spearman = float(pearsonr(a, b).statistic), float(spearmanr(a, b).statistic)
    else:
        slope = float(np.dot(a, b) / np.dot(a, a))
        residual = float(np.linalg.norm(b - slope * a) / max(np.linalg.norm(b), 1e-30))
        pearson, spearman = float(pearsonr(a, b).statistic), float(spearmanr(a, b).statistic)
        if residual <= PROP_RESIDUAL and abs(slope) > 1e-12:
            relation = "proportional_duplicate"
        elif abs(pearson) >= HIGH and abs(spearman) >= HIGH:
            relation = "high_redundancy"
        else:
            relation = "distinct_or_unresolved"
    return {"common_models": int(common.sum()), "left_variable": av, "right_variable": bv, "relation": relation, "through_origin_slope": slope, "normalized_L2_residual": residual, "pearson": pearson, "spearman": spearman}


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    values_path = TABLES / "PRM099_third_wave_full58_six_values_long.csv"
    values = pd.read_csv(values_path)
    xreg = pd.read_csv(TABLES / "PRM096_xreg_v0_2_values_long.csv")
    scope = pd.read_csv(TABLES / "PRM099_returned_six_output_scope.csv")
    permit = json.loads(PERMIT.read_text(encoding="utf-8"))
    ledger = pd.read_csv(FACTORY100 / "reports" / "PRM100_execution_ledger.csv")

    if len(values) != 348 or set(values.candidate_id) != set(OUTPUTS) or values.model_id.nunique() != 58:
        raise SystemExit("merged full58 scope mismatch")
    if not np.isfinite(values.value).all():
        raise SystemExit("nonfinite merged value")
    if not (ledger.status.isin(["passed", "reused"]).all() and len(ledger) == 58):
        raise SystemExit("atomic ledger mismatch")

    wide = values.pivot(index="model_id", columns="candidate_id", values="value").sort_index()
    metadata = xreg[["model_id", "model_family"]].drop_duplicates().set_index("model_id")
    wide = metadata.join(wide, how="right")
    cov = []
    for cid in OUTPUTS:
        v = wide[cid].to_numpy(float)
        cov.append({"candidate_id": cid, "finite_count": int(np.isfinite(v).sum()), "unique_count": int(np.unique(v[np.isfinite(v)]).size), "mean": float(np.mean(v)), "population_std": float(np.std(v, ddof=0)), "median": float(np.median(v)), "iqr": float(np.quantile(v,.75)-np.quantile(v,.25)), "min": float(np.min(v)), "max": float(np.max(v)), "cv": float(np.std(v,ddof=0)/np.mean(v)) if abs(np.mean(v))>1e-12 else np.nan, "technical_state": "full58_xonly_unselected"})
    coverage = pd.DataFrame(cov)
    coverage.to_csv(TABLES / "PRM100_full58_coverage_variation.csv", index=False, encoding="utf-8-sig")

    parent_rows = []
    for model in wide.index:
        one = xreg[xreg.model_id.eq(model)].set_index("candidate_id")
        ratios = {axis: float(one.loc[f"LIT-X001::solid_chord_{axis}_q50_mm", "value"]) / float(one.loc[f"LIT-X016::void_chord_{axis}_q50_mm", "value"]) for axis in "xyz"}
        expected = {"LIT-X019::solid_void_chord_q50_geomean_ratio": float(math.exp(np.mean(np.log(list(ratios.values()))))), **{f"LIT-X019::solid_void_chord_{a}_q50_ratio": ratios[a] for a in "xyz"}}
        for cid, val in expected.items():
            err = abs(val - float(wide.loc[model, cid]))
            parent_rows.append({"model_id": model, "candidate_id": cid, "expected_parent_derived": val, "observed": float(wide.loc[model,cid]), "abs_error": err, "status": "PASS" if err <= 1e-12 else "FAIL"})
    parent = pd.DataFrame(parent_rows)
    parent.to_csv(TABLES / "PRM100_X019_full58_parent_lineage_replay.csv", index=False, encoding="utf-8-sig")

    ect_rows = []
    x004 = xreg[xreg.candidate_id.eq("LIT-X004::chi_solid_26_per_mm3")].set_index("model_id")
    for model in wide.index:
        marker = json.loads((FACTORY99 / "intermediate" / model / "done.json").read_text(encoding="utf-8"))
        observed, expected = float(marker["diagnostic_final_chi"]), float(x004.loc[model,"value"])
        ect_rows.append({"model_id": model, "marker_final_chi": observed, "X004_final_chi": expected, "abs_error": abs(observed-expected), "curve_sha256": marker["ECT_curve_sha256"], "status": "PASS" if abs(observed-expected)<=1e-12 else "FAIL"})
    ect = pd.DataFrame(ect_rows)
    ect.to_csv(TABLES / "PRM100_X024_final_chi_lineage_replay.csv", index=False, encoding="utf-8-sig")

    relation_rows = []
    for cid in OUTPUTS:
        left = wide[cid].rename("left").reset_index()
        for eid in sorted(xreg.candidate_id.unique()):
            right = xreg[xreg.candidate_id.eq(eid)][["model_id", "value"]].rename(columns={"value":"right"})
            m = left.merge(right, on="model_id", how="inner")
            relation_rows.append({"candidate_id": cid, "existing_candidate_id": eid, **classify(m.left.to_numpy(float),m.right.to_numpy(float)), "evidence_scope":"full58_xonly", "selection_effect":"none"})
    relations = pd.DataFrame(relation_rows)
    relations.to_csv(TABLES / "PRM100_full58_vs_XREG_redundancy.csv", index=False, encoding="utf-8-sig")

    internal_rows = []
    for i, left_id in enumerate(OUTPUTS):
        for right_id in OUTPUTS[i+1:]:
            internal_rows.append({"left_candidate_id":left_id,"right_candidate_id":right_id,**classify(wide[left_id].to_numpy(float),wide[right_id].to_numpy(float)),"evidence_scope":"full58_xonly","selection_effect":"none"})
    internal = pd.DataFrame(internal_rows)
    internal.to_csv(TABLES / "PRM100_internal_six_redundancy.csv", index=False, encoding="utf-8-sig")

    pairs = []
    for a,b,label in [("T8","T9","T8_T9"),("T5","T6","T5_T6")]:
        for cid in OUTPUTS:
            va,vb=float(wide.loc[a,cid]),float(wide.loc[b,cid])
            pairs.append({"pair_id":label,"left_model":a,"right_model":b,"candidate_id":cid,"left_value":va,"right_value":vb,"absolute_delta":abs(va-vb),"relative_delta":abs(va-vb)/max(abs(va),abs(vb),1e-12),"nonzero":abs(va-vb)>1e-12,"claim_boundary":"diagnostic only; no rescue/prediction claim"})
    pair_df = pd.DataFrame(pairs)
    pair_df.to_csv(TABLES / "PRM100_difficult_pair_diagnostic.csv", index=False, encoding="utf-8-sig")

    routes = []
    for cid in OUTPUTS:
        r = relations[relations.candidate_id.eq(cid)]
        ir = internal[(internal.left_candidate_id.eq(cid)) | (internal.right_candidate_id.eq(cid))]
        routes.append({"candidate_id":cid,"full58_state":"likely_technical_unselected","exact_vs_XREG":int(r.relation.eq("exact_duplicate").sum()),"proportional_vs_XREG":int(r.relation.eq("proportional_duplicate").sum()),"high_redundancy_vs_XREG":int(r.relation.eq("high_redundancy").sum()),"internal_exact_or_prop":int(ir.relation.isin(["exact_duplicate","proportional_duplicate"]).sum()),"active_feature":False,"promoted":False,"y_used":False,"next_route":"return_control_tower_for_no_y_block_policy"})
    pd.DataFrame(routes).to_csv(TABLES / "PRM100_full58_technical_route.csv", index=False, encoding="utf-8-sig")

    qa = [
        ("P100-01",len(values)==348,"348 merged values"),("P100-02",values.model_id.nunique()==58,"58 models"),("P100-03",set(values.candidate_id)==set(OUTPUTS),"exact six roster"),("P100-04",np.isfinite(values.value).all(),"all finite"),("P100-05",len(ledger)==58 and ledger.status.eq("passed").all(),"58 atomic passed"),("P100-06",len(parent)==232 and parent.status.eq("PASS").all(),"232 X019 parent replays"),("P100-07",len(ect)==58 and ect.status.eq("PASS").all(),"58 X024 final chi replays"),("P100-08",len(relations)==648,"648 crossbank relations"),("P100-09",len(internal)==15,"15 internal relations"),("P100-10",len(pair_df)==12,"two difficult pairs x six outputs"),("P100-11",permit["expected_values"]==348 and permit["execution_authorized"] is True,"permit scope"),("P100-12",scope.active_feature.astype(str).str.lower().eq("false").all(),"no active feature"),
    ]
    producer=pd.DataFrame([{"check_id":i,"status":"PASS" if ok else "FAIL","detail":d} for i,ok,d in qa])
    producer.to_csv(REPORTS / "PRM100_producer_QA.csv",index=False,encoding="utf-8-sig")
    summary={"status":"PASS" if producer.status.eq("PASS").all() else "FAIL","checks":f"{int(producer.status.eq('PASS').sum())}/{len(producer)}","values":348,"models":58,"execution_performed":True,"y_fit_selection_promotion":"0/0/0/0"}
    (REPORTS / "PRM100_technical_review_summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2))
    if summary["status"]!="PASS": raise SystemExit(1)


if __name__=="__main__": main()
