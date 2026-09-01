from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
TABLES = LAB / "reports" / "tables"
FACTORY = LAB / "factories" / "PRM-109"
CONTRACT = FACTORY / "contracts" / "PRM-109_XREG_V0_7_AXIAL_SYMMETRY_CONSOLIDATION_CONTRACT_20260723.json"


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
    hashes_ok = all(
        sha256(ROOT / item["path"]) == item["sha256"]
        for item in contract["inputs"]
    )
    prior_bank = pd.read_csv(TABLES / "PRM107_xreg_v0_6_candidate_bank.csv")
    prior_values = pd.read_csv(TABLES / "PRM107_xreg_v0_6_values_long.csv")
    prior_edges = pd.read_csv(TABLES / "PRM107_unified_redundancy_edge_registry.csv")
    cohort_registry = pd.read_csv(TABLES / "PRM108_axial_distribution_symmetry_candidate_registry.csv")
    cohort_values = pd.read_csv(TABLES / "PRM108_axial_distribution_symmetry_values_long.csv")
    internal = pd.read_csv(TABLES / "PRM108_axial_distribution_symmetry_internal_redundancy.csv")
    bank = pd.read_csv(TABLES / "PRM109_xreg_v0_7_candidate_bank.csv")
    values = pd.read_csv(TABLES / "PRM109_xreg_v0_7_values_long.csv")
    wide = pd.read_csv(TABLES / "PRM109_xreg_v0_7_values_wide.csv")
    edges = pd.read_csv(TABLES / "PRM109_unified_redundancy_edge_registry.csv")
    blocks = pd.read_csv(TABLES / "PRM109_unified_redundancy_block_registry.csv")
    policy = pd.read_csv(TABLES / "PRM109_axial_symmetry_cohort_block_policy.csv")

    prior_subset = (
        values[values["candidate_id"].isin(prior_bank["candidate_id"])]
        .sort_values(["model_id", "candidate_id"])
        .reset_index(drop=True)
    )
    prior_original = prior_values.sort_values(
        ["model_id", "candidate_id"]
    ).reset_index(drop=True)
    prior_ok = (
        len(prior_subset) == len(prior_original)
        and prior_subset[["model_id", "candidate_id"]].equals(
            prior_original[["model_id", "candidate_id"]]
        )
        and np.allclose(
            prior_subset["value"].to_numpy(float),
            prior_original["value"].to_numpy(float),
            rtol=1e-12,
            atol=1e-12,
            equal_nan=True,
        )
    )
    new_subset = (
        values[values["candidate_id"].isin(cohort_registry["candidate_id"])]
        .sort_values(["model_id", "candidate_id"])
        .reset_index(drop=True)
    )
    new_original = cohort_values.sort_values(
        ["model_id", "candidate_id"]
    ).reset_index(drop=True)
    new_ok = (
        len(new_subset) == len(new_original)
        and new_subset[["model_id", "candidate_id"]].equals(
            new_original[["model_id", "candidate_id"]]
        )
        and np.allclose(
            new_subset["value"].to_numpy(float),
            new_original["value"].to_numpy(float),
            rtol=1e-12,
            atol=1e-12,
        )
    )

    expected_row = internal.loc[internal["relation"].eq("high_redundancy")].iloc[0]
    expected_pair = canonical(
        expected_row["left_candidate_id"], expected_row["right_candidate_id"]
    )
    added = edges.loc[edges["edge_source"].eq("PRM108_axial_symmetry_internal_full58")]
    actual_pairs = {
        canonical(row.left_candidate_id, row.right_candidate_id)
        for row in added.itertuples(index=False)
    }
    predecessor_edges_ok = edges.iloc[: len(prior_edges)][
        prior_edges.columns
    ].astype(str).equals(prior_edges.astype(str))
    lookup = blocks.set_index("candidate_id")["unified_block_id"].to_dict()
    edge_blocks_ok = all(
        lookup[row.left_candidate_id] == lookup[row.right_candidate_id]
        for row in edges.itertuples(index=False)
    )
    member_counts = blocks.groupby("unified_block_id")["candidate_id"].size().to_dict()
    count_ok = all(
        int(row.unified_block_member_count) == member_counts[row.unified_block_id]
        for row in blocks.itertuples(index=False)
    )
    prior_blocks_ok = all(
        lookup[row.candidate_id] == row.unified_block_id
        for row in prior_bank.itertuples(index=False)
    )
    locks_ok = (
        not bank["active_feature"].any()
        and not bank["promoted"].any()
        and bank["y_evidence"].astype(str).str.lower().eq("false").all()
        and all(value == 0 for value in contract["locks"].values())
    )
    checks = [
        ("I109-01", hashes_ok, "all nine input hashes"),
        ("I109-02", len(bank) == 217 and bank["candidate_id"].nunique() == 217, "217 candidates"),
        ("I109-03", len(values) == 12586 and int(values["value"].notna().sum()) == 12584 and wide.shape == (58, 219), "values/matrix and inherited missingness"),
        ("I109-04", prior_ok, "predecessor v0.6 rows/values within 1e-12 serialization bound"),
        ("I109-05", new_ok, "PRM108 rows/values within 1e-12 serialization bound"),
        ("I109-06", len(edges) == 49 and len(added) == 1 and actual_pairs == {expected_pair} and predecessor_edges_ok, "48 prior plus exact one PRM108 edge"),
        ("I109-07", len(blocks) == 217 and blocks["unified_block_id"].nunique() == 175 and edge_blocks_ok and count_ok and prior_blocks_ok, "block graph closure and predecessor IDs"),
        ("I109-08", len(policy) == 24 and policy["selection_status"].eq("not_selected").all() and locks_ok, "cohort unselected and locks intact"),
    ]
    qa = pd.DataFrame(
        [
            {
                "check_id": check_id,
                "status": "PASS" if condition else "FAIL",
                "detail": detail,
            }
            for check_id, condition, detail in checks
        ]
    )
    (FACTORY / "reports").mkdir(parents=True, exist_ok=True)
    qa.to_csv(
        FACTORY / "reports" / "PRM109_independent_QA.csv",
        index=False,
        encoding="utf-8-sig",
    )
    summary = {
        "status": "PASS" if qa["status"].eq("PASS").all() else "FAIL",
        "checks": f"{qa['status'].eq('PASS').sum()}/{len(qa)}",
        "predecessor_values_within_1e-12_serialization_bound": bool(prior_ok),
        "cohort_values_within_1e-12_serialization_bound": bool(new_ok),
        "predecessor_block_ids_preserved": bool(prior_blocks_ok),
        "performance_y_read": 0,
    }
    (FACTORY / "reports" / "PRM109_independent_QA_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    if summary["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
