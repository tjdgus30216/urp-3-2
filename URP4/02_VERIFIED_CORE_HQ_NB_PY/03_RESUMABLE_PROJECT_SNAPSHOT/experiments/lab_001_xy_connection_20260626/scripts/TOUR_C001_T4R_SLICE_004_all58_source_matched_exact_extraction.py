"""Resumable all-58 canonical-N40 exact slice extraction.

This R09-SCRIPT extends the source-matched SLICE-003A gate without rerunning
its five completed models.  T8/T9 are promoted from the immutable CINT-02
canonical-N40 P1000_S801 overlay fixtures by readback, not by rerasterizing
their geometry.  Every other model is an independent resume unit executed by
the already validated SLICE-001 image -> pixel -> component -> LEGACY-PY path.

The execution stage is strictly x-only.  It reads no performance y, fits no
predictive model, promotes no feature, and changes no protected source.
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
import subprocess
import sys
import time
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

import cv2
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
FACTORY = LAB / "factories" / "TOUR-C001"
RUN_ID = "TOUR-C001-T4R-SLICE-004"
TASK_NAME = "TOUR-C001-T4R-SLICE-004_ALL58_SOURCE_MATCHED_EXACT_EXTRACTION"
CONFIG_ID = "P1000_S801"
CONFIG = {
    "pixel_resolution": 1000,
    "slice_count": 801,
    "slice_spacing_mm": 0.05,
    # Kept byte-identical to SLICE-003A so its five config hashes are reusable.
    "role": "canonical_N40_source_matched_rebuild",
}
KST = timezone(timedelta(hours=9))

CONTRACT = FACTORY / "contracts" / "TOUR-C001_T4R_SLICE_004_ALL58_SOURCE_MATCHED_EXACT_EXTRACTION_20260720.json"
REGISTRY = LAB / "reports" / "tables" / "R09-20260715_final_canonical_geometry_registry.csv"
LEGACY_REGISTRY = LAB / "reports" / "tables" / "CINT-02_legacy_source_adapter_registry_20260718.csv"
CINT02_PANEL_MANIFEST = LAB / "reports" / "tables" / "CINT-02_golden_panel_input_manifest_20260718.csv"
CINT02_PAYLOAD = LAB / "factories" / "CINT-02" / "outputs" / "CINT-02_panel_replay_actual.json"
CINT02_PNG_ROOT = LAB / "factories" / "CINT-02" / "runtime" / "panel_png"
SLICE001_SCRIPT = LAB / "scripts" / "TOUR_C001_T4R_SLICE_001_t8_t9_legacy_detail_convergence.py"
SLICE003A_SCRIPT = LAB / "scripts" / "TOUR_C001_T4R_SLICE_003A_matched_source_five_model_audit.py"
SLICE003A_CONTRACT = FACTORY / "contracts" / "TOUR-C001_T4R_SLICE_003A_MATCHED_SOURCE_FIVE_MODEL_PREREGISTRATION_20260720.json"
SLICE003A_REPORT = LAB / "results" / "R09-20260720-TOUR-C001_T4R_SLICE_003A_MATCHED_SOURCE_FIVE_MODEL_CONTROL_TOWER_REVIEW_20260720.md"
SLICE003A_WORK = ROOT / ".tmp" / "t4rs3a" / CONFIG_ID
SLICE001_BASELINE = FACTORY / "analysis_factory" / "intermediate" / "TOUR-C001-T4R-SLICE-001" / CONFIG_ID

RUN_WORK = ROOT / ".tmp" / "t4rs4"
MODEL_WORK = RUN_WORK / CONFIG_ID
CLAIMS = RUN_WORK / "claims"
ATTEMPTS = RUN_WORK / "attempts"
FAILURES = RUN_WORK / "failures"
LOGS = RUN_WORK / "logs"
REPORTS = FACTORY / "analysis_factory" / "reports"
FROZEN = FACTORY / "analysis_factory" / "frozen"

REUSE_003A = ["B3", "C1", "L1", "F1", "F2"]
REUSE_CINT02 = ["T8", "T9"]
SIGNALS = [
    {"signal_id": "SIG-A", "candidate_id": "LPA::angle::GLOBAL_WEIGHTED::stdev", "raw_candidate_ids": ["LPA::angle::GLOBAL_WEIGHTED::stdev"]},
    {"signal_id": "SIG-B", "candidate_id": "LPR::angle::IP::stdev", "raw_candidate_ids": ["LPR::angle::IP::stdev"]},
    {"signal_id": "SIG-C", "candidate_id": "LPR::angle::LAYER_MEAN::stdev", "raw_candidate_ids": ["LPR::angle::LIP::stdev", "LPR::angle::LTP::stdev"]},
    {"signal_id": "SIG-D", "candidate_id": "LPR::curvature::LTP::stdev", "raw_candidate_ids": ["LPR::curvature::LTP::stdev"]},
]
SHARDS = {
    "SHARD-01-B": [f"B{i}" for i in range(1, 6)],
    "SHARD-02-C01-C07": [f"C{i}" for i in range(1, 8)],
    "SHARD-03-C08-C14": [f"C{i}" for i in range(8, 15)],
    "SHARD-04-L01-L07": [f"L{i}" for i in range(1, 8)],
    "SHARD-05-L08-L14": [f"L{i}" for i in range(8, 15)],
    "SHARD-06-L15-L20": [f"L{i}" for i in range(15, 21)],
    "SHARD-07-F-T01-T04": ["F1", "F2"] + [f"T{i}" for i in range(1, 5)],
    "SHARD-08-T05-T11": [f"T{i}" for i in range(5, 12)],
    "SHARD-09-T12-T17": [f"T{i}" for i in range(12, 18)],
}


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


def require_kmk312() -> None:
    required = (ROOT / "tools" / "envs" / "KMK312" / "python.exe").resolve()
    if Path(sys.executable).resolve() != required:
        raise RuntimeError(f"KMK312 required: expected={required} actual={sys.executable}")
    if sys.version_info[:2] != (3, 12):
        raise RuntimeError(f"Python 3.12 required, received {platform.python_version()}")


def registry_frame() -> pd.DataFrame:
    frame = pd.read_csv(REGISTRY, dtype=str, keep_default_na=False)
    expected = [f"B{i}" for i in range(1, 6)] + [f"C{i}" for i in range(1, 15)] + [f"L{i}" for i in range(1, 21)] + ["F1", "F2"] + [f"T{i}" for i in range(1, 18)]
    if len(frame) != 58 or sorted(frame["model_id"]) != sorted(expected):
        raise RuntimeError("canonical registry is not the exact expected 58-model population")
    if not (frame["final_geometry_gate"] == "pass").all():
        raise RuntimeError("canonical registry contains a non-pass geometry")
    return frame.set_index("model_id", drop=False).loc[expected].reset_index(drop=True)


def model_maps(model_ids: Iterable[str] | None = None) -> tuple[dict[str, Path], dict[str, str]]:
    frame = registry_frame()
    if model_ids is not None:
        wanted = set(model_ids)
        frame = frame[frame["model_id"].isin(wanted)]
    paths = {row.model_id: ROOT / row.processed_file for row in frame.itertuples(index=False)}
    hashes = {row.model_id: row.processed_sha256 for row in frame.itertuples(index=False)}
    return paths, hashes


def configure_base(model_ids: Iterable[str]):
    base = load_module(SLICE001_SCRIPT, f"tour_slice001_for_004_{os.getpid()}_{time.time_ns()}")
    paths, hashes = model_maps(model_ids)
    base.CONTRACT = CONTRACT
    base.RUN_ID = RUN_ID
    base.RUN_WORK = RUN_WORK
    base.MODEL_PATHS = paths
    base.MODEL_HASHES = hashes
    base.CONFIGS = {CONFIG_ID: CONFIG}
    base.NEW_CONFIGS = [CONFIG_ID]
    return base


def aggregate_directory_hash(path: Path, pattern: str) -> tuple[int, str, str, str]:
    files = sorted(path.glob(pattern))
    digest = hashlib.sha256()
    first = ""
    last = ""
    for index, item in enumerate(files):
        item_hash = sha256_file(item)
        if index == 0:
            first = item_hash
        last = item_hash
        digest.update(item.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(item_hash.encode("ascii"))
        digest.update(b"\n")
    return len(files), digest.hexdigest(), first, last


def parent_evidence() -> list[dict[str, str]]:
    paths = [
        REGISTRY,
        LEGACY_REGISTRY,
        CINT02_PANEL_MANIFEST,
        CINT02_PAYLOAD,
        SLICE001_SCRIPT,
        SLICE003A_SCRIPT,
        SLICE003A_CONTRACT,
        SLICE003A_REPORT,
    ]
    return [{"path": rel(path), "sha256": sha256_file(path)} for path in paths]


def freeze_contract() -> None:
    require_kmk312()
    if CONTRACT.exists():
        raise RuntimeError(f"contract already exists; refusing overwrite: {CONTRACT}")
    frame = registry_frame()
    fixed_geometry: list[dict[str, Any]] = []
    for row in frame.itertuples(index=False):
        path = ROOT / row.processed_file
        actual = sha256_file(path)
        if actual != row.processed_sha256:
            raise RuntimeError(f"geometry hash mismatch: {row.model_id}")
        fixed_geometry.append(
            {
                "model_id": row.model_id,
                "family": row.model_family,
                "path": row.processed_file,
                "sha256": actual,
                "physical_size_mm": [40.0, 40.0, 40.0],
                "geometry_gate": row.final_geometry_gate,
            }
        )
    legacy = pd.read_csv(LEGACY_REGISTRY, dtype=str, keep_default_na=False)
    legacy = legacy[legacy["legacy_alias"].isin(["LEGACY-PY-RESULT", "LEGACY-PY-ANGLE-ALL"])]
    payload = {
        "contract_id": TASK_NAME,
        "run_id": RUN_ID,
        "created_at_kst": now_kst(),
        "status": "frozen_before_all58_execution",
        "parent_evidence": parent_evidence(),
        "runtime": {"environment": "KMK312", "python_version": "3.12.12", "max_workers_legion5": 2},
        "fixed_configuration": {
            "config_id": CONFIG_ID,
            "physical_size_mm": [40.0, 40.0, 40.0],
            "slice_axis": "z",
            "pixel_resolution": [1000, 1000],
            "slice_count": 801,
            "slice_spacing_mm": 0.05,
            "slice_mode": "endpoint",
            "threshold_rule": "BGR exact red/blue/purple; gray 76/29/105",
            "connected_component_rule": "8-connectivity; direct LEGACY-PY authority behavior; min2 retained as trace only",
            "base_config_payload": CONFIG,
        },
        "legacy_authorities": legacy.to_dict(orient="records"),
        "fixed_geometry": fixed_geometry,
        "fixed_shards": [{"shard_id": key, "model_ids": value} for key, value in SHARDS.items()],
        "reuse_policy": {
            "SLICE003A": {"models": REUSE_003A, "required": ["geometry_path", "geometry_sha256", "config_sha256", "candidate_values_sha256", "all_supporting_tables"]},
            "CINT02": {"models": REUSE_CINT02, "required": ["geometry_path", "geometry_sha256", "explicit_config_fields", "combine_aggregate_sha256", "direct_payload", "candidate_reconstruction_match"]},
            "mismatch_action": "quarantine_only_that_model_then_recompute",
        },
        "output_contract_per_model": [
            "complete.json", "geometry path/hash", "config hash", "801 slice rows", "800 overlay rows",
            "component population table", "direct LEGACY-PY payload", "40 mapped candidates", "four rescue signals",
            "six audit PNGs", "transient deletion ledger", "candidate output hash",
        ],
        "fixed_rescue_signals": SIGNALS,
        "scientific_boundaries": {
            "performance_y_access": 0,
            "predictive_fits": 0,
            "feature_promotions": 0,
            "formula_canon_claims": 0,
            "active_roster_changes": 0,
            "T5_entry": 0,
            "inverse_design_claims": 0,
        },
        "protected_assets": ["source Excel", "LEGACY-PY", "NB-ORIG", "NB-CURRENT", "Training/generator originals", "Master Ledger v0.2", "Tournament HQ"],
    }
    write_json(CONTRACT, payload)
    print(json.dumps({"status": "contract_frozen", "path": rel(CONTRACT), "sha256": sha256_file(CONTRACT), "models": 58}, ensure_ascii=False))


def validate_contract() -> dict[str, Any]:
    require_kmk312()
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    failures: list[str] = []
    execution = contract["execution_code"]
    execution_path = ROOT / execution["path"]
    execution_actual = sha256_file(execution_path) if execution_path.is_file() else "missing"
    if execution_actual != execution["sha256"]:
        failures.append(f"execution_code:{execution['path']}")
    for item in contract["parent_evidence"]:
        path = ROOT / item["path"]
        actual = sha256_file(path) if path.is_file() else "missing"
        if actual != item["sha256"]:
            failures.append(f"parent:{item['path']}")
    for item in contract["fixed_geometry"]:
        path = ROOT / item["path"]
        actual = sha256_file(path) if path.is_file() else "missing"
        if actual != item["sha256"]:
            failures.append(f"geometry:{item['model_id']}")
    if failures:
        raise RuntimeError("contract validation failed: " + ", ".join(failures))
    return contract


def valid_complete(model_id: str) -> tuple[bool, str]:
    path = MODEL_WORK / model_id / "complete.json"
    values = MODEL_WORK / model_id / "candidate_values.csv"
    if not path.is_file() or not values.is_file():
        return False, "missing_complete_or_candidate"
    complete = json.loads(path.read_text(encoding="utf-8"))
    _paths, hashes = model_maps([model_id])
    base = configure_base([model_id])
    checks = {
        "status": complete.get("status") in {"passed", "passed_reused"},
        "geometry": complete.get("geometry_sha256") == hashes[model_id],
        "config": complete.get("config_sha256") == base.config_hash(CONFIG_ID),
        "candidate": complete.get("candidate_values_sha256") == sha256_file(values),
        "rows": int(complete.get("candidate_rows", -1)) == 40,
        "readback": int(complete.get("readback_mismatch_sum", -1)) == 0,
        "remaining": int(complete.get("transient_png_remaining", -1)) == 0,
        "audit": int(complete.get("audit_png_retained", -1)) == 6,
    }
    failed = [key for key, value in checks.items() if not value]
    return not failed, ";".join(failed) if failed else "all_hash_and_count_gates_passed"


def copy_slice003a_reuse(model_id: str) -> dict[str, Any]:
    source = SLICE003A_WORK / model_id
    complete_path = source / "complete.json"
    if not complete_path.is_file():
        raise FileNotFoundError(complete_path)
    original = json.loads(complete_path.read_text(encoding="utf-8"))
    original_hash = sha256_file(complete_path)
    target = MODEL_WORK / model_id
    if target.exists():
        okay, _ = valid_complete(model_id)
        if okay:
            return {"model_id": model_id, "reuse_source": "SLICE003A", "status": "already_prepared"}
        quarantine = RUN_WORK / "quarantine" / f"prepare_{model_id}_{datetime.now().strftime('%Y%m%dT%H%M%S')}"
        quarantine.parent.mkdir(parents=True, exist_ok=True)
        target.rename(quarantine)
    shutil.copytree(source, target)
    shutil.copy2(complete_path, target / "origin_complete.json")
    complete = dict(original)
    complete.update(
        {
            "run_id": RUN_ID,
            "status": "passed_reused",
            "reuse_source": "TOUR-C001-T4R-SLICE-003A",
            "reuse_source_path": rel(source),
            "reuse_source_complete_sha256": original_hash,
            "prepared_at_kst": now_kst(),
        }
    )
    write_json(target / "complete.json", complete)
    okay, detail = valid_complete(model_id)
    if not okay:
        raise RuntimeError(f"SLICE003A reuse validation failed: {model_id}: {detail}")
    return {"model_id": model_id, "reuse_source": "SLICE003A", "status": "passed_reused", "detail": detail}


def process_mask(mask: np.ndarray, model_id: str, slice_index: int, z_mm: float, mask_path: Path) -> tuple[dict[str, Any], np.ndarray, int]:
    mask = np.asarray(mask, dtype=bool)
    if not cv2.imwrite(str(mask_path), mask.astype(np.uint8) * 255, [cv2.IMWRITE_PNG_COMPRESSION, 1]):
        raise RuntimeError(f"failed to write {mask_path}")
    readback = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
    if readback is None:
        raise RuntimeError(f"failed to read {mask_path}")
    readback_bool = readback > 0
    mismatch = int(np.count_nonzero(readback_bool != mask))
    count, _labels, stats, _centroids = cv2.connectedComponentsWithStats(readback_bool.astype(np.uint8), connectivity=8)
    kept = int(sum(int(stats[label, cv2.CC_STAT_AREA]) >= 2 for label in range(1, count)))
    row = {
        "model_id": model_id,
        "config_id": CONFIG_ID,
        "slice_index": slice_index,
        "z_mm": z_mm,
        "material_pixel_count": int(readback_bool.sum()),
        "material_area_mm2": float(readback_bool.sum() * 0.0016),
        "component_count_raw": int(count - 1),
        "component_count_min2": kept,
        "mask_sha256": sha256_file(mask_path),
        "source_lane": "CINT02_overlay_reconstruction",
    }
    return row, readback_bool, mismatch


def prepare_cint02_reuse(model_id: str) -> dict[str, Any]:
    start = time.perf_counter()
    target = MODEL_WORK / model_id
    if target.exists():
        okay, _ = valid_complete(model_id)
        if okay:
            return {"model_id": model_id, "reuse_source": "CINT02", "status": "already_prepared"}
        quarantine = RUN_WORK / "quarantine" / f"prepare_{model_id}_{datetime.now().strftime('%Y%m%dT%H%M%S')}"
        quarantine.parent.mkdir(parents=True, exist_ok=True)
        target.rename(quarantine)
    table_dir = target / "tables"
    mask_dir = target / "runtime_images" / "mask"
    audit_dir = target / "audit_images"
    for path in (table_dir, mask_dir, audit_dir):
        path.mkdir(parents=True, exist_ok=True)

    manifest = pd.read_csv(CINT02_PANEL_MANIFEST, dtype=str, keep_default_na=False).set_index("model_id")
    row = manifest.loc[model_id]
    _paths, hashes = model_maps([model_id])
    if row["geometry_sha256"] != hashes[model_id]:
        raise RuntimeError(f"CINT02 geometry mismatch: {model_id}")
    expected_cfg = {
        "pixel_resolution": "1000x1000",
        "slice_count": "801",
        "slice_spacing_mm": "0.05",
        "axis": "z",
        "physical_size_mm": "40x40x40",
    }
    for key, value in expected_cfg.items():
        if str(row[key]) != value:
            raise RuntimeError(f"CINT02 config mismatch: {model_id}/{key}: {row[key]}")
    combine_dir = ROOT / row["combine_png_dir"]
    count, aggregate, first, last = aggregate_directory_hash(combine_dir, "combine_image_*.png")
    if (count, aggregate, first, last) != (800, row["combine_aggregate_sha256"], row["first_png_sha256"], row["last_png_sha256"]):
        raise RuntimeError(f"CINT02 PNG hash mismatch: {model_id}")

    payload_all = json.loads(CINT02_PAYLOAD.read_text(encoding="utf-8"))
    payload = {
        "LEGACY-PY-RESULT": payload_all[model_id]["LEGACY-PY-RESULT"],
        "LEGACY-PY-ANGLE-ALL": payload_all[model_id]["LEGACY-PY-ANGLE-ALL"],
    }
    base = configure_base([model_id])
    mapped = base.descriptor_rows(model_id, CONFIG_ID, payload)
    prior = pd.read_csv(SLICE001_BASELINE / "candidate_values.csv")
    prior = prior[prior["model_id"] == model_id].sort_values("candidate_id").reset_index(drop=True)
    current = pd.DataFrame(mapped).sort_values("candidate_id").reset_index(drop=True)
    if len(current) != 40 or not np.allclose(current["value"].astype(float), prior["value"].astype(float), rtol=0.0, atol=1e-12, equal_nan=True):
        raise RuntimeError(f"CINT02 candidate reconstruction mismatch: {model_id}")

    slice_rows: list[dict[str, Any]] = []
    overlay_rows: list[dict[str, Any]] = []
    component_rows: list[dict[str, Any]] = []
    audit_rows: list[dict[str, Any]] = []
    mismatch_sum = 0
    z_positions = np.linspace(-20.0, 20.0, 801)
    lower_first: np.ndarray | None = None
    for pair_index, combine_path in enumerate(sorted(combine_dir.glob("combine_image_*.png")), start=1):
        observed = cv2.imread(str(combine_path))
        if observed is None:
            raise RuntimeError(f"failed to read {combine_path}")
        gray = cv2.cvtColor(observed, cv2.COLOR_BGR2GRAY)
        values = sorted(int(value) for value in np.unique(gray))
        if not set(values).issubset({0, 29, 76, 105}):
            raise RuntimeError(f"gray contract failed: {combine_path}")
        red = gray == 76
        blue = gray == 29
        purple = gray == 105
        lower = red | purple
        upper = blue | purple
        if pair_index == 1:
            lower_first = lower
            mask_path = mask_dir / "m0000.png"
            slice_row, _readback, mismatch = process_mask(lower, model_id, 0, float(z_positions[0]), mask_path)
            slice_rows.append(slice_row)
            mismatch_sum += mismatch
        mask_path = mask_dir / f"m{pair_index:04d}.png"
        slice_row, _readback, mismatch = process_mask(upper, model_id, pair_index, float(z_positions[pair_index]), mask_path)
        slice_rows.append(slice_row)
        mismatch_sum += mismatch
        union = red | blue | purple
        comp_count, labels, stats, _centroids = cv2.connectedComponentsWithStats(union.astype(np.uint8), connectivity=8)
        overlay_rows.append(
            {
                "model_id": model_id,
                "config_id": CONFIG_ID,
                "pair_index": pair_index,
                "red_pixel_count": int(red.sum()),
                "blue_pixel_count": int(blue.sum()),
                "purple_pixel_count": int(purple.sum()),
                "union_pixel_count": int(union.sum()),
                "component_count_raw": int(comp_count - 1),
                "component_count_min2": int(sum(int(stats[label, cv2.CC_STAT_AREA]) >= 2 for label in range(1, comp_count))),
                "gray_values": ";".join(map(str, values)),
                "combine_sha256": sha256_file(combine_path),
                "source_lane": "CINT02_readonly_overlay",
            }
        )
        for label in range(1, comp_count):
            pixels = int(stats[label, cv2.CC_STAT_AREA])
            component_rows.append(
                {
                    "model_id": model_id,
                    "config_id": CONFIG_ID,
                    "pair_index": pair_index,
                    "component_index": label,
                    "pixel_count": pixels,
                    "area_mm2": pixels * 0.0016,
                    "kept_by_min2": pixels >= 2,
                    "source_lane": "CINT02_readonly_overlay",
                }
            )
    if lower_first is None or len(slice_rows) != 801 or len(overlay_rows) != 800:
        raise RuntimeError(f"CINT02 reconstruction count failure: {model_id}")

    write_csv(table_dir / "slice_pixel_readback.csv", slice_rows)
    write_csv(table_dir / "overlay_pixel_readback.csv", overlay_rows)
    write_csv(table_dir / "overlay_component_population.csv", component_rows)
    write_json(target / "legacy_direct_payload.json", payload)
    candidate_path = target / "candidate_values.csv"
    write_csv(candidate_path, mapped)
    for index in (0, 400, 800):
        source = mask_dir / f"m{index:04d}.png"
        destination = audit_dir / f"mask_{index:04d}.png"
        shutil.copy2(source, destination)
        audit_rows.append({"model_id": model_id, "config_id": CONFIG_ID, "artifact_role": "mask_audit", "artifact_index": index, "path": rel(destination), "sha256": sha256_file(destination)})
    for index in (1, 400, 800):
        source = combine_dir / f"combine_image_{index:04d}.png"
        destination = audit_dir / f"combine_{index:04d}.png"
        shutil.copy2(source, destination)
        audit_rows.append({"model_id": model_id, "config_id": CONFIG_ID, "artifact_role": "combine_audit", "artifact_index": index, "path": rel(destination), "sha256": sha256_file(destination), "source_path": rel(source)})
    write_csv(target / "audit_image_manifest.csv", audit_rows)

    deletion_rows: list[dict[str, Any]] = []
    for path in sorted((target / "runtime_images").rglob("*.png")):
        record = {"model_id": model_id, "config_id": CONFIG_ID, "transient_path": rel(path), "sha256_before_delete": sha256_file(path), "deleted": False, "reuse_note": "reconstructed from immutable CINT02 overlays"}
        path.unlink()
        record["deleted"] = not path.exists()
        deletion_rows.append(record)
    write_csv(target / "transient_png_deletion_ledger.csv", deletion_rows)
    remaining = list((target / "runtime_images").rglob("*.png"))
    complete = {
        "run_id": RUN_ID,
        "model_id": model_id,
        "config_id": CONFIG_ID,
        "status": "passed_reused" if mismatch_sum == 0 and not remaining and len(mapped) == 40 else "failed",
        "runtime_environment": "KMK312",
        "python_executable": sys.executable,
        "python_version": platform.python_version(),
        "geometry_path": row["geometry_path"],
        "geometry_sha256": row["geometry_sha256"],
        "config_sha256": base.config_hash(CONFIG_ID),
        "slice_rows": len(slice_rows),
        "overlay_rows": len(overlay_rows),
        "component_rows": len(component_rows),
        "candidate_rows": len(mapped),
        "readback_mismatch_sum": mismatch_sum,
        "transient_png_deleted": sum(bool(item["deleted"]) for item in deletion_rows),
        "transient_source_png_reused_readonly": 800,
        "transient_png_remaining": len(remaining),
        "audit_png_retained": len(audit_rows),
        "candidate_values_sha256": sha256_file(candidate_path),
        "runtime_seconds": time.perf_counter() - start,
        "completed_at_kst": now_kst(),
        "reuse_source": "CINT-02 canonical-N40 P1000_S801 overlays and direct payload",
        "reuse_source_manifest": rel(CINT02_PANEL_MANIFEST),
        "reuse_source_manifest_sha256": sha256_file(CINT02_PANEL_MANIFEST),
        "combine_aggregate_sha256": aggregate,
        "fit_metadata": {"fit_mode": "inherited_CINT02_fit_max_extent_to_cube", "fit_scale": 1.0},
    }
    write_json(target / "complete.json", complete)
    okay, detail = valid_complete(model_id)
    if not okay:
        raise RuntimeError(f"CINT02 reuse validation failed: {model_id}: {detail}")
    return {"model_id": model_id, "reuse_source": "CINT02", "status": "passed_reused", "detail": detail}


def model_to_shard() -> dict[str, str]:
    return {model_id: shard_id for shard_id, model_ids in SHARDS.items() for model_id in model_ids}


def prepare() -> None:
    validate_contract()
    RUN_WORK.mkdir(parents=True, exist_ok=True)
    for path in (CLAIMS, ATTEMPTS, FAILURES, LOGS):
        path.mkdir(parents=True, exist_ok=True)
    reuse_rows: list[dict[str, Any]] = []
    for model_id in REUSE_003A:
        reuse_rows.append(copy_slice003a_reuse(model_id))
    for model_id in REUSE_CINT02:
        reuse_rows.append(prepare_cint02_reuse(model_id))
    write_csv(REPORTS / "TOUR-C001-T4R-SLICE-004_reuse_audit.csv", reuse_rows)

    runtime_rows: list[dict[str, Any]] = []
    for model_id in REUSE_003A:
        complete = json.loads((SLICE003A_WORK / model_id / "complete.json").read_text(encoding="utf-8"))
        runtime_rows.append({"model_id": model_id, "family": model_id[0], "runtime_seconds": complete["runtime_seconds"], "runtime_minutes": complete["runtime_seconds"] / 60.0})
    runtimes = np.array([row["runtime_seconds"] for row in runtime_rows], dtype=float)
    median = float(np.median(runtimes))
    pending = 58 - len(REUSE_003A) - len(REUSE_CINT02)
    estimates = {
        "measured_model_count": len(runtime_rows),
        "median_runtime_seconds": median,
        "median_runtime_minutes": median / 60.0,
        "reused_model_count": 7,
        "new_geometry_slice_model_count": pending,
        "estimated_one_worker_seconds": pending * median,
        "estimated_two_worker_seconds": pending * median / 2.0,
        "estimated_one_worker_hours": pending * median / 3600.0,
        "estimated_two_worker_hours": pending * median / 7200.0,
        "estimate_excludes_contention_and_complexity_variation": True,
        "created_at_kst": now_kst(),
    }
    write_csv(REPORTS / "TOUR-C001-T4R-SLICE-004_runtime_reference.csv", runtime_rows)
    write_json(REPORTS / "TOUR-C001-T4R-SLICE-004_runtime_estimate.json", estimates)

    shard_of = model_to_shard()
    shard_rows: list[dict[str, Any]] = []
    for model_id in registry_frame()["model_id"]:
        okay, detail = valid_complete(model_id)
        shard_rows.append(
            {
                "shard_id": shard_of[model_id],
                "model_id": model_id,
                "family_code": model_id[0],
                "execution_state": "complete_reused" if okay else "pending",
                "reuse_lane": "SLICE003A" if model_id in REUSE_003A else "CINT02" if model_id in REUSE_CINT02 else "new_exact_slice",
                "validation_detail": detail,
            }
        )
    write_csv(REPORTS / "TOUR-C001-T4R-SLICE-004_shard_manifest.csv", shard_rows)
    print(json.dumps({"status": "prepared", **estimates}, ensure_ascii=False, allow_nan=False), flush=True)


def claim(model_id: str, worker_id: str) -> bool:
    CLAIMS.mkdir(parents=True, exist_ok=True)
    path = CLAIMS / f"{model_id}.json"
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
    except FileExistsError:
        return False
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        json.dump({"model_id": model_id, "worker_id": worker_id, "claimed_at_kst": now_kst(), "pid": os.getpid()}, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return True


def worker(worker_id: str) -> None:
    validate_contract()
    order = [model_id for model_ids in SHARDS.values() for model_id in model_ids]
    completed = 0
    skipped = 0
    failed = 0
    for model_id in order:
        okay, _detail = valid_complete(model_id)
        if okay:
            skipped += 1
            continue
        if not claim(model_id, worker_id):
            continue
        started = now_kst()
        try:
            base = configure_base([model_id])
            base.run_one(model_id, CONFIG_ID)
            okay, detail = valid_complete(model_id)
            if not okay:
                raise RuntimeError(f"post-run complete validation failed: {detail}")
            write_json(ATTEMPTS / f"{model_id}.json", {"model_id": model_id, "worker_id": worker_id, "status": "passed", "started_at_kst": started, "completed_at_kst": now_kst(), "detail": detail})
            completed += 1
        except Exception as error:
            write_json(
                FAILURES / f"{model_id}.json",
                {"model_id": model_id, "worker_id": worker_id, "status": "failed", "started_at_kst": started, "failed_at_kst": now_kst(), "error_type": type(error).__name__, "error": str(error), "traceback": traceback.format_exc()},
            )
            failed += 1
        print(json.dumps({"worker_id": worker_id, "model_id": model_id, "completed": completed, "failed": failed}, ensure_ascii=False), flush=True)
    print(json.dumps({"status": "worker_done", "worker_id": worker_id, "completed": completed, "skipped": skipped, "failed": failed}, ensure_ascii=False), flush=True)


def status() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    shard_of = model_to_shard()
    for model_id in registry_frame()["model_id"]:
        okay, detail = valid_complete(model_id)
        failure = FAILURES / f"{model_id}.json"
        claim_path = CLAIMS / f"{model_id}.json"
        if okay:
            state = "passed"
        elif failure.is_file():
            state = "failed"
        elif claim_path.is_file():
            state = "running_or_claimed"
        else:
            state = "pending"
        rows.append({"shard_id": shard_of[model_id], "model_id": model_id, "status": state, "validation_detail": detail})
    write_csv(REPORTS / "TOUR-C001-T4R-SLICE-004_live_status.csv", rows)
    summary = {state: sum(row["status"] == state for row in rows) for state in ["passed", "failed", "running_or_claimed", "pending"]}
    summary["checked_at_kst"] = now_kst()
    print(json.dumps(summary, ensure_ascii=False), flush=True)
    return summary


def reset_failed() -> None:
    for failure in sorted(FAILURES.glob("*.json")):
        model_id = failure.stem
        okay, _ = valid_complete(model_id)
        if okay:
            failure.unlink()
            continue
        claim_path = CLAIMS / f"{model_id}.json"
        if claim_path.exists():
            claim_path.unlink()
        failure.rename(FAILURES / f"{model_id}_{datetime.now().strftime('%Y%m%dT%H%M%S')}.history.json")
    print(json.dumps({"status": "failed_claims_reset", "at_kst": now_kst()}))


def launch_workers() -> None:
    """Launch exactly two hidden KMK312 workers and persist their process IDs."""
    validate_contract()
    summary = status()
    if summary["failed"]:
        raise RuntimeError("failed models exist; run reset-failed before relaunch")
    if summary["pending"] == 0 and summary["running_or_claimed"] == 0:
        print(json.dumps({"status": "nothing_to_launch", "passed": summary["passed"]}))
        return
    worker_state_path = RUN_WORK / "workers.json"
    if worker_state_path.is_file():
        prior = json.loads(worker_state_path.read_text(encoding="utf-8"))
        live = []
        for item in prior.get("workers", []):
            try:
                os.kill(int(item["pid"]), 0)
                live.append(item)
            except OSError:
                pass
        if live:
            raise RuntimeError(f"workers already live: {live}")
    workers: list[dict[str, Any]] = []
    creationflags = int(getattr(subprocess, "CREATE_NO_WINDOW", 0))
    for worker_id in ("W1", "W2"):
        stdout_path = LOGS / f"{worker_id}.stdout.log"
        stderr_path = LOGS / f"{worker_id}.stderr.log"
        stdout_handle = stdout_path.open("a", encoding="utf-8")
        stderr_handle = stderr_path.open("a", encoding="utf-8")
        process = subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve()), "worker", "--worker-id", worker_id],
            cwd=str(ROOT),
            stdin=subprocess.DEVNULL,
            stdout=stdout_handle,
            stderr=stderr_handle,
            creationflags=creationflags,
        )
        stdout_handle.close()
        stderr_handle.close()
        workers.append({"worker_id": worker_id, "pid": process.pid, "stdout": rel(stdout_path), "stderr": rel(stderr_path), "launched_at_kst": now_kst()})
    write_json(worker_state_path, {"run_id": RUN_ID, "workers": workers})
    print(json.dumps({"status": "workers_launched", "workers": workers}, ensure_ascii=False), flush=True)


def aggregate() -> None:
    validate_contract()
    all_candidates: list[pd.DataFrame] = []
    model_rows: list[dict[str, Any]] = []
    for model_id in registry_frame()["model_id"]:
        okay, detail = valid_complete(model_id)
        if not okay:
            raise RuntimeError(f"cannot aggregate incomplete model {model_id}: {detail}")
        root = MODEL_WORK / model_id
        complete = json.loads((root / "complete.json").read_text(encoding="utf-8"))
        model_rows.append(complete)
        all_candidates.append(pd.read_csv(root / "candidate_values.csv"))
    candidates = pd.concat(all_candidates, ignore_index=True)
    if len(candidates) != 2320 or candidates["model_id"].nunique() != 58:
        raise RuntimeError("58x40 candidate census failed")
    candidate_path = FROZEN / "TOUR-C001-T4R-SLICE-004_all58_direct_legacy_candidate_values.csv"
    candidate_path.parent.mkdir(parents=True, exist_ok=True)
    candidates.to_csv(candidate_path, index=False, encoding="utf-8-sig")
    selected_rows: list[dict[str, Any]] = []
    for signal in SIGNALS:
        for model_id in registry_frame()["model_id"]:
            subset = candidates[(candidates["model_id"] == model_id) & (candidates["candidate_id"].isin(signal["raw_candidate_ids"]))]
            values = subset["value"].astype(float).to_numpy()
            if len(values) == 0 or not np.isfinite(values).all() or not np.allclose(values, values[0], rtol=0.0, atol=1e-12):
                raise RuntimeError(f"selected signal lineage failure: {model_id}/{signal['signal_id']}")
            selected_rows.append({"model_id": model_id, "signal_id": signal["signal_id"], "canonical_candidate_id": signal["candidate_id"], "raw_candidate_ids": ";".join(signal["raw_candidate_ids"]), "value": float(values[0])})
    selected_path = FROZEN / "TOUR-C001-T4R-SLICE-004_all58_selected_rescue_signals.csv"
    write_csv(selected_path, selected_rows)
    write_csv(REPORTS / "TOUR-C001-T4R-SLICE-004_model_execution_QA.csv", model_rows)
    summary = {
        "run_id": RUN_ID,
        "model_count": 58,
        "candidate_rows": len(candidates),
        "candidate_ids": int(candidates["candidate_id"].nunique()),
        "selected_signal_rows": len(selected_rows),
        "reused_models": 7,
        "newly_sliced_models": 51,
        "slice_rows": sum(int(row["slice_rows"]) for row in model_rows),
        "overlay_rows": sum(int(row["overlay_rows"]) for row in model_rows),
        "component_rows": sum(int(row["component_rows"]) for row in model_rows),
        "readback_mismatch_sum": sum(int(row["readback_mismatch_sum"]) for row in model_rows),
        "transient_png_deleted": sum(int(row["transient_png_deleted"]) for row in model_rows),
        "transient_png_remaining": sum(int(row["transient_png_remaining"]) for row in model_rows),
        "audit_png_retained": sum(int(row["audit_png_retained"]) for row in model_rows),
        "performance_y_access": 0,
        "predictive_fits": 0,
        "feature_promotions": 0,
        "completed_at_kst": now_kst(),
    }
    write_json(REPORTS / "TOUR-C001-T4R-SLICE-004_execution_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, allow_nan=False), flush=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["freeze-contract", "prepare", "worker", "launch-workers", "status", "reset-failed", "aggregate"])
    parser.add_argument("--worker-id", default="W1")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "freeze-contract":
        freeze_contract()
    elif args.command == "prepare":
        prepare()
    elif args.command == "worker":
        worker(args.worker_id)
    elif args.command == "launch-workers":
        launch_workers()
    elif args.command == "status":
        status()
    elif args.command == "reset-failed":
        reset_failed()
    elif args.command == "aggregate":
        aggregate()


if __name__ == "__main__":
    main()
