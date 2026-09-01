"""Bounded T8/T9 image-descriptor convergence rescue (no predictive fit).

The experiment reuses the known CINT-02 1000x801 baseline, calculates only
three preregistered pixel/slice perturbations, invokes immutable LEGACY-PY
through the validated adapters, and deletes transient PNGs after hashes,
primitive tables, direct descriptor values, and deterministic audit images
have been frozen.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import os
import platform
import shutil
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

import cv2
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
SCRIPT_DIR = LAB / "scripts"
FACTORY = LAB / "factories" / "TOUR-C001"
CONTRACT = FACTORY / "contracts" / "TOUR-C001_T4R_SLICE_001_T8_T9_CONVERGENCE_PREREGISTRATION_20260720.json"
WORK = FACTORY / "analysis_factory" / "intermediate" / "TOUR-C001-T4R-SLICE-001"
# Windows' classic path limit is exceeded by 1600 transient PNG paths under
# the official factory tree.  Only resumable run-time material uses this
# short, experiment-scoped path; frozen tables/reports stay in the factory.
RUN_WORK = ROOT / ".tmp" / "t4rs1"
FROZEN = FACTORY / "analysis_factory" / "frozen"
REPORTS = FACTORY / "analysis_factory" / "reports"
FIGURES = FACTORY / "analysis_factory" / "figures"
RUN_ID = "TOUR-C001-T4R-SLICE-001"
KST = timezone(timedelta(hours=9))

BASELINE_JSON = LAB / "factories" / "CINT-02" / "outputs" / "CINT-02_panel_replay_actual.json"
BASELINE_PNG = LAB / "factories" / "CINT-02" / "runtime" / "panel_png"
PROBE_PATH = SCRIPT_DIR / "R09_ppt_slice_setting_reproduction_probe.py"
PRIOR_PROTECTED = REPORTS / "TOUR-C001-T4R-001_protected_asset_verification.csv"

MODEL_PATHS = {
    "T8": LAB / "data" / "processed" / "n40_all58_20260715" / "stl" / "T8__9db42618a6__N40.stl",
    "T9": LAB / "data" / "processed" / "n40_all58_20260715" / "stl" / "T9__f466dfe3fd__N40.stl",
}
MODEL_HASHES = {
    "T8": "24d0c1b1f1e190fcea3da70ec421968fc7cf58d8dccf367c34e8263db5677933",
    "T9": "76bc0f0bd05dbe549c0fcfd5321a46b9d99ce71631faa4346a0ad2db27c9b429",
}
CONFIGS = {
    "P1000_S801": {"pixel_resolution": 1000, "slice_count": 801, "slice_spacing_mm": 0.05, "role": "known_baseline"},
    "P500_S801": {"pixel_resolution": 500, "slice_count": 801, "slice_spacing_mm": 0.05, "role": "new_pixel_perturbation"},
    "P1000_S401": {"pixel_resolution": 1000, "slice_count": 401, "slice_spacing_mm": 0.10, "role": "new_slice_perturbation"},
    "P500_S401": {"pixel_resolution": 500, "slice_count": 401, "slice_spacing_mm": 0.10, "role": "new_combined_perturbation"},
}
NEW_CONFIGS = ["P500_S801", "P1000_S401", "P500_S401"]

SLICE_GROUPS = ["mass_orientation", "curvature", "angle", "perimeter_to_area"]
POP_STATS = [("IP", "avg"), ("IP", "stdev"), ("LIP", "avg"), ("LIP", "stdev"), ("LTP", "avg"), ("LTP", "stdev")]
ANGLE_ALL_GROUPS = ["angle", "thickness", "massori", "curvature", "pta"]

sys.path.insert(0, str(ROOT))
from urp4.legacy_reference.v0_1.adapters import run_angle_all, run_slice_result  # noqa: E402
from urp4.legacy_reference.v0_1.loader import sha256_file  # noqa: E402


def now_kst() -> str:
    return datetime.now(KST).isoformat(timespec="seconds")


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def hash_json(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


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


def validate_environment_and_contract() -> dict[str, Any]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if Path(sys.executable).resolve() != (ROOT / "tools" / "envs" / "KMK312" / "python.exe").resolve():
        raise RuntimeError(f"KMK312 required, received {sys.executable}")
    if sys.version_info[:2] != (3, 12):
        raise RuntimeError(f"Python 3.12 required, received {sys.version}")
    failed: list[str] = []
    for item in contract["parent_evidence"]:
        path = ROOT / item["path"]
        actual = sha256_file(path) if path.is_file() else "missing"
        if actual != item["sha256"]:
            failed.append(f"{item['path']} expected={item['sha256']} actual={actual}")
    for model_id, path in MODEL_PATHS.items():
        actual = sha256_file(path) if path.is_file() else "missing"
        if actual != MODEL_HASHES[model_id]:
            failed.append(f"{model_id} geometry expected={MODEL_HASHES[model_id]} actual={actual}")
    if failed:
        raise RuntimeError("contract hash gate failed: " + " | ".join(failed))
    return contract


def config_hash(config_id: str) -> str:
    payload = {"config_id": config_id, "physical_size_mm": 40.0, "axis": "z", "slice_mode": "endpoint", **CONFIGS[config_id]}
    return hash_json(payload)


def exact_combine(lower: np.ndarray, upper: np.ndarray) -> np.ndarray:
    lower_b = np.asarray(lower, dtype=bool)
    upper_b = np.asarray(upper, dtype=bool)
    image = np.zeros((*lower_b.shape, 3), dtype=np.uint8)
    image[lower_b & ~upper_b] = [0, 0, 255]
    image[upper_b & ~lower_b] = [255, 0, 0]
    image[lower_b & upper_b] = [255, 0, 255]
    return image


def descriptor_rows(model_id: str, config_id: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    result = payload["LEGACY-PY-RESULT"]
    slice_values = result["slice_values"]
    if len(slice_values) != 24 or len(result["thickness_values"]) != 6:
        raise RuntimeError(f"{model_id}/{config_id}: unexpected LEGACY-PY-RESULT output shape")
    cursor = 0
    for descriptor in SLICE_GROUPS:
        for population, statistic in POP_STATS:
            rows.append(
                {
                    "model_id": model_id,
                    "config_id": config_id,
                    "candidate_id": f"LPR::{descriptor}::{population}::{statistic}",
                    "source_alias": "LEGACY-PY-RESULT",
                    "source_file": "2._Parameter_result_0727.py",
                    "descriptor": descriptor,
                    "population": population,
                    "statistic": statistic,
                    "value": float(slice_values[cursor]),
                    "unit": "dimensionless" if descriptor == "mass_orientation" else ("degree" if descriptor == "angle" else "legacy_formula_unit"),
                    "candidate_status": "sensitivity_rescue_not_canonical",
                }
            )
            cursor += 1
    for index, (population, statistic) in enumerate(POP_STATS):
        rows.append(
            {
                "model_id": model_id,
                "config_id": config_id,
                "candidate_id": f"LPR::thickness::{population}::{statistic}",
                "source_alias": "LEGACY-PY-RESULT",
                "source_file": "2._Parameter_result_0727.py",
                "descriptor": "thickness",
                "population": population,
                "statistic": statistic,
                "value": float(result["thickness_values"][index]),
                "unit": "mm^2_area",
                "candidate_status": "sensitivity_rescue_not_canonical",
            }
        )
    summary = payload["LEGACY-PY-ANGLE-ALL"]["summary"]
    descriptor_alias = {"massori": "mass_orientation", "pta": "perimeter_to_area"}
    for raw_descriptor in ANGLE_ALL_GROUPS:
        descriptor = descriptor_alias.get(raw_descriptor, raw_descriptor)
        for index, statistic in enumerate(("avg", "stdev")):
            rows.append(
                {
                    "model_id": model_id,
                    "config_id": config_id,
                    "candidate_id": f"LPA::{descriptor}::GLOBAL_WEIGHTED::{statistic}",
                    "source_alias": "LEGACY-PY-ANGLE-ALL",
                    "source_file": "3._parameter_angle_all_0727.py",
                    "descriptor": descriptor,
                    "population": "GLOBAL_WEIGHTED",
                    "statistic": statistic,
                    "value": float(summary[raw_descriptor][index]),
                    "unit": "dimensionless" if descriptor == "mass_orientation" else ("degree" if descriptor == "angle" else ("mm" if descriptor == "thickness" else "legacy_formula_unit")),
                    "candidate_status": "sensitivity_rescue_not_canonical",
                }
            )
    if len(rows) != 40:
        raise RuntimeError(f"{model_id}/{config_id}: expected 40 mapped values, received {len(rows)}")
    return rows


def prepare_baseline() -> None:
    validate_environment_and_contract()
    destination = WORK / "P1000_S801"
    destination.mkdir(parents=True, exist_ok=True)
    source = json.loads(BASELINE_JSON.read_text(encoding="utf-8"))
    all_rows: list[dict[str, Any]] = []
    audit_rows: list[dict[str, Any]] = []
    audit_root = destination / "audit_images"
    audit_root.mkdir(parents=True, exist_ok=True)
    for model_id in ("T8", "T9"):
        payload = {
            "LEGACY-PY-RESULT": source[model_id]["LEGACY-PY-RESULT"],
            "LEGACY-PY-ANGLE-ALL": source[model_id]["LEGACY-PY-ANGLE-ALL"],
        }
        all_rows.extend(descriptor_rows(model_id, "P1000_S801", payload))
        png_dir = BASELINE_PNG / model_id / "z_1000x801_endpoint"
        for pair_index in (1, 400, 800):
            src = png_dir / f"combine_image_{pair_index:04d}.png"
            dst = audit_root / f"{model_id}_combine_{pair_index:04d}.png"
            if not dst.is_file() or sha256_file(dst) != sha256_file(src):
                shutil.copy2(src, dst)
            audit_rows.append({"model_id": model_id, "config_id": "P1000_S801", "artifact_role": "combine_audit", "source_path": rel(src), "retained_path": rel(dst), "sha256": sha256_file(dst)})
    values_path = destination / "candidate_values.csv"
    write_csv(values_path, all_rows)
    write_csv(destination / "audit_image_manifest.csv", audit_rows)
    write_json(
        destination / "complete.json",
        {
            "run_id": RUN_ID,
            "config_id": "P1000_S801",
            "status": "passed_reused_frozen_baseline",
            "source": rel(BASELINE_JSON),
            "source_sha256": sha256_file(BASELINE_JSON),
            "candidate_rows": len(all_rows),
            "candidate_values_sha256": sha256_file(values_path),
            "completed_at_kst": now_kst(),
        },
    )
    print(json.dumps({"status": "baseline_prepared", "rows": len(all_rows), "path": rel(values_path)}), flush=True)


def run_one(model_id: str, config_id: str) -> None:
    validate_environment_and_contract()
    if model_id not in MODEL_PATHS or config_id not in NEW_CONFIGS:
        raise ValueError(f"unsupported model/config: {model_id}/{config_id}")
    cfg = CONFIGS[config_id]
    output = RUN_WORK / config_id / model_id
    complete_path = output / "complete.json"
    if complete_path.is_file():
        complete = json.loads(complete_path.read_text(encoding="utf-8"))
        values_path = output / "candidate_values.csv"
        if (
            complete.get("status") == "passed"
            and complete.get("geometry_sha256") == MODEL_HASHES[model_id]
            and complete.get("config_sha256") == config_hash(config_id)
            and values_path.is_file()
            and complete.get("candidate_values_sha256") == sha256_file(values_path)
        ):
            print(json.dumps({"status": "already_complete", "model_id": model_id, "config_id": config_id}), flush=True)
            return
    if output.exists():
        quarantine = RUN_WORK / "quarantine" / f"{config_id}_{model_id}_{datetime.now().strftime('%Y%m%dT%H%M%S')}"
        quarantine.parent.mkdir(parents=True, exist_ok=True)
        output.rename(quarantine)
    mask_dir = output / "runtime_images" / "mask"
    combine_dir = output / "runtime_images" / "combine"
    table_dir = output / "tables"
    audit_dir = output / "audit_images"
    for path in (mask_dir, combine_dir, table_dir, audit_dir):
        path.mkdir(parents=True, exist_ok=True)

    start = time.perf_counter()
    probe = load_module(PROBE_PATH, f"t4r_slice_probe_{model_id}_{config_id}")
    mesh, fit_meta = probe.load_and_fit_mesh(MODEL_PATHS[model_id], 40.0, "fit_max_extent_to_cube")
    profile = probe.SliceProfile(
        name=f"{RUN_ID}_{config_id}",
        cube_width_mm=40.0,
        layer_height_mm=float(cfg["slice_spacing_mm"]),
        slice_count=int(cfg["slice_count"]),
        pixel_count=int(cfg["pixel_resolution"]),
        description="bounded T8/T9 detailed LEGACY-PY convergence rescue",
        slice_mode="endpoint",
    )
    positions = probe.slice_positions(profile)
    normal = probe.normalized_normal("z")
    area_per_pixel = 40.0**2 / int(cfg["pixel_resolution"]) ** 2
    length_per_pixel = 40.0 / int(cfg["pixel_resolution"])
    slice_rows: list[dict[str, Any]] = []
    overlay_rows: list[dict[str, Any]] = []
    component_rows: list[dict[str, Any]] = []
    previous: np.ndarray | None = None
    readback_mismatch_sum = 0

    for slice_index, position in enumerate(positions):
        mask = np.asarray(probe.rasterize_section(mesh, normal, float(position), 40.0, int(cfg["pixel_resolution"])), dtype=np.uint8)
        mask_path = mask_dir / f"m{slice_index:04d}.png"
        if not cv2.imwrite(str(mask_path), mask * 255, [cv2.IMWRITE_PNG_COMPRESSION, 1]):
            raise RuntimeError(f"failed to write {mask_path}")
        readback = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
        if readback is None:
            raise RuntimeError(f"failed to read {mask_path}")
        readback_bool = readback > 0
        readback_mismatch_sum += int(np.count_nonzero(readback_bool != (mask > 0)))
        component_count, _labels, stats, _centroids = cv2.connectedComponentsWithStats(readback_bool.astype(np.uint8), connectivity=8)
        kept_count = int(sum(int(stats[label, cv2.CC_STAT_AREA]) >= 2 for label in range(1, component_count)))
        slice_rows.append(
            {
                "model_id": model_id,
                "config_id": config_id,
                "slice_index": slice_index,
                "z_mm": float(position),
                "material_pixel_count": int(readback_bool.sum()),
                "material_area_mm2": float(readback_bool.sum() * area_per_pixel),
                "component_count_raw": int(component_count - 1),
                "component_count_min2": kept_count,
                "mask_sha256": sha256_file(mask_path),
            }
        )
        if previous is not None:
            pair_index = slice_index
            combine_path = combine_dir / f"combine_image_{pair_index:04d}.png"
            expected = exact_combine(previous, readback_bool)
            if not cv2.imwrite(str(combine_path), expected, [cv2.IMWRITE_PNG_COMPRESSION, 1]):
                raise RuntimeError(f"failed to write {combine_path}")
            observed = cv2.imread(str(combine_path))
            if observed is None:
                raise RuntimeError(f"failed to read {combine_path}")
            readback_mismatch_sum += int(np.count_nonzero(observed != expected))
            gray = cv2.cvtColor(observed, cv2.COLOR_BGR2GRAY)
            gray_values = sorted(int(x) for x in np.unique(gray))
            if not set(gray_values).issubset({0, 29, 76, 105}):
                raise RuntimeError(f"gray contract failed: {combine_path} {gray_values}")
            red = gray == 76
            blue = gray == 29
            purple = gray == 105
            union = red | blue | purple
            count, labels, stats, _centroids = cv2.connectedComponentsWithStats(union.astype(np.uint8), connectivity=8)
            overlay_rows.append(
                {
                    "model_id": model_id,
                    "config_id": config_id,
                    "pair_index": pair_index,
                    "red_pixel_count": int(red.sum()),
                    "blue_pixel_count": int(blue.sum()),
                    "purple_pixel_count": int(purple.sum()),
                    "union_pixel_count": int(union.sum()),
                    "component_count_raw": int(count - 1),
                    "component_count_min2": int(sum(int(stats[label, cv2.CC_STAT_AREA]) >= 2 for label in range(1, count))),
                    "gray_values": ";".join(map(str, gray_values)),
                    "combine_sha256": sha256_file(combine_path),
                }
            )
            for label in range(1, count):
                pixels = int(stats[label, cv2.CC_STAT_AREA])
                component_rows.append(
                    {
                        "model_id": model_id,
                        "config_id": config_id,
                        "pair_index": pair_index,
                        "component_index": label,
                        "pixel_count": pixels,
                        "area_mm2": pixels * area_per_pixel,
                        "kept_by_min2": pixels >= 2,
                    }
                )
        previous = readback_bool
        if slice_index % 100 == 0 or slice_index == len(positions) - 1:
            print(f"[{model_id}/{config_id}] {slice_index + 1}/{len(positions)} slices", flush=True)

    write_csv(table_dir / "slice_pixel_readback.csv", slice_rows)
    write_csv(table_dir / "overlay_pixel_readback.csv", overlay_rows)
    write_csv(table_dir / "overlay_component_population.csv", component_rows)
    result = run_slice_result(
        ROOT,
        combine_dir,
        mask_dir,
        area_per_pixel_mm2=area_per_pixel,
        layer_height_mm=float(cfg["slice_spacing_mm"]),
        length_per_pixel_mm=length_per_pixel,
    )
    angle = run_angle_all(
        ROOT,
        combine_dir,
        width_mm=40.0,
        layer_height_mm=float(cfg["slice_spacing_mm"]),
        volume_fraction=0.30,
        total_pixel=int(cfg["pixel_resolution"]),
    )
    payload = {"LEGACY-PY-RESULT": result, "LEGACY-PY-ANGLE-ALL": angle}
    write_json(output / "legacy_direct_payload.json", payload)
    candidate_path = output / "candidate_values.csv"
    mapped = descriptor_rows(model_id, config_id, payload)
    write_csv(candidate_path, mapped)

    audit_rows: list[dict[str, Any]] = []
    audit_indices = {0, int(cfg["slice_count"]) // 2, int(cfg["slice_count"]) - 1}
    for slice_index in sorted(audit_indices):
        source = mask_dir / f"m{slice_index:04d}.png"
        target = audit_dir / f"mask_{slice_index:04d}.png"
        shutil.copy2(source, target)
        audit_rows.append({"model_id": model_id, "config_id": config_id, "artifact_role": "mask_audit", "artifact_index": slice_index, "path": rel(target), "sha256": sha256_file(target)})
    pair_indices = {1, int(cfg["slice_count"]) // 2, int(cfg["slice_count"]) - 1}
    for pair_index in sorted(pair_indices):
        source = combine_dir / f"combine_image_{pair_index:04d}.png"
        target = audit_dir / f"combine_{pair_index:04d}.png"
        shutil.copy2(source, target)
        audit_rows.append({"model_id": model_id, "config_id": config_id, "artifact_role": "combine_audit", "artifact_index": pair_index, "path": rel(target), "sha256": sha256_file(target)})
    write_csv(output / "audit_image_manifest.csv", audit_rows)

    deletion_rows: list[dict[str, Any]] = []
    for image_path in sorted((output / "runtime_images").rglob("*.png")):
        record = {"model_id": model_id, "config_id": config_id, "transient_path": rel(image_path), "sha256_before_delete": sha256_file(image_path), "deleted": False}
        image_path.unlink()
        record["deleted"] = not image_path.exists()
        deletion_rows.append(record)
    write_csv(output / "transient_png_deletion_ledger.csv", deletion_rows)
    remaining = list((output / "runtime_images").rglob("*.png"))
    elapsed = time.perf_counter() - start
    complete = {
        "run_id": RUN_ID,
        "model_id": model_id,
        "config_id": config_id,
        "status": "passed" if readback_mismatch_sum == 0 and not remaining and len(mapped) == 40 else "failed",
        "runtime_environment": "KMK312",
        "python_executable": sys.executable,
        "python_version": platform.python_version(),
        "geometry_path": rel(MODEL_PATHS[model_id]),
        "geometry_sha256": MODEL_HASHES[model_id],
        "config_sha256": config_hash(config_id),
        "slice_rows": len(slice_rows),
        "overlay_rows": len(overlay_rows),
        "component_rows": len(component_rows),
        "candidate_rows": len(mapped),
        "readback_mismatch_sum": readback_mismatch_sum,
        "transient_png_deleted": sum(bool(row["deleted"]) for row in deletion_rows),
        "transient_png_remaining": len(remaining),
        "audit_png_retained": len(audit_rows),
        "candidate_values_sha256": sha256_file(candidate_path),
        "runtime_seconds": elapsed,
        "completed_at_kst": now_kst(),
        "fit_metadata": fit_meta,
    }
    write_json(complete_path, complete)
    if complete["status"] != "passed":
        raise RuntimeError(f"{model_id}/{config_id}: execution gate failed: {complete}")
    print(json.dumps(complete, ensure_ascii=False), flush=True)


def symmetric_relative_difference(a: float, b: float) -> float:
    denominator = abs(a) + abs(b)
    if denominator <= 1e-12:
        return 0.0
    return 2.0 * abs(a - b) / (denominator + 1e-12)


def contact_sheet() -> Path:
    rows: list[list[tuple[str, Path]]] = []
    for config_id in CONFIGS:
        row: list[tuple[str, Path]] = []
        if config_id == "P1000_S801":
            for model_id in ("T8", "T9"):
                row.append((f"{model_id} {config_id}", BASELINE_PNG / model_id / "z_1000x801_endpoint" / "combine_image_0400.png"))
        else:
            pair_index = int(CONFIGS[config_id]["slice_count"]) // 2
            for model_id in ("T8", "T9"):
                row.append((f"{model_id} {config_id}", RUN_WORK / config_id / model_id / "audit_images" / f"combine_{pair_index:04d}.png"))
        rows.append(row)
    thumb = 420
    label_h = 42
    canvas = Image.new("RGB", (2 * thumb, len(rows) * (thumb + label_h)), "white")
    draw = ImageDraw.Draw(canvas)
    for r_index, row in enumerate(rows):
        for c_index, (label, path) in enumerate(row):
            with Image.open(path) as image:
                image = image.convert("RGB")
                image.thumbnail((thumb, thumb))
                x = c_index * thumb + (thumb - image.width) // 2
                y = r_index * (thumb + label_h) + label_h
                canvas.paste(image, (x, y))
            draw.text((c_index * thumb + 8, r_index * (thumb + label_h) + 10), label, fill="black")
    target = FIGURES / f"{RUN_ID}_midplane_contact_sheet.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(target)
    return target


def aggregate() -> None:
    validate_environment_and_contract()
    required = [WORK / "P1000_S801" / "complete.json"] + [RUN_WORK / config_id / model_id / "complete.json" for config_id in NEW_CONFIGS for model_id in ("T8", "T9")]
    for path in required:
        if not path.is_file():
            raise FileNotFoundError(f"required run is incomplete: {path}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not str(payload.get("status", "")).startswith("passed"):
            raise RuntimeError(f"required run failed: {path}")
    all_values = [pd.read_csv(WORK / "P1000_S801" / "candidate_values.csv")]
    for config_id in NEW_CONFIGS:
        for model_id in ("T8", "T9"):
            all_values.append(pd.read_csv(RUN_WORK / config_id / model_id / "candidate_values.csv"))
    values = pd.concat(all_values, ignore_index=True)
    if len(values) != 320 or values.groupby(["config_id", "model_id"]).size().ne(40).any():
        raise RuntimeError("candidate census failed; expected 4 configs x 2 models x 40 values")
    pair_rows: list[dict[str, Any]] = []
    for (config_id, candidate_id), group in values.groupby(["config_id", "candidate_id"], sort=False):
        lookup = dict(zip(group["model_id"], group["value"], strict=True))
        a, b = float(lookup["T8"]), float(lookup["T9"])
        first = group.iloc[0]
        pair_rows.append(
            {
                "config_id": config_id,
                "candidate_id": candidate_id,
                "source_alias": first["source_alias"],
                "descriptor": first["descriptor"],
                "population": first["population"],
                "statistic": first["statistic"],
                "T8_value": a,
                "T9_value": b,
                "T8_minus_T9": a - b,
                "sign": int(np.sign(a - b)),
                "symmetric_relative_difference": symmetric_relative_difference(a, b),
            }
        )
    pair = pd.DataFrame(pair_rows)
    classifications: list[dict[str, Any]] = []
    for candidate_id, group in pair.groupby("candidate_id", sort=False):
        indexed = group.set_index("config_id")
        diffs = indexed.loc[list(CONFIGS), "symmetric_relative_difference"].astype(float)
        signs = indexed.loc[list(CONFIGS), "sign"].astype(int)
        positive_diffs = diffs[diffs > 1e-12]
        ratio = float(positive_diffs.max() / positive_diffs.min()) if len(positive_diffs) == 4 else math.inf
        sign_stable = bool((signs != 0).all() and signs.nunique() == 1)
        all_one = bool((diffs >= 0.01).all())
        robust = bool(all_one and sign_stable and ratio <= 2.0)
        strong = bool(robust and int((diffs >= 0.02).sum()) >= 3)
        baseline = float(diffs.loc["P1000_S801"])
        if strong:
            classification = "strongly_distinguishing"
            status = "likely"
        elif robust:
            classification = "robustly_distinguishing"
            status = "likely"
        elif baseline >= 0.01:
            classification = "resolution_sensitive"
            status = "unresolved"
        else:
            classification = "weak_or_no_rescue"
            status = "rejected"
        first = group.iloc[0]
        classifications.append(
            {
                "candidate_id": candidate_id,
                "source_alias": first["source_alias"],
                "descriptor": first["descriptor"],
                "population": first["population"],
                "statistic": first["statistic"],
                "baseline_symmetric_relative_difference": baseline,
                "min_symmetric_relative_difference": float(diffs.min()),
                "max_symmetric_relative_difference": float(diffs.max()),
                "relative_difference_max_min_ratio": ratio,
                "sign_stable": sign_stable,
                "configs_ge_1pct": int((diffs >= 0.01).sum()),
                "configs_ge_2pct": int((diffs >= 0.02).sum()),
                "classification": classification,
                "decision_status": status,
                "promotion_allowed": False,
            }
        )
    classification = pd.DataFrame(classifications).sort_values(["classification", "min_symmetric_relative_difference"], ascending=[True, False])

    FROZEN.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    value_path = FROZEN / f"{RUN_ID}_candidate_values.csv"
    pair_path = FROZEN / f"{RUN_ID}_pair_comparison.csv"
    class_path = FROZEN / f"{RUN_ID}_candidate_classification.csv"
    config_path = FROZEN / f"{RUN_ID}_configuration_registry.csv"
    values.to_csv(value_path, index=False, encoding="utf-8-sig")
    pair.to_csv(pair_path, index=False, encoding="utf-8-sig")
    classification.to_csv(class_path, index=False, encoding="utf-8-sig")
    pd.DataFrame([{"config_id": key, **value, "config_sha256": config_hash(key)} for key, value in CONFIGS.items()]).to_csv(config_path, index=False, encoding="utf-8-sig")

    pivot = pair.pivot(index="candidate_id", columns="config_id", values="symmetric_relative_difference").loc[:, list(CONFIGS)]
    ordered = classification.sort_values("max_symmetric_relative_difference", ascending=False)["candidate_id"].tolist()
    pivot = pivot.loc[ordered]
    fig, ax = plt.subplots(figsize=(10, 14))
    image = ax.imshow(pivot.to_numpy() * 100.0, aspect="auto", cmap="viridis")
    ax.set_xticks(range(len(pivot.columns)), pivot.columns, rotation=25, ha="right")
    ax.set_yticks(range(len(pivot.index)), pivot.index, fontsize=6)
    ax.set_title("T8/T9 detailed descriptor separation across resolution configs (%)")
    fig.colorbar(image, ax=ax, label="symmetric relative difference (%)")
    fig.tight_layout()
    heatmap_path = FIGURES / f"{RUN_ID}_candidate_separation_heatmap.png"
    fig.savefig(heatmap_path, dpi=180)
    plt.close(fig)

    top_ids = classification.sort_values("min_symmetric_relative_difference", ascending=False).head(12)["candidate_id"].tolist()
    fig, ax = plt.subplots(figsize=(12, 7))
    for candidate_id in top_ids:
        series = pair[pair["candidate_id"].eq(candidate_id)].set_index("config_id").loc[list(CONFIGS)]
        ax.plot(list(CONFIGS), series["symmetric_relative_difference"] * 100.0, marker="o", label=candidate_id)
    ax.axhline(1.0, color="black", linestyle="--", linewidth=1, label="1% gate")
    ax.set_ylabel("symmetric relative difference (%)")
    ax.set_title("Top T8/T9 rescue candidates: resolution convergence")
    ax.tick_params(axis="x", rotation=20)
    ax.legend(fontsize=7, bbox_to_anchor=(1.02, 1), loc="upper left")
    fig.tight_layout()
    convergence_path = FIGURES / f"{RUN_ID}_top_candidate_convergence.png"
    fig.savefig(convergence_path, dpi=180)
    plt.close(fig)
    contact_path = contact_sheet()

    qa_rows: list[dict[str, Any]] = []
    for config_id in NEW_CONFIGS:
        for model_id in ("T8", "T9"):
            complete = json.loads((RUN_WORK / config_id / model_id / "complete.json").read_text(encoding="utf-8"))
            qa_rows.append(
                {
                    "config_id": config_id,
                    "model_id": model_id,
                    "status": complete["status"],
                    "slice_rows": complete["slice_rows"],
                    "overlay_rows": complete["overlay_rows"],
                    "candidate_rows": complete["candidate_rows"],
                    "readback_mismatch_sum": complete["readback_mismatch_sum"],
                    "transient_png_deleted": complete["transient_png_deleted"],
                    "transient_png_remaining": complete["transient_png_remaining"],
                    "audit_png_retained": complete["audit_png_retained"],
                    "runtime_seconds": complete["runtime_seconds"],
                    "qa_pass": complete["status"] == "passed" and complete["readback_mismatch_sum"] == 0 and complete["transient_png_remaining"] == 0,
                }
            )
    qa_path = REPORTS / f"{RUN_ID}_QA.csv"
    write_csv(qa_path, qa_rows)
    counts = classification["classification"].value_counts().to_dict()
    summary = {
        "run_id": RUN_ID,
        "status": "passed" if all(row["qa_pass"] for row in qa_rows) else "failed",
        "runtime_environment": "KMK312",
        "models": ["T8", "T9"],
        "configuration_count": 4,
        "new_configuration_model_runs": 6,
        "candidate_count": 40,
        "candidate_value_rows": len(values),
        "pair_comparison_rows": len(pair),
        "classification_counts": counts,
        "strong_or_robust_candidates": classification[classification["classification"].isin(["strongly_distinguishing", "robustly_distinguishing"])]["candidate_id"].tolist(),
        "scientific_boundary": "Detailed LEGACY-PY sensitivity candidates only; no formula canon, feature promotion, predictive fit, roster mutation, or inverse-design claim.",
        "completed_at_kst": now_kst(),
    }
    summary_path = REPORTS / f"{RUN_ID}_execution_summary.json"
    write_json(summary_path, summary)
    manifest_targets = [
        CONTRACT,
        Path(__file__),
        value_path,
        pair_path,
        class_path,
        config_path,
        qa_path,
        summary_path,
        heatmap_path,
        convergence_path,
        contact_path,
    ]
    protected_report = REPORTS / f"{RUN_ID}_protected_asset_verification.csv"
    if protected_report.is_file():
        manifest_targets.append(protected_report)
    manifest_path = REPORTS / f"{RUN_ID}_output_manifest.csv"
    write_csv(manifest_path, [{"path": rel(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)} for path in manifest_targets])
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)


def verify_protected_against_immediate_prior() -> None:
    """Compare against T4R-001's post-task hashes, including Ledger v0.2."""
    validate_environment_and_contract()
    guard = load_module(SCRIPT_DIR / "CINT_01_protected_asset_guard.py", "t4r_slice_protected_guard")
    previous = pd.read_csv(PRIOR_PROTECTED, dtype=str, keep_default_na=False)
    current_rows = guard.collect_protected_assets()
    current = {
        (row["guard_kind"], row["path"], row["source_alias"]): row
        for row in current_rows
    }
    rows: list[dict[str, Any]] = []
    previous_keys: set[tuple[str, str, str]] = set()
    for item in previous.itertuples(index=False):
        key = (item.guard_kind, item.path, item.source_alias)
        previous_keys.add(key)
        actual = current.get(key)
        expected_hash = item.after_sha256
        expected_size = item.after_size_bytes
        status = "missing" if actual is None else (
            "unchanged"
            if actual["sha256"] == expected_hash and actual["size_bytes"] == expected_size
            else "changed"
        )
        rows.append(
            {
                "guard_kind": key[0],
                "path": key[1],
                "source_alias": key[2],
                "expected_sha256_from_T4R001_after": expected_hash,
                "actual_sha256": actual["sha256"] if actual else "",
                "expected_size_bytes": expected_size,
                "actual_size_bytes": actual["size_bytes"] if actual else "",
                "verification_status": status,
            }
        )
    for key, actual in current.items():
        if key not in previous_keys:
            rows.append(
                {
                    "guard_kind": key[0],
                    "path": key[1],
                    "source_alias": key[2],
                    "expected_sha256_from_T4R001_after": "",
                    "actual_sha256": actual["sha256"],
                    "expected_size_bytes": "",
                    "actual_size_bytes": actual["size_bytes"],
                    "verification_status": "unexpected_added",
                }
            )
    target = REPORTS / f"{RUN_ID}_protected_asset_verification.csv"
    write_csv(target, rows)
    failed = [row for row in rows if row["verification_status"] != "unchanged"]
    print(json.dumps({"verified": len(rows), "failed": len(failed), "report": rel(target), "failure_preview": failed[:3]}, ensure_ascii=False), flush=True)
    if failed:
        raise SystemExit(2)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["baseline", "run-one", "aggregate", "verify-protected"])
    parser.add_argument("--model", choices=sorted(MODEL_PATHS))
    parser.add_argument("--config", choices=NEW_CONFIGS)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "baseline":
        prepare_baseline()
    elif args.command == "run-one":
        if not args.model or not args.config:
            raise SystemExit("run-one requires --model and --config")
        run_one(args.model, args.config)
    elif args.command == "aggregate":
        aggregate()
    else:
        verify_protected_against_immediate_prior()


if __name__ == "__main__":
    main()
