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
FACTORY = LAB / "factories" / "PRM-121"
CONTRACT = FACTORY / "contracts" / "PRM-121_XREG_V1_3_OVERLAY_PAIR_COMPONENT_COMPOSITION_CONSOLIDATION_CONTRACT_20260723.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1_048_576), b""):
            digest.update(chunk)
    return digest.hexdigest()


def graph(nodes: list[str], pairs: list[tuple[str, str]]) -> tuple[dict[str, list[str]], dict[str, int]]:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for left, right in pairs:
        adjacency[left].add(right)
        adjacency[right].add(left)
    seen: set[str] = set()
    members: dict[str, list[str]] = {}
    for root in sorted(nodes):
        if root in seen:
            continue
        stack, group = [root], []
        seen.add(root)
        while stack:
            node = stack.pop()
            group.append(node)
            for neighbour in sorted(adjacency[node]):
                if neighbour not in seen:
                    seen.add(neighbour)
                    stack.append(neighbour)
        for node in group:
            members[node] = sorted(group)
    return members, {node: len(adjacency[node]) for node in nodes}


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    expected = contract["expected"]
    for item in contract["inputs"]:
        if sha256(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError(f"input hash mismatch: {item['path']}")
    prior = pd.read_csv(TABLES / "PRM119_xreg_v1_2_candidate_bank.csv")
    prior_values = pd.read_csv(TABLES / "PRM119_xreg_v1_2_values_long.csv")
    prior_edges = pd.read_csv(TABLES / "PRM119_unified_redundancy_edge_registry.csv")
    prior_blocks = pd.read_csv(TABLES / "PRM119_unified_redundancy_block_registry.csv")
    cohort = pd.read_csv(TABLES / "PRM120_overlay_pair_component_composition_candidate_registry.csv")
    cohort_values = pd.read_csv(TABLES / "PRM120_overlay_pair_component_composition_values_long.csv")
    cross = pd.read_csv(TABLES / "PRM120_overlay_pair_component_composition_vs_XREG_v1_2_redundancy.csv")
    internal = pd.read_csv(TABLES / "PRM120_overlay_pair_component_composition_internal_redundancy.csv")
    cohort_ids, prior_ids = sorted(cohort.candidate_id), prior.candidate_id.tolist()
    include = contract["relation_policy"]["include_relations"]
    cross_selected = cross[cross.relation.isin(include)].sort_values(["candidate_id", "existing_candidate_id"])
    internal_selected = internal[internal.relation.isin(include)].sort_values(["left_candidate_id", "right_candidate_id"])
    if not (len(prior_ids) == expected["prior_candidates"] and len(cohort_ids) == expected["new_candidates"] and not (set(prior_ids) & set(cohort_ids)) and len(prior_values) == expected["prior_values"] and len(cohort_values) == expected["new_values"] and np.isfinite(cohort_values.value).all() and len(prior_edges) == expected["prior_edges"] and len(cross_selected) == expected["new_crossbank_edges"] and len(internal_selected) == expected["new_internal_edges"]):
        raise RuntimeError("scope mismatch")
    cross_edges = pd.DataFrame([{"edge_id": f"U121-EDGE-{n:03d}", "left_candidate_id": row.candidate_id, "right_candidate_id": row.existing_candidate_id, "relation": row.relation, "edge_source": "PRM120_pair_component_composition_crossbank_full58", "metric_note": f"Pearson={row.pearson:.6f}; Spearman={row.spearman:.6f}; residual={row.normalized_L2_residual:.3e}; no representative", "selection_rule": False} for n, row in enumerate(cross_selected.itertuples(index=False), expected["prior_edges"] + 1)])
    internal_edges = pd.DataFrame([{"edge_id": f"U121-EDGE-{n:03d}", "left_candidate_id": row.left_candidate_id, "right_candidate_id": row.right_candidate_id, "relation": row.relation, "edge_source": "PRM120_pair_component_composition_internal_full58", "metric_note": f"Pearson={row.pearson:.6f}; Spearman={row.spearman:.6f}; residual={row.normalized_L2_residual:.3e}; no representative", "selection_rule": False} for n, row in enumerate(internal_selected.itertuples(index=False), expected["prior_edges"] + len(cross_edges) + 1)])
    added = pd.concat([cross_edges, internal_edges], ignore_index=True)
    pairs = [(row.left_candidate_id, row.right_candidate_id) for row in prior_edges.itertuples(index=False)] + [(row.left_candidate_id, row.right_candidate_id) for row in added.itertuples(index=False)]
    members, degree = graph(prior_ids + cohort_ids, pairs)
    prior_block = prior.set_index("candidate_id").unified_block_id.to_dict()
    successor: dict[str, str] = {}
    changed_groups: list[list[str]] = []
    for group in {tuple(value) for value in members.values()}:
        inherited = {prior_block[candidate_id] for candidate_id in group if candidate_id in prior_block}
        has_new = any(candidate_id in cohort_ids for candidate_id in group)
        if not has_new and len(inherited) == 1:
            block_id = next(iter(inherited))
        else:
            block_id = ""
            changed_groups.append(sorted(group))
        for candidate_id in group:
            successor[candidate_id] = block_id
    for number, group in enumerate(sorted(changed_groups, key=lambda value: tuple(value)), 1):
        for candidate_id in group:
            successor[candidate_id] = f"U121-BLK-{number:03d}"
    changed_predecessors = sum(successor[candidate_id] != block_id for candidate_id, block_id in prior_block.items())
    if not (len(changed_groups) == expected["changed_or_new_components"] and len(set(successor.values())) == expected["total_blocks"] and changed_predecessors == expected["merged_predecessor_members"]):
        raise RuntimeError("graph projection mismatch")

    bank = prior.copy()
    bank["predecessor_unified_block_id"] = bank.unified_block_id
    bank["bank_version"] = "XREG-v1.3-TECHNICAL"
    bank["unified_block_id"] = bank.candidate_id.map(successor)
    bank["unified_block_member_count"] = bank.candidate_id.map(lambda candidate_id: len(members[candidate_id]))
    bank["unified_edge_degree"] = bank.candidate_id.map(degree)
    columns = bank.columns.tolist()
    source = cohort.set_index("candidate_id")
    rows = []
    for candidate_id in cohort_ids:
        entry = source.loc[candidate_id]
        values = cohort_values.loc[cohort_values.candidate_id.eq(candidate_id), "value"].to_numpy(float)
        rows.append({"bank_version": "XREG-v1.3-TECHNICAL", "candidate_id": candidate_id, "candidate_group_id": entry.candidate_group_id, "descriptor_family": entry.descriptor_family, "output_name": entry.output_name, "unit": entry.unit, "source_population": entry.source_population, "aggregation_formula": entry.aggregation_formula, "applicable_family": entry.applicable_family, "direct_or_derived": entry.direct_or_derived, "source_bank": "PRM120_overlay_pair_component_composition_batch", "source_value_table": "PRM120_overlay_pair_component_composition_values_long.csv", "technical_role": "batch_BC_candidate", "qualification_status": "full58_raw_table_batch_not_selected", "confidence_status": "confirmed_raw_table_lineage", "later_evaluation_role": "batch_BC_unselected_block_aware", "active_feature": False, "promoted": False, "y_evidence": False, "notes": "PRM120 overlay pair component composition cohort; no y, selection or promotion", "model_count": 58, "finite_count": int(np.isfinite(values).sum()), "unique_count": int(np.unique(values).size), "unified_block_id": successor[candidate_id], "unified_block_member_count": len(members[candidate_id]), "unified_edge_degree": degree[candidate_id], "operational_grade": entry.operational_grade, "literature_anchor": entry.literature_anchor, "anchor_scope": entry.anchor_scope, "predecessor_unified_block_id": pd.NA})
    bank = pd.concat([bank, pd.DataFrame(rows).reindex(columns=columns)], ignore_index=True)
    values = pd.concat([prior_values.assign(bank_version="XREG-v1.3-TECHNICAL"), cohort_values.assign(bank_version="XREG-v1.3-TECHNICAL", finite=True, source_bank="PRM120_overlay_pair_component_composition_batch")["bank_version model_id model_family candidate_id value finite source_bank".split()]], ignore_index=True)
    wide = values.pivot(index=["model_id", "model_family"], columns="candidate_id", values="value").reindex(columns=bank.candidate_id.tolist()).reset_index()
    edges = pd.concat([prior_edges, added.reindex(columns=prior_edges.columns)], ignore_index=True)
    blocks = prior_blocks.copy()
    blocks["predecessor_unified_block_id"] = blocks.unified_block_id
    blocks["unified_block_id"] = blocks.candidate_id.map(successor)
    blocks["unified_block_member_count"] = blocks.candidate_id.map(lambda candidate_id: len(members[candidate_id]))
    blocks["unified_edge_degree"] = blocks.candidate_id.map(degree)
    blocks["new_in_PRM121"] = False
    block_columns = blocks.columns.tolist()
    new_blocks = []
    for candidate_id in cohort_ids:
        entry = source.loc[candidate_id]
        group = members[candidate_id]
        new_blocks.append({"unified_block_id": successor[candidate_id], "predecessor_unified_block_id": pd.NA, "candidate_id": candidate_id, "candidate_group_id": entry.candidate_group_id, "descriptor_family": entry.descriptor_family, "source_bank": "PRM120_overlay_pair_component_composition_batch", "technical_role": "batch_BC_candidate", "later_evaluation_role": "batch_BC_unselected_block_aware", "unified_block_member_count": len(group), "unified_edge_degree": degree[candidate_id], "representative_selected": False, "block_policy": "standalone technical candidate; no selection in PRM121" if len(group) == 1 else "x-only graph block; no representative selected", "new_in_PRM121": True})
    blocks = pd.concat([blocks, pd.DataFrame(new_blocks).reindex(columns=block_columns)], ignore_index=True)
    policy = pd.DataFrame([{"candidate_id": candidate_id, "operational_grade": source.loc[candidate_id, "operational_grade"], "unified_block_id": successor[candidate_id], "block_status": "crossbank_high_redundancy_block" if any(member in prior_block for member in members[candidate_id]) else ("internal_high_redundancy_block" if len(members[candidate_id]) > 1 else "singleton"), "block_member_count": len(members[candidate_id]), "selection_status": "not_selected", "next_allowed_action": "future no-y batch or separately authorised block-aware grouped-y protocol"} for candidate_id in cohort_ids])
    checks = [("P121-01", len(bank) == 323 and bank.candidate_id.nunique() == 323, "323 candidates"), ("P121-02", len(values) == 18734 and int(values.value.notna().sum()) == 18732, "18,734 values and two inherited NA"), ("P121-03", wide.shape == (58, 325), "58x323 wide matrix"), ("P121-04", len(blocks) == 323 and blocks.unified_block_id.nunique() == 259, "259 graph blocks"), ("P121-05", len(edges) == 81 and edges.edge_id.nunique() == 81, "81 edges"), ("P121-06", len(cross_edges) == 3 and len(internal_edges) == 2 and cross_edges.relation.eq("high_redundancy").all() and internal_edges.relation.eq("high_redundancy").all(), "three crossbank plus two internal PRM120 edges"), ("P121-07", len(policy) == 24 and policy.block_status.value_counts().to_dict() == {"singleton": 17, "crossbank_high_redundancy_block": 3, "internal_high_redundancy_block": 4}, "24-candidate policy"), ("P121-08", not bank.active_feature.any() and not bank.promoted.any() and bank.y_evidence.astype(str).str.lower().eq("false").all(), "bank locks remain")]
    qa = pd.DataFrame([{"check_id": check_id, "status": "PASS" if passed else "FAIL", "detail": detail} for check_id, passed, detail in checks])
    if not qa.status.eq("PASS").all():
        raise RuntimeError(qa.to_dict(orient="records"))
    (FACTORY / "reports").mkdir(parents=True, exist_ok=True)
    for suffix, frame in {"candidate_bank": bank, "values_long": values, "values_wide": wide}.items():
        frame.to_csv(TABLES / f"PRM121_xreg_v1_3_{suffix}.csv", index=False, encoding="utf-8-sig", float_format="%.17g")
    edges.to_csv(TABLES / "PRM121_unified_redundancy_edge_registry.csv", index=False, encoding="utf-8-sig")
    blocks.to_csv(TABLES / "PRM121_unified_redundancy_block_registry.csv", index=False, encoding="utf-8-sig")
    policy.to_csv(TABLES / "PRM121_overlay_pair_component_composition_cohort_block_policy.csv", index=False, encoding="utf-8-sig")
    qa.to_csv(FACTORY / "reports" / "PRM121_producer_QA.csv", index=False, encoding="utf-8-sig")
    summary = {"status": "PASS", "checks": "8/8", "candidates": 323, "values": 18734, "finite_values": 18732, "blocks": 259, "edges": 81, "y_fit_selection_promotion": "0/0/0/0"}
    (FACTORY / "reports" / "PRM121_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
