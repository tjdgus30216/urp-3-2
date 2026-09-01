from __future__ import annotations

import hashlib
import json
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


def pair(left: str, right: str) -> tuple[str, str]:
    return tuple(sorted((str(left), str(right))))


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    hashes_ok = all(sha256(ROOT / item["path"]) == item["sha256"] for item in contract["inputs"])
    prior = pd.read_csv(TABLES / "PRM119_xreg_v1_2_candidate_bank.csv")
    prior_values = pd.read_csv(TABLES / "PRM119_xreg_v1_2_values_long.csv")
    prior_edges = pd.read_csv(TABLES / "PRM119_unified_redundancy_edge_registry.csv")
    cohort = pd.read_csv(TABLES / "PRM120_overlay_pair_component_composition_candidate_registry.csv")
    cohort_values = pd.read_csv(TABLES / "PRM120_overlay_pair_component_composition_values_long.csv")
    cross = pd.read_csv(TABLES / "PRM120_overlay_pair_component_composition_vs_XREG_v1_2_redundancy.csv")
    internal = pd.read_csv(TABLES / "PRM120_overlay_pair_component_composition_internal_redundancy.csv")
    bank = pd.read_csv(TABLES / "PRM121_xreg_v1_3_candidate_bank.csv")
    values = pd.read_csv(TABLES / "PRM121_xreg_v1_3_values_long.csv")
    wide = pd.read_csv(TABLES / "PRM121_xreg_v1_3_values_wide.csv")
    edges = pd.read_csv(TABLES / "PRM121_unified_redundancy_edge_registry.csv")
    blocks = pd.read_csv(TABLES / "PRM121_unified_redundancy_block_registry.csv")
    policy = pd.read_csv(TABLES / "PRM121_overlay_pair_component_composition_cohort_block_policy.csv")
    old = values[values.candidate_id.isin(prior.candidate_id)].sort_values(["model_id", "candidate_id"]).reset_index(drop=True)
    old_ref = prior_values.sort_values(["model_id", "candidate_id"]).reset_index(drop=True)
    old_ok = len(old) == len(old_ref) and old[["model_id", "candidate_id"]].equals(old_ref[["model_id", "candidate_id"]]) and np.allclose(old.value, old_ref.value, rtol=1e-12, atol=1e-12, equal_nan=True)
    new = values[values.candidate_id.isin(cohort.candidate_id)].sort_values(["model_id", "candidate_id"]).reset_index(drop=True)
    new_ref = cohort_values.sort_values(["model_id", "candidate_id"]).reset_index(drop=True)
    new_ok = len(new) == len(new_ref) and new[["model_id", "candidate_id"]].equals(new_ref[["model_id", "candidate_id"]]) and np.allclose(new.value, new_ref.value, rtol=1e-12, atol=1e-12)
    include = contract["relation_policy"]["include_relations"]
    expected = {pair(row.candidate_id, row.existing_candidate_id) for row in cross[cross.relation.isin(include)].itertuples(index=False)} | {pair(row.left_candidate_id, row.right_candidate_id) for row in internal[internal.relation.isin(include)].itertuples(index=False)}
    added = edges[edges.edge_source.astype(str).str.startswith("PRM120_")]
    actual = {pair(row.left_candidate_id, row.right_candidate_id) for row in added.itertuples(index=False)}
    prior_edges_ok = edges.iloc[:len(prior_edges)][prior_edges.columns].astype(str).equals(prior_edges.astype(str))
    predecessor_block = prior.set_index("candidate_id").unified_block_id.to_dict()
    successor_block = bank.set_index("candidate_id").unified_block_id.to_dict()
    changed = sum(successor_block[candidate_id] != block_id for candidate_id, block_id in predecessor_block.items())
    lookup = blocks.set_index("candidate_id").unified_block_id.to_dict()
    edges_closed = all(lookup[row.left_candidate_id] == lookup[row.right_candidate_id] for row in edges.itertuples(index=False))
    counts = blocks.groupby("unified_block_id").candidate_id.size().to_dict()
    count_ok = all(int(row.unified_block_member_count) == counts[row.unified_block_id] for row in blocks.itertuples(index=False))
    locks_ok = not bank.active_feature.any() and not bank.promoted.any() and bank.y_evidence.astype(str).str.lower().eq("false").all() and all(value == 0 for value in contract["locks"].values())
    checks = [
        ("I121-01", hashes_ok, "all nine input hashes"),
        ("I121-02", len(bank) == 323 and bank.candidate_id.nunique() == 323, "323 candidates"),
        ("I121-03", len(values) == 18734 and int(values.value.notna().sum()) == 18732 and wide.shape == (58, 325), "values/matrix and inherited missingness"),
        ("I121-04", old_ok, "predecessor v1.2 rows/values within 1e-12"),
        ("I121-05", new_ok, "PRM120 rows/values within 1e-12"),
        ("I121-06", len(edges) == 81 and len(added) == 5 and actual == expected and prior_edges_ok, "76 prior plus exact five PRM120 edges"),
        ("I121-07", len(blocks) == 323 and blocks.unified_block_id.nunique() == 259 and edges_closed and count_ok and changed == 5, "graph closure and five merged predecessor members"),
        ("I121-08", len(policy) == 24 and policy.selection_status.eq("not_selected").all() and locks_ok, "cohort policy and locks"),
    ]
    qa = pd.DataFrame([{"check_id": check_id, "status": "PASS" if passed else "FAIL", "detail": detail} for check_id, passed, detail in checks])
    (FACTORY / "reports").mkdir(parents=True, exist_ok=True)
    qa.to_csv(FACTORY / "reports" / "PRM121_independent_QA.csv", index=False, encoding="utf-8-sig")
    summary = {"status": "PASS" if qa.status.eq("PASS").all() else "FAIL", "checks": f"{qa.status.eq('PASS').sum()}/{len(qa)}", "predecessor_values_within_1e-12_serialization_bound": bool(old_ok), "cohort_values_within_1e-12_serialization_bound": bool(new_ok), "merged_predecessor_members": changed, "performance_y_read": 0}
    (FACTORY / "reports" / "PRM121_independent_QA_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if summary["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
