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
FACTORY = LAB / "factories" / "PRM-111"
CONTRACT = FACTORY / "contracts" / "PRM-111_XREG_V0_8_AXIAL_SHAPE_ENTROPY_CONSOLIDATION_CONTRACT_20260723.json"
RELATIONS = {"exact_duplicate", "proportional_duplicate", "high_redundancy"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1_048_576), b""):
            digest.update(chunk)
    return digest.hexdigest()


def graph_components(nodes: list[str], edges: list[tuple[str, str]]) -> tuple[list[list[str]], dict[str, int]]:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    visited: set[str] = set()
    components: list[list[str]] = []
    for node in sorted(nodes):
        if node in visited:
            continue
        stack, group = [node], []
        visited.add(node)
        while stack:
            current = stack.pop()
            group.append(current)
            for neighbour in sorted(adjacency[current]):
                if neighbour not in visited:
                    visited.add(neighbour)
                    stack.append(neighbour)
        components.append(sorted(group))
    return components, {node: len(adjacency[node]) for node in nodes}


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    for item in contract["inputs"]:
        if sha256(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError(f"input hash mismatch: {item['path']}")

    prior_bank = pd.read_csv(TABLES / "PRM109_xreg_v0_7_candidate_bank.csv")
    prior_values = pd.read_csv(TABLES / "PRM109_xreg_v0_7_values_long.csv")
    prior_edges = pd.read_csv(TABLES / "PRM109_unified_redundancy_edge_registry.csv")
    prior_blocks = pd.read_csv(TABLES / "PRM109_unified_redundancy_block_registry.csv")
    cohort_registry = pd.read_csv(TABLES / "PRM110_axial_shape_entropy_candidate_registry.csv")
    cohort_values = pd.read_csv(TABLES / "PRM110_axial_shape_entropy_values_long.csv")
    cross = pd.read_csv(TABLES / "PRM110_axial_shape_entropy_vs_XREG_v0_7_redundancy.csv")
    internal = pd.read_csv(TABLES / "PRM110_axial_shape_entropy_internal_redundancy.csv")
    expected = contract["expected"]
    prior_ids = prior_bank["candidate_id"].tolist()
    cohort_ids = sorted(cohort_registry["candidate_id"].tolist())
    if len(prior_ids) != expected["prior_candidates"] or len(cohort_ids) != expected["new_candidates"] or set(prior_ids) & set(cohort_ids):
        raise RuntimeError("candidate scope/overlap mismatch")
    if len(prior_values) != expected["prior_values"] or len(cohort_values) != expected["new_values"] or not np.isfinite(cohort_values["value"].to_numpy(float)).all():
        raise RuntimeError("value scope mismatch")
    if len(prior_edges) != expected["prior_edges"] or prior_blocks["unified_block_id"].nunique() != expected["prior_blocks"]:
        raise RuntimeError("predecessor graph scope mismatch")

    cross_selected = cross[cross["relation"].isin(RELATIONS)].copy().sort_values(["candidate_id", "existing_candidate_id"])
    internal_selected = internal[internal["relation"].isin(RELATIONS)].copy().sort_values(["left_candidate_id", "right_candidate_id"])
    if cross_selected["relation"].value_counts().to_dict() != {"high_redundancy": 3} or internal_selected["relation"].value_counts().to_dict() != {"high_redundancy": 7}:
        raise RuntimeError("frozen PRM110 relation scope mismatch")
    new_edges: list[dict] = []
    for row in cross_selected.itertuples(index=False):
        new_edges.append({"left_candidate_id": str(row.candidate_id), "right_candidate_id": str(row.existing_candidate_id), "relation": str(row.relation), "edge_source": "PRM110_axial_shape_entropy_crossbank_full58", "metric_note": f"Pearson={float(row.pearson):.6f}; Spearman={float(row.spearman):.6f}; residual={float(row.normalized_L2_residual):.3e}; no representative", "selection_rule": False})
    for row in internal_selected.itertuples(index=False):
        new_edges.append({"left_candidate_id": str(row.left_candidate_id), "right_candidate_id": str(row.right_candidate_id), "relation": str(row.relation), "edge_source": "PRM110_axial_shape_entropy_internal_full58", "metric_note": f"Pearson={float(row.pearson):.6f}; Spearman={float(row.spearman):.6f}; residual={float(row.normalized_L2_residual):.3e}; no representative", "selection_rule": False})

    pairs = [(str(row.left_candidate_id), str(row.right_candidate_id)) for row in prior_edges.itertuples(index=False)]
    pairs += [(row["left_candidate_id"], row["right_candidate_id"]) for row in new_edges]
    groups, degree = graph_components(prior_ids + cohort_ids, pairs)
    prior_block = prior_bank.set_index("candidate_id")["unified_block_id"].to_dict()
    block_id: dict[str, str] = {}
    changed: list[list[str]] = []
    for group in groups:
        has_new = any(candidate in cohort_ids for candidate in group)
        inherited = {prior_block[candidate] for candidate in group if candidate in prior_block}
        if not has_new and len(inherited) == 1:
            assigned = next(iter(inherited))
        else:
            assigned = ""
            changed.append(group)
        for candidate in group:
            block_id[candidate] = assigned
    for number, group in enumerate(sorted(changed, key=lambda group: tuple(group)), start=1):
        for candidate in group:
            block_id[candidate] = f"U111-BLK-{number:03d}"
    if len(changed) != expected["changed_or_new_components"] or len(set(block_id.values())) != expected["total_blocks"]:
        raise RuntimeError("successor block projection mismatch")
    group_lookup = {candidate: group for group in groups for candidate in group}

    bank = prior_bank.copy()
    bank["predecessor_unified_block_id"] = bank["unified_block_id"]
    bank["bank_version"] = "XREG-v0.8-TECHNICAL"
    bank["unified_block_id"] = bank["candidate_id"].map(block_id)
    bank["unified_block_member_count"] = bank["candidate_id"].map(lambda candidate: len(group_lookup[candidate]))
    bank["unified_edge_degree"] = bank["candidate_id"].map(degree)
    columns = bank.columns.tolist()
    source_lookup = cohort_registry.set_index("candidate_id")
    rows: list[dict] = []
    for candidate in cohort_ids:
        source = source_lookup.loc[candidate]
        vector = cohort_values.loc[cohort_values["candidate_id"].eq(candidate), "value"].to_numpy(float)
        rows.append({"bank_version": "XREG-v0.8-TECHNICAL", "candidate_id": candidate, "candidate_group_id": source["candidate_group_id"], "descriptor_family": source["descriptor_family"], "output_name": source["output_name"], "unit": source["unit"], "source_population": source["source_population"], "aggregation_formula": source["aggregation_formula"], "applicable_family": source["applicable_family"], "direct_or_derived": source["direct_or_derived"], "source_bank": "PRM110_axial_shape_entropy_batch", "source_value_table": "PRM110_axial_shape_entropy_values_long.csv", "technical_role": "batch_BC_candidate", "qualification_status": "full58_raw_table_batch_not_selected", "confidence_status": "confirmed_raw_table_lineage", "later_evaluation_role": "batch_BC_unselected_block_aware", "active_feature": False, "promoted": False, "y_evidence": False, "notes": "PRM110 axial-position shape/entropy cohort; no y, selection or promotion", "model_count": 58, "finite_count": int(np.isfinite(vector).sum()), "unique_count": int(np.unique(vector).size), "unified_block_id": block_id[candidate], "unified_block_member_count": len(group_lookup[candidate]), "unified_edge_degree": degree[candidate], "operational_grade": source["operational_grade"], "literature_anchor": source["literature_anchor"], "anchor_scope": source["anchor_scope"], "predecessor_unified_block_id": pd.NA})
    bank = pd.concat([bank, pd.DataFrame(rows).reindex(columns=columns)], ignore_index=True)
    prior_out = prior_values.copy()
    prior_out["bank_version"] = "XREG-v0.8-TECHNICAL"
    new_out = cohort_values.assign(bank_version="XREG-v0.8-TECHNICAL", finite=True, source_bank="PRM110_axial_shape_entropy_batch")[["bank_version", "model_id", "model_family", "candidate_id", "value", "finite", "source_bank"]]
    values = pd.concat([prior_out, new_out], ignore_index=True)
    wide = values.pivot(index=["model_id", "model_family"], columns="candidate_id", values="value").reindex(columns=bank["candidate_id"].tolist()).reset_index()

    added = pd.DataFrame(new_edges)
    added.insert(0, "edge_id", [f"U111-EDGE-{number:03d}" for number in range(50, 60)])
    edges = pd.concat([prior_edges, added.reindex(columns=prior_edges.columns)], ignore_index=True)
    old_new107 = set(prior_blocks.loc[prior_blocks["new_in_PRM107"].astype(str).str.lower().eq("true"), "candidate_id"])
    old_new109 = set(prior_blocks.loc[prior_blocks["new_in_PRM109"].astype(str).str.lower().eq("true"), "candidate_id"])
    lookup = bank.set_index("candidate_id")
    blocks = pd.DataFrame([{"unified_block_id": block_id[candidate], "predecessor_unified_block_id": lookup.loc[candidate, "predecessor_unified_block_id"], "candidate_id": candidate, "candidate_group_id": lookup.loc[candidate, "candidate_group_id"], "descriptor_family": lookup.loc[candidate, "descriptor_family"], "source_bank": lookup.loc[candidate, "source_bank"], "technical_role": lookup.loc[candidate, "technical_role"], "later_evaluation_role": lookup.loc[candidate, "later_evaluation_role"], "unified_block_member_count": len(group_lookup[candidate]), "unified_edge_degree": degree[candidate], "representative_selected": False, "block_policy": "standalone technical candidate; no selection in PRM111" if len(group_lookup[candidate]) == 1 else "exact/proportional/high x-only block; no representative selected", "new_in_PRM107": candidate in old_new107, "new_in_PRM109": candidate in old_new109, "new_in_PRM111": candidate in cohort_ids} for candidate in bank["candidate_id"]])
    policy_rows = []
    for candidate in cohort_ids:
        group = group_lookup[candidate]
        has_prior = any(member in prior_block for member in group)
        policy_rows.append({"candidate_id": candidate, "operational_grade": source_lookup.loc[candidate, "operational_grade"], "unified_block_id": block_id[candidate], "block_status": "crossbank_high_redundancy_block" if has_prior else ("singleton" if len(group) == 1 else "internal_high_redundancy_block"), "block_member_count": len(group), "selection_status": "not_selected", "next_allowed_action": "future no-y batch or separately authorised block-aware grouped-y protocol"})
    policy = pd.DataFrame(policy_rows)

    qa: list[dict] = []
    def check(check_id: str, condition: bool, detail: str) -> None:
        qa.append({"check_id": check_id, "status": "PASS" if condition else "FAIL", "detail": detail})
    check("P111-01", len(bank) == expected["total_candidates"] and bank["candidate_id"].nunique() == expected["total_candidates"], "241 candidates")
    check("P111-02", len(values) == expected["total_values"] and int(values["value"].notna().sum()) == expected["finite_values"], "13,978 values and two inherited NA")
    check("P111-03", wide.shape == (58, 243), "58x241 wide matrix")
    check("P111-04", len(blocks) == expected["total_candidates"] and blocks["unified_block_id"].nunique() == expected["total_blocks"], "193 graph blocks")
    check("P111-05", len(edges) == expected["total_edges"] and edges["edge_id"].nunique() == expected["total_edges"], "59 edges")
    check("P111-06", len(added) == 10 and added["relation"].value_counts().to_dict() == {"high_redundancy": 10}, "ten declared PRM110 high relations")
    check("P111-07", len(policy) == 24 and policy["block_status"].value_counts().to_dict() == {"singleton": 16, "crossbank_high_redundancy_block": 3, "internal_high_redundancy_block": 5} and policy["selection_status"].eq("not_selected").all(), "24-candidate policy")
    check("P111-08", not bank["active_feature"].any() and not bank["promoted"].any() and bank["y_evidence"].astype(str).str.lower().eq("false").all(), "bank locks remain")
    qa_frame = pd.DataFrame(qa)
    if not qa_frame["status"].eq("PASS").all():
        raise RuntimeError(qa_frame.to_dict(orient="records"))
    TABLES.mkdir(parents=True, exist_ok=True)
    (FACTORY / "reports").mkdir(parents=True, exist_ok=True)
    bank.to_csv(TABLES / "PRM111_xreg_v0_8_candidate_bank.csv", index=False, encoding="utf-8-sig")
    values.to_csv(TABLES / "PRM111_xreg_v0_8_values_long.csv", index=False, encoding="utf-8-sig", float_format="%.17g")
    wide.to_csv(TABLES / "PRM111_xreg_v0_8_values_wide.csv", index=False, encoding="utf-8-sig", float_format="%.17g")
    edges.to_csv(TABLES / "PRM111_unified_redundancy_edge_registry.csv", index=False, encoding="utf-8-sig")
    blocks.to_csv(TABLES / "PRM111_unified_redundancy_block_registry.csv", index=False, encoding="utf-8-sig")
    policy.to_csv(TABLES / "PRM111_axial_shape_entropy_cohort_block_policy.csv", index=False, encoding="utf-8-sig")
    qa_frame.to_csv(FACTORY / "reports" / "PRM111_producer_QA.csv", index=False, encoding="utf-8-sig")
    summary = {"status": "PASS", "checks": "8/8", "candidates": 241, "values": 13978, "finite_values": 13976, "blocks": 193, "edges": 59, "y_fit_selection_promotion": "0/0/0/0"}
    (FACTORY / "reports" / "PRM111_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
