"""Execute one isolated PRM-047 B3 500x500/801 STREAMING canary attempt."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import sys
import threading
import time
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import psutil

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from urp4.descriptor_service.v0_1.config import ExtractionConfig
from urp4.descriptor_service.v0_1.formula import population_mean, population_std_ddof0
from urp4.descriptor_service.v0_1.pipeline import Run139ExtractionPipeline
from urp4.descriptor_service.v0_1.population import (
    finite_component_population,
    overlay_change_fraction,
    overlay_overlap_fraction,
    slice_component_count,
    slice_occupancy,
)


LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
FACTORY = LAB / "factories" / "R09-SLICE-005"
CONTRACT = FACTORY / "contracts" / "R09-SLICE-005_B3_COARSE_DUPLICATE_CANARY_FINAL_EXECUTION_20260721.json"
KST = timezone(timedelta(hours=9))


def now_kst() -> str:
    return datetime.now(KST).isoformat(timespec="milliseconds")


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def atomic_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def dir_bytes(path: Path) -> int:
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


class ResourceSampler:
    def __init__(self) -> None:
        self.process = psutil.Process(os.getpid())
        self.stop = threading.Event()
        self.peak_rss = 0
        self.peak_system_percent = 0.0
        self.samples = 0
        self.thread = threading.Thread(target=self._run, daemon=True)

    def _run(self) -> None:
        while not self.stop.is_set():
            try:
                self.peak_rss = max(self.peak_rss, int(self.process.memory_info().rss))
                self.peak_system_percent = max(self.peak_system_percent, float(psutil.virtual_memory().percent))
                self.samples += 1
            except psutil.Error:
                pass
            self.stop.wait(0.2)

    def __enter__(self) -> "ResourceSampler":
        self.thread.start()
        return self

    def __exit__(self, *_args: object) -> None:
        self.stop.set()
        self.thread.join(timeout=2)
        try:
            self.peak_rss = max(self.peak_rss, int(self.process.memory_info().rss))
        except psutil.Error:
            pass


def scalar_rows(model_id: str, cfg: ExtractionConfig, output: Any) -> pd.DataFrame:
    tables = output.tables
    occupancy = slice_occupancy(tables.slice_pixels, pixel_count=cfg.pixel_width * cfg.pixel_height)
    counts = slice_component_count(tables.slice_pixels)
    change = overlay_change_fraction(tables.overlay_pixels)
    overlap = overlay_overlap_fraction(tables.overlay_pixels)
    thickness = finite_component_population(tables.overlay_components, "thickness_sqrt_red_purple")
    massori = finite_component_population(tables.overlay_components, "mass_orientation")
    specs = [
        ("XRV1-F001", "slice_occupancy_mean", "mean", "dimensionless", population_mean(occupancy), len(occupancy), "confirmed"),
        ("XRV1-F002", "slice_occupancy_std_pop", "std_pop_ddof0", "dimensionless", population_std_ddof0(occupancy), len(occupancy), "confirmed"),
        ("XRV1-F003", "component_count_mean", "mean", "count", population_mean(counts), len(counts), "confirmed"),
        ("XRV1-F004", "component_count_std_pop", "std_pop_ddof0", "count", population_std_ddof0(counts), len(counts), "confirmed"),
        ("XRV1-F005", "overlay_change_fraction_mean", "mean", "dimensionless", population_mean(change), len(change), "confirmed"),
        ("XRV1-F006", "overlay_overlap_fraction_mean", "mean", "dimensionless", population_mean(overlap), len(overlap), "confirmed"),
        ("XRV1-F007", "thickness_component_sqrt_red_purple_area", "mean", "mm", population_mean(thickness), len(thickness), "provisional"),
        ("XRV1-F007", "thickness_component_sqrt_red_purple_area", "std_pop_ddof0", "mm", population_std_ddof0(thickness), len(thickness), "provisional"),
        ("XRV1-F008", "massori_component_pool_mean", "mean", "dimensionless", population_mean(massori), len(massori), "likely"),
    ]
    rows = []
    for formula_id, descriptor, statistic, unit, value, n, state in specs:
        rows.append({"model_id": model_id, "formula_id": formula_id, "descriptor": descriptor,
                     "statistic": statistic, "unit": unit, "value": value, "population_n": n,
                     "scientific_state": state, "config_sha256": cfg.config_sha256})
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", choices=["E", "F"], required=True)
    args = parser.parse_args()
    if platform.python_version() != "3.12.12" or "KMK312" not in sys.executable:
        raise RuntimeError("KMK312 Python 3.12.12 required")
    if not CONTRACT.is_file():
        raise FileNotFoundError("PRM-047 contract missing")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if contract["preregistration_id"] != "PRM-049" or not contract["execution_authorized"]:
        raise RuntimeError("current canary authority missing")
    worker_expected = contract["worker_script"]["sha256"]
    if sha(Path(__file__).resolve()) != worker_expected:
        raise RuntimeError("worker live hash differs from PRM-047")
    allowed = set(contract["authorized_attempts"])
    attempt_id = f"B3-COARSE-{args.attempt}"
    if attempt_id not in allowed:
        raise RuntimeError("attempt not authorized")
    source = ROOT / contract["source"]["path"]
    if sha(source) != contract["source"]["sha256"]:
        raise RuntimeError("B3 source hash drift")
    output_dir = FACTORY / "runtime" / attempt_id
    if output_dir.exists():
        raise FileExistsError(f"attempt directory already exists: {output_dir}")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    started = now_kst()
    start_clock = time.perf_counter()
    free_before = shutil.disk_usage(output_dir.parent).free
    c = contract["config"]
    cfg = ExtractionConfig(**c)
    cfg.validate()
    sampler = ResourceSampler()
    try:
        with sampler:
            result = Run139ExtractionPipeline(cfg).extract(
                model_id="B3", geometry_path=source, output_dir=output_dir,
                mode="STREAMING", expected_geometry_sha256=contract["source"]["sha256"], overwrite=False,
            )
            scalars = scalar_rows("B3", cfg, result)
            scalar_path = output_dir / "tables" / "descriptor_result.csv"
            scalars.to_csv(scalar_path, index=False, encoding="utf-8-sig", lineterminator="\n")
        elapsed = time.perf_counter() - start_clock
        free_after = shutil.disk_usage(output_dir.parent).free
        table_paths = sorted((output_dir / "tables").glob("*.csv"))
        table_manifest = pd.DataFrame([{"path": rel(p), "bytes": p.stat().st_size, "sha256": sha(p)} for p in table_paths])
        table_manifest_path = output_dir / "table_hash_manifest.csv"
        table_manifest.to_csv(table_manifest_path, index=False, encoding="utf-8-sig", lineterminator="\n")
        qa = result.qa
        gates = {
            "pipeline_status": qa["status"] == "passed",
            "slice_rows": qa["slice_rows"] == 801,
            "overlay_rows": qa["overlay_rows"] == 800,
            "png_accounting": qa["png_created"] == 1601 and qa["png_deleted"] == 1601 and qa["remaining_png"] == 0,
            "readback": qa["readback_mismatch_sum"] == 0,
            "scalar_rows": bool(len(scalars) == 9 and bool(np.isfinite(scalars.value).all())),
            "runtime": elapsed <= float(contract["resource_gates"]["per_attempt_seconds"]),
            "memory": sampler.peak_rss <= float(contract["resource_gates"]["peak_rss_bytes"]),
            "scratch": dir_bytes(output_dir) <= float(contract["resource_gates"]["per_attempt_output_bytes"]),
        }
        complete = {
            "attempt_id": attempt_id, "status": "passed" if all(gates.values()) else "failed",
            "started_at_kst": started, "completed_at_kst": now_kst(), "runtime_seconds": elapsed,
            "runtime": {"alias": "KMK312", "python": platform.python_version(), "executable": str(Path(sys.executable).resolve())},
            "source": contract["source"], "config": c, "config_sha256": cfg.config_sha256,
            "qa": qa, "resource": {"peak_rss_bytes": sampler.peak_rss, "peak_rss_gib": sampler.peak_rss/2**30,
                                          "peak_system_memory_percent": sampler.peak_system_percent, "samples": sampler.samples,
                                          "output_bytes": dir_bytes(output_dir), "disk_free_before": free_before,
                                          "disk_free_after": free_after},
            "gates": gates, "table_manifest": rel(table_manifest_path), "table_manifest_sha256": sha(table_manifest_path),
            "worker_sha256": worker_expected, "contract_sha256": sha(CONTRACT),
        }
        atomic_json(output_dir / "complete.json", complete)
        if complete["status"] != "passed":
            raise RuntimeError(f"canary attempt gates failed: {[k for k,v in gates.items() if not v]}")
        print(json.dumps({"status":"passed", "attempt":attempt_id, "seconds":round(elapsed,3),
                          "peak_rss_gib":round(sampler.peak_rss/2**30,3), "output_mib":round(dir_bytes(output_dir)/2**20,3)}, ensure_ascii=False))
    except Exception as exc:
        failure = {"attempt_id": attempt_id, "status": "failed", "started_at_kst": started,
                   "failed_at_kst": now_kst(), "error_type": type(exc).__name__, "error": str(exc),
                   "traceback": traceback.format_exc(), "worker_sha256": sha(Path(__file__).resolve()),
                   "contract_sha256": sha(CONTRACT) if CONTRACT.is_file() else ""}
        atomic_json(output_dir / "failure.json", failure)
        raise


if __name__ == "__main__":
    main()
