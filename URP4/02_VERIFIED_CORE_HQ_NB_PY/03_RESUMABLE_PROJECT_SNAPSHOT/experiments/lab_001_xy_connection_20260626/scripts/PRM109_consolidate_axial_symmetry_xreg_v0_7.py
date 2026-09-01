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
FACTORY = LAB / "factories" / "PRM-109"
CONTRACT = FACTORY / "contracts" / "PRM-109_XREG_V0_7_AXIAL_SYMMETRY_CONSOLIDATION_CONTRACT_20260723.json"
RELATIONS = {"exact_duplicate", "proportional_duplicate", "high_redundancy"}


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
    groups: list[list[str]] = []
    visited: set[str] = set()
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

    prior_bank = pd.read_csv(TABLES / "PRM107_xreg_v0_6_candidate_bank.csv")
    prior_values = pd.read_csv(TABLES / "PRM107_xreg_v0_6_values_long.csv")
    prior_edges = pd.read_csv(TABLES / "PRM107_unified_redundancy_edge_registry.csv")
    prior_blocks = pd.read_csv(TABLES / "PRM107_unified_redundancy_block_registry.csv")
    cohort_registry = pd.read_csv(TABLES / "PRM108_axial_distribution_symmetry_candidate_registry.csv")
    cohort_values = pd.read_csv(TABLES / "PRM108_axial_distribution_symmetry_values_long.csv")
    cross = pd.read_csv(TABLES / "PRM108_axial_distribution_symmetry_vs_XREG_v0_6_redundancy.csv")
    internal = pd.read_csv(TABLES / "PRM108_axial_distribution_symmetry_internal_redundancy.csv")

    prior_ids = prior_bank["candidate_id"].tolist()
    cohort_ids = sorted(cohort_registry["candidate_id"].tolist())
    if len(prior_ids) != 193 or len(cohort_ids) != 24 or set(prior_ids) & set(cohort_ids):
        raise RuntimeError("candidate scope/overlap mismatch")
    if len(prior_values) != 11194 or len(cohort_values) != 1392:
        raise RuntimeError("value scope mismatch")
    if not np.isfinite(cohort_values["value"].to_numpy(float)).all():
        raise RuntimeError("non-finite PRM108 cohort value")
    if len(prior_edges) != 48 or prior_blocks["unified_block_id"].nunique() != 152:
        raise RuntimeError("predecessor graph scope mismatch")

    cross_selected = cross[cross["relation"].isin(RELATIONS)].copy()
    internal_selected = internal[internal["relation"].isin(RELATIONS)].copy()
    if len(cross_selected) != 0:
        raise RuntimeError("unexpected PRM108 crossbank edge")
    if internal_selected["relation"].value_counts().to_dict() != {"high_redundancy": 1}:
        raise RuntimeError("PRM108 internal relation scope mismatch")

    edge_row = internal_selected.iloc[0]
    new_edge = {
        "edge_id": "U109-EDGE-049",
        "left_candidate_id": str(edge_row["left_candidate_id"]),
        "right_candidate_id": str(edge_row["right_candidate_id"]),
        "relation": str(edge_row["relation"]),
        "edge_source": "PRM108_axial_symmetry_internal_full58",
        "metric_note": (
            f"Pearson={float(edge_row['pearson']):.6f}; "
            f"Spearman={float(edge_row['spearman']):.6f}; "
            f"residual={float(edge_row['normalized_L2_residual']):.3e}; no representative"
        ),
        "selection_rule": False,
    }
    all_ids = prior_ids + cohort_ids
    graph_pairs = [
        (str(row.left_candidate_id), str(row.right_candidate_id))
        for row in prior_edges.itertuples(index=False)
    ] + [(new_edge["left_candidate_id"], new_edge["right_candidate_id"])]
    groups, degree = components(all_ids, graph_pairs)
    group_lookup = {candidate_id: group for group in groups for candidate_id in group}
    prior_block_lookup = prior_bank.set_index("candidate_id")["unified_block_id"].to_dict()
    block_id = dict(prior_block_lookup)
    new_groups = sorted(
        {tuple(group_lookup[candidate_id]) for candidate_id in cohort_ids},
        key=lambda group: tuple(group),
    )
    if len(new_groups) != 23:
        raise RuntimeError("new component count mismatch")
    for number, group in enumerate(new_groups, start=1):
        for candidate_id in group:
            block_id[candidate_id] = f"U109-BLK-{number:03d}"
    if len(set(block_id.values())) != 175:
        raise RuntimeError("successor block count mismatch")

    bank = prior_bank.copy()
    bank["predecessor_unified_block_id"] = bank["unified_block_id"]
    bank["bank_version"] = "XREG-v0.7-TECHNICAL"
    bank["unified_block_member_count"] = bank["candidate_id"].map(
        lambda candidate_id: len(group_lookup[candidate_id])
    )
    bank["unified_edge_degree"] = bank["candidate_id"].map(degree)
    columns = bank.columns.tolist()
    cohort_lookup = cohort_registry.set_index("candidate_id")
    rows: list[dict] = []
    for candidate_id in cohort_ids:
        source = cohort_lookup.loc[candidate_id]
        vector = cohort_values.loc[
            cohort_values["candidate_id"].eq(candidate_id), "value"
        ].to_numpy(float)
        rows.append(
            {
                "bank_version": "XREG-v0.7-TECHNICAL",
                "candidate_id": candidate_id,
                "candidate_group_id": source["candidate_group_id"],
                "descriptor_family": source["descriptor_family"],
                "output_name": source["output_name"],
                "unit": source["unit"],
                "source_population": source["source_population"],
                "aggregation_formula": source["aggregation_formula"],
                "applicable_family": source["applicable_family"],
                "direct_or_derived": source["direct_or_derived"],
                "source_bank": "PRM108_axial_distribution_symmetry_batch",
                "source_value_table": "PRM108_axial_distribution_symmetry_values_long.csv",
                "technical_role": "batch_BC_candidate",
                "qualification_status": "full58_raw_table_batch_not_selected",
                "confidence_status": "confirmed_raw_table_lineage",
                "later_evaluation_role": "batch_BC_unselected_block_aware",
                "active_feature": False,
                "promoted": False,
                "y_evidence": False,
                "notes": "PRM108 axial distribution/reflection-symmetry cohort; no y, selection or promotion",
                "model_count": 58,
                "finite_count": int(np.isfinite(vector).sum()),
                "unique_count": int(np.unique(vector).size),
                "unified_block_id": block_id[candidate_id],
                "unified_block_member_count": len(group_lookup[candidate_id]),
                "unified_edge_degree": degree[candidate_id],
                "operational_grade": source["operational_grade"],
                "literature_anchor": source["literature_anchor"],
                "anchor_scope": source["anchor_scope"],
                "predecessor_unified_block_id": pd.NA,
            }
        )
    bank = pd.concat(
        [bank, pd.DataFrame(rows).reindex(columns=columns)], ignore_index=True
    )

    prior_out = prior_values.copy()
    prior_out["bank_version"] = "XREG-v0.7-TECHNICAL"
    new_out = cohort_values.assign(
        bank_version="XREG-v0.7-TECHNICAL",
        finite=True,
        source_bank="PRM108_axial_distribution_symmetry_batch",
    )[
        [
            "bank_version",
            "model_id",
            "model_family",
            "candidate_id",
            "value",
            "finite",
            "source_bank",
        ]
    ]
    values = pd.concat([prior_out, new_out], ignore_index=True)
    wide = (
        values.pivot(
            index=["model_id", "model_family"], columns="candidate_id", values="value"
        )
        .reindex(columns=bank["candidate_id"].tolist())
        .reset_index()
    )

    edges = pd.concat(
        [prior_edges, pd.DataFrame([new_edge]).reindex(columns=prior_edges.columns)],
        ignore_index=True,
    )
    bank_lookup = bank.set_index("candidate_id")
    block_rows: list[dict] = []
    for candidate_id in bank["candidate_id"]:
        source = bank_lookup.loc[candidate_id]
        member_count = len(group_lookup[candidate_id])
        block_rows.append(
            {
                "unified_block_id": block_id[candidate_id],
                "predecessor_unified_block_id": source[
                    "predecessor_unified_block_id"
                ],
                "candidate_id": candidate_id,
                "candidate_group_id": source["candidate_group_id"],
                "descriptor_family": source["descriptor_family"],
                "source_bank": source["source_bank"],
                "technical_role": source["technical_role"],
                "later_evaluation_role": source["later_evaluation_role"],
                "unified_block_member_count": member_count,
                "unified_edge_degree": degree[candidate_id],
                "representative_selected": False,
                "block_policy": (
                    "standalone technical candidate; no selection in PRM109"
                    if member_count == 1
                    else "exact/proportional/high x-only block; no representative selected"
                ),
                "new_in_PRM107": bool(
                    candidate_id in prior_blocks.loc[
                        prior_blocks["new_in_PRM107"].astype(str).str.lower().eq("true"),
                        "candidate_id",
                    ].tolist()
                ),
                "new_in_PRM109": bool(candidate_id in cohort_ids),
            }
        )
    blocks = pd.DataFrame(block_rows)
    policy = pd.DataFrame(
        [
            {
                "candidate_id": candidate_id,
                "operational_grade": cohort_lookup.loc[
                    candidate_id, "operational_grade"
                ],
                "unified_block_id": block_id[candidate_id],
                "block_status": (
                    "singleton"
                    if len(group_lookup[candidate_id]) == 1
                    else "internal_high_redundancy_block"
                ),
                "block_member_count": len(group_lookup[candidate_id]),
                "selection_status": "not_selected",
                "next_allowed_action": "future no-y batch or separately authorised block-aware grouped-y protocol",
            }
            for candidate_id in cohort_ids
        ]
    )

    checks: list[dict] = []

    def check(check_id: str, condition: bool, detail: str) -> None:
        checks.append(
            {
                "check_id": check_id,
                "status": "PASS" if condition else "FAIL",
                "detail": detail,
            }
        )

    check("P109-01", len(bank) == 217 and bank["candidate_id"].nunique() == 217, "217 candidates")
    check("P109-02", len(values) == 12586 and int(values["value"].notna().sum()) == 12584, "12,586 values and two inherited NA")
    check("P109-03", wide.shape == (58, 219), "58x217 wide matrix")
    check("P109-04", len(blocks) == 217 and blocks["unified_block_id"].nunique() == 175, "175 graph blocks")
    check("P109-05", len(edges) == 49 and edges["edge_id"].nunique() == 49, "49 edges")
    check("P109-06", len(policy) == 24 and policy["block_status"].value_counts().to_dict() == {"singleton": 22, "internal_high_redundancy_block": 2}, "24-candidate block policy")
    check("P109-07", (bank.loc[bank["candidate_id"].isin(prior_ids), "unified_block_id"].to_numpy() == prior_bank["unified_block_id"].to_numpy()).all(), "all predecessor block IDs preserved")
    check("P109-08", not bank["active_feature"].any() and not bank["promoted"].any() and bank["y_evidence"].astype(str).str.lower().eq("false").all(), "bank locks remain")
    qa = pd.DataFrame(checks)
    if not qa["status"].eq("PASS").all():
        raise RuntimeError(qa.to_dict(orient="records"))

    TABLES.mkdir(parents=True, exist_ok=True)
    (FACTORY / "reports").mkdir(parents=True, exist_ok=True)
    bank.to_csv(TABLES / "PRM109_xreg_v0_7_candidate_bank.csv", index=False, encoding="utf-8-sig")
    values.to_csv(TABLES / "PRM109_xreg_v0_7_values_long.csv", index=False, encoding="utf-8-sig", float_format="%.17g")
    wide.to_csv(TABLES / "PRM109_xreg_v0_7_values_wide.csv", index=False, encoding="utf-8-sig", float_format="%.17g")
    edges.to_csv(TABLES / "PRM109_unified_redundancy_edge_registry.csv", index=False, encoding="utf-8-sig")
    blocks.to_csv(TABLES / "PRM109_unified_redundancy_block_registry.csv", index=False, encoding="utf-8-sig")
    policy.to_csv(TABLES / "PRM109_axial_symmetry_cohort_block_policy.csv", index=False, encoding="utf-8-sig")
    qa.to_csv(FACTORY / "reports" / "PRM109_producer_QA.csv", index=False, encoding="utf-8-sig")
    summary = {
        "status": "PASS",
        "checks": "8/8",
        "candidates": 217,
        "values": 12586,
        "finite_values": 12584,
        "blocks": 175,
        "edges": 49,
        "y_fit_selection_promotion": "0/0/0/0",
    }
    (FACTORY / "reports" / "PRM109_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
