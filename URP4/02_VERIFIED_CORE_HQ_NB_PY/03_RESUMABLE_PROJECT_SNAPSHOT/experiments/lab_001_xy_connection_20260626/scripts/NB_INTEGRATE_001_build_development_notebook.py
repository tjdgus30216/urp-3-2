"""Build a status-only NB-DEV v0.6 notebook; it never alters prior notebooks."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
TARGET = LAB / "notebooks" / "NB_DEV_v0_6_ROUTE_VALID_004_IMPORT_POLICY.ipynb"
POLICY = LAB / "results" / "ROUTE-VALID-004" / "ROUTE-VALID-004-20260729-001" / "POLICY_CONTRACT.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cell(kind: str, source: str, semantic_id: str) -> dict[str, object]:
    payload: dict[str, object] = {
        "cell_type": kind,
        "id": semantic_id.lower(),
        "metadata": {"semantic_id": semantic_id, "urp4_role": "NB-INTEGRATE-001"},
        "source": [line + "\n" for line in source.rstrip("\n").split("\n")],
    }
    if kind == "code":
        payload.update({"execution_count": None, "outputs": []})
    return payload


def main() -> None:
    if TARGET.exists():
        raise FileExistsError(f"Refusing to overwrite versioned notebook: {TARGET}")
    if not POLICY.is_file():
        raise FileNotFoundError(POLICY)
    policy_hash = sha256(POLICY)
    config_cell = r'''# NB-DEV v0.6: versioned Route-C development preflight only
# This notebook does not slice, calculate descriptors, access y, or train.
from pathlib import Path
import hashlib, json, sys

PROJECT_ROOT = Path.cwd().resolve()
while not (PROJECT_ROOT / "URP4-1_DELIVERABLE" / "urp4").is_dir() and PROJECT_ROOT.parent != PROJECT_ROOT:
    PROJECT_ROOT = PROJECT_ROOT.parent
if not (PROJECT_ROOT / "URP4-1_DELIVERABLE" / "urp4").is_dir():
    raise RuntimeError("Set cwd inside URP4-1 project root before running")
sys.path.insert(0, str(PROJECT_ROOT / "URP4-1_DELIVERABLE"))

from urp4.route_policy.v0_1 import ImportRouteRequest, decide_route, build_development_manifest

POLICY_PATH = PROJECT_ROOT / "experiments/lab_001_xy_connection_20260626/results/ROUTE-VALID-004/ROUTE-VALID-004-20260729-001/POLICY_CONTRACT.json"
POLICY_SHA256 = hashlib.sha256(POLICY_PATH.read_bytes()).hexdigest()

# Public edit surface.  Keep RUN_PREFLIGHT=False until a separately approved input is supplied.
ROUTE_POLICY_CONFIG = {
    "model_id": "F1",
    "input_mode": "imported",
    "source_type": "paired_confirmed",
    "source_identity_status": "confirmed",
    "source_path": "",
    "expected_source_sha256": "",
    "production_requested": False,
    "route_config": {
        "axis": "z",
        "algorithm_revision": "ORIENTED_NONZERO_RAW/IMSTL-004/r1",
        "normalization_mode": "uniform_bbox_to_expected",
        "source_mutation": False,
        "mesh_repair": False,
        "stl_to_step_proxy": False,
    },
}
RUN_PREFLIGHT = False
print("NB-DEV v0.6 is status-only; RUN_PREFLIGHT=False; no geometry execution is available.")
'''
    preflight_cell = r'''# Optional preflight.  This only writes a manifest when explicitly enabled.
if RUN_PREFLIGHT:
    request = ImportRouteRequest(**ROUTE_POLICY_CONFIG, policy_evidence_sha256=POLICY_SHA256)
    decision = decide_route(request)
    manifest = build_development_manifest(request, decision, command=[sys.executable, "NB_DEV_v0_6_ROUTE_VALID_004_IMPORT_POLICY.ipynb"])
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    assert decision.execution_enabled is False
else:
    print("Preflight not run. Slice/descriptor/y/model stages remain locked.")
'''
    notebook = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {"display_name": "KMK312", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.12.12"},
            "urp4_nb_dev": {
                "alias": "NB-DEV",
                "version": "v0.6",
                "feature": "ROUTE-VALID-004 source-aware import development preflight",
                "policy_contract_sha256": policy_hash,
                "replaces": "none",
                "nb_current_modified": False,
                "scientific_production_qualified": False,
            },
        },
        "cells": [
            cell("markdown", "# NB-DEV v0.6 — Route-C development controller\n\nThis is a separate development-only preflight notebook. It cannot run slicing, descriptor extraction, y access, Training or production release.", "NBDEV6-CELL-00"),
            cell("code", config_cell, "NBDEV6-CELL-01"),
            cell("code", preflight_cell, "NBDEV6-CELL-02"),
            cell("markdown", "## Gate\n\n- `paired_confirmed` imported STL only\n- F1 writes `F1_Z400_UNRESOLVED`\n- every decision has source/config/policy hashes\n- `execution_enabled` remains false\n- `paired_likely`, STL-only, orientation-held and production requests fail closed", "NBDEV6-CELL-03"),
        ],
    }
    TARGET.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"target": str(TARGET), "sha256": sha256(TARGET), "policy_sha256": policy_hash}, ensure_ascii=False))


if __name__ == "__main__":
    main()
