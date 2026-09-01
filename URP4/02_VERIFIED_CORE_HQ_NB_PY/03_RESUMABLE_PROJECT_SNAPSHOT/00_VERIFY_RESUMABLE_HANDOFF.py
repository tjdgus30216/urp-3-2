#!/usr/bin/env python3
"""Read-only integrity/syntax check for the resumable URP4-1 snapshot."""
from __future__ import annotations

import ast
import csv
import hashlib
import json
from pathlib import Path
import sys
import zipfile


HERE = Path(__file__).resolve().parent
RELEASE_ROOT = HERE.parents[2]
URP4_ROOT = RELEASE_ROOT / "URP4"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


checks: list[dict[str, object]] = []


def record(name: str, passed: bool, detail: str) -> None:
    checks.append({"check": name, "passed": bool(passed), "detail": detail})


required = [
    HERE / "URP4_1_HQ.ipynb",
    HERE / "URP4-1_DELIVERABLE" / "urp4",
    HERE / "RAW_SLICE_TABLES_XREG_V2_7.zip",
    HERE / "RAW_SLICE_TABLE_MANIFEST.csv",
    HERE / "experiments" / "lab_001_xy_connection_20260626" / "scripts" / "STRICT_STEP_026_c1_direct_legacy_py_xonly.py",
    HERE / "experiments" / "lab_001_xy_connection_20260626" / "results" / "STRICT-STEP-026" / "STRICT-STEP-026-20260731-001" / "INDEPENDENT_QA.json",
]
for path in required:
    record(f"required:{path.name}", path.exists(), str(path))

index_path = URP4_ROOT / "00_READ_ME_FIRST" / "ALGORITHM_FILE_INDEX.csv"
with index_path.open("r", encoding="utf-8-sig", newline="") as handle:
    index_rows = list(csv.DictReader(handle))
missing = []
mismatched = []
for row in index_rows:
    path = RELEASE_ROOT / row["relative_path"]
    if not path.is_file():
        missing.append(row["relative_path"])
        continue
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest.lower() != row["sha256"].lower() or path.stat().st_size != int(row["bytes"]):
        mismatched.append(row["relative_path"])
record("algorithm_index_paths", not missing, f"rows={len(index_rows)} missing={len(missing)}")
record("algorithm_index_hashes", not mismatched, f"mismatched={len(mismatched)}")

syntax_failures = []
py_roots = [
    HERE / "experiments" / "lab_001_xy_connection_20260626" / "scripts",
    HERE / "URP4-1_DELIVERABLE" / "urp4",
]
py_count = 0
for root in py_roots:
    for path in root.rglob("*.py"):
        py_count += 1
        try:
            ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
        except Exception as exc:  # pragma: no cover - diagnostic output
            syntax_failures.append(f"{path}: {exc}")
record("python_ast_parse", not syntax_failures, f"files={py_count} failures={len(syntax_failures)}")

raw_manifest = HERE / "RAW_SLICE_TABLE_MANIFEST.csv"
with raw_manifest.open("r", encoding="utf-8-sig", newline="") as handle:
    raw_rows = list(csv.DictReader(handle))
raw_bad = []
with zipfile.ZipFile(HERE / "RAW_SLICE_TABLES_XREG_V2_7.zip") as archive:
    crc_bad = archive.testzip()
    names = set(archive.namelist())
    for row in raw_rows:
        name = row["relative_path"]
        if name not in names:
            raw_bad.append(f"missing:{name}")
            continue
        data = archive.read(name)
        if len(data) != int(row["bytes"]) or sha256_bytes(data).lower() != row["sha256"].lower():
            raw_bad.append(f"hash:{name}")
record("raw_table_archive_crc", crc_bad is None, f"first_bad={crc_bad}")
record("raw_table_manifest", not raw_bad and len(names) == len(raw_rows), f"manifest={len(raw_rows)} archive={len(names)} bad={len(raw_bad)}")

c1_qa_path = HERE / "experiments" / "lab_001_xy_connection_20260626" / "results" / "STRICT-STEP-026" / "STRICT-STEP-026-20260731-001" / "INDEPENDENT_QA.json"
if c1_qa_path.is_file():
    c1 = json.loads(c1_qa_path.read_text(encoding="utf-8-sig"))
    payload = json.dumps(c1, ensure_ascii=False).lower()
    record("c1_copied_independent_qa", "pass" in payload and "fail" not in payload, str(c1_qa_path))

result = {
    "verifier": "00_VERIFY_RESUMABLE_HANDOFF.py",
    "read_only": True,
    "python": sys.version,
    "checks": checks,
    "passed": all(bool(item["passed"]) for item in checks),
}
print(json.dumps(result, ensure_ascii=False, indent=2))
raise SystemExit(0 if result["passed"] else 1)
