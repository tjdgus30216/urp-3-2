from __future__ import annotations

import hashlib
import json
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


def undirected(left: str, right: str) -> tuple[str, str]:
    return tuple(sorted((str(left), str(right))))


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    hashes_ok = all(sha256(ROOT / item["path"]) == item["sha256"] for item in contract["inputs"])

    prior = pd.read_csv(TABLES / "PRM117_xreg_v1_1_candidate_bank.csv")
    prior_values = pd.read_csv(TABLES / "PRM117_xreg_v1_1_values_long.csv")
    prior_edges = pd.read_csv(TABLES / "PRM117_unified_redundancy_edge_registry.csv")
    cohort = pd.read_csv(TABLES / "PRM118_slice_component_filter_sensitivity_candidate_registry.csv")
    cohort_values = pd.read_csv(TABLES / "PRM118_slice_component_filter_sensitivity_values_long.csv")
    crossbank = pd.read_csv(TABLES / "PRM118_slice_component_filter_sensitivity_vs_XREG_v1_1_redundancy.csv")
    bank = pd.read_csv(TABLES / "PRM119_xreg_v1_2_candidate_bank.csv")
    values = pd.read_csv(TABLES / "PRM119_xreg_v1_2_values_long.csv")
    wide = pd.read_csv(TABLES / "PRM119_xreg_v1_2_values_wide.csv")
    edges = pd.read_csv(TABLES / "PRM119_unified_redundancy_edge_registry.csv")
    blocks = pd.read_csv(TABLES / "PRM119_unified_redundancy_block_registry.csv")
    policy = pd.read_csv(TABLES / "PRM119_slice_component_filter_sensitivity_cohort_block_policy.csv")

    predecessor = values[values.candidate_id.isin(prior.candidate_id)].sort_values(["model_id", "candidate_id"]).reset_index(drop=True)
    predecessor_reference = prior_values.sort_values(["model_id", "candidate_id"]).reset_index(drop=True)
    predecessor_ok = (
        len(predecessor) == len(predecessor_reference)
        and predecessor[["model_id", "candidate_id"]].equals(predecessor_reference[["model_id", "candidate_id"]])
        and np.allclose(predecessor.value, predecessor_reference.value, rtol=1e-12, atol=1e-12, equal_nan=True)
    )
    appended = values[values.candidate_id.isin(cohort.candidate_id)].sort_values(["model_id", "candidate_id"]).reset_index(drop=True)
    appended_reference = cohort_values.sort_values(["model_id", "candidate_id"]).reset_index(drop=True)
    appended_ok = (
        len(appended) == len(appended_reference)
        and appended[["model_id", "candidate_id"]].equals(appended_reference[["model_id", "candidate_id"]])
        and np.allclose(appended.value, appended_reference.value, rtol=1e-12, atol=1e-12)
    )
    declared = {
        undirected(row.candidate_id, row.existing_candidate_id)
        for row in crossbank[crossbank.relation.isin(contract["relation_policy"]["include_relations"])].itertuples(index=False)
    }
    added = edges[edges.edge_source.astype(str).str.startswith("PRM118_")]
    actual = {undirected(row.left_candidate_id, row.right_candidate_id) for row in added.itertuples(index=False)}
    predecessor_edges_ok = edges.iloc[: len(prior_edges)][prior_edges.columns].astype(str).equals(prior_edges.astype(str))

    predecessor_block = prior.set_index("candidate_id").unified_block_id.to_dict()
    successor_block = bank.set_index("candidate_id").unified_block_id.to_dict()
    changed_predecessors = sum(successor_block[candidate_id] != prior_id for candidate_id, prior_id in predecessor_block.items())
    block_lookup = blocks.set_index("candidate_id").unified_block_id.to_dict()
    edges_closed = all(block_lookup[row.left_candidate_id] == block_lookup[row.right_candidate_id] for row in edges.itertuples(index=False))
    member_counts = blocks.groupby("unified_block_id").candidate_id.size().to_dict()
    counts_ok = all(int(row.unified_block_member_count) == member_counts[row.unified_block_id] for row in blocks.itertuples(index=False))
    locks_ok = (
        not bank.active_feature.any()
        and not bank.promoted.any()
        and bank.y_evidence.astype(str).str.lower().eq("false").all()
        and all(value == 0 for value in contract["locks"].values())
    )
    checks = [
        ("I119-01", hashes_ok, "all eight input hashes"),
        ("I119-02", len(bank) == 299 and bank.candidate_id.nunique() == 299, "299 candidates"),
        ("I119-03", len(values) == 17342 and int(values.value.notna().sum()) == 17340 and wide.shape == (58, 301), "values/matrix and inherited missingness"),
        ("I119-04", predecessor_ok, "predecessor v1.1 rows/values within 1e-12"),
        ("I119-05", appended_ok, "PRM118 rows/values within 1e-12"),
        ("I119-06", len(edges) == 76 and len(added) == 11 and actual == declared and predecessor_edges_ok, "65 prior plus exact 11 PRM118 edges"),
        ("I119-07", len(blocks) == 299 and blocks.unified_block_id.nunique() == 240 and edges_closed and counts_ok and changed_predecessors == 11, "graph closure and eleven merged predecessor members"),
        ("I119-08", len(policy) == 11 and policy.block_status.value_counts().to_dict() == {"crossbank_exact_or_high_redundancy_block": 6, "singleton": 5} and policy.selection_status.eq("not_selected").all() and locks_ok, "cohort policy and locks"),
    ]
    qa = pd.DataFrame([{"check_id": check_id, "status": "PASS" if passed else "FAIL", "detail": detail} for check_id, passed, detail in checks])
    (FACTORY / "reports").mkdir(parents=True, exist_ok=True)
    qa.to_csv(FACTORY / "reports" / "PRM119_independent_QA.csv", index=False, encoding="utf-8-sig")
    summary = {
        "status": "PASS" if qa.status.eq("PASS").all() else "FAIL",
        "checks": f"{qa.status.eq('PASS').sum()}/{len(qa)}",
        "predecessor_values_within_1e-12_serialization_bound": bool(predecessor_ok),
        "cohort_values_within_1e-12_serialization_bound": bool(appended_ok),
        "merged_predecessor_members": changed_predecessors,
        "performance_y_read": 0,
    }
    (FACTORY / "reports" / "PRM119_independent_QA_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if summary["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
