"""One-request Lattice Type-A generator plugin."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from urp4.contracts.v0_1.canonical import canonical_json_bytes, sha256_file, sha256_hex
from urp4.contracts.v0_1.models import GenerationRequest, GeometryArtifact

from .contracts import GENERATOR_ID, SOURCE_PATH, SOURCE_SHA256, build_geometry_artifact
from .descriptors import extract_start_end_structural_factors
from .exporters import export_step_optional, export_stl, mesh_qa
from .graph import create_type_a_model
from .models import ExportAttempt, GenerationConfig, LatticeGeneratorError, LatticeGraph


@dataclass
class GenerationOutcome:
    request: GenerationRequest
    graph: LatticeGraph
    graph_path: Path
    graph_sha256: str
    descriptor_row: dict[str, object]
    export_attempts: list[ExportAttempt]
    geometry_artifacts: list[GeometryArtifact]


def package_code_sha256(root: str | Path) -> str:
    package = Path(root) / "urp4" / "generators" / "lattice_typeab" / "v0_1"
    rows = [{"path": item.relative_to(root).as_posix(), "sha256": sha256_file(item)} for item in sorted(package.glob("*.py"))]
    return sha256_hex(rows)


class LatticeTypeABPlugin:
    def __init__(self, root: str | Path, freecad_library_path: str | None = None):
        self.root = Path(root).resolve()
        self.freecad_library_path = freecad_library_path

    def verify_source(self) -> None:
        path = self.root / SOURCE_PATH
        if not path.is_file():
            raise LatticeGeneratorError(f"immutable source notebook missing: {path}")
        observed = sha256_file(path)
        if observed != SOURCE_SHA256:
            raise LatticeGeneratorError(f"source notebook SHA-256 mismatch: {observed}")

    @staticmethod
    def _config_from_request(request: GenerationRequest) -> GenerationConfig:
        config = dict(request.payload["generation_config"])
        config.pop("model_id", None)
        return GenerationConfig(**config)

    def generate(self, request_document: dict[str, object], output_dir: str | Path) -> GenerationOutcome:
        self.verify_source()
        request = GenerationRequest.from_dict(request_document)
        if request.payload["generator_id"] != GENERATOR_ID or request.payload["generator_family"] != "lattice":
            raise LatticeGeneratorError("request is not for the CINT-04 Lattice Type-A plugin")
        if request.payload["random_seed"] is None or request.payload["target_vf"] is None:
            raise LatticeGeneratorError("Type-A request requires random_seed and target_vf")
        config = self._config_from_request(request)
        model_id = str(request.payload["generation_config"]["model_id"])
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)
        graph = create_type_a_model(
            float(request.payload["target_vf"]), config, np.random.default_rng(int(request.payload["random_seed"]))
        )
        graph_payload = {
            "model_id": model_id, "source_type": graph.source_type, "source_name": graph.source_name,
            "target_vf": graph.target_vf, "actual_vf": graph.actual_vf,
            "nodes": graph.nodes.tolist(), "edges": graph.edges.tolist(), "radii": graph.radii.tolist(),
        }
        graph_path = output / f"{model_id}.graph.json"
        graph_path.write_bytes(canonical_json_bytes(graph_payload))
        attempts: list[ExportAttempt] = []
        artifacts: list[GeometryArtifact] = []
        for geometry_format in request.payload["requested_geometry_formats"]:
            if geometry_format == "stl":
                attempt = export_stl(graph, output / f"{model_id}.stl", config)
                qa = mesh_qa(attempt.path)
                artifacts.append(build_geometry_artifact(
                    request=request, attempt=attempt, model_id=model_id, qa=qa,
                    observed_vf=graph.actual_vf, root=self.root,
                ))
            elif geometry_format in ("stp", "step"):
                attempt = export_step_optional(
                    graph, output / f"{model_id}.stp", config, self.freecad_library_path
                )
            else:
                raise LatticeGeneratorError(f"unsupported geometry format for Type-A v0.1: {geometry_format}")
            attempts.append(attempt)
        return GenerationOutcome(
            request=request, graph=graph, graph_path=graph_path, graph_sha256=sha256_file(graph_path),
            descriptor_row=extract_start_end_structural_factors(model_id, graph, config),
            export_attempts=attempts, geometry_artifacts=artifacts,
        )

