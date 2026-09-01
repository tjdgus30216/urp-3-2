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
FACTORY = LAB / "factories" / "PRM-105"
CONTRACT = FACTORY / "contracts" / "PRM-105_XREG_V0_5_OVERLAY_PHASE_CONSOLIDATION_CONTRACT_20260723.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1_048_576), b""):
            digest.update(chunk)
    return digest.hexdigest()


def connected_components(nodes: list[str], edges: list[tuple[str, str]]) -> tuple[list[list[str]], dict[str, int]]:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    visited: set[str] = set()
    components: list[list[str]] = []
    for node in sorted(nodes):
        if node in visited:
            continue
        stack = [node]
        visited.add(node)
        component: list[str] = []
        while stack:
            current = stack.pop()
            component.append(current)
            for neighbour in sorted(adjacency[current]):
                if neighbour not in visited:
                    visited.add(neighbour)
                    stack.append(neighbour)
        components.append(sorted(component))
    degree = {node: len(adjacency[node]) for node in nodes}
    return components, degree


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    for item in contract["inputs"]:
        if sha256(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError(f"input hash mismatch: {item['path']}")

    prior_bank = pd.read_csv(TABLES / "PRM103_xreg_v0_4_candidate_bank.csv")
    prior_values = pd.read_csv(TABLES / "PRM103_xreg_v0_4_values_long.csv")
    prior_edges = pd.read_csv(TABLES / "PRM103_unified_redundancy_edge_registry.csv")
    prior_blocks = pd.read_csv(TABLES / "PRM103_unified_redundancy_block_registry.csv")
    cohort_registry = pd.read_csv(TABLES / "PRM104_overlay_phase_profile_candidate_registry.csv")
    cohort_values = pd.read_csv(TABLES / "PRM104_overlay_phase_profile_values_long.csv")
    crossbank = pd.read_csv(TABLES / "PRM104_overlay_phase_profile_vs_XREG_v0_4_redundancy.csv")
    internal = pd.read_csv(TABLES / "PRM104_overlay_phase_profile_internal_redundancy.csv")
    expected = contract["expected"]

    prior_ids = prior_bank["candidate_id"].tolist()
    cohort_ids = sorted(cohort_registry["candidate_id"].tolist())
    if len(prior_ids) != expected["prior_candidates"] or len(cohort_ids) != expected["new_candidates"] or set(prior_ids) & set(cohort_ids):
        raise RuntimeError("candidate scope/overlap mismatch")
    if len(prior_values) != expected["prior_values"] or len(cohort_values) != expected["new_values"] or not np.isfinite(cohort_values["value"].to_numpy(float)).all():
        raise RuntimeError("value scope/finite mismatch")

    cross_high = crossbank[crossbank["relation"].eq("high_redundancy")].copy().sort_values(["candidate_id", "existing_candidate_id"])
    internal_high = internal[internal["relation"].eq("high_redundancy")].copy().sort_values(["left_candidate_id", "right_candidate_id"])
    if len(cross_high) != 6 or len(internal_high) != 10:
        raise RuntimeError("frozen PRM104 redundancy scope mismatch")

    predecessor_pairs = [(str(row.left_candidate_id), str(row.right_candidate_id)) for row in prior_edges.itertuples(index=False)]
    new_edge_rows: list[dict] = []
    for row in cross_high.itertuples(index=False):
        new_edge_rows.append({
            "left_candidate_id": str(row.candidate_id),
            "right_candidate_id": str(row.existing_candidate_id),
            "relation": "high_redundancy",
            "edge_source": "PRM104_overlay_phase_crossbank_full58",
            "metric_note": f"Pearson={float(row.pearson):.6f}; Spearman={float(row.spearman):.6f}; x-only warning; no representative selected",
            "selection_rule": False,
        })
    for row in internal_high.itertuples(index=False):
        new_edge_rows.append({
            "left_candidate_id": str(row.left_candidate_id),
            "right_candidate_id": str(row.right_candidate_id),
            "relation": "high_redundancy",
            "edge_source": "PRM104_overlay_phase_internal_full58",
            "metric_note": f"Pearson={float(row.pearson):.6f}; Spearman={float(row.spearman):.6f}; x-only warning; no representative selected",
            "selection_rule": False,
        })
    graph_pairs = predecessor_pairs + [(row["left_candidate_id"], row["right_candidate_id"]) for row in new_edge_rows]
    all_ids = prior_ids + cohort_ids
    components, degree = connected_components(all_ids, graph_pairs)
    old_block = prior_bank.set_index("candidate_id")["unified_block_id"].to_dict()
    component_lookup: dict[str, list[str]] = {candidate_id: component for component in components for candidate_id in component}

    block_id: dict[str, str] = {}
    changed_components: list[list[str]] = []
    for component in components:
        prior_component_ids = [candidate_id for candidate_id in component if candidate_id in old_block]
        has_new = any(candidate_id in cohort_ids for candidate_id in component)
        existing_ids = {old_block[candidate_id] for candidate_id in prior_component_ids}
        if not has_new and len(existing_ids) == 1:
            assigned = next(iter(existing_ids))
        else:
            changed_components.append(component)
            assigned = ""
        for candidate_id in component:
            block_id[candidate_id] = assigned
    for number, component in enumerate(sorted(changed_components, key=lambda item: tuple(item)), start=1):
        assigned = f"U105-BLK-{number:03d}"
        for candidate_id in component:
            block_id[candidate_id] = assigned
    if len(changed_components) != expected["new_changed_or_new_block_ids"] or len(set(block_id.values())) != expected["total_blocks"]:
        raise RuntimeError("block graph projection mismatch")

    bank = prior_bank.copy()
    bank["predecessor_unified_block_id"] = bank["unified_block_id"]
    bank["bank_version"] = "XREG-v0.5-TECHNICAL"
    bank["unified_block_id"] = bank["candidate_id"].map(block_id)
    bank["unified_block_member_count"] = bank["candidate_id"].map(lambda candidate_id: len(component_lookup[candidate_id]))
    bank["unified_edge_degree"] = bank["candidate_id"].map(degree)
    base_columns = bank.columns.tolist()
    cohort_lookup = cohort_registry.set_index("candidate_id")
    new_bank_rows: list[dict] = []
    for candidate_id in cohort_ids:
        source = cohort_lookup.loc[candidate_id]
        values = cohort_values[cohort_values["candidate_id"].eq(candidate_id)]["value"].to_numpy(float)
        row = {
            "bank_version": "XREG-v0.5-TECHNICAL",
            "candidate_id": candidate_id,
            "candidate_group_id": source["candidate_group_id"],
            "descriptor_family": source["descriptor_family"],
            "output_name": source["output_name"],
            "unit": source["unit"],
            "source_population": source["source_population"],
            "aggregation_formula": source["aggregation_formula"],
            "applicable_family": source["applicable_family"],
            "direct_or_derived": source["direct_or_derived"],
            "source_bank": "PRM104_overlay_phase_profile_batch",
            "source_value_table": "PRM104_overlay_phase_profile_values_long.csv",
            "technical_role": "batch_BC_candidate",
            "qualification_status": "full58_raw_table_batch_not_selected",
            "confidence_status": "confirmed_raw_table_lineage",
            "later_evaluation_role": "batch_BC_unselected_block_aware",
            "active_feature": False,
            "promoted": False,
            "y_evidence": False,
            "notes": "PRM104 overlay phase-profile cohort; no y, selection or promotion",
            "model_count": 58,
            "finite_count": int(np.isfinite(values).sum()),
            "unique_count": int(np.unique(values).size),
            "unified_block_id": block_id[candidate_id],
            "unified_block_member_count": len(component_lookup[candidate_id]),
            "unified_edge_degree": degree[candidate_id],
            "operational_grade": source["operational_grade"],
            "literature_anchor": source["literature_anchor"],
            "anchor_scope": source["anchor_scope"],
            "predecessor_unified_block_id": pd.NA,
        }
        new_bank_rows.append(row)
    bank = pd.concat([bank, pd.DataFrame(new_bank_rows).reindex(columns=base_columns)], ignore_index=True)
    if len(bank) != expected["total_candidates"] or bank["candidate_id"].nunique() != expected["total_candidates"]:
        raise RuntimeError("bank append mismatch")

    prior_out = prior_values.copy()
    prior_out["bank_version"] = "XREG-v0.5-TECHNICAL"
    family = prior_out[["model_id", "model_family"]].drop_duplicates().set_index("model_id")["model_family"].to_dict()
    cohort_out = cohort_values.assign(
        bank_version="XREG-v0.5-TECHNICAL",
        model_family=cohort_values["model_id"].map(family),
        finite=True,
        source_bank="PRM104_overlay_phase_profile_batch",
    )[["bank_version", "model_id", "model_family", "candidate_id", "value", "finite", "source_bank"]]
    values = pd.concat([prior_out, cohort_out], ignore_index=True)
    candidate_order = bank["candidate_id"].tolist()
    wide = values.pivot(index=["model_id", "model_family"], columns="candidate_id", values="value").reindex(columns=candidate_order).reset_index()

    edge_rows = prior_edges.copy()
    added = pd.DataFrame(new_edge_rows)
    added.insert(0, "edge_id", [f"U105-EDGE-{number:03d}" for number in range(28, 28 + len(added))])
    edges = pd.concat([edge_rows, added.reindex(columns=edge_rows.columns)], ignore_index=True)

    block_rows: list[dict] = []
    bank_lookup = bank.set_index("candidate_id")
    for candidate_id in candidate_order:
        source = bank_lookup.loc[candidate_id]
        members = len(component_lookup[candidate_id])
        is_new = candidate_id in cohort_ids
        if members == 1:
            policy = "standalone technical candidate; no selection in PRM105"
        elif candidate_id.startswith("RAW-X037"):
            policy = "compositional dependency block; no independent starter or selection"
        else:
            policy = "no selection; later block-aware comparison only"
        block_rows.append({
            "unified_block_id": block_id[candidate_id],
            "predecessor_unified_block_id": source["predecessor_unified_block_id"],
            "candidate_id": candidate_id,
            "candidate_group_id": source["candidate_group_id"],
            "descriptor_family": source["descriptor_family"],
            "source_bank": source["source_bank"],
            "technical_role": source["technical_role"],
            "later_evaluation_role": source["later_evaluation_role"],
            "unified_block_member_count": members,
            "unified_edge_degree": degree[candidate_id],
            "representative_selected": False,
            "block_policy": policy,
            "new_in_PRM105": bool(is_new),
        })
    blocks = pd.DataFrame(block_rows)

    policy_rows: list[dict] = []
    for candidate_id in cohort_ids:
        component = component_lookup[candidate_id]
        prior_member = any(member in old_block for member in component)
        if len(component) == 1:
            status = "singleton"
        elif prior_member:
            status = "crossbank_merge_block"
        elif candidate_id.startswith("RAW-X037"):
            status = "compositional_batch_block"
        else:
            status = "internal_batch_block"
        policy_rows.append({
            "candidate_id": candidate_id,
            "operational_grade": cohort_lookup.loc[candidate_id, "operational_grade"],
            "unified_block_id": block_id[candidate_id],
            "block_status": status,
            "block_member_count": len(component),
            "selection_status": "not_selected",
            "next_allowed_action": "future no-y batch or separately authorised block-aware grouped-y protocol",
        })
    policy = pd.DataFrame(policy_rows)

    qa: list[dict] = []
    def check(check_id: str, ok: bool, detail: str) -> None:
        qa.append({"check_id": check_id, "status": "PASS" if ok else "FAIL", "detail": detail})

    check("P105-01", len(bank) == 171 and bank["candidate_id"].nunique() == 171, "171 candidates")
    check("P105-02", len(values) == 9918 and int(values["value"].notna().sum()) == 9916, "9,918 values, two inherited NA")
    check("P105-03", wide.shape == (58, 173), "58x171 wide candidate matrix")
    check("P105-04", len(blocks) == 171 and blocks["unified_block_id"].nunique() == 135, "135 graph-closure blocks")
    check("P105-05", len(edges) == 43 and edges["edge_id"].nunique() == 43, "43 redundancy edges")
    check("P105-06", len(added) == 16 and set(added["edge_source"]) == {"PRM104_overlay_phase_crossbank_full58", "PRM104_overlay_phase_internal_full58"}, "six crossbank plus ten internal PRM104 edges")
    check("P105-07", len(policy) == 28 and policy["selection_status"].eq("not_selected").all(), "28 appended candidates remain unselected")
    check("P105-08", not bank["active_feature"].any() and not bank["promoted"].any() and bank["y_evidence"].astype(str).str.lower().eq("false").all(), "bank locks remain")
    if not all(item["status"] == "PASS" for item in qa):
        raise RuntimeError(qa)

    TABLES.mkdir(parents=True, exist_ok=True)
    (FACTORY / "reports").mkdir(parents=True, exist_ok=True)
    bank.to_csv(TABLES / "PRM105_xreg_v0_5_candidate_bank.csv", index=False, encoding="utf-8-sig")
    values.to_csv(TABLES / "PRM105_xreg_v0_5_values_long.csv", index=False, encoding="utf-8-sig", float_format="%.17g")
    wide.to_csv(TABLES / "PRM105_xreg_v0_5_values_wide.csv", index=False, encoding="utf-8-sig", float_format="%.17g")
    edges.to_csv(TABLES / "PRM105_unified_redundancy_edge_registry.csv", index=False, encoding="utf-8-sig")
    blocks.to_csv(TABLES / "PRM105_unified_redundancy_block_registry.csv", index=False, encoding="utf-8-sig")
    policy.to_csv(TABLES / "PRM105_overlay_phase_cohort_block_policy.csv", index=False, encoding="utf-8-sig")
    qa_frame = pd.DataFrame(qa)
    qa_frame.to_csv(FACTORY / "reports" / "PRM105_producer_QA.csv", index=False, encoding="utf-8-sig")
    summary = {"status": "PASS", "checks": "8/8", "candidates": 171, "values": 9918, "finite_values": 9916, "blocks": 135, "edges": 43, "y_fit_selection_promotion": "0/0/0/0"}
    (FACTORY / "reports" / "PRM105_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
