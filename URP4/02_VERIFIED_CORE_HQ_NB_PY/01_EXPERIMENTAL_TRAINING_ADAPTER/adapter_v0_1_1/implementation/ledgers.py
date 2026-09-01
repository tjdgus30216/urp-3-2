from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


PREDICTION_FIELDS = (
    "execution_status", "target_id", "outer_repeat", "fold_id", "row_id", "group_id", "y_true", "y_pred",
    "method_id", "estimator_id", "transform_id", "feature_set_hash", "fold_manifest_hash", "source_hash",
    "adapter_version", "config_hash",
)
METRIC_FIELDS = (
    "execution_status", "target_id", "repeat", "fold_id", "metric_name", "metric_value",
    "prediction_ledger_hash", "aggregation_level", "sample_count",
)


@dataclass
class SchemaOnlyLedgerWriter:
    path: Path
    fields: tuple[str, ...]
    kind: str

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(columns=self.fields).to_csv(self.path, index=False, encoding="utf-8-sig")

    def append(self, *_args, **_kwargs) -> None:
        raise PermissionError(f"NO_{self.kind.upper()}_WRITE: TRAIN-PARITY-002A is schema-only")

    def row_count(self) -> int:
        return len(pd.read_csv(self.path))
