from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

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


def skewness(values: np.ndarray) -> float:
    centered = values - values.mean()
    sigma = np.sqrt(np.mean(centered ** 2))
    return float(np.mean(centered ** 3) / sigma ** 3)


def normalized_tv(values: np.ndarray) -> float:
    return float(np.abs(np.diff(values)).mean() / np.abs(values).mean())


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    input_hashes_ok = all(sha256(ROOT / item["path"]) == item["sha256"] for item in contract["inputs"])
    manifest = pd.read_csv(ROOT / contract["inputs"][0]["path"])
    registry = pd.read_csv(TABLES / "PRM106_profile_dynamics_candidate_registry.csv")
    values = pd.read_csv(TABLES / "PRM106_profile_dynamics_values_long.csv")
    wide = pd.read_csv(TABLES / "PRM106_profile_dynamics_values_wide.csv").set_index("model_id")
    crossbank = pd.read_csv(TABLES / "PRM106_profile_dynamics_vs_XREG_v0_5_redundancy.csv")
    internal = pd.read_csv(TABLES / "PRM106_profile_dynamics_internal_redundancy.csv")
    collision = pd.read_csv(TABLES / "PRM106_profile_dynamics_collision_diagnostic.csv")
    models = sorted(wide.index.tolist())
    frozen = dict(zip(manifest["path"], manifest["sha256"]))
    source_ok = True
    for model in models:
        for name in ["slice_pixel_readback.csv", "overlay_pixel_readback.csv"]:
            path = f".tmp/t4rs4/P1000_S801/{model}/tables/{name}"
            source_ok = source_ok and path in frozen and sha256(ROOT / path) == frozen[path]
    slice_b3 = pd.read_csv(ROOT / ".tmp/t4rs4/P1000_S801/B3/tables/slice_pixel_readback.csv").sort_values("slice_index")
    overlay_b3 = pd.read_csv(ROOT / ".tmp/t4rs4/P1000_S801/B3/tables/overlay_pixel_readback.csv").sort_values("pair_index")
    area = slice_b3["material_area_mm2"].to_numpy(float)
    component_count = slice_b3["component_count_min2"].to_numpy(float)
    red = overlay_b3["red_pixel_count"].to_numpy(float)
    union = overlay_b3["union_pixel_count"].to_numpy(float)
    blue_fraction = overlay_b3["blue_pixel_count"].to_numpy(float) / union
    purple_fraction = overlay_b3["purple_pixel_count"].to_numpy(float) / union
    probes = {
        "RAW-X038::slice_material_area_moment_skewness": skewness(area),
        "RAW-X038::slice_component_count_peak_to_mean": float(component_count.max() / component_count.mean()),
        "RAW-X039::overlay_red_pixel_count_lag1_autocorr": float(np.corrcoef(red[:-1], red[1:])[0, 1]),
        "RAW-X039::overlay_union_pixel_count_normalized_total_variation": normalized_tv(union),
        "RAW-X040::overlay_blue_fraction_population_std": float(blue_fraction.std(ddof=0)),
        "RAW-X040::overlay_purple_fraction_lag1_autocorr": float(np.corrcoef(purple_fraction[:-1], purple_fraction[1:])[0, 1]),
    }
    probe_ok = all(np.isclose(float(wide.loc["B3", candidate_id]), expected, rtol=1e-12, atol=1e-12) for candidate_id, expected in probes.items())
    locks_ok = not registry["active_feature"].any() and not registry["promoted"].any() and not registry["y_evidence"].any() and all(value == 0 for value in contract["locks"].values())
    checks = [
        ("I106-01", input_hashes_ok, "four contract input hashes"),
        ("I106-02", len(models) == 58 and source_ok, "116 independently hash-verified raw sources"),
        ("I106-03", len(registry) == 22 and (registry["operational_grade"] == "B").sum() == 4 and (registry["operational_grade"] == "C").sum() == 18, "candidate/grade schema"),
        ("I106-04", len(values) == 1276 and np.isfinite(values["value"].to_numpy(float)).all() and wide.shape == (58, 22), "finite long/wide matrix"),
        ("I106-05", len(crossbank) == 3762 and len(internal) == 231 and len(collision) == 44, "x-only relation and collision shapes"),
        ("I106-06", probe_ok, "independent B3 formula probes"),
        ("I106-07", registry["candidate_group_id"].value_counts().to_dict() == {"RAW-X039": 8, "RAW-X038": 8, "RAW-X040": 6}, "declared group counts"),
        ("I106-08", locks_ok, "no y/selection/promotion and locks intact"),
    ]
    qa = pd.DataFrame([{"check_id": check_id, "status": "PASS" if ok else "FAIL", "detail": detail} for check_id, ok, detail in checks])
    qa.to_csv(FACTORY / "reports" / "PRM106_independent_QA.csv", index=False, encoding="utf-8-sig")
    summary = {"status": "PASS" if qa["status"].eq("PASS").all() else "FAIL", "checks": f"{qa['status'].eq('PASS').sum()}/{len(qa)}", "formula_probes": len(probes), "models": 58, "candidates": 22, "performance_y_read": 0}
    (FACTORY / "reports" / "PRM106_independent_QA_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if summary["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
