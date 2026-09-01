from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from .models import ExecLayerContractError, ExecutionPermit


DATASET_ID = "DATASET::DATASET-XREG-GM-FS4-V0.1::sha256-33aa35ce6c7f"
ADAPTER_VERSION = "FS4-P1-ADAPTER-v0.1"
EXEC_LAYER_VERSION = "FS4-P1-EXEC-LAYER-v0.1"
METHOD_IDS = tuple(f"FS4-METHOD-0{index}" for index in range(1, 5))
OUTER_FOLDS = tuple(f"FS4-P1-OUT-{family}" for family in "BCFLT")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical_payload(doc: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "authorization_contract_id": doc.get("authorization_contract_id"),
        "dataset_manifest_id": doc.get("dataset_manifest_id"),
        "adapter_contract_version": doc.get("adapter_contract_version"),
        "executable_layer_version": doc.get("executable_layer_version"),
        "allowed_method_family_ids": list(doc.get("allowed_method_family_ids", ())),
        "allowed_outer_fold_ids": list(doc.get("allowed_outer_fold_ids", ())),
        "max_estimator_fits": doc.get("max_estimator_fits"),
        "execution_authorized": doc.get("execution_authorized"),
    }


def _payload_sha256(doc: Mapping[str, Any]) -> str:
    encoded = json.dumps(_canonical_payload(doc), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_execution_permit(path: str | Path, *, expected_file_sha256: str) -> ExecutionPermit:
    permit_path = Path(path).resolve()
    if not expected_file_sha256 or len(expected_file_sha256) != 64:
        raise ExecLayerContractError("an explicit 64-character permit file hash is required")
    actual_file_hash = _sha256(permit_path)
    if actual_file_hash != expected_file_sha256:
        raise ExecLayerContractError("execution permit file hash mismatch")
    doc = json.loads(permit_path.read_text(encoding="utf-8"))
    payload_hash = _payload_sha256(doc)
    if doc.get("permit_payload_sha256") != payload_hash:
        raise ExecLayerContractError("execution permit payload hash mismatch")
    if not str(doc.get("authorization_contract_id", "")).startswith("FS4-P1-AUTH2-"):
        raise ExecLayerContractError("permit is not an AUTH2 contract")
    if doc.get("dataset_manifest_id") != DATASET_ID:
        raise ExecLayerContractError("permit dataset identity mismatch")
    if doc.get("adapter_contract_version") != ADAPTER_VERSION:
        raise ExecLayerContractError("permit adapter version mismatch")
    if doc.get("executable_layer_version") != EXEC_LAYER_VERSION:
        raise ExecLayerContractError("permit executable-layer version mismatch")
    if tuple(doc.get("allowed_method_family_ids", ())) != METHOD_IDS:
        raise ExecLayerContractError("permit method roster mismatch")
    if tuple(doc.get("allowed_outer_fold_ids", ())) != OUTER_FOLDS:
        raise ExecLayerContractError("permit outer-fold roster mismatch")
    if int(doc.get("max_estimator_fits", 0)) > 4000 or int(doc.get("max_estimator_fits", 0)) < 1535:
        raise ExecLayerContractError("permit fit ceiling is outside the frozen P1 envelope")
    if doc.get("execution_authorized") is not True:
        raise ExecLayerContractError("permit does not authorize execution")
    return ExecutionPermit(
        authorization_contract_id=str(doc["authorization_contract_id"]),
        dataset_manifest_id=str(doc["dataset_manifest_id"]),
        adapter_contract_version=str(doc["adapter_contract_version"]),
        executable_layer_version=str(doc["executable_layer_version"]),
        allowed_method_family_ids=tuple(doc["allowed_method_family_ids"]),
        allowed_outer_fold_ids=tuple(doc["allowed_outer_fold_ids"]),
        max_estimator_fits=int(doc["max_estimator_fits"]),
        execution_authorized=True,
        permit_payload_sha256=payload_hash,
        source_path=str(permit_path),
        source_file_sha256=actual_file_hash,
    )


def assert_execution_authorized(
    permit: ExecutionPermit | None,
    *,
    method_family_id: str,
    outer_fold_id: str,
    prospective_fit_count: int,
) -> None:
    # This check must remain the first operation in every fit/predict method.
    if permit is None:
        raise ExecLayerContractError("AUTH2 execution permit is absent")
    if permit.execution_authorized is not True:
        raise ExecLayerContractError("AUTH2 execution permit is not authorized")
    if permit.dataset_manifest_id != DATASET_ID:
        raise ExecLayerContractError("runtime permit dataset mismatch")
    if permit.adapter_contract_version != ADAPTER_VERSION or permit.executable_layer_version != EXEC_LAYER_VERSION:
        raise ExecLayerContractError("runtime permit version mismatch")
    if method_family_id not in permit.allowed_method_family_ids:
        raise ExecLayerContractError("method is not authorized by permit")
    if outer_fold_id not in permit.allowed_outer_fold_ids:
        raise ExecLayerContractError("outer fold is not authorized by permit")
    if prospective_fit_count > permit.max_estimator_fits:
        raise ExecLayerContractError("prospective fit count exceeds permit ceiling")
