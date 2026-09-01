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
FACTORY = LAB / "factories" / "PRM-120"
CONTRACT = FACTORY / "contracts" / "PRM-120_OVERLAY_PAIR_COMPONENT_COMPOSITION_BC_BATCH_CONTRACT_20260723.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1_048_576), b""):
            digest.update(chunk)
    return digest.hexdigest()


def gini(values: np.ndarray) -> float:
    values = np.sort(np.asarray(values, dtype=float))
    count = len(values)
    if count <= 1:
        return 0.0
    total = values.sum()
    return float(np.dot(2 * np.arange(1, count + 1) - count - 1, values) / (count * total))


def pair_composition_profile(frame: pd.DataFrame) -> dict[str, np.ndarray]:
    effective_count, top2_share, area_cv, area_gini = [], [], [], []
    for _, group in frame.groupby("pair_index", sort=True):
        areas = group.area_mm2.to_numpy(float)
        total = areas.sum()
        weights = areas / total
        effective_count.append(float(1.0 / np.dot(weights, weights)))
        top2_share.append(float(np.sort(weights)[-2:].sum()))
        area_cv.append(float(areas.std(ddof=0) / areas.mean()) if len(areas) > 1 else 0.0)
        area_gini.append(gini(areas))
    return {
        "pair_effective_component_count": np.asarray(effective_count, dtype=float),
        "pair_top2_component_area_share": np.asarray(top2_share, dtype=float),
        "pair_component_area_cv": np.asarray(area_cv, dtype=float),
        "pair_component_area_gini": np.asarray(area_gini, dtype=float),
    }


def aggregate_profiles(profiles: dict[str, np.ndarray]) -> dict[str, float]:
    results: dict[str, float] = {}
    for prefix, values in profiles.items():
        results |= {
            f"{prefix}_mean": float(values.mean()),
            f"{prefix}_population_std": float(values.std(ddof=0)),
            f"{prefix}_q10": float(np.quantile(values, 0.10)),
            f"{prefix}_q50": float(np.quantile(values, 0.50)),
            f"{prefix}_q90": float(np.quantile(values, 0.90)),
            f"{prefix}_iqr": float(np.quantile(values, 0.75) - np.quantile(values, 0.25)),
        }
    return results


def variable(values: np.ndarray) -> bool:
    values = values[np.isfinite(values)]
    return len(values) >= 3 and len(np.unique(values)) >= 3 and values.max() - values.min() > 1e-10 * max(1.0, abs(values).max())


