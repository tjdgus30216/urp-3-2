from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr

ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
TABLES = LAB / "reports" / "tables"
FACTORY = LAB / "factories" / "PRM-112"
CONTRACT = FACTORY / "contracts" / "PRM-112_AXIAL_WEIGHTED_QUANTILE_LOCATION_B_BATCH_CONTRACT_20260723.json"
QUANTILES = (0.10, 0.25, 0.75, 0.90)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1_048_576), b""):
            digest.update(chunk)
    return digest.hexdigest()


def weighted_position_quantile(profile: np.ndarray, q: float) -> float:
    profile = np.asarray(profile, dtype=float)
    if (len(profile) < 4 or not np.isfinite(profile).all() or np.any(profile < 0)
            or profile.sum() <= 1e-12 or not 0.0 < q < 1.0):
        raise RuntimeError("invalid profile or quantile")
    position = np.linspace(0.0, 1.0, len(profile))
    index = int(np.searchsorted(np.cumsum(profile) / profile.sum(), q, side="left"))
    return float(position[min(index, len(position) - 1)])


def variable(values: np.ndarray) -> bool:
    values = values[np.isfinite(values)]
    return len(values) >= 3 and len(np.unique(values)) >= 3 and (values.max() - values.min()) > 1e-10 * max(1.0, np.abs(values).max())


