from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
TABLES = LAB / "reports" / "tables"
FACTORY = LAB / "factories" / "PRM-118"
CONTRACT = FACTORY / "contracts" / "PRM-118_SLICE_COMPONENT_FILTER_SENSITIVITY_BC_BATCH_CONTRACT_20260723.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1_048_576), b""):
            digest.update(chunk)
    return digest.hexdigest()


def independent_values(frame: pd.DataFrame) -> dict[str, float]:
    """Independent replay of six RAW-X050 B3 probes from the frozen slice table."""
    raw = frame.component_count_raw.to_numpy(float)
    kept = frame.component_count_min2.to_numpy(float)
    removed = raw - kept
    fraction = removed / np.maximum(raw, 1.0)
    if np.std(fraction[:-1]) <= 1e-12 or np.std(fraction[1:]) <= 1e-12:
        lag1 = 0.0
    else:
        lag1 = float(np.corrcoef(fraction[:-1], fraction[1:])[0, 1])
    return {
        "RAW-X050::raw_component_count_mean": float(raw.mean()),
        "RAW-X050::raw_component_count_population_std": float(raw.std(ddof=0)),
        "RAW-X050::raw_component_count_iqr": float(np.quantile(raw, 0.75) - np.quantile(raw, 0.25)),
        "RAW-X050::filter_removed_component_delta_mean": float(removed.mean()),
        "RAW-X050::filter_removed_component_fraction_mean": float(fraction.mean()),
        "RAW-X050::filter_removed_component_fraction_lag1_autocorr": lag1,
    }


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    hashes_ok = all(sha256(ROOT / item["path"]) == item["sha256"] for item in contract["inputs"])

    manifest = pd.read_csv(ROOT / contract["inputs"][0]["path"])
    registry = pd.read_csv(TABLES / "PRM118_slice_component_filter_sensitivity_candidate_registry.csv")
    values_long = pd.read_csv(TABLES / "PRM118_slice_component_filter_sensitivity_values_long.csv")
    values_wide = pd.read_csv(TABLES / "PRM118_slice_component_filter_sensitivity_values_wide.csv").set_index("model_id")
    cross = pd.read_csv(TABLES / "PRM118_slice_component_filter_sensitivity_vs_XREG_v1_1_redundancy.csv")
    internal = pd.read_csv(TABLES / "PRM118_slice_component_filter_sensitivity_internal_redundancy.csv")
    collision = pd.read_csv(TABLES / "PRM118_slice_component_filter_sensitivity_collision_diagnostic.csv")

    models = sorted(values_wide.index)
    frozen = dict(zip(manifest.path, manifest.sha256))
    source_ok = all(
        (source := f".tmp/t4rs4/P1000_S801/{model_id}/tables/slice_pixel_readback.csv") in frozen
        and sha256(ROOT / source) == frozen[source]
        for model_id in models
    )

    b3 = pd.read_csv(ROOT / ".tmp/t4rs4/P1000_S801/B3/tables/slice_pixel_readback.csv").sort_values("slice_index")
    probes = independent_values(b3)
    probes_ok = all(
        np.isclose(float(values_wide.loc["B3", candidate_id]), value, rtol=1e-12, atol=1e-12)
        for candidate_id, value in probes.items()
    )
    locks_ok = (
        not registry.active_feature.any()
        and not registry.promoted.any()
        and not registry.y_evidence.any()
        and all(value == 0 for value in contract["locks"].values())
    )
    relation_counts = cross.relation.value_counts().to_dict()
    expected_relation_counts = {
        "distinct_or_unresolved": 2819,
        "degenerate_nonvarying_reference_or_candidate": 316,
        "insufficient_common_coverage": 22,
        "high_redundancy": 9,
        "exact_duplicate": 2,
    }
    checks = [
        ("I118-01", hashes_ok, "four contract input hashes"),
        ("I118-02", len(models) == 58 and source_ok, "58 independently hash-verified slice sources"),
        ("I118-03", len(registry) == 11 and (registry.operational_grade == "B").sum() == 8 and (registry.operational_grade == "C").sum() == 3, "candidate/grade schema"),
        ("I118-04", len(values_long) == 638 and np.isfinite(values_long.value).all() and values_wide.shape == (58, 11), "finite long/wide matrix"),
        ("I118-05", len(cross) == 3168 and len(internal) == 55 and len(collision) == 22 and relation_counts == expected_relation_counts, "relation/collision shapes and crossbank relation census"),
        ("I118-06", probes_ok, "six independent B3 formula probes"),
        ("I118-07", registry.candidate_group_id.value_counts().to_dict() == {"RAW-X050": 11}, "declared group count"),
        ("I118-08", locks_ok, "no y/selection/promotion and locks intact"),
    ]
    qa = pd.DataFrame([{"check_id": check_id, "status": "PASS" if passed else "FAIL", "detail": detail} for check_id, passed, detail in checks])
    (FACTORY / "reports").mkdir(parents=True, exist_ok=True)
    qa.to_csv(FACTORY / "reports" / "PRM118_independent_QA.csv", index=False, encoding="utf-8-sig")
    summary = {
        "status": "PASS" if qa.status.eq("PASS").all() else "FAIL",
        "checks": f"{qa.status.eq('PASS').sum()}/{len(qa)}",
        "formula_probes": 6,
        "models": 58,
        "candidates": 11,
        "performance_y_read": 0,
    }
    (FACTORY / "reports" / "PRM118_independent_QA_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if summary["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
