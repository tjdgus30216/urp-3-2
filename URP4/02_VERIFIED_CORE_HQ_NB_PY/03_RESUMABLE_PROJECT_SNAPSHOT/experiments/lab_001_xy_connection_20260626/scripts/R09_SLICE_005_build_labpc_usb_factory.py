from __future__ import annotations

import csv
import hashlib
import json
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments/lab_001_xy_connection_20260626"
SCRIPTS = LAB / "scripts"
TARGET = ROOT / "outputs/URP4-1_R09_SLICE005_LABPC_FACTORY_USB_20260721"
PANEL = LAB / "reports/tables/R09-SLICE-005_representative_panel_20260721.csv"
MATRIX = LAB / "reports/tables/R09-SLICE-005_execution_matrix_20260721.csv"
PRM046 = LAB / "factories/R09-SLICE-005/contracts/R09-SLICE-005_STRICT_CONVERGENCE_PREREGISTRATION_NOEXEC_20260721.json"
PRM049 = LAB / "factories/R09-SLICE-005/contracts/R09-SLICE-005_B3_COARSE_DUPLICATE_CANARY_FINAL_EXECUTION_20260721.json"
CANARY_CONTROL = LAB / "factories/R09-SLICE-005/reports/R09-SLICE-005_B3_coarse_canary_control_summary_20260721.json"
KST = timezone(timedelta(hours=9))


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def main() -> None:
    if TARGET.exists():
        raise FileExistsError(f"refusing to overwrite existing package: {TARGET}")
    TARGET.mkdir(parents=True)
    for folder in ["factory", "config", "contracts", "assets/stl", "baseline", "results", "preflight", "returned_results"]:
        (TARGET / folder).mkdir(parents=True, exist_ok=True)

    script_names = ["common", "doctor", "worker", "runner", "verify", "collect"]
    code_hashes: dict[str, str] = {}
    for name in script_names:
        source = SCRIPTS / f"R09_SLICE_005_labpc_{name}.py"
        destination = TARGET / "factory" / source.name
        copy_file(source, destination)
        code_hashes[name] = sha(destination)

    shutil.copytree(
        ROOT / "urp4",
        TARGET / "urp4",
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )

    panel_rows = read_csv(PANEL)
    sources: dict[str, dict] = {}
    baselines: dict[str, dict] = {}
    for row in panel_rows:
        model_id = row["model_id"]
        source = ROOT / row["source_n40_path"]
        destination = TARGET / "assets/stl" / source.name
        copy_file(source, destination)
        sources[model_id] = {
            "path": destination.relative_to(TARGET).as_posix(),
            "bytes": destination.stat().st_size,
            "sha256": sha(destination),
            "identity_status": row["historical_identity_status"],
        }
        baseline_source = LAB / f"runs/xrv1_s2/all58_20260715/models/{model_id}/a01"
        baseline_target = TARGET / "baseline" / model_id
        for relative in [
            "tables/descriptor_result.csv",
            "qc_summary.json",
            "complete.json",
            "run_config.json",
            "source_manifest.csv",
            "artifact_hash_manifest.csv",
        ]:
            copy_file(baseline_source / relative, baseline_target / relative)
        descriptor = baseline_target / "tables/descriptor_result.csv"
        baselines[model_id] = {
            "descriptor_path": descriptor.relative_to(TARGET).as_posix(),
            "descriptor_sha256": sha(descriptor),
            "qc_path": (baseline_target / "qc_summary.json").relative_to(TARGET).as_posix(),
            "source_run": "RUN-139/R09-RESLICE-003",
            "recompute": False,
        }

    jobs = [row for row in read_csv(MATRIX) if row["status"] == "pending_not_authorized"]
    jobs.sort(key=lambda row: float(row["estimated_runtime_seconds"]))
    fields = ["execution_order"] + list(jobs[0].keys())
    pending_rows = [{"execution_order": index, **row} for index, row in enumerate(jobs, start=1)]
    pending_matrix = TARGET / "config/pending_32_job_matrix.csv"
    write_csv(pending_matrix, fields, pending_rows)
    copy_file(MATRIX, TARGET / "config/original_40_cell_matrix.csv")
    copy_file(PANEL, TARGET / "config/representative_panel.csv")
    copy_file(PRM046, TARGET / "contracts/PRM-046_PARENT_CONVERGENCE_CONTRACT.json")
    copy_file(PRM049, TARGET / "contracts/PRM-049_PARENT_CANARY_CONTRACT.json")
    copy_file(CANARY_CONTROL, TARGET / "contracts/PRM-049_CANARY_CONTROL_SUMMARY.json")

    contract = {
        "contract_version": "R09-SLICE-005-labpc-exec-v0.1",
        "preregistration_id": "PRM-050",
        "parent_preregistration_id": "PRM-049",
        "run_id": "R09-SLICE-005-LABPC-FACTORY-EXEC-001",
        "created_at_kst": datetime.now(KST).isoformat(timespec="seconds"),
        "status": "authorized_conditionally_on_live_doctor",
        "execution_authorized": True,
        "authority": "Chuck requested a USB-ready direct execution package after RUN-194 canary pass",
        "scope": "32 pending convergence cells only; eight RUN-139 baselines are frozen reuse",
        "parent_hashes": {
            "PRM-046": sha(PRM046),
            "PRM-049": sha(PRM049),
            "RUN-194_control": sha(CANARY_CONTROL),
        },
        "job_matrix": {
            "path": pending_matrix.relative_to(TARGET).as_posix(),
            "bytes": pending_matrix.stat().st_size,
            "sha256": sha(pending_matrix),
            "jobs": 32,
            "order": "estimated runtime ascending; scientific evaluation remains order-independent",
        },
        "sources": sources,
        "baselines": baselines,
        "code_hashes": code_hashes,
        "config_constant": {"png_compress_level": 1},
        "max_attempts_per_cell": 2,
        "execution_policy": "sequential one-model-per-process; atomic immutable attempt folders; passed cells skipped on resume",
        "failure_policy": "preserve failed/partial attempt; continue other cells; second invocation may create attempt02; quarantine after two attempts",
        "artifact_policy": "save PNG, reopen/read, freeze primitive tables and hashes, delete transient PNG immediately",
        "resource_gates": {
            "minimum_available_ram_bytes": 12 * 2**30,
            "minimum_free_disk_bytes": 25 * 2**30,
            "per_cell_seconds": 7200,
            "per_cell_peak_rss_bytes": 24 * 2**30,
            "per_cell_output_bytes": 8 * 2**30,
            "factory_hard_seconds": 14 * 3600,
        },
        "scientific_locks": {
            "excel_read": 0,
            "target_read": 0,
            "fit": 0,
            "prediction": 0,
            "feature_selection": 0,
            "feature_promotion": 0,
            "formula_change": 0,
            "source_change": 0,
            "baseline_recompute": 0,
            "all58_reslice": 0,
            "parallel_workers": 0,
        },
        "claim_boundary": "LabPC pass means technical completion only; convergence decisions require control-tower independent analysis",
        "expected_runtime": "5.42 h estimated single worker; 14 h hard start-new-cell ceiling",
    }
    contract_path = TARGET / "contracts/PRM-050_R09-SLICE-005_LABPC_EXECUTION.json"
    contract_path.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    readme = """# URP4-1 R09-SLICE-005 LabPC factory USB packet

This packet runs only the 32 pending pixel/slice convergence cells. It does not rerun the eight RUN-139 baselines and does not access Excel, performance y or modeling.

## On this USB

1. Run `00_DOCTOR_FIRST.cmd`.
2. Run `01_INSTALL_LOCAL_FACTORY.cmd` to copy immutable inputs to the LabPC local user folder.
3. Run `02_RUN_OR_RESUME_FACTORY.cmd`. Expected time is about 5.42 hours; the hard ceiling for starting new cells is 14 hours.
4. If Windows or the job stops, run `02_RUN_OR_RESUME_FACTORY.cmd` again. Passed cells are skipped. A failed cell gets at most one immutable retry.
5. Run `03_VERIFY_RESULTS.cmd`.
6. Run `04_COLLECT_RESULTS_TO_USB.cmd` and bring back the ZIP plus manifest from `returned_results/`.

Do not open or edit STL, contract, matrix or Python files. Do not run multiple workers in parallel. Keep the USB connected only for install and collection; calculation happens in `%USERPROFILE%\\URP4-1_FACTORY\\R09_SLICE005_20260721`.
"""
    (TARGET / "README_FIRST.md").write_text(readme, encoding="utf-8")

    find_python = r"""@echo off
set "KMK312_PY="
if defined KMK312_PYTHON if exist "%KMK312_PYTHON%" set "KMK312_PY=%KMK312_PYTHON%"
for %%P in ("%USERPROFILE%\anaconda3\envs\KMK312\python.exe" "%USERPROFILE%\.conda\envs\KMK312\python.exe" "C:\ProgramData\anaconda3\envs\KMK312\python.exe") do if not defined KMK312_PY if exist "%%~P" set "KMK312_PY=%%~P"
if not defined KMK312_PY (
  echo [FAIL] KMK312 python.exe not found.
  echo Set KMK312_PYTHON to the exact python.exe path and retry.
  exit /b 2
)
"%KMK312_PY%" -c "import sys; assert sys.version_info[:3]==(3,12,12); assert 'KMK312' in sys.executable; print(sys.executable)"
if errorlevel 1 exit /b 3
exit /b 0
"""
    (TARGET / "factory/FIND_KMK312.cmd").write_text(find_python, encoding="utf-8")

    commands = {
        "00_DOCTOR_FIRST.cmd": r"""@echo off
setlocal
call "%~dp0factory\FIND_KMK312.cmd"
if errorlevel 1 goto :fail
"%KMK312_PY%" "%~dp0factory\R09_SLICE_005_labpc_doctor.py"
if errorlevel 1 goto :fail
echo [PASS] USB package and KMK312 preflight passed.
pause
exit /b 0
:fail
echo [FAIL] Doctor failed. Do not run the factory.
pause
exit /b 1
""",
        "01_INSTALL_LOCAL_FACTORY.cmd": r"""@echo off
setlocal
set "DEST=%USERPROFILE%\URP4-1_FACTORY\R09_SLICE005_20260721"
if not exist "%DEST%" mkdir "%DEST%"
robocopy "%~dp0" "%DEST%" /E /COPY:DAT /DCOPY:DAT /R:2 /W:2 /XD results preflight returned_results /XF LOCAL_FACTORY_PATH.txt
set "RC=%ERRORLEVEL%"
if %RC% GEQ 8 goto :fail
>"%~dp0LOCAL_FACTORY_PATH.txt" echo %DEST%
echo [PASS] Installed to %DEST%
pause
exit /b 0
:fail
echo [FAIL] robocopy error %RC%
pause
exit /b %RC%
""",
        "02_RUN_OR_RESUME_FACTORY.cmd": r"""@echo off
setlocal
if not exist "%~dp0LOCAL_FACTORY_PATH.txt" goto :notinstalled
set /p DEST=<"%~dp0LOCAL_FACTORY_PATH.txt"
if not exist "%DEST%\README_FIRST.md" goto :notinstalled
call "%DEST%\factory\FIND_KMK312.cmd"
if errorlevel 1 goto :fail
cd /d "%DEST%"
"%KMK312_PY%" "factory\R09_SLICE_005_labpc_doctor.py" --authorize
if errorlevel 1 goto :fail
"%KMK312_PY%" "factory\R09_SLICE_005_labpc_runner.py"
set "RC=%ERRORLEVEL%"
if %RC% EQU 0 "%KMK312_PY%" "factory\R09_SLICE_005_labpc_verify.py"
echo Factory exit code: %RC%
echo Re-run this same CMD to resume or use 03_CHECK_STATUS.cmd.
pause
exit /b %RC%
:notinstalled
echo [FAIL] Run 01_INSTALL_LOCAL_FACTORY.cmd first.
pause
exit /b 2
:fail
echo [FAIL] Preflight or factory failed closed.
pause
exit /b 1
""",
        "03_CHECK_STATUS_AND_VERIFY.cmd": r"""@echo off
setlocal
if not exist "%~dp0LOCAL_FACTORY_PATH.txt" goto :fail
set /p DEST=<"%~dp0LOCAL_FACTORY_PATH.txt"
call "%DEST%\factory\FIND_KMK312.cmd"
if errorlevel 1 goto :fail
cd /d "%DEST%"
"%KMK312_PY%" "factory\R09_SLICE_005_labpc_runner.py" --status-only
"%KMK312_PY%" "factory\R09_SLICE_005_labpc_verify.py"
pause
exit /b %ERRORLEVEL%
:fail
echo [FAIL] Local installation or KMK312 missing.
pause
exit /b 1
""",
        "04_COLLECT_RESULTS_TO_USB.cmd": r"""@echo off
setlocal
if not exist "%~dp0LOCAL_FACTORY_PATH.txt" goto :fail
set /p DEST=<"%~dp0LOCAL_FACTORY_PATH.txt"
call "%DEST%\factory\FIND_KMK312.cmd"
if errorlevel 1 goto :fail
cd /d "%DEST%"
"%KMK312_PY%" "factory\R09_SLICE_005_labpc_verify.py"
if errorlevel 1 goto :fail
"%KMK312_PY%" "factory\R09_SLICE_005_labpc_collect.py" --destination "%~dp0returned_results"
if errorlevel 1 goto :fail
echo [PASS] Results copied to USB returned_results.
pause
exit /b 0
:fail
echo [FAIL] Collection stopped. Check status and verification first.
pause
exit /b 1
""",
    }
    for name, text in commands.items():
        (TARGET / name).write_text(text, encoding="utf-8")

    immutable_files = [
        path
        for path in TARGET.rglob("*")
        if path.is_file()
        and "results" not in path.relative_to(TARGET).parts
        and "preflight" not in path.relative_to(TARGET).parts
        and "returned_results" not in path.relative_to(TARGET).parts
        and path.name != "PACKAGE_MANIFEST.csv"
        and path.name != "LOCAL_FACTORY_PATH.txt"
    ]
    manifest_rows = [
        {
            "path": path.relative_to(TARGET).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha(path),
        }
        for path in sorted(immutable_files)
    ]
    write_csv(TARGET / "PACKAGE_MANIFEST.csv", ["path", "bytes", "sha256"], manifest_rows)
    summary = {
        "package": TARGET.name,
        "created_at_kst": datetime.now(KST).isoformat(timespec="seconds"),
        "status": "built_pending_QA",
        "immutable_files": len(manifest_rows),
        "package_bytes": sum(path.stat().st_size for path in TARGET.rglob("*") if path.is_file()),
        "source_models": len(sources),
        "frozen_baselines": len(baselines),
        "pending_jobs": len(jobs),
        "contract": "PRM-050",
        "execution_authorized_only_after_live_doctor": True,
    }
    (TARGET / "PACKAGE_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
