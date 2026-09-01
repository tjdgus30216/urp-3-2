"""Bridge CINT-08 static plans into URP4-CONTRACT-v0.1 manifests."""

from __future__ import annotations

import copy
from typing import Any, Mapping

from urp4.contracts.v0_1.ids import build_document
from urp4.contracts.v0_1.models import DatasetManifest, TrainingRunManifest

from .models import TrainingPlan, TrainingPolicyError


def build_pending_training_manifest(
    *,
    plan: TrainingPlan,
    dataset_document: Mapping[str, Any],
    provenance: Mapping[str, Any],
) -> TrainingRunManifest:
    dataset = DatasetManifest.from_dict(dataset_document)
    if dataset.object_id != plan.dataset_manifest_id:
        raise TrainingPolicyError("plan dataset_manifest_id differs from DatasetManifest")
    if dataset.payload["data_sha256"] != plan.dataset_sha256:
        raise TrainingPolicyError("plan dataset_sha256 differs from DatasetManifest")
    payload = {
        "training_run_label": plan.plan_id,
        "dataset_manifest_id": dataset.object_id,
        "dataset_version": dataset.payload["dataset_version"],
        "dataset_sha256": dataset.payload["data_sha256"],
        "target_id": plan.target_id,
        "objective_direction": plan.objective_direction,
        "performance_domain": plan.performance_domain,
        "feature_ids": list(plan.feature_ids),
        "method_id": plan.method_id,
        "split_contract": copy.deepcopy(plan.split_contract),
        "runtime_alias": plan.runtime_alias,
        "result_artifacts": [],
        "leakage_checks": [
            {"check_id": "CINT08-NOFIT", "status": "not_run", "evidence": "Static plan only; no model fit or prediction."},
            {"check_id": "CINT08-GROUPED", "status": "pass", "evidence": "Split contract is grouped and includes base_geometry_id."},
            {"check_id": "CINT08-INVERSE", "status": "not_applicable", "evidence": "Inverse-design claim is prohibited in CINT-08."},
        ],
        "inverse_design_claim_authorized": False,
        "legacy_ids": [],
        "notes": plan.notes,
    }
    document = build_document(
        "TrainingRunManifest",
        payload,
        provenance,
        execution_status="pending",
        scientific_status="unresolved",
    )
    return TrainingRunManifest.from_dict(document)

