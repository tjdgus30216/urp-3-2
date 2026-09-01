from __future__ import annotations

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


def initialize_empty_ledgers(directory: Path):
    directory.mkdir(parents=True, exist_ok=True)
    prediction = directory / "PREDICTION_LEDGER_EMPTY.csv"
    metric = directory / "METRIC_LEDGER_EMPTY.csv"
    pd.DataFrame(columns=PREDICTION_FIELDS).to_csv(prediction, index=False, encoding="utf-8-sig")
    pd.DataFrame(columns=METRIC_FIELDS).to_csv(metric, index=False, encoding="utf-8-sig")
    return prediction, metric


def ledger_status(path: Path):
    frame = pd.read_csv(path)
    return {"path": path.name, "rows": len(frame), "columns": list(frame.columns), "execution_status": "no_fit_no_prediction"}


class PredictionLedgerWriter:
    def append(self, *_args, **_kwargs):
        raise PermissionError("NO_PREDICTION: TRAIN-PARITY-002 permits schema creation only")


class MetricLedgerWriter:
    def append(self, *_args, **_kwargs):
        raise PermissionError("NO_METRIC: TRAIN-PARITY-002 permits schema creation only")
