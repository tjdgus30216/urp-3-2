"""CINT-01-compatible contract adaptation for frozen RUN-139 observations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from urp4.contracts.v0_1.canonical import normalize_relative_path, sha256_file, sha256_hex
from urp4.contracts.v0_1.ids import build_document
from urp4.contracts.v0_1.validation import validate_document

from .service import RUN139_BACKEND_ID


def _rel(root: Path, path: Path) -> str:
    return normalize_relative_path(path.resolve().relative_to(root.resolve()).as_posix())


def _source_ref(root: Path, alias: str, path: Path, role: str) -> dict[str, str]:
    return {"source_alias": alias, "path": _rel(root, path), "sha256": sha256_file(path), "role": role}


def _provenance(
    *,
    aliases: list[str],
    artifacts: list[dict[str, str]],
    parents: list[str],
    code_id: str,
    code_sha256: str,
    config_id: str,
    config_sha256: str,
    notes: str,
    producer: str = "CINT-01-contract-harness",
) -> dict[str, Any]:
    return {
        "producer": producer,
        "runtime_alias": "KMK312",
        "source_aliases": aliases,
        "source_artifacts": artifacts,
        "parent_object_ids": parents,
        "code_identity": {"id": code_id, "sha256": code_sha256},
        "config_identity": {"id": config_id, "sha256": config_sha256},
        "notes": notes,
    }


def geometry_reference_documents(root: str | Path) -> dict[str, dict[str, Any]]:
    """Build identity-complete read-only geometry references for all 58 models.

    The previously published B3 CINT-01 fixture is reused byte-for-byte. Other
    models receive new metadata-only references; no geometry is generated.
    """

    project_root = Path(root).resolve()
    lab = project_root / "experiments" / "lab_001_xy_connection_20260626"
    table = lab / "reports" / "tables"
    registry_path = table / "R09-20260715_final_canonical_geometry_registry.csv"
    registry = pd.read_csv(registry_path, dtype=str, keep_default_na=False)
    cint01_fixture = lab / "factories" / "CINT-01" / "fixtures" / "geometry_artifact.example.json"
    cint01_generation = lab / "factories" / "CINT-01" / "fixtures" / "generation_request.example.json"
    b3_geometry = json.loads(cint01_fixture.read_text(encoding="utf-8-sig"))
    b3_generation = json.loads(cint01_generation.read_text(encoding="utf-8-sig"))
    validate_document(b3_geometry, expected_type="GeometryArtifact")
    validate_document(b3_generation, expected_type="GenerationRequest")

    adapter_code = Path(__file__).resolve()
    output: dict[str, dict[str, Any]] = {
        "B3": {"generation": b3_generation, "geometry": b3_geometry}
    }
    for _, row in registry.iterrows():
        model_id = str(row["model_id"])
        if model_id == "B3":
            continue
        raw_path = project_root / str(row["canonical_stl_path"])
        processed_path = project_root / str(row["processed_file"])
        extents = [float(row[f"source_extent_{axis}_mm"]) for axis in "xyz"]
        scales = [40.0 / value for value in extents]
        family_code = model_id[0]
        generation_config = {
            "normalization_policy_id": "R09-N40-CANONICAL-v0.1",
            "source_geometry_format": "stl",
            "execution_performed_in_cint03": False,
            "axis_scaling": "per-axis-to-40mm",
        }
        theta = [
            {
                "parameter_id": f"THETA-N40-SCALE-{axis.upper()}",
                "raw_parameter_name": f"scale_{axis}",
                "normalized_name": f"axis_scale_ratio_{axis}",
                "value": scales[index],
                "unit": "dimensionless",
                "value_type": "continuous",
                "applicable_family": [family_code],
            }
            for index, axis in enumerate("xyz")
        ]
        generation_payload = {
            "generator_id": "GEN-EXTERNAL-IMPORT-REFERENCE-STL-v0.1",
            "generator_version": "0.1",
            "generator_family": "external_import",
            "theta_schema_id": "THETA-N40-AXIS-SCALE-v0.1",
            "theta_values": theta,
            "generation_config": generation_config,
            "physical_size_mm": {"x": 40.0, "y": 40.0, "z": 40.0},
            "target_vf": None,
            "random_seed": None,
            "requested_geometry_formats": ["stl"],
            "base_geometry_id": f"BASEGEOM::{model_id}",
            "legacy_ids": [model_id, str(row["canonical_source_id"])],
            "notes": "Contract-only adaptation of an existing N40 artifact; no generation executed in CINT-03.",
        }
        generation = build_document(
            "GenerationRequest",
            generation_payload,
            _provenance(
                aliases=[f"REF-STL-{model_id}", "R09-N40-ALL58"],
                artifacts=[_source_ref(project_root, f"REF-STL-{model_id}", raw_path, "raw_geometry")],
                parents=[],
                code_id="CINT-03-GEOMETRY-REGISTRY-ADAPTER",
                code_sha256=sha256_file(adapter_code),
                config_id="R09-N40-CANONICAL-v0.1",
                config_sha256=sha256_hex(generation_config),
                notes="Existing artifact wrapped without mutating source geometry.",
                producer="CINT-03-descriptor-service-harness",
            ),
            execution_status="passed",
            scientific_status="confirmed" if row["model_to_excel_identity_status"] == "confirmed" else "likely",
            created_at_utc="2026-07-19T00:00:00Z",
        )
        geometry_payload = {
            "model_id": model_id,
            "base_geometry_id": f"BASEGEOM::{model_id}",
            "model_family": str(row["model_family"]),
            "geometry_role": "normalized",
            "geometry_format": "stl",
            "path": _rel(project_root, processed_path),
            "geometry_sha256": str(row["processed_sha256"]),
            "size_bytes": processed_path.stat().st_size,
            "units": "mm",
            "physical_size_mm": {"x": 40.0, "y": 40.0, "z": 40.0},
            "generation_request_id": generation["object_id"],
            "parent_geometry_artifact_id": None,
            "observed_vf": None,
            "qa": {
                "technical_status": str(row["final_geometry_gate"]),
                "topology_status": str(row["processed_topology_status"]),
                "connected_region_count": int(row["processed_connected_region_count"]),
                "boundary_edge_count": int(row["processed_boundary_edge_count"]),
                "nonmanifold_edge_count": int(row["processed_nonmanifold_edge_count"]),
            },
            "legacy_ids": [model_id, str(row["canonical_source_id"])],
            "notes": "N40 processed artifact from the frozen canonical geometry registry.",
        }
        scientific = "confirmed" if row["model_to_excel_identity_status"] == "confirmed" else "likely"
        geometry = build_document(
            "GeometryArtifact",
            geometry_payload,
            _provenance(
                aliases=["R09-N40-ALL58", f"REF-STL-{model_id}"],
                artifacts=[
                    _source_ref(project_root, "R09-CANONICAL-GEOMETRY-REGISTRY", registry_path, "identity_registry"),
                    _source_ref(project_root, f"REF-STL-{model_id}-N40", processed_path, "geometry"),
                ],
                parents=[generation["object_id"]],
                code_id="CINT-03-GEOMETRY-REGISTRY-ADAPTER",
                code_sha256=sha256_file(adapter_code),
                config_id="R09-N40-CANONICAL-v0.1",
                config_sha256=sha256_hex(generation_config),
                notes="Metadata adapter only; N40 geometry bytes predate CINT-03.",
                producer="CINT-03-descriptor-service-harness",
            ),
            execution_status="passed",
            scientific_status=scientific,
            created_at_utc="2026-07-19T00:00:01Z",
        )
        validate_document(generation, expected_type="GenerationRequest")
        validate_document(geometry, expected_type="GeometryArtifact")
        output[model_id] = {"generation": generation, "geometry": geometry}
    if len(output) != 58:
        raise ValueError(f"expected 58 geometry references, got {len(output)}")
    return output


def descriptor_documents(root: str | Path, frozen_rows: pd.DataFrame) -> list[dict[str, Any]]:
    """Convert frozen RUN-139 observations without changing their semantic IDs."""

    project_root = Path(root).resolve()
    lab = project_root / "experiments" / "lab_001_xy_connection_20260626"
    table = lab / "reports" / "tables"
    descriptor_result = table / "R09-RESLICE-003_descriptor_result_20260715.csv"
    formula_registry = table / "R09-RESLICE-003_formula_registry_20260715.csv"
    descriptor_schema = table / "R09-DESC-001_descriptor_schema_v0_1_20260715.csv"
    factory_freeze = table / "R09-RESLICE-003_factory_freeze_20260715.json"
    descriptor_code = lab / "scripts" / "R09_RESLICE_003_all58_resumable_factory.py"
    freeze = json.loads(factory_freeze.read_text(encoding="utf-8"))
    schema = pd.read_csv(descriptor_schema, dtype=str, keep_default_na=False)
    schema = schema[schema["descriptor_id"].str.match(r"^XRV1-F00[1-8]$")]
    schema_by_id = {row["descriptor_id"]: row for _, row in schema.iterrows()}
    references = geometry_reference_documents(project_root)
    documents: list[dict[str, Any]] = []
    for _, row in frozen_rows.iterrows():
        model_id = str(row["model_id"])
        formula_id = str(row["formula_id"])
        geometry = references[model_id]["geometry"]
        schema_row = schema_by_id[formula_id]
        applicable = [item for item in schema_row["applicable_family"].split("/") if item]
        payload = {
            "descriptor_schema_version": freeze["schema_version"],
            "descriptor_schema_sha256": freeze["schema_hash"],
            "geometry_artifact_id": geometry["object_id"],
            "geometry_sha256": geometry["payload"]["geometry_sha256"],
            "descriptor_id": formula_id,
            "formula_id": formula_id,
            "population_id": str(row["population_id"]),
            "backend_id": RUN139_BACKEND_ID,
            "statistic": str(row["statistic"]),
            "unit": str(row["unit"]),
            "value": float(row["value"]),
            "population_n": int(row["population_n"]),
            "applicable_family": applicable,
            "scientific_status": str(schema_row["scientific_status"]),
            "modeling_status": str(schema_row["modeling_status"]),
            "scalar_output_id": "PENDING",
            "run_id": freeze["run_id"],
            "artifact_refs": [
                {
                    "artifact_kind": "descriptor_result_table",
                    "path": _rel(project_root, descriptor_result),
                    "sha256": sha256_file(descriptor_result),
                },
                {
                    "artifact_kind": "formula_registry",
                    "path": _rel(project_root, formula_registry),
                    "sha256": sha256_file(formula_registry),
                },
            ],
            "legacy_ids": [formula_id, f"RUN-139::{model_id}::{formula_id}"],
            "notes": "Actual RUN-139 scalar adapted without recalculation.",
        }
        document = build_document(
            "DescriptorResult",
            payload,
            _provenance(
                aliases=["X_RESLICE_V1", "R09-RESLICE-003", "DESCRIPTOR-SCHEMA-v0.1"],
                artifacts=[
                    _source_ref(project_root, "R09-RESLICE-003-RESULT", descriptor_result, "descriptor_values"),
                    _source_ref(project_root, "DESCRIPTOR-SCHEMA-v0.1", descriptor_schema, "descriptor_schema"),
                    _source_ref(project_root, "R09-RESLICE-003-FREEZE", factory_freeze, "factory_freeze"),
                ],
                parents=[geometry["object_id"]],
                code_id="R09-RESLICE-003-SCRIPT",
                code_sha256=sha256_file(descriptor_code),
                config_id="R09-RESLICE-003-CONFIG",
                config_sha256=freeze["config_hash"],
                notes="Formula/population/backend are independently named; value was not recomputed.",
            ),
            execution_status="passed",
            scientific_status=str(schema_row["scientific_status"]),
            created_at_utc="2026-07-19T00:00:02Z",
        )
        validate_document(document, expected_type="DescriptorResult")
        documents.append(document)
    if len(documents) != 522:
        raise ValueError(f"expected 522 descriptor documents, got {len(documents)}")
    return documents
