from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments/lab_001_xy_connection_20260626"
FACTORY = LAB / "factories/TOUR-C001"
REPORTS = FACTORY / "analysis_factory/reports"
FIGURES = FACTORY / "analysis_factory/figures"
CONTRACT = FACTORY / "contracts/PRM-070_SLICE005_CONVERGENCE_CONTROL_PREREG_20260722.json"
MATRIX = Path(r"C:\Users\chuck\URP4-1_FACTORY\R09_SLICE005_20260721\results\reports\all40_descriptor_scalar_matrix.csv")
DETAIL = REPORTS / "PRM070_SLICE005_model_descriptor_axis_convergence.csv"
DESC = REPORTS / "PRM070_SLICE005_descriptor_axis_summary.csv"
POLICY = REPORTS / "PRM070_SLICE005_descriptor_reference_policy.csv"
SUMMARY = REPORTS / "PRM070_SLICE005_summary.json"
INDEPENDENT = REPORTS / "PRM070_SLICE005_independent_QA.csv"
CONTROL = REPORTS / "PRM070_SLICE005_control_QA.csv"
F005_DIAG = REPORTS / "PRM070_SLICE005_F005_per_mm_post_result_diagnostic.csv"
INDEPENDENT_SUMMARY = REPORTS / "PRM070_SLICE005_independent_control_summary.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def srd(a: float, b: float) -> float:
    denom = abs(a) + abs(b)
    return 0.0 if denom == 0 else 200.0 * abs(a - b) / denom


