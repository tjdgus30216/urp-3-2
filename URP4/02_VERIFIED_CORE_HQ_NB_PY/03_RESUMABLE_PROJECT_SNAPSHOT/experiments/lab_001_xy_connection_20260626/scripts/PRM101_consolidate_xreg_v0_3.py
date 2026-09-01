from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
TABLES = LAB / "reports" / "tables"
FACTORY = LAB / "factories" / "PRM-101"
CONTRACT = FACTORY / "contracts" / "PRM-101_XREG_V0_3_CONSOLIDATION_CONTRACT_20260723.json"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for c in iter(lambda: f.read(1024 * 1024), b""):
            h.update(c)
    return h.hexdigest()


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    for item in contract["inputs"]:
        p = ROOT / item["path"]
        if sha(p) != item["sha256"]:
            raise RuntimeError(f"immutable input hash mismatch: {item['path']}")
    prior_bank = pd.read_csv(TABLES / "PRM096_enriched_xreg_v0_2_candidate_bank.csv")
    prior_values = pd.read_csv(TABLES / "PRM096_xreg_v0_2_values_long.csv")
    prior_edges = pd.read_csv(TABLES / "PRM096_unified_redundancy_edge_registry.csv")
    prior_blocks = pd.read_csv(TABLES / "PRM096_unified_redundancy_block_registry.csv")
    six = pd.read_csv(TABLES / "PRM099_third_wave_full58_six_values_long.csv")
    coverage = pd.read_csv(TABLES / "PRM100_full58_coverage_variation.csv").set_index("candidate_id")
    cross = pd.read_csv(TABLES / "PRM100_full58_vs_XREG_redundancy.csv")
    model_family = prior_values[["model_id", "model_family"]].drop_duplicates().set_index("model_id")["model_family"].to_dict()
    six_ids = [
        "LIT-X019::solid_void_chord_q50_geomean_ratio", "LIT-X019::solid_void_chord_x_q50_ratio",
        "LIT-X019::solid_void_chord_y_q50_ratio", "LIT-X019::solid_void_chord_z_q50_ratio",
        "LIT-X024::ect_abs_auc_direction_mean_per_mm3", "LIT-X024::ect_total_variation_direction_mean_per_mm3",
    ]
    if sorted(six.candidate_id.unique()) != sorted(six_ids) or len(six) != 348 or not np.isfinite(six.value).all():
        raise RuntimeError("PRM100 six-output source scope is not exactly 348 finite values")
    old = prior_bank.copy()
    old["bank_version"] = "XREG-v0.3-TECHNICAL"
    old.loc[old.unified_block_id.eq("U096-BLK-044"), ["unified_block_member_count", "unified_edge_degree"]] = [3, 2]
    old.loc[old.unified_block_id.eq("U096-BLK-044"), "notes"] = "v0.3 block expanded with X024 absolute-AUC; no selection; block-aware later evaluation only"
    metadata = {
        six_ids[0]: ("LIT-X019", "phase_scale_ratio", "solid_void_chord_q50_geomean_ratio", "ratio", "matched fixed-V128 solid/void directional q50 chord summaries", "geometric mean of matched x/y/z q50 solid-to-void chord ratios", "derived_from_existing_X001_X016_parents", "U101-BLK-090", 1, 0, "sensitivity_candidate", "likely_resolution_qualified_confirmed_lineage", "third_wave_likely_unselected"),
        six_ids[1]: ("LIT-X019", "phase_scale_ratio", "solid_void_chord_x_q50_ratio", "ratio", "matched fixed-V128 solid/void x-direction q50 chord summaries", "solid q50 / void q50, same x axis/stat/resolution", "derived_from_existing_X001_X016_parents", "U101-BLK-091", 1, 0, "sensitivity_candidate", "likely_resolution_qualified_confirmed_lineage", "third_wave_likely_unselected"),
        six_ids[2]: ("LIT-X019", "phase_scale_ratio", "solid_void_chord_y_q50_ratio", "ratio", "matched fixed-V128 solid/void y-direction q50 chord summaries", "solid q50 / void q50, same y axis/stat/resolution", "derived_from_existing_X001_X016_parents", "U101-BLK-092", 1, 0, "sensitivity_candidate", "likely_resolution_qualified_confirmed_lineage", "third_wave_likely_unselected"),
        six_ids[3]: ("LIT-X019", "phase_scale_ratio", "solid_void_chord_z_q50_ratio", "ratio", "matched fixed-V128 solid/void z-direction q50 chord summaries", "solid q50 / void q50, same z axis/stat/resolution", "derived_from_existing_X001_X016_parents", "U101-BLK-093", 1, 0, "sensitivity_candidate", "likely_resolution_qualified_confirmed_lineage", "third_wave_likely_unselected"),
        six_ids[4]: ("LIT-X024", "euler_characteristic_transform", "ect_abs_auc_direction_mean_per_mm3", "1/mm3", "fixed-V128 solid-26 ECT curves over 26 directions and 129 projection heights", "mean direction-normalized absolute ECT area under curve / specimen volume", "direct_from_existing_V128_mask_formula", "U096-BLK-044", 3, 2, "diagnostic_blocked_by_X004_redundancy", "likely_resolution_qualified_confirmed_lineage", "blocked_diagnostic_not_selected"),
        six_ids[5]: ("LIT-X024", "euler_characteristic_transform", "ect_total_variation_direction_mean_per_mm3", "1/mm3", "fixed-V128 solid-26 ECT curves over 26 directions and 129 projection heights", "mean direction-normalized total variation / specimen volume", "direct_from_existing_V128_mask_formula", "U101-BLK-094", 1, 0, "sensitivity_candidate", "likely_resolution_qualified_confirmed_lineage", "third_wave_likely_unselected"),
    }
    rows = []
    for cid in six_ids:
        group, family, name, unit, pop, formula, lineage, bid, count, degree, role, confidence, later = metadata[cid]
        c = coverage.loc[cid]
        rows.append({"bank_version": "XREG-v0.3-TECHNICAL", "candidate_id": cid, "candidate_group_id": group, "descriptor_family": family, "output_name": name, "unit": unit, "source_population": pop, "aggregation_formula": formula, "applicable_family": "B|C|F|L|T", "direct_or_derived": lineage, "source_bank": "PRM100_full58_exact_permit", "source_value_table": "PRM099_third_wave_full58_six_values_long.csv", "technical_role": role, "qualification_status": "full58_resolution_qualified_not_selected", "confidence_status": confidence, "later_evaluation_role": later, "active_feature": False, "promoted": False, "y_evidence": False, "notes": "PRM100 exact execution; source filename retains PRM099 prefix by permit-runner compatibility; no y/selection/promotion", "model_count": 58, "finite_count": int(c.finite_count), "unique_count": int(c.unique_count), "unified_block_id": bid, "unified_block_member_count": count, "unified_edge_degree": degree})
    bank = pd.concat([old, pd.DataFrame(rows, columns=old.columns)], ignore_index=True)
    prior_out = prior_values.copy(); prior_out["bank_version"] = "XREG-v0.3-TECHNICAL"
    new_out = six.assign(bank_version="XREG-v0.3-TECHNICAL", model_family=six.model_id.map(model_family), finite=np.isfinite(six.value), source_bank="PRM100_full58_exact_permit")
    new_out = new_out[["bank_version", "model_id", "model_family", "candidate_id", "value", "finite", "source_bank"]]
    values = pd.concat([prior_out, new_out], ignore_index=True)
    order = bank.candidate_id.tolist()
    wide = values.pivot(index=["model_id", "model_family"], columns="candidate_id", values="value").reindex(columns=order).reset_index()
    edges = prior_edges.copy()
    new_edges = pd.DataFrame([
        {"edge_id": "U101-EDGE-024", "left_candidate_id": six_ids[4], "right_candidate_id": "LIT-X004::chi_solid_26", "relation": "high_redundancy", "edge_source": "PRM100_full58_crossbank", "metric_note": "full58 pearson/spearman high; retain provenance, primary block", "selection_rule": False},
        {"edge_id": "U101-EDGE-025", "left_candidate_id": six_ids[4], "right_candidate_id": "LIT-X004::chi_solid_26_per_mm3", "relation": "high_redundancy", "edge_source": "PRM100_full58_crossbank", "metric_note": "full58 pearson/spearman high; retain provenance, primary block", "selection_rule": False},
    ])
    edges = pd.concat([edges, new_edges], ignore_index=True)
    blocks = prior_blocks.copy()
    blocks.loc[blocks.unified_block_id.eq("U096-BLK-044"), ["unified_block_member_count", "unified_edge_degree", "block_policy"]] = [3, 2, "no selection; X024 absolute-AUC diagnostic block with X004; later inner-fold-only comparison if separately authorized"]
    abs_meta = metadata[six_ids[4]]
    blocks.loc[len(blocks)] = {"unified_block_id": "U096-BLK-044", "candidate_id": six_ids[4], "candidate_group_id": abs_meta[0], "descriptor_family": abs_meta[1], "source_bank": "PRM100_full58_exact_permit", "technical_role": abs_meta[10], "later_evaluation_role": abs_meta[12], "unified_block_member_count": 3, "unified_edge_degree": 2, "representative_selected": False, "block_policy": "no selection; X024 absolute-AUC diagnostic block with X004; later inner-fold-only comparison if separately authorized"}
    for cid in six_ids:
        if cid == six_ids[4]:
            continue
        m = metadata[cid]
        blocks.loc[len(blocks)] = {"unified_block_id": m[7], "candidate_id": cid, "candidate_group_id": m[0], "descriptor_family": m[1], "source_bank": "PRM100_full58_exact_permit", "technical_role": m[10], "later_evaluation_role": m[12], "unified_block_member_count": 1, "unified_edge_degree": 0, "representative_selected": False, "block_policy": "standalone technical candidate; no selection in PRM101"}
    policy = pd.DataFrame([{"candidate_id": cid, "candidate_group_id": metadata[cid][0], "technical_disposition": "block_with_U096-BLK-044" if cid == six_ids[4] else "retain_likely_unselected", "unified_block_id": metadata[cid][7], "why": "two full58 high-redundancy X004 edges" if cid == six_ids[4] else "full58 finite coverage and no exact/proportional/high XREG redundancy", "selection_status": "not_selected", "y_access": False, "next_allowed_action": "no-y registry audit only; grouped predictive work requires separate authorization"} for cid in six_ids])
    qa = []
    def q(k: str, ok: bool, got: object, want: object) -> None: qa.append({"check_id": k, "status": "PASS" if ok else "FAIL", "observed": got, "expected": want})
    q("P101-01_bank", len(bank) == 114 and bank.candidate_id.nunique() == 114, len(bank), 114)
    q("P101-02_values", len(values) == 6612 and values[values.candidate_id.isin(six_ids)].value.notna().all() and values.value.notna().sum() == prior_values.value.notna().sum() + 348, f"{len(values)} rows/{values.value.notna().sum()} finite", "6612 rows/6610 finite; no new missingness")
    q("P101-03_wide", wide.shape == (58, 116) and wide[six_ids].notna().all().all() and wide.iloc[:, 2:].isna().sum().sum() == 2, f"{wide.shape}/NA={wide.iloc[:,2:].isna().sum().sum()}", "(58, 116)/2 inherited NA")
    q("P101-04_blocks", blocks.unified_block_id.nunique() == 94 and len(blocks) == 114, f"{blocks.unified_block_id.nunique()}/{len(blocks)}", "94/114")
    q("P101-05_edges", len(edges) == 25 and edges.edge_id.nunique() == 25, len(edges), 25)
    q("P101-06_block044", set(blocks.loc[blocks.unified_block_id.eq("U096-BLK-044"), "candidate_id"]) == {six_ids[4], "LIT-X004::chi_solid_26", "LIT-X004::chi_solid_26_per_mm3"}, "U096-BLK-044", "3 exact members")
    q("P101-07_no_selection", not bank.active_feature.any() and not bank.promoted.any() and not bank.y_evidence.any(), "all false", "all false")
    q("P101-08_new_values", values[values.candidate_id.isin(six_ids)].groupby("candidate_id").size().eq(58).all(), "6x58", "6x58")
    q("P101-09_policy", len(policy) == 6 and policy.selection_status.eq("not_selected").all(), len(policy), 6)
    q("P101-10_locks", all(v == 0 for v in contract["locks"].values()), contract["locks"], "all zero")
    failed = [x for x in qa if x["status"] != "PASS"]
    if failed:
        print(json.dumps(failed, indent=2))
        raise RuntimeError("producer QA failure")
    TABLES.mkdir(parents=True, exist_ok=True); FACTORY.joinpath("reports").mkdir(parents=True, exist_ok=True)
    bank.to_csv(TABLES / "PRM101_xreg_v0_3_candidate_bank.csv", index=False, encoding="utf-8-sig")
    values.to_csv(TABLES / "PRM101_xreg_v0_3_values_long.csv", index=False, encoding="utf-8-sig", float_format="%.17g")
    wide.to_csv(TABLES / "PRM101_xreg_v0_3_values_wide.csv", index=False, encoding="utf-8-sig", float_format="%.17g")
    edges.to_csv(TABLES / "PRM101_unified_redundancy_edge_registry.csv", index=False, encoding="utf-8-sig")
    blocks.to_csv(TABLES / "PRM101_unified_redundancy_block_registry.csv", index=False, encoding="utf-8-sig")
    policy.to_csv(TABLES / "PRM101_third_wave_block_policy.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(qa).to_csv(FACTORY / "reports" / "PRM101_producer_QA.csv", index=False, encoding="utf-8-sig")
    (FACTORY / "reports" / "PRM101_consolidation_summary.json").write_text(json.dumps({"status":"PASS","bank":"XREG-v0.3-TECHNICAL","candidates":114,"values":6612,"blocks":94,"edges":25,"y_fit_selection_promotion":"0/0/0/0"}, indent=2)+"\n", encoding="utf-8")
    print("PRM101 PASS: 114 candidates, 6612 values, 94 blocks, 25 edges")


if __name__ == "__main__": main()