def relation(left: np.ndarray, right: np.ndarray) -> dict[str, float | int | str]:
    common = np.isfinite(left) & np.isfinite(right)
    left, right = left[common], right[common]
    if len(left) != 58:
        return {"common_models": int(len(left)), "relation": "insufficient_common_coverage", "pearson": np.nan, "spearman": np.nan, "normalized_L2_residual": np.nan}
    if not variable(left) or not variable(right):
        return {"common_models": 58, "relation": "degenerate_nonvarying_reference_or_candidate", "pearson": np.nan, "spearman": np.nan, "normalized_L2_residual": np.nan}
    if np.allclose(left, right, rtol=1e-10, atol=1e-12):
        return {"common_models": 58, "relation": "exact_duplicate", "pearson": 1.0, "spearman": 1.0, "normalized_L2_residual": 0.0}
    slope = float(np.dot(left, right) / np.dot(left, left))
    residual = float(np.linalg.norm(right - slope * left) / max(np.linalg.norm(right), 1e-30))
    pearson, spearman = float(pearsonr(left, right).statistic), float(spearmanr(left, right).statistic)
    kind = "proportional_duplicate" if residual <= 1e-6 and abs(slope) > 1e-12 else ("high_redundancy" if abs(pearson) >= .98 and abs(spearman) >= .98 else "distinct_or_unresolved")
    return {"common_models": 58, "relation": kind, "pearson": pearson, "spearman": spearman, "normalized_L2_residual": residual}


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    for item in contract["inputs"]:
        if sha256(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError(f"input hash mismatch: {item['path']}")
    manifest = pd.read_csv(ROOT / contract["inputs"][0]["path"])
    xreg = pd.read_csv(ROOT / contract["inputs"][2]["path"])
    models = sorted(xreg["model_id"].unique())
    family = xreg[["model_id", "model_family"]].drop_duplicates().set_index("model_id")["model_family"].to_dict()
    if len(models) != 58 or xreg["candidate_id"].nunique() != 241:
        raise RuntimeError("XREG-v0.8 scope mismatch")
    frozen = dict(zip(manifest["path"], manifest["sha256"]))
    raw_paths = [f".tmp/t4rs4/P1000_S801/{model}/tables/{name}" for model in models for name in ("slice_pixel_readback.csv", "overlay_pixel_readback.csv")]
    if len(raw_paths) != 116 or any(path not in frozen or sha256(ROOT / path) != frozen[path] for path in raw_paths):
        raise RuntimeError("raw source hash/coverage mismatch")

    records, metadata = [], {}
    profile_specs = {
        "slice_material_area": ("slice_pixel_readback.csv", "material_area_mm2", "801-row slice material-area ordered profile"),
        "slice_component_count": ("slice_pixel_readback.csv", "component_count_min2", "801-row slice min2-component-count ordered profile"),
        "overlay_red_pixel_count": ("overlay_pixel_readback.csv", "red_pixel_count", "800-pair overlay red-pixel-count ordered profile"),
        "overlay_blue_pixel_count": ("overlay_pixel_readback.csv", "blue_pixel_count", "800-pair overlay blue-pixel-count ordered profile"),
        "overlay_purple_pixel_count": ("overlay_pixel_readback.csv", "purple_pixel_count", "800-pair overlay purple-pixel-count ordered profile"),
        "overlay_union_pixel_count": ("overlay_pixel_readback.csv", "union_pixel_count", "800-pair overlay union-pixel-count ordered profile"),
    }
    for model in models:
        base = ROOT / f".tmp/t4rs4/P1000_S801/{model}/tables"
        slice_df = pd.read_csv(base / "slice_pixel_readback.csv").sort_values("slice_index")
        overlay_df = pd.read_csv(base / "overlay_pixel_readback.csv").sort_values("pair_index")
        if len(slice_df) != 801 or len(overlay_df) != 800 or not slice_df["slice_index"].is_unique or not overlay_df["pair_index"].is_unique:
            raise RuntimeError(f"profile index mismatch: {model}")
        for profile_name, (file_name, column, population) in profile_specs.items():
            frame = slice_df if file_name.startswith("slice") else overlay_df
            profile = frame[column].to_numpy(float)
            for q in QUANTILES:
                q_label = f"q{int(q * 100):02d}"
                candidate_id = f"RAW-X047::{profile_name}_weighted_axial_{q_label}_position"
                value = weighted_position_quantile(profile, q)
                records.append({"model_id": model, "model_family": family[model], "candidate_id": candidate_id, "value": value, "operational_grade": "B"})
                metadata.setdefault(candidate_id, {
                    "candidate_id": candidate_id, "candidate_group_id": "RAW-X047", "descriptor_family": "axial_weighted_quantile_location",
                    "output_name": candidate_id.split("::", 1)[1], "unit": "dimensionless", "source_population": population,
                    "aggregation_formula": f"min z_norm where cumulative(profile)/sum(profile) >= {q:.2f}", "applicable_family": "B|C|F|L|T",
                    "direct_or_derived": "direct_statistic_from_verified_SLICE004_profile", "source_bank": "PRM112_axial_weighted_quantile_location_batch",
                    "source_value_table": "PRM112_axial_weighted_quantile_location_values_long.csv", "technical_role": "batch_B_candidate",
                    "qualification_status": "full58_raw_table_batch_not_selected", "confidence_status": "confirmed_raw_table_lineage",
                    "later_evaluation_role": "batch_B_unselected_block_aware", "active_feature": False, "promoted": False, "y_evidence": False,
                    "notes": "PRM112 weighted axial quantile-location batch; no y, selection, mask or slicing", "operational_grade": "B",
                    "literature_anchor": "LIT-X033", "anchor_scope": "robust normalized 1D axial distribution-location statistic only; not a full 3D topology estimator"})

    values = pd.DataFrame(records)
    registry = pd.DataFrame(metadata.values()).sort_values("candidate_id").reset_index(drop=True)
    candidate_ids = registry["candidate_id"].tolist()
    if len(candidate_ids) != 24 or len(values) != 1392 or not np.isfinite(values["value"].to_numpy(float)).all():
        raise RuntimeError("candidate/value scope mismatch")
    wide = values.pivot(index="model_id", columns="candidate_id", values="value").reindex(index=models, columns=candidate_ids)
    coverage = [{"candidate_id": cid, "finite_count": int(np.isfinite(wide[cid]).sum()), "missing_count": int((~np.isfinite(wide[cid])).sum()), "unique_count": int(wide[cid].nunique()), "population_std_across_models": float(wide[cid].std(ddof=0)), "iqr_across_models": float(np.quantile(wide[cid], .75)-np.quantile(wide[cid], .25)), "operational_grade": "B", "technical_status": "batch_B_unselected"} for cid in candidate_ids]
    old_vectors = {cid: group.set_index("model_id").reindex(models)["value"].to_numpy(float) for cid, group in xreg.groupby("candidate_id")}
    crossbank = [{"candidate_id": cid, "existing_candidate_id": old_id, **relation(wide[cid].to_numpy(float), old), "evidence_scope": "full58_x_only", "selection_effect": "none"} for cid in candidate_ids for old_id, old in sorted(old_vectors.items())]
    internal = [{"left_candidate_id": left, "right_candidate_id": right, **relation(wide[left].to_numpy(float), wide[right].to_numpy(float)), "evidence_scope": "full58_x_only", "selection_effect": "none"} for i, left in enumerate(candidate_ids) for right in candidate_ids[i+1:]]
    collisions = [{"pair_id": pair, "candidate_id": cid, "absolute_delta": abs(float(wide.loc[left, cid])-float(wide.loc[right, cid])), "relative_delta": abs(float(wide.loc[left,cid])-float(wide.loc[right,cid]))/max(abs(float(wide.loc[left,cid])),abs(float(wide.loc[right,cid])),1e-12), "diagnostic_only": True} for left,right,pair in (("T8","T9","T8_T9"),("T5","T6","T5_T6")) for cid in candidate_ids]
    outputs = {"candidate_registry": registry, "values_long": values, "values_wide": wide.reset_index(), "coverage_variation": pd.DataFrame(coverage), "vs_XREG_v0_8_redundancy": pd.DataFrame(crossbank), "internal_redundancy": pd.DataFrame(internal), "collision_diagnostic": pd.DataFrame(collisions)}
    for suffix, frame in outputs.items():
        frame.to_csv(TABLES / f"PRM112_axial_weighted_quantile_location_{suffix}.csv", index=False, encoding="utf-8-sig", float_format="%.17g")
    checks = [("P112-01", len(models)==58, "58 XREG-v0.8 models"), ("P112-02", len(raw_paths)==116, "116 hash-verified raw sources"), ("P112-03", len(candidate_ids)==24 and (registry["operational_grade"]=="B").sum()==24, "24 Grade-B candidates"), ("P112-04", len(values)==1392 and np.isfinite(values["value"]).all(), "1,392 finite values"), ("P112-05", len(crossbank)==24*241, "5,784 crossbank relations"), ("P112-06", len(internal)==276, "276 internal relations"), ("P112-07", len(collisions)==48, "two collision pairs x 24"), ("P112-08", not registry[["active_feature","promoted","y_evidence"]].any().any() and all(v==0 for v in contract["locks"].values()), "no y, selection or promotion and locks intact")]
    qa = pd.DataFrame([{"check_id":c, "status":"PASS" if ok else "FAIL", "detail":d} for c,ok,d in checks])
    (FACTORY / "reports").mkdir(parents=True, exist_ok=True)
    qa.to_csv(FACTORY / "reports" / "PRM112_producer_QA.csv", index=False, encoding="utf-8-sig")
    summary={"status":"PASS" if qa.status.eq("PASS").all() else "FAIL", "checks":f"{qa.status.eq('PASS').sum()}/{len(qa)}", "models":58, "candidates":24, "grade_B":24, "grade_C":0, "values":1392, "y_fit_selection_promotion":"0/0/0/0"}
    (FACTORY / "reports" / "PRM112_batch_summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2))
    if summary["status"] != "PASS": raise SystemExit(1)


if __name__ == "__main__":
    main()
