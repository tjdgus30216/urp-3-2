"""Fixture-only regression tests for NB-INTEGRATE-001.  No slicer is invoked."""

from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "URP4-1_DELIVERABLE"))

from urp4.route_policy.v0_1 import (  # noqa: E402
    F1_Z400_WARNING,
    ImportRouteRequest,
    RoutePolicyError,
    build_development_manifest,
    decide_route,
)


CONFIG = {
    "axis": "z",
    "algorithm_revision": "ORIENTED_NONZERO_RAW/IMSTL-004/r1",
    "normalization_mode": "uniform_bbox_to_expected",
    "source_mutation": False,
    "mesh_repair": False,
    "stl_to_step_proxy": False,
}
POLICY_HASH = "policy-fixture-sha256"


class RoutePolicyTests(unittest.TestCase):
    def fixture(self) -> tuple[Path, str, tempfile.TemporaryDirectory[str]]:
        directory = tempfile.TemporaryDirectory()
        path = Path(directory.name) / "fixture.stl"
        path.write_bytes(b"solid deterministic fixture; no geometry execution")
        return path, hashlib.sha256(path.read_bytes()).hexdigest(), directory

    def request(self, path: Path, source_hash: str, **overrides: object) -> ImportRouteRequest:
        values: dict[str, object] = {
            "model_id": "C1", "input_mode": "imported", "source_type": "paired_confirmed",
            "source_identity_status": "confirmed", "source_path": str(path),
            "expected_source_sha256": source_hash, "route_config": CONFIG,
            "policy_evidence_sha256": POLICY_HASH,
        }
        values.update(overrides)
        return ImportRouteRequest(**values)

    def test_confirmed_pair_is_development_only(self) -> None:
        path, source_hash, temp = self.fixture()
        with temp:
            decision = decide_route(self.request(path, source_hash))
            self.assertEqual(decision.decision_status, "approved_development")
            self.assertFalse(decision.execution_enabled)
            self.assertFalse(decision.scientific_production_qualified)
            self.assertEqual(decision.warning_flags, ())

    def test_f1_warning_propagates_to_manifest(self) -> None:
        path, source_hash, temp = self.fixture()
        with temp:
            request = self.request(path, source_hash, model_id="F1")
            decision = decide_route(request)
            manifest = build_development_manifest(request, decision, command=[sys.executable, "fixture"])
            self.assertIn(F1_Z400_WARNING, decision.warning_flags)
            self.assertIn(F1_Z400_WARNING, manifest["decision"]["warning_flags"])
            self.assertFalse(manifest["execution"]["slice_executed"])

    def test_hash_mismatch_fails_closed(self) -> None:
        path, _, temp = self.fixture()
        with temp:
            with self.assertRaisesRegex(RoutePolicyError, "SRC-006"):
                decide_route(self.request(path, "0" * 64))

    def test_likely_pair_fails_closed(self) -> None:
        path, source_hash, temp = self.fixture()
        with temp:
            with self.assertRaisesRegex(RoutePolicyError, "SRC-001"):
                decide_route(self.request(path, source_hash, source_type="paired_likely", source_identity_status="likely"))

    def test_stl_only_fails_closed(self) -> None:
        path, source_hash, temp = self.fixture()
        with temp:
            with self.assertRaisesRegex(RoutePolicyError, "SRC-001"):
                decide_route(self.request(path, source_hash, source_type="stl_only_imported", source_identity_status="unresolved"))

    def test_orientation_hold_fails_closed(self) -> None:
        path, source_hash, temp = self.fixture()
        with temp:
            with self.assertRaisesRegex(RoutePolicyError, "SRC-001"):
                decide_route(self.request(path, source_hash, source_type="orientation_held_pair", source_identity_status="hold"))

    def test_production_request_fails_closed(self) -> None:
        path, source_hash, temp = self.fixture()
        with temp:
            with self.assertRaisesRegex(RoutePolicyError, "POL-001"):
                decide_route(self.request(path, source_hash, production_requested=True))

    def test_repair_config_fails_closed(self) -> None:
        path, source_hash, temp = self.fixture()
        with temp:
            config = {**CONFIG, "hole_fill": False}
            with self.assertRaisesRegex(RoutePolicyError, "CFG-003"):
                decide_route(self.request(path, source_hash, route_config=config))

    def test_generated_clean_route_is_status_only(self) -> None:
        request = ImportRouteRequest(
            model_id="GEN-V001", input_mode="generated", source_type="generated_controlled_stl_topology_clean",
            source_identity_status="controlled", topology_clean=True, policy_evidence_sha256=POLICY_HASH,
        )
        decision = decide_route(request)
        self.assertEqual(decision.decision_status, "approved_development")
        self.assertFalse(decision.execution_enabled)


if __name__ == "__main__":
    unittest.main(verbosity=2)
