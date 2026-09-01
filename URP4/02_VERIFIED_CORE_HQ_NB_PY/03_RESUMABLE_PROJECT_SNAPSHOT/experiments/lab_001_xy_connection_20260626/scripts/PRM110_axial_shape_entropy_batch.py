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
FACTORY = LAB / "factories" / "PRM-110"
CONTRACT = FACTORY / "contracts" / "PRM-110_AXIAL_SHAPE_ENTROPY_BC_BATCH_CONTRACT_20260723.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1_048_576), b""):
            digest.update(chunk)
    return digest.hexdigest()


def distribution(profile: np.ndarray, label: str) -> tuple[np.ndarray, np.ndarray, float, float]:
    profile = np.asarray(profile, dtype=float)
    if (
        len(profile) < 4
        or not np.isfinite(profile).all()
        or np.any(profile < 0)
        or float(profile.sum()) <= 1e-12
    ):
        raise RuntimeError(f"invalid nonnegative profile: {label}")
    probability = profile / profile.sum()
    position = np.linspace(0.0, 1.0, len(profile))
    center = float(np.dot(probability, position))
    spread = float(np.sqrt(np.dot(probability, (position - center) ** 2)))
    if spread <= 1e-12:
        raise RuntimeError(f"degenerate axial spread: {label}")
    return profile, probability, center, spread


def axial_skewness(profile: np.ndarray) -> float:
    _, probability, center, spread = distribution(profile, "axial_skewness")
    position = np.linspace(0.0, 1.0, len(profile))
    return float(np.dot(probability, ((position - center) / spread) ** 3))


def axial_excess_kurtosis(profile: np.ndarray) -> float:
    _, probability, center, spread = distribution(profile, "axial_excess_kurtosis")
    position = np.linspace(0.0, 1.0, len(profile))
    return float(np.dot(probability, ((position - center) / spread) ** 4) - 3.0)


def normalized_entropy(profile: np.ndarray) -> float:
    _, probability, _, _ = distribution(profile, "normalized_entropy")
    nonzero = probability[probability > 0]
    return float(-np.dot(nonzero, np.log(nonzero)) / np.log(len(probability)))


def center_edge_contrast(profile: np.ndarray) -> float:
    profile, _, _, _ = distribution(profile, "center_edge_contrast")
    position = np.linspace(0.0, 1.0, len(profile))
    center_mass = float(profile[(position >= 0.25) & (position <= 0.75)].sum())
    edge_mass = float(profile.sum() - center_mass)
    return float((center_mass - edge_mass) / (center_mass + edge_mass))


def variable(values: np.ndarray) -> bool:
    finite = values[np.isfinite(values)]
    return (
        len(finite) >= 3
        and len(np.unique(finite)) >= 3
        and (finite.max() - finite.min())
        > 1e-10 * max(1.0, np.max(np.abs(finite)))
    )


