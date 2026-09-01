from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


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
    return 0.0 if count <= 1 else float(np.dot(2 * np.arange(1, count + 1) - count - 1, values) / (count * values.sum()))


def independent_b3_probes(frame: pd.DataFrame) -> dict[str, float]:
    effective, top2, cv, gini_values = [], [], [], []
    for _, group in frame.groupby("pair_index", sort=True):
        areas = group.area_mm2.to_numpy(float)
        weights = areas / areas.sum()
        effective.append(float(1.0 / np.dot(weights, weights)))
        top2.append(float(np.sort(weights)[-2:].sum()))
        cv.append(float(areas.std(ddof=0) / areas.mean()) if len(areas) > 1 else 0.0)
        gini_values.append(gini(areas))
    effective, top2, cv, gini_values = map(np.asarray, (effective, top2, cv, gini_values))
    return {
        "RAW-X051::pair_effective_component_count_mean": float(effective.mean()),
        "RAW-X051::pair_effective_component_count_q90": float(np.quantile(effective, 0.90)),
        "RAW-X051::pair_top2_component_area_share_q10": float(np.quantile(top2, 0.10)),
        "RAW-X051::pair_top2_component_area_share_iqr": float(np.quantile(top2, 0.75) - np.quantile(top2, 0.25)),
        "RAW-X051::pair_component_area_cv_q50": float(np.quantile(cv, 0.50)),
        "RAW-X051::pair_component_area_gini_iqr": float(np.quantile(gini_values, 0.75) - np.quantile(gini_values, 0.25)),
    }


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    hashes_ok = all(sha256(ROOT / item["path"]) == item["sha256"] for item in contract["inputs"])
    manifest = pd.read_csv(ROOT / contract["inputs"][0]["path"])
    registry = pd.read_csv(TABLES / "PRM120_overlay_pair_component_composition_candidate_registry.csv")
    values_long = pd.read_csv(TABLES / "PRM120_overlay_pair_component_composition_values_long.csv")
    values_wide = pd.read_csv(TABLES / "PRM120_overlay_pair_component_composition_values_wide.csv").set_index("model_id")
    crossbank = pd.read_csv(TABLES / "PRM120_overlay_pair_component_composition_vs_XREG_v1_2_redundancy.csv")
    internal = pd.read_csv(TABLES / "PRM120_overlay_pair_component_composition_internal_redundancy.csv")
    collision = pd.read_csv(TABLES / "PRM120_overlay_pair_component_composition_collision_diagnostic.csv")
    models = sorted(values_wide.index)
    frozen = dict(zip(manifest.path, manifest.sha256))
    source_ok = all(
        (source := f".tmp/t4rs4/P1000_S801/{model_id}/tables/overlay_component_population.csv") in frozen
        and sha256(ROOT / source) == frozen[source]
        for model_id in models
    )
    b3 = pd.read_csv(ROOT / ".tmp/t4rs4/P1000_S801/B3/tables/overlay_component_population.csv")
    b3 = b3[b3.kept_by_min2.astype(bool)].copy()
    probes = independent_b3_probes(b3)
    probes_ok = all(np.isclose(float(values_wide.loc["B3", candidate_id]), value, rtol=1e-12, atol=1e-12) for candidate_id, value in probes.items())
    locks_ok = (
        not registry.active_feature.any()
        and not registry.promoted.any()
        and not registry.y_evidence.any()
        and all(value == 0 for value in contract["locks"].values())
    )
    checks = [
        ("I120-01", hashes_ok, "four contract input hashes"),
        ("I120-02", len(models) == 58 and source_ok, "58 independently hash-verified component sources"),
        ("I120-03", len(registry) == 24 and (registry.operational_grade == "B").sum() == 12 and (registry.operational_grade == "C").sum() == 12, "candidate/grade schema"),
        ("I120-04", len(values_long) == 1392 and np.isfinite(values_long.value).all() and values_wide.shape == (58, 24), "finite long/wide matrix"),
        ("I120-05", len(crossbank) == 7176 and len(internal) == 276 and len(collision) == 48, "relation/collision shapes"),
        ("I120-06", probes_ok, "six independent B3 formula probes"),
        ("I120-07", registry.candidate_group_id.value_counts().to_dict() == {"RAW-X051": 24}, "declared group count"),
        ("I120-08", locks_ok, "no y/selection/promotion and locks intact"),
    ]
    qa = pd.DataFrame([{"check_id": check_id, "status": "PASS" if passed else "FAIL", "detail": detail} for check_id, passed, detail in checks])
    (FACTORY / "reports").mkdir(parents=True, exist_ok=True)
    qa.to_csv(FACTORY / "reports" / "PRM120_independent_QA.csv", index=False, encoding="utf-8-sig")
    summary = {"status": "PASS" if qa.status.eq("PASS").all() else "FAIL", "checks": f"{qa.status.eq('PASS').sum()}/{len(qa)}", "formula_probes": 6, "models": 58, "candidates": 24, "performance_y_read": 0}
    (FACTORY / "reports" / "PRM120_independent_QA_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if summary["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
