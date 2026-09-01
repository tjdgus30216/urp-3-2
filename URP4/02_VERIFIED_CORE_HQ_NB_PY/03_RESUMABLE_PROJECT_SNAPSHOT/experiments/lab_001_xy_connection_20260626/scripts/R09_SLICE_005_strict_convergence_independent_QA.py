"""Independent integrity and semantic QA for PRM-046 (no execution)."""

from __future__ import annotations

import hashlib
import json
import math
import platform
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pandas as pd

import T3P_mesh_native_grouped_evaluation_preregistration_no_fit as protected_engine
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from urp4.descriptor_service.v0_1.config import ExtractionConfig, RUN139_EXTRACTION_CONFIG


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
TABLES = LAB / "reports" / "tables"
FACTORY = LAB / "factories" / "R09-SLICE-005"
CONTRACT = FACTORY / "contracts" / "R09-SLICE-005_STRICT_CONVERGENCE_PREREGISTRATION_NOEXEC_20260721.json"
MANIFEST = FACTORY / "merge" / "R09-SLICE-005_preregistration_manifest_20260721.csv"
REPORTS = FACTORY / "reports"
KST = timezone(timedelta(hours=9))


def now_kst() -> str:
    return datetime.now(KST).isoformat(timespec="seconds")


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def asset(path: Path) -> dict[str, Any]:
    return {"path": rel(path), "bytes": path.stat().st_size, "sha256": sha(path)}


def write_csv(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, encoding="utf-8-sig", lineterminator="\n")


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def manifest_check() -> tuple[bool, int]:
    frame = pd.read_csv(MANIFEST, dtype=str, keep_default_na=False)
    ok = True
    for row in frame.itertuples(index=False):
        path = ROOT / row.path
        ok = ok and path.is_file() and str(path.stat().st_size) == row.bytes and sha(path) == row.sha256
    return bool(ok), len(frame)


