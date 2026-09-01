from __future__ import annotations

"""Fail-closed runner for a future PRM-100 six-output V128 census.

PRM-099 may call only ``doctor``. ``run-cell`` and ``merge`` require the
exact-hash PRM-100 permit and are intentionally not invoked by PRM-099.
"""

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import psutil


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
FACTORY = LAB / "factories" / "PRM-099"
DEFAULT_CONFIG = FACTORY / "contracts" / "PRM099_FULL58_SIX_OUTPUT_CONFIG_20260723.json"
DEFAULT_CONTRACT = FACTORY / "contracts" / "PRM-099_FULL58_PERMIT_DECISION_CONTRACT_20260723.json"
DEFAULT_PERMIT = FACTORY / "authorizations" / "PRM-100_THIRD_WAVE_FULL58_V128_EXECUTION_PERMIT_20260723.json"
FORMULA_LIBRARY = LAB / "scripts" / "PRM098_third_wave_formula_library.py"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from PRM098_third_wave_formula_library import ect_outputs  # noqa: E402


OUTPUTS = [
    "LIT-X019::solid_void_chord_q50_geomean_ratio",
    "LIT-X019::solid_void_chord_x_q50_ratio",
    "LIT-X019::solid_void_chord_y_q50_ratio",
    "LIT-X019::solid_void_chord_z_q50_ratio",
    "LIT-X024::ect_abs_auc_direction_mean_per_mm3",
    "LIT-X024::ect_total_variation_direction_mean_per_mm3",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(payload: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def atomic_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    frame.to_csv(tmp, index=False, encoding="utf-8-sig", lineterminator="\n")
    os.replace(tmp, path)


def competitors() -> list[dict]:
    out = []
    ancestor_pids = {p.pid for p in psutil.Process(os.getpid()).parents()}
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            if proc.pid == os.getpid() or proc.pid in ancestor_pids:
                continue
            if "python" in (proc.info.get("name") or "").lower():
                out.append({"pid": proc.pid, "name": proc.info.get("name"), "cmdline": proc.info.get("cmdline")})
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return out


def validate_config(config_path: Path, contract_path: Path) -> tuple[dict, dict]:
    config = read_json(config_path)
    contract = read_json(contract_path)
    if config.get("work_id") != "PRM-099" or contract.get("work_id") != "PRM-099":
        raise SystemExit("work identity mismatch")
    if config.get("resolution_id") != "V128" or config.get("expected_models") != 58:
        raise SystemExit("scope mismatch")
    if config.get("output_roster") != OUTPUTS or contract.get("output_roster") != OUTPUTS:
        raise SystemExit("output roster mismatch")
    if contract.get("runner_sha256") != sha256(Path(__file__)):
        raise SystemExit("runner hash mismatch")
    if contract.get("config_sha256") != sha256(config_path):
        raise SystemExit("config hash mismatch")
    if contract.get("formula_library_sha256") != sha256(FORMULA_LIBRARY):
        raise SystemExit("formula library hash mismatch")
    return config, contract


def validate_permit(permit_path: Path, config_path: Path, contract_path: Path) -> dict:
    permit = read_json(permit_path)
    expected = {
        "execution_authorized": True,
        "authorized_work_id": "PRM-100",
        "runner_sha256": sha256(Path(__file__)),
        "config_sha256": sha256(config_path),
        "contract_sha256": sha256(contract_path),
        "formula_library_sha256": sha256(FORMULA_LIBRARY),
        "expected_models": 58,
        "expected_values": 348,
        "output_roster": OUTPUTS,
    }
    for key, value in expected.items():
        if permit.get(key) != value:
            raise SystemExit(f"permit mismatch: {key}")
    if permit.get("allowed_actions") != ["run-cell", "merge"]:
        raise SystemExit("permit action mismatch")
    if any(int(v) != 0 for v in permit.get("locks", {}).values()):
        raise SystemExit("permit scientific lock mismatch")
    return permit


def validate_assets(config: dict) -> None:
    for cell in config["cells"]:
        mask = ROOT / cell["mask_path"]
        if not mask.is_file() or sha256(mask) != cell["mask_sha256"]:
            raise SystemExit(f"mask mismatch: {cell['model_id']}")
    parent = ROOT / config["xreg_parent_table_path"]
    if not parent.is_file() or sha256(parent) != config["xreg_parent_table_sha256"]:
        raise SystemExit("XREG parent table mismatch")


def doctor(args: argparse.Namespace) -> None:
    config, _ = validate_config(args.config, args.contract)
    validate_assets(config)
    permit_valid = False
    if args.permit:
        validate_permit(args.permit, args.config, args.contract)
        permit_valid = True
    payload = {
        "status": "PASS",
        "source_mask_cells_verified": "58/58",
        "output_roster": "6/6",
        "x019_route": "derive_from_existing_X001_X016_V128_values",
        "x024_route": "compute_from_existing_V128_masks",
        "permit_valid": permit_valid,
        "competing_python_processes": competitors(),
        "available_ram_gib": psutil.virtual_memory().available / 2**30,
        "free_disk_gib": psutil.disk_usage(str(ROOT)).free / 2**30,
    }
    print(json.dumps(payload, ensure_ascii=False))


def derive_x019(model_id: str, config: dict) -> dict[str, float]:
    table = pd.read_csv(ROOT / config["xreg_parent_table_path"])
    table = table[table["model_id"].eq(model_id)].set_index("candidate_id")
    ratios: dict[str, float] = {}
    for axis in "xyz":
        solid = float(table.loc[f"LIT-X001::solid_chord_{axis}_q50_mm", "value"])
        void = float(table.loc[f"LIT-X016::void_chord_{axis}_q50_mm", "value"])
        if not np.isfinite(solid) or not np.isfinite(void) or void <= 1e-12:
            raise SystemExit(f"invalid X019 parent: {model_id}/{axis}")
        ratios[axis] = solid / void
    return {
        "LIT-X019::solid_void_chord_q50_geomean_ratio": float(np.exp(np.mean(np.log(list(ratios.values()))))),
        **{f"LIT-X019::solid_void_chord_{axis}_q50_ratio": value for axis, value in ratios.items()},
    }


def run_cell(args: argparse.Namespace) -> None:
    config, _ = validate_config(args.config, args.contract)
    validate_permit(args.permit, args.config, args.contract)
    if competitors():
        raise SystemExit("competing Python process")
    cells = {row["model_id"]: row for row in config["cells"]}
    if args.model not in cells:
        raise SystemExit("model outside scope")
    cell = cells[args.model]
    mask_path = ROOT / cell["mask_path"]
    if sha256(mask_path) != cell["mask_sha256"]:
        raise SystemExit("mask hash mismatch")
    outdir = FACTORY / "intermediate" / args.model
    if (outdir / "done.json").exists():
        marker = read_json(outdir / "done.json")
        if marker.get("status") == "passed" and marker.get("output_roster") == OUTPUTS:
            print(json.dumps({"status": "reused", "model_id": args.model}))
            return
        raise SystemExit("existing incomplete or mismatched cell")
    start = time.perf_counter()
    x019 = derive_x019(args.model, config)
    with np.load(mask_path) as z:
        mask = z["volume"].astype(bool, copy=False)
        pitch = float(z["pitch_mm"])
    ect = ect_outputs(mask, pitch, heights=129, max_seconds=float(config["resource_stop"]["single_cell_wall_seconds_max"]))
    x024 = {key: ect.outputs[key] for key in OUTPUTS if key.startswith("LIT-X024")}
    values = {**x019, **x024}
    if set(values) != set(OUTPUTS) or not all(np.isfinite(v) for v in values.values()):
        raise SystemExit("output roster/nonfinite mismatch")
    outdir.mkdir(parents=True, exist_ok=True)
    curve_path = outdir / "ECT_curve_26x129.npz"
    np.savez_compressed(curve_path, value=ect.artifacts["ECT_curve_26x129"])
    frame = pd.DataFrame([{"model_id": args.model, "candidate_id": cid, "value": values[cid]} for cid in OUTPUTS])
    atomic_csv(frame, outdir / "values.csv")
    elapsed = time.perf_counter() - start
    marker = {
        "status": "passed",
        "model_id": args.model,
        "resolution_id": "V128",
        "output_roster": OUTPUTS,
        "output_count": 6,
        "runtime_s": elapsed,
        "mask_sha256": cell["mask_sha256"],
        "runner_sha256": sha256(Path(__file__)),
        "formula_library_sha256": sha256(FORMULA_LIBRARY),
        "permit_sha256": sha256(args.permit),
        "ECT_curve_sha256": sha256(curve_path),
        "diagnostic_final_chi": ect.outputs["LIT-X024::ect_final_chi_solid_density_trace_per_mm3"],
    }
    if elapsed > float(config["resource_stop"]["single_cell_wall_seconds_max"]):
        marker["status"] = "resource_stop"
    atomic_json(marker, outdir / "done.json")
    print(json.dumps(marker, ensure_ascii=False))
    if marker["status"] != "passed":
        raise SystemExit(2)


def merge(args: argparse.Namespace) -> None:
    config, _ = validate_config(args.config, args.contract)
    validate_permit(args.permit, args.config, args.contract)
    rows = []
    for cell in config["cells"]:
        outdir = FACTORY / "intermediate" / cell["model_id"]
        marker = read_json(outdir / "done.json") if (outdir / "done.json").exists() else {}
        if marker.get("status") != "passed" or marker.get("output_roster") != OUTPUTS:
            raise SystemExit(f"partial merge blocked: {cell['model_id']}")
        frame = pd.read_csv(outdir / "values.csv")
        if len(frame) != 6 or set(frame["candidate_id"]) != set(OUTPUTS):
            raise SystemExit(f"cell roster mismatch: {cell['model_id']}")
        rows.append(frame)
    merged = pd.concat(rows, ignore_index=True)
    if len(merged) != 348 or not np.isfinite(merged["value"]).all():
        raise SystemExit("merged scope mismatch")
    atomic_csv(merged, LAB / "reports" / "tables" / "PRM099_third_wave_full58_six_values_long.csv")
    wide = merged.pivot(index="model_id", columns="candidate_id", values="value").reset_index()
    atomic_csv(wide, LAB / "reports" / "tables" / "PRM099_third_wave_full58_six_values_wide.csv")
    print(json.dumps({"status": "PASS", "models": 58, "values": 348}))


def parse() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["doctor", "run-cell", "merge"])
    ap.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    ap.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    ap.add_argument("--permit", type=Path, default=None)
    ap.add_argument("--model")
    args = ap.parse_args()
    if args.action in {"run-cell", "merge"} and args.permit is None:
        ap.error("--permit is required")
    if args.action == "run-cell" and not args.model:
        ap.error("--model is required")
    return args


if __name__ == "__main__":
    args = parse()
    {"doctor": doctor, "run-cell": run_cell, "merge": merge}[args.action](args)
