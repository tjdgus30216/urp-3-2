from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
TABLES = LAB / "reports" / "tables"
FIGURES = LAB / "reports" / "figures"
FACTORY_REPORTS = LAB / "factories" / "PRM-098" / "reports"


def write_attempt_ledger() -> Path:
    rows = [
        ("P098-P01", "preflight", "PASS", "8/8 contract checks and 24/24 protected hashes passed before execution.", False, False),
        ("P098-A01", "contract amendment", "PASS", "X019 V128-only wording corrected to same current-resolution mask/axis/stat before observing candidate results; PRM-097 source preserved.", True, False),
        ("P098-H01", "cost runner header", "CORRECTED", "Runner expected max_seconds_per_cell while permit used max_wall_seconds; corrected before any affected cell executed.", False, False),
        ("P098-O01", "ECT coordinate precision", "CORRECTED", "Optimized ECT first differed from reference because the reference constructed center coordinates as float32; reference changed to float64 and all synthetic/canary checks rerun before the panel.", False, True),
        ("P098-M01", "C1 V192 mask review", "PASS_WITH_WARNING", "Same-STL replay across V64/V96/V128/V160/V192/V224/V256 confirmed deterministic voxel-grid resonance; no gate threshold changed.", False, False),
        ("P098-R01", "parent wait interruption", "RESUMED", "A parent wait ended while Windows child processes continued. Hash-valid atomic done files were reused; no completed cell was recomputed.", False, False),
        ("P098-C01", "X006 C1 V192 resource stop", "HOLD", "Cell exceeded bounded wall-time and was terminated. Remaining X006 V192 panel cells were not run; no retry or threshold relaxation.", False, False),
        ("P098-Q01", "X031 lineage replay tolerance", "CORRECTED", "Independent verifier tolerance changed from 1e-12 to 1e-10 for CSV round-trip differences (max about 3.1e-12); candidate values/formulas unchanged.", False, False),
    ]
    path = FACTORY_REPORTS / "PRM098_attempt_ledger.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["attempt_id", "stage", "status", "finding_or_action", "scientific_contract_change", "numerical_implementation_change"])
        w.writerows(rows)
    return path


def make_figure() -> Path:
    gates = pd.read_csv(TABLES / "PRM098_output_resolution_gate.csv")
    technical = gates[
        (gates["candidate_group_id"] != "LIT-X028")
        & (gates["technical_state"] != "diagnostic_or_negative_control_only")
    ].copy()
    # The preregistered technical routes contain 37 outputs; diagnostics and the
    # X028 negative-control rows are intentionally excluded from promotion counts.
    groups = ["LIT-X006", "LIT-X008", "LIT-X019", "LIT-X024", "LIT-X028", "LIT-X031"]
    pass_counts = []
    fail_counts = []
    for group in groups:
        if group == "LIT-X028":
            pass_counts.append(0)
            fail_counts.append(0)
            continue
        g = technical[technical["candidate_group_id"] == group]
        pass_counts.append(int(g["frozen_gate_pass"].fillna(False).astype(bool).sum()))
        fail_counts.append(int(len(g) - pass_counts[-1]))

    fig, axes = plt.subplots(1, 2, figsize=(14, 6), constrained_layout=True)
    x = np.arange(len(groups))
    axes[0].bar(x, pass_counts, color="#1f9d55", label="resolution-qualified")
    axes[0].bar(x, fail_counts, bottom=pass_counts, color="#cbd5e1", label="held / not evaluable")
    axes[0].set_xticks(x, [g.replace("LIT-", "") for g in groups])
    axes[0].set_ylabel("technical output count")
    axes[0].set_title("PRM-098 technical route by candidate group")
    axes[0].legend(frameon=False)
    axes[0].text(4, 0.25, "negative\ncontrol", ha="center", va="bottom", fontsize=9, color="#475569")
    axes[0].text(0, max(pass_counts[0] + fail_counts[0], 1) + 0.2, "cost hold", ha="center", fontsize=9, color="#b91c1c")

    plot = technical.dropna(subset=["median_srd_percent", "q90_srd_percent"]).copy()
    colors = {
        "LIT-X006": "#8b5cf6", "LIT-X008": "#f59e0b", "LIT-X019": "#2563eb",
        "LIT-X024": "#059669", "LIT-X031": "#dc2626",
    }
    for group, g in plot.groupby("candidate_group_id"):
        axes[1].scatter(g["median_srd_percent"], g["q90_srd_percent"], s=42,
                        alpha=0.8, label=group.replace("LIT-", ""), color=colors.get(group, "#64748b"))
    qualified = plot[plot["frozen_gate_pass"].astype(bool)]
    axes[1].scatter(qualified["median_srd_percent"], qualified["q90_srd_percent"],
                    s=100, facecolors="none", edgecolors="black", linewidths=1.2, label="qualified")
    axes[1].axvline(5.0, color="#64748b", linestyle="--", linewidth=1)
    axes[1].axhline(10.0, color="#64748b", linestyle="--", linewidth=1)
    axes[1].set_xlabel("V128–V192 median SRD (%)")
    axes[1].set_ylabel("V128–V192 q90 SRD (%)")
    axes[1].set_title("Frozen resolution-gate evidence (technical outputs only)")
    axes[1].set_xlim(left=-0.2)
    axes[1].set_ylim(bottom=-0.2)
    axes[1].legend(frameon=False, fontsize=8, ncol=2)

    fig.suptitle("PRM-098 bounded third-wave review — no y, no selection, no promotion", fontsize=14, fontweight="bold")
    path = FIGURES / "PRM098_third_wave_bounded_gate.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


if __name__ == "__main__":
    print(write_attempt_ledger())
    print(make_figure())
