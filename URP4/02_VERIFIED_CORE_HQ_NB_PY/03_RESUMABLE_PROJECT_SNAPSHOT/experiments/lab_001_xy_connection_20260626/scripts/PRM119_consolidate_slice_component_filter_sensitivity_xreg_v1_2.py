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
FACTORY = LAB / "factories" / "PRM-119"
CONTRACT = FACTORY / "contracts" / "PRM-119_XREG_V1_2_SLICE_COMPONENT_FILTER_SENSITIVITY_CONSOLIDATION_CONTRACT_20260723.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1_048_576), b""):
            digest.update(chunk)
    return digest.hexdigest()


def connected_components(nodes: list[str], pairs: list[tuple[str, str]]) -> tuple[dict[str, list[str]], dict[str, int]]:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for left, right in pairs:
        adjacency[left].add(right)
        adjacency[right].add(left)
    seen: set[str] = set()
    grouped: dict[str, list[str]] = {}
    for root in sorted(nodes):
        if root in seen:
            continue
        stack, group = [root], []
        seen.add(root)
        while stack:
            current = stack.pop()
            group.append(current)
            for neighbour in sorted(adjacency[current]):
                if neighbour not in seen:
                    seen.add(neighbour)
                    stack.append(neighbour)
        for member in group:
            grouped[member] = sorted(group)
    return grouped, {node: len(adjacency[node]) for node in nodes}


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    expected = contract["expected"]
    for item in contract["inputs"]:
        if sha256(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError(f"input hash mismatch: {item['path']}")

    prior = pd.read_csv(TABLES / "PRM117_xreg_v1_1_candidate_bank.csv")
    prior_values = pd.read_csv(TABLES / "PRM117_xreg_v1_1_values_long.csv")
    prior_edges = pd.read_csv(TABLES / "PRM117_unified_redundancy_edge_registry.csv")
    prior_blocks = pd.read_csv(TABLES / "PRM117_unified_redundancy_block_registry.csv")
    cohort = pd.read_csv(TABLES / "PRM118_slice_component_filter_sensitivity_candidate_registry.csv")
    cohort_values = pd.read_csv(TABLES / "PRM118_slice_component_filter_sensitivity_values_long.csv")
    crossbank = pd.read_csv(TABLES / "PRM118_slice_component_filter_sensitivity_vs_XREG_v1_1_redundancy.csv")

    cohort_ids = sorted(cohort.candidate_id)
    prior_ids = prior.candidate_id.tolist()
    selected = crossbank[crossbank.relation.isin(contract["relation_policy"]["include_relations"])].sort_values(["candidate_id", "existing_candidate_id"])
    scope_ok = (
        len(prior_ids) == expected["prior_candidates"]
        and len(cohort_ids) == expected["new_candidates"]
        and not (set(prior_ids) & set(cohort_ids))
        and len(prior_values) == expected["prior_values"]
        and len(cohort_values) == expected["new_values"]
        and np.isfinite(cohort_values.value).all()
        and len(prior_edges) == expected["prior_edges"]
        and len(selected) == expected["new_edges"]
    )
    if not scope_ok:
        raise RuntimeError("scope mismatch")

    additions = pd.DataFrame(
        [
            {
                "edge_id": f"U119-EDGE-{number:03d}",
                "left_candidate_id": row.candidate_id,
                "right_candidate_id": row.existing_candidate_id,
                "relation": row.relation,
                "edge_source": "PRM118_slice_component_filter_sensitivity_crossbank_full58",
                "metric_note": f"Pearson={row.pearson:.6f}; Spearman={row.spearman:.6f}; residual={row.normalized_L2_residual:.3e}; no representative",
                "selection_rule": False,
            }
            for number, row in enumerate(selected.itertuples(index=False), expected["prior_edges"] + 1)
        ]
    )
    pairs = [(row.left_candidate_id, row.right_candidate_id) for row in prior_edges.itertuples(index=False)]
    pairs += [(row.left_candidate_id, row.right_candidate_id) for row in additions.itertuples(index=False)]
    groups, degree = connected_components(prior_ids + cohort_ids, pairs)
    prior_block = prior.set_index("candidate_id").unified_block_id.to_dict()
    successor_block: dict[str, str] = {}
    changed_groups: list[list[str]] = []
    for group in {tuple(value) for value in groups.values()}:
        inherited = {prior_block[candidate_id] for candidate_id in group if candidate_id in prior_block}
        has_new = any(candidate_id in cohort_ids for candidate_id in group)
        if not has_new and len(inherited) == 1:
            assigned = next(iter(inherited))
        else:
            assigned = ""
            changed_groups.append(sorted(group))
        for candidate_id in group:
            successor_block[candidate_id] = assigned
    for number, group in enumerate(sorted(changed_groups, key=lambda members: tuple(members)), 1):
        for candidate_id in group:
            successor_block[candidate_id] = f"U119-BLK-{number:03d}"
    changed_predecessors = sum(successor_block[candidate_id] != old_id for candidate_id, old_id in prior_block.items())
    if len(changed_groups) != expected["changed_or_new_components"] or len(set(successor_block.values())) != expected["total_blocks"] or changed_predecessors != expected["merged_predecessor_members"]:
        raise RuntimeError("graph projection mismatch")

    bank = prior.copy()
    bank["predecessor_unified_block_id"] = bank.unified_block_id
    bank["bank_version"] = "XREG-v1.2-TECHNICAL"
    bank["unified_block_id"] = bank.candidate_id.map(successor_block)
    bank["unified_block_member_count"] = bank.candidate_id.map(lambda candidate_id: len(groups[candidate_id]))
    bank["unified_edge_degree"] = bank.candidate_id.map(degree)
    bank_columns = bank.columns.tolist()
    cohort_source = cohort.set_index("candidate_id")
    new_rows = []
    for candidate_id in cohort_ids:
        source = cohort_source.loc[candidate_id]
        candidate_values = cohort_values.loc[cohort_values.candidate_id.eq(candidate_id), "value"].to_numpy(float)
        new_rows.append(
            {
                "bank_version": "XREG-v1.2-TECHNICAL",
                "candidate_id": candidate_id,
                "candidate_group_id": source.candidate_group_id,
                "descriptor_family": source.descriptor_family,
                "output_name": source.output_name,
                "unit": source.unit,
                "source_population": source.source_population,
                "aggregation_formula": source.aggregation_formula,
                "applicable_family": source.applicable_family,
                "direct_or_derived": source.direct_or_derived,
                "source_bank": "PRM118_slice_component_filter_sensitivity_batch",
                "source_value_table": "PRM118_slice_component_filter_sensitivity_values_long.csv",
                "technical_role": "batch_BC_candidate",
                "qualification_status": "full58_raw_table_batch_not_selected",
                "confidence_status": "confirmed_raw_table_lineage",
                "later_evaluation_role": "batch_BC_unselected_block_aware",
                "active_feature": False,
                "promoted": False,
                "y_evidence": False,
                "notes": "PRM118 slice component filter sensitivity cohort; no y, selection or promotion",
                "model_count": 58,
                "finite_count": int(np.isfinite(candidate_values).sum()),
                "unique_count": int(np.unique(candidate_values).size),
                "unified_block_id": successor_block[candidate_id],
                "unified_block_member_count": len(groups[candidate_id]),
                "unified_edge_degree": degree[candidate_id],
                "operational_grade": source.operational_grade,
                "literature_anchor": source.literature_anchor,
                "anchor_scope": source.anchor_scope,
                "predecessor_unified_block_id": pd.NA,
            }
        )
    bank = pd.concat([bank, pd.DataFrame(new_rows).reindex(columns=bank_columns)], ignore_index=True)

    values = pd.concat(
        [
            prior_values.assign(bank_version="XREG-v1.2-TECHNICAL"),
            cohort_values.assign(bank_version="XREG-v1.2-TECHNICAL", finite=True, source_bank="PRM118_slice_component_filter_sensitivity_batch")["bank_version model_id model_family candidate_id value finite source_bank".split()],
        ],
        ignore_index=True,
    )
    wide = values.pivot(index=["model_id", "model_family"], columns="candidate_id", values="value").reindex(columns=bank.candidate_id.tolist()).reset_index()
    edges = pd.concat([prior_edges, additions.reindex(columns=prior_edges.columns)], ignore_index=True)

    blocks = prior_blocks.copy()
    blocks["predecessor_unified_block_id"] = blocks.unified_block_id
    blocks["unified_block_id"] = blocks.candidate_id.map(successor_block)
    blocks["unified_block_member_count"] = blocks.candidate_id.map(lambda candidate_id: len(groups[candidate_id]))
    blocks["unified_edge_degree"] = blocks.candidate_id.map(degree)
    blocks["new_in_PRM119"] = False
    block_columns = blocks.columns.tolist()
    new_blocks = []
    for candidate_id in cohort_ids:
        source = cohort_source.loc[candidate_id]
        members = groups[candidate_id]
        new_blocks.append(
            {
                "unified_block_id": successor_block[candidate_id],
                "predecessor_unified_block_id": pd.NA,
                "candidate_id": candidate_id,
                "candidate_group_id": source.candidate_group_id,
                "descriptor_family": source.descriptor_family,
                "source_bank": "PRM118_slice_component_filter_sensitivity_batch",
                "technical_role": "batch_BC_candidate",
                "later_evaluation_role": "batch_BC_unselected_block_aware",
                "unified_block_member_count": len(members),
                "unified_edge_degree": degree[candidate_id],
                "representative_selected": False,
                "block_policy": "standalone technical candidate; no selection in PRM119" if len(members) == 1 else "crossbank exact/high x-only block; no representative selected",
                "new_in_PRM119": True,
            }
        )
    blocks = pd.concat([blocks, pd.DataFrame(new_blocks).reindex(columns=block_columns)], ignore_index=True)
    policy = pd.DataFrame(
        [
            {
                "candidate_id": candidate_id,
                "operational_grade": cohort_source.loc[candidate_id, "operational_grade"],
                "unified_block_id": successor_block[candidate_id],
                "block_status": "crossbank_exact_or_high_redundancy_block" if any(member in prior_block for member in groups[candidate_id]) else "singleton",
                "block_member_count": len(groups[candidate_id]),
                "selection_status": "not_selected",
                "next_allowed_action": "future no-y batch or separately authorised block-aware grouped-y protocol",
            }
            for candidate_id in cohort_ids
        ]
    )
    checks = [
        ("P119-01", len(bank) == expected["total_candidates"] and bank.candidate_id.nunique() == expected["total_candidates"], "299 candidates"),
        ("P119-02", len(values) == expected["total_values"] and int(values.value.notna().sum()) == expected["finite_values"], "17,342 values and two inherited NA"),
        ("P119-03", wide.shape == (58, 301), "58x299 wide matrix"),
        ("P119-04", len(blocks) == expected["total_candidates"] and blocks.unified_block_id.nunique() == expected["total_blocks"], "240 graph blocks"),
        ("P119-05", len(edges) == expected["total_edges"] and edges.edge_id.nunique() == expected["total_edges"], "76 edges"),
        ("P119-06", len(additions) == expected["new_edges"] and additions.relation.value_counts().to_dict() == {"high_redundancy": 9, "exact_duplicate": 2}, "two exact and nine high declared PRM118 relations"),
        ("P119-07", len(policy) == 11 and policy.block_status.value_counts().to_dict() == {"crossbank_exact_or_high_redundancy_block": 6, "singleton": 5}, "11-candidate policy"),
        ("P119-08", not bank.active_feature.any() and not bank.promoted.any() and bank.y_evidence.astype(str).str.lower().eq("false").all(), "bank locks remain"),
    ]
    qa = pd.DataFrame([{"check_id": check_id, "status": "PASS" if passed else "FAIL", "detail": detail} for check_id, passed, detail in checks])
    if not qa.status.eq("PASS").all():
        raise RuntimeError(qa.to_dict(orient="records"))
    (FACTORY / "reports").mkdir(parents=True, exist_ok=True)
    for suffix, frame in {"candidate_bank": bank, "values_long": values, "values_wide": wide}.items():
        frame.to_csv(TABLES / f"PRM119_xreg_v1_2_{suffix}.csv", index=False, encoding="utf-8-sig", float_format="%.17g")
    edges.to_csv(TABLES / "PRM119_unified_redundancy_edge_registry.csv", index=False, encoding="utf-8-sig")
    blocks.to_csv(TABLES / "PRM119_unified_redundancy_block_registry.csv", index=False, encoding="utf-8-sig")
    policy.to_csv(TABLES / "PRM119_slice_component_filter_sensitivity_cohort_block_policy.csv", index=False, encoding="utf-8-sig")
    qa.to_csv(FACTORY / "reports" / "PRM119_producer_QA.csv", index=False, encoding="utf-8-sig")
    summary = {"status": "PASS", "checks": "8/8", "candidates": 299, "values": 17342, "finite_values": 17340, "blocks": 240, "edges": 76, "y_fit_selection_promotion": "0/0/0/0"}
    (FACTORY / "reports" / "PRM119_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
