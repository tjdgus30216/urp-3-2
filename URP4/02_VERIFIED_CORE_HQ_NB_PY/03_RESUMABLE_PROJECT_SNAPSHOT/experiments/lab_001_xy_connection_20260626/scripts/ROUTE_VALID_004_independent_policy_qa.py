"""Independent read-only QA for ROUTE-VALID-004 policy outputs.

No geometry/math/model execution.  Checks that the policy is rooted in passed
predecessor evidence, retains the F1 warning, and cannot silently promote
development integration to scientific production qualification.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
RUN_ID = "ROUTE-VALID-004-20260729-001"
RESULT = LAB / "results" / "ROUTE-VALID-004" / RUN_ID
TABLES = LAB / "reports" / "tables"
PREFIX = f"{RUN_ID}_"


def rows(name: str) -> list[dict[str, str]]:
    with (TABLES / f"{PREFIX}{name}.csv").open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tree_identity(path: Path) -> tuple[str, int, int]:
    digest = hashlib.sha256()
    files = [item for item in sorted(path.rglob("*")) if item.is_file() and "__pycache__" not in item.parts]
    total = 0
    for item in files:
        relative = item.relative_to(path).as_posix()
        size = item.stat().st_size
        total += size
        digest.update(relative.encode("utf-8") + b"\0" + sha256(item).encode("ascii") + b"\0" + str(size).encode("ascii") + b"\n")
    return digest.hexdigest(), len(files), total


def protected_audit() -> tuple[bool, list[dict[str, str]]]:
    baseline_path = LAB / "results" / "HQ-BLUEPRINT-001" / "PROTECTED_ASSET_BASELINE.json"
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))["assets"]
    audit_rows: list[dict[str, str]] = []
    for item in baseline:
        path = ROOT / item["path"]
        if item["asset_kind"] == "tree":
            actual_hash, count, size = tree_identity(path)
        else:
            actual_hash, count, size = sha256(path), 1, path.stat().st_size
        expected = item.get("expected_sha256", item["before_sha256"])
        audit_rows.append({
            "alias": item["alias"], "asset_kind": item["asset_kind"], "path": item["path"],
            "expected_sha256": expected, "actual_sha256": actual_hash,
            "expected_size_bytes": str(item["before_size_bytes"]), "actual_size_bytes": str(size),
            "expected_file_count": str(item.get("before_file_count", 1)), "actual_file_count": str(count),
            "status": "passed" if actual_hash == expected else "failed",
        })
    with (RESULT / "PROTECTED_ASSET_RECHECK.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(audit_rows[0]))
        writer.writeheader()
        writer.writerows(audit_rows)
    return all(row["status"] == "passed" for row in audit_rows), audit_rows


def main() -> None:
    contract = json.loads((RESULT / "POLICY_CONTRACT.json").read_text(encoding="utf-8"))
    source = rows("source_type_route_policy")
    evidence = rows("family_model_evidence_matrix")
    gate = rows("nb_integration_gate")
    fallback = rows("fail_closed_fallback")
    report = (RESULT / "REPORT.md").read_text(encoding="utf-8")
    protected_ok, protected_rows = protected_audit()
    checks = {
        "predecessor_001_003_all_passed": all(
            json.loads(Path(contract["predecessors"][key]["path"]).read_text(encoding="utf-8"))["status"] == "passed"
            for key in ("route_valid_001", "route_valid_002", "route_valid_003")
        ),
        "003a_is_quarantine_only": "not eligible for QA, merge" in Path(contract["predecessors"]["route_valid_003a_quarantine"]["path"]).read_text(encoding="utf-8"),
        "development_and_production_separated": any(r["scope"] == "NB versioned development integration" and r["decision"] == "conditional_yes" for r in gate) and any(r["scope"] == "scientific production qualification" and r["decision"] == "no" for r in gate),
        "003a_not_development_prerequisite": contract["decisions"]["route_valid_003a_as_prerequisite"] == "no",
        "f1_z400_warning_persistent": any(r["model_or_group"] == "F1" and r["status"] == "unresolved" and "z400" in r["evidence"] for r in evidence) and "F1_Z400_UNRESOLVED" in report,
        "all_required_source_type_lanes_present": {r["source_type"] for r in source} >= {"original_step_with_paired_confirmed_imported_stl", "original_step_with_paired_likely_imported_stl", "stl_only_imported", "orientation_held_pair", "missing_or_hash_mismatch"},
        "stl_only_does_not_claim_step_reference": any(r["source_type"] == "stl_only_imported" and "no A-C reference" in r["production_qualification"] for r in source),
        "fallback_is_fail_closed": len(fallback) >= 8 and all(r["status"] == "fail_closed" for r in fallback),
        "a_b_not_imported_stl_claim": "A-B is representation consistency only" in report,
        "no_protected_asset_mutation_claim": "remain unchanged" in report,
        "protected_asset_recheck_31_31": protected_ok and len(protected_rows) == 31,
        "strict_backlog_named": "STRICT-F1-001_EXACT_A_LONG_RUN_AND_DECLARED_DEFLECTION_SENSITIVITY_NO_Y" in report,
    }
    result = {
        "work_id": "ROUTE-VALID-004_ROUTE_POLICY_DECISION_AND_NB_INTEGRATION_GATE_NO_Y",
        "run_id": RUN_ID,
        "status": "passed" if all(checks.values()) else "failed",
        "checks": checks,
        "scope": "independent read-only policy audit; no geometry/slice/descriptor/Excel/y/notebook mutation",
    }
    (RESULT / "INDEPENDENT_QA.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest_rows = []
    for path in sorted(RESULT.iterdir()):
        if path.is_file() and path.name not in {"OUTPUT_MANIFEST.csv", "FINAL_OUTPUT_MANIFEST.csv"}:
            manifest_rows.append({
                "path": str(path.relative_to(ROOT)), "sha256": sha256(path),
                "bytes": str(path.stat().st_size), "role": "result_or_qa_artifact",
            })
    for path in sorted(TABLES.glob(f"{PREFIX}*.csv")):
        manifest_rows.append({
            "path": str(path.relative_to(ROOT)), "sha256": sha256(path),
            "bytes": str(path.stat().st_size), "role": "policy_table",
        })
    with (RESULT / "FINAL_OUTPUT_MANIFEST.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(manifest_rows[0]))
        writer.writeheader()
        writer.writerows(manifest_rows)
    if not all(checks.values()):
        raise SystemExit("ROUTE-VALID-004 independent QA failed")


if __name__ == "__main__":
    main()
