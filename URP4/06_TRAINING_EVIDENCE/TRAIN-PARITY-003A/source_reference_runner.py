from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from adapter_v0_1_1.implementation.contracts import (
    FOLD_MANIFEST_SHA256,
    SOURCE_SHA256,
    TARGET_POLICY_HASH,
    TARGET_REGISTRY,
    WORKBOOK_SHA256,
)
from adapter_v0_1_1.implementation.source_exact_runtime import SourceExactRuntime


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


@dataclass(frozen=True)
class ReferenceExecutionPermit:
    mode: str = "NO_FIT"
    fit_allowed: bool = False
    predict_allowed: bool = False
    source_hash: str = SOURCE_SHA256
    workbook_hash: str = WORKBOOK_SHA256
    fold_hash: str = FOLD_MANIFEST_SHA256
    target_policy_hash: str = TARGET_POLICY_HASH

    def validate(self) -> None:
        if self.mode != "NO_FIT" or self.fit_allowed or self.predict_allowed:
            raise PermissionError("REFERENCE_RUNNER_PERMIT_REJECTED")
        if self.source_hash != SOURCE_SHA256 or self.workbook_hash != WORKBOOK_SHA256:
            raise ValueError("REFERENCE_SOURCE_OR_WORKBOOK_HASH_MISMATCH")
        if self.fold_hash != FOLD_MANIFEST_SHA256:
            raise ValueError("REFERENCE_FOLD_HASH_MISMATCH")
        if self.target_policy_hash != TARGET_POLICY_HASH:
            raise ValueError("REFERENCE_TARGET_POLICY_HASH_MISMATCH")


class IsolatedSourceReferenceRunner:
    """Load protected notebook definitions and bind inputs without numerical execution.

    The runner compiles the hash-bound source's definition AST directly.  It does
    not rewrite numerical logic.  Dynamic notebook state must be injected through
    an explicit binding method.  NO_FIT is the only permit accepted in this gate.
    """

    def __init__(self, source: Path, workbook: Path, fold_manifest: Path):
        if sha256_file(source) != SOURCE_SHA256:
            raise ValueError("SOURCE_HASH_MISMATCH")
        if sha256_file(workbook) != WORKBOOK_SHA256:
            raise ValueError("WORKBOOK_HASH_MISMATCH")
        if sha256_file(fold_manifest) != FOLD_MANIFEST_SHA256:
            raise ValueError("FOLD_HASH_MISMATCH")
        self.source = source
        self.workbook = workbook
        self.fold_manifest = fold_manifest
        self.runtime = SourceExactRuntime(source).compile()
        self.dynamic_state_bound = False
        self.target_packet: dict[str, Any] | None = None

    def bind_dynamic_state(self, *, data_by_output: dict, family_mt_data: dict) -> None:
        self.runtime.bind_dynamic_state(DATA_BY_OUTPUT=data_by_output, FAMILY_MT_DATA=family_mt_data)
        self.dynamic_state_bound = True

    def bind_target(self, target_id: str, outer_repeat: int) -> dict[str, Any]:
        if target_id not in TARGET_REGISTRY:
            raise KeyError(f"UNKNOWN_TARGET: {target_id}")
        rows = []
        with self.fold_manifest.open("r", encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                if row["target_id"] == target_id and row["outer_repeat"] == str(outer_repeat):
                    rows.append(row)
        if not rows:
            raise ValueError("TARGET_FOLD_BINDING_EMPTY")
        target = TARGET_REGISTRY[target_id]
        self.target_packet = {
            "target_id": target_id,
            "excel_col": target["excel_col"],
            "value_hash": target["value_hash"],
            "nan_mask_hash": target["nan_mask_hash"],
            "group_id_membership_hash": target["group_id_membership_hash"],
            "outer_repeat": outer_repeat,
            "fold_rows": len(rows),
            "fold_manifest_sha256": FOLD_MANIFEST_SHA256,
        }
        return dict(self.target_packet)

    def evaluator_signature(self) -> str:
        return self.runtime.signature("evaluate_method_train_test")

    def execute(self, permit: ReferenceExecutionPermit, *args, **kwargs):
        permit.validate()
        if self.target_packet is None:
            raise RuntimeError("REFERENCE_TARGET_NOT_BOUND")
        if not self.dynamic_state_bound:
            raise RuntimeError("REFERENCE_DYNAMIC_STATE_NOT_BOUND")
        raise PermissionError("NO_FIT_PERMIT: protected source evaluator entry blocked")
