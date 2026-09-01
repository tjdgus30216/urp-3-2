from __future__ import annotations

import csv
import hashlib
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments/lab_001_xy_connection_20260626"
FACTORY = LAB / "factories/TOUR-C001"
REPORTS = FACTORY / "analysis_factory/reports"
FIGURES = FACTORY / "analysis_factory/figures"
RESULTS = LAB / "results"
CONTRACT_PATH = FACTORY / "contracts/PRM-070_SLICE005_CONVERGENCE_CONTROL_PREREG_20260722.json"
KST = timezone(timedelta(hours=9))

MODEL_AXIS = REPORTS / "PRM070_SLICE005_model_descriptor_axis_convergence.csv"
DESCRIPTOR_AXIS = REPORTS / "PRM070_SLICE005_descriptor_axis_summary.csv"
DESCRIPTOR_POLICY = REPORTS / "PRM070_SLICE005_descriptor_reference_policy.csv"
CONFIG_SUMMARY = REPORTS / "PRM070_SLICE005_configuration_summary.csv"
MODEL_SUMMARY = REPORTS / "PRM070_SLICE005_model_risk_summary.csv"
T89 = REPORTS / "PRM070_SLICE005_T8_T9_diagnostic.csv"
L7 = REPORTS / "PRM070_SLICE005_L7_diagnostic.csv"
RUNTIME = REPORTS / "PRM070_SLICE005_runtime_cost_summary.csv"
QA = REPORTS / "PRM070_SLICE005_producer_QA.csv"
SUMMARY = REPORTS / "PRM070_SLICE005_summary.json"
FIG_HEAT = FIGURES / "PRM070_SLICE005_fine_SRD_heatmap.png"
FIG_DESC = FIGURES / "PRM070_SLICE005_descriptor_convergence_summary.png"
FIG_T89 = FIGURES / "PRM070_SLICE005_T8_T9_separation.png"
REPORT = RESULTS / "R09-20260722-PRM070_SLICE005_CONVERGENCE_CONTROL_REVIEW.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def srd(a: float, b: float) -> float:
    denom = abs(a) + abs(b)
    return 0.0 if denom == 0 else 200.0 * abs(a - b) / denom


def q90(values: pd.Series) -> float:
    return float(np.quantile(values.to_numpy(dtype=float), 0.9, method="linear"))


def scalar_key(row: pd.Series) -> str:
    return f"{row['formula_id']}::{row['statistic']}"


def short_label(key: str) -> str:
    return key.replace("XRV1-", "").replace("::std_pop_ddof0", " std").replace("::mean", "")


def write_csv(path: Path, frame: pd.DataFrame) -> None:
    frame.to_csv(path, index=False, encoding="utf-8-sig")


