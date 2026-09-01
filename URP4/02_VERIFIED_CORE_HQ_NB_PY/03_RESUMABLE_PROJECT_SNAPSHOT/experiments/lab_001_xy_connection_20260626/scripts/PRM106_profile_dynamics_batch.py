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
FACTORY = LAB / "factories" / "PRM-106"
CONTRACT = FACTORY / "contracts" / "PRM-106_PROFILE_DYNAMICS_BATCH_CONTRACT_20260723.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1_048_576), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_variable(values: np.ndarray, label: str) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    if len(values) < 3 or not np.isfinite(values).all() or float(values.std(ddof=0)) <= 1e-12 or float(np.mean(np.abs(values))) <= 1e-12:
        raise RuntimeError(f"non-variable or non-positive profile: {label}")
    return values


def moment_skewness(values: np.ndarray) -> float:
    values = ensure_variable(values, "moment_skewness")
    centered = values - values.mean()
    sigma = np.sqrt(np.mean(centered ** 2))
    return float(np.mean(centered ** 3) / sigma ** 3)


def excess_kurtosis(values: np.ndarray) -> float:
    values = ensure_variable(values, "excess_kurtosis")
    centered = values - values.mean()
    variance = np.mean(centered ** 2)
    return float(np.mean(centered ** 4) / variance ** 2 - 3.0)


def peak_to_mean(values: np.ndarray) -> float:
    values = ensure_variable(values, "peak_to_mean")
    return float(values.max() / values.mean())


def range_over_mean(values: np.ndarray) -> float:
    values = ensure_variable(values, "range_over_mean")
    return float((values.max() - values.min()) / values.mean())


def lag1_autocorr(values: np.ndarray) -> float:
    values = ensure_variable(values, "lag1_autocorr")
    return float(np.corrcoef(values[:-1], values[1:])[0, 1])


def normalized_total_variation(values: np.ndarray) -> float:
    values = ensure_variable(values, "normalized_total_variation")
    return float(np.abs(np.diff(values)).mean() / np.abs(values).mean())


