from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

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


def close(actual: float, expected: float, tolerance: float = 1e-12) -> bool:
    return bool(np.isclose(actual, expected, rtol=tolerance, atol=tolerance))


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    source_results = []
    for item in contract["inputs"]:
        source_results.append((item["path"], sha256(ROOT / item["path"]) == item["sha256"]))
    manifest = pd.read_csv(ROOT / contract["inputs"][0]["path"])
    registry = pd.read_csv(TABLES / "PRM104_overlay_phase_profile_candidate_registry.csv")
    values = pd.read_csv(TABLES / "PRM104_overlay_phase_profile_values_long.csv")
    wide = pd.read_csv(TABLES / "PRM104_overlay_phase_profile_values_wide.csv").set_index("model_id")
    crossbank = pd.read_csv(TABLES / "PRM104_overlay_phase_profile_vs_XREG_v0_4_redundancy.csv")
    internal = pd.read_csv(TABLES / "PRM104_overlay_phase_profile_internal_redundancy.csv")
    collisions = pd.read_csv(TABLES / "PRM104_overlay_phase_profile_collision_diagnostic.csv")
    models = sorted(wide.index.tolist())
    frozen = dict(zip(manifest["path"], manifest["sha256"]))
    hashes_ok = True
    for model in models:
        path = f".tmp/t4rs4/P1000_S801/{model}/tables/overlay_pixel_readback.csv"
        hashes_ok = hashes_ok and path in frozen and sha256(ROOT / path) == frozen[path]

    raw_b3 = pd.read_csv(ROOT / ".tmp/t4rs4/P1000_S801/B3/tables/overlay_pixel_readback.csv").sort_values("pair_index")
    union = raw_b3["union_pixel_count"].to_numpy(float)
    q25, q50, q75 = np.quantile(raw_b3["blue_pixel_count"].to_numpy(float), [0.25, 0.5, 0.75])
    probes = {
        "RAW-X036::overlay_red_pixel_count_mean": float(raw_b3["red_pixel_count"].mean()),
        "RAW-X036::overlay_blue_pixel_count_q50": float(q50),
        "RAW-X036::overlay_purple_pixel_count_mad": float(np.median(np.abs(raw_b3["purple_pixel_count"].to_numpy(float) - np.median(raw_b3["purple_pixel_count"].to_numpy(float))))),
        "RAW-X036::overlay_union_pixel_count_iqr": float(np.quantile(union, 0.75) - np.quantile(union, 0.25)),
        "RAW-X037::overlay_red_fraction_mean": float((raw_b3["red_pixel_count"].to_numpy(float) / union).mean()),
        "RAW-X037::overlay_purple_fraction_mean": float((raw_b3["purple_pixel_count"].to_numpy(float) / union).mean()),
    }
    probe_ok = all(close(float(wide.loc["B3", candidate_id]), expected) for candidate_id, expected in probes.items())
    fraction_sum = wide[["RAW-X037::overlay_red_fraction_mean", "RAW-X037::overlay_blue_fraction_mean", "RAW-X037::overlay_purple_fraction_mean"]].sum(axis=1).to_numpy(float)
    fraction_sum_ok = bool(np.allclose(fraction_sum, 1.0, rtol=1e-12, atol=1e-12))
    locks_ok = all(value == 0 for value in contract["locks"].values())
    checks = [
        ("I104-01", all(ok for _, ok in source_results), "contract input hashes"),
        ("I104-02", len(models) == 58 and hashes_ok, "58 independently hash-verified overlay sources"),
        ("I104-03", len(registry) == 28 and (registry["operational_grade"] == "B").sum() == 25 and (registry["operational_grade"] == "C").sum() == 3, "candidate/grade schema"),
        ("I104-04", len(values) == 1624 and np.isfinite(values["value"].to_numpy(float)).all() and wide.shape == (58, 28), "finite long/wide matrix"),
        ("I104-05", len(crossbank) == 4004 and len(internal) == 378 and len(collisions) == 56, "x-only relation and collision shapes"),
        ("I104-06", probe_ok, "independent B3 formula probes"),
        ("I104-07", fraction_sum_ok, "phase fractions form the explicitly declared compositional identity"),
        ("I104-08", not registry["active_feature"].any() and not registry["promoted"].any() and not registry["y_evidence"].any() and locks_ok, "no y/selection/promotion and locks intact"),
    ]
    qa = pd.DataFrame([{"check_id": check_id, "status": "PASS" if ok else "FAIL", "detail": detail} for check_id, ok, detail in checks])
    qa.to_csv(FACTORY / "reports" / "PRM104_independent_QA.csv", index=False, encoding="utf-8-sig")
    summary = {"status": "PASS" if qa["status"].eq("PASS").all() else "FAIL", "checks": f"{qa['status'].eq('PASS').sum()}/{len(qa)}", "formula_probes": len(probes), "models": 58, "candidates": 28, "performance_y_read": 0}
    (FACTORY / "reports" / "PRM104_independent_QA_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if summary["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
