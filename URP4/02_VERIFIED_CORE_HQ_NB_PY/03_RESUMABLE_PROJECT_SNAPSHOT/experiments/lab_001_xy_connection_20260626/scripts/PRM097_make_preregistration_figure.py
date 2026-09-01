from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
TABLES = LAB / "reports" / "tables"
FIGURES = LAB / "reports" / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

roster = pd.read_csv(TABLES / "PRM097_candidate_output_schema.csv")
fixtures = pd.read_csv(TABLES / "PRM097_synthetic_truth_fixture_registry.csv")
groups = ["LIT-X006", "LIT-X008", "LIT-X019", "LIT-X024", "LIT-X028", "LIT-X031"]
labels = ["Skeleton\ngraph", "Local\nthickness", "Phase-scale\nratio", "Euler\ntransform", "Binary GLCM\ncontrol", "Normal\nharmonics"]
outputs = roster.groupby("candidate_group_id").size().reindex(groups)
truths = fixtures.groupby("candidate_group_id").size().reindex(groups)

fig, ax = plt.subplots(figsize=(12, 6.6))
x = range(len(groups))
ax.bar([i - 0.19 for i in x], outputs, width=0.38, label="Frozen scalar/artifact outputs", color="#2878B5")
ax.bar([i + 0.19 for i in x], truths, width=0.38, label="Synthetic-truth fixtures", color="#F28E2B")
for i, value in enumerate(outputs):
    ax.text(i - 0.19, value + 0.55, str(int(value)), ha="center", fontweight="bold")
for i, value in enumerate(truths):
    ax.text(i + 0.19, value + 0.55, str(int(value)), ha="center", fontweight="bold")
ax.set_xticks(list(x), labels)
ax.set_ylabel("Registered count")
ax.set_title("PRM-097 — Third-wave formula and synthetic-truth preregistration")
ax.grid(axis="y", alpha=0.2)
ax.legend(loc="upper left")
ax.text(0.01, -0.20, "NO EXECUTION: 0 candidate values · 0 y reads · 0 fits · 0 selections · 0 promotions", transform=ax.transAxes, color="#B22222", fontweight="bold")
ax.text(0.01, -0.27, "Next gate: PRM-098 synthetic truth → serial V64 cost canary → representative panel; full58 remains locked", transform=ax.transAxes, color="#333333")
fig.subplots_adjust(bottom=0.28, top=0.88, left=0.08, right=0.98)
out = FIGURES / "PRM097_third_wave_preregistration_map.png"
fig.savefig(out, dpi=180)
plt.close(fig)
print(out)
