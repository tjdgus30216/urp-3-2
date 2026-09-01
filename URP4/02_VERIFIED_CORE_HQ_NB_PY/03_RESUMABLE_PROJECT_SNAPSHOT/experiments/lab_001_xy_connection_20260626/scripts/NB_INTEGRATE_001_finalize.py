"""Finalize NB-INTEGRATE-001 documentation only after all QA passes."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
CANONICAL_KMK = ROOT / "tools" / "envs" / "KMK312" / "python.exe"
RUN = LAB / "results" / "NB-INTEGRATE-001" / "NB-INTEGRATE-001-20260729-001"
FACTORY = LAB / "factories" / "NB-INTEGRATE-001"
POLICY_RUN = LAB / "results" / "ROUTE-VALID-004" / "ROUTE-VALID-004-20260729-001"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    if Path(sys.executable).resolve() != CANONICAL_KMK.resolve():
        raise RuntimeError("canonical KMK312 required")
    independent = json.loads((RUN / "INDEPENDENT_QA.json").read_text(encoding="utf-8"))
    notebook_qa = json.loads((RUN / "NOTEBOOK_STATIC_QA.json").read_text(encoding="utf-8"))
    if independent["status"] != "passed" or notebook_qa["status"] != "passed":
        raise RuntimeError("refusing to finalize before QA passes")
    manifest = json.loads((FACTORY / "outputs" / "NB-INTEGRATE-001_F1_PREFLIGHT_MANIFEST.json").read_text(encoding="utf-8"))
    report = f'''# NB-INTEGRATE-001 — versioned development import route controller

- Run: `NB-INTEGRATE-001-20260729-001`
- Index: `RUN-361 / DEC-366 / CHG-351 / LAB-CHG-320 / R09-BB-1321..1323`
- Runtime: `KMK312` — `{manifest["runtime"]["sys_executable"]}` / Python `{manifest["runtime"]["python_version"]}`
- Scope: source-policy controller, fixture tests, status-only notebook and manifests. No slicing, descriptor extraction, y, model fit, prediction or source mutation.

## Delivered development integration

1. New module `urp4.route_policy.v0_1` implements ROUTE-VALID-004 as a strict preflight controller.
2. New notebook `NB-DEV v0.6` is a four-cell status/preflight notebook, with `RUN_PREFLIGHT=False` by default. It is neither NB-CURRENT nor a replacement for it.
3. A real hash-bound F1 raw STL preflight chooses development Route C and carries the mandatory `{manifest["decision"]["warning_flags"][0]}` warning.
4. Every manifest records source SHA, policy SHA, config SHA, `sys.executable`, Python version, environment path and actual command.

## Fail-closed implementation

| Input condition | Controller result |
|---|---|
| paired-confirmed imported STL + exact SHA + approved config | development preflight approved; `execution_enabled=false` |
| F1 | same, plus persistent `F1_Z400_UNRESOLVED` |
| paired-likely, STL-only, orientation-held or hash mismatch | rejected before route dispatch |
| repair/hole-fill/proxy STEP setting | rejected |
| production request | rejected |

Route A/B/C science is not reimplemented here. Route C is referenced only as `IMP-STL-ORIENTED-NONZERO-DEVELOPMENT-ROUTE-C`; an additional scientific gate is necessary before any actual route execution.

## QA

- Controller fixture regression: `9/9 PASS`.
- Independent controller/notebook/hash regression: `{independent["qa"]} PASS`; protected assets `{independent["protected_assets"]}` unchanged.
- Independent notebook static QA: `{notebook_qa["qa"]} PASS`.
- F1 real-source preflight: source SHA matches ROUTE-VALID-003; warning propagates; all geometry/slice/descriptor/y/model execution fields are false.

## Runtime discovery correction

The canonical environment is the project-local KMK312 runtime shown above. The interrupted duplicate directory `C:\\Users\\chuck\\anaconda3\\envs\\KMK312` is marked noncanonical/partial and is not used. This correction does not alter or invalidate prior SLICE/R09 scientific outputs.

## Merge recommendation

**CONDITIONAL YES — versioned development scope only.** Merge this new module, new NB-DEV v0.6, contracts/fixtures/QA and documentation as an additive development integration. Do not modify or replace NB-CURRENT, NB-ORIG or LEGACY-PY. Keep scientific production qualification closed and retain `STRICT-F1-001` as a deferred resource-bound task.
'''
    (RUN / "REPORT.md").write_text(report, encoding="utf-8")
    packet = '''# NB-INTEGRATE-001 merge packet

## Recommendation

**CONDITIONAL YES — additive versioned development integration only.**

## Merge scope

- Add `urp4.route_policy.v0_1` controller package.
- Add `NB_DEV_v0_6_ROUTE_VALID_004_IMPORT_POLICY.ipynb`.
- Add controller smoke/fixture/independent QA scripts and hash-addressed manifests.
- Synchronize logs only after QA.

## Not merged / not changed

- NB-CURRENT, NB-ORIG, LEGACY-PY, original STEP/STL, original Excel.
- No slicer execution, descriptor extraction, y, feature selection, Training or production release.

## Evidence

- ROUTE-VALID-004 policy QA is accepted.
- F1 preflight records the expected raw source SHA and `F1_Z400_UNRESOLVED`.
- Controller tests `9/9`, independent QA `13/13`, notebook static QA `8/8`, protected audit `31/31` pass.

## Remaining lock

`STRICT-F1-001_EXACT_A_LONG_RUN_AND_DECLARED_DEFLECTION_SENSITIVITY_NO_Y` is still required for later scientific F1 qualification, not for this development integration.
'''
    (RUN / "MERGE_PACKET.md").write_text(packet, encoding="utf-8")
    correction = '''# Runtime path discovery correction

- Incorrect discovery statement: KMK312 was thought absent because only user-profile Anaconda paths were searched.
- Correct canonical runtime: `tools/envs/KMK312/python.exe` inside the URP4-1 project.
- Verified version: Python 3.12.12 packaged by Anaconda.
- The partial duplicate under `C:\\Users\\chuck\\anaconda3\\envs\\KMK312` is quarantined and never selected.
- No previous KMK312 execution, scientific evidence or result was changed or invalidated.
'''
    (RUN / "RUNTIME_PATH_DISCOVERY_CORRECTION.md").write_text(correction, encoding="utf-8")
    artifacts = [
        ROOT / "URP4-1_DELIVERABLE" / "urp4" / "route_policy" / "__init__.py",
        ROOT / "URP4-1_DELIVERABLE" / "urp4" / "route_policy" / "v0_1" / "__init__.py",
        ROOT / "URP4-1_DELIVERABLE" / "urp4" / "route_policy" / "v0_1" / "models.py",
        ROOT / "URP4-1_DELIVERABLE" / "urp4" / "route_policy" / "v0_1" / "controller.py",
        LAB / "notebooks" / "NB_DEV_v0_6_ROUTE_VALID_004_IMPORT_POLICY.ipynb",
        LAB / "scripts" / "NB_INTEGRATE_001_build_development_notebook.py",
        LAB / "scripts" / "NB_INTEGRATE_001_controller_smoke.py",
        LAB / "scripts" / "test_NB_INTEGRATE_001_route_policy.py",
        LAB / "scripts" / "NB_INTEGRATE_001_independent_regression_qa.py",
        LAB / "scripts" / "NB_INTEGRATE_001_notebook_static_qa.py",
        LAB / "scripts" / "NB_INTEGRATE_001_finalize.py",
        FACTORY / "contracts" / "NB-INTEGRATE-001_CONTRACT.json",
        FACTORY / "outputs" / "NB-INTEGRATE-001_F1_PREFLIGHT_MANIFEST.json",
        FACTORY / "outputs" / "NB-INTEGRATE-001_CONTROLLER_SMOKE.json",
        RUN / "INDEPENDENT_QA.json", RUN / "INDEPENDENT_QA.csv", RUN / "PROTECTED_ASSET_RECHECK.csv", RUN / "NOTEBOOK_STATIC_QA.json", RUN / "FIXTURE_TEST_OUTPUT.txt", RUN / "REPORT.md", RUN / "MERGE_PACKET.md", RUN / "RUNTIME_PATH_DISCOVERY_CORRECTION.md",
    ]
    rows = [{"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": sha256(path)} for path in artifacts]
    with (RUN / "OUTPUT_MANIFEST.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    print(json.dumps({"status": "passed", "artifact_count": len(rows), "manifest": str(RUN / "OUTPUT_MANIFEST.csv")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
