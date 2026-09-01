from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

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


def shape_metrics(profile: np.ndarray) -> tuple[float, float, float, float]:
    profile = np.asarray(profile, dtype=float)
    probability = profile / profile.sum()
    position = np.linspace(0.0, 1.0, len(profile))
    center = float(np.dot(probability, position))
    spread = float(np.sqrt(np.dot(probability, (position - center) ** 2)))
    skewness = float(np.dot(probability, ((position - center) / spread) ** 3))
    kurtosis = float(
        np.dot(probability, ((position - center) / spread) ** 4) - 3.0
    )
    nonzero = probability[probability > 0]
    entropy = float(
        -np.dot(nonzero, np.log(nonzero)) / np.log(len(probability))
    )
    center_mass = float(
        profile[(position >= 0.25) & (position <= 0.75)].sum()
    )
    contrast = float((2.0 * center_mass - profile.sum()) / profile.sum())
    return skewness, kurtosis, entropy, contrast


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    hashes_ok = all(
        sha256(ROOT / item["path"]) == item["sha256"]
        for item in contract["inputs"]
    )
    manifest = pd.read_csv(ROOT / contract["inputs"][0]["path"])
    registry = pd.read_csv(
        TABLES / "PRM110_axial_shape_entropy_candidate_registry.csv"
    )
    values = pd.read_csv(TABLES / "PRM110_axial_shape_entropy_values_long.csv")
    wide = pd.read_csv(
        TABLES / "PRM110_axial_shape_entropy_values_wide.csv"
    ).set_index("model_id")
    crossbank = pd.read_csv(
        TABLES / "PRM110_axial_shape_entropy_vs_XREG_v0_7_redundancy.csv"
    )
    internal = pd.read_csv(
        TABLES / "PRM110_axial_shape_entropy_internal_redundancy.csv"
    )
    collision = pd.read_csv(
        TABLES / "PRM110_axial_shape_entropy_collision_diagnostic.csv"
    )
    models = sorted(wide.index.tolist())
    frozen = dict(zip(manifest["path"], manifest["sha256"]))
    source_ok = True
    for model in models:
        for name in ["slice_pixel_readback.csv", "overlay_pixel_readback.csv"]:
            path = f".tmp/t4rs4/P1000_S801/{model}/tables/{name}"
            source_ok = (
                source_ok
                and path in frozen
                and sha256(ROOT / path) == frozen[path]
            )

    slices = pd.read_csv(
        ROOT / ".tmp/t4rs4/P1000_S801/B3/tables/slice_pixel_readback.csv"
    ).sort_values("slice_index")
    overlay = pd.read_csv(
        ROOT / ".tmp/t4rs4/P1000_S801/B3/tables/overlay_pixel_readback.csv"
    ).sort_values("pair_index")
    slice_area = shape_metrics(slices["material_area_mm2"].to_numpy(float))
    slice_count = shape_metrics(slices["component_count_min2"].to_numpy(float))
    red = shape_metrics(overlay["red_pixel_count"].to_numpy(float))
    blue = shape_metrics(overlay["blue_pixel_count"].to_numpy(float))
    purple = shape_metrics(overlay["purple_pixel_count"].to_numpy(float))
    union = shape_metrics(overlay["union_pixel_count"].to_numpy(float))
    probes = {
        "RAW-X045::slice_material_area_axial_position_skewness": slice_area[0],
        "RAW-X045::slice_component_count_axial_position_excess_kurtosis": slice_count[1],
        "RAW-X046::overlay_red_pixel_count_normalized_profile_entropy": red[2],
        "RAW-X046::overlay_blue_pixel_count_center_edge_mass_contrast": blue[3],
        "RAW-X046::overlay_purple_pixel_count_axial_position_skewness": purple[0],
        "RAW-X046::overlay_union_pixel_count_normalized_profile_entropy": union[2],
    }
    probes_ok = all(
        np.isclose(
            float(wide.loc["B3", candidate_id]),
            expected,
            rtol=1e-12,
            atol=1e-12,
        )
        for candidate_id, expected in probes.items()
    )
    locks_ok = (
        not registry["active_feature"].any()
        and not registry["promoted"].any()
        and not registry["y_evidence"].any()
        and all(value == 0 for value in contract["locks"].values())
    )
    checks = [
        ("I110-01", hashes_ok, "four contract input hashes"),
        ("I110-02", len(models) == 58 and source_ok, "116 independently hash-verified raw sources"),
        (
            "I110-03",
            len(registry) == 24
            and (registry["operational_grade"] == "B").sum() == 18
            and (registry["operational_grade"] == "C").sum() == 6,
            "candidate/grade schema",
        ),
        (
            "I110-04",
            len(values) == 1392
            and np.isfinite(values["value"].to_numpy(float)).all()
            and wide.shape == (58, 24),
            "finite long/wide matrix",
        ),
        (
            "I110-05",
            len(crossbank) == 5208
            and len(internal) == 276
            and len(collision) == 48,
            "relation/collision shapes",
        ),
        ("I110-06", probes_ok, "six independent B3 formula probes"),
        (
            "I110-07",
            registry["candidate_group_id"].value_counts().to_dict()
            == {"RAW-X046": 16, "RAW-X045": 8},
            "declared group counts",
        ),
        ("I110-08", locks_ok, "no y/selection/promotion and locks intact"),
    ]
    qa = pd.DataFrame(
        [
            {
                "check_id": check_id,
                "status": "PASS" if ok else "FAIL",
                "detail": detail,
            }
            for check_id, ok, detail in checks
        ]
    )
    (FACTORY / "reports").mkdir(parents=True, exist_ok=True)
    qa.to_csv(
        FACTORY / "reports" / "PRM110_independent_QA.csv",
        index=False,
        encoding="utf-8-sig",
    )
    summary = {
        "status": "PASS" if qa["status"].eq("PASS").all() else "FAIL",
        "checks": f"{qa['status'].eq('PASS').sum()}/{len(qa)}",
        "formula_probes": len(probes),
        "models": 58,
        "candidates": 24,
        "performance_y_read": 0,
    }
    (FACTORY / "reports" / "PRM110_independent_QA_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    if summary["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
