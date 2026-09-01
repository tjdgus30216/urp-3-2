from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .hashing import canonical_hash


SOURCE_SHA256 = "11129a41bd4303d82c599148cd761adb3c858f58da017586e07fb0f06d055ff2"
WORKBOOK_SHA256 = "4a6ec7d03d92fa25851998689768d9db9f63227f00e778a528d758b368851dce"
FOLD_MANIFEST_SHA256 = "3b18913ef68b6487b273a113ab3b3c0569d3246444f17003f68c0e01af1e89a6"
TOLERANCE_REVISION = "TRAIN-PARITY-TOL-v0.1"
RUNTIME_CONTRACT = {
    "python": "3.12.12",
    "environment": "project-local KMK312",
    "PYTHONHASHSEED": "42",
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "CUDA_VISIBLE_DEVICES": "-1",
    "n_jobs": 1,
}
HOLD_TARGETS = frozenset(("TRAIN2NF::FW", "TRAIN2NF::GA", "TRAIN2NF::HE"))
TARGETS = tuple(f"TRAIN2NF::{col}" for col in ("FW", "FX", "FZ", "GA", "GC", "GG", "GJ", "GZ", "HA", "HB", "HC", "HD", "HE", "HG", "HI", "HK"))


@dataclass(frozen=True)
class ExecutionPermit:
    mode: str = "NO_FIT"
    source_hash: str = SOURCE_SHA256
    fold_manifest_hash: str = FOLD_MANIFEST_SHA256
    tolerance_revision: str = TOLERANCE_REVISION
    fit_allowed: bool = False
    predict_allowed: bool = False

    def validate(self) -> None:
        if self.mode != "NO_FIT" or self.fit_allowed or self.predict_allowed:
            raise PermissionError("EXECUTION_PERMIT_REJECTED: TRAIN-PARITY-002A accepts NO_FIT only")
        if self.source_hash != SOURCE_SHA256:
            raise ValueError("EXECUTION_PERMIT_SOURCE_HASH_MISMATCH")
        if self.fold_manifest_hash != FOLD_MANIFEST_SHA256:
            raise ValueError("EXECUTION_PERMIT_FOLD_HASH_MISMATCH")
        if self.tolerance_revision != TOLERANCE_REVISION:
            raise ValueError("EXECUTION_PERMIT_TOLERANCE_MISMATCH")


@dataclass(frozen=True)
class BranchRequest:
    dataset_manifest_id: str
    dataset_manifest_hash: str
    target_id: str
    fold_manifest_path: str
    fold_manifest_hash: str
    row_group_identity_hash: str
    branch_id: str
    deterministic_runtime_hash: str
    target_policy_hash: str
    config_hash: str
    prediction_ledger_writer: Any
    metric_ledger_writer: Any
    final_refit_state: str = "not_requested"
    final_refit_requested: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self, permit: ExecutionPermit, known_branch_ids: set[str]) -> None:
        permit.validate()
        if not self.dataset_manifest_id or len(self.dataset_manifest_hash) != 64:
            raise ValueError("DATASET_MANIFEST_CONTRACT_INVALID")
        if self.target_id not in TARGETS:
            raise KeyError(f"UNKNOWN_TARGET: {self.target_id}")
        if self.branch_id not in known_branch_ids:
            raise KeyError(f"UNKNOWN_BRANCH: {self.branch_id}")
        if self.fold_manifest_hash != permit.fold_manifest_hash:
            raise ValueError("REQUEST_FOLD_HASH_MISMATCH")
        if len(self.row_group_identity_hash) != 64 or len(self.config_hash) != 64:
            raise ValueError("REQUEST_IDENTITY_HASH_INVALID")
        if self.prediction_ledger_writer is None or self.metric_ledger_writer is None:
            raise ValueError("LEDGER_WRITER_HANDLE_MISSING")
        expected_runtime = canonical_hash(RUNTIME_CONTRACT)
        if self.deterministic_runtime_hash != expected_runtime:
            raise ValueError("RUNTIME_CONTRACT_HASH_MISMATCH")
        expected_policy = canonical_hash({"targets": TARGETS, "hold": sorted(HOLD_TARGETS), "primary": 13})
        if self.target_policy_hash != expected_policy:
            raise ValueError("TARGET_POLICY_HASH_MISMATCH")
        if self.final_refit_requested and self.target_id in HOLD_TARGETS:
            raise PermissionError(f"FINAL_REFIT_HOLD: {self.target_id}")


def fixture_request(branch_id: str, prediction_writer: Any, metric_writer: Any, target_id: str = "TRAIN2NF::FX") -> BranchRequest:
    return BranchRequest(
        dataset_manifest_id="FIXTURE::SYNTHETIC-NO-FIT-v0.1",
        dataset_manifest_hash="a" * 64,
        target_id=target_id,
        fold_manifest_path="artifacts/SHARED_FOLD_MANIFEST.csv",
        fold_manifest_hash=FOLD_MANIFEST_SHA256,
        row_group_identity_hash="b" * 64,
        branch_id=branch_id,
        deterministic_runtime_hash=canonical_hash(RUNTIME_CONTRACT),
        target_policy_hash=canonical_hash({"targets": TARGETS, "hold": sorted(HOLD_TARGETS), "primary": 13}),
        config_hash="c" * 64,
        prediction_ledger_writer=prediction_writer,
        metric_ledger_writer=metric_writer,
    )
