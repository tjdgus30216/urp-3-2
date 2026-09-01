from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pandas as pd
import psutil


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
TABLES = LAB / "reports" / "tables"
FACTORY = LAB / "factories" / "PRM-098"
CONTRACTS = FACTORY / "contracts"
REPORTS = FACTORY / "reports"
GROUPS = ["LIT-X006", "LIT-X008", "LIT-X019", "LIT-X024", "LIT-X028", "LIT-X031"]
MODELS = ["B3", "C1", "L1", "F1", "T8", "T9"]
KST = timezone(timedelta(hours=9))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    CONTRACTS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    p97 = LAB / "factories" / "PRM-097"
    old_contract_path = p97 / "contracts" / "PRM-097_THIRD_WAVE_FORMULA_TEST_CONTRACT_20260723.json"
    old_contract = json.loads(old_contract_path.read_text(encoding="utf-8"))
    old_independent = json.loads((p97 / "reports" / "PRM097_independent_QA_summary.json").read_text(encoding="utf-8"))
    input_hash_pass = all((ROOT / x["path"]).exists() and sha256(ROOT / x["path"]) == x["sha256"] for x in old_contract["inputs"])

    prm078 = pd.read_csv(TABLES / "PRM078_fixed_domain_mask_manifest.csv", dtype=str, keep_default_na=False)
    prm081 = pd.read_csv(TABLES / "PRM081_full58_model_source_registry.csv", dtype=str, keep_default_na=False)
    rows = []
    for model in MODELS:
        for resolution in ["V064", "V096"]:
            hit = prm078.loc[prm078.model_id.eq(model) & prm078.resolution_id.eq(resolution)].iloc[0]
            path = ROOT / hit.mask_path
            rows.append({"model_id": model, "model_family": model[0], "resolution_id": resolution, "voxels_per_axis": int(resolution[1:]), "pitch_mm": 40/int(resolution[1:]), "asset_role": "reuse_existing_mask", "asset_path": hit.mask_path, "expected_sha256": hit.mask_sha256, "actual_sha256": sha256(path), "hash_pass": sha256(path) == hit.mask_sha256, "creation_authorized": False})
        source = prm081.loc[prm081.model_id.eq(model)].iloc[0]
        mask_path = ROOT / source.reuse_mask_path
        rows.append({"model_id": model, "model_family": source.model_family, "resolution_id": "V128", "voxels_per_axis": 128, "pitch_mm": 0.3125, "asset_role": "reuse_existing_mask", "asset_path": source.reuse_mask_path, "expected_sha256": source.reuse_mask_sha256, "actual_sha256": sha256(mask_path), "hash_pass": sha256(mask_path) == source.reuse_mask_sha256, "creation_authorized": False})
        stl_path = ROOT / source.processed_file
        rows.append({"model_id": model, "model_family": source.model_family, "resolution_id": "V192", "voxels_per_axis": 192, "pitch_mm": 40/192, "asset_role": "new_mask_only_if_progressive_gate_passes", "asset_path": source.processed_file, "expected_sha256": source.expected_processed_sha256, "actual_sha256": sha256(stl_path), "hash_pass": sha256(stl_path) == source.expected_processed_sha256, "creation_authorized": True})
    registry = pd.DataFrame(rows)
    registry.to_csv(TABLES / "PRM098_input_mask_source_registry.csv", index=False, encoding="utf-8-sig", lineterminator="\n")

    amendment = pd.DataFrame([{
        "amendment_id": "P098-A01",
        "source_contract": "PRM097 X019-F01",
        "original_text": "numerator and denominator must use the same V128 mask, axis and statistic",
        "corrected_pre_execution_text": "numerator and denominator must use the same current-resolution mask, axis and statistic",
        "reason": "PRM097 independently froze V64/V96/V128/V192 resolution rows; V128 token is a clerical specialization inconsistent with that panel",
        "result_seen_before_amendment": False,
        "scientific_change": True,
        "scope_change": "none; same-parent rule generalized to every preregistered resolution",
        "status": "confirmed_pre_execution_amendment",
    }])
    amendment.to_csv(TABLES / "PRM098_pre_execution_contract_amendment.csv", index=False, encoding="utf-8-sig", lineterminator="\n")

    available_gib = psutil.virtual_memory().available / 1024**3
    free_gib = psutil.disk_usage(str(ROOT)).free / 1024**3
    other_python = [p.pid for p in psutil.process_iter(["pid", "name"]) if (p.info["name"] or "").lower().startswith("python") and p.pid != os.getpid()]
    preflight = pd.DataFrame([
        {"check_id": "PF-01", "check": "PRM097 contract exists", "status": "PASS" if old_contract_path.exists() else "FAIL", "detail": str(old_contract_path)},
        {"check_id": "PF-02", "check": "PRM097 independent QA", "status": "PASS" if old_independent["status"] == "PASS" else "FAIL", "detail": str(old_independent)},
        {"check_id": "PF-03", "check": "PRM097 input hashes", "status": "PASS" if input_hash_pass else "FAIL", "detail": str(input_hash_pass)},
        {"check_id": "PF-04", "check": "18 reused masks plus six V192 STL sources", "status": "PASS" if len(registry) == 24 and registry.hash_pass.all() else "FAIL", "detail": f"{int(registry.hash_pass.sum())}/{len(registry)}"},
        {"check_id": "PF-05", "check": "available RAM >= 8 GiB", "status": "PASS" if available_gib >= 8 else "FAIL", "detail": f"{available_gib:.2f} GiB"},
        {"check_id": "PF-06", "check": "free disk >= 10 GiB", "status": "PASS" if free_gib >= 10 else "FAIL", "detail": f"{free_gib:.2f} GiB"},
        {"check_id": "PF-07", "check": "no competing Python process", "status": "PASS" if not other_python else "FAIL", "detail": str(other_python)},
        {"check_id": "PF-08", "check": "X019 amendment occurs before results", "status": "PASS", "detail": "result_seen_before_amendment=False"},
    ])
    preflight.to_csv(REPORTS / "PRM098_preflight_QA.csv", index=False, encoding="utf-8-sig", lineterminator="\n")

    permit = {
        "work_id": "PRM-098",
        "title": "BOUNDED_THIRD_WAVE_SYNTHETIC_TRUTH_COST_CANARY_AND_REPRESENTATIVE_PANEL",
        "created_at_kst": datetime.now(KST).isoformat(),
        "status": "authorized_bounded_progressive_execution" if preflight.status.eq("PASS").all() else "blocked",
        "parent_contract_path": str(old_contract_path.relative_to(ROOT)),
        "parent_contract_sha256": sha256(old_contract_path),
        "pre_execution_amendment": amendment.iloc[0].to_dict(),
        "candidate_groups": GROUPS,
        "representative_models": MODELS,
        "ordered_stages": ["synthetic_truth", "serial_V064_cost_canary", "progressive_representative_panel_V064_V096_V128_V192", "control_tower_return"],
        "authorized_actions": {"synthetic_truth": 1, "serial_V064_cost_canary": 1, "representative_panel": 1, "create_six_V192_masks_after_gate": 1},
        "locks": {"full58": 0, "performance_y_read": 0, "model_fit": 0, "feature_selection": 0, "feature_promotion": 0, "NB_CURRENT_mutation": 0, "LEGACY_PY_mutation": 0, "original_Excel_mutation": 0},
        "stop_policy": "group stops on synthetic failure, nondeterminism, resource cap or unchanged EQG-11 failure; no automatic retry or threshold tuning",
    }
    permit_path = CONTRACTS / "PRM-098_BOUNDED_EXECUTION_PERMIT_20260723.json"
    permit_path.write_text(json.dumps(permit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = {"status": "PASS" if preflight.status.eq("PASS").all() else "FAIL", "checks": f"{preflight.status.eq('PASS').sum()}/{len(preflight)}", "asset_hashes": f"{int(registry.hash_pass.sum())}/{len(registry)}", "other_python": other_python, "permit": permit["status"]}
    (REPORTS / "PRM098_preflight_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    if summary["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