def main() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    matrix_path = Path(contract["inputs"]["aggregate_matrix"]["path"])
    job_path = Path(contract["inputs"]["job_matrix"]["path"])
    zip_path = Path(contract["inputs"]["return_zip"]["path"])
    if sha256(matrix_path) != contract["inputs"]["aggregate_matrix"]["sha256"]:
        raise RuntimeError("Aggregate matrix hash drift")
    if sha256(job_path) != contract["inputs"]["job_matrix"]["sha256"]:
        raise RuntimeError("Job matrix hash drift")
    if sha256(zip_path) != contract["inputs"]["return_zip"]["sha256"]:
        raise RuntimeError("Return ZIP hash drift")

    matrix = pd.read_csv(matrix_path, keep_default_na=False)
    matrix["value"] = pd.to_numeric(matrix["value"], errors="raise")
    matrix["scalar_key"] = matrix.apply(scalar_key, axis=1)
    matrix["scalar_label"] = matrix["scalar_key"].map(short_label)
    models = contract["panel"]["models"]
    expected_configs = [
        contract["pixel_axis"]["coarse"],
        contract["pixel_axis"]["reference"],
        contract["pixel_axis"]["fine"],
        contract["slice_axis"]["coarse"],
        contract["slice_axis"]["fine"],
    ]
    scalar_keys = sorted(matrix["scalar_key"].unique())
    if len(scalar_keys) != 9:
        raise RuntimeError(f"Expected 9 scalar keys, got {len(scalar_keys)}")
    pivot = matrix.pivot(index=["model_id", "scalar_key", "scalar_label", "descriptor", "statistic", "unit"], columns="config_id", values="value").reset_index()
    missing_configs = set(expected_configs) - set(pivot.columns)
    if missing_configs:
        raise RuntimeError(f"Missing configs: {missing_configs}")

    thresholds = contract["thresholds"]
    axis_specs = {"pixel": contract["pixel_axis"], "slice": contract["slice_axis"]}
    detail_rows: list[dict] = []
    for _, row in pivot.iterrows():
        for axis, spec in axis_specs.items():
            coarse = float(row[spec["coarse"]])
            reference = float(row[spec["reference"]])
            fine = float(row[spec["fine"]])
            coarse_srd = srd(coarse, reference)
            fine_srd = srd(fine, reference)
            trend_pass = fine_srd <= coarse_srd + thresholds["trend_tolerance_percentage_points"]
            if fine_srd <= thresholds["model_descriptor_strict_srd_percent"] and trend_pass:
                state = "strict_converged"
            elif fine_srd <= thresholds["model_descriptor_usable_srd_percent"] and trend_pass:
                state = "usable_sensitivity"
            elif fine_srd <= thresholds["model_descriptor_usable_srd_percent"]:
                state = "nonmonotonic"
            else:
                state = "unconverged"
            detail_rows.append(
                {
                    "model_id": row["model_id"],
                    "model_family": row["model_id"][0],
                    "source_identity_status": "confirmed" if row["model_id"] in contract["panel"]["identity_risk"]["confirmed"] else "likely",
                    "scalar_key": row["scalar_key"],
                    "scalar_label": row["scalar_label"],
                    "descriptor": row["descriptor"],
                    "statistic": row["statistic"],
                    "unit": row["unit"],
                    "axis": axis,
                    "coarse_config": spec["coarse"],
                    "reference_config": spec["reference"],
                    "fine_config": spec["fine"],
                    "coarse_value": coarse,
                    "reference_value": reference,
                    "fine_value": fine,
                    "coarse_to_reference_srd_percent": coarse_srd,
                    "fine_to_reference_srd_percent": fine_srd,
                    "refinement_step_ratio": fine_srd / coarse_srd if coarse_srd > 0 else (0.0 if fine_srd == 0 else math.inf),
                    "trend_pass": trend_pass,
                    "convergence_state": state,
                    "alert_over_15_percent": fine_srd > thresholds["model_alert_srd_percent"],
                }
            )
    detail = pd.DataFrame(detail_rows)
    write_csv(MODEL_AXIS, detail)

    summary_rows: list[dict] = []
    for (scalar, axis), group in detail.groupby(["scalar_key", "axis"], sort=True):
        spec = axis_specs[axis]
        values = pivot.loc[pivot.scalar_key.eq(scalar), ["model_id", spec["reference"], spec["fine"]]].sort_values("model_id")
        spearman = float(values[spec["reference"]].corr(values[spec["fine"]], method="spearman"))
        ref_top = set(values.nlargest(2, spec["reference"])["model_id"])
        fine_top = set(values.nlargest(2, spec["fine"])["model_id"])
        top_overlap = len(ref_top & fine_top) / 2.0
        fine_median = float(group["fine_to_reference_srd_percent"].median())
        fine_q90 = q90(group["fine_to_reference_srd_percent"])
        strict_count = int(group.convergence_state.eq("strict_converged").sum())
        usable_count = int(group.convergence_state.isin(["strict_converged", "usable_sensitivity"]).sum())
        rank_pass = spearman >= thresholds["panel_spearman_min"] and top_overlap >= thresholds["top_quartile_overlap_min"]
        strict = (
            fine_median <= thresholds["descriptor_axis_strict_median_percent"]
            and fine_q90 <= thresholds["descriptor_axis_strict_q90_percent"]
            and strict_count >= thresholds["descriptor_axis_strict_min_models"]
            and rank_pass
        )
        usable = (
            fine_median <= thresholds["descriptor_axis_usable_median_percent"]
            and fine_q90 <= thresholds["descriptor_axis_usable_q90_percent"]
            and usable_count >= thresholds["descriptor_axis_usable_min_models"]
            and rank_pass
        )
        axis_state = "descriptor_axis_strict" if strict else ("descriptor_axis_usable" if usable else "descriptor_axis_unresolved")
        summary_rows.append(
            {
                "scalar_key": scalar,
                "scalar_label": group.scalar_label.iloc[0],
                "descriptor": group.descriptor.iloc[0],
                "statistic": group.statistic.iloc[0],
                "unit": group.unit.iloc[0],
                "axis": axis,
                "median_fine_srd_percent": fine_median,
                "q90_fine_srd_percent": fine_q90,
                "max_fine_srd_percent": float(group.fine_to_reference_srd_percent.max()),
                "median_coarse_srd_percent": float(group.coarse_to_reference_srd_percent.median()),
                "strict_models": strict_count,
                "strict_or_usable_models": usable_count,
                "nonmonotonic_models": int(group.convergence_state.eq("nonmonotonic").sum()),
                "unconverged_models": int(group.convergence_state.eq("unconverged").sum()),
                "panel_spearman": spearman,
                "top2_overlap": top_overlap,
                "rank_gate_pass": rank_pass,
                "axis_state": axis_state,
            }
        )
    descriptor_axis = pd.DataFrame(summary_rows)
    write_csv(DESCRIPTOR_AXIS, descriptor_axis)

    policy_rows: list[dict] = []
    for scalar in scalar_keys:
        sub = descriptor_axis.loc[descriptor_axis.scalar_key.eq(scalar)].set_index("axis")
        pixel_state = sub.loc["pixel", "axis_state"]
        slice_state = sub.loc["slice", "axis_state"]
        accepted = {"descriptor_axis_strict", "descriptor_axis_usable"}
        decision = "reference_retained_for_descriptor" if pixel_state in accepted and slice_state in accepted else "reference_hold_for_descriptor"
        policy_rows.append(
            {
                "scalar_key": scalar,
                "scalar_label": sub.iloc[0]["scalar_label"],
                "pixel_state": pixel_state,
                "slice_state": slice_state,
                "decision": decision,
                "scientific_status": "likely_panel_evidence" if decision.startswith("reference_retained") else "unresolved",
                "claim_limit": "panel convergence only; not historical parity or feature promotion",
            }
        )
    policy = pd.DataFrame(policy_rows)
    write_csv(DESCRIPTOR_POLICY, policy)

    config_rows: list[dict] = []
    reference = contract["reference_config"]
    reference_values = pivot.set_index(["model_id", "scalar_key"])[reference]
    for config in expected_configs:
        config_values = pivot.set_index(["model_id", "scalar_key"])[config]
        srds = pd.Series([srd(float(a), float(b)) for a, b in zip(config_values, reference_values)], dtype=float)
        config_rows.append(
            {
                "config_id": config,
                "role": "reference" if config == reference else next((spec_name + "_" + level for spec_name, spec in axis_specs.items() for level in ["coarse", "fine"] if spec[level] == config), "variant"),
                "model_descriptor_cells": len(srds),
                "median_srd_percent": float(srds.median()),
                "q90_srd_percent": q90(srds),
                "max_srd_percent": float(srds.max()),
                "within_5_percent": int((srds <= 5.0).sum()),
                "within_10_percent": int((srds <= 10.0).sum()),
                "over_15_percent": int((srds > 15.0).sum()),
            }
        )
    config_summary = pd.DataFrame(config_rows)
    write_csv(CONFIG_SUMMARY, config_summary)

    model_rows: list[dict] = []
    for model, group in detail.groupby("model_id", sort=True):
        for axis in ["pixel", "slice"]:
            sub = group.loc[group.axis.eq(axis)]
            model_rows.append(
                {
                    "model_id": model,
                    "model_family": model[0],
                    "source_identity_status": sub.source_identity_status.iloc[0],
                    "axis": axis,
                    "median_fine_srd_percent": float(sub.fine_to_reference_srd_percent.median()),
                    "max_fine_srd_percent": float(sub.fine_to_reference_srd_percent.max()),
                    "strict_count": int(sub.convergence_state.eq("strict_converged").sum()),
                    "usable_count": int(sub.convergence_state.isin(["strict_converged", "usable_sensitivity"]).sum()),
                    "nonmonotonic_count": int(sub.convergence_state.eq("nonmonotonic").sum()),
                    "unconverged_count": int(sub.convergence_state.eq("unconverged").sum()),
                    "alert": bool((sub.fine_to_reference_srd_percent > thresholds["model_alert_srd_percent"]).any()),
                }
            )
    model_summary = pd.DataFrame(model_rows)
    write_csv(MODEL_SUMMARY, model_summary)

    t89_rows: list[dict] = []
    base_orders: dict[str, int] = {}
    for scalar in scalar_keys:
        base = pivot.loc[pivot.scalar_key.eq(scalar)].set_index("model_id")[reference]
        delta = float(base["T8"] - base["T9"])
        base_orders[scalar] = 0 if delta == 0 else (1 if delta > 0 else -1)
    for config in expected_configs:
        for scalar in scalar_keys:
            values = pivot.loc[pivot.scalar_key.eq(scalar)].set_index("model_id")[config]
            t8 = float(values["T8"])
            t9 = float(values["T9"])
            delta = t8 - t9
            order = 0 if delta == 0 else (1 if delta > 0 else -1)
            t89_rows.append(
                {
                    "config_id": config,
                    "scalar_key": scalar,
                    "scalar_label": short_label(scalar),
                    "T8_value": t8,
                    "T9_value": t9,
                    "absolute_delta": abs(delta),
                    "symmetric_separation_percent": srd(t8, t9),
                    "order_sign": order,
                    "reference_order_sign": base_orders[scalar],
                    "order_preserved": order == base_orders[scalar],
                }
            )
    t89 = pd.DataFrame(t89_rows)
    write_csv(T89, t89)

    l7 = detail.loc[detail.model_id.eq("L7")].copy()
    write_csv(L7, l7)

    job_matrix = pd.read_csv(job_path, keep_default_na=False)
    runtime_rows: list[dict] = []
    runtime_root = Path(r"C:\Users\chuck\URP4-1_FACTORY\R09_SLICE005_20260721\results\runtime")
    for _, job in job_matrix.iterrows():
        attempt = runtime_root / job.execution_cell_id.replace("::", "__") / "attempt01" / "complete.json"
        payload = json.loads(attempt.read_text(encoding="utf-8"))
        runtime_rows.append(
            {
                "config_id": job.config_id,
                "model_id": job.model_id,
                "runtime_seconds": payload["runtime_seconds"],
                "peak_rss_gib": payload["resource"]["peak_rss_gib"],
                "output_bytes": payload["resource"]["output_bytes"],
            }
        )
    runtime_detail = pd.DataFrame(runtime_rows)
    runtime_summary = runtime_detail.groupby("config_id").agg(
        cells=("model_id", "count"),
        total_runtime_seconds=("runtime_seconds", "sum"),
        median_runtime_seconds=("runtime_seconds", "median"),
        max_runtime_seconds=("runtime_seconds", "max"),
        max_peak_rss_gib=("peak_rss_gib", "max"),
        total_output_bytes=("output_bytes", "sum"),
    ).reset_index()
    write_csv(RUNTIME, runtime_summary)

    # Heatmaps of the fine-vs-reference SRD.
    labels = [short_label(key) for key in scalar_keys]
    fig, axes = plt.subplots(1, 2, figsize=(18, 7), constrained_layout=True)
    for ax, axis in zip(axes, ["pixel", "slice"]):
        heat = detail.loc[detail.axis.eq(axis)].pivot(index="model_id", columns="scalar_key", values="fine_to_reference_srd_percent").reindex(index=models, columns=scalar_keys)
        im = ax.imshow(heat.to_numpy(), cmap="YlOrRd", vmin=0, vmax=max(15, float(np.nanpercentile(heat.to_numpy(), 95))))
        ax.set_title(f"{axis.capitalize()} fine → P1000-S801 SRD (%)")
        ax.set_xticks(range(len(labels)), labels, rotation=45, ha="right")
        ax.set_yticks(range(len(models)), models)
        for i in range(len(models)):
            for j in range(len(labels)):
                ax.text(j, i, f"{heat.iloc[i, j]:.1f}", ha="center", va="center", fontsize=7)
        fig.colorbar(im, ax=ax, fraction=0.046)
    fig.suptitle("PRM-070 · Fine-grid sensitivity by model and scalar (y-blind)")
    fig.savefig(FIG_HEAT, dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(18, 6), sharey=True, constrained_layout=True)
    for ax, axis in zip(axes, ["pixel", "slice"]):
        sub = descriptor_axis.loc[descriptor_axis.axis.eq(axis)].set_index("scalar_key").reindex(scalar_keys)
        x = np.arange(len(labels))
        ax.bar(x - 0.18, sub.median_fine_srd_percent, 0.36, label="median")
        ax.bar(x + 0.18, sub.q90_fine_srd_percent, 0.36, label="q90")
        ax.axhline(5, color="green", linestyle="--", linewidth=1, label="strict 5%")
        ax.axhline(10, color="orange", linestyle="--", linewidth=1, label="usable 10%")
        ax.axhline(15, color="red", linestyle=":", linewidth=1, label="alert 15%")
        ax.set_title(f"{axis.capitalize()} descriptor convergence")
        ax.set_xticks(x, labels, rotation=45, ha="right")
        ax.set_ylabel("Fine-to-reference SRD (%)")
        ax.legend(fontsize=8)
    fig.suptitle("PRM-070 · Descriptor median and q90 sensitivity")
    fig.savefig(FIG_DESC, dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(14, 6), constrained_layout=True)
    for config in expected_configs:
        sub = t89.loc[t89.config_id.eq(config)].set_index("scalar_key").reindex(scalar_keys)
        ax.plot(labels, sub.symmetric_separation_percent, marker="o", label=config)
    ax.set_ylabel("T8/T9 symmetric separation (%)")
    ax.set_title("PRM-070 · T8/T9 descriptor separation across configurations")
    ax.tick_params(axis="x", rotation=45)
    ax.legend(fontsize=8)
    fig.savefig(FIG_T89, dpi=180)
    plt.close(fig)

    retained = int(policy.decision.eq("reference_retained_for_descriptor").sum())
    held = int(policy.decision.eq("reference_hold_for_descriptor").sum())
    pixel_states = descriptor_axis.loc[descriptor_axis.axis.eq("pixel"), "axis_state"].value_counts().to_dict()
    slice_states = descriptor_axis.loc[descriptor_axis.axis.eq("slice"), "axis_state"].value_counts().to_dict()
    t89_order_breaks = int((~t89.order_preserved).sum())
    l7_alerts = int(l7.alert_over_15_percent.sum())
    overall_decision = "retain_reference_for_supported_descriptors_only" if retained > 0 else "reference_hold_all_descriptors"

    qa_rows: list[dict] = []

    def add(qid: str, check: str, observed, expected, passed: bool) -> None:
        qa_rows.append({"qa_id": qid, "check": check, "observed": observed, "expected": expected, "passed": bool(passed)})

    add("Q01", "contract frozen status", contract["status"], "frozen_before_delta_calculation", contract["status"] == "frozen_before_delta_calculation")
    add("Q02", "matrix hash", sha256(matrix_path), contract["inputs"]["aggregate_matrix"]["sha256"], sha256(matrix_path) == contract["inputs"]["aggregate_matrix"]["sha256"])
    add("Q03", "job hash", sha256(job_path), contract["inputs"]["job_matrix"]["sha256"], sha256(job_path) == contract["inputs"]["job_matrix"]["sha256"])
    add("Q04", "ZIP hash", sha256(zip_path), contract["inputs"]["return_zip"]["sha256"], sha256(zip_path) == contract["inputs"]["return_zip"]["sha256"])
    add("Q05", "matrix rows", len(matrix), 360, len(matrix) == 360)
    add("Q06", "models", matrix.model_id.nunique(), 8, matrix.model_id.nunique() == 8)
    add("Q07", "configs", matrix.config_id.nunique(), 5, matrix.config_id.nunique() == 5)
    add("Q08", "scalar keys", matrix.scalar_key.nunique(), 9, matrix.scalar_key.nunique() == 9)
    add("Q09", "unique cells", matrix.execution_cell_id.nunique(), 40, matrix.execution_cell_id.nunique() == 40)
    add("Q10", "finite values", int(np.isfinite(matrix.value).sum()), 360, np.isfinite(matrix.value).all())
    add("Q11", "pivot rows", len(pivot), 72, len(pivot) == 72)
    add("Q12", "detail rows", len(detail), 144, len(detail) == 144)
    add("Q13", "descriptor-axis rows", len(descriptor_axis), 18, len(descriptor_axis) == 18)
    add("Q14", "policy rows", len(policy), 9, len(policy) == 9)
    add("Q15", "config rows", len(config_summary), 5, len(config_summary) == 5)
    add("Q16", "model-risk rows", len(model_summary), 16, len(model_summary) == 16)
    add("Q17", "T8/T9 rows", len(t89), 45, len(t89) == 45)
    add("Q18", "L7 rows", len(l7), 18, len(l7) == 18)
    add("Q19", "runtime rows", len(runtime_detail), 32, len(runtime_detail) == 32)
    add("Q20", "runtime config rows", len(runtime_summary), 4, len(runtime_summary) == 4)
    add("Q21", "heatmap exists", FIG_HEAT.is_file(), True, FIG_HEAT.is_file())
    add("Q22", "descriptor figure exists", FIG_DESC.is_file(), True, FIG_DESC.is_file())
    add("Q23", "T8/T9 figure exists", FIG_T89.is_file(), True, FIG_T89.is_file())
    add("Q24", "no y/fit", [contract["locks"]["performance_y_read"], contract["locks"]["model_fit"], contract["locks"]["prediction"]], [0, 0, 0], contract["locks"]["performance_y_read"] == contract["locks"]["model_fit"] == contract["locks"]["prediction"] == 0)
    qa = pd.DataFrame(qa_rows)
    write_csv(QA, qa)
    if not qa.passed.all():
        raise RuntimeError("PRM070 producer QA failed")

    completed_at = datetime.now(KST).isoformat(timespec="seconds")
    summary = {
        "run_id": contract["run_id"],
        "completed_at_kst": completed_at,
        "status": "passed_y_blind_convergence_review",
        "decision": overall_decision,
        "reference_config": reference,
        "descriptor_reference_retained": retained,
        "descriptor_reference_hold": held,
        "pixel_axis_states": pixel_states,
        "slice_axis_states": slice_states,
        "T8_T9_order_break_rows": t89_order_breaks,
        "L7_over15_alert_rows": l7_alerts,
        "producer_QA": "24/24",
        "performance_y_read": 0,
        "model_fit": 0,
        "feature_promotion": 0,
        "next_task": "PRM070-INDEPENDENT-CONTROL-REVIEW",
    }
    SUMMARY.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    desc_lines = []
    for _, row in policy.iterrows():
        desc_lines.append(f"| {row.scalar_label} | {row.pixel_state} | {row.slice_state} | {row.decision} |")
    report_text = "\n".join(
        [
            "# PRM-070 · SLICE-005 configuration convergence control review",
            "",
            f"- Completed: `{completed_at}`",
            f"- Decision: `{overall_decision}`",
            "- Scope: y-blind eight-model panel; historical parity and feature promotion are outside scope.",
            "",
            "## Result",
            "",
            f"The frozen P1000-S801 reference is retained for `{retained}/9` scalar descriptors and held for `{held}/9`. This is descriptor-specific panel evidence, not one universal configuration approval.",
            "",
            f"Pixel states: `{json.dumps(pixel_states, ensure_ascii=False)}`  ",
            f"Slice states: `{json.dumps(slice_states, ensure_ascii=False)}`",
            "",
            "## Descriptor policy",
            "",
            "| scalar | pixel | slice | decision |",
            "|---|---|---|---|",
            *desc_lines,
            "",
            "## Special diagnostics",
            "",
            f"- T8/T9 ordering breaks across config×scalar rows: `{t89_order_breaks}/45`.",
            f"- L7 fine-grid SRD alerts over 15%: `{l7_alerts}/18`.",
            "- F1/F2 and T8/T9 remain source-identity `likely`; convergence cannot upgrade source identity.",
            "- Panel rank is across eight representatives, not within-family generalization.",
            "",
            "## Runtime",
            "",
            "The 32 new cells are summarized in `PRM070_SLICE005_runtime_cost_summary.csv`; cost is descriptive and cannot rescue a failed scientific gate.",
            "",
            "## Boundaries",
            "",
            "- performance y read / fit / prediction / feature promotion: `0 / 0 / 0 / 0`",
            "- thresholds were frozen in PRM-070 before delta calculation",
            "- no raw result, formula, source or historical Excel value was changed",
            "",
            "## Next",
            "",
            "Run independent/control QA and inspect the three figures. Only after that may a descriptor-specific reference policy be merged.",
            "",
        ]
    )
    REPORT.write_text(report_text, encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
