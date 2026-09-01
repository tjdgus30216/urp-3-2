"""Independent static QA for the new development-only NB-DEV v0.6."""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
CANONICAL_KMK = ROOT / "tools" / "envs" / "KMK312" / "python.exe"
NB = LAB / "notebooks" / "NB_DEV_v0_6_ROUTE_VALID_004_IMPORT_POLICY.ipynb"
OUT = LAB / "results" / "NB-INTEGRATE-001" / "NB-INTEGRATE-001-20260729-001" / "NOTEBOOK_STATIC_QA.json"


def main() -> None:
    if Path(sys.executable).resolve() != CANONICAL_KMK.resolve():
        raise RuntimeError("canonical KMK312 required")
    nb = json.loads(NB.read_text(encoding="utf-8"))
    code = ["".join(cell["source"]) for cell in nb["cells"] if cell["cell_type"] == "code"]
    source = "\n".join(code)
    whole_notebook_source = "\n".join("".join(cell["source"]) for cell in nb["cells"])
    syntax_ok = True
    try:
        for text in code:
            ast.parse(text)
    except SyntaxError:
        syntax_ok = False
    checks = {
        "kernel_is_kmk312": nb["metadata"]["kernelspec"]["display_name"] == "KMK312",
        "four_semantic_cells": [cell["metadata"]["semantic_id"] for cell in nb["cells"]] == ["NBDEV6-CELL-00", "NBDEV6-CELL-01", "NBDEV6-CELL-02", "NBDEV6-CELL-03"],
        "code_syntax": syntax_ok,
        "preflight_default_off": "RUN_PREFLIGHT = False" in source,
        "no_slice_executor": "imported_stl_mask_stream" not in source and "extract_imported_stl" not in source,
        "no_y_or_training": "target_y" not in source and "fit(" not in source and "predict(" not in source,
        "f1_warning_is_documented": "F1_Z400_UNRESOLVED" in whole_notebook_source,
        "no_code_cell_has_execution_output": all(cell.get("execution_count") is None and not cell.get("outputs") for cell in nb["cells"] if cell["cell_type"] == "code"),
    }
    payload = {"status": "passed" if all(checks.values()) else "failed", "qa": f"{sum(checks.values())}/{len(checks)}", "checks": checks, "runtime": sys.executable}
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if payload["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
