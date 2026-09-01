from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
TABLES = LAB / "reports" / "tables"
FACTORY = LAB / "factories" / "PRM-108"
CONTRACT = FACTORY / "contracts" / "PRM-108_AXIAL_DISTRIBUTION_SYMMETRY_BATCH_CONTRACT_20260723.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1_048_576), b""):
            digest.update(chunk)
    return digest.hexdigest()


def centroid(values: np.ndarray) -> float:
    position = np.linspace(0.0, 1.0, len(values))
    return float(np.dot(values, position) / values.sum())


def spread(values: np.ndarray) -> float:
    position = np.linspace(0.0, 1.0, len(values)); center = np.dot(values, position) / values.sum()
    return float(np.sqrt(np.dot(values, (position - center) ** 2) / values.sum()))


def asymmetry(values: np.ndarray) -> float:
    return float(np.mean(np.abs(values - values[::-1])) / np.mean(np.abs(values)))


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    hashes_ok = all(sha256(ROOT / item["path"]) == item["sha256"] for item in contract["inputs"])
    manifest = pd.read_csv(ROOT / contract["inputs"][0]["path"])
    registry = pd.read_csv(TABLES / "PRM108_axial_distribution_symmetry_candidate_registry.csv")
    values = pd.read_csv(TABLES / "PRM108_axial_distribution_symmetry_values_long.csv")
    wide = pd.read_csv(TABLES / "PRM108_axial_distribution_symmetry_values_wide.csv").set_index("model_id")
    crossbank = pd.read_csv(TABLES / "PRM108_axial_distribution_symmetry_vs_XREG_v0_6_redundancy.csv")
    internal = pd.read_csv(TABLES / "PRM108_axial_distribution_symmetry_internal_redundancy.csv")
    collision = pd.read_csv(TABLES / "PRM108_axial_distribution_symmetry_collision_diagnostic.csv")
    models = sorted(wide.index.tolist())
    frozen = dict(zip(manifest["path"], manifest["sha256"]))
    source_ok = True
    for model in models:
        for name in ["slice_pixel_readback.csv", "overlay_pixel_readback.csv"]:
            path = f".tmp/t4rs4/P1000_S801/{model}/tables/{name}"
            source_ok = source_ok and path in frozen and sha256(ROOT / path) == frozen[path]
    slices = pd.read_csv(ROOT / ".tmp/t4rs4/P1000_S801/B3/tables/slice_pixel_readback.csv").sort_values("slice_index")
    overlay = pd.read_csv(ROOT / ".tmp/t4rs4/P1000_S801/B3/tables/overlay_pixel_readback.csv").sort_values("pair_index")
    area = slices["material_area_mm2"].to_numpy(float); count = slices["component_count_min2"].to_numpy(float); red = overlay["red_pixel_count"].to_numpy(float); union = overlay["union_pixel_count"].to_numpy(float); purple_fraction = overlay["purple_pixel_count"].to_numpy(float) / union
    probes = {
        "RAW-X041::slice_material_area_normalized_axial_centroid": centroid(area),
        "RAW-X041::slice_component_count_normalized_axial_spread": spread(count),
        "RAW-X042::overlay_red_pixel_count_normalized_axial_centroid": centroid(red),
        "RAW-X043::overlay_purple_fraction_normalized_axial_spread": spread(purple_fraction),
        "RAW-X044::slice_component_count_reflection_asymmetry": asymmetry(count),
        "RAW-X044::overlay_union_pixel_count_reflection_asymmetry": asymmetry(union),
    }
    probes_ok = all(np.isclose(float(wide.loc["B3", candidate_id]), expected, rtol=1e-12, atol=1e-12) for candidate_id, expected in probes.items())
    locks_ok = not registry["active_feature"].any() and not registry["promoted"].any() and not registry["y_evidence"].any() and all(value == 0 for value in contract["locks"].values())
    checks = [
        ("I108-01", hashes_ok, "four contract input hashes"),
        ("I108-02", len(models) == 58 and source_ok, "116 independently hash-verified raw sources"),
        ("I108-03", len(registry) == 24 and (registry["operational_grade"] == "B").sum() == 12 and (registry["operational_grade"] == "C").sum() == 12, "candidate/grade schema"),
        ("I108-04", len(values) == 1392 and np.isfinite(values["value"].to_numpy(float)).all() and wide.shape == (58, 24), "finite long/wide matrix"),
        ("I108-05", len(crossbank) == 4632 and len(internal) == 276 and len(collision) == 48, "relation/collision shapes"),
        ("I108-06", probes_ok, "six independent B3 formula probes"),
        ("I108-07", registry["candidate_group_id"].value_counts().to_dict() == {"RAW-X042": 8, "RAW-X043": 6, "RAW-X044": 6, "RAW-X041": 4}, "declared group counts"),
        ("I108-08", locks_ok, "no y/selection/promotion and locks intact"),
    ]
    qa = pd.DataFrame([{"check_id": check_id, "status": "PASS" if ok else "FAIL", "detail": detail} for check_id, ok, detail in checks])
    qa.to_csv(FACTORY / "reports" / "PRM108_independent_QA.csv", index=False, encoding="utf-8-sig")
    summary = {"status": "PASS" if qa["status"].eq("PASS").all() else "FAIL", "checks": f"{qa['status'].eq('PASS').sum()}/{len(qa)}", "formula_probes": len(probes), "models": 58, "candidates": 24, "performance_y_read": 0}
    (FACTORY / "reports" / "PRM108_independent_QA_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if summary["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
