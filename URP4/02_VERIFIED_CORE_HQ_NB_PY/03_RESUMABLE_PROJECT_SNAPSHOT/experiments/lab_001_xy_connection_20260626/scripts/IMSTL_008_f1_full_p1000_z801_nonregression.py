"""Run the preregistered F1 full P1000/Z801 HQ image-readback extraction."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments/lab_001_xy_connection_20260626"
DELIVERABLE = ROOT / "URP4-1_DELIVERABLE"
if str(DELIVERABLE) not in sys.path:
    sys.path.insert(0, str(DELIVERABLE))

from urp4.hq.v0_1 import URP4Controller, run_hq  # noqa: E402
from urp4.hq.v0_1.controller import (  # noqa: E402
    ArtifactControl,
    GeometryControl,
    PathControl,
    WorkflowControl,
)


RUN_ID = "IMSTL-008-20260728-002"
TASK_ID = "IMSTL-008_F1_FULL_P1000_Z801_AND_FAMILY_NONREGRESSION_NO_Y"
CONTRACT = LAB / "factories/IMSTL-008/contracts/IMSTL-008_F1_FULL_P1000_Z801_NONREGRESSION_v0_2_20260728.json"
RUN = LAB / "runs/I008" / RUN_ID
RESULT = LAB / "results/I008_F1" / RUN_ID
TABLES = LAB / "reports/tables"
PROTECTED_BASELINE = LAB / "results/HQ-BLUEPRINT-001/PROTECTED_ASSET_BASELINE.json"
I006_RUN = LAB / "runs/I006/IMSTL-006-20260728-002"
I006_RESULT = LAB / "results/IMSTL-006_SMALL_GENERALIZATION/IMSTL-006-20260728-002"
I007_RUN = LAB / "runs/I007/IMSTL-007-20260728-002"
I007_RESULT = LAB / "results/I007_F1/IMSTL-007-20260728-002"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tree_identity(path: Path) -> tuple[str, int, int]:
    digest = hashlib.sha256()
    files = [item for item in sorted(path.rglob("*")) if item.is_file() and "__pycache__" not in item.parts]
    total = 0
    for item in files:
        relative = item.relative_to(path).as_posix()
        size = item.stat().st_size
        total += size
        digest.update(relative.encode("utf-8") + b"\0" + sha256(item).encode("ascii") + b"\0" + str(size).encode("ascii") + b"\n")
    return digest.hexdigest(), len(files), total


def protected_audit() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for item in json.loads(PROTECTED_BASELINE.read_text(encoding="utf-8"))["assets"]:
        path = ROOT / item["path"]
        if item["asset_kind"] == "tree":
            current, count, size = tree_identity(path)
        else:
            current, count, size = sha256(path), 1, path.stat().st_size
        rows.append({
            "alias": item["alias"],
            "path": item["path"],
            "expected_sha256": item["before_sha256"],
            "current_sha256": current,
            "file_count": count,
            "size_bytes": size,
            "status": "passed" if current == item["before_sha256"] else "failed",
        })
    return rows


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    if RUN.exists() or RESULT.exists():
        raise FileExistsError(f"run/result already exists; refusing overwrite: {RUN_ID}")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    source = ROOT / contract["source"]["path"]
    if sha256(source) != contract["source"]["sha256"]:
        raise RuntimeError("F1 source hash mismatch")
    i007 = json.loads((I007_RESULT / "DECISION_PACKET.json").read_text(encoding="utf-8"))
    if i007.get("status") != "passed" or i007.get("source_sha256") != contract["source"]["sha256"]:
        raise RuntimeError("IMSTL-007 approval/source prerequisite failed")
    before = protected_audit()
    if any(row["status"] != "passed" for row in before):
        raise RuntimeError("protected asset pre-audit failed")

    RUN.mkdir(parents=True)
    RESULT.mkdir(parents=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    shutil.copy2(CONTRACT, RUN / "CONTRACT.json")
    upstream = {
        "protected_assets": {row["alias"]: row["current_sha256"] for row in before},
        "i006_run_tree": tree_identity(I006_RUN)[0],
        "i006_result_tree": tree_identity(I006_RESULT)[0],
        "i007_run_tree": tree_identity(I007_RUN)[0],
        "i007_result_tree": tree_identity(I007_RESULT)[0],
    }
    write_json(RUN / "UPSTREAM_BASELINE.json", upstream)

    controller = URP4Controller(
        workflow=WorkflowControl(import_geometry=True, generate_geometry=False, extract_descriptors=True),
        paths=PathControl(
            input_geometry=str(source),
            output_root=str(ROOT / contract["runtime_output_root"]),
            experiment_name=TASK_ID,
        ),
        geometry=GeometryControl(
            model_id="F1",
            source_type="imported_stl",
            geometry_revision="N40-20260715-d76883bc10af",
            expected_size_mm=40.0,
            normalize_imported_stl=True,
        ),
        artifacts=ArtifactControl(
            image_policy="STREAMING_TEMP_PNG",
            overwrite=False,
            export_component_tables=True,
            visual_review_export=False,
        ),
    )
    started = datetime.now(UTC).isoformat()
    status = run_hq(controller, DELIVERABLE)
    completed = datetime.now(UTC).isoformat()
    run_dir = Path(status["run_dir"])
    descriptor = status.get("descriptor") or {}
    qa = descriptor.get("qa") or {}
    scalar = pd.read_csv(run_dir / "descriptor_result.csv")
    required = [
        "run_manifest.json", "input_geometry_manifest.json", "output_manifest.csv",
        "training_required_input_schema.json", "descriptor_result.csv", "descriptor_result.xlsx",
        "descriptor/qa.json", "descriptor/tables/slice_pixel_count_table.csv",
        "descriptor/tables/slice_component_table.csv", "descriptor/tables/overlay_pixel_table.csv",
        "descriptor/tables/overlay_component_table.csv",
    ]
    artifact_complete = all((run_dir / item).is_file() for item in required)
    producer_pass = bool(
        status.get("status") == "passed"
        and descriptor.get("status") == "passed"
        and len(scalar) == 9
        and qa.get("slice_rows") == 801
        and qa.get("overlay_rows") == 800
        and qa.get("readback_mismatch_sum") == 0
        and qa.get("png_created") == 1601
        and qa.get("png_deleted") == 1601
        and qa.get("remaining_png") == 0
        and qa.get("source_geometry_sha256") == contract["source"]["sha256"]
        and artifact_complete
    )
    scalar.insert(0, "task_run_id", RUN_ID)
    scalar.to_csv(TABLES / f"{RUN_ID}_f1_run139_scalar_result.csv", index=False, encoding="utf-8-sig")
    summary = {
        "task_id": TASK_ID,
        "run_id": RUN_ID,
        "settings_address": contract["settings_address"],
        "started_at_utc": started,
        "completed_at_utc": completed,
        "status": "passed" if producer_pass else "failed",
        "hq_run_dir": str(run_dir),
        "source_sha256": contract["source"]["sha256"],
        "descriptor_rows": len(scalar),
        "slice_rows": qa.get("slice_rows"),
        "overlay_rows": qa.get("overlay_rows"),
        "slice_component_rows": qa.get("slice_component_rows"),
        "overlay_component_rows": qa.get("overlay_component_rows"),
        "readback_mismatch_sum": qa.get("readback_mismatch_sum"),
        "png_created": qa.get("png_created"),
        "png_deleted": qa.get("png_deleted"),
        "remaining_png": qa.get("remaining_png"),
        "artifact_complete": artifact_complete,
        "y_accessed": False,
        "all58_executed": False,
        "feature_selection_performed": False,
        "model_fitting_performed": False,
    }
    write_json(RESULT / "PRODUCER_SUMMARY.json", summary)
    write_csv(RESULT / "PROTECTED_ASSET_PRE_AUDIT.csv", before)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not producer_pass:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
