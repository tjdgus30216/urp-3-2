from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "experiments/lab_001_xy_connection_20260626/reports/tables"
OUT = ROOT / "experiments/lab_001_xy_connection_20260626/factories/PRM-125/reports"
OUT.mkdir(parents=True, exist_ok=True)


def membership(nodes: list[str], pairs: list[tuple[str, str]]) -> dict[str, list[str]]:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for left, right in pairs:
        adjacency[left].add(right)
        adjacency[right].add(left)
    seen, result = set(), {}
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
        for candidate in group:
            result[candidate] = group
    return result


def main() -> None:
    prior = pd.read_csv(TABLES / "PRM123_xreg_v1_4_candidate_bank.csv")
    prior_values = pd.read_csv(TABLES / "PRM123_xreg_v1_4_values_long.csv")
    cohort = pd.read_csv(TABLES / "PRM124_overlay_phase_balance_candidate_registry.csv")
    cohort_values = pd.read_csv(TABLES / "PRM124_overlay_phase_balance_values_long.csv")
    bank = pd.read_csv(TABLES / "PRM125_xreg_v1_5_candidate_bank.csv")
    values = pd.read_csv(TABLES / "PRM125_xreg_v1_5_values_long.csv")
    edges = pd.read_csv(TABLES / "PRM125_unified_redundancy_edge_registry.csv")
    groups = membership(bank.candidate_id.tolist(), [(row.left_candidate_id, row.right_candidate_id) for row in edges.itertuples(index=False)])
    blocks = bank[["candidate_id", "candidate_group_id", "descriptor_family", "source_bank", "technical_role", "later_evaluation_role", "unified_block_id", "unified_block_member_count", "unified_edge_degree"]].copy()
    blocks["representative_selected"] = False
    blocks["block_policy"] = blocks.unified_block_member_count.map(lambda size: "standalone technical candidate; no selection" if size == 1 else "x-only graph block; no representative")
    blocks.to_csv(TABLES / "PRM125_unified_redundancy_block_registry.csv", index=False, encoding="utf-8-sig")
    policy = blocks.loc[blocks.candidate_id.isin(cohort.candidate_id), ["candidate_id", "unified_block_id", "unified_block_member_count"]].copy()
    policy["selection_status"] = "not_selected"
    policy.to_csv(TABLES / "PRM125_overlay_phase_balance_cohort_block_policy.csv", index=False, encoding="utf-8-sig")
    old = values.loc[values.candidate_id.isin(prior.candidate_id)].sort_values(["model_id", "candidate_id"]).reset_index(drop=True)
    old_ref = prior_values.sort_values(["model_id", "candidate_id"]).reset_index(drop=True)
    new = values.loc[values.candidate_id.isin(cohort.candidate_id)].sort_values(["model_id", "candidate_id"]).reset_index(drop=True)
    new_ref = cohort_values.sort_values(["model_id", "candidate_id"]).reset_index(drop=True)
    old_ok = len(old) == len(old_ref) and np.allclose(old.value, old_ref.value, rtol=1e-12, atol=1e-12, equal_nan=True)
    new_ok = len(new) == len(new_ref) and np.allclose(new.value, new_ref.value, rtol=1e-12, atol=1e-12)
    closed = all(bank.set_index("candidate_id").unified_block_id[row.left_candidate_id] == bank.set_index("candidate_id").unified_block_id[row.right_candidate_id] for row in edges.itertuples(index=False))
    locks = not bank.active_feature.any() and not bank.promoted.any() and bank.y_evidence.astype(str).str.lower().eq("false").all()
    checks = [
        ("I125-01", len(bank) == 365 and bank.candidate_id.nunique() == 365, "365 unique candidates"),
        ("I125-02", len(values) == 21170 and values.value.notna().sum() == 21168, "21,170 values / inherited two missing"),
        ("I125-03", old_ok, "XREG-v1.4 predecessor replay"),
        ("I125-04", new_ok, "PRM124 cohort replay"),
        ("I125-05", len(edges) == 88 and closed, "88 closed x-only edges"),
        ("I125-06", len(blocks) == 365 and blocks.unified_block_id.nunique() == 294, "294 blocks"),
        ("I125-07", len(policy) == 18 and policy.selection_status.eq("not_selected").all(), "cohort policy remains non-selecting"),
        ("I125-08", locks, "no y/selection/promotion flags"),
    ]
    qa = pd.DataFrame([{"check_id": check_id, "status": "PASS" if passed else "FAIL", "detail": detail} for check_id, passed, detail in checks])
    qa.to_csv(OUT / "PRM125_independent_QA.csv", index=False, encoding="utf-8-sig")
    summary = {"status": "PASS" if qa.status.eq("PASS").all() else "FAIL", "checks": f"{qa.status.eq('PASS').sum()}/{len(qa)}", "predecessor_replay": bool(old_ok), "cohort_replay": bool(new_ok), "performance_y_read": 0}
    (OUT / "PRM125_independent_QA_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary))
    if summary["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
