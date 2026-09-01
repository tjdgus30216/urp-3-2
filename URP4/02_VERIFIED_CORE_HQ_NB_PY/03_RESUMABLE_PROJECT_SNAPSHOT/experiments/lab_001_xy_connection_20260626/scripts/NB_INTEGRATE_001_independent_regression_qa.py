"""Read-only independent regression QA for NB-INTEGRATE-001."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
CANONICAL_KMK = ROOT / "tools" / "envs" / "KMK312" / "python.exe"
FACTORY = LAB / "factories" / "NB-INTEGRATE-001"
CONTRACT = FACTORY / "contracts" / "NB-INTEGRATE-001_CONTRACT.json"
OUTPUT = FACTORY / "outputs"
QA_DIR = LAB / "results" / "NB-INTEGRATE-001" / "NB-INTEGRATE-001-20260729-001"
NOTEBOOK = LAB / "notebooks" / "NB_DEV_v0_6_ROUTE_VALID_004_IMPORT_POLICY.ipynb"
POLICY_QA = LAB / "results" / "ROUTE-VALID-004" / "ROUTE-VALID-004-20260729-001" / "INDEPENDENT_QA.json"
BASELINE = LAB / "results" / "HQ-BLUEPRINT-001" / "PROTECTED_ASSET_BASELINE.json"


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


def main() -> None:
    if Path(sys.executable).resolve() != CANONICAL_KMK.resolve():
        raise RuntimeError(f"canonical KMK312 required; got {sys.executable}")
    QA_DIR.mkdir(parents=True, exist_ok=False)
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    smoke = json.loads((OUTPUT / "NB-INTEGRATE-001_CONTROLLER_SMOKE.json").read_text(encoding="utf-8"))
    manifest = json.loads((OUTPUT / "NB-INTEGRATE-001_F1_PREFLIGHT_MANIFEST.json").read_text(encoding="utf-8"))
    policy_qa = json.loads(POLICY_QA.read_text(encoding="utf-8"))
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    test = subprocess.run([sys.executable, str(LAB / "scripts" / "test_NB_INTEGRATE_001_route_policy.py")], capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=ROOT)
    (QA_DIR / "FIXTURE_TEST_OUTPUT.txt").write_text(test.stdout + test.stderr, encoding="utf-8")
    protected = json.loads(BASELINE.read_text(encoding="utf-8"))["assets"]
    protected_rows = []
    for item in protected:
        path = ROOT / item["path"]
        if item["asset_kind"] == "tree":
            current, count, size = tree_identity(path)
        else:
            current, count, size = sha256(path), 1, path.stat().st_size
        expected = item.get("expected_sha256") or item["before_sha256"]
        protected_rows.append({"alias": item["alias"], "status": "passed" if current == expected else "failed", "expected": expected, "actual": current, "file_count": count, "bytes": size})
    checks = [
        ("IQ01", Path(sys.executable).resolve() == CANONICAL_KMK.resolve(), "canonical project-local KMK312 executable"),
        ("IQ02", policy_qa["status"] == "passed" and all(policy_qa["checks"].values()), "ROUTE-VALID-004 policy QA accepted"),
        ("IQ03", smoke["status"] == "passed" and smoke["route_id"] == "IMP-STL-ORIENTED-NONZERO-DEVELOPMENT-ROUTE-C", "F1 paired-confirmed Route C preflight"),
        ("IQ04", smoke["warning_flags"] == ["F1_Z400_UNRESOLVED"], "F1 warning propagated"),
        ("IQ05", smoke["execution_enabled"] is False and smoke["scientific_production_qualified"] is False, "technical development separated from production"),
        ("IQ06", all(value is False for value in manifest["execution"].values()), "no geometry/slice/descriptor/y/model execution"),
        ("IQ07", manifest["runtime"]["sys_executable"] == str(CANONICAL_KMK), "manifest records canonical sys.executable"),
        ("IQ08", bool(manifest["decision"]["config_sha256"]) and bool(contract["policy_contract_sha256"]), "config and policy hashes present"),
        ("IQ09", nb["metadata"]["kernelspec"]["display_name"] == "KMK312" and len(nb["cells"]) == 4, "versioned notebook kernel and cell map"),
        ("IQ10", all(cell.get("execution_count") is None for cell in nb["cells"] if cell["cell_type"] == "code"), "notebook has no executed code cells"),
        ("IQ11", test.returncode == 0 and "Ran 9 tests" in (test.stdout + test.stderr), "fixture fail-closed regression suite"),
        ("IQ12", len(protected_rows) == 31 and all(row["status"] == "passed" for row in protected_rows), "protected assets unchanged"),
        ("IQ13", manifest["runtime_path_discovery_correction"]["prior_scientific_results_invalidated"] is False, "runtime discovery correction does not invalidate prior science"),
    ]
    with (QA_DIR / "INDEPENDENT_QA.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle); writer.writerow(["check_id", "status", "evidence"])
        writer.writerows([[name, "passed" if passed else "failed", evidence] for name, passed, evidence in checks])
    with (QA_DIR / "PROTECTED_ASSET_RECHECK.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(protected_rows[0])); writer.writeheader(); writer.writerows(protected_rows)
    result = {"work_id": "NB-INTEGRATE-001_IMPORT_ROUTE_CONTROLLER_VERSIONED_DEVELOPMENT_NO_Y", "run_id": "NB-INTEGRATE-001-20260729-001", "status": "passed" if all(item[1] for item in checks) else "failed", "qa": f"{sum(item[1] for item in checks)}/{len(checks)}", "runtime": manifest["runtime"], "protected_assets": f"{sum(row['status'] == 'passed' for row in protected_rows)}/{len(protected_rows)}", "scope": "independent controller/fixture/notebook/hash regression only; no slicing/descriptor/y/model execution"}
    (QA_DIR / "INDEPENDENT_QA.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