def relation(left: np.ndarray, right: np.ndarray) -> dict[str, float | int | str]:
    common = np.isfinite(left) & np.isfinite(right)
    left, right = left[common], right[common]
    if len(left) != 58:
        return {
            "common_models": int(len(left)),
            "relation": "insufficient_common_coverage",
            "pearson": np.nan,
            "spearman": np.nan,
            "normalized_L2_residual": np.nan,
        }
    if not variable(left) or not variable(right):
        return {
            "common_models": 58,
            "relation": "degenerate_nonvarying_reference_or_candidate",
            "pearson": np.nan,
            "spearman": np.nan,
            "normalized_L2_residual": np.nan,
        }
    if np.allclose(left, right, rtol=1e-10, atol=1e-12):
        return {
            "common_models": 58,
            "relation": "exact_duplicate",
            "pearson": 1.0,
            "spearman": 1.0,
            "normalized_L2_residual": 0.0,
        }
    slope = float(np.dot(left, right) / np.dot(left, left))
    residual = float(
        np.linalg.norm(right - slope * left) / max(np.linalg.norm(right), 1e-30)
    )
    pearson = float(pearsonr(left, right).statistic)
    spearman = float(spearmanr(left, right).statistic)
    if residual <= 1e-6 and abs(slope) > 1e-12:
        kind = "proportional_duplicate"
    elif abs(pearson) >= 0.98 and abs(spearman) >= 0.98:
        kind = "high_redundancy"
    else:
        kind = "distinct_or_unresolved"
    return {
        "common_models": 58,
        "relation": kind,
        "pearson": pearson,
        "spearman": spearman,
        "normalized_L2_residual": residual,
    }


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    for item in contract["inputs"]:
        if sha256(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError(f"input hash mismatch: {item['path']}")
    manifest = pd.read_csv(ROOT / contract["inputs"][0]["path"])
    xreg = pd.read_csv(ROOT / contract["inputs"][2]["path"])
    models = sorted(xreg["model_id"].unique())
    family = (
        xreg[["model_id", "model_family"]]
        .drop_duplicates()
        .set_index("model_id")["model_family"]
        .to_dict()
    )
    if len(models) != 58 or xreg["candidate_id"].nunique() != 217:
        raise RuntimeError("XREG-v0.7 scope mismatch")
    frozen = dict(zip(manifest["path"], manifest["sha256"]))
    raw_paths = [
        f".tmp/t4rs4/P1000_S801/{model}/tables/{name}"
        for model in models
        for name in ["slice_pixel_readback.csv", "overlay_pixel_readback.csv"]
    ]
    if len(raw_paths) != 116 or any(
        path not in frozen or sha256(ROOT / path) != frozen[path]
        for path in raw_paths
    ):
        raise RuntimeError("raw source hash/coverage mismatch")

    records: list[dict] = []
    metadata: dict[str, dict] = {}

    def put(
        model: str,
        candidate_id: str,
        value: float,
        grade: str,
        population: str,
        formula: str,
        source_table: str,
        anchor: str,
    ) -> None:
        if not np.isfinite(value):
            raise RuntimeError(f"non-finite candidate: {model} {candidate_id}")
        records.append(
            {
                "model_id": model,
                "model_family": family[model],
                "candidate_id": candidate_id,
                "value": float(value),
                "operational_grade": grade,
            }
        )
        group = candidate_id.split("::", 1)[0]
        metadata.setdefault(
            candidate_id,
            {
                "candidate_id": candidate_id,
                "candidate_group_id": group,
                "descriptor_family": (
                    "slice_axial_position_shape"
                    if group == "RAW-X045"
                    else "overlay_axial_position_shape"
                ),
                "output_name": candidate_id.split("::", 1)[1],
                "unit": "dimensionless",
                "source_population": population,
                "aggregation_formula": formula,
                "applicable_family": "B|C|F|L|T",
                "direct_or_derived": (
                    "direct_statistic_from_verified_SLICE004_profile"
                    if grade == "B"
                    else "derived_normalized_contrast_from_verified_SLICE004_profile"
                ),
                "source_bank": "PRM110_axial_shape_entropy_batch",
                "source_value_table": "PRM110_axial_shape_entropy_values_long.csv",
                "technical_role": "batch_BC_candidate",
                "qualification_status": "full58_raw_table_batch_not_selected",
                "confidence_status": "confirmed_raw_table_lineage",
                "later_evaluation_role": "batch_BC_unselected_block_aware",
                "active_feature": False,
                "promoted": False,
                "y_evidence": False,
                "notes": "PRM110 weighted axial-position shape/entropy/contrast batch; no y, selection, mask or slicing",
                "operational_grade": grade,
                "literature_anchor": anchor,
                "anchor_scope": "normalized 1D axial distribution statistic only; not a full 3D topology estimator",
            },
        )

    metrics = [
        (
            "axial_position_skewness",
            axial_skewness,
            "B",
            "sum(p*((z_norm-mu)/sigma)^3)",
        ),
        (
            "axial_position_excess_kurtosis",
            axial_excess_kurtosis,
            "B",
            "sum(p*((z_norm-mu)/sigma)^4)-3",
        ),
        (
            "normalized_profile_entropy",
            normalized_entropy,
            "B",
            "-sum(p*ln(p))/ln(number_of_ordered_rows)",
        ),
        (
            "center_edge_mass_contrast",
            center_edge_contrast,
            "C",
            "(mass(z in [0.25,0.75])-mass(edges))/total_mass",
        ),
    ]
    for model in models:
        base = ROOT / f".tmp/t4rs4/P1000_S801/{model}/tables"
        slices = pd.read_csv(base / "slice_pixel_readback.csv").sort_values(
            "slice_index"
        )
        overlay = pd.read_csv(base / "overlay_pixel_readback.csv").sort_values(
            "pair_index"
        )
        if (
            len(slices) != 801
            or len(overlay) != 800
            or not slices["slice_index"].is_unique
            or not overlay["pair_index"].is_unique
        ):
            raise RuntimeError(f"profile index mismatch: {model}")
        profiles = {
            "slice_material_area": (
                "RAW-X045",
                slices["material_area_mm2"].to_numpy(float),
                "801-row slice material-area ordered profile",
                "slice_pixel_readback.csv",
                "LIT-X033",
            ),
            "slice_component_count": (
                "RAW-X045",
                slices["component_count_min2"].to_numpy(float),
                "801-row slice min2-component-count ordered profile",
                "slice_pixel_readback.csv",
                "LIT-X033",
            ),
        }
        for channel in ["red", "blue", "purple", "union"]:
            profiles[f"overlay_{channel}_pixel_count"] = (
                "RAW-X046",
                overlay[f"{channel}_pixel_count"].to_numpy(float),
                f"800-pair overlay {channel}-pixel-count ordered profile",
                "overlay_pixel_readback.csv",
                "LIT-X028",
            )
        for profile_name, (
            group,
            profile,
            population,
            source_table,
            anchor,
        ) in profiles.items():
            for metric_name, function, grade, formula in metrics:
                put(
                    model,
                    f"{group}::{profile_name}_{metric_name}",
                    function(profile),
                    grade,
                    population,
                    formula,
                    source_table,
                    anchor,
                )

    values = pd.DataFrame(records)
    registry = (
        pd.DataFrame(metadata.values())
        .sort_values("candidate_id")
        .reset_index(drop=True)
    )
    candidate_ids = registry["candidate_id"].tolist()
    if (
        len(candidate_ids) != 24
        or len(values) != 1392
        or not np.isfinite(values["value"].to_numpy(float)).all()
    ):
        raise RuntimeError("candidate/value scope mismatch")
    if (
        (registry["operational_grade"] == "B").sum() != 18
        or (registry["operational_grade"] == "C").sum() != 6
    ):
        raise RuntimeError("grade scope mismatch")
    wide = values.pivot(
        index="model_id", columns="candidate_id", values="value"
    ).reindex(index=models, columns=candidate_ids)

    coverage = []
    registry_lookup = registry.set_index("candidate_id")
    for candidate_id in candidate_ids:
        vector = wide[candidate_id].to_numpy(float)
        coverage.append(
            {
                "candidate_id": candidate_id,
                "finite_count": int(np.isfinite(vector).sum()),
                "missing_count": int((~np.isfinite(vector)).sum()),
                "unique_count": int(np.unique(vector).size),
                "population_std_across_models": float(vector.std(ddof=0)),
                "iqr_across_models": float(
                    np.quantile(vector, 0.75) - np.quantile(vector, 0.25)
                ),
                "operational_grade": registry_lookup.loc[
                    candidate_id, "operational_grade"
                ],
                "technical_status": "batch_BC_unselected",
            }
        )
    xreg_vectors = {
        candidate_id: group.set_index("model_id")
        .reindex(models)["value"]
        .to_numpy(float)
        for candidate_id, group in xreg.groupby("candidate_id")
    }
    crossbank = []
    for candidate_id in candidate_ids:
        vector = wide[candidate_id].to_numpy(float)
        for existing_id, existing_values in sorted(xreg_vectors.items()):
            crossbank.append(
                {
                    "candidate_id": candidate_id,
                    "existing_candidate_id": existing_id,
                    **relation(vector, existing_values),
                    "evidence_scope": "full58_x_only",
                    "selection_effect": "none",
                }
            )
    internal = []
    for index, left_id in enumerate(candidate_ids):
        for right_id in candidate_ids[index + 1 :]:
            internal.append(
                {
                    "left_candidate_id": left_id,
                    "right_candidate_id": right_id,
                    **relation(
                        wide[left_id].to_numpy(float),
                        wide[right_id].to_numpy(float),
                    ),
                    "evidence_scope": "full58_x_only",
                    "selection_effect": "none",
                }
            )
    collision = []
    for left_model, right_model, pair_id in [
        ("T8", "T9", "T8_T9"),
        ("T5", "T6", "T5_T6"),
    ]:
        for candidate_id in candidate_ids:
            left_value = float(wide.loc[left_model, candidate_id])
            right_value = float(wide.loc[right_model, candidate_id])
            collision.append(
                {
                    "pair_id": pair_id,
                    "candidate_id": candidate_id,
                    "absolute_delta": abs(left_value - right_value),
                    "relative_delta": abs(left_value - right_value)
                    / max(abs(left_value), abs(right_value), 1e-12),
                    "diagnostic_only": True,
                }
            )

    TABLES.mkdir(parents=True, exist_ok=True)
    (FACTORY / "reports").mkdir(parents=True, exist_ok=True)
    registry.to_csv(
        TABLES / "PRM110_axial_shape_entropy_candidate_registry.csv",
        index=False,
        encoding="utf-8-sig",
    )
    values.to_csv(
        TABLES / "PRM110_axial_shape_entropy_values_long.csv",
        index=False,
        encoding="utf-8-sig",
        float_format="%.17g",
    )
    wide.reset_index().to_csv(
        TABLES / "PRM110_axial_shape_entropy_values_wide.csv",
        index=False,
        encoding="utf-8-sig",
        float_format="%.17g",
    )
    pd.DataFrame(coverage).to_csv(
        TABLES / "PRM110_axial_shape_entropy_coverage_variation.csv",
        index=False,
        encoding="utf-8-sig",
    )
    pd.DataFrame(crossbank).to_csv(
        TABLES / "PRM110_axial_shape_entropy_vs_XREG_v0_7_redundancy.csv",
        index=False,
        encoding="utf-8-sig",
    )
    pd.DataFrame(internal).to_csv(
        TABLES / "PRM110_axial_shape_entropy_internal_redundancy.csv",
        index=False,
        encoding="utf-8-sig",
    )
    pd.DataFrame(collision).to_csv(
        TABLES / "PRM110_axial_shape_entropy_collision_diagnostic.csv",
        index=False,
        encoding="utf-8-sig",
    )
    checks = [
        ("P110-01", len(models) == 58, "58 XREG-v0.7 models"),
        ("P110-02", len(raw_paths) == 116, "116 hash-verified raw sources"),
        ("P110-03", len(candidate_ids) == 24, "24 candidates"),
        (
            "P110-04",
            len(values) == 1392
            and np.isfinite(values["value"].to_numpy(float)).all(),
            "1,392 finite values",
        ),
        ("P110-05", len(crossbank) == 24 * 217, "5,208 crossbank relations"),
        ("P110-06", len(internal) == 24 * 23 // 2, "276 internal relations"),
        ("P110-07", len(collision) == 48, "two collision pairs x 24"),
        (
            "P110-08",
            not registry["active_feature"].any()
            and not registry["promoted"].any()
            and not registry["y_evidence"].any(),
            "no y, selection or promotion",
        ),
    ]
    producer = pd.DataFrame(
        [
            {
                "check_id": check_id,
                "status": "PASS" if ok else "FAIL",
                "detail": detail,
            }
            for check_id, ok, detail in checks
        ]
    )
    producer.to_csv(
        FACTORY / "reports" / "PRM110_producer_QA.csv",
        index=False,
        encoding="utf-8-sig",
    )
    summary = {
        "status": "PASS" if producer["status"].eq("PASS").all() else "FAIL",
        "checks": f"{producer['status'].eq('PASS').sum()}/{len(producer)}",
        "models": 58,
        "candidates": 24,
        "grade_B": 18,
        "grade_C": 6,
        "values": 1392,
        "y_fit_selection_promotion": "0/0/0/0",
    }
    (FACTORY / "reports" / "PRM110_batch_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    if summary["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
