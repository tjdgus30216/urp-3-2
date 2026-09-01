"""Freeze PRM-046 for one bounded STRICT resolution-convergence execution.

This script performs no slicing, descriptor calculation, Excel read, target
read, fitting, prediction, feature selection, or source mutation.  It only
reconciles the 2026-07-08 DOE with frozen RUN-139/CINT-03 evidence and writes
the prospective execution contract.
"""

from __future__ import annotations

import ast
import hashlib
import json
import platform
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

import T3P_mesh_native_grouped_evaluation_preregistration_no_fit as protected_engine


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
TABLES = LAB / "reports" / "tables"
RESULTS = LAB / "results"
FACTORY = LAB / "factories" / "R09-SLICE-005"
CONTRACTS = FACTORY / "contracts"
REPORTS = FACTORY / "reports"
FIGURES = FACTORY / "figures"
MERGE = FACTORY / "merge"
KST = timezone(timedelta(hours=9))

PREREG_ID = "PRM-046"
RUN_ID = "R09-SLICE-005-STRICT-CONVERGENCE-PREREG-001"
DATE = "20260721"

DOE_REPORT = RESULTS / "R09-SLICE-003_PIXEL_SIZE_SLICE_SPACING_DOE_PLAN_20260708.md"
DOE_FACTORS = TABLES / "R09-SLICE-003_doe_factor_table_20260708.csv"
DOE_RUNS = TABLES / "R09-SLICE-003_doe_run_matrix_20260708.csv"
DOE_METRICS = TABLES / "R09-SLICE-003_validation_metric_table_20260708.csv"
DOE_GATES = TABLES / "R09-SLICE-003_promotion_gate_table_20260708.csv"
RUN139_FREEZE = TABLES / "R09-RESLICE-003_factory_freeze_20260715.json"
RUN139_SUMMARY = TABLES / "R09-RESLICE-003_summary_20260715.json"
RUN139_FORMULAS = TABLES / "R09-RESLICE-003_formula_registry_20260715.csv"
CINT03_REPORT = RESULTS / "CINT-03_DESCRIPTOR_SERVICE_MODULARIZATION_AND_RUN139_REGRESSION_20260719.md"
CINT03_PARITY = TABLES / "CINT-03_B3_artifact_full_streaming_parity_20260719.csv"
CINT03_LINEAGE = TABLES / "CINT-03_descriptor_service_module_lineage_20260719.csv"
CINT02_PANEL = TABLES / "CINT-02_golden_panel_input_manifest_20260718.csv"
SERVICE_CONFIG = ROOT / "urp4" / "descriptor_service" / "v0_1" / "config.py"

