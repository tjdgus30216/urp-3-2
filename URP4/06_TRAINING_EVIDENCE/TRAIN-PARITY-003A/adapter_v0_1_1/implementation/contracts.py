from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .hashing import canonical_hash


ADAPTER_VERSION = "TRAIN-2ND-NEWFEATURE-EXACT-ADAPTER-v0.1.1"
SOURCE_SHA256 = "11129a41bd4303d82c599148cd761adb3c858f58da017586e07fb0f06d055ff2"
WORKBOOK_SHA256 = "4a6ec7d03d92fa25851998689768d9db9f63227f00e778a528d758b368851dce"
FOLD_MANIFEST_SHA256 = "3b18913ef68b6487b273a113ab3b3c0569d3246444f17003f68c0e01af1e89a6"
TOLERANCE_REVISION = "TRAIN-PARITY-TOL-v0.1"
POLICY_PATH = Path(__file__).resolve().parents[2] / "TRAIN_TARGET_POLICY_V0_2.json"
TARGET_POLICY = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
TARGET_POLICY_HASH = TARGET_POLICY["policy_hash"]
TARGET_REGISTRY = {item["target_id"]: item for item in TARGET_POLICY["canonical_targets"]}
TARGETS = tuple(TARGET_REGISTRY)
HOLD_TARGETS = frozenset(TARGET_POLICY["hold_target_ids"])
PRIMARY_TARGETS = frozenset(TARGET_POLICY["primary_target_ids"])
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


@dataclass(frozen=True)
class ExecutionPermit:
    mode: str = "NO_FIT"
    source_hash: str = SOURCE_SHA256
    workbook_hash: str = WORKBOOK_SHA256
    fold_manifest_hash: str = FOLD_MANIFEST_SHA256
    target_policy_hash: str = TARGET_POLICY_HASH
    tolerance_revision: str = TOLERANCE_REVISION
    fit_allowed: bool = False
    predict_allowed: bool = False

    def validate(self) -> None:
        if self.mode != "NO_FIT" or self.fit_allowed or self.predict_allowed:
            raise PermissionError("EXECUTION_PERMIT_REJECTED: v0.1.1 accepts NO_FIT only")
        if self.source_hash != SOURCE_SHA256:
            raise ValueError("EXECUTION_PERMIT_SOURCE_HASH_MISMATCH")
        if self.workbook_hash != WORKBOOK_SHA256:
            raise ValueError("EXECUTION_PERMIT_WORKBOOK_HASH_MISMATCH")
        if self.fold_manifest_hash != FOLD_MANIFEST_SHA256:
            raise ValueError("EXECUTION_PERMIT_FOLD_HASH_MISMATCH")
        if self.target_policy_hash != TARGET_POLICY_HASH:
            raise ValueError("EXECUTION_PERMIT_TARGET_POLICY_HASH_MISMATCH")
        if self.tolerance_revision != TOLERANCE_REVISION:
            raise ValueError("EXECUTION_PERMIT_TOLERANCE_MISMATCH")


@dataclass(frozen=True)
class BranchRequest:
    dataset_manifest_id: str
    dataset_manifest_hash: str
    target_id: str
    target_excel_col: str
    target_value_hash: str
    target_nan_mask_hash: str
    target_display_name: str
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
        if self.target_id not in TARGET_REGISTRY:
            raise KeyError(f"UNKNOWN_TARGET: {self.target_id}")
        expected = TARGET_REGISTRY[self.target_id]
        if self.target_excel_col != expected["excel_col"]:
            raise ValueError("TARGET_EXCEL_COLUMN_IDENTITY_MISMATCH")
        if self.target_value_hash != expected["value_hash"]:
            raise ValueError("TARGET_VALUE_HASH_MISMATCH")
        if self.target_nan_mask_hash != expected["nan_mask_hash"]:
            raise ValueError("TARGET_NAN_MASK_HASH_MISMATCH")
        if self.target_display_name != expected["display_name"]:
            raise ValueError("TARGET_DISPLAY_METADATA_MISMATCH")
        if self.branch_id not in known_branch_ids:
            raise KeyError(f"UNKNOWN_BRANCH: {self.branch_id}")
        if self.fold_manifest_hash != permit.fold_manifest_hash:
            raise ValueError("REQUEST_FOLD_HASH_MISMATCH")
        if len(self.row_group_identity_hash) != 64 or len(self.config_hash) != 64:
            raise ValueError("REQUEST_IDENTITY_HASH_INVALID")
        if self.prediction_ledger_writer is None or self.metric_ledger_writer is None:
            raise ValueError("LEDGER_WRITER_HANDLE_MISSING")
        if self.deterministic_runtime_hash != canonical_hash(RUNTIME_CONTRACT):
            raise ValueError("RUNTIME_CONTRACT_HASH_MISMATCH")
        if self.target_policy_hash != TARGET_POLICY_HASH:
            raise ValueError("TARGET_POLICY_HASH_MISMATCH")
        if self.final_refit_requested and self.target_id in HOLD_TARGETS:
            raise PermissionError(f"FINAL_REFIT_HOLD: {self.target_id}")


def fixture_request(branch_id: str, prediction_writer: Any, metric_writer: Any, target_id: str = "TRAIN2NF::HI") -> BranchRequest:
    target = TARGET_REGISTRY[target_id]
    return BranchRequest(
        dataset_manifest_id="FIXTURE::SYNTHETIC-NO-FIT-v0.1.1",
        dataset_manifest_hash="a" * 64,
        target_id=target_id,
        target_excel_col=target["excel_col"],
        target_value_hash=target["value_hash"],
        target_nan_mask_hash=target["nan_mask_hash"],
        target_display_name=target["display_name"],
        fold_manifest_path="artifacts/SHARED_FOLD_MANIFEST.csv",
        fold_manifest_hash=FOLD_MANIFEST_SHA256,
        row_group_identity_hash=target["group_id_membership_hash"],
        branch_id=branch_id,
        deterministic_runtime_hash=canonical_hash(RUNTIME_CONTRACT),
        target_policy_hash=TARGET_POLICY_HASH,
        config_hash="c" * 64,
        prediction_ledger_writer=prediction_writer,
        metric_ledger_writer=metric_writer,
    )
