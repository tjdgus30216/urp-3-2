from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
TABLES = LAB / "reports" / "tables"
FACTORY = LAB / "factories" / "PRM-113"
CONTRACT = FACTORY / "contracts" / "PRM-113_XREG_V0_9_WEIGHTED_QUANTILE_LOCATION_CONSOLIDATION_CONTRACT_20260723.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1_048_576), b""):
            digest.update(chunk)
    return digest.hexdigest()


def components(nodes: list[str], pairs: list[tuple[str, str]]) -> tuple[dict[str, list[str]], dict[str, int]]:
    adjacent: dict[str, set[str]] = defaultdict(set)
    for left, right in pairs:
        adjacent[left].add(right); adjacent[right].add(left)
    seen, lookup = set(), {}
    for root in sorted(nodes):
        if root in seen: continue
        stack, group = [root], []
        seen.add(root)
        while stack:
            current = stack.pop(); group.append(current)
            for neighbour in sorted(adjacent[current]):
                if neighbour not in seen: seen.add(neighbour); stack.append(neighbour)
        group = sorted(group)
        for member in group: lookup[member] = group
    return lookup, {node: len(adjacent[node]) for node in nodes}


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8")); expected = contract["expected"]
    for item in contract["inputs"]:
        if sha256(ROOT / item["path"]) != item["sha256"]: raise RuntimeError(f"input hash mismatch: {item['path']}")
    prior_bank = pd.read_csv(TABLES / "PRM111_xreg_v0_8_candidate_bank.csv")
    prior_values = pd.read_csv(TABLES / "PRM111_xreg_v0_8_values_long.csv")
    prior_edges = pd.read_csv(TABLES / "PRM111_unified_redundancy_edge_registry.csv")
    prior_blocks = pd.read_csv(TABLES / "PRM111_unified_redundancy_block_registry.csv")
    cohort_bank = pd.read_csv(TABLES / "PRM112_axial_weighted_quantile_location_candidate_registry.csv")
    cohort_values = pd.read_csv(TABLES / "PRM112_axial_weighted_quantile_location_values_long.csv")
    internal = pd.read_csv(TABLES / "PRM112_axial_weighted_quantile_location_internal_redundancy.csv")
    prior_ids, cohort_ids = prior_bank.candidate_id.tolist(), sorted(cohort_bank.candidate_id.tolist())
    if len(prior_ids)!=expected["prior_candidates"] or len(cohort_ids)!=expected["new_candidates"] or set(prior_ids)&set(cohort_ids): raise RuntimeError("candidate scope mismatch")
    if len(prior_values)!=expected["prior_values"] or len(cohort_values)!=expected["new_values"] or not np.isfinite(cohort_values.value).all(): raise RuntimeError("value scope mismatch")
    selected = internal[internal.relation.eq("high_redundancy")].sort_values(["left_candidate_id","right_candidate_id"])
    if len(selected)!=1: raise RuntimeError("frozen PRM112 relation scope mismatch")
    row=selected.iloc[0]
    added = pd.DataFrame([{"edge_id":"U113-EDGE-060", "left_candidate_id":str(row.left_candidate_id), "right_candidate_id":str(row.right_candidate_id), "relation":str(row.relation), "edge_source":"PRM112_axial_weighted_quantile_location_internal_full58", "metric_note":f"Pearson={float(row.pearson):.6f}; Spearman={float(row.spearman):.6f}; residual={float(row.normalized_L2_residual):.3e}; no representative", "selection_rule":False}])
    all_pairs=[(str(r.left_candidate_id),str(r.right_candidate_id)) for r in prior_edges.itertuples(index=False)]+[(str(row.left_candidate_id),str(row.right_candidate_id))]
    groups, degree=components(prior_ids+cohort_ids,all_pairs)
    prior_block=prior_bank.set_index("candidate_id").unified_block_id.to_dict()
    new_groups=sorted({tuple(groups[candidate]) for candidate in cohort_ids}, key=lambda x:x)
    if len(new_groups)!=expected["new_components"]: raise RuntimeError("new component count mismatch")
    block_id=dict(prior_block)
    for number, group in enumerate(new_groups,1):
        for candidate in group: block_id[candidate]=f"U113-BLK-{number:03d}"
    if len(set(block_id.values()))!=expected["total_blocks"]: raise RuntimeError("block count mismatch")
    bank=prior_bank.copy(); bank["predecessor_unified_block_id"]=bank["unified_block_id"]; bank["bank_version"]="XREG-v0.9-TECHNICAL"; bank["unified_block_member_count"]=bank.candidate_id.map(lambda c:len(groups[c])); bank["unified_edge_degree"]=bank.candidate_id.map(degree)
    source=cohort_bank.set_index("candidate_id"); cols=bank.columns.tolist(); rows=[]
    for cid in cohort_ids:
        s=source.loc[cid]; vector=cohort_values.loc[cohort_values.candidate_id.eq(cid),"value"].to_numpy(float)
        rows.append({"bank_version":"XREG-v0.9-TECHNICAL","candidate_id":cid,"candidate_group_id":s.candidate_group_id,"descriptor_family":s.descriptor_family,"output_name":s.output_name,"unit":s.unit,"source_population":s.source_population,"aggregation_formula":s.aggregation_formula,"applicable_family":s.applicable_family,"direct_or_derived":s.direct_or_derived,"source_bank":"PRM112_axial_weighted_quantile_location_batch","source_value_table":"PRM112_axial_weighted_quantile_location_values_long.csv","technical_role":"batch_B_candidate","qualification_status":"full58_raw_table_batch_not_selected","confidence_status":"confirmed_raw_table_lineage","later_evaluation_role":"batch_B_unselected_block_aware","active_feature":False,"promoted":False,"y_evidence":False,"notes":"PRM112 weighted axial quantile-location cohort; no y, selection or promotion","model_count":58,"finite_count":int(np.isfinite(vector).sum()),"unique_count":int(np.unique(vector).size),"unified_block_id":block_id[cid],"unified_block_member_count":len(groups[cid]),"unified_edge_degree":degree[cid],"operational_grade":s.operational_grade,"literature_anchor":s.literature_anchor,"anchor_scope":s.anchor_scope,"predecessor_unified_block_id":pd.NA})
    bank=pd.concat([bank,pd.DataFrame(rows).reindex(columns=cols)],ignore_index=True)
    values=pd.concat([prior_values.assign(bank_version="XREG-v0.9-TECHNICAL"),cohort_values.assign(bank_version="XREG-v0.9-TECHNICAL",finite=True,source_bank="PRM112_axial_weighted_quantile_location_batch")[["bank_version","model_id","model_family","candidate_id","value","finite","source_bank"]]],ignore_index=True)
    wide=values.pivot(index=["model_id","model_family"],columns="candidate_id",values="value").reindex(columns=bank.candidate_id.tolist()).reset_index()
    edges=pd.concat([prior_edges,added.reindex(columns=prior_edges.columns)],ignore_index=True)
    old=prior_blocks.copy(); old["predecessor_unified_block_id"]=old["unified_block_id"]; old["new_in_PRM113"]=False; old["unified_block_member_count"]=old.candidate_id.map(lambda c:len(groups[c])); old["unified_edge_degree"]=old.candidate_id.map(degree)
    block_rows=[]
    for cid in cohort_ids:
        s=source.loc[cid]; group=groups[cid]
        block_rows.append({"unified_block_id":block_id[cid],"predecessor_unified_block_id":pd.NA,"candidate_id":cid,"candidate_group_id":s.candidate_group_id,"descriptor_family":s.descriptor_family,"source_bank":"PRM112_axial_weighted_quantile_location_batch","technical_role":"batch_B_candidate","later_evaluation_role":"batch_B_unselected_block_aware","unified_block_member_count":len(group),"unified_edge_degree":degree[cid],"representative_selected":False,"block_policy":"standalone technical candidate; no selection in PRM113" if len(group)==1 else "high x-only block; no representative selected","new_in_PRM107":False,"new_in_PRM109":False,"new_in_PRM111":False,"new_in_PRM113":True})
    blocks=pd.concat([old,pd.DataFrame(block_rows).reindex(columns=old.columns)],ignore_index=True)
    policy=pd.DataFrame([{"candidate_id":cid,"operational_grade":"B","unified_block_id":block_id[cid],"block_status":"singleton" if len(groups[cid])==1 else "internal_high_redundancy_block","block_member_count":len(groups[cid]),"selection_status":"not_selected","next_allowed_action":"future no-y batch or separately authorised block-aware grouped-y protocol"} for cid in cohort_ids])
    qa=[]
    def check(i,ok,d):qa.append({"check_id":i,"status":"PASS" if ok else "FAIL","detail":d})
    check("P113-01",len(bank)==265 and bank.candidate_id.nunique()==265,"265 candidates")
    check("P113-02",len(values)==15370 and int(values.value.notna().sum())==15368,"15,370 values and two inherited NA")
    check("P113-03",wide.shape==(58,267),"58x265 wide matrix")
    check("P113-04",len(blocks)==265 and blocks.unified_block_id.nunique()==216,"216 graph blocks")
    check("P113-05",len(edges)==60 and edges.edge_id.nunique()==60,"60 edges")
    check("P113-06",len(added)==1 and added.relation.iloc[0]=="high_redundancy","one declared PRM112 high relation")
    check("P113-07",len(policy)==24 and policy.block_status.value_counts().to_dict()=={"singleton":22,"internal_high_redundancy_block":2} and policy.selection_status.eq("not_selected").all(),"24-candidate policy")
    check("P113-08",not bank.active_feature.any() and not bank.promoted.any() and bank.y_evidence.astype(str).str.lower().eq("false").all(),"bank locks remain")
    qa=pd.DataFrame(qa)
    if not qa.status.eq("PASS").all(): raise RuntimeError(qa.to_dict(orient="records"))
    (FACTORY/"reports").mkdir(parents=True,exist_ok=True)
    for suffix,frame in {"candidate_bank":bank,"values_long":values,"values_wide":wide,"unified_redundancy_edge_registry":edges,"unified_redundancy_block_registry":blocks,"weighted_quantile_location_cohort_block_policy":policy}.items(): frame.to_csv(TABLES/f"PRM113_xreg_v0_9_{suffix}.csv" if suffix in {"candidate_bank","values_long","values_wide"} else TABLES/f"PRM113_{suffix}.csv",index=False,encoding="utf-8-sig",float_format="%.17g")
    qa.to_csv(FACTORY/"reports"/"PRM113_producer_QA.csv",index=False,encoding="utf-8-sig")
    summary={"status":"PASS","checks":"8/8","candidates":265,"values":15370,"finite_values":15368,"blocks":216,"edges":60,"y_fit_selection_promotion":"0/0/0/0"}
    (FACTORY/"reports"/"PRM113_summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8"); print(json.dumps(summary,indent=2))


if __name__=="__main__":main()
