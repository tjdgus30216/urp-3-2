from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
TABLES = LAB / "reports" / "tables"
FACTORY = LAB / "factories" / "PRM-107"
CONTRACT = FACTORY / "contracts" / "PRM-107_XREG_V0_6_PROFILE_DYNAMICS_CONSOLIDATION_CONTRACT_20260723.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1_048_576), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical(left: str, right: str) -> tuple[str, str]:
    return tuple(sorted((str(left), str(right))))


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    hashes_ok = all(sha256(ROOT / item["path"]) == item["sha256"] for item in contract["inputs"])
    prior_bank = pd.read_csv(TABLES / "PRM105_xreg_v0_5_candidate_bank.csv")
    prior_values = pd.read_csv(TABLES / "PRM105_xreg_v0_5_values_long.csv")
    cohort_registry = pd.read_csv(TABLES / "PRM106_profile_dynamics_candidate_registry.csv")
    cohort_values = pd.read_csv(TABLES / "PRM106_profile_dynamics_values_long.csv")
    cross = pd.read_csv(TABLES / "PRM106_profile_dynamics_vs_XREG_v0_5_redundancy.csv")
    internal = pd.read_csv(TABLES / "PRM106_profile_dynamics_internal_redundancy.csv")
    bank = pd.read_csv(TABLES / "PRM107_xreg_v0_6_candidate_bank.csv")
    values = pd.read_csv(TABLES / "PRM107_xreg_v0_6_values_long.csv")
    wide = pd.read_csv(TABLES / "PRM107_xreg_v0_6_values_wide.csv")
    edges = pd.read_csv(TABLES / "PRM107_unified_redundancy_edge_registry.csv")
    blocks = pd.read_csv(TABLES / "PRM107_unified_redundancy_block_registry.csv")
    policy = pd.read_csv(TABLES / "PRM107_profile_dynamics_cohort_block_policy.csv")
    prior_subset = values[values["candidate_id"].isin(prior_bank["candidate_id"])].sort_values(["model_id", "candidate_id"]).reset_index(drop=True)
    prior_original = prior_values.sort_values(["model_id", "candidate_id"]).reset_index(drop=True)
    prior_ok = len(prior_subset) == len(prior_original) and prior_subset[["model_id", "candidate_id"]].equals(prior_original[["model_id", "candidate_id"]]) and np.allclose(prior_subset["value"].to_numpy(float), prior_original["value"].to_numpy(float), rtol=1e-12, atol=1e-12, equal_nan=True)
    new_subset = values[values["candidate_id"].isin(cohort_registry["candidate_id"])].sort_values(["model_id", "candidate_id"]).reset_index(drop=True)
    new_original = cohort_values.sort_values(["model_id", "candidate_id"]).reset_index(drop=True)
    new_ok = len(new_subset) == len(new_original) and new_subset[["model_id", "candidate_id"]].equals(new_original[["model_id", "candidate_id"]]) and np.allclose(new_subset["value"].to_numpy(float), new_original["value"].to_numpy(float), rtol=1e-12, atol=1e-12)
    relation_types = {"exact_duplicate", "proportional_duplicate", "high_redundancy"}
    expected_pairs = {canonical(row.candidate_id, row.existing_candidate_id) for row in cross[cross["relation"].isin(relation_types)].itertuples(index=False)}
    expected_pairs |= {canonical(row.left_candidate_id, row.right_candidate_id) for row in internal[internal["relation"].isin(relation_types)].itertuples(index=False)}
    added = edges[edges["edge_source"].astype(str).str.startswith("PRM106_")]
    actual_pairs = {canonical(row.left_candidate_id, row.right_candidate_id) for row in added.itertuples(index=False)}
    lookup = blocks.set_index("candidate_id")["unified_block_id"].to_dict()
    edge_blocks_ok = all(lookup[row.left_candidate_id] == lookup[row.right_candidate_id] for row in edges.itertuples(index=False))
    member_counts = blocks.groupby("unified_block_id")["candidate_id"].size().to_dict()
    count_ok = all(int(row.unified_block_member_count) == member_counts[row.unified_block_id] for row in blocks.itertuples(index=False))
    locks_ok = not bank["active_feature"].any() and not bank["promoted"].any() and bank["y_evidence"].astype(str).str.lower().eq("false").all() and all(value == 0 for value in contract["locks"].values())
    checks = [
        ("I107-01", hashes_ok, "all nine input hashes"),
        ("I107-02", len(bank) == 193 and bank["candidate_id"].nunique() == 193, "193 candidates"),
        ("I107-03", len(values) == 11194 and int(values["value"].notna().sum()) == 11192 and wide.shape == (58, 195), "values/matrix and inherited missingness"),
        ("I107-04", prior_ok, "prior v0.5 rows/values within 1e-12 serialization bound"),
        ("I107-05", new_ok, "PRM106 rows/values within 1e-12 serialization bound"),
        ("I107-06", len(edges) == 48 and len(added) == 5 and actual_pairs == expected_pairs, "43 prior plus exact five PRM106 edges"),
        ("I107-07", len(blocks) == 193 and blocks["unified_block_id"].nunique() == 152 and edge_blocks_ok and count_ok, "block graph closure"),
        ("I107-08", len(policy) == 22 and policy["selection_status"].eq("not_selected").all() and locks_ok, "cohort unselected and locks intact"),
    ]
    qa = pd.DataFrame([{"check_id": check_id, "status": "PASS" if ok else "FAIL", "detail": detail} for check_id, ok, detail in checks])
    qa.to_csv(FACTORY / "reports" / "PRM107_independent_QA.csv", index=False, encoding="utf-8-sig")
    summary = {"status": "PASS" if qa["status"].eq("PASS").all() else "FAIL", "checks": f"{qa['status'].eq('PASS').sum()}/{len(qa)}", "predecessor_values_within_1e-12_serialization_bound": bool(prior_ok), "cohort_values_within_1e-12_serialization_bound": bool(new_ok), "performance_y_read": 0}
    (FACTORY / "reports" / "PRM107_independent_QA_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if summary["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
