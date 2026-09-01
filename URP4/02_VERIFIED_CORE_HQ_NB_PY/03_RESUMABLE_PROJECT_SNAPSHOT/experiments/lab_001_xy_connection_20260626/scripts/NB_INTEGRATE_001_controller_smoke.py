"""Run the development-only F1 Route-C preflight under canonical KMK312."""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
CANONICAL_KMK = ROOT / "tools" / "envs" / "KMK312" / "python.exe"
FACTORY = LAB / "factories" / "NB-INTEGRATE-001"
CONTRACT_DIR = FACTORY / "contracts"
OUTPUT_DIR = FACTORY / "outputs"
POLICY = LAB / "results" / "ROUTE-VALID-004" / "ROUTE-VALID-004-20260729-001" / "POLICY_CONTRACT.json"
F1_SOURCE = LAB / "data" / "raw" / "notion_reference_models_20260701" / "stl" / "F1-Foam-Kelvin_foam.stl"
F1_SHA256 = "0dff3c1b133d7c9d5eee7d32cb0b19734eadc20c3c710268d745118ffdfe9300"

sys.path.insert(0, str(ROOT / "URP4-1_DELIVERABLE"))
from urp4.route_policy.v0_1 import ImportRouteRequest, build_development_manifest, decide_route  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if Path(sys.executable).resolve() != CANONICAL_KMK.resolve():
        raise RuntimeError(f"canonical KMK312 required; got {sys.executable}")
    if not POLICY.is_file() or not F1_SOURCE.is_file():
        raise FileNotFoundError("policy or F1 source missing")
    if sha256(F1_SOURCE) != F1_SHA256:
        raise RuntimeError("F1 source hash drift")
    CONTRACT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    policy_sha = sha256(POLICY)
    request = ImportRouteRequest(
        model_id="F1",
        input_mode="imported",
        source_type="paired_confirmed",
        source_identity_status="confirmed",
        source_path=str(F1_SOURCE),
        expected_source_sha256=F1_SHA256,
        route_config={
            "axis": "z",
            "algorithm_revision": "ORIENTED_NONZERO_RAW/IMSTL-004/r1",
            "normalization_mode": "uniform_bbox_to_expected",
            "source_mutation": False,
            "mesh_repair": False,
            "stl_to_step_proxy": False,
        },
        policy_evidence_sha256=policy_sha,
        production_requested=False,
    )
    decision = decide_route(request)
    manifest = build_development_manifest(request, decision, command=[sys.executable, str(Path(__file__).resolve())])
    manifest["runtime_path_discovery_correction"] = {
        "canonical_runtime": str(CANONICAL_KMK),
        "canonical_runtime_version": platform.python_version(),
        "noncanonical_duplicate_path": r"C:\Users\chuck\anaconda3\envs\KMK312",
        "duplicate_state": "partial_quarantined_do_not_use",
        "prior_scientific_results_invalidated": False,
    }
    contract = {
        "work_id": "NB-INTEGRATE-001_IMPORT_ROUTE_CONTROLLER_VERSIONED_DEVELOPMENT_NO_Y",
        "run_id": "NB-INTEGRATE-001-20260729-001",
        "policy_contract_path": str(POLICY),
        "policy_contract_sha256": policy_sha,
        "f1_source_path": str(F1_SOURCE),
        "f1_source_sha256": F1_SHA256,
        "runtime": manifest["runtime"],
        "prohibitions": manifest["execution"],
        "required_warning": "F1_Z400_UNRESOLVED",
        "decision_boundary": "development_controller_only; scientific_production_qualification_closed",
    }
    (CONTRACT_DIR / "NB-INTEGRATE-001_CONTRACT.json").write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUTPUT_DIR / "NB-INTEGRATE-001_F1_PREFLIGHT_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = {
        "status": "passed",
        "route_id": decision.route_id,
        "warning_flags": list(decision.warning_flags),
        "execution_enabled": decision.execution_enabled,
        "scientific_production_qualified": decision.scientific_production_qualified,
        "config_sha256": decision.config_sha256,
        "policy_sha256": policy_sha,
        "source_sha256": decision.source_sha256,
        "runtime": manifest["runtime"],
        "no_geometry_or_descriptor_execution": True,
    }
    (OUTPUT_DIR / "NB-INTEGRATE-001_CONTROLLER_SMOKE.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
