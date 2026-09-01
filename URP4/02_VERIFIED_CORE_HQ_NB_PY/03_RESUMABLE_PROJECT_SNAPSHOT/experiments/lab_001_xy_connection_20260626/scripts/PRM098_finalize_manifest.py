from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
OUT = LAB / "factories" / "PRM-098" / "reports" / "PRM098_output_manifest.csv"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    roots = [LAB / "factories" / "PRM-098"]
    explicit = [
        *sorted((LAB / "scripts").glob("PRM098_*.py")),
        *sorted((LAB / "reports" / "tables").glob("PRM098_*.csv")),
        *sorted((LAB / "reports" / "figures").glob("PRM098_*.png")),
        LAB / "results" / "R09-20260723-PRM098_BOUNDED_THIRD_WAVE_SYNTHETIC_COST_PANEL.md",
        LAB / "results" / "R09_blackbox_decision_register_20260703.md",
        LAB / "runlog.md",
        LAB / "decision_log.md",
        LAB / "changelog.md",
        ROOT / "AI_START_HERE.md",
        ROOT / "outputs" / "URP4-1_ROADMAP.md",
        ROOT / "outputs" / "URP4-1_ROADMAP_LOG.md",
        ROOT / "outputs" / "URP4-1_CHANGELOG.md",
        ROOT / "outputs" / "URP4-1_PROFESSOR_PROJECT_ROADMAP_20260629.md",
    ]
    files: set[Path] = set()
    for root in roots:
        files.update(p for p in root.rglob("*") if p.is_file())
    files.update(p for p in explicit if p.exists())
    # Self-hashing makes a stable manifest impossible; QA checks the manifest
    # schema/content separately and re-runs it after the final edits.
    files.discard(OUT)
    files.discard(LAB / "factories" / "PRM-098" / "reports" / "PRM098_postmerge_sync_QA.csv")
    files.discard(LAB / "factories" / "PRM-098" / "reports" / "PRM098_postmerge_sync_QA_summary.json")
    rows = []
    for path in sorted(files, key=lambda p: str(p).lower()):
        rel = path.relative_to(ROOT)
        rows.append({
            "path": str(rel),
            "size_bytes": path.stat().st_size,
            "sha256": sha256(path),
            "exists": True,
        })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT, index=False, encoding="utf-8-sig")
    print(f"manifest_rows={len(rows)}")


if __name__ == "__main__":
    main()
