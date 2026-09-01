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
FACTORY = LAB / "factories" / "PRM-104"
CONTRACT = FACTORY / "contracts" / "PRM-104_OVERLAY_PHASE_PROFILE_BATCH_CONTRACT_20260723.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1_048_576), b""):
            digest.update(chunk)
    return digest.hexdigest()


def profile_stats(values: np.ndarray) -> dict[str, float]:
    values = np.asarray(values, dtype=float)
    q10, q25, q50, q75, q90 = np.quantile(values, [0.10, 0.25, 0.50, 0.75, 0.90])
    return {
        "mean": float(values.mean()),
        "population_std": float(values.std(ddof=0)),
        "q10": float(q10),
        "q50": float(q50),
        "q90": float(q90),
        "iqr": float(q75 - q25),
        "mad": float(np.median(np.abs(values - q50))),
    }


def variable(values: np.ndarray) -> bool:
    values = values[np.isfinite(values)]
    return len(values) >= 3 and len(np.unique(values)) >= 3 and (values.max() - values.min()) > 1e-10 * max(1.0, np.max(np.abs(values)))


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
    pearson = float(pearsonr(left, right).statistic)
    spearman = float(spearmanr(left, right).statistic)
    kind = "proportional_duplicate" if residual <= 1e-6 and abs(slope) > 1e-12 else ("high_redundancy" if abs(pearson) >= 0.98 and abs(spearman) >= 0.98 else "distinct_or_unresolved")
    return {"common_models": 58, "relation": kind, "pearson": pearson, "spearman": spearman, "normalized_L2_residual": residual}


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    for item in contract["inputs"]:
        if sha256(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError(f"input hash mismatch: {item['path']}")

    manifest = pd.read_csv(ROOT / contract["inputs"][0]["path"])
    xreg = pd.read_csv(ROOT / contract["inputs"][1]["path"])
    models = sorted(xreg["model_id"].unique())
    family = xreg[["model_id", "model_family"]].drop_duplicates().set_index("model_id")["model_family"].to_dict()
    if len(models) != 58 or len(family) != 58:
        raise RuntimeError("XREG-v0.4 model coverage mismatch")

    frozen_hashes = dict(zip(manifest["path"], manifest["sha256"]))
    raw_paths = [f".tmp/t4rs4/P1000_S801/{model}/tables/overlay_pixel_readback.csv" for model in models]
    if len(raw_paths) != 58 or any(path not in frozen_hashes for path in raw_paths):
        raise RuntimeError("SLICE-004 overlay raw-file manifest coverage mismatch")
    for raw_path in raw_paths:
        if sha256(ROOT / raw_path) != frozen_hashes[raw_path]:
            raise RuntimeError(f"raw table hash mismatch: {raw_path}")

    records: list[dict] = []
    metadata: dict[str, dict] = {}

    def put(model: str, candidate_id: str, value: float, grade: str, unit: str, population: str, formula: str, direct: str) -> None:
        records.append({"model_id": model, "model_family": family[model], "candidate_id": candidate_id, "value": float(value), "operational_grade": grade})
        metadata.setdefault(candidate_id, {
            "candidate_id": candidate_id,
            "candidate_group_id": "RAW-X036" if candidate_id.startswith("RAW-X036") else "RAW-X037",
            "descriptor_family": "overlay_color_phase_profile" if candidate_id.startswith("RAW-X036") else "overlay_color_phase_composition",
            "output_name": candidate_id.split("::", 1)[1],
            "unit": unit,
            "source_population": population,
            "aggregation_formula": formula,
            "applicable_family": "B|C|F|L|T",
            "direct_or_derived": direct,
            "source_bank": "PRM104_overlay_phase_profile_batch",
            "source_value_table": "PRM104_overlay_phase_profile_values_long.csv",
            "technical_role": "batch_BC_candidate",
            "qualification_status": "full58_raw_table_batch_not_selected",
            "confidence_status": "confirmed_raw_table_lineage",
            "later_evaluation_role": "batch_BC_unselected_block_aware",
            "active_feature": False,
            "promoted": False,
            "y_evidence": False,
            "notes": "PRM-104 overlay_pixel_readback batch; no y, selection, promotion, mask or slicing",
            "operational_grade": grade,
            "literature_anchor": "LIT-X028",
            "anchor_scope": "overlay phase-profile/composition analogue only; not a GLCM or full 3D estimator",
        })

    channels = ["red", "blue", "purple"]
    for model in models:
        raw = pd.read_csv(ROOT / f".tmp/t4rs4/P1000_S801/{model}/tables/overlay_pixel_readback.csv").sort_values("pair_index")
        if len(raw) != 800 or not raw["pair_index"].is_unique:
            raise RuntimeError(f"pair population mismatch: {model}")
        union = raw["union_pixel_count"].to_numpy(float)
        if not np.all(union > 0):
            raise RuntimeError(f"non-positive union denominator: {model}")
        for channel in channels:
            values = raw[f"{channel}_pixel_count"].to_numpy(float)
            for name, value in profile_stats(values).items():
                put(
                    model,
                    f"RAW-X036::overlay_{channel}_pixel_count_{name}",
                    value,
                    "B",
                    "pixel_count",
                    f"800-pair overlay {channel}-pixel-count profile",
                    f"population {name} across 800 pairs (ddof=0 for population_std)",
                    "direct_from_verified_SLICE004_raw_table",
                )
        for name in ["mean", "population_std", "q50", "iqr"]:
            value = profile_stats(union)[name]
            put(
                model,
                f"RAW-X036::overlay_union_pixel_count_{name}",
                value,
                "B",
                "pixel_count",
                "800-pair overlay union-pixel-count profile",
                f"population {name} across 800 pairs (ddof=0 for population_std)",
                "direct_from_verified_SLICE004_raw_table",
            )
        for channel in channels:
            fraction = raw[f"{channel}_pixel_count"].to_numpy(float) / union
            put(
                model,
                f"RAW-X037::overlay_{channel}_fraction_mean",
                float(fraction.mean()),
                "C",
                "dimensionless_fraction",
                f"800-pair overlay {channel}/union phase-fraction profile",
                f"mean({channel}_pixel_count / union_pixel_count) across 800 pairs; positive denominator verified",
                "derived_from_verified_SLICE004_profile",
            )

    values = pd.DataFrame(records)
    registry = pd.DataFrame(metadata.values()).sort_values("candidate_id").reset_index(drop=True)
    candidate_ids = registry["candidate_id"].tolist()
    expected = contract["expected"]
    if len(candidate_ids) != expected["new_candidates"] or len(values) != expected["values"] or not np.isfinite(values["value"]).all():
        raise RuntimeError(f"batch scope failure: {len(candidate_ids)} candidates / {len(values)} values")
    if (registry["operational_grade"] == "B").sum() != expected["grade_B_candidates"] or (registry["operational_grade"] == "C").sum() != expected["grade_C_candidates"]:
        raise RuntimeError("grade scope mismatch")

    wide = values.pivot(index="model_id", columns="candidate_id", values="value").reindex(index=models, columns=candidate_ids)
    coverage = []
    for candidate_id in candidate_ids:
        vector = wide[candidate_id].to_numpy(float)
        coverage.append({
            "candidate_id": candidate_id,
            "finite_count": int(np.isfinite(vector).sum()),
            "missing_count": int((~np.isfinite(vector)).sum()),
            "unique_count": int(np.unique(vector).size),
            "population_std_across_models": float(vector.std(ddof=0)),
            "iqr_across_models": float(np.quantile(vector, 0.75) - np.quantile(vector, 0.25)),
            "operational_grade": registry.set_index("candidate_id").loc[candidate_id, "operational_grade"],
            "technical_status": "batch_BC_unselected",
        })

    xreg_by_candidate = {candidate_id: group.set_index("model_id").reindex(models)["value"].to_numpy(float) for candidate_id, group in xreg.groupby("candidate_id")}
    crossbank = []
    for candidate_id in candidate_ids:
        vector = wide[candidate_id].to_numpy(float)
        for existing_id, existing_vector in sorted(xreg_by_candidate.items()):
            crossbank.append({"candidate_id": candidate_id, "existing_candidate_id": existing_id, **relation(vector, existing_vector), "evidence_scope": "full58_x_only", "selection_effect": "none"})
    internal = []
    for left_index, left_id in enumerate(candidate_ids):
        for right_id in candidate_ids[left_index + 1:]:
            internal.append({"left_candidate_id": left_id, "right_candidate_id": right_id, **relation(wide[left_id].to_numpy(float), wide[right_id].to_numpy(float)), "evidence_scope": "full58_x_only", "selection_effect": "none"})
    collisions = []
    for left_model, right_model, pair_id in [("T8", "T9", "T8_T9"), ("T5", "T6", "T5_T6")]:
        for candidate_id in candidate_ids:
            left_value, right_value = wide.loc[left_model, candidate_id], wide.loc[right_model, candidate_id]
            collisions.append({"pair_id": pair_id, "candidate_id": candidate_id, "absolute_delta": abs(left_value - right_value), "relative_delta": abs(left_value - right_value) / max(abs(left_value), abs(right_value), 1e-12), "diagnostic_only": True})

    TABLES.mkdir(parents=True, exist_ok=True)
    (FACTORY / "reports").mkdir(parents=True, exist_ok=True)
    registry.to_csv(TABLES / "PRM104_overlay_phase_profile_candidate_registry.csv", index=False, encoding="utf-8-sig")
    values.to_csv(TABLES / "PRM104_overlay_phase_profile_values_long.csv", index=False, encoding="utf-8-sig", float_format="%.17g")
    wide.reset_index().to_csv(TABLES / "PRM104_overlay_phase_profile_values_wide.csv", index=False, encoding="utf-8-sig", float_format="%.17g")
    pd.DataFrame(coverage).to_csv(TABLES / "PRM104_overlay_phase_profile_coverage_variation.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(crossbank).to_csv(TABLES / "PRM104_overlay_phase_profile_vs_XREG_v0_4_redundancy.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(internal).to_csv(TABLES / "PRM104_overlay_phase_profile_internal_redundancy.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(collisions).to_csv(TABLES / "PRM104_overlay_phase_profile_collision_diagnostic.csv", index=False, encoding="utf-8-sig")

    qa = [
        ("P104-01", len(models) == 58, "58 XREG-v0.4 models"),
        ("P104-02", len(raw_paths) == 58, "58 hash-verified overlay_pixel_readback sources"),
        ("P104-03", len(candidate_ids) == 28 and len(registry) == 28, "28 candidates"),
        ("P104-04", len(values) == 1624 and np.isfinite(values["value"]).all(), "1,624 finite values"),
        ("P104-05", len(crossbank) == 28 * 143, "4,004 x-only crossbank relations"),
        ("P104-06", len(internal) == 28 * 27 // 2, "378 internal x-only relations"),
        ("P104-07", len(collisions) == 56, "two collision pairs x 28 candidates"),
        ("P104-08", not registry["active_feature"].any() and not registry["promoted"].any() and not registry["y_evidence"].any(), "no y, selection or promotion"),
    ]
    producer_qa = pd.DataFrame([{"check_id": check_id, "status": "PASS" if ok else "FAIL", "detail": detail} for check_id, ok, detail in qa])
    producer_qa.to_csv(FACTORY / "reports" / "PRM104_producer_QA.csv", index=False, encoding="utf-8-sig")
    summary = {
        "status": "PASS" if producer_qa["status"].eq("PASS").all() else "FAIL",
        "checks": f"{producer_qa['status'].eq('PASS').sum()}/{len(producer_qa)}",
        "models": 58,
        "candidates": 28,
        "grade_B": 25,
        "grade_C": 3,
        "values": 1624,
        "y_fit_selection_promotion": "0/0/0/0",
    }
    (FACTORY / "reports" / "PRM104_batch_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if summary["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
