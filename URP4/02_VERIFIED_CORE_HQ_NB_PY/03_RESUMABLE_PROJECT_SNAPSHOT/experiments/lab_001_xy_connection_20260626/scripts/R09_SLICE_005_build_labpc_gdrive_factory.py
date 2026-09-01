from __future__ import annotations

"""Build a Google-Drive delivery copy of the already QA'd LabPC factory.

This is transport-only: execution remains on the LabPC local disk.  It never
changes the USB packet, the scientific contract, or protected project assets.
"""

import csv
import hashlib
import json
import os
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "outputs/URP4-1_R09_SLICE005_LABPC_FACTORY_USB_20260721"
DEFAULT_TARGET = "URP4-1_R09_SLICE005_LABPC_FACTORY_GDRIVE_20260721"
KST = timezone(timedelta(hours=9))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_manifest(target: Path) -> int:
    files = [
        path
        for path in target.rglob("*")
        if path.is_file()
        and not {"results", "preflight", "returned_results"}.intersection(path.relative_to(target).parts)
        and path.name not in {"PACKAGE_MANIFEST.csv", "LOCAL_FACTORY_PATH.txt"}
    ]
    with (target / "PACKAGE_MANIFEST.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["path", "bytes", "sha256"])
        writer.writeheader()
        for path in sorted(files):
            writer.writerow(
                {
                    "path": path.relative_to(target).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
            )
    return len(files)


def main() -> None:
    target_name = os.environ.get("URP4_GDRIVE_FACTORY_NAME", DEFAULT_TARGET)
    target = ROOT / "outputs" / target_name
    if not SOURCE.is_dir():
        raise FileNotFoundError(f"source package missing: {SOURCE}")
    if target.exists():
        raise FileExistsError(f"refusing to overwrite: {target}")

    shutil.copytree(SOURCE, target, ignore=shutil.ignore_patterns("LOCAL_FACTORY_PATH.txt"))
    for folder in ["preflight", "results", "returned_results"]:
        destination = target / folder
        if destination.exists():
            shutil.rmtree(destination)
        destination.mkdir(parents=True)

    (target / "config/google_drive_return_route.json").write_text(
        json.dumps(
            {
                "route_id": "GDRIVE-R09-SLICE005-v0.1",
                "destination": r"G:\내 드라이브\labfactory\returned_results",
                "minimum_free_bytes": 10 * 2**30,
                "purpose": "Verified LabPC results ZIP and manifest only. Calculation remains local.",
                "scientific_scope_changed": False,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    wrapper = r'''from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    route_path = ROOT / "config/google_drive_return_route.json"
    route = json.loads(route_path.read_text(encoding="utf-8"))
    destination = Path(route["destination"])
    anchor = Path(destination.anchor)
    if not anchor.exists():
        raise RuntimeError(f"Google Drive mapping unavailable: {anchor}")
    destination.mkdir(parents=True, exist_ok=True)
    free = shutil.disk_usage(anchor).free
    required = int(route["minimum_free_bytes"])
    if free < required:
        raise RuntimeError(f"Google Drive free space {free} < required {required} bytes")
    command = [sys.executable, str(ROOT / "factory/R09_SLICE_005_labpc_collect.py"), "--destination", str(destination)]
    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
'''
    (target / "factory/R09_SLICE_005_labpc_collect_to_gdrive.py").write_text(wrapper, encoding="utf-8")

    (target / "04_COLLECT_RESULTS_TO_GOOGLE_DRIVE.cmd").write_text(
        r'''@echo off
setlocal
if not exist "%~dp0LOCAL_FACTORY_PATH.txt" goto :fail
set /p DEST=<"%~dp0LOCAL_FACTORY_PATH.txt"
call "%DEST%\factory\FIND_KMK312.cmd"
if errorlevel 1 goto :fail
cd /d "%DEST%"
"%KMK312_PY%" "factory\R09_SLICE_005_labpc_verify.py"
if errorlevel 1 goto :fail
"%KMK312_PY%" "factory\R09_SLICE_005_labpc_collect_to_gdrive.py"
if errorlevel 1 goto :fail
echo [PASS] Verified results ZIP and manifest copied to Google Drive.
pause
exit /b 0
:fail
echo [FAIL] Collection stopped. Check Google Drive mapping, space, and verification.
pause
exit /b 1
''',
        encoding="utf-8",
    )
    obsolete = target / "04_COLLECT_RESULTS_TO_USB.cmd"
    if obsolete.exists():
        obsolete.unlink()

    (target / "README_FIRST.md").write_text(
        """# URP4-1 R09-SLICE-005 LabPC factory — Google Drive packet

This packet runs only the 32 pending pixel/slice convergence cells. It reuses the eight frozen RUN-139 baselines and does not access Excel, performance y, or modeling.

## Required computer setup

- The LabPC must have the exact `KMK312` environment.
- Google Drive must be mounted as `G:` and have `G:\\내 드라이브` available.
- Calculation happens on the LabPC local disk, not in Google Drive.
- Keep at least 10 GiB free on Google Drive before collection.

## Run in this order

1. Run `00_DOCTOR_FIRST.cmd`.
2. Run `01_INSTALL_LOCAL_FACTORY.cmd`; it copies the immutable package to `%USERPROFILE%\\URP4-1_FACTORY\\R09_SLICE005_20260721`.
3. Run `02_RUN_OR_RESUME_FACTORY.cmd`. Expected duration is about 5.42 h; the hard ceiling for starting new cells is 14 h.
4. If interrupted, run `02_RUN_OR_RESUME_FACTORY.cmd` again. Passed cells are skipped; a failed cell gets at most one immutable retry.
5. Run `03_CHECK_STATUS_AND_VERIFY.cmd`.
6. Run `04_COLLECT_RESULTS_TO_GOOGLE_DRIVE.cmd`. It writes only a verified result ZIP and manifest to `G:\\내 드라이브\\labfactory\\returned_results`.

Do not edit STL, contract, matrix, or Python files. Do not run workers in parallel. The Google Drive route is delivery-only and changes no scientific setting.
""",
        encoding="utf-8",
    )
    immutable_files = write_manifest(target)
    summary = {
        "package": target.name,
        "source_package": SOURCE.name,
        "created_at_kst": datetime.now(KST).isoformat(timespec="seconds"),
        "status": "built_pending_drive_copy_QA",
        "transport": "Google Drive delivery only; compute remains local",
        "return_destination": r"G:\내 드라이브\labfactory\returned_results",
        "immutable_files": immutable_files,
        "scientific_contract": "PRM-050 unchanged",
        "pending_jobs": 32,
    }
    (target / "PACKAGE_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Summary itself is immutable too, so refresh once more with its final bytes.
    summary["immutable_files"] = write_manifest(target)
    (target / "PACKAGE_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_manifest(target)
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
