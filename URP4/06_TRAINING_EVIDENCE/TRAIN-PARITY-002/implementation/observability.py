from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


EVENT_FIELDS = (
    "event_id", "event_type", "timestamp_kst", "target_id", "outer_repeat", "inner_split", "stage_id",
    "row_id", "group_id", "method_id", "estimator_id", "transform_id", "feature_set_hash",
    "random_seed", "container_type", "traversal_order_hash", "tie_count", "tie_break_rule",
    "none_gate", "exception_type", "exception_message", "fallback_id", "parameter_hash",
    "input_identity_hash", "output_identity_hash", "execution_status",
)


@dataclass
class EventRecorder:
    path: Path

    def record(self, event: dict[str, Any]) -> None:
        unknown = set(event) - set(EVENT_FIELDS)
        if unknown:
            raise ValueError(f"OBSERVABILITY_SCHEMA_UNKNOWN_FIELDS: {sorted(unknown)}")
        payload = {field: event.get(field, "") for field in EVENT_FIELDS}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
