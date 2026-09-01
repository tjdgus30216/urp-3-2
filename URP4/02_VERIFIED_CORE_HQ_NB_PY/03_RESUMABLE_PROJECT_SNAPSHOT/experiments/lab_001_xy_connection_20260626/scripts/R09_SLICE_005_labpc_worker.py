from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import sys
import threading
import time
import traceback
from pathlib import Path

import numpy as np
import pandas as pd
import psutil

from R09_SLICE_005_labpc_common import (
    atomic_json,
    directory_bytes,
    now_kst,
    package_root,
    read_csv,
    read_json,
    safe_job_name,
    sha256,
)


ROOT = package_root()
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


CONTRACT_PATH = ROOT / "contracts/PRM-050_R09-SLICE-005_LABPC_EXECUTION.json"
MATRIX_PATH = ROOT / "config/pending_32_job_matrix.csv"
AUTH_PATH = ROOT / "preflight/runtime_authorization.json"
MANIFEST_PATH = ROOT / "PACKAGE_MANIFEST.csv"


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
                self.peak_system_percent = max(
                    self.peak_system_percent, float(psutil.virtual_memory().percent)
                )
                self.samples += 1
            except psutil.Error:
                pass
            self.stop.wait(0.25)

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


def scalar_rows(model_id: str, cfg: ExtractionConfig, output: object) -> pd.DataFrame:
    tables = output.tables
    occupancy = slice_occupancy(
        tables.slice_pixels, pixel_count=cfg.pixel_width * cfg.pixel_height
    )
    counts = slice_component_count(tables.slice_pixels)
    change = overlay_change_fraction(tables.overlay_pixels)
    overlap = overlay_overlap_fraction(tables.overlay_pixels)
    thickness = finite_component_population(
        tables.overlay_components, "thickness_sqrt_red_purple"
    )
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
    return pd.DataFrame(
        [
            {
                "model_id": model_id,
                "formula_id": formula_id,
                "descriptor": descriptor,
                "statistic": statistic,
                "unit": unit,
                "value": value,
                "population_n": population_n,
                "scientific_state": state,
                "config_sha256": cfg.config_sha256,
            }
            for formula_id, descriptor, statistic, unit, value, population_n, state in specs
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--attempt", type=int, required=True)
    args = parser.parse_args()

    contract = read_json(CONTRACT_PATH)
    authorization = read_json(AUTH_PATH)
    if platform.python_version() != "3.12.12" or "KMK312" not in str(Path(sys.executable)):
        raise RuntimeError("KMK312 Python 3.12.12 is required")
    if contract["preregistration_id"] != "PRM-050" or not contract["execution_authorized"]:
        raise RuntimeError("PRM-050 execution authority is missing")
    if authorization.get("status") != "passed_and_authorized":
        raise RuntimeError("live doctor authorization is missing")
    if authorization["static_contract_sha256"] != sha256(CONTRACT_PATH):
        raise RuntimeError("static contract hash drift after doctor authorization")
    if authorization["package_manifest_sha256"] != sha256(MANIFEST_PATH):
        raise RuntimeError("package manifest hash drift after doctor authorization")
    if sha256(Path(__file__).resolve()) != contract["code_hashes"]["worker"]:
        raise RuntimeError("worker hash drift")

    jobs = {row["execution_cell_id"]: row for row in read_csv(MATRIX_PATH)}
    if args.job_id not in jobs:
        raise KeyError(f"unknown or non-pending job: {args.job_id}")
    if not 1 <= args.attempt <= int(contract["max_attempts_per_cell"]):
        raise RuntimeError("attempt number exceeds contract")
    job = jobs[args.job_id]
    source_meta = contract["sources"][job["model_id"]]
    source = ROOT / source_meta["path"]
    if sha256(source) != source_meta["sha256"]:
        raise RuntimeError(f"source hash drift: {job['model_id']}")

    job_root = ROOT / "results/runtime" / safe_job_name(args.job_id)
    output_dir = job_root / f"attempt{args.attempt:02d}"
    if output_dir.exists():
        raise FileExistsError(f"attempt directory already exists: {output_dir}")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    started = now_kst()
    started_clock = time.perf_counter()
    free_before = shutil.disk_usage(output_dir.parent).free
    cfg = ExtractionConfig(
        axis=job["axis"],
        physical_size_mm=float(job["physical_size_mm"]),
        pixel_width=int(job["pixel_width"]),
        pixel_height=int(job["pixel_height"]),
        slice_count=int(job["slice_count"]),
        slice_spacing_mm=float(job["slice_spacing_mm"]),
        area_per_pixel_mm2=float(job["area_per_pixel_mm2"]),
        length_per_pixel_mm=float(job["length_per_pixel_mm"]),
        connectivity=int(job["connectivity"]),
        min_component_pixels=int(job["min_component_pixels"]),
        endpoint_nudge_mm=float(job["endpoint_nudge_mm"]),
        png_compress_level=int(contract["config_constant"]["png_compress_level"]),
    )
    cfg.validate()
    sampler = ResourceSampler()
    try:
        with sampler:
            result = Run139ExtractionPipeline(cfg).extract(
                model_id=job["model_id"],
                geometry_path=source,
                output_dir=output_dir,
                mode="STREAMING",
                expected_geometry_sha256=source_meta["sha256"],
                overwrite=False,
            )
            scalars = scalar_rows(job["model_id"], cfg, result)
            scalar_path = output_dir / "tables/descriptor_result.csv"
            scalars.to_csv(
                scalar_path, index=False, encoding="utf-8-sig", lineterminator="\n"
            )

        elapsed = time.perf_counter() - started_clock
        free_after = shutil.disk_usage(output_dir.parent).free
        table_paths = sorted((output_dir / "tables").glob("*.csv"))
        table_manifest = pd.DataFrame(
            [
                {
                    "path": path.relative_to(ROOT).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
                for path in table_paths
            ]
        )
        table_manifest_path = output_dir / "table_hash_manifest.csv"
        table_manifest.to_csv(
            table_manifest_path, index=False, encoding="utf-8-sig", lineterminator="\n"
        )
        qa = result.qa
        gates = {
            "pipeline_status": qa["status"] == "passed",
            "slice_rows": qa["slice_rows"] == int(job["slice_count"]),
            "overlay_rows": qa["overlay_rows"] == int(job["slice_count"]) - 1,
            "png_accounting": qa["png_created"] == 2 * int(job["slice_count"]) - 1
            and qa["png_deleted"] == 2 * int(job["slice_count"]) - 1
            and qa["remaining_png"] == 0,
            "readback": qa["readback_mismatch_sum"] == 0,
            "scalar_rows": bool(len(scalars) == 9 and np.isfinite(scalars.value).all()),
            "runtime": elapsed <= float(contract["resource_gates"]["per_cell_seconds"]),
            "memory": sampler.peak_rss <= float(contract["resource_gates"]["per_cell_peak_rss_bytes"]),
            "output": directory_bytes(output_dir) <= float(contract["resource_gates"]["per_cell_output_bytes"]),
        }
        complete = {
            "job_id": args.job_id,
            "attempt": args.attempt,
            "status": "passed" if all(gates.values()) else "failed",
            "started_at_kst": started,
            "completed_at_kst": now_kst(),
            "runtime_seconds": elapsed,
            "runtime": {
                "alias": "KMK312",
                "python": platform.python_version(),
                "executable": str(Path(sys.executable).resolve()),
            },
            "source": source_meta,
            "job": job,
            "config_sha256": cfg.config_sha256,
            "qa": qa,
            "resource": {
                "peak_rss_bytes": sampler.peak_rss,
                "peak_rss_gib": sampler.peak_rss / 2**30,
                "peak_system_memory_percent": sampler.peak_system_percent,
                "samples": sampler.samples,
                "output_bytes": directory_bytes(output_dir),
                "disk_free_before": free_before,
                "disk_free_after": free_after,
            },
            "gates": gates,
            "table_manifest": table_manifest_path.relative_to(ROOT).as_posix(),
            "table_manifest_sha256": sha256(table_manifest_path),
            "worker_sha256": contract["code_hashes"]["worker"],
            "static_contract_sha256": sha256(CONTRACT_PATH),
        }
        atomic_json(output_dir / "complete.json", complete)
        if complete["status"] != "passed":
            raise RuntimeError(
                f"cell gates failed: {[name for name, value in gates.items() if not value]}"
            )
        print(
            json.dumps(
                {
                    "status": "passed",
                    "job_id": args.job_id,
                    "attempt": args.attempt,
                    "seconds": round(elapsed, 3),
                    "peak_rss_gib": round(sampler.peak_rss / 2**30, 3),
                    "output_mib": round(directory_bytes(output_dir) / 2**20, 3),
                },
                ensure_ascii=False,
            )
        )
    except Exception as exc:
        atomic_json(
            output_dir / "failure.json",
            {
                "job_id": args.job_id,
                "attempt": args.attempt,
                "status": "failed",
                "started_at_kst": started,
                "failed_at_kst": now_kst(),
                "error_type": type(exc).__name__,
                "error": str(exc),
                "traceback": traceback.format_exc(),
                "worker_sha256": sha256(Path(__file__).resolve()),
                "static_contract_sha256": sha256(CONTRACT_PATH),
            },
        )
        raise


if __name__ == "__main__":
    main()
