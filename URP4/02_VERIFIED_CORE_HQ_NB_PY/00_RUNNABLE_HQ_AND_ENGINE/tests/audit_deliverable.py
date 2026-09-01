"""Independent audit of HQ package, frozen sources and smoke evidence."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import nbformat
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from urp4.generators.lattice_typeab.v0_1.contracts import SOURCE_PATH as LAT_PATH, SOURCE_SHA256 as LAT_SHA
from urp4.generators.tpms_multiwall.v0_1.contracts import SOURCE_PATH as TPMS_PATH, SOURCE_SHA256 as TPMS_SHA
from urp4.generators.voxel.v0_1.source_kernel import MATCHING_SOURCES, SOURCE_PATH as VOX_PATH, SOURCE_SHA256 as VOX_SHA
from urp4.training.v0_1.registry import build_source_registry


AUDIT = ROOT / "outputs" / "hq_audit"
FULL_ROOT = ROOT / "outputs" / "smoke_full_descriptor"
REQUIRED_RUN_ARTIFACTS = (
    "run_manifest.json",
    "input_geometry_manifest.json",
    "output_manifest.csv",
    "training_required_input_schema.json",
    "descriptor_result.csv",
    "descriptor/tables/slice_pixel_count_table.csv",
    "descriptor/tables/slice_component_table.csv",
    "descriptor/tables/overlay_pixel_table.csv",
    "descriptor/tables/overlay_component_table.csv",
)


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def source_rows() -> list[dict[str, object]]:
    expected = [("lattice", LAT_PATH, LAT_SHA), ("tpms", TPMS_PATH, TPMS_SHA), ("voxel", VOX_PATH, VOX_SHA)]
    expected.extend((alias, path, digest) for alias, path, digest in MATCHING_SOURCES)
    expected.extend((row.alias_id, row.relative_path, row.sha256) for row in build_source_registry())
    rows = []
    for alias, relative, digest in expected:
        path = ROOT / relative
        actual = sha(path) if path.is_file() else "missing"
        rows.append({"source_alias": alias, "relative_path": relative, "expected_sha256": digest, "actual_sha256": actual, "status": "passed" if actual == digest else "failed"})
    return rows


def complete_runs(model_id: str) -> list[Path]:
    rows: list[Path] = []
    for path in sorted(FULL_ROOT.glob("HQ-*")):
        status_path = path / "run_status.json"
        if not status_path.is_file():
            continue
        status = json.loads(status_path.read_text(encoding="utf-8"))
        observed_model = ((status.get("descriptor") or {}).get("qa") or {}).get("model_id")
        if status.get("status") != "passed" or observed_model != model_id:
            continue
        if all((path / relative).is_file() for relative in REQUIRED_RUN_ARTIFACTS):
            rows.append(path)
    return rows


def output_manifest_valid(run_dir: Path) -> bool:
    manifest = pd.read_csv(run_dir / "output_manifest.csv", dtype=str, keep_default_na=False)
    for row in manifest.to_dict(orient="records"):
        path = run_dir / row["relative_path"]
        if not path.is_file() or str(path.stat().st_size) != row["size_bytes"] or sha(path) != row["sha256"]:
            return False
    return True


def main() -> None:
    AUDIT.mkdir(parents=True, exist_ok=True)
    sources = pd.DataFrame(source_rows())
    sources.to_csv(AUDIT / "source_identity_audit.csv", index=False, encoding="utf-8-sig")

    notebook = nbformat.read(ROOT / "URP4_1_HQ.ipynb", as_version=4)
    notebook_rows = []
    for index, cell in enumerate(notebook.cells):
        tags = cell.metadata.get("tags", [])
        notebook_rows.append({
            "cell_index": index,
            "cell_id": cell.id,
            "cell_type": cell.cell_type,
            "tags": ";".join(tags),
            "role": "user_edit" if "USER_EDIT_ONLY" in tags else "locked_pipeline_or_explanation",
            "first_line": (cell.source.splitlines() or [""])[0],
        })
    cells = pd.DataFrame(notebook_rows)
    cells.to_csv(AUDIT / "notebook_cell_tree.csv", index=False, encoding="utf-8-sig")

    smoke = pd.read_csv(ROOT / "outputs" / "smoke" / "smoke_results.csv")
    imported_pass = complete_runs("HQ-SMOKE-L28-VF30")
    deterministic = False
    if len(imported_pass) >= 2:
        deterministic = all(
            sha(imported_pass[-2] / rel) == sha(imported_pass[-1] / rel)
            for rel in (
                "descriptor_result.csv",
                "descriptor/tables/slice_pixel_count_table.csv",
                "descriptor/tables/slice_component_table.csv",
                "descriptor/tables/overlay_pixel_table.csv",
                "descriptor/tables/overlay_component_table.csv",
            )
        )
    imported_status = json.loads((imported_pass[-1] / "run_status.json").read_text(encoding="utf-8")) if imported_pass else {}
    fixture_runs = complete_runs("HQ-SMOKE-GENERATED-FIXTURE")
    lattice_runs = complete_runs("HQ-SMOKE-GEN-LATTICE")
    tpms_runs = complete_runs("HQ-SMOKE-GEN-TPMS")
    voxel_runs = complete_runs("HQ-SMOKE-GEN-VOXEL")
    selected_runs = [runs[-1] for runs in (imported_pass, fixture_runs, lattice_runs, tpms_runs, voxel_runs) if runs]
    manifests_valid = len(selected_runs) == 5 and all(output_manifest_valid(path) for path in selected_runs)
    evidence = pd.DataFrame([
        {"gate": "fast_smoke_9_cases", "status": "passed" if (smoke["expected"] == smoke["observed"]).all() else "failed", "evidence": "outputs/smoke/smoke_results.csv"},
        {"gate": "imported_l28_full_P1000_Z801", "status": imported_status.get("status", "missing"), "evidence": str(imported_pass[-1]) if imported_pass else "missing"},
        {"gate": "imported_l28_independent_repeat", "status": "passed" if deterministic else "failed", "evidence": f"exact CSV replay across {len(imported_pass)} completed runs"},
        {"gate": "generated_fixture_full_P1000_Z801", "status": "passed" if fixture_runs else "failed", "evidence": str(fixture_runs[-1]) if fixture_runs else "missing"},
        {"gate": "generated_lattice_full_P1000_Z801", "status": "passed" if lattice_runs else "failed", "evidence": str(lattice_runs[-1]) if lattice_runs else "missing"},
        {"gate": "generated_tpms_full_P1000_Z801", "status": "passed" if tpms_runs else "failed", "evidence": str(tpms_runs[-1]) if tpms_runs else "missing"},
        {"gate": "generated_voxel_full_P1000_Z801", "status": "passed" if voxel_runs else "failed", "evidence": str(voxel_runs[-1]) if voxel_runs else "missing"},
        {"gate": "selected_run_output_manifests", "status": "passed" if manifests_valid else "failed", "evidence": f"verified {len(selected_runs)}/5 latest complete run manifests"},
        {"gate": "source_identity", "status": "passed" if sources["status"].eq("passed").all() else "failed", "evidence": "outputs/hq_audit/source_identity_audit.csv"},
        {"gate": "single_user_edit_cell", "status": "passed" if cells["role"].eq("user_edit").sum() == 1 else "failed", "evidence": "outputs/hq_audit/notebook_cell_tree.csv"},
    ])
    evidence.to_csv(AUDIT / "smoke_and_integration_audit.csv", index=False, encoding="utf-8-sig")

    manifest_rows = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts or path.is_relative_to(ROOT / "outputs"):
            continue
        manifest_rows.append({"relative_path": path.relative_to(ROOT).as_posix(), "size_bytes": path.stat().st_size, "sha256": sha(path)})
    pd.DataFrame(manifest_rows).to_csv(AUDIT / "deliverable_file_manifest.csv", index=False, encoding="utf-8-sig")
    summary = {
        "status": "passed" if evidence["status"].eq("passed").all() else "failed",
        "source_identity_passed": int(sources["status"].eq("passed").sum()),
        "source_identity_total": len(sources),
        "smoke_gate_passed": int(evidence["status"].eq("passed").sum()),
        "smoke_gate_total": len(evidence),
        "deliverable_manifest_files": len(manifest_rows),
        "imported_repeat_exact": deterministic,
    }
    (AUDIT / "audit_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(sources.to_string(index=False))
    print(evidence.to_string(index=False))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if summary["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