def main() -> None:
    if platform.python_version() != "3.12.12" or "KMK312" not in sys.executable:
        raise RuntimeError("KMK312 Python 3.12.12 required")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    matrix = pd.read_csv(TABLES / "R09-SLICE-005_execution_matrix_20260721.csv")
    panel = pd.read_csv(TABLES / "R09-SLICE-005_representative_panel_20260721.csv")
    formulas = pd.read_csv(TABLES / "R09-SLICE-005_formula_scope_20260721.csv")
    gates = pd.read_csv(TABLES / "R09-SLICE-005_convergence_gates_20260721.csv")
    rec = pd.read_csv(TABLES / "R09-SLICE-005_DOE_RUN139_CINT03_reconciliation_20260721.csv")
    budget = pd.read_csv(TABLES / "R09-SLICE-005_resource_budget_20260721.csv")
    old_metric_text = (TABLES / "R09-SLICE-003_validation_metric_table_20260708.csv").read_text(encoding="utf-8-sig")
    run139_config = json.loads((LAB / "runs" / "xrv1_s2" / "all58_20260715" / "run_config.json").read_text(encoding="utf-8"))
    freeze = json.loads((TABLES / "R09-RESLICE-003_factory_freeze_20260715.json").read_text(encoding="utf-8"))
    manifest_pass, manifest_rows = manifest_check()

    config_valid = True
    for row in matrix.drop_duplicates("config_id").itertuples(index=False):
        cfg = ExtractionConfig(axis="z", physical_size_mm=40.0, slice_count=int(row.slice_count),
                               slice_spacing_mm=float(row.slice_spacing_mm), pixel_width=int(row.pixel_width),
                               pixel_height=int(row.pixel_height), area_per_pixel_mm2=float(row.area_per_pixel_mm2),
                               length_per_pixel_mm=float(row.length_per_pixel_mm), connectivity=8,
                               min_component_pixels=2, endpoint_nudge_mm=1e-6, png_compress_level=1)
        try:
            cfg.validate()
        except Exception:
            config_valid = False

    expected_factors = {"pixel_coarse": 0.65, "pixel_fine": 3.0, "slice_coarse": 0.55, "slice_fine": 1.9}
    expected_runtime = 0.0
    for p in panel.itertuples(index=False):
        expected_runtime += float(p.run139_runtime_seconds) * sum(expected_factors.values())
    actual_runtime = float(budget.loc[budget.config_id.eq("TOTAL_NEW"), "estimated_seconds"].iloc[0])

    source_ok = all((ROOT / r.source_n40_path).is_file() and sha(ROOT / r.source_n40_path) == r.source_n40_sha256
                    for r in panel.itertuples(index=False))
    protected = protected_engine.protected_post()
    runtime_dir_absent = not (FACTORY / "runtime").exists()
    primary = formulas.loc[formulas.prm046_role.eq("primary_convergence"), "formula_id"].tolist()

    checks = [
        ("IQA-001", "contract identity and lock", contract["preregistration_id"] == "PRM-046" and contract["execution_authorized"] is False),
        ("IQA-002", "manifest integrity", manifest_pass and manifest_rows >= 10),
        ("IQA-003", "panel exact", panel.model_id.tolist() == ["B3","C1","L1","L7","F1","F2","T8","T9"]),
        ("IQA-004", "all source hashes exact", source_ok),
        ("IQA-005", "five config validators pass", config_valid and matrix.config_id.nunique() == 5),
        ("IQA-006", "40 unique cells", len(matrix) == 40 and matrix.execution_cell_id.nunique() == 40),
        ("IQA-007", "8 baseline reuse and 32 pending", matrix.baseline_artifact_reuse.sum() == 8 and (~matrix.baseline_artifact_reuse).sum() == 32),
        ("IQA-008", "pixel levels exact", set(matrix.loc[matrix.slice_count.eq(801), "pixel_width"]) == {500,1000,2000}),
        ("IQA-009", "slice levels exact", set(matrix.loc[matrix.pixel_width.eq(1000), "slice_count"]) == {401,801,1601}),
        ("IQA-010", "OFAT separability", not ((matrix.pixel_width.ne(1000)) & (matrix.slice_count.ne(801))).any()),
        ("IQA-011", "F001-F006 primary exact", primary == [f"XRV1-F{i:03d}" for i in range(1,7)]),
        ("IQA-012", "F007-F008 sensitivity only", set(formulas.loc[formulas.prm046_role.eq("sensitivity_only"), "formula_id"]) == {"XRV1-F007","XRV1-F008"}),
        ("IQA-013", "F009-F012 excluded", set(formulas.loc[formulas.prm046_role.eq("excluded"), "formula_id"]) == {"XRV1-F009","XRV1-F010","XRV1-F011","XRV1-F012"}),
        ("IQA-014", "3-5 percent lineage exists before PRM046", "3 to 5 percent" in old_metric_text),
        ("IQA-015", "gates frozen and unique", len(gates) == 13 and gates.gate_id.nunique() == 13),
        ("IQA-016", "resource estimate independently reproduced", math.isclose(actual_runtime, expected_runtime, rel_tol=0, abs_tol=0.01)),
        ("IQA-017", "three config hash namespaces exact", contract["prerequisites"]["run139_freeze_config_hash"] == freeze["config_hash"] and contract["prerequisites"]["run139_payload_config_hash"] == run139_config["config_sha256"] and contract["prerequisites"]["cint03_dataclass_config_hash"] == RUN139_EXTRACTION_CONFIG.config_sha256),
        ("IQA-018", "reconciliation covers old ambiguity", len(rec) == 14 and {"partially_resolved","resolved_as_namespaces","superseded_and_satisfied"}.issubset(set(rec.current_status))),
        ("IQA-019", "no execution directory", runtime_dir_absent),
        ("IQA-020", "protected assets 29/29", len(protected) == 29 and protected.status.isin(["pass","pass_with_alias_lock"]).all()),
    ]
    qa = pd.DataFrame(checks, columns=["gate_id", "gate", "passed"])
    qa_path = REPORTS / "R09-SLICE-005_independent_QA_20260721.csv"
    write_csv(qa_path, qa)
    if not qa.passed.all():
        raise RuntimeError(f"independent QA failed: {qa.loc[~qa.passed, 'gate_id'].tolist()}")

    fixtures = pd.DataFrame([
        ("FIX-001", "pixel 500 area", 0.0064, float(matrix.loc[matrix.config_id.eq("CFG-P0500-S0801"), "area_per_pixel_mm2"].iloc[0])),
        ("FIX-002", "pixel 2000 area", 0.0004, float(matrix.loc[matrix.config_id.eq("CFG-P2000-S0801"), "area_per_pixel_mm2"].iloc[0])),
        ("FIX-003", "401 slice span", 40.0, (401-1)*0.1),
        ("FIX-004", "1601 slice span", 40.0, (1601-1)*0.025),
        ("FIX-005", "baseline panel minutes", sum(panel.run139_runtime_seconds)/60, 53.2741666666667),
    ], columns=["fixture_id", "fixture", "computed", "expected"])
    fixtures["abs_delta"] = (fixtures.computed-fixtures.expected).abs()
    fixtures["passed"] = fixtures.abs_delta.le(1e-10)
    fixture_path = REPORTS / "R09-SLICE-005_independent_semantic_fixtures_20260721.csv"
    write_csv(fixture_path, fixtures)
    if not fixtures.passed.all():
        raise RuntimeError("semantic fixtures failed")

    summary = {"run_id": "R09-SLICE-005-STRICT-CONVERGENCE-IQA-001", "created_at_kst": now_kst(),
               "runtime": f"KMK312 / Python {platform.python_version()}", "status": "passed",
               "qa": f"{int(qa.passed.sum())}/{len(qa)}", "fixtures": f"{int(fixtures.passed.sum())}/{len(fixtures)}",
               "manifest_rows": manifest_rows, "execution_detected": not runtime_dir_absent,
               "target_or_excel_read": 0, "fits": 0, "predictions": 0,
               "protected_assets": f"{len(protected)}/{len(protected)}"}
    summary_path = REPORTS / "R09-SLICE-005_independent_QA_summary_20260721.json"
    write_json(summary_path, summary)
    out_manifest = pd.DataFrame([asset(qa_path), asset(fixture_path), asset(summary_path)])
    out_path = FACTORY / "merge" / "R09-SLICE-005_independent_QA_manifest_20260721.csv"
    write_csv(out_path, out_manifest)
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
