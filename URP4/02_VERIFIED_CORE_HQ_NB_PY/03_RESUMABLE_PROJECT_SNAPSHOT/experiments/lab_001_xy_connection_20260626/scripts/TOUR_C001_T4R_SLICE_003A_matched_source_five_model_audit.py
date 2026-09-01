"""Source-matched five-model gate before the all-58 detailed image batch.

This R09-SCRIPT reuses the already validated T4R-SLICE-001 exact pipeline,
but replaces the unresolved cached B3/C1/L1/F1/F2 PNG provenance with frozen
canonical N40 STL paths and hashes.  It reads no performance y and fits no
predictive model.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import platform
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
FACTORY = LAB / "factories" / "TOUR-C001"
CONTRACT = FACTORY / "contracts" / "TOUR-C001_T4R_SLICE_003A_MATCHED_SOURCE_FIVE_MODEL_PREREGISTRATION_20260720.json"
RUN_ID = "TOUR-C001-T4R-SLICE-003A"
RUN_WORK = ROOT / ".tmp" / "t4rs3a"
FROZEN = FACTORY / "analysis_factory" / "frozen"
REPORTS = FACTORY / "analysis_factory" / "reports"
FIGURES = FACTORY / "analysis_factory" / "figures"
PRIOR_PROTECTED = REPORTS / "TOUR-C001-T4R-SLICE-002_protected_asset_verification.csv"
SOURCE_SCRIPT = LAB / "scripts" / "TOUR_C001_T4R_SLICE_001_t8_t9_legacy_detail_convergence.py"
OLD_CINT02 = LAB / "factories" / "CINT-02" / "outputs" / "CINT-02_panel_replay_actual.json"
RESLICE_ROOT = LAB / "runs" / "xrv1_s2" / "all58_20260715" / "models"
PANEL = ["B3", "C1", "L1", "F1", "F2"]
CONFIG_ID = "P1000_S801"
KST = timezone(timedelta(hours=9))

MODEL_PATHS = {
    "B3": LAB / "data" / "processed" / "n40_all58_20260715" / "stl" / "B3__a272cdb922__N40.stl",
    "C1": LAB / "data" / "processed" / "n40_all58_20260715" / "stl" / "C1__7755dda7d0__N40.stl",
    "L1": LAB / "data" / "processed" / "n40_all58_20260715" / "stl" / "L1__412f5bec5e__N40.stl",
    "F1": LAB / "data" / "processed" / "n40_all58_20260715" / "stl" / "F1__0dff3c1b13__N40.stl",
    "F2": LAB / "data" / "processed" / "n40_all58_20260715" / "stl" / "F2__69a3599146__N40.stl",
}
MODEL_HASHES = {
    "B3": "beb368e9c9945669cc202046802bd24ec15e70b61cd472ce061e2e482ba70afc",
    "C1": "d798f7b032de8eccfd771037e849b201c7604b833fc0ed8ce07e316529cc5729",
    "L1": "7189d16e6f812608f31cb7bf54f604caaf438272cbb31a45c153b8a2e8b0730a",
    "F1": "d76883bc10af4f4b3817ccbe90b2863f97c9b843f30c5214cde81d2f76fdb0f8",
    "F2": "bd471508c7d2073419cbf2c37f16d0d0a07690a5b4a660c5179230cf4ad285f4",
}
CONFIG = {
    "pixel_resolution": 1000,
    "slice_count": 801,
    "slice_spacing_mm": 0.05,
    "role": "canonical_N40_source_matched_rebuild",
}
SIGNALS = [
    {
        "signal_id": "SIG-A",
        "candidate_id": "LPA::angle::GLOBAL_WEIGHTED::stdev",
        "raw_candidate_ids": ["LPA::angle::GLOBAL_WEIGHTED::stdev"],
    },
    {
        "signal_id": "SIG-B",
        "candidate_id": "LPR::angle::IP::stdev",
        "raw_candidate_ids": ["LPR::angle::IP::stdev"],
    },
    {
        "signal_id": "SIG-C",
        "candidate_id": "LPR::angle::LAYER_MEAN::stdev",
        "raw_candidate_ids": ["LPR::angle::LIP::stdev", "LPR::angle::LTP::stdev"],
    },
    {
        "signal_id": "SIG-D",
        "candidate_id": "LPR::curvature::LTP::stdev",
        "raw_candidate_ids": ["LPR::curvature::LTP::stdev"],
    },
]


def now_kst() -> str:
    return datetime.now(KST).isoformat(timespec="seconds")


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    records = list(rows)
    if not records:
        raise ValueError(f"refusing to write empty CSV: {path}")
    columns: list[str] = []
    for row in records:
        for key in row:
            if key not in columns:
                columns.append(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def configure_exact_pipeline():
    base = load_module(SOURCE_SCRIPT, "tour_c001_t4r_slice_001_reused_by_003a")
    base.CONTRACT = CONTRACT
    base.RUN_ID = RUN_ID
    base.RUN_WORK = RUN_WORK
    base.MODEL_PATHS = MODEL_PATHS
    base.MODEL_HASHES = MODEL_HASHES
    base.CONFIGS = {CONFIG_ID: CONFIG}
    base.NEW_CONFIGS = [CONFIG_ID]
    return base


def validate_contract() -> dict[str, Any]:
    if Path(sys.executable).resolve() != (ROOT / "tools" / "envs" / "KMK312" / "python.exe").resolve():
        raise RuntimeError(f"KMK312 required, received {sys.executable}")
    if sys.version_info[:2] != (3, 12):
        raise RuntimeError(f"Python 3.12 required, received {platform.python_version()}")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    failures: list[str] = []
    for section in ("parent_evidence", "cached_png_inventory_evidence"):
        for item in contract[section]:
            path = ROOT / item["path"]
            actual = sha256_file(path) if path.is_file() else "missing"
            if actual != item["sha256"]:
                failures.append(f"{item['path']} expected={item['sha256']} actual={actual}")
    for item in contract["fixed_geometry"]:
        path = ROOT / item["path"]
        actual = sha256_file(path) if path.is_file() else "missing"
        if actual != item["sha256"] or actual != MODEL_HASHES[item["model_id"]]:
            failures.append(f"{item['model_id']} geometry expected={item['sha256']} actual={actual}")
    if failures:
        raise RuntimeError("contract hash gate failed: " + " | ".join(failures))
    return contract


def run_one(model_id: str) -> None:
    validate_contract()
    if model_id not in PANEL:
        raise ValueError(model_id)
    base = configure_exact_pipeline()
    base.run_one(model_id, CONFIG_ID)


def symmetric_relative_difference(a: float, b: float) -> float:
    denominator = abs(a) + abs(b)
    if denominator <= 1e-12:
        return 0.0
    return 2.0 * abs(a - b) / (denominator + 1e-12)


def weighted_std(values: np.ndarray, weights: np.ndarray) -> float:
    valid = np.isfinite(values) & np.isfinite(weights) & (weights > 0)
    if not np.any(valid):
        return math.nan
    values = values[valid]
    weights = weights[valid]
    avg = np.sum(values * weights) / np.sum(weights)
    return float(np.sqrt(np.sum(weights * (values - avg) ** 2) / np.sum(weights)))


def extract_selected(frame: pd.DataFrame, source_lane: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    selected: list[dict[str, Any]] = []
    duplicate_trace: list[dict[str, Any]] = []
    for model_id in PANEL:
        model = frame[frame["model_id"].eq(model_id)]
        for signal in SIGNALS:
            raw = model[model["candidate_id"].isin(signal["raw_candidate_ids"])]
            if len(raw) != len(signal["raw_candidate_ids"]):
                raise RuntimeError(f"{source_lane}/{model_id}/{signal['signal_id']}: source rows missing")
            values = raw["value"].astype(float).to_numpy()
            duplicate_equal = bool(np.allclose(values, values[0], rtol=1e-12, atol=1e-12, equal_nan=False))
            if signal["signal_id"] == "SIG-C" and not duplicate_equal:
                raise RuntimeError(f"{source_lane}/{model_id}: LIP/LTP angle source duplicate diverged")
            selected.append(
                {
                    "model_id": model_id,
                    "model_family": model_id[0],
                    "signal_id": signal["signal_id"],
                    "canonical_candidate_id": signal["candidate_id"],
                    "source_lane": source_lane,
                    "value": float(values[0]),
                    "raw_source_row_count": len(values),
                    "raw_duplicate_equal": duplicate_equal,
                }
            )
            for row in raw.itertuples(index=False):
                duplicate_trace.append(
                    {
                        "model_id": model_id,
                        "signal_id": signal["signal_id"],
                        "source_lane": source_lane,
                        "raw_candidate_id": row.candidate_id,
                        "value": float(row.value),
                        "raw_duplicate_equal": duplicate_equal,
                    }
                )
    return selected, duplicate_trace


def old_cached_full_values(base) -> pd.DataFrame:
    payload = json.loads(OLD_CINT02.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    for model_id in PANEL:
        model_payload = {
            "LEGACY-PY-RESULT": payload[model_id]["LEGACY-PY-RESULT"],
            "LEGACY-PY-ANGLE-ALL": payload[model_id]["LEGACY-PY-ANGLE-ALL"],
        }
        rows.extend(base.descriptor_rows(model_id, CONFIG_ID, model_payload))
    return pd.DataFrame(rows)


def reslice_proxy_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for model_id in PANEL:
        path = RESLICE_ROOT / model_id / "a01" / "tables" / "overlay_component_table.csv"
        frame = pd.read_csv(path)
        # R09-RESLICE-003 kept connected components at min_component_pixels=2.
        # No-contact angles are restored to LEGACY-PY's explicit 90-degree value.
        a2h = frame["angle_current_2h_contact_sum"].astype(float).fillna(90.0).to_numpy()
        ah = frame["angle_h_contact_sum"].astype(float).fillna(90.0).to_numpy()
        weights = frame["physical_weight_volume"].astype(float).to_numpy()
        layer_angle = frame.assign(_ah=pd.Series(ah, index=frame.index)).groupby("pair_index")["_ah"].mean().to_numpy()
        layer_total = frame.groupby("pair_index", as_index=False).agg(red_area=("red_area", "sum"), blue_area=("blue_area", "sum"))
        curvature_ltp = (np.sqrt(layer_total["red_area"].to_numpy()) + np.sqrt(layer_total["blue_area"].to_numpy())) / (2.0 * 0.05)
        values = {
            "SIG-A": weighted_std(a2h, weights),
            "SIG-B": float(np.std(ah)),
            "SIG-C": float(np.std(layer_angle)),
            "SIG-D": float(np.std(curvature_ltp)),
        }
        for signal_id, value in values.items():
            rows.append(
                {
                    "model_id": model_id,
                    "model_family": model_id[0],
                    "signal_id": signal_id,
                    "source_lane": "R09-RESLICE-003_min2_table_proxy",
                    "value": value,
                    "component_rows": len(frame),
                    "layer_rows_present": int(frame["pair_index"].nunique()),
                    "diagnostic_boundary": "min-2 component/table proxy; not exact LEGACY-PY replacement",
                }
            )
    return rows


def signal_summary(selected: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for signal in SIGNALS:
        group = selected[selected["signal_id"].eq(signal["signal_id"])].set_index("model_id").loc[PANEL]
        values = group["value"].astype(float).to_numpy()
        median = float(np.median(values))
        mad = float(np.median(np.abs(values - median)))
        std = float(np.std(values))
        finite = int(np.isfinite(values).sum())
        unique_count = int(np.unique(np.round(values, 12)).size)
        rows.append(
            {
                "signal_id": signal["signal_id"],
                "candidate_id": signal["candidate_id"],
                "finite_count": finite,
                "panel_count": len(PANEL),
                "unique_count": unique_count,
                "population_std": std,
                "median_absolute_deviation": mad,
                "coefficient_of_variation": std / abs(float(np.mean(values))) if abs(float(np.mean(values))) > 1e-12 else math.nan,
                "applicability_pass": finite == 5 and unique_count >= 4 and std > 1e-12 and mad > 1e-12,
                "decision_status": "likely" if finite == 5 and unique_count >= 4 and std > 1e-12 and mad > 1e-12 else "rejected",
            }
        )
    return pd.DataFrame(rows)


def redundancy(selected: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    pivot = selected.pivot(index="model_id", columns="signal_id", values="value").loc[PANEL, [x["signal_id"] for x in SIGNALS]]
    spearman = pivot.rank(method="average").corr(method="pearson")
    pairs: list[dict[str, Any]] = []
    parent = {signal["signal_id"]: signal["signal_id"] for signal in SIGNALS}

    def find(value: str) -> str:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    ids = [signal["signal_id"] for signal in SIGNALS]
    for i, left in enumerate(ids):
        for right in ids[i + 1 :]:
            a = pivot[left].to_numpy(dtype=float)
            b = pivot[right].to_numpy(dtype=float)
            scale = float(np.dot(a, b) / np.dot(a, a)) if float(np.dot(a, a)) > 1e-18 else math.nan
            predicted = a * scale
            residuals = np.array([symmetric_relative_difference(x, y) for x, y in zip(predicted, b, strict=True)])
            exact = bool(np.allclose(a, b, rtol=1e-12, atol=1e-12))
            proportional = bool(np.isfinite(scale) and float(np.max(residuals)) <= 0.01)
            rho = float(spearman.loc[left, right])
            clustered = exact or (abs(rho) >= 0.95 and proportional)
            if clustered:
                union(left, right)
            pairs.append(
                {
                    "signal_a": left,
                    "signal_b": right,
                    "pearson_r": float(pivot[left].corr(pivot[right], method="pearson")),
                    "spearman_rho": rho,
                    "through_origin_scale_b_from_a": scale,
                    "max_symmetric_relative_residual": float(np.max(residuals)),
                    "exact_duplicate": exact,
                    "proportional_duplicate": proportional,
                    "same_redundancy_cluster": clustered,
                }
            )
    clusters: dict[str, list[str]] = {}
    for signal_id in ids:
        clusters.setdefault(find(signal_id), []).append(signal_id)
    cluster_rows = [
        {"cluster_id": f"RC-{index:02d}", "signal_ids": "|".join(members), "signal_count": len(members)}
        for index, members in enumerate(clusters.values(), 1)
    ]
    matrix_rows = []
    for left in ids:
        for right in ids:
            matrix_rows.append({"signal_a": left, "signal_b": right, "spearman_rho": float(spearman.loc[left, right])})
    return pd.DataFrame(pairs), pd.DataFrame(cluster_rows), pd.DataFrame(matrix_rows)


def protected_verification() -> tuple[Path, list[dict[str, Any]]]:
    prior = pd.read_csv(PRIOR_PROTECTED, dtype=str, keep_default_na=False)
    rows: list[dict[str, Any]] = []
    for item in prior.itertuples(index=False):
        path = ROOT / item.path
        if item.guard_kind == "site_git_state":
            actual_hash = subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()
            actual_size = ""
        elif item.guard_kind == "site_git_status":
            status_bytes = subprocess.check_output(["git", "-C", str(path), "status", "--porcelain"])
            actual_hash = hashlib.sha256(status_bytes).hexdigest()
            actual_size = ""
        else:
            actual_hash = sha256_file(path) if path.is_file() else "missing"
            actual_size = str(path.stat().st_size) if path.is_file() else "missing"
        expected_hash = item.actual_sha256
        expected_size = item.actual_size_bytes
        status = "unchanged" if actual_hash == expected_hash and actual_size == expected_size else "changed_or_missing"
        rows.append(
            {
                "guard_kind": item.guard_kind,
                "path": item.path,
                "source_alias": item.source_alias,
                "expected_sha256_from_SLICE002_after": expected_hash,
                "actual_sha256": actual_hash,
                "expected_size_bytes": expected_size,
                "actual_size_bytes": actual_size,
                "verification_status": status,
            }
        )
    target = REPORTS / f"{RUN_ID}_protected_asset_verification.csv"
    write_csv(target, rows)
    return target, rows


def make_figures(new_selected: pd.DataFrame, comparison: pd.DataFrame, spearman_long: pd.DataFrame) -> list[Path]:
    FIGURES.mkdir(parents=True, exist_ok=True)
    pivot = new_selected.pivot(index="signal_id", columns="model_id", values="value").loc[[x["signal_id"] for x in SIGNALS], PANEL]
    robust = pivot.copy()
    for signal_id in robust.index:
        values = pivot.loc[signal_id].to_numpy(dtype=float)
        median = float(np.median(values))
        mad = float(np.median(np.abs(values - median)))
        scale = 1.4826 * mad if mad > 1e-12 else float(np.std(values))
        robust.loc[signal_id] = (values - median) / scale if scale > 1e-12 else np.zeros_like(values)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    image = ax.imshow(robust.to_numpy(dtype=float), cmap="coolwarm", aspect="auto")
    ax.set_xticks(range(len(PANEL)), PANEL)
    ax.set_yticks(range(len(robust.index)), robust.index)
    ax.set_title("Source-matched canonical N40 panel: robust z-score")
    fig.colorbar(image, ax=ax, label="robust z")
    fig.tight_layout()
    z_path = FIGURES / f"{RUN_ID}_matched_panel_robust_z_heatmap.png"
    fig.savefig(z_path, dpi=190)
    plt.close(fig)

    delta = comparison.pivot(index="signal_id", columns="model_id", values="old_vs_new_symmetric_relative_difference").loc[[x["signal_id"] for x in SIGNALS], PANEL] * 100.0
    fig, ax = plt.subplots(figsize=(9, 4.5))
    image = ax.imshow(delta.to_numpy(dtype=float), cmap="magma", aspect="auto")
    ax.set_xticks(range(len(PANEL)), PANEL)
    ax.set_yticks(range(len(delta.index)), delta.index)
    ax.set_title("Old cached versus source-matched N40 LEGACY-PY difference")
    fig.colorbar(image, ax=ax, label="symmetric relative difference (%)")
    fig.tight_layout()
    delta_path = FIGURES / f"{RUN_ID}_old_vs_matched_difference_heatmap.png"
    fig.savefig(delta_path, dpi=190)
    plt.close(fig)

    matrix = spearman_long.pivot(index="signal_a", columns="signal_b", values="spearman_rho").loc[[x["signal_id"] for x in SIGNALS], [x["signal_id"] for x in SIGNALS]]
    fig, ax = plt.subplots(figsize=(6, 5))
    image = ax.imshow(matrix.to_numpy(dtype=float), vmin=-1, vmax=1, cmap="coolwarm")
    ax.set_xticks(range(len(matrix.columns)), matrix.columns)
    ax.set_yticks(range(len(matrix.index)), matrix.index)
    for i in range(len(matrix.index)):
        for j in range(len(matrix.columns)):
            ax.text(j, i, f"{matrix.iloc[i, j]:.2f}", ha="center", va="center", fontsize=9)
    ax.set_title("Source-matched panel Spearman redundancy")
    fig.colorbar(image, ax=ax, label="Spearman rho")
    fig.tight_layout()
    corr_path = FIGURES / f"{RUN_ID}_matched_panel_spearman_heatmap.png"
    fig.savefig(corr_path, dpi=190)
    plt.close(fig)

    thumb = 260
    label_h = 35
    canvas = Image.new("RGB", (len(PANEL) * thumb, thumb + label_h), "white")
    draw = ImageDraw.Draw(canvas)
    for index, model_id in enumerate(PANEL):
        source = RUN_WORK / CONFIG_ID / model_id / "audit_images" / "combine_0400.png"
        with Image.open(source) as image_item:
            image_item = image_item.convert("RGB")
            image_item.thumbnail((thumb, thumb))
            x = index * thumb + (thumb - image_item.width) // 2
            y = label_h + (thumb - image_item.height) // 2
            canvas.paste(image_item, (x, y))
        draw.text((index * thumb + 10, 10), f"{model_id} / N40 / pair 400", fill="black")
    contact_path = FIGURES / f"{RUN_ID}_matched_midplane_contact_sheet.png"
    canvas.save(contact_path)
    return [z_path, delta_path, corr_path, contact_path]


def aggregate() -> None:
    contract = validate_contract()
    base = configure_exact_pipeline()
    complete_rows: list[dict[str, Any]] = []
    full_frames: list[pd.DataFrame] = []
    for model_id in PANEL:
        model_root = RUN_WORK / CONFIG_ID / model_id
        complete_path = model_root / "complete.json"
        if not complete_path.is_file():
            raise FileNotFoundError(f"incomplete model: {model_id}")
        complete = json.loads(complete_path.read_text(encoding="utf-8"))
        values_path = model_root / "candidate_values.csv"
        if complete.get("status") != "passed" or complete.get("geometry_sha256") != MODEL_HASHES[model_id]:
            raise RuntimeError(f"failed/source-mismatched model: {model_id}")
        complete_rows.append(complete)
        full_frames.append(pd.read_csv(values_path))
    new_full = pd.concat(full_frames, ignore_index=True)
    if len(new_full) != 200 or new_full.groupby("model_id").size().ne(40).any():
        raise RuntimeError("expected five models x 40 mapped values")

    old_full = old_cached_full_values(base)
    new_selected_rows, new_duplicate_rows = extract_selected(new_full, "canonical_N40_exact_LEGACY_PY")
    old_selected_rows, old_duplicate_rows = extract_selected(old_full, "old_cached_CINT02_unresolved_geometry")
    new_selected = pd.DataFrame(new_selected_rows)
    old_selected = pd.DataFrame(old_selected_rows)
    proxy = pd.DataFrame(reslice_proxy_rows())

    comparison = new_selected[["model_id", "model_family", "signal_id", "canonical_candidate_id", "value"]].rename(columns={"value": "new_source_matched_value"})
    comparison = comparison.merge(old_selected[["model_id", "signal_id", "value"]].rename(columns={"value": "old_cached_value"}), on=["model_id", "signal_id"], validate="one_to_one")
    comparison = comparison.merge(proxy[["model_id", "signal_id", "value"]].rename(columns={"value": "reslice_min2_proxy_value"}), on=["model_id", "signal_id"], validate="one_to_one")
    comparison["old_vs_new_symmetric_relative_difference"] = [
        symmetric_relative_difference(float(a), float(b)) for a, b in zip(comparison["old_cached_value"], comparison["new_source_matched_value"], strict=True)
    ]
    comparison["reslice_proxy_vs_new_symmetric_relative_difference"] = [
        symmetric_relative_difference(float(a), float(b)) for a, b in zip(comparison["reslice_min2_proxy_value"], comparison["new_source_matched_value"], strict=True)
    ]
    comparison["old_provenance_status"] = "unresolved"
    comparison["new_provenance_status"] = "confirmed"
    comparison["proxy_status"] = "diagnostic_only"

    provenance_rows: list[dict[str, Any]] = []
    for item in contract["cached_png_inventory_evidence"]:
        inventory = json.loads((ROOT / item["path"]).read_text(encoding="utf-8"))
        provenance_rows.append(
            {
                "model_id": item["model_id"],
                "old_png_inventory_path": item["path"],
                "old_png_count": inventory.get("png_count", ""),
                "old_source_stl": inventory.get("source_stl", ""),
                "old_source_sha256": inventory.get("source_sha256", ""),
                "old_settings_json": inventory.get("settings_json", ""),
                "old_source_identity_status": "unresolved" if not inventory.get("source_stl") or not inventory.get("source_sha256") else "confirmed",
                "new_geometry_path": rel(MODEL_PATHS[item["model_id"]]),
                "new_geometry_sha256": MODEL_HASHES[item["model_id"]],
                "new_source_identity_status": "confirmed",
            }
        )

    summary = signal_summary(new_selected)
    pair, clusters, spearman_long = redundancy(new_selected)
    applicable = int(summary["applicability_pass"].sum())
    cluster_count = len(clusters)
    technical_pass = all(
        row["status"] == "passed"
        and row["slice_rows"] == 801
        and row["overlay_rows"] == 800
        and row["candidate_rows"] == 40
        and row["readback_mismatch_sum"] == 0
        and row["transient_png_remaining"] == 0
        and row["audit_png_retained"] == 6
        and row["geometry_sha256"] == MODEL_HASHES[row["model_id"]]
        for row in complete_rows
    )
    selected_finite = bool(np.isfinite(new_selected["value"].astype(float)).all())
    go = technical_pass and selected_finite and applicable >= 2 and cluster_count >= 2
    decision = {
        "run_id": RUN_ID,
        "decision": "GO_SEPARATE_ALL58_SOURCE_MATCHED_CONTRACT" if go else "HOLD_ALL58_SOURCE_MATCHED_EXECUTION",
        "technical_source_gate_pass": technical_pass,
        "selected_value_rows": len(new_selected),
        "selected_values_all_finite": selected_finite,
        "applicable_signal_count": applicable,
        "total_signal_count": len(SIGNALS),
        "nonduplicate_redundancy_cluster_count": cluster_count,
        "old_cached_geometry_provenance": "unresolved",
        "new_canonical_N40_geometry_provenance": "confirmed",
        "decision_status": "likely" if go else "unresolved",
        "scientific_boundary": "Authorizes only a separately preregistered source-matched all-58 x-only extraction; no y, fit, promotion, formula canon, roster change, T5 or inverse design.",
    }

    FROZEN.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    paths = {
        "all40": FROZEN / f"{RUN_ID}_all40_source_matched_candidate_values.csv",
        "new": FROZEN / f"{RUN_ID}_selected_source_matched_values.csv",
        "old": FROZEN / f"{RUN_ID}_selected_old_cached_values.csv",
        "proxy": FROZEN / f"{RUN_ID}_selected_reslice_min2_proxy_values.csv",
        "comparison": FROZEN / f"{RUN_ID}_three_lane_comparison.csv",
        "duplicates": FROZEN / f"{RUN_ID}_source_duplicate_trace.csv",
        "summary": FROZEN / f"{RUN_ID}_signal_summary.csv",
        "pairs": FROZEN / f"{RUN_ID}_redundancy_pairs.csv",
        "clusters": FROZEN / f"{RUN_ID}_redundancy_clusters.csv",
        "spearman": FROZEN / f"{RUN_ID}_spearman_matrix.csv",
        "decision": FROZEN / f"{RUN_ID}_all58_go_hold_decision.csv",
        "provenance": REPORTS / f"{RUN_ID}_cached_vs_matched_provenance_audit.csv",
        "model_qa": REPORTS / f"{RUN_ID}_model_execution_QA.csv",
    }
    new_full.to_csv(paths["all40"], index=False, encoding="utf-8-sig")
    new_selected.to_csv(paths["new"], index=False, encoding="utf-8-sig")
    old_selected.to_csv(paths["old"], index=False, encoding="utf-8-sig")
    proxy.to_csv(paths["proxy"], index=False, encoding="utf-8-sig")
    comparison.to_csv(paths["comparison"], index=False, encoding="utf-8-sig")
    pd.DataFrame(new_duplicate_rows + old_duplicate_rows).to_csv(paths["duplicates"], index=False, encoding="utf-8-sig")
    summary.to_csv(paths["summary"], index=False, encoding="utf-8-sig")
    pair.to_csv(paths["pairs"], index=False, encoding="utf-8-sig")
    clusters.to_csv(paths["clusters"], index=False, encoding="utf-8-sig")
    spearman_long.to_csv(paths["spearman"], index=False, encoding="utf-8-sig")
    write_csv(paths["decision"], [decision])
    write_csv(paths["provenance"], provenance_rows)
    write_csv(paths["model_qa"], complete_rows)

    figures = make_figures(new_selected, comparison, spearman_long)
    protected_path, protected_rows = protected_verification()
    protected_pass = all(row["verification_status"] == "unchanged" for row in protected_rows)
    qa_rows = [
        {"test_id": "environment_KMK312_python312", "passed": Path(sys.executable).resolve() == (ROOT / "tools" / "envs" / "KMK312" / "python.exe").resolve() and sys.version_info[:2] == (3, 12), "details": sys.executable},
        {"test_id": "contract_hash_gate", "passed": True, "details": rel(CONTRACT)},
        {"test_id": "five_model_technical_source_gate", "passed": technical_pass, "details": f"{sum(row['status']=='passed' for row in complete_rows)}/5"},
        {"test_id": "all40_census", "passed": len(new_full) == 200, "details": str(len(new_full))},
        {"test_id": "selected_signal_census", "passed": len(new_selected) == 20, "details": str(len(new_selected))},
        {"test_id": "selected_values_finite", "passed": selected_finite, "details": f"{int(np.isfinite(new_selected['value']).sum())}/20"},
        {"test_id": "SIG_C_source_duplicate", "passed": bool(new_selected[new_selected['signal_id'].eq('SIG-C')]['raw_duplicate_equal'].all()), "details": "LEGACY-PY-RESULT LIP/LTP angle stdev"},
        {"test_id": "old_cached_provenance_exposed", "passed": all(row["old_source_identity_status"] == "unresolved" for row in provenance_rows), "details": "5/5 empty source path/hash"},
        {"test_id": "new_source_provenance_confirmed", "passed": all(row["new_source_identity_status"] == "confirmed" for row in provenance_rows), "details": "5/5 canonical N40 path/hash"},
        {"test_id": "transient_png_deleted", "passed": all(row["transient_png_remaining"] == 0 for row in complete_rows), "details": f"deleted={sum(row['transient_png_deleted'] for row in complete_rows)}"},
        {"test_id": "audit_png_retained", "passed": all(row["audit_png_retained"] == 6 for row in complete_rows), "details": f"retained={sum(row['audit_png_retained'] for row in complete_rows)}"},
        {"test_id": "protected_assets_unchanged", "passed": protected_pass, "details": f"{sum(row['verification_status']=='unchanged' for row in protected_rows)}/{len(protected_rows)}"},
        {"test_id": "no_y_no_fit_no_promotion", "passed": True, "details": "contract and script contain x-only comparison lanes"},
    ]
    qa_path = REPORTS / f"{RUN_ID}_QA.csv"
    write_csv(qa_path, qa_rows)
    qa_pass = all(row["passed"] for row in qa_rows)
    if not qa_pass:
        decision["decision"] = "HOLD_ALL58_SOURCE_MATCHED_EXECUTION"
        decision["decision_status"] = "unresolved"
        write_csv(paths["decision"], [decision])

    attempt_path = REPORTS / f"{RUN_ID}_attempt_history.csv"
    write_csv(
        attempt_path,
        [
            {
                "attempt_id": "A01",
                "status": "passed" if qa_pass else "failed",
                "runtime_environment": "KMK312",
                "models": "|".join(PANEL),
                "source_configuration": CONFIG_ID,
                "scientific_changes_after_freeze": "none",
                "completed_at_kst": now_kst(),
            }
        ],
    )
    execution_summary = {
        "run_id": RUN_ID,
        "status": "passed" if qa_pass else "failed",
        "runtime_environment": "KMK312",
        "models": PANEL,
        "configuration": CONFIG_ID,
        "model_runs": len(complete_rows),
        "candidate_value_rows": len(new_full),
        "selected_value_rows": len(new_selected),
        "applicable_signal_count": applicable,
        "redundancy_cluster_count": cluster_count,
        "decision": decision["decision"],
        "old_cached_geometry_provenance": "unresolved",
        "new_canonical_N40_geometry_provenance": "confirmed",
        "performance_y_accessed": False,
        "predictive_model_fit": False,
        "feature_promotions": 0,
        "transient_png_deleted": sum(row["transient_png_deleted"] for row in complete_rows),
        "audit_png_retained": sum(row["audit_png_retained"] for row in complete_rows),
        "completed_at_kst": now_kst(),
        "scientific_boundary": decision["scientific_boundary"],
    }
    summary_path = REPORTS / f"{RUN_ID}_execution_summary.json"
    write_json(summary_path, execution_summary)
    manifest_targets = [
        CONTRACT,
        Path(__file__),
        *paths.values(),
        *figures,
        protected_path,
        qa_path,
        attempt_path,
        summary_path,
    ]
    manifest_path = REPORTS / f"{RUN_ID}_output_manifest.csv"
    write_csv(manifest_path, [{"path": rel(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)} for path in manifest_targets])
    print(json.dumps(execution_summary, ensure_ascii=False, indent=2), flush=True)
    if not qa_pass:
        raise SystemExit(2)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["run-one", "aggregate"])
    parser.add_argument("--model", choices=PANEL)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "run-one":
        if not args.model:
            raise SystemExit("--model required")
        run_one(args.model)
    else:
        aggregate()


if __name__ == "__main__":
    main()