def write(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    raw = pd.read_csv(MATRIX, keep_default_na=False)
    raw["value"] = pd.to_numeric(raw["value"], errors="raise")
    raw["scalar_key"] = raw["formula_id"] + "::" + raw["statistic"]
    detail = pd.read_csv(DETAIL, keep_default_na=False)
    desc = pd.read_csv(DESC, keep_default_na=False)
    policy = pd.read_csv(POLICY, keep_default_na=False)
    pivot = raw.pivot(index=["model_id", "scalar_key"], columns="config_id", values="value")

    independent_rows: list[dict] = []

    def add(qid: str, check: str, observed, expected, passed: bool) -> None:
        independent_rows.append({"qa_id": qid, "check": check, "observed": observed, "expected": expected, "passed": bool(passed)})

    recomputed: dict[tuple[str, str, str], tuple[float, float]] = {}
    for (model, scalar), row in pivot.iterrows():
        recomputed[(model, scalar, "pixel")] = (
            srd(row["CFG-P0500-S0801"], row["CFG-P1000-S0801"]),
            srd(row["CFG-P2000-S0801"], row["CFG-P1000-S0801"]),
        )
        recomputed[(model, scalar, "slice")] = (
            srd(row["CFG-P1000-S0401"], row["CFG-P1000-S0801"]),
            srd(row["CFG-P1000-S1601"], row["CFG-P1000-S0801"]),
        )
    coarse_delta = []
    fine_delta = []
    for _, row in detail.iterrows():
        expected = recomputed[(row.model_id, row.scalar_key, row.axis)]
        coarse_delta.append(abs(float(row.coarse_to_reference_srd_percent) - expected[0]))
        fine_delta.append(abs(float(row.fine_to_reference_srd_percent) - expected[1]))

    add("I01", "contract hash matrix", sha256(MATRIX), contract["inputs"]["aggregate_matrix"]["sha256"], sha256(MATRIX) == contract["inputs"]["aggregate_matrix"]["sha256"])
    add("I02", "raw rows", len(raw), 360, len(raw) == 360)
    add("I03", "raw unique model-config-scalar", raw[["model_id", "config_id", "scalar_key"]].drop_duplicates().shape[0], 360, raw[["model_id", "config_id", "scalar_key"]].drop_duplicates().shape[0] == 360)
    add("I04", "pivot cells", int(pivot.notna().sum().sum()), 360, int(pivot.notna().sum().sum()) == 360)
    add("I05", "detail rows", len(detail), 144, len(detail) == 144)
    add("I06", "coarse SRD replay max delta", max(coarse_delta), 1e-10, max(coarse_delta) <= 1e-10)
    add("I07", "fine SRD replay max delta", max(fine_delta), 1e-10, max(fine_delta) <= 1e-10)
    add("I08", "descriptor summary rows", len(desc), 18, len(desc) == 18)
    add("I09", "policy rows", len(policy), 9, len(policy) == 9)
    add("I10", "retained descriptors", int(policy.decision.eq("reference_retained_for_descriptor").sum()), 8, int(policy.decision.eq("reference_retained_for_descriptor").sum()) == 8)
    add("I11", "held descriptors", int(policy.decision.eq("reference_hold_for_descriptor").sum()), 1, int(policy.decision.eq("reference_hold_for_descriptor").sum()) == 1)
    held = policy.loc[policy.decision.eq("reference_hold_for_descriptor"), "scalar_key"].tolist()
    add("I12", "held identity", held, ["XRV1-F005::mean"], held == ["XRV1-F005::mean"])
    add("I13", "pixel strict", int(desc.loc[desc.axis.eq("pixel"), "axis_state"].eq("descriptor_axis_strict").sum()), 9, int(desc.loc[desc.axis.eq("pixel"), "axis_state"].eq("descriptor_axis_strict").sum()) == 9)
    add("I14", "slice strict", int(desc.loc[desc.axis.eq("slice"), "axis_state"].eq("descriptor_axis_strict").sum()), 8, int(desc.loc[desc.axis.eq("slice"), "axis_state"].eq("descriptor_axis_strict").sum()) == 8)
    f005 = desc.loc[(desc.scalar_key.eq("XRV1-F005::mean")) & desc.axis.eq("slice")].iloc[0]
    add("I15", "F005 slice median", float(f005.median_fine_srd_percent), 65.4156682015096, abs(float(f005.median_fine_srd_percent) - 65.4156682015096) < 1e-10)
    add("I16", "F005 slice all unconverged", int(f005.unconverged_models), 8, int(f005.unconverged_models) == 8)
    add("I17", "pixel max fine SRD", float(detail.loc[detail.axis.eq("pixel"), "fine_to_reference_srd_percent"].max()), 1.0005262305225908, abs(float(detail.loc[detail.axis.eq("pixel"), "fine_to_reference_srd_percent"].max()) - 1.0005262305225908) < 1e-10)
    add("I18", "L7 >15 alerts", int(((detail.model_id.eq("L7")) & detail.alert_over_15_percent.astype(bool)).sum()), 1, int(((detail.model_id.eq("L7")) & detail.alert_over_15_percent.astype(bool)).sum()) == 1)
    t89 = pd.read_csv(REPORTS / "PRM070_SLICE005_T8_T9_diagnostic.csv", keep_default_na=False)
    add("I19", "T8/T9 order breaks", int((~t89.order_preserved.astype(bool)).sum()), 8, int((~t89.order_preserved.astype(bool)).sum()) == 8)
    break_max = float(t89.loc[~t89.order_preserved.astype(bool), "symmetric_separation_percent"].max())
    add("I20", "T8/T9 break maximum separation", break_max, "<0.1%", break_max < 0.1)
    add("I21", "summary decision", summary["decision"], "retain_reference_for_supported_descriptors_only", summary["decision"] == "retain_reference_for_supported_descriptors_only")
    add("I22", "y read", summary["performance_y_read"], 0, summary["performance_y_read"] == 0)
    add("I23", "model fit", summary["model_fit"], 0, summary["model_fit"] == 0)
    add("I24", "feature promotion", summary["feature_promotion"], 0, summary["feature_promotion"] == 0)

    # Explicitly post-result and exploratory: explain F005's expected finite-difference scaling.
    spacing = {"CFG-P1000-S0401": 0.1, "CFG-P1000-S0801": 0.05, "CFG-P1000-S1601": 0.025}
    f005_raw = raw.loc[(raw.formula_id.eq("XRV1-F005")) & raw.statistic.eq("mean") & raw.config_id.isin(spacing)].copy()
    f005_raw["per_mm_rate"] = f005_raw.value / f005_raw.config_id.map(spacing)
    f005_pivot = f005_raw.pivot(index="model_id", columns="config_id", values="per_mm_rate")
    diagnostic_rows = []
    for model, row in f005_pivot.iterrows():
        diagnostic_rows.append(
            {
                "model_id": model,
                "coarse_rate_per_mm": row["CFG-P1000-S0401"],
                "reference_rate_per_mm": row["CFG-P1000-S0801"],
                "fine_rate_per_mm": row["CFG-P1000-S1601"],
                "coarse_rate_srd_percent": srd(row["CFG-P1000-S0401"], row["CFG-P1000-S0801"]),
                "fine_rate_srd_percent": srd(row["CFG-P1000-S1601"], row["CFG-P1000-S0801"]),
                "post_result_exploratory": True,
                "promotion_allowed": False,
                "engineering_hypothesis": "Raw overlay change fraction scales approximately with slice spacing; divide by delta-z to estimate a per-mm change rate.",
            }
        )
    write(F005_DIAG, diagnostic_rows)
    fine_diag = [row["fine_rate_srd_percent"] for row in diagnostic_rows]

    if not all(row["passed"] for row in independent_rows):
        print(json.dumps([row for row in independent_rows if not row["passed"]], indent=2, ensure_ascii=False))
        raise RuntimeError("PRM070 independent QA failed")
    write(INDEPENDENT, independent_rows)

    figures = [
        FIGURES / "PRM070_SLICE005_fine_SRD_heatmap.png",
        FIGURES / "PRM070_SLICE005_descriptor_convergence_summary.png",
        FIGURES / "PRM070_SLICE005_T8_T9_separation.png",
    ]
    control_rows: list[dict] = []

    def addc(qid: str, check: str, observed, expected, passed: bool) -> None:
        control_rows.append({"qa_id": qid, "check": check, "observed": observed, "expected": expected, "passed": bool(passed)})

    for index, figure in enumerate(figures, start=1):
        with Image.open(figure) as image:
            width, height = image.size
        addc(f"C{index:02d}", f"figure {index} exists", figure.is_file(), True, figure.is_file())
        addc(f"C{index+3:02d}", f"figure {index} dimensions", f"{width}x{height}", ">=1200x600", width >= 1200 and height >= 600)
    addc("C07", "thresholds frozen", contract["status"], "frozen_before_delta_calculation", contract["status"] == "frozen_before_delta_calculation")
    addc("C08", "F005 raw remains held", held, ["XRV1-F005::mean"], held == ["XRV1-F005::mean"])
    addc("C09", "F005 per-mm diagnostic flag", all(row["post_result_exploratory"] for row in diagnostic_rows), True, all(row["post_result_exploratory"] for row in diagnostic_rows))
    addc("C10", "F005 per-mm promotion blocked", all(not row["promotion_allowed"] for row in diagnostic_rows), True, all(not row["promotion_allowed"] for row in diagnostic_rows))
    addc("C11", "F005 per-mm fine median", float(np.median(fine_diag)), "<5% exploratory", float(np.median(fine_diag)) < 5.0)
    addc("C12", "claim boundary", [summary["performance_y_read"], summary["model_fit"], summary["feature_promotion"]], [0, 0, 0], summary["performance_y_read"] == summary["model_fit"] == summary["feature_promotion"] == 0)
    if not all(row["passed"] for row in control_rows):
        raise RuntimeError("PRM070 control QA failed")
    write(CONTROL, control_rows)
    output = {
        "run_id": "PRM070-SLICE005-INDEPENDENT-CONTROL-001",
        "status": "passed_independent_control",
        "independent_QA": "24/24",
        "control_QA": "12/12",
        "decision_confirmed": summary["decision"],
        "F005_raw_status": "hold",
        "F005_per_mm_diagnostic": {
            "status": "post_result_exploratory_no_promotion",
            "median_fine_srd_percent": float(np.median(fine_diag)),
            "max_fine_srd_percent": float(np.max(fine_diag)),
        },
        "T8_T9_order_breaks": 8,
        "T8_T9_break_max_separation_percent": break_max,
        "next_task": "PRM070-CONTROL-TOWER-MERGE",
    }
    INDEPENDENT_SUMMARY.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