def relation(left: np.ndarray, right: np.ndarray) -> dict[str, object]:
    common = np.isfinite(left) & np.isfinite(right)
    left, right = left[common], right[common]
    if len(left) != 58:
        return {"common_models": len(left), "relation": "insufficient_common_coverage", "pearson": np.nan, "spearman": np.nan, "normalized_L2_residual": np.nan}
    if not variable(left) or not variable(right):
        return {"common_models": 58, "relation": "degenerate_nonvarying_reference_or_candidate", "pearson": np.nan, "spearman": np.nan, "normalized_L2_residual": np.nan}
    if np.allclose(left, right, rtol=1e-10, atol=1e-12):
        return {"common_models": 58, "relation": "exact_duplicate", "pearson": 1.0, "spearman": 1.0, "normalized_L2_residual": 0.0}
    slope = np.dot(left, right) / np.dot(left, left)
    residual = float(np.linalg.norm(right - slope * left) / max(np.linalg.norm(right), 1e-30))
    pearson = float(pearsonr(left, right).statistic)
    spearman = float(spearmanr(left, right).statistic)
    kind = "proportional_duplicate" if residual <= 1e-6 and abs(slope) > 1e-12 else ("high_redundancy" if abs(pearson) >= 0.98 and abs(spearman) >= 0.98 else "distinct_or_unresolved")
    return {"common_models": 58, "relation": kind, "pearson": pearson, "spearman": spearman, "normalized_L2_residual": residual}


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    expected = contract["expected"]
    for item in contract["inputs"]:
        if sha256(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError(f"input hash mismatch: {item['path']}")

    manifest = pd.read_csv(ROOT / contract["inputs"][0]["path"])
    xreg = pd.read_csv(ROOT / contract["inputs"][2]["path"])
    models = sorted(xreg.model_id.unique())
    family = xreg[["model_id", "model_family"]].drop_duplicates().set_index("model_id").model_family.to_dict()
    frozen = dict(zip(manifest.path, manifest.sha256))
    sources = [f".tmp/t4rs4/P1000_S801/{model_id}/tables/overlay_component_population.csv" for model_id in models]
    if len(models) != expected["models"] or xreg.candidate_id.nunique() != 299 or any(path not in frozen or sha256(ROOT / path) != frozen[path] for path in sources):
        raise RuntimeError("source scope/hash mismatch")

    grade_b_prefixes = {"pair_effective_component_count", "pair_top2_component_area_share"}
    records: list[dict[str, object]] = []
    metadata: dict[str, dict[str, object]] = {}
    for model_id in models:
        source = pd.read_csv(ROOT / f".tmp/t4rs4/P1000_S801/{model_id}/tables/overlay_component_population.csv")
        source = source[source.kept_by_min2.astype(bool)].copy()
        if source.pair_index.nunique() != 800 or len(source) < 800 or not (source.area_mm2 > 0).all():
            raise RuntimeError(f"component population mismatch: {model_id}")
        metrics = aggregate_profiles(pair_composition_profile(source))
        for output_name, value in metrics.items():
            prefix = next(name for name in grade_b_prefixes | {"pair_component_area_cv", "pair_component_area_gini"} if output_name.startswith(name))
            grade = "B" if prefix in grade_b_prefixes else "C"
            candidate_id = f"RAW-X051::{output_name}"
            records.append({"model_id": model_id, "model_family": family[model_id], "candidate_id": candidate_id, "value": value, "operational_grade": grade})
            metadata.setdefault(
                candidate_id,
                {
                    "candidate_id": candidate_id,
                    "candidate_group_id": "RAW-X051",
                    "descriptor_family": "overlay_pair_component_composition_profile",
                    "output_name": output_name,
                    "unit": "dimensionless",
                    "source_population": "800 overlay-pair kept connected-component area compositions",
                    "aggregation_formula": "per-pair inverse-HHI effective count, top-two area share, area CV, or area Gini; then full-pair population mean/std/q10/q50/q90/IQR",
                    "applicable_family": "B|C|F|L|T",
                    "direct_or_derived": "direct_statistic_from_verified_SLICE004_component_table" if grade == "B" else "derived_pair_composition_statistic_from_verified_SLICE004_component_table",
                    "source_bank": "PRM120_overlay_pair_component_composition_batch",
                    "source_value_table": "PRM120_overlay_pair_component_composition_values_long.csv",
                    "technical_role": "batch_BC_candidate",
                    "qualification_status": "full58_raw_table_batch_not_selected",
                    "confidence_status": "confirmed_raw_table_lineage",
                    "later_evaluation_role": "batch_BC_unselected_block_aware",
                    "active_feature": False,
                    "promoted": False,
                    "y_evidence": False,
                    "notes": "PRM120 pair component-composition profile; no y, selection, mask or slicing",
                    "operational_grade": grade,
                    "literature_anchor": "LIT-X035",
                    "anchor_scope": "2D overlay connected-component area composition only; not a 3D topology estimator",
                },
            )

    values = pd.DataFrame(records)
    registry = pd.DataFrame(metadata.values()).sort_values("candidate_id").reset_index(drop=True)
    candidate_ids = registry.candidate_id.tolist()
    if len(candidate_ids) != expected["new_candidates"] or len(values) != expected["values"] or not np.isfinite(values.value).all() or (registry.operational_grade == "B").sum() != expected["grade_B_candidates"] or (registry.operational_grade == "C").sum() != expected["grade_C_candidates"]:
        raise RuntimeError("candidate/value/grade scope mismatch")
    wide = values.pivot(index="model_id", columns="candidate_id", values="value").reindex(index=models, columns=candidate_ids)
    coverage = pd.DataFrame(
        [
            {
                "candidate_id": candidate_id,
                "finite_count": 58,
                "missing_count": 0,
                "unique_count": int(wide[candidate_id].nunique()),
                "population_std_across_models": float(wide[candidate_id].std(ddof=0)),
                "iqr_across_models": float(np.quantile(wide[candidate_id], 0.75) - np.quantile(wide[candidate_id], 0.25)),
                "operational_grade": registry.set_index("candidate_id").loc[candidate_id, "operational_grade"],
                "technical_status": "batch_BC_unselected",
            }
            for candidate_id in candidate_ids
        ]
    )
    existing = {candidate_id: group.set_index("model_id").reindex(models).value.to_numpy(float) for candidate_id, group in xreg.groupby("candidate_id")}
    crossbank = pd.DataFrame(
        [
            {"candidate_id": candidate_id, "existing_candidate_id": existing_id, **relation(wide[candidate_id].to_numpy(float), existing_values), "evidence_scope": "full58_x_only", "selection_effect": "none"}
            for candidate_id in candidate_ids
            for existing_id, existing_values in sorted(existing.items())
        ]
    )
    internal = pd.DataFrame(
        [
            {"left_candidate_id": left, "right_candidate_id": right, **relation(wide[left].to_numpy(float), wide[right].to_numpy(float)), "evidence_scope": "full58_x_only", "selection_effect": "none"}
            for index, left in enumerate(candidate_ids)
            for right in candidate_ids[index + 1 :]
        ]
    )
    collision = pd.DataFrame(
        [
            {
                "pair_id": pair_id,
                "candidate_id": candidate_id,
                "absolute_delta": abs(float(wide.loc[left, candidate_id]) - float(wide.loc[right, candidate_id])),
                "relative_delta": abs(float(wide.loc[left, candidate_id]) - float(wide.loc[right, candidate_id])) / max(abs(float(wide.loc[left, candidate_id])), abs(float(wide.loc[right, candidate_id])), 1e-12),
                "diagnostic_only": True,
            }
            for left, right, pair_id in [("T8", "T9", "T8_T9"), ("T5", "T6", "T5_T6")]
            for candidate_id in candidate_ids
        ]
    )
    if len(crossbank) != expected["crossbank_relations"] or len(internal) != expected["internal_relations"] or len(collision) != expected["diagnostic_pair_values"]:
        raise RuntimeError("relation/collision scope mismatch")
    for suffix, frame in {
        "candidate_registry": registry,
        "values_long": values,
        "values_wide": wide.reset_index(),
        "coverage_variation": coverage,
        "vs_XREG_v1_2_redundancy": crossbank,
        "internal_redundancy": internal,
        "collision_diagnostic": collision,
    }.items():
        frame.to_csv(TABLES / f"PRM120_overlay_pair_component_composition_{suffix}.csv", index=False, encoding="utf-8-sig", float_format="%.17g")
    locks_ok = not registry[["active_feature", "promoted", "y_evidence"]].any().any() and all(value == 0 for value in contract["locks"].values())
    checks = [
        ("P120-01", len(models) == 58, "58 XREG-v1.2 models"),
        ("P120-02", len(sources) == 58, "58 hash-verified component sources"),
        ("P120-03", len(candidate_ids) == 24 and (registry.operational_grade == "B").sum() == 12 and (registry.operational_grade == "C").sum() == 12, "24 candidate B/C schema"),
        ("P120-04", len(values) == 1392 and np.isfinite(values.value).all(), "1,392 finite values"),
        ("P120-05", len(crossbank) == 7176, "7,176 crossbank relations"),
        ("P120-06", len(internal) == 276, "276 internal relations"),
        ("P120-07", len(collision) == 48, "two collision pairs x 24"),
        ("P120-08", locks_ok, "no y, selection or promotion and locks intact"),
    ]
    qa = pd.DataFrame([{"check_id": check_id, "status": "PASS" if passed else "FAIL", "detail": detail} for check_id, passed, detail in checks])
    (FACTORY / "reports").mkdir(parents=True, exist_ok=True)
    qa.to_csv(FACTORY / "reports" / "PRM120_producer_QA.csv", index=False, encoding="utf-8-sig")
    summary = {"status": "PASS" if qa.status.eq("PASS").all() else "FAIL", "checks": f"{qa.status.eq('PASS').sum()}/{len(qa)}", "models": 58, "candidates": 24, "grade_B": 12, "grade_C": 12, "values": 1392, "y_fit_selection_promotion": "0/0/0/0"}
    (FACTORY / "reports" / "PRM120_batch_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if summary["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
