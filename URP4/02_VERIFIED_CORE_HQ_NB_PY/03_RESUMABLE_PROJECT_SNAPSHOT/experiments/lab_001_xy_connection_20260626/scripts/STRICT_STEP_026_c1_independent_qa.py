"""Independent, post-completion QA for STRICT-STEP-026 C1 direct LEGACY-PY run.

This checker is deliberately non-generative. It refuses to inspect a running
run, rehashes saved artifacts, and never calls the STEP slicer or LEGACY-PY.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
RUN = LAB / "results" / "STRICT-STEP-026" / "STRICT-STEP-026-20260731-001"
EXPECTED_STEP_SHA256 = "3c47641d340e85acd9d2464dc46d665676c90895141e0c3c7c04a3b23ffdc73c"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    if sys.version_info[:2] != (3, 12) or "kmk312" not in sys.executable.lower():
        raise SystemExit("[FAIL] canonical KMK312 Python 3.12 is required")
    state_path = RUN / "RUN_STATE.json"
    if not state_path.is_file():
        raise SystemExit("[FAIL] run state is absent")
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if state.get("status") != "completed":
        raise SystemExit(f"[BLOCKED] run is not completed: {state.get('status')}")
    manifest = json.loads((RUN / "CONTRACT_MANIFEST.json").read_text(encoding="utf-8"))
    slice_rows = csv_rows(RUN / "slice_png_manifest.csv")
    overlay_rows = csv_rows(RUN / "overlay_png_manifest.csv")
    scalar_rows = csv_rows(RUN / "direct_legacy_scalar_table.csv")
    checks = {
        "run_id": state.get("run_id") == "STRICT-STEP-026-20260731-001",
        "completed_counts": state.get("completed_slices") == 801 and state.get("completed_overlays") == 800,
        "source_step_sha256": manifest.get("source_step_sha256") == EXPECTED_STEP_SHA256,
        "slice_manifest_801": len(slice_rows) == 801 and [int(row["slice_index"]) for row in slice_rows] == list(range(801)),
        "overlay_manifest_800": len(overlay_rows) == 800 and [int(row["pair_index"]) for row in overlay_rows] == list(range(800)),
        "direct_scalar_40": len(scalar_rows) == 40,
        "nine_anchor_pngs": len(list((RUN / "anchor_pngs").glob("*.png"))) == 9,
        "bulk_png_evicted": not (RUN / "temporary_pngs").exists(),
        "all_scalar_finite": all(row.get("value", "").lower() not in {"", "nan", "inf", "-inf"} for row in scalar_rows),
    }
    result = {
        "run_id": state["run_id"],
        "status": "passed" if all(checks.values()) else "failed",
        "qa_runtime": sys.executable,
        "checks": checks,
        "artifact_hashes": {
            "contract_manifest": sha256_file(RUN / "CONTRACT_MANIFEST.json"),
            "run_state": sha256_file(state_path),
            "slice_png_manifest": sha256_file(RUN / "slice_png_manifest.csv"),
            "overlay_png_manifest": sha256_file(RUN / "overlay_png_manifest.csv"),
            "direct_legacy_scalar_table": sha256_file(RUN / "direct_legacy_scalar_table.csv"),
        },
        "scope_boundary": "artifact QA only; no slicing, no PNG regeneration, no LEGACY-PY modification, no Excel/y/training access",
    }
    (RUN / "INDEPENDENT_QA.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "checks_passed": sum(checks.values()), "checks_total": len(checks)}, ensure_ascii=False))
    if result["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