def variable(values: np.ndarray) -> bool:
    finite = values[np.isfinite(values)]
    return len(finite) >= 3 and len(np.unique(finite)) >= 3 and (finite.max() - finite.min()) > 1e-10 * max(1.0, np.max(np.abs(finite)))


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
    if len(models) != 58 or xreg["candidate_id"].nunique() != 171:
        raise RuntimeError("XREG-v0.5 scope mismatch")
    frozen = dict(zip(manifest["path"], manifest["sha256"]))
    raw_paths = []
    for model in models:
        raw_paths += [
            f".tmp/t4rs4/P1000_S801/{model}/tables/slice_pixel_readback.csv",
            f".tmp/t4rs4/P1000_S801/{model}/tables/overlay_pixel_readback.csv",
        ]
    if len(raw_paths) != 116 or any(path not in frozen for path in raw_paths):
        raise RuntimeError("raw source coverage mismatch")
    for path in raw_paths:
        if sha256(ROOT / path) != frozen[path]:
            raise RuntimeError(f"raw table hash mismatch: {path}")

    records: list[dict] = []
    metadata: dict[str, dict] = {}

    def put(model: str, candidate_id: str, value: float, grade: str, population: str, formula: str, source_table: str, anchor: str) -> None:
        records.append({"model_id": model, "model_family": family[model], "candidate_id": candidate_id, "value": float(value), "operational_grade": grade})
        group = candidate_id.split("::", 1)[0]
        metadata.setdefault(candidate_id, {
            "candidate_id": candidate_id,
            "candidate_group_id": group,
            "descriptor_family": "slice_profile_shape" if group == "RAW-X038" else ("overlay_phase_profile_dynamics" if group == "RAW-X039" else "overlay_phase_fraction_dynamics"),
            "output_name": candidate_id.split("::", 1)[1],
            "unit": "dimensionless",
            "source_population": population,
            "aggregation_formula": formula,
            "applicable_family": "B|C|F|L|T",
            "direct_or_derived": "direct_from_verified_SLICE004_raw_table" if grade == "B" else "derived_from_verified_SLICE004_profile",
            "source_bank": "PRM106_profile_dynamics_batch",
            "source_value_table": "PRM106_profile_dynamics_values_long.csv",
            "technical_role": "batch_BC_candidate",
            "qualification_status": "full58_raw_table_batch_not_selected",
            "confidence_status": "confirmed_raw_table_lineage",
            "later_evaluation_role": "batch_BC_unselected_block_aware",
            "active_feature": False,
            "promoted": False,
            "y_evidence": False,
            "notes": "PRM106 profile-dynamics batch; no y, selection, promotion, mask or slicing",
            "operational_grade": grade,
            "literature_anchor": anchor,
            "anchor_scope": "1D slice/overlay profile dynamics analogue only; not a full 3D estimator",
        })

    for model in models:
        base = ROOT / f".tmp/t4rs4/P1000_S801/{model}/tables"
        slices = pd.read_csv(base / "slice_pixel_readback.csv").sort_values("slice_index")
        overlay = pd.read_csv(base / "overlay_pixel_readback.csv").sort_values("pair_index")
        if len(slices) != 801 or len(overlay) != 800 or not slices["slice_index"].is_unique or not overlay["pair_index"].is_unique:
            raise RuntimeError(f"profile row/index mismatch: {model}")
        for name, series, population in [
            ("slice_material_area", slices["material_area_mm2"].to_numpy(float), "801-slice material-area profile"),
            ("slice_component_count", slices["component_count_min2"].to_numpy(float), "801-slice connected-component-count profile"),
        ]:
            put(model, f"RAW-X038::{name}_moment_skewness", moment_skewness(series), "B", population, "third central moment / population std^3", "slice_pixel_readback.csv", "LIT-X033")
            put(model, f"RAW-X038::{name}_excess_kurtosis", excess_kurtosis(series), "B", population, "fourth central moment / population variance^2 - 3", "slice_pixel_readback.csv", "LIT-X033")
            put(model, f"RAW-X038::{name}_peak_to_mean", peak_to_mean(series), "C", population, "max(profile) / mean(profile)", "slice_pixel_readback.csv", "LIT-X033")
            put(model, f"RAW-X038::{name}_range_over_mean", range_over_mean(series), "C", population, "(max(profile) - min(profile)) / mean(profile)", "slice_pixel_readback.csv", "LIT-X033")
        union = overlay["union_pixel_count"].to_numpy(float)
        if not np.all(union > 0):
            raise RuntimeError(f"non-positive overlay union denominator: {model}")
        for channel in ["red", "blue", "purple", "union"]:
            series = overlay[f"{channel}_pixel_count"].to_numpy(float)
            put(model, f"RAW-X039::overlay_{channel}_pixel_count_lag1_autocorr", lag1_autocorr(series), "C", f"800-pair overlay {channel}-pixel-count profile", "lag-1 Pearson autocorrelation across consecutive overlay pairs", "overlay_pixel_readback.csv", "LIT-X028")
            put(model, f"RAW-X039::overlay_{channel}_pixel_count_normalized_total_variation", normalized_total_variation(series), "C", f"800-pair overlay {channel}-pixel-count profile", "mean(abs(adjacent difference)) / mean(abs(profile))", "overlay_pixel_readback.csv", "LIT-X028")
        for channel in ["red", "blue", "purple"]:
            fractions = overlay[f"{channel}_pixel_count"].to_numpy(float) / union
            put(model, f"RAW-X040::overlay_{channel}_fraction_population_std", float(fractions.std(ddof=0)), "C", f"800-pair overlay {channel}/union phase-fraction profile", "population std across 800 phase fractions (ddof=0)", "overlay_pixel_readback.csv", "LIT-X028")
            put(model, f"RAW-X040::overlay_{channel}_fraction_lag1_autocorr", lag1_autocorr(fractions), "C", f"800-pair overlay {channel}/union phase-fraction profile", "lag-1 Pearson autocorrelation across consecutive phase fractions", "overlay_pixel_readback.csv", "LIT-X028")

    values = pd.DataFrame(records)
    registry = pd.DataFrame(metadata.values()).sort_values("candidate_id").reset_index(drop=True)
    candidate_ids = registry["candidate_id"].tolist()
    expected = contract["expected"]
    if len(candidate_ids) != expected["new_candidates"] or len(values) != expected["values"] or not np.isfinite(values["value"].to_numpy(float)).all():
        raise RuntimeError("candidate/value scope mismatch")
    if (registry["operational_grade"] == "B").sum() != expected["grade_B_candidates"] or (registry["operational_grade"] == "C").sum() != expected["grade_C_candidates"]:
        raise RuntimeError("grade schema mismatch")
    wide = values.pivot(index="model_id", columns="candidate_id", values="value").reindex(index=models, columns=candidate_ids)
    coverage = []
    for candidate_id in candidate_ids:
        vector = wide[candidate_id].to_numpy(float)
        coverage.append({"candidate_id": candidate_id, "finite_count": int(np.isfinite(vector).sum()), "missing_count": int((~np.isfinite(vector)).sum()), "unique_count": int(np.unique(vector).size), "population_std_across_models": float(vector.std(ddof=0)), "iqr_across_models": float(np.quantile(vector, 0.75) - np.quantile(vector, 0.25)), "operational_grade": registry.set_index("candidate_id").loc[candidate_id, "operational_grade"], "technical_status": "batch_BC_unselected"})
    xreg_by_candidate = {candidate_id: group.set_index("model_id").reindex(models)["value"].to_numpy(float) for candidate_id, group in xreg.groupby("candidate_id")}
    crossbank = []
    for candidate_id in candidate_ids:
        vector = wide[candidate_id].to_numpy(float)
        for existing_id, existing_values in sorted(xreg_by_candidate.items()):
            crossbank.append({"candidate_id": candidate_id, "existing_candidate_id": existing_id, **relation(vector, existing_values), "evidence_scope": "full58_x_only", "selection_effect": "none"})
    internal = []
    for index, left_id in enumerate(candidate_ids):
        for right_id in candidate_ids[index + 1:]:
            internal.append({"left_candidate_id": left_id, "right_candidate_id": right_id, **relation(wide[left_id].to_numpy(float), wide[right_id].to_numpy(float)), "evidence_scope": "full58_x_only", "selection_effect": "none"})
    collision = []
    for left_model, right_model, pair_id in [("T8", "T9", "T8_T9"), ("T5", "T6", "T5_T6")]:
        for candidate_id in candidate_ids:
            left_value, right_value = wide.loc[left_model, candidate_id], wide.loc[right_model, candidate_id]
            collision.append({"pair_id": pair_id, "candidate_id": candidate_id, "absolute_delta": abs(left_value - right_value), "relative_delta": abs(left_value - right_value) / max(abs(left_value), abs(right_value), 1e-12), "diagnostic_only": True})

    TABLES.mkdir(parents=True, exist_ok=True)
    (FACTORY / "reports").mkdir(parents=True, exist_ok=True)
    registry.to_csv(TABLES / "PRM106_profile_dynamics_candidate_registry.csv", index=False, encoding="utf-8-sig")
    values.to_csv(TABLES / "PRM106_profile_dynamics_values_long.csv", index=False, encoding="utf-8-sig", float_format="%.17g")
    wide.reset_index().to_csv(TABLES / "PRM106_profile_dynamics_values_wide.csv", index=False, encoding="utf-8-sig", float_format="%.17g")
    pd.DataFrame(coverage).to_csv(TABLES / "PRM106_profile_dynamics_coverage_variation.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(crossbank).to_csv(TABLES / "PRM106_profile_dynamics_vs_XREG_v0_5_redundancy.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(internal).to_csv(TABLES / "PRM106_profile_dynamics_internal_redundancy.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(collision).to_csv(TABLES / "PRM106_profile_dynamics_collision_diagnostic.csv", index=False, encoding="utf-8-sig")
    qa = [
        ("P106-01", len(models) == 58, "58 XREG-v0.5 models"),
        ("P106-02", len(raw_paths) == 116, "116 hash-verified slice/overlay raw sources"),
        ("P106-03", len(candidate_ids) == 22 and len(registry) == 22, "22 candidates"),
        ("P106-04", len(values) == 1276 and np.isfinite(values["value"].to_numpy(float)).all(), "1,276 finite values"),
        ("P106-05", len(crossbank) == 22 * 171, "3,762 x-only crossbank relations"),
        ("P106-06", len(internal) == 22 * 21 // 2, "231 internal x-only relations"),
        ("P106-07", len(collision) == 44, "two collision pairs x 22 candidates"),
        ("P106-08", not registry["active_feature"].any() and not registry["promoted"].any() and not registry["y_evidence"].any(), "no y, selection or promotion"),
    ]
    producer = pd.DataFrame([{"check_id": check_id, "status": "PASS" if ok else "FAIL", "detail": detail} for check_id, ok, detail in qa])
    producer.to_csv(FACTORY / "reports" / "PRM106_producer_QA.csv", index=False, encoding="utf-8-sig")
    summary = {"status": "PASS" if producer["status"].eq("PASS").all() else "FAIL", "checks": f"{producer['status'].eq('PASS').sum()}/{len(producer)}", "models": 58, "candidates": 22, "grade_B": 4, "grade_C": 18, "values": 1276, "y_fit_selection_promotion": "0/0/0/0"}
    (FACTORY / "reports" / "PRM106_batch_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if summary["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
