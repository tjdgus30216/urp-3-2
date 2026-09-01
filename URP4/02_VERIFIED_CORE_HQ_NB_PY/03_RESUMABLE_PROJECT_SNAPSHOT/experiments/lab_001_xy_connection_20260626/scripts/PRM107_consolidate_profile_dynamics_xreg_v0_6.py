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
FACTORY = LAB / "factories" / "PRM-107"
CONTRACT = FACTORY / "contracts" / "PRM-107_XREG_V0_6_PROFILE_DYNAMICS_CONSOLIDATION_CONTRACT_20260723.json"
REDUNDANCY_RELATIONS = {"exact_duplicate", "proportional_duplicate", "high_redundancy"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1_048_576), b""):
            digest.update(chunk)
    return digest.hexdigest()


def components(nodes: list[str], edges: list[tuple[str, str]]) -> tuple[list[list[str]], dict[str, int]]:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    visited: set[str] = set()
    groups: list[list[str]] = []
    for node in sorted(nodes):
        if node in visited:
            continue
        stack = [node]
        visited.add(node)
        group: list[str] = []
        while stack:
            current = stack.pop()
            group.append(current)
            for neighbour in sorted(adjacency[current]):
                if neighbour not in visited:
                    visited.add(neighbour)
                    stack.append(neighbour)
        groups.append(sorted(group))
    return groups, {node: len(adjacency[node]) for node in nodes}


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    for item in contract["inputs"]:
        if sha256(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError(f"input hash mismatch: {item['path']}")
    expected = contract["expected"]
    prior_bank = pd.read_csv(TABLES / "PRM105_xreg_v0_5_candidate_bank.csv")
    prior_values = pd.read_csv(TABLES / "PRM105_xreg_v0_5_values_long.csv")
    prior_edges = pd.read_csv(TABLES / "PRM105_unified_redundancy_edge_registry.csv")
    prior_blocks = pd.read_csv(TABLES / "PRM105_unified_redundancy_block_registry.csv")
    cohort_registry = pd.read_csv(TABLES / "PRM106_profile_dynamics_candidate_registry.csv")
    cohort_values = pd.read_csv(TABLES / "PRM106_profile_dynamics_values_long.csv")
    cross = pd.read_csv(TABLES / "PRM106_profile_dynamics_vs_XREG_v0_5_redundancy.csv")
    internal = pd.read_csv(TABLES / "PRM106_profile_dynamics_internal_redundancy.csv")
    prior_ids = prior_bank["candidate_id"].tolist()
    cohort_ids = sorted(cohort_registry["candidate_id"].tolist())
    if len(prior_ids) != 171 or len(cohort_ids) != 22 or set(prior_ids) & set(cohort_ids):
        raise RuntimeError("candidate scope/overlap mismatch")
    if len(prior_values) != 9918 or len(cohort_values) != 1276 or not np.isfinite(cohort_values["value"].to_numpy(float)).all():
        raise RuntimeError("value scope mismatch")

    cross_selected = cross[cross["relation"].isin(REDUNDANCY_RELATIONS)].copy().sort_values(["candidate_id", "existing_candidate_id"])
    internal_selected = internal[internal["relation"].isin(REDUNDANCY_RELATIONS)].copy().sort_values(["left_candidate_id", "right_candidate_id"])
    if cross_selected["relation"].value_counts().to_dict() != {"proportional_duplicate": 2}:
        raise RuntimeError("crossbank relation scope mismatch")
    if internal_selected["relation"].value_counts().to_dict() != {"exact_duplicate": 2, "high_redundancy": 1}:
        raise RuntimeError("internal relation scope mismatch")

    new_edge_rows: list[dict] = []
    for row in cross_selected.itertuples(index=False):
        new_edge_rows.append({"left_candidate_id": str(row.candidate_id), "right_candidate_id": str(row.existing_candidate_id), "relation": str(row.relation), "edge_source": "PRM106_profile_dynamics_crossbank_full58", "metric_note": f"Pearson={float(row.pearson):.6f}; Spearman={float(row.spearman):.6f}; residual={float(row.normalized_L2_residual):.3e}; no representative", "selection_rule": False})
    for row in internal_selected.itertuples(index=False):
        new_edge_rows.append({"left_candidate_id": str(row.left_candidate_id), "right_candidate_id": str(row.right_candidate_id), "relation": str(row.relation), "edge_source": "PRM106_profile_dynamics_internal_full58", "metric_note": f"Pearson={float(row.pearson):.6f}; Spearman={float(row.spearman):.6f}; residual={float(row.normalized_L2_residual):.3e}; no representative", "selection_rule": False})
    predecessor_pairs = [(str(row.left_candidate_id), str(row.right_candidate_id)) for row in prior_edges.itertuples(index=False)]
    graph_pairs = predecessor_pairs + [(row["left_candidate_id"], row["right_candidate_id"]) for row in new_edge_rows]
    all_ids = prior_ids + cohort_ids
    groups, degree = components(all_ids, graph_pairs)
    old_block = prior_bank.set_index("candidate_id")["unified_block_id"].to_dict()
    component_lookup = {candidate_id: group for group in groups for candidate_id in group}
    block_id: dict[str, str] = {}
    changed: list[list[str]] = []
    for group in groups:
        has_new = any(candidate_id in cohort_ids for candidate_id in group)
        predecessor_ids = {old_block[candidate_id] for candidate_id in group if candidate_id in old_block}
        if not has_new and len(predecessor_ids) == 1:
            assigned = next(iter(predecessor_ids))
        else:
            assigned = ""
            changed.append(group)
        for candidate_id in group:
            block_id[candidate_id] = assigned
    for number, group in enumerate(sorted(changed, key=lambda item: tuple(item)), start=1):
        for candidate_id in group:
            block_id[candidate_id] = f"U107-BLK-{number:03d}"
    if len(changed) != 19 or len(set(block_id.values())) != 152:
        raise RuntimeError("successor block projection mismatch")

    bank = prior_bank.copy()
    bank["predecessor_unified_block_id"] = bank["unified_block_id"]
    bank["bank_version"] = "XREG-v0.6-TECHNICAL"
    bank["unified_block_id"] = bank["candidate_id"].map(block_id)
    bank["unified_block_member_count"] = bank["candidate_id"].map(lambda candidate_id: len(component_lookup[candidate_id]))
    bank["unified_edge_degree"] = bank["candidate_id"].map(degree)
    columns = bank.columns.tolist()
    cohort_lookup = cohort_registry.set_index("candidate_id")
    rows: list[dict] = []
    for candidate_id in cohort_ids:
        source = cohort_lookup.loc[candidate_id]
        candidate_values = cohort_values[cohort_values["candidate_id"].eq(candidate_id)]["value"].to_numpy(float)
        rows.append({
            "bank_version": "XREG-v0.6-TECHNICAL", "candidate_id": candidate_id, "candidate_group_id": source["candidate_group_id"], "descriptor_family": source["descriptor_family"], "output_name": source["output_name"], "unit": source["unit"], "source_population": source["source_population"], "aggregation_formula": source["aggregation_formula"], "applicable_family": source["applicable_family"], "direct_or_derived": source["direct_or_derived"], "source_bank": "PRM106_profile_dynamics_batch", "source_value_table": "PRM106_profile_dynamics_values_long.csv", "technical_role": "batch_BC_candidate", "qualification_status": "full58_raw_table_batch_not_selected", "confidence_status": "confirmed_raw_table_lineage", "later_evaluation_role": "batch_BC_unselected_block_aware", "active_feature": False, "promoted": False, "y_evidence": False, "notes": "PRM106 profile-dynamics cohort; no y, selection or promotion", "model_count": 58, "finite_count": int(np.isfinite(candidate_values).sum()), "unique_count": int(np.unique(candidate_values).size), "unified_block_id": block_id[candidate_id], "unified_block_member_count": len(component_lookup[candidate_id]), "unified_edge_degree": degree[candidate_id], "operational_grade": source["operational_grade"], "literature_anchor": source["literature_anchor"], "anchor_scope": source["anchor_scope"], "predecessor_unified_block_id": pd.NA,
        })
    bank = pd.concat([bank, pd.DataFrame(rows).reindex(columns=columns)], ignore_index=True)

    prior_out = prior_values.copy()
    prior_out["bank_version"] = "XREG-v0.6-TECHNICAL"
    family = prior_out[["model_id", "model_family"]].drop_duplicates().set_index("model_id")["model_family"].to_dict()
    new_out = cohort_values.assign(bank_version="XREG-v0.6-TECHNICAL", model_family=cohort_values["model_id"].map(family), finite=True, source_bank="PRM106_profile_dynamics_batch")[["bank_version", "model_id", "model_family", "candidate_id", "value", "finite", "source_bank"]]
    values = pd.concat([prior_out, new_out], ignore_index=True)
    wide = values.pivot(index=["model_id", "model_family"], columns="candidate_id", values="value").reindex(columns=bank["candidate_id"].tolist()).reset_index()

    added = pd.DataFrame(new_edge_rows)
    added.insert(0, "edge_id", [f"U107-EDGE-{number:03d}" for number in range(44, 49)])
    edges = pd.concat([prior_edges, added.reindex(columns=prior_edges.columns)], ignore_index=True)
    bank_lookup = bank.set_index("candidate_id")
    block_rows: list[dict] = []
    for candidate_id in bank["candidate_id"]:
        source = bank_lookup.loc[candidate_id]
        member_count = len(component_lookup[candidate_id])
        if member_count == 1:
            policy = "standalone technical candidate; no selection in PRM107"
        else:
            policy = "exact/proportional/high x-only block; no representative selected"
        block_rows.append({"unified_block_id": block_id[candidate_id], "predecessor_unified_block_id": source["predecessor_unified_block_id"], "candidate_id": candidate_id, "candidate_group_id": source["candidate_group_id"], "descriptor_family": source["descriptor_family"], "source_bank": source["source_bank"], "technical_role": source["technical_role"], "later_evaluation_role": source["later_evaluation_role"], "unified_block_member_count": member_count, "unified_edge_degree": degree[candidate_id], "representative_selected": False, "block_policy": policy, "new_in_PRM107": bool(candidate_id in cohort_ids)})
    blocks = pd.DataFrame(block_rows)
    policy_rows = []
    for candidate_id in cohort_ids:
        group = component_lookup[candidate_id]
        has_prior = any(member in old_block for member in group)
        relations = {row["relation"] for row in new_edge_rows if candidate_id in {row["left_candidate_id"], row["right_candidate_id"]}}
        if len(group) == 1:
            status = "singleton"
        elif has_prior:
            status = "crossbank_proportional_block"
        elif "exact_duplicate" in relations:
            status = "internal_exact_block"
        else:
            status = "internal_high_redundancy_block"
        policy_rows.append({"candidate_id": candidate_id, "operational_grade": cohort_lookup.loc[candidate_id, "operational_grade"], "unified_block_id": block_id[candidate_id], "block_status": status, "block_member_count": len(group), "selection_status": "not_selected", "next_allowed_action": "future no-y batch or separately authorised block-aware grouped-y protocol"})
    policy = pd.DataFrame(policy_rows)

    qa = []
    def check(check_id: str, condition: bool, detail: str) -> None:
        qa.append({"check_id": check_id, "status": "PASS" if condition else "FAIL", "detail": detail})
    check("P107-01", len(bank) == 193 and bank["candidate_id"].nunique() == 193, "193 candidates")
    check("P107-02", len(values) == 11194 and int(values["value"].notna().sum()) == 11192, "11,194 values and two inherited NA")
    check("P107-03", wide.shape == (58, 195), "58x193 wide matrix")
    check("P107-04", len(blocks) == 193 and blocks["unified_block_id"].nunique() == 152, "152 graph blocks")
    check("P107-05", len(edges) == 48 and edges["edge_id"].nunique() == 48, "48 edges")
    check("P107-06", len(added) == 5 and added["relation"].value_counts().to_dict() == {"proportional_duplicate": 2, "exact_duplicate": 2, "high_redundancy": 1}, "five declared PRM106 relations")
    check("P107-07", len(policy) == 22 and policy["selection_status"].eq("not_selected").all(), "22 unselected cohort candidates")
    check("P107-08", not bank["active_feature"].any() and not bank["promoted"].any() and bank["y_evidence"].astype(str).str.lower().eq("false").all(), "bank locks remain")
    if not all(row["status"] == "PASS" for row in qa):
        raise RuntimeError(qa)
    TABLES.mkdir(parents=True, exist_ok=True)
    (FACTORY / "reports").mkdir(parents=True, exist_ok=True)
    bank.to_csv(TABLES / "PRM107_xreg_v0_6_candidate_bank.csv", index=False, encoding="utf-8-sig")
    values.to_csv(TABLES / "PRM107_xreg_v0_6_values_long.csv", index=False, encoding="utf-8-sig", float_format="%.17g")
    wide.to_csv(TABLES / "PRM107_xreg_v0_6_values_wide.csv", index=False, encoding="utf-8-sig", float_format="%.17g")
    edges.to_csv(TABLES / "PRM107_unified_redundancy_edge_registry.csv", index=False, encoding="utf-8-sig")
    blocks.to_csv(TABLES / "PRM107_unified_redundancy_block_registry.csv", index=False, encoding="utf-8-sig")
    policy.to_csv(TABLES / "PRM107_profile_dynamics_cohort_block_policy.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(qa).to_csv(FACTORY / "reports" / "PRM107_producer_QA.csv", index=False, encoding="utf-8-sig")
    summary = {"status": "PASS", "checks": "8/8", "candidates": 193, "values": 11194, "finite_values": 11192, "blocks": 152, "edges": 48, "y_fit_selection_promotion": "0/0/0/0"}
    (FACTORY / "reports" / "PRM107_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
