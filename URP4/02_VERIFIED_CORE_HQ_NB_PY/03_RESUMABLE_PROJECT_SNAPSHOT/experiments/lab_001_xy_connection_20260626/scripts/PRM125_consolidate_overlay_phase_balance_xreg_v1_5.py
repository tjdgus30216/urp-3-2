from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "experiments/lab_001_xy_connection_20260626/reports/tables"
OUT = ROOT / "experiments/lab_001_xy_connection_20260626/factories/PRM-125"
OUT.mkdir(parents=True, exist_ok=True)


def components(nodes: list[str], edge_pairs: list[tuple[str, str]]) -> tuple[dict[str, list[str]], dict[str, int]]:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for left, right in edge_pairs:
        adjacency[left].add(right)
        adjacency[right].add(left)
    seen: set[str] = set()
    membership: dict[str, list[str]] = {}
    for root in sorted(nodes):
        if root in seen:
            continue
        stack, group = [root], []
        seen.add(root)
        while stack:
            current = stack.pop()
            group.append(current)
            for neighbor in adjacency[current]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        for member in group:
            membership[member] = group
    return membership, {node: len(adjacency[node]) for node in nodes}


def main() -> None:
    prior = pd.read_csv(TABLES / "PRM123_xreg_v1_4_candidate_bank.csv")
    prior_values = pd.read_csv(TABLES / "PRM123_xreg_v1_4_values_long.csv")
    prior_edges = pd.read_csv(TABLES / "PRM123_unified_redundancy_edge_registry.csv")
    cohort = pd.read_csv(TABLES / "PRM124_overlay_phase_balance_candidate_registry.csv")
    cohort_values = pd.read_csv(TABLES / "PRM124_overlay_phase_balance_values_long.csv")
    internal = pd.read_csv(TABLES / "PRM124_overlay_phase_balance_internal_redundancy.csv")
    cohort_ids = sorted(cohort.candidate_id.tolist())
    selected_internal = internal.loc[internal.relation.eq("high_redundancy")].copy()
    added_edges = pd.DataFrame([
        {
            "edge_id": f"U125-EDGE-{number:03d}",
            "left_candidate_id": row.left_candidate_id,
            "right_candidate_id": row.right_candidate_id,
            "relation": "high_redundancy",
            "edge_source": "PRM124_xonly",
            "metric_note": "no representative",
            "selection_rule": False,
        }
        for number, row in enumerate(selected_internal.itertuples(index=False), start=87)
    ])
    all_edges = pd.concat([prior_edges, added_edges.reindex(columns=prior_edges.columns)], ignore_index=True)
    all_ids = prior.candidate_id.tolist() + cohort_ids
    membership, degree = components(all_ids, [(row.left_candidate_id, row.right_candidate_id) for row in all_edges.itertuples(index=False)])
    prior_blocks = prior.set_index("candidate_id").unified_block_id.to_dict()
    block_id: dict[str, str] = {}
    new_groups: list[list[str]] = []
    for group in {tuple(sorted(value)) for value in membership.values()}:
        inherited = {prior_blocks[candidate] for candidate in group if candidate in prior_blocks}
        if not any(candidate in cohort_ids for candidate in group) and len(inherited) == 1:
            chosen = next(iter(inherited))
            for candidate in group:
                block_id[candidate] = chosen
        else:
            new_groups.append(list(group))
    for number, group in enumerate(sorted(new_groups), start=1):
        for candidate in group:
            block_id[candidate] = f"U125-BLK-{number:03d}"

    bank = prior.copy()
    bank["predecessor_unified_block_id"] = bank.unified_block_id
    bank["bank_version"] = "XREG-v1.5-TECHNICAL"
    bank["unified_block_id"] = bank.candidate_id.map(block_id)
    bank["unified_block_member_count"] = bank.candidate_id.map(lambda candidate: len(membership[candidate]))
    bank["unified_edge_degree"] = bank.candidate_id.map(degree)
    columns = bank.columns.tolist()
    metadata = cohort.set_index("candidate_id")
    appended = []
    for candidate in cohort_ids:
        source = metadata.loc[candidate]
        values = cohort_values.loc[cohort_values.candidate_id.eq(candidate), "value"].to_numpy(float)
        appended.append({
            "bank_version": "XREG-v1.5-TECHNICAL",
            "candidate_id": candidate,
            "candidate_group_id": source.candidate_group_id,
            "descriptor_family": source.descriptor_family,
            "output_name": source.output_name,
            "unit": source.unit,
            "source_population": source.source_population,
            "aggregation_formula": source.aggregation_formula,
            "applicable_family": source.applicable_family,
            "direct_or_derived": source.direct_or_derived,
            "source_bank": "PRM124_overlay_phase_balance_batch",
            "source_value_table": "PRM124_overlay_phase_balance_values_long.csv",
            "technical_role": "batch_BC_candidate",
            "qualification_status": "full58_raw_table_batch_not_selected",
            "confidence_status": "confirmed_raw_table_lineage",
            "later_evaluation_role": "batch_BC_unselected_block_aware",
            "active_feature": False,
            "promoted": False,
            "y_evidence": False,
            "notes": "PRM124 no y",
            "model_count": 58,
            "finite_count": int(np.isfinite(values).sum()),
            "unique_count": len(np.unique(values)),
            "unified_block_id": block_id[candidate],
            "unified_block_member_count": len(membership[candidate]),
            "unified_edge_degree": degree[candidate],
            "operational_grade": source.operational_grade,
            "literature_anchor": source.literature_anchor,
            "anchor_scope": source.anchor_scope,
            "predecessor_unified_block_id": pd.NA,
        })
    bank = pd.concat([bank, pd.DataFrame(appended).reindex(columns=columns)], ignore_index=True)
    values = pd.concat([
        prior_values.assign(bank_version="XREG-v1.5-TECHNICAL"),
        cohort_values.assign(bank_version="XREG-v1.5-TECHNICAL", finite=True, source_bank="PRM124_overlay_phase_balance_batch")[
            ["bank_version", "model_id", "model_family", "candidate_id", "value", "finite", "source_bank"]
        ],
    ], ignore_index=True)
    wide = values.pivot(index=["model_id", "model_family"], columns="candidate_id", values="value").reindex(columns=bank.candidate_id.tolist()).reset_index()
    bank.to_csv(TABLES / "PRM125_xreg_v1_5_candidate_bank.csv", index=False, encoding="utf-8-sig")
    values.to_csv(TABLES / "PRM125_xreg_v1_5_values_long.csv", index=False, encoding="utf-8-sig")
    wide.to_csv(TABLES / "PRM125_xreg_v1_5_values_wide.csv", index=False, encoding="utf-8-sig")
    all_edges.to_csv(TABLES / "PRM125_unified_redundancy_edge_registry.csv", index=False, encoding="utf-8-sig")
    qa = pd.DataFrame([{
        "check_id": "P125-01",
        "status": "PASS" if len(bank) == 365 and len(values) == 21170 and values.value.notna().sum() == 21168 and len(all_edges) == 88 and len(set(block_id.values())) == 294 else "FAIL",
        "detail": "scope, inherited missingness, edge and block totals",
    }])
    qa.to_csv(OUT / "PRM125_producer_QA.csv", index=False, encoding="utf-8-sig")
    print(qa.to_dict("records"))
    if not qa.status.eq("PASS").all():
        raise SystemExit(1)


if __name__ == "__main__":
    main()
