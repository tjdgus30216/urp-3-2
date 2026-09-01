"""Independent, read-only QA for the SUBMIT-CLOSE-001 staging tree or archive."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path
from urllib.parse import unquote

from openpyxl import load_workbook


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def add(checks, cid, description, passed, observed, expected):
    checks.append({"check_id": cid, "description": description, "status": "PASS" if passed else "FAIL", "observed": observed, "expected": expected})


def check_tree(package: Path, write_result: bool) -> dict:
    checks = []
    required_dirs = [
        "00_READ_ME_FIRST", "01_PROJECT_MAP_AND_LEDGER", "02_VERIFIED_CORE_HQ_NB_PY", "03_CONFIG_RUNTIME_AND_COMMANDS",
        "04_REFERENCE_INPUTS", "05_DESCRIPTOR_XREG_GEOMETRY_EVIDENCE", "06_TRAINING_EVIDENCE",
        "07_COMPRESSION_DATA_AND_PILOT", "08_OPTIONAL_UI_DEMO", "09_LIMITATIONS_AND_RESUME", "10_MANIFEST_SHA256_AND_QA",
    ]
    add(checks, "QA-001", "required directories", all((package / d).is_dir() for d in required_dirs), [d for d in required_dirs if (package / d).is_dir()], required_dirs)
    schema_path = package / "01_PROJECT_MAP_AND_LEDGER" / "PROJECT_SCHEMA.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    add(checks, "QA-002", "schema cutoff/version", schema.get("cutoff_id") == "HANDOFF-CUTOFF-20260801-001" and schema.get("schema_version") == "1.1", [schema.get("cutoff_id"), schema.get("schema_version")], ["HANDOFF-CUTOFF-20260801-001", "1.1"])
    c1 = schema.get("submission_close_v1_1", {}).get("c1", {})
    add(checks, "QA-003", "C1 terminal state", c1.get("status") == "completed_with_evidence" and c1.get("slices") == 801 and c1.get("overlays") == 800 and c1.get("scalars") == 40, c1, "completed/801/800/40")
    training = schema.get("submission_close_v1_1", {}).get("training", {})
    add(checks, "QA-004", "Training blocker state", training.get("status") == "closed_for_submission_as_blocked_with_evidence" and training.get("numerical_parity") == "BLOCKED_BY_SOURCE_RUNTIME", training, "closed_for_submission_as_blocked_with_evidence")
    ai = schema.get("submission_close_v1_1", {}).get("ai_lattice", {})
    add(checks, "QA-005", "AI Lattice technical pilot state", ai.get("exact_join") == 149 and ai.get("oof_predictions") == 9536 and ai.get("qa") == "36/36 PASS", ai, "149/9536/36-of-36")
    blob = schema_path.read_text(encoding="utf-8")
    stale = []
    for row in schema.get("work_packages", []):
        if row.get("work_id") == "STRICT-STEP-026" and row.get("execution_status") == "running":
            stale.append("STRICT-STEP-026 running")
        if row.get("work_id") == "TRAIN-PARITY-004" and "not_started" in row.get("execution_status", ""):
            stale.append("TRAIN-PARITY-004 not_started")
    add(checks, "QA-006", "no stale C1/Training status", not stale, stale, [])

    json_errors = []
    for p in package.rglob("*.json"):
        try:
            json.loads(p.read_text(encoding="utf-8-sig"))
        except Exception as e:
            json_errors.append(f"{p.relative_to(package)}:{type(e).__name__}")
    for p in package.rglob("*.ipynb"):
        try:
            json.loads(p.read_text(encoding="utf-8-sig"))
        except Exception as e:
            json_errors.append(f"{p.relative_to(package)}:{type(e).__name__}")
    add(checks, "QA-007", "JSON/IPYNB parse", not json_errors, json_errors, [])

    csv_errors = []
    csv_count = 0
    for p in package.rglob("*.csv"):
        try:
            with p.open("r", encoding="utf-8-sig", newline="") as f:
                reader = csv.reader(f)
                next(reader, None)
            csv_count += 1
        except Exception as e:
            csv_errors.append(f"{p.relative_to(package)}:{type(e).__name__}")
    add(checks, "QA-008", "CSV parse", not csv_errors, {"parsed": csv_count, "errors": csv_errors}, "zero errors")

    xlsx_errors = []
    xlsx_count = 0
    for p in package.rglob("*.xlsx"):
        try:
            wb = load_workbook(p, read_only=True, data_only=False)
            _ = wb.sheetnames
            wb.close()
            xlsx_count += 1
        except Exception as e:
            xlsx_errors.append(f"{p.relative_to(package)}:{type(e).__name__}")
    add(checks, "QA-009", "XLSX open", not xlsx_errors, {"opened": xlsx_count, "errors": xlsx_errors}, "zero errors")

    current_html = package / "01_PROJECT_MAP_AND_LEDGER" / "URP4_1_HQ_PROJECT_MAP.html"
    hrefs = re.findall(r'href=["\']([^"\']+)', current_html.read_text(encoding="utf-8"), flags=re.I)
    broken = []
    for href in hrefs:
        if href.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target = (current_html.parent / unquote(href)).resolve()
        if not target.exists():
            broken.append(href)
    add(checks, "QA-010", "current HTML local links", not broken, broken, [])

    forbidden = []
    for p in package.rglob("*"):
        rp = p.relative_to(package).as_posix().lower()
        if any(x in rp for x in ["/__pycache__/", "/.pytest_cache/", "/.ipynb_checkpoints/"]) or p.suffix.lower() in {".pyc", ".pyo", ".ndjson"}:
            forbidden.append(rp)
        if "/quarantine/" in rp or "/a1/" in rp:
            forbidden.append(rp)
    add(checks, "QA-011", "cache/quarantine exclusion", not forbidden, forbidden[:20], [])

    included = package / "10_MANIFEST_SHA256_AND_QA" / "INCLUDED_EXCLUDED_FILE_MANIFEST.csv"
    mismatches = []
    with included.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if row["include_status"] != "included":
                continue
            p = package / row["package_path"]
            if not p.exists() or sha256(p) != row["package_sha256"]:
                mismatches.append(row["package_path"])
    add(checks, "QA-012", "copied-source hash equality", not mismatches, mismatches, [])

    c1qa = json.loads((package / "05_DESCRIPTOR_XREG_GEOMETRY_EVIDENCE" / "STRICT-STEP-026" / "INDEPENDENT_QA.json").read_text(encoding="utf-8"))
    add(checks, "QA-013", "C1 independent evidence replay", c1qa.get("status") == "passed" and sum(bool(v) for v in c1qa.get("checks", {}).values()) == 9, c1qa.get("checks"), "9/9")
    tpqa = json.loads((package / "06_TRAINING_EVIDENCE" / "TRAIN-PARITY-004" / "INDEPENDENT_QA.json").read_text(encoding="utf-8"))
    add(checks, "QA-014", "Training blocker QA", tpqa.get("overall_status") == "PASS" and tpqa.get("passed") == 21 and tpqa.get("total") == 21, [tpqa.get("overall_status"), tpqa.get("passed"), tpqa.get("total")], ["PASS", 21, 21])
    compqa = json.loads((package / "07_COMPRESSION_DATA_AND_PILOT" / "COMP-FACTORY-002" / "INDEPENDENT_QA_SUMMARY.json").read_text(encoding="utf-8"))
    add(checks, "QA-015", "Compression pilot QA", compqa.get("status") == "passed" and compqa.get("checks_passed") == 36, [compqa.get("status"), compqa.get("checks_passed")], ["passed", 36])

    raw_geom = [p for p in package.rglob("*.stl")] + [p for p in package.rglob("*.stp")] + [p for p in package.rglob("*.step")]
    add(checks, "QA-016", "bulk raw geometry excluded", not raw_geom, [str(p.relative_to(package)) for p in raw_geom[:10]], [])
    core_zips = list((package / "02_VERIFIED_CORE_HQ_NB_PY" / "00_IMMUTABLE_V1_0_CORE").glob("URP4-1_HANDOFF-RELEASE-20260731-002.zip"))
    add(checks, "QA-017", "verified v1.0 core included exactly once", len(core_zips) == 1, len(core_zips), 1)
    large_by_hash = {}
    for p in package.rglob("*"):
        if p.is_file() and p.stat().st_size > 1024 * 1024:
            large_by_hash.setdefault(sha256(p), []).append(p.relative_to(package).as_posix())
    large_dupes = {h: paths for h, paths in large_by_hash.items() if len(paths) > 1}
    add(checks, "QA-018", "no duplicate large files", not large_dupes, large_dupes, {})
    overall = "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"
    result = {"qa_id": "SUBMIT-CLOSE-001-INDEPENDENT-CONTENT-QA", "overall_status": overall, "passed": sum(c["status"] == "PASS" for c in checks), "total": len(checks), "checks": checks, "scope": "read-only staging/package-content QA; no research calculation"}
    if write_result:
        out = package / "10_MANIFEST_SHA256_AND_QA" / "INDEPENDENT_CONTENT_QA.json"
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def check_archive(archive: Path) -> dict:
    checks = []
    with zipfile.ZipFile(archive, "r") as z:
        bad = z.testzip()
        names = z.namelist()
        root = names[0].split("/")[0] if names else ""
        manifest_name = f"{root}/10_MANIFEST_SHA256_AND_QA/PACKAGE_CONTENT_SHA256.csv"
        add(checks, "ZIP-001", "ZIP CRC", bad is None, bad, None)
        add(checks, "ZIP-002", "single package root", bool(root) and all(n.startswith(root + "/") for n in names), root, "one root")
        add(checks, "ZIP-003", "content manifest present", manifest_name in names, manifest_name in names, True)
        mismatches = []
        if manifest_name in names:
            rows = list(csv.DictReader(z.read(manifest_name).decode("utf-8-sig").splitlines()))
            for row in rows:
                member = f"{root}/{row['package_path']}"
                if member not in names:
                    mismatches.append(member + ":missing")
                elif hashlib.sha256(z.read(member)).hexdigest() != row["sha256"]:
                    mismatches.append(member + ":hash")
        add(checks, "ZIP-004", "member hashes vs manifest", not mismatches, mismatches[:20], [])
        forbidden = [n for n in names if any(x in n.lower() for x in ["__pycache__", ".pyc", ".ipynb_checkpoints", "/quarantine/", "/a1/"])]
        add(checks, "ZIP-005", "forbidden transient members absent", not forbidden, forbidden[:20], [])
    overall = "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"
    return {"qa_id": "SUBMIT-CLOSE-001-INDEPENDENT-FINAL-ARCHIVE-QA", "overall_status": overall, "passed": sum(c["status"] == "PASS" for c in checks), "total": len(checks), "archive": str(archive), "archive_sha256": sha256(archive), "archive_bytes": archive.stat().st_size, "member_count": len(names), "checks": checks}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--extract-smoke", action="store_true")
    args = ap.parse_args()
    target = Path(args.target).resolve()
    if target.is_dir():
        result = check_tree(target, args.write)
    else:
        archive_result = check_archive(target)
        if args.extract_smoke:
            extract_root = Path(r"C:\URP4H\VERIFY_EXTRACT_PROFESSOR_HANDOFF_20260801_001")
            if extract_root.exists():
                raise SystemExit(f"Refusing overwrite of extraction smoke root: {extract_root}")
            extract_root.mkdir(parents=True)
            with zipfile.ZipFile(target, "r") as z:
                z.extractall(extract_root)
                first = z.namelist()[0].split("/")[0]
            content_result = check_tree(extract_root / first, False)
            result = {
                "qa_id": "SUBMIT-CLOSE-001-EXTRACTED-SMOKE-QA",
                "overall_status": "PASS" if archive_result["overall_status"] == "PASS" and content_result["overall_status"] == "PASS" else "FAIL",
                "archive_qa": archive_result,
                "extracted_content_qa": content_result,
                "extraction_root": str(extract_root),
                "research_calculation": False,
            }
        else:
            result = archive_result
        if args.write:
            out = target.parent / ("EXTRACTED_SMOKE_QA.json" if args.extract_smoke else "INDEPENDENT_PACKAGE_QA.json")
            out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["overall_status"] == "PASS" else 2)


if __name__ == "__main__":
    main()
