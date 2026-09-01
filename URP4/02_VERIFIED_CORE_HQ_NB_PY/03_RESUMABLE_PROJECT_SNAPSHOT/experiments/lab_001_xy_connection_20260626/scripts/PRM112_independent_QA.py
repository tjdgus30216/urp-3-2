from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
TABLES = LAB / "reports" / "tables"
FACTORY = LAB / "factories" / "PRM-112"
CONTRACT = FACTORY / "contracts" / "PRM-112_AXIAL_WEIGHTED_QUANTILE_LOCATION_B_BATCH_CONTRACT_20260723.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1_048_576), b""):
            digest.update(chunk)
    return digest.hexdigest()


def independent_quantile(profile: np.ndarray, q: float) -> float:
    """Independent implementation: loop through normalized masses, not searchsorted."""
    profile = np.asarray(profile, dtype=float)
    if len(profile) < 4 or not np.isfinite(profile).all() or np.any(profile < 0) or profile.sum() <= 1e-12:
        raise RuntimeError("invalid source profile")
    cumulative, total = 0.0, float(profile.sum())
    for index, weight in enumerate(profile):
        cumulative += float(weight) / total
        if cumulative >= q:
            return float(index / (len(profile) - 1))
    raise RuntimeError("quantile not reached")


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    hashes_ok = all(sha256(ROOT / item["path"]) == item["sha256"] for item in contract["inputs"])
    manifest = pd.read_csv(ROOT / contract["inputs"][0]["path"])
    registry = pd.read_csv(TABLES / "PRM112_axial_weighted_quantile_location_candidate_registry.csv")
    values = pd.read_csv(TABLES / "PRM112_axial_weighted_quantile_location_values_long.csv")
    wide = pd.read_csv(TABLES / "PRM112_axial_weighted_quantile_location_values_wide.csv").set_index("model_id")
    crossbank = pd.read_csv(TABLES / "PRM112_axial_weighted_quantile_location_vs_XREG_v0_8_redundancy.csv")
    internal = pd.read_csv(TABLES / "PRM112_axial_weighted_quantile_location_internal_redundancy.csv")
    collision = pd.read_csv(TABLES / "PRM112_axial_weighted_quantile_location_collision_diagnostic.csv")
    models = sorted(wide.index.tolist())
    frozen = dict(zip(manifest["path"], manifest["sha256"]))
    source_ok = all(
        path in frozen and sha256(ROOT / path) == frozen[path]
        for model in models
        for path in (f".tmp/t4rs4/P1000_S801/{model}/tables/slice_pixel_readback.csv", f".tmp/t4rs4/P1000_S801/{model}/tables/overlay_pixel_readback.csv")
    )
    base = ROOT / ".tmp/t4rs4/P1000_S801/B3/tables"
    slices = pd.read_csv(base / "slice_pixel_readback.csv").sort_values("slice_index")
    overlay = pd.read_csv(base / "overlay_pixel_readback.csv").sort_values("pair_index")
    probes = {
        "RAW-X047::slice_material_area_weighted_axial_q10_position": independent_quantile(slices["material_area_mm2"].to_numpy(float), .10),
        "RAW-X047::slice_component_count_weighted_axial_q75_position": independent_quantile(slices["component_count_min2"].to_numpy(float), .75),
        "RAW-X047::overlay_red_pixel_count_weighted_axial_q25_position": independent_quantile(overlay["red_pixel_count"].to_numpy(float), .25),
        "RAW-X047::overlay_blue_pixel_count_weighted_axial_q90_position": independent_quantile(overlay["blue_pixel_count"].to_numpy(float), .90),
        "RAW-X047::overlay_purple_pixel_count_weighted_axial_q10_position": independent_quantile(overlay["purple_pixel_count"].to_numpy(float), .10),
        "RAW-X047::overlay_union_pixel_count_weighted_axial_q75_position": independent_quantile(overlay["union_pixel_count"].to_numpy(float), .75),
    }
    probes_ok = all(np.isclose(float(wide.loc["B3", cid]), expected, rtol=1e-12, atol=1e-12) for cid, expected in probes.items())
    locks_ok = (not registry["active_feature"].any() and not registry["promoted"].any() and not registry["y_evidence"].any() and all(value == 0 for value in contract["locks"].values()))
    checks = [
        ("I112-01", hashes_ok, "four contract input hashes"),
        ("I112-02", len(models) == 58 and source_ok, "116 independently hash-verified raw sources"),
        ("I112-03", len(registry) == 24 and (registry["operational_grade"] == "B").sum() == 24, "candidate/grade schema"),
        ("I112-04", len(values) == 1392 and np.isfinite(values["value"].to_numpy(float)).all() and wide.shape == (58, 24), "finite long/wide matrix"),
        ("I112-05", len(crossbank) == 5784 and len(internal) == 276 and len(collision) == 48, "relation/collision shapes"),
        ("I112-06", probes_ok, "six independent B3 quantile formula probes"),
        ("I112-07", registry["candidate_group_id"].value_counts().to_dict() == {"RAW-X047": 24}, "declared group count"),
        ("I112-08", locks_ok, "no y/selection/promotion and locks intact"),
    ]
    qa = pd.DataFrame([{"check_id": cid, "status": "PASS" if ok else "FAIL", "detail": detail} for cid, ok, detail in checks])
    (FACTORY / "reports").mkdir(parents=True, exist_ok=True)
    qa.to_csv(FACTORY / "reports" / "PRM112_independent_QA.csv", index=False, encoding="utf-8-sig")
    summary = {"status": "PASS" if qa.status.eq("PASS").all() else "FAIL", "checks": f"{qa.status.eq('PASS').sum()}/{len(qa)}", "formula_probes": len(probes), "models": 58, "candidates": 24, "performance_y_read": 0}
    (FACTORY / "reports" / "PRM112_independent_QA_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if summary["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
