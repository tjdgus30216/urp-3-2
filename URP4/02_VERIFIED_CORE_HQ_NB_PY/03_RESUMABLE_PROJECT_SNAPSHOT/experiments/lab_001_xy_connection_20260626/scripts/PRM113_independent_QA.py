from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
TABLES = LAB / "reports" / "tables"
FACTORY = LAB / "factories" / "PRM-113"
CONTRACT = FACTORY / "contracts" / "PRM-113_XREG_V0_9_WEIGHTED_QUANTILE_LOCATION_CONSOLIDATION_CONTRACT_20260723.json"


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
    prior_bank = pd.read_csv(TABLES / "PRM111_xreg_v0_8_candidate_bank.csv")
    prior_values = pd.read_csv(TABLES / "PRM111_xreg_v0_8_values_long.csv")
    prior_edges = pd.read_csv(TABLES / "PRM111_unified_redundancy_edge_registry.csv")
    cohort_bank = pd.read_csv(TABLES / "PRM112_axial_weighted_quantile_location_candidate_registry.csv")
    cohort_values = pd.read_csv(TABLES / "PRM112_axial_weighted_quantile_location_values_long.csv")
    internal = pd.read_csv(TABLES / "PRM112_axial_weighted_quantile_location_internal_redundancy.csv")
    bank = pd.read_csv(TABLES / "PRM113_xreg_v0_9_candidate_bank.csv")
    values = pd.read_csv(TABLES / "PRM113_xreg_v0_9_values_long.csv")
    wide = pd.read_csv(TABLES / "PRM113_xreg_v0_9_values_wide.csv")
    edges = pd.read_csv(TABLES / "PRM113_unified_redundancy_edge_registry.csv")
    blocks = pd.read_csv(TABLES / "PRM113_unified_redundancy_block_registry.csv")
    policy = pd.read_csv(TABLES / "PRM113_weighted_quantile_location_cohort_block_policy.csv")
    old = values[values.candidate_id.isin(prior_bank.candidate_id)].sort_values(["model_id","candidate_id"]).reset_index(drop=True)
    old_ref = prior_values.sort_values(["model_id","candidate_id"]).reset_index(drop=True)
    old_ok = len(old)==len(old_ref) and old[["model_id","candidate_id"]].equals(old_ref[["model_id","candidate_id"]]) and np.allclose(old.value, old_ref.value,rtol=1e-12,atol=1e-12,equal_nan=True)
    new = values[values.candidate_id.isin(cohort_bank.candidate_id)].sort_values(["model_id","candidate_id"]).reset_index(drop=True)
    new_ref = cohort_values.sort_values(["model_id","candidate_id"]).reset_index(drop=True)
    new_ok = len(new)==len(new_ref) and new[["model_id","candidate_id"]].equals(new_ref[["model_id","candidate_id"]]) and np.allclose(new.value,new_ref.value,rtol=1e-12,atol=1e-12)
    expected_pairs={pair(row.left_candidate_id,row.right_candidate_id) for row in internal[internal.relation.eq("high_redundancy")].itertuples(index=False)}
    added=edges[edges.edge_source.astype(str).str.startswith("PRM112_")]
    actual_pairs={pair(row.left_candidate_id,row.right_candidate_id) for row in added.itertuples(index=False)}
    predecessor_edges_ok=edges.iloc[:len(prior_edges)][prior_edges.columns].astype(str).equals(prior_edges.astype(str))
    prior_block=prior_bank.set_index("candidate_id").unified_block_id.to_dict(); new_block=bank.set_index("candidate_id").unified_block_id.to_dict()
    unchanged_prior=all(new_block[candidate]==block for candidate,block in prior_block.items())
    lookup=blocks.set_index("candidate_id").unified_block_id.to_dict()
    edge_blocks_ok=all(lookup[row.left_candidate_id]==lookup[row.right_candidate_id] for row in edges.itertuples(index=False))
    member_counts=blocks.groupby("unified_block_id").candidate_id.size().to_dict()
    counts_ok=all(int(row.unified_block_member_count)==member_counts[row.unified_block_id] for row in blocks.itertuples(index=False))
    locks_ok=not bank.active_feature.any() and not bank.promoted.any() and bank.y_evidence.astype(str).str.lower().eq("false").all() and all(value==0 for value in contract["locks"].values())
    checks=[
        ("I113-01",hashes_ok,"all eight input hashes"),
        ("I113-02",len(bank)==265 and bank.candidate_id.nunique()==265,"265 candidates"),
        ("I113-03",len(values)==15370 and int(values.value.notna().sum())==15368 and wide.shape==(58,267),"values/matrix and inherited missingness"),
        ("I113-04",old_ok,"predecessor v0.8 rows/values within 1e-12 serialization bound"),
        ("I113-05",new_ok,"PRM112 rows/values within 1e-12 serialization bound"),
        ("I113-06",len(edges)==60 and len(added)==1 and actual_pairs==expected_pairs and predecessor_edges_ok,"59 prior plus exact PRM112 edge"),
        ("I113-07",len(blocks)==265 and blocks.unified_block_id.nunique()==216 and unchanged_prior and edge_blocks_ok and counts_ok,"graph closure and all predecessor block IDs unchanged"),
        ("I113-08",len(policy)==24 and policy.block_status.value_counts().to_dict()=={"singleton":22,"internal_high_redundancy_block":2} and policy.selection_status.eq("not_selected").all() and locks_ok,"cohort policy and locks"),
    ]
    qa=pd.DataFrame([{"check_id":cid,"status":"PASS" if ok else "FAIL","detail":detail} for cid,ok,detail in checks])
    (FACTORY/"reports").mkdir(parents=True,exist_ok=True)
    qa.to_csv(FACTORY/"reports"/"PRM113_independent_QA.csv",index=False,encoding="utf-8-sig")
    summary={"status":"PASS" if qa.status.eq("PASS").all() else "FAIL","checks":f"{qa.status.eq('PASS').sum()}/{len(qa)}","predecessor_values_within_1e-12_serialization_bound":bool(old_ok),"cohort_values_within_1e-12_serialization_bound":bool(new_ok),"predecessor_block_ids_unchanged":bool(unchanged_prior),"performance_y_read":0}
    (FACTORY/"reports"/"PRM113_independent_QA_summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2))
    if summary["status"]!="PASS":raise SystemExit(1)


if __name__=="__main__":main()
