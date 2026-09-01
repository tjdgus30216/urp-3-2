from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
TABLES = LAB / "reports" / "tables"


def main() -> None:
    cost = pd.read_csv(TABLES / "PRM099_full58_cost_projection.csv")
    overlap = pd.read_csv(TABLES / "PRM099_six_output_vs_XREG_v0_2_panel_overlap.csv")
    counts = overlap.groupby(["candidate_id", "relation"]).size().unstack(fill_value=0)
    labels = [x.split("::", 1)[1].replace("solid_void_chord_", "").replace("_direction_mean_per_mm3", "") for x in counts.index]
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), constrained_layout=True)
    axes[0].bar(["X019\nderive", "X024\ncompute"], cost.projected_full58_wall_min, color=["#2563eb", "#059669"])
    axes[0].set_ylabel("projected serial wall time (min)")
    axes[0].set_title("58-model execution route and 2×p90 safety cost")
    for i, row in cost.reset_index(drop=True).iterrows():
        axes[0].text(i, row.projected_full58_wall_min + .08, f"{row.projected_full58_wall_min:.2f} min", ha="center")
    high = counts.get("high_redundancy_small_panel", pd.Series(0, index=counts.index))
    other = counts.sum(axis=1) - high
    axes[1].barh(labels, other, color="#cbd5e1", label="distinct/unresolved")
    axes[1].barh(labels, high, left=other, color="#f59e0b", label="high redundancy flag")
    axes[1].set_xlabel("comparisons with XREG-v0.2 (108 each)")
    axes[1].set_title("Six-model x-only overlap diagnostic — not selection")
    axes[1].legend(frameon=False)
    fig.suptitle("PRM-099 exact-hash permit review — 58×6 authorized for PRM-100, not executed", fontweight="bold", fontsize=14)
    out = LAB / "reports" / "figures" / "PRM099_full58_permit_decision.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    main()
