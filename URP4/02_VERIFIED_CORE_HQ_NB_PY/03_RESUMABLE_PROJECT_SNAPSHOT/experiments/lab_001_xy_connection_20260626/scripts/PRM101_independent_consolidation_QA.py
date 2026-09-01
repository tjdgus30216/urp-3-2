from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
TABLES = LAB / "reports" / "tables"
FACTORY = LAB / "factories" / "PRM-101"
CONTRACT = FACTORY / "contracts" / "PRM-101_XREG_V0_3_CONSOLIDATION_CONTRACT_20260723.json"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for c in iter(lambda: f.read(1024 * 1024), b""):
            h.update(c)
    return h.hexdigest()


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    checks: list[dict[str, object]] = []
    def add(k: str, ok: bool, got: object, want: object) -> None: checks.append({"check_id":k,"status":"PASS" if ok else "FAIL","observed":got,"expected":want})
    for i, item in enumerate(contract["inputs"], start=1):
        add(f"I101-{i:02d}_immutable_input", sha(ROOT / item["path"]) == item["sha256"], item["path"], "hash exact")
    bank = pd.read_csv(TABLES / "PRM101_xreg_v0_3_candidate_bank.csv")
    values = pd.read_csv(TABLES / "PRM101_xreg_v0_3_values_long.csv")
    wide = pd.read_csv(TABLES / "PRM101_xreg_v0_3_values_wide.csv")
    edges = pd.read_csv(TABLES / "PRM101_unified_redundancy_edge_registry.csv")
    blocks = pd.read_csv(TABLES / "PRM101_unified_redundancy_block_registry.csv")
    policy = pd.read_csv(TABLES / "PRM101_third_wave_block_policy.csv")
    prior = pd.read_csv(TABLES / "PRM096_xreg_v0_2_values_long.csv")
    source = pd.read_csv(TABLES / "PRM099_third_wave_full58_six_values_long.csv")
    new_ids = set(source.candidate_id.unique())
    add("I101-10_bank_scope", len(bank)==114 and bank.candidate_id.nunique()==114 and bank.bank_version.eq("XREG-v0.3-TECHNICAL").all(), f"{len(bank)}/{bank.candidate_id.nunique()}", "114/114")
    add("I101-11_locks", not bank.active_feature.any() and not bank.promoted.any() and not bank.y_evidence.any(), "all false", "all false")
    add("I101-12_value_scope", len(values)==6612 and values.model_id.nunique()==58 and values.candidate_id.nunique()==114 and values.value.notna().sum()==6610 and values.loc[values.candidate_id.isin(new_ids),"value"].notna().all(), f"{len(values)} rows/{values.value.notna().sum()} finite", "6612 rows/6610 finite; no new missingness")
    old = values[~values.candidate_id.isin(new_ids)].copy(); old["bank_version"]="XREG-v0.2-TECHNICAL"
    cols=["bank_version","model_id","model_family","candidate_id","value","finite","source_bank"]
    old=old.sort_values(cols[:4]).reset_index(drop=True); prior=prior.sort_values(cols[:4]).reset_index(drop=True)
    same_meta=old[["bank_version","model_id","model_family","candidate_id","finite","source_bank"]].equals(prior[["bank_version","model_id","model_family","candidate_id","finite","source_bank"]])
    same_values=np.allclose(old.value.to_numpy(), prior.value.to_numpy(), rtol=1e-14, atol=2e-15, equal_nan=True)
    add("I101-13_prior_value_immutability", same_meta and same_values, len(old), 6264)
    new = values[values.candidate_id.isin(new_ids)][["model_id","candidate_id","value"]].sort_values(["model_id","candidate_id"]).reset_index(drop=True)
    src = source.sort_values(["model_id","candidate_id"]).reset_index(drop=True)
    add("I101-14_new_value_lineage", new[["model_id","candidate_id"]].equals(src[["model_id","candidate_id"]]) and np.allclose(new.value.to_numpy(), src.value.to_numpy(), rtol=1e-14, atol=2e-15), len(new), 348)
    rebuilt = values.pivot(index=["model_id","model_family"], columns="candidate_id", values="value").reindex(columns=bank.candidate_id.tolist()).reset_index()
    wide_values_match=np.allclose(rebuilt.iloc[:,2:].to_numpy(float), wide.iloc[:,2:].to_numpy(float), rtol=1e-14, atol=2e-15, equal_nan=True)
    add("I101-15_wide_replay", rebuilt.shape==wide.shape and rebuilt.columns.tolist()==wide.columns.tolist() and rebuilt.iloc[:,:2].equals(wide.iloc[:,:2]) and wide_values_match, str(wide.shape), "(58,116) numeric replay including inherited NA")
    b44=set(blocks.loc[blocks.unified_block_id.eq("U096-BLK-044"),"candidate_id"])
    want={"LIT-X004::chi_solid_26","LIT-X004::chi_solid_26_per_mm3","LIT-X024::ect_abs_auc_direction_mean_per_mm3"}
    add("I101-16_block_policy", blocks.unified_block_id.nunique()==94 and len(blocks)==114 and b44==want, f"{blocks.unified_block_id.nunique()}/{len(blocks)}", "94/114 with exact U096-BLK-044")
    newedge=edges[edges.edge_id.isin(["U101-EDGE-024","U101-EDGE-025"])]
    add("I101-17_edge_policy", len(edges)==25 and len(newedge)==2 and newedge.relation.eq("high_redundancy").all(), len(edges), 25)
    add("I101-18_disposition", len(policy)==6 and policy.selection_status.eq("not_selected").all() and policy.y_access.astype(str).str.lower().eq("false").all(), len(policy), 6)
    observed_y_columns=[c for c in list(bank.columns)+list(values.columns)+list(policy.columns) if str(c).lower().startswith("y_") and str(c).lower() not in {"y_evidence", "y_access"}]
    add("I101-19_no_y_target_data", not observed_y_columns and bank.y_evidence.astype(str).str.lower().eq("false").all(), observed_y_columns, "no performance-y target columns; y_evidence all false")
    add("I101-20_contract_locks", all(v==0 for v in contract["locks"].values()), contract["locks"], "all zero")
    out=pd.DataFrame(checks); out.to_csv(FACTORY/"reports"/"PRM101_independent_QA.csv",index=False,encoding="utf-8-sig")
    failed=out.loc[out.status.ne("PASS"),"check_id"].tolist()
    final={"status":"PASS" if not failed else "FAIL","checks":f"{len(out)-len(failed)}/{len(out)}","failed":failed,"y_fit_selection_promotion":"0/0/0/0"}
    (FACTORY/"reports"/"PRM101_independent_QA_summary.json").write_text(json.dumps(final,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(final,indent=2))
    if failed: raise SystemExit(1)


if __name__ == "__main__": main()
