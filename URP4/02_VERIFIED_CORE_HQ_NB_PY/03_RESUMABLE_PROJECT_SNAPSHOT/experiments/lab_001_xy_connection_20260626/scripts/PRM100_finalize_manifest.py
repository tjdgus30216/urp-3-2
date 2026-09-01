from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
FACTORY = LAB / "factories" / "PRM-100"
OUT = FACTORY / "reports" / "PRM100_output_manifest.csv"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    files = {p for p in FACTORY.rglob("*") if p.is_file() and "quarantine" not in p.parts}
    files.update((LAB / "scripts").glob("PRM100_*.py"))
    files.update((LAB / "reports" / "tables").glob("PRM100_*.csv"))
    files.update((LAB / "reports" / "figures").glob("PRM100_*.png"))
    files.update([
        LAB / "results" / "R09-20260723-PRM100_THIRD_WAVE_FULL58_V128_SIX_OUTPUT_EXECUTION_AND_XONLY_REVIEW.md",
        LAB / "results" / "R09_blackbox_decision_register_20260703.md", LAB / "runlog.md", LAB / "decision_log.md", LAB / "changelog.md",
        ROOT / "AI_START_HERE.md", ROOT / "outputs" / "URP4-1_ROADMAP.md", ROOT / "outputs" / "URP4-1_ROADMAP_LOG.md",
        ROOT / "outputs" / "URP4-1_CHANGELOG.md", ROOT / "outputs" / "URP4-1_PROFESSOR_PROJECT_ROADMAP_20260629.md",
    ])
    files = {p for p in files if p.exists()}
    files.discard(OUT)
    files.discard(FACTORY / "reports" / "PRM100_postmerge_sync_QA.csv")
    files.discard(FACTORY / "reports" / "PRM100_postmerge_sync_QA_summary.json")
    rows = [{"path": str(p.relative_to(ROOT)), "size_bytes": p.stat().st_size, "sha256": digest(p)} for p in sorted(files, key=lambda x: str(x).lower())]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT, index=False, encoding="utf-8-sig")
    print(f"manifest_rows={len(rows)}")


if __name__ == "__main__":
    main()