PARENT_INPUTS = [DOE_REPORT, DOE_FACTORS, DOE_RUNS, DOE_METRICS, DOE_GATES,
                 RUN139_FREEZE, RUN139_SUMMARY, RUN139_FORMULAS,
                 CINT03_REPORT, CINT03_PARITY, CINT03_LINEAGE, CINT02_PANEL,
                 SERVICE_CONFIG]


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
    if frame.empty:
        raise RuntimeError(f"refuse empty artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, encoding="utf-8-sig", lineterminator="\n")


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def runtime_guard() -> None:
    if platform.python_version() != "3.12.12" or "KMK312" not in sys.executable:
        raise RuntimeError("KMK312 Python 3.12.12 required")


def reconciliation() -> pd.DataFrame:
    rows = [
        ("REC-001", "source identity", "to_be_locked", "RUN-139 N40 source path and SHA frozen for 58/58", "superseded_and_satisfied", "reuse exact N40 path/hash; no raw/STP substitution"),
        ("REC-002", "physical scale", "measured bbox; 30/40 unresolved", "N40 40x40x40 mm", "superseded_and_satisfied", "freeze 40 mm; no rescaling sweep"),
        ("REC-003", "geometry backend", "STL section candidate", "binary STL + half-open triangle-plane + even-odd fill", "superseded_and_satisfied", "reuse CINT-03 modules unchanged"),
        ("REC-004", "slice axis", "z seed; x/y later", "z canonical", "satisfied_for_current_scope", "z only; axis DOE excluded"),
        ("REC-005", "pixel baseline", "1000x1000", "1000x1000 RUN-139; B3 streaming parity", "satisfied_baseline", "reuse baseline; test 500 and 2000"),
        ("REC-006", "slice baseline", "801 / 0.05 mm", "801 / 0.05 mm RUN-139", "satisfied_baseline", "reuse baseline; test 401/0.1 and 1601/0.025"),
        ("REC-007", "slice origin", "bbox min-max inclusive likely", "40 mm span; endpoint nudge 1e-6 mm", "resolved", "freeze CINT-03 implementation"),
        ("REC-008", "threshold/readback", "alpha/material>0 candidate", "exact material raster and saved-PNG readback", "resolved", "freeze exact readback; no threshold sweep"),
        ("REC-009", "connected component", "CC8 min2", "OpenCV CC8M2", "resolved", "freeze; no component-rule sweep"),
        ("REC-010", "artifact lifecycle", "full images expected", "ARTIFACT-FULL/STREAMING parity; 1601/1601 deleted", "resolved", "STREAMING; retain only deterministic audit images"),
        ("REC-011", "formula scope", "stdev unresolved broadly", "F001-F006 confirmed; F007 provisional; F008 likely; F009-F012 hold", "partially_resolved", "F001-F006 primary; F007-F008 sensitivity; F009-F012 excluded"),
        ("REC-012", "all-family expansion", "blocked before B3 pass", "RUN-139 58/58 complete", "superseded", "do not rerun 58; use bounded 8-model panel"),
        ("REC-013", "config identities", "single unspecified config hash", "RUN-139 freeze=e33b; run payload=eac0; CINT dataclass=ac26", "resolved_as_namespaces", "record all three; never compare them as same serialization"),
        ("REC-014", "Excel similarity", "scale-aware secondary evidence", "RUN-139 comparison exists", "out_of_scope_for_convergence", "no Excel or y access in PRM-046"),
    ]
    return pd.DataFrame(rows, columns=["reconciliation_id", "field", "doe_20260708_state", "canonical_evidence", "current_status", "prm046_action"])


def panel() -> pd.DataFrame:
    manifest = pd.read_csv(CINT02_PANEL, dtype=str, keep_default_na=False)
    wanted = ["B3", "C1", "L1", "L7", "F1", "F2", "T8", "T9"]
    # L7 is not in CINT-02 golden panel, so pull only path/hash from frozen RUN-139
    selected = manifest.loc[manifest.model_id.isin([x for x in wanted if x != "L7"]),
                            ["model_id", "model_family", "model_name", "geometry_path", "geometry_sha256", "model_to_excel_identity_status"]].copy()
    selected = selected.rename(columns={"geometry_path": "source_n40_path", "geometry_sha256": "source_n40_sha256",
                                        "model_to_excel_identity_status": "historical_identity_status"})
    if "source_n40_path" not in selected.columns:
        raise RuntimeError("CINT-02 panel schema drift")
    l7_path = LAB / "data" / "processed" / "n40_all58_20260715" / "stl" / "L7__052431157f__N40.stl"
    l7 = pd.DataFrame([{"model_id": "L7", "model_family": "Truss lattice", "model_name": "3D chiral metamaterial",
                        "source_n40_path": rel(l7_path), "source_n40_sha256": sha(l7_path),
                        "historical_identity_status": "confirmed"}])
    selected = pd.concat([selected, l7], ignore_index=True)
    selected["model_id"] = pd.Categorical(selected.model_id, categories=wanted, ordered=True)
    selected = selected.sort_values("model_id").reset_index(drop=True)
    selected["model_id"] = selected.model_id.astype(str)
    roles = {
        "B3": ("simple_debug_anchor", "primary"),
        "C1": ("cubic_lattice_family", "primary"),
        "L1": ("truss_lattice_family", "primary"),
        "L7": ("complex_chiral_and_historical_outlier", "diagnostic"),
        "F1": ("foam_family_source_likely", "primary_with_provenance_caution"),
        "F2": ("foam_family_source_likely", "primary_with_provenance_caution"),
        "T8": ("tpms_near_collision_pair_A", "diagnostic"),
        "T9": ("tpms_near_collision_pair_B", "diagnostic"),
    }
    selected[["selection_reason", "gate_role"]] = selected.model_id.map(roles).apply(pd.Series)
    runtimes = []
    for mid in wanted:
        qpath = LAB / "runs" / "xrv1_s2" / "all58_20260715" / "models" / mid / "a01" / "qc_summary.json"
        q = json.loads(qpath.read_text(encoding="utf-8"))
        runtimes.append((mid, float(q["runtime_seconds"]), rel(qpath), sha(qpath)))
    rt = pd.DataFrame(runtimes, columns=["model_id", "run139_runtime_seconds", "run139_qc_path", "run139_qc_sha256"])
    selected = selected.merge(rt, on="model_id", validate="one_to_one")
    selected["scientific_use"] = "resolution_convergence_only_no_excel_no_y"
    return selected


def matrix(panel_df: pd.DataFrame) -> pd.DataFrame:
    configs = [
        ("CFG-P0500-S0801", "pixel_coarse", 500, 801, 0.05, 0.0064, 0.08, 0.65, False),
        ("CFG-P1000-S0801", "canonical_reuse", 1000, 801, 0.05, 0.0016, 0.04, 1.00, True),
        ("CFG-P2000-S0801", "pixel_fine", 2000, 801, 0.05, 0.0004, 0.02, 3.00, False),
        ("CFG-P1000-S0401", "slice_coarse", 1000, 401, 0.10, 0.0016, 0.04, 0.55, False),
        ("CFG-P1000-S1601", "slice_fine", 1000, 1601, 0.025, 0.0016, 0.04, 1.90, False),
    ]
    rows = []
    for p in panel_df.itertuples(index=False):
        for cfg, role, px, slices, spacing, area, length, factor, reuse in configs:
            rows.append({
                "execution_cell_id": f"STRICT-CV::{p.model_id}::{cfg}", "model_id": p.model_id,
                "config_id": cfg, "config_role": role, "axis": "z", "physical_size_mm": 40.0,
                "pixel_width": px, "pixel_height": px, "slice_count": slices,
                "slice_spacing_mm": spacing, "area_per_pixel_mm2": area,
                "length_per_pixel_mm": length, "connectivity": 8,
                "min_component_pixels": 2, "endpoint_nudge_mm": 1e-6,
                "backend": "CINT-03 frozen half-open/even-odd/saved-PNG-readback",
                "execution_mode": "FROZEN_REUSE" if reuse else "STREAMING",
                "baseline_artifact_reuse": reuse,
                "estimated_runtime_factor_vs_run139": factor,
                "estimated_runtime_seconds": round(float(p.run139_runtime_seconds) * factor, 3),
                "execution_device": "frozen_RUN139" if reuse else ("Legion5_canary_then_LabPC" if role in {"pixel_coarse", "slice_coarse"} else "LabPC_preferred"),
                "status": "frozen_reuse" if reuse else "pending_not_authorized",
            })
    return pd.DataFrame(rows)


def formula_scope() -> pd.DataFrame:
    source = pd.read_csv(RUN139_FORMULAS, dtype=str, keep_default_na=False)
    rows = []
    for row in source.itertuples(index=False):
        if row.formula_id in {"XRV1-F001", "XRV1-F002", "XRV1-F003", "XRV1-F004", "XRV1-F005", "XRV1-F006"}:
            role, gate = "primary_convergence", True
        else:
            role, gate = "sensitivity_only", False
        rows.append({"formula_id": row.formula_id, "descriptor": row.descriptor,
                     "population_id": row.population_id, "statistic": row.statistic,
                     "unit": row.unit, "run139_state": row.state,
                     "prm046_role": role, "eligible_for_scientific_pass_gate": gate,
                     "boundary": "formula and population unchanged; resolution variables only"})
    for fid, family, reason in [
        ("XRV1-F009", "curvature candidates", "formula/population unresolved"),
        ("XRV1-F010", "angle candidates", "denominator/population unresolved"),
        ("XRV1-F011", "perimeter-to-area", "perimeter convention unresolved"),
        ("XRV1-F012", "MassOri/Curvature stdev", "avg-about-std population unresolved"),
    ]:
        rows.append({"formula_id": fid, "descriptor": family, "population_id": "unresolved",
                     "statistic": "unresolved", "unit": "unresolved", "run139_state": "hold",
                     "prm046_role": "excluded", "eligible_for_scientific_pass_gate": False,
                     "boundary": reason})
    return pd.DataFrame(rows)


def gates() -> pd.DataFrame:
    rows = [
        ("CV-G01", "runtime_and_source_integrity", "hard", "100% KMK312; exact source SHA; config/hash manifest", "technical_pass"),
        ("CV-G02", "image_pixel_traceability", "hard", "100% PNG generated-readback-accounted; zero mismatch; zero untracked PNG", "technical_pass"),
        ("CV-G03", "row_and_formula_completeness", "hard", "8 models x 5 configs x 9 scalar outputs; F001-F008 lineage exact", "technical_pass"),
        ("CV-G04", "deterministic_canary_replay", "hard", "B3 coarse canary repeated; max scalar absolute delta <=1e-12", "technical_pass"),
        ("CV-G05", "fine_increment_median", "scientific", "primary F001-F006 pooled median symmetric relative delta <=0.03 for pixel and slice", "resolution_stable"),
        ("CV-G06", "fine_increment_p90", "scientific", "primary F001-F006 pooled p90 symmetric relative delta <=0.05 for pixel and slice", "resolution_stable"),
        ("CV-G07", "refinement_increment_shrinks", "scientific", "abs(fine-baseline) <= abs(baseline-coarse) in >=80% of primary model-formula cells for each axis", "resolution_stable"),
        ("CV-G08", "rank_stability", "scientific", "Spearman rho baseline versus fine >=0.90 for every primary formula with finite variance", "resolution_stable"),
        ("CV-G09", "family_technical_coverage", "hard", "B/C/L/F/T all represented and no family has zero passing models", "technical_pass"),
        ("CV-G10", "resource_ceiling", "hard", "single-worker wall <=8 h; peak RSS <=16 GiB; scratch <=20 GiB; per-cell <=3 h", "bounded_execution"),
        ("CV-G11", "T8_T9_diagnostic_boundary", "claim", "report pair distance/sign only; never select resolution to maximize separation", "anti_tuning"),
        ("CV-G12", "L7_diagnostic_boundary", "claim", "report convergence only; no Excel outlier repair or source remapping", "anti_tuning"),
        ("CV-G13", "no_auto_promotion", "claim", "passing means resolution-stable candidate, not optimized/canonical/LEGACY-PY identity", "claim_boundary"),
    ]
    return pd.DataFrame(rows, columns=["gate_id", "gate_name", "gate_class", "frozen_rule", "decision_role"])


def resource_budget(matrix_df: pd.DataFrame) -> pd.DataFrame:
    new = matrix_df.loc[~matrix_df.baseline_artifact_reuse]
    by_cfg = new.groupby(["config_id", "config_role"], as_index=False).agg(cells=("execution_cell_id", "size"), estimated_seconds=("estimated_runtime_seconds", "sum"))
    by_cfg["estimated_hours"] = by_cfg.estimated_seconds / 3600
    by_cfg["estimate_status"] = "likely_scaling_from_RUN139_not_benchmark"
    by_cfg["execution_policy"] = "one model per process; atomic checkpoint; fail isolated; no parallel workers until canary memory measured"
    total = pd.DataFrame([{"config_id": "TOTAL_NEW", "config_role": "all_new_variants", "cells": len(new),
                           "estimated_seconds": float(new.estimated_runtime_seconds.sum()),
                           "estimated_hours": float(new.estimated_runtime_seconds.sum()/3600),
                           "estimate_status": "likely_scaling_from_RUN139_not_benchmark",
                           "execution_policy": "hard stop at 8 h single-worker or any resource gate; resume by cell"}])
    return pd.concat([by_cfg, total], ignore_index=True)


def next_queue() -> pd.DataFrame:
    rows = [
        ("SLICE005-Q01", 1, "pending_after_prereg", "control-tower live-hash authorization", "execution remains locked in PRM-046"),
        ("SLICE005-Q02", 2, "pending", "Legion5 B3 pixel-coarse duplicate canary", "measure determinism/runtime/RSS/disk before factory"),
        ("SLICE005-Q03", 3, "pending", "LabPC environment/spec/free-space doctor", "do not infer LabPC budget from Legion5"),
        ("SLICE005-Q04", 4, "pending", "execute 32 new cells with atomic resume", "baseline 8 cells are reused, not recomputed"),
        ("SLICE005-Q05", 5, "pending", "independent convergence calculation and visual QA", "no formula/config choice before QA"),
        ("SLICE005-Q06", 6, "pending", "control merge or quarantine", "pass does not promote descriptors or authorize modeling"),
    ]
    return pd.DataFrame(rows, columns=["queue_id", "order", "status", "action", "boundary"])


def draw_matrix(path: Path) -> None:
    fig, ax = plt.subplots(figsize=(13.5, 6.2))
    ax.axis("off")
    ax.set_xlim(0, 13.5); ax.set_ylim(0, 6.2)
    ax.text(6.75, 5.8, "PRM-046 bounded STRICT convergence design (no execution)", ha="center", fontsize=16, weight="bold")
    models = "8-model panel\nB3 · C1 · L1 · L7\nF1 · F2 · T8 · T9"
    pixel = "Pixel OFAT\n500 → 1000 → 2000\n801 slices fixed"
    slicing = "Slice OFAT\n401 → 801 → 1601\n1000 px fixed"
    gates_text = "Frozen gates\nmedian ≤3% · p90 ≤5%\nshrink ≥80% · ρ ≥0.90"
    for x, label, color in [(0.4, models, "#dbeafe"), (3.7, pixel, "#dcfce7"), (6.8, slicing, "#fef3c7"), (10.0, gates_text, "#f3e8ff")]:
        ax.add_patch(plt.Rectangle((x, 2.25), 2.7, 2.25, fc=color, ec="#334155", lw=1.4))
        ax.text(x+1.35, 3.38, label, ha="center", va="center", fontsize=10.5)
    for x in [3.4, 6.5, 9.7]:
        ax.annotate("", xy=(x+0.25, 3.38), xytext=(x-0.25, 3.38), arrowprops={"arrowstyle": "->", "lw": 1.5})
    ax.text(6.75, 1.35, "Baseline 1000×1000 / 801 / 0.05 mm is hash-reused from RUN-139 — not recalculated", ha="center", fontsize=11, color="#1e3a8a")
    ax.text(6.75, 0.72, "F001–F006 primary · F007–F008 sensitivity · F009–F012 excluded", ha="center", fontsize=11)
    ax.text(6.75, 0.22, "No Excel/y · no fitting · no feature promotion · no optimization claim · T8/T9 and L7 diagnostic only", ha="center", fontsize=10, color="#991b1b")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


def main() -> None:
    runtime_guard()
    for path in PARENT_INPUTS:
        if not path.is_file():
            raise FileNotFoundError(path)
    freeze = json.loads(RUN139_FREEZE.read_text(encoding="utf-8"))
    summary = json.loads(RUN139_SUMMARY.read_text(encoding="utf-8"))
    if freeze["run_id"] != "R09-RESLICE-003" or len(freeze["source_hashes"]) != 58:
        raise RuntimeError("RUN-139 freeze drift")
    descriptor_rows = len(pd.read_csv(TABLES / "R09-RESLICE-003_descriptor_result_20260715.csv"))
    if int(summary["models_passed"]) != 58 or descriptor_rows != 522:
        raise RuntimeError("RUN-139 QA prerequisite not met")
    parity = pd.read_csv(CINT03_PARITY)
    if len(parity) != 4 or not parity.status.eq("passed").all():
        raise RuntimeError("CINT-03 parity prerequisite not met")

    rec = reconciliation()
    pnl = panel()
    mx = matrix(pnl)
    formulas = formula_scope()
    gate_df = gates()
    budget = resource_budget(mx)
    queue = next_queue()

    paths = {
        "reconciliation": TABLES / f"R09-SLICE-005_DOE_RUN139_CINT03_reconciliation_{DATE}.csv",
        "panel": TABLES / f"R09-SLICE-005_representative_panel_{DATE}.csv",
        "matrix": TABLES / f"R09-SLICE-005_execution_matrix_{DATE}.csv",
        "formulas": TABLES / f"R09-SLICE-005_formula_scope_{DATE}.csv",
        "gates": TABLES / f"R09-SLICE-005_convergence_gates_{DATE}.csv",
        "budget": TABLES / f"R09-SLICE-005_resource_budget_{DATE}.csv",
        "queue": TABLES / f"R09-SLICE-005_next_action_queue_{DATE}.csv",
    }
    for key, frame in [("reconciliation", rec), ("panel", pnl), ("matrix", mx), ("formulas", formulas),
                       ("gates", gate_df), ("budget", budget), ("queue", queue)]:
        write_csv(paths[key], frame)

    figure = FIGURES / f"R09-SLICE-005_STRICT_convergence_design_{DATE}.png"
    draw_matrix(figure)

    source_text = Path(__file__).read_text(encoding="utf-8")
    tree = ast.parse(source_text)
    called_names: set[str] = set()
    called_attrs: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                called_names.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                called_attrs.add(node.func.attr)
    negative = pd.DataFrame([
        ("NEG-001", "no target or Excel data input", not any("comparison_to_excel" in rel(p).lower() or p.suffix.lower() in {".xlsx", ".xls"} for p in PARENT_INPUTS)),
        ("NEG-002", "no slicing execution", not ({"run_pipeline", "extract_geometry"} & (called_names | called_attrs))),
        ("NEG-003", "baseline is reused", int(mx.baseline_artifact_reuse.sum()) == 8),
        ("NEG-004", "only 32 new cells", int((~mx.baseline_artifact_reuse).sum()) == 32),
        ("NEG-005", "OFAT only", not ((mx.pixel_width.ne(1000)) & (mx.slice_count.ne(801))).any()),
        ("NEG-006", "F009-F012 excluded", formulas.loc[formulas.formula_id.isin(["XRV1-F009","XRV1-F010","XRV1-F011","XRV1-F012"]), "prm046_role"].eq("excluded").all()),
        ("NEG-007", "T8/T9 diagnostic only", pnl.loc[pnl.model_id.isin(["T8","T9"]), "gate_role"].eq("diagnostic").all()),
        ("NEG-008", "no model fit or prediction", not ({"fit", "predict"} & called_attrs)),
        ("NEG-009", "execution remains unauthorized", mx.loc[~mx.baseline_artifact_reuse, "status"].eq("pending_not_authorized").all()),
        ("NEG-010", "all protected assets unchanged", len(protected_engine.protected_post()) == 29 and protected_engine.protected_post().status.isin(["pass", "pass_with_alias_lock"]).all()),
    ], columns=["test_id", "test", "passed"])
    negative_path = REPORTS / f"R09-SLICE-005_negative_tests_{DATE}.csv"
    write_csv(negative_path, negative)
    if not negative.passed.all():
        raise RuntimeError("negative tests failed")

    protected = protected_engine.protected_post()
    input_verification = pd.DataFrame([{"check": "parent_input", **asset(p), "status": "pass"} for p in PARENT_INPUTS] +
                                      [{"check": "protected_asset", "path": r.path, "bytes": "", "sha256": r.actual,
                                        "status": "pass" if r.status in {"pass", "pass_with_alias_lock"} else "fail"}
                                       for r in protected.itertuples(index=False)])
    input_path = REPORTS / f"R09-SLICE-005_input_verification_{DATE}.csv"
    write_csv(input_path, input_verification)
    if not input_verification.status.eq("pass").all():
        raise RuntimeError("input/protected verification failed")

    contract_path = CONTRACTS / f"R09-SLICE-005_STRICT_CONVERGENCE_PREREGISTRATION_NOEXEC_{DATE}.json"
    payload = {
        "contract_version": "R09-SLICE-005-v0.1", "preregistration_id": PREREG_ID,
        "run_id": RUN_ID, "status": "frozen_no_execution_authority",
        "created_at_kst": now_kst(), "runtime": {"alias": "KMK312", "python": platform.python_version(), "executable": str(Path(sys.executable).resolve())},
        "purpose": "prospectively test pixel and slice resolution convergence under the frozen RUN-139/CINT-03 image-pixel-component pipeline",
        "prerequisites": {"run139_models_passed": 58, "run139_descriptor_rows": 522, "cint03_parity_tables": 4,
                          "run139_freeze_config_hash": freeze["config_hash"],
                          "run139_payload_config_hash": "eac06db6c963adf5e67c9efcc4d871c8469fe01ef45b26941291e5389a69edc3",
                          "cint03_dataclass_config_hash": "ac2672de7b2338e0c820b9cf6711f0aae7ecc7bd62e5b26c5e5450a460e500fc",
                          "hash_namespace_note": "different serialized objects; lineage identities, not equality candidates"},
        "panel": pnl.model_id.tolist(), "families": sorted(pnl.model_family.unique().tolist()),
        "design": {"method": "two independent one-factor-at-a-time three-level sweeps",
                   "baseline": "1000x1000 / 801 / 0.05 mm reused from RUN-139",
                   "pixel_levels": [500, 1000, 2000], "slice_levels": [[401,0.1],[801,0.05],[1601,0.025]],
                   "total_cells": len(mx), "reused_cells": int(mx.baseline_artifact_reuse.sum()), "new_cells": int((~mx.baseline_artifact_reuse).sum())},
        "formula_policy": {"primary": [f"XRV1-F{i:03d}" for i in range(1,7)], "sensitivity": ["XRV1-F007","XRV1-F008"],
                           "excluded": ["XRV1-F009","XRV1-F010","XRV1-F011","XRV1-F012"]},
        "artifact_policy": "STREAMING: generate PNG, reopen/read, freeze primitive tables/hashes, delete transient PNG immediately; retain deterministic audit images",
        "execution_policy": "one model per process, atomic cell checkpoint, isolated failure, resume by cell; baseline never recomputed",
        "execution_device": "Legion5 canary; LabPC preferred for full 32-cell execution",
        "execution_authorized": False,
        "scientific_locks": {"excel_read": 0, "target_read": 0, "fit": 0, "prediction": 0, "feature_selection": 0,
                             "feature_promotion": 0, "formula_change": 0, "source_change": 0, "all58_reslice": 0,
                             "threshold_sweep": 0, "component_rule_sweep": 0, "axis_sweep": 0},
        "pass_semantics": "all technical and scientific gates pass => resolution-stable candidate only; not optimized, canonical, Excel-identical, or LEGACY-PY-identical",
        "failure_semantics": "technical failure => quarantine; scientific failure => keep RUN-139 lineage but mark resolution stability unresolved and diagnose without post-hoc threshold changes",
        "parent_inputs": [asset(p) for p in PARENT_INPUTS],
        "artifacts": [asset(p) for p in paths.values()] + [asset(figure), asset(negative_path), asset(input_path)],
        "future_execution_outputs_required": ["cell manifests", "primitive-table hashes", "descriptor matrix", "convergence metrics", "resource log", "independent replay", "visual QA", "control merge or quarantine"],
    }
    write_json(contract_path, payload)

    qa = pd.DataFrame([
        ("QA-001", "RUN-139 58/58 and 522 rows", int(summary["models_passed"]) == 58 and descriptor_rows == 522),
        ("QA-002", "CINT-03 four-table B3 parity", len(parity) == 4 and parity.status.eq("passed").all()),
        ("QA-003", "8-model panel", len(pnl) == 8 and pnl.model_id.nunique() == 8),
        ("QA-004", "five families represented", set(pnl.model_id.str[0]) == {"B","C","L","F","T"}),
        ("QA-005", "40 total and 32 new cells", len(mx) == 40 and (~mx.baseline_artifact_reuse).sum() == 32),
        ("QA-006", "source paths and SHA exact", all((ROOT / r.source_n40_path).is_file() and sha(ROOT / r.source_n40_path) == r.source_n40_sha256 for r in pnl.itertuples(index=False))),
        ("QA-007", "primary formula identities", formulas.loc[formulas.prm046_role.eq("primary_convergence"), "formula_id"].tolist() == [f"XRV1-F{i:03d}" for i in range(1,7)]),
        ("QA-008", "13 frozen gates", len(gate_df) == 13 and gate_df.gate_id.nunique() == 13),
        ("QA-009", "all negative tests", negative.passed.all()),
        ("QA-010", "execution locked", payload["execution_authorized"] is False),
        ("QA-011", "protected assets 29/29", len(protected) == 29 and protected.status.isin(["pass", "pass_with_alias_lock"]).all()),
        ("QA-012", "no parent artifact modified during generation", all(sha(p) == a["sha256"] for p,a in zip(PARENT_INPUTS,payload["parent_inputs"]))),
    ], columns=["gate_id", "gate", "passed"])
    qa_path = REPORTS / f"R09-SLICE-005_preregistration_QA_{DATE}.csv"
    write_csv(qa_path, qa)
    if not qa.passed.all():
        raise RuntimeError("preregistration QA failed")

    report_path = RESULTS / f"R09-20260721-SLICE-005_STRICT_CONVERGENCE_PREREGISTRATION_NOEXEC.md"
    report = f"""# R09-SLICE-005 — STRICT resolution convergence preregistration (no execution)

Date: 2026-07-21  
Contract: `{PREREG_ID}`  
Runtime: `KMK312 / Python {platform.python_version()}`  
Status: **frozen; execution not authorized**

## Outcome first

The 2026-07-08 DOE is not repeated. RUN-139 and CINT-03 already satisfy source lock,
40 mm normalization, z-axis backend, 1000×1000/801 baseline, exact PNG readback,
CC8M2, streaming deletion, and the full 58-model technical extraction.

One bounded convergence execution is now preregistered:

```text
panel: B3, C1, L1, L7, F1, F2, T8, T9
pixel OFAT: 500 -> 1000 -> 2000 at 801 slices
slice OFAT: 401 -> 801 -> 1601 at 1000 pixels
baseline reuse: 8 cells
new execution: 32 cells
formula gates: F001-F006
sensitivity only: F007-F008
excluded: F009-F012
```

## Why these eight models

- `B3`: simple debug anchor.
- `C1`, `L1`: distinct lattice families.
- `F1`, `F2`: complete Foam coverage, with historical-source caution retained.
- `T8`, `T9`: near-collision pair; diagnostic only, never a tuning target.
- `L7`: complex chiral geometry and historical outlier; convergence diagnostic only.

This covers all B/C/L/F/T divisions without repeating 58-model extraction.

## Frozen scientific test

For each primary formula, use the middle resolution as the reference and compare
both coarse and fine increments. Symmetric relative delta is used for aggregate
stability; absolute increments are used for the refinement-shrink test.

Required scientific gates:

1. fine-to-baseline median symmetric relative delta `<= 3%` for pixel and slice,
2. fine-to-baseline p90 `<= 5%`,
3. fine increment no larger than coarse increment in `>= 80%` of cells,
4. baseline-to-fine model ranking Spearman `>= 0.90` for every nonconstant F001-F006.

The 3–5% band inherits the original R09-SLICE-003 review rule and is frozen before
new values exist. Passing means only **resolution-stable candidate**. It does not
mean optimized, canonical, Excel-identical, or LEGACY-PY-identical.

## Resource boundary

RUN-139 measured baseline runtime for the eight models is
`{pnl.run139_runtime_seconds.sum()/60:.2f} min`. Conservative scaling estimates
the 32 new cells at `{mx.loc[~mx.baseline_artifact_reuse, 'estimated_runtime_seconds'].sum()/3600:.2f} h`
single-worker. This is a planning estimate, not a benchmark.

Hard limits are 8 h single-worker total, 3 h per cell, 16 GiB peak RSS and 20 GiB
scratch. Run a duplicated B3 coarse canary on Legion5 first; use LabPC for the full
factory. Every cell is atomic and resumable.

## Claim and mutation locks

No Excel, performance y, fitting, prediction, feature selection, descriptor
promotion, formula change, source change, all-58 reslicing, threshold sweep,
component-rule sweep or axis sweep is authorized. Transient PNGs must be read back
then deleted; primitive tables and hashes remain.

## Evidence

- Contract: `{rel(contract_path)}`
- Reconciliation: `{rel(paths['reconciliation'])}`
- Panel: `{rel(paths['panel'])}`
- Execution matrix: `{rel(paths['matrix'])}`
- Formula scope: `{rel(paths['formulas'])}`
- Gates: `{rel(paths['gates'])}`
- Resource budget: `{rel(paths['budget'])}`
- Queue: `{rel(paths['queue'])}`
- Figure: `{rel(figure)}`
- QA: `{rel(qa_path)}`

## Next authorized action

Only independent preregistration QA and control review are authorized now. Actual
slicing requires a separate live-hash authorization after the control packet.
"""
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")

    outputs = list(paths.values()) + [figure, negative_path, input_path, contract_path, qa_path, report_path]
    manifest = pd.DataFrame([asset(p) for p in outputs])
    manifest_path = MERGE / f"R09-SLICE-005_preregistration_manifest_{DATE}.csv"
    write_csv(manifest_path, manifest)
    print(json.dumps({"status": "passed", "preregistration_id": PREREG_ID, "models": len(pnl),
                      "cells": len(mx), "new_cells": int((~mx.baseline_artifact_reuse).sum()),
                      "qa": f"{int(qa.passed.sum())}/{len(qa)}", "negative": f"{int(negative.passed.sum())}/{len(negative)}",
                      "execution_authorized": False, "manifest": rel(manifest_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
