from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from .hashing import canonical_hash


EVENT_TYPES = (
    "branch_enter", "permit_denied", "branch_exit", "none_return", "exception", "suppressed_exception",
    "unordered_traversal", "tie_detected", "tie_break", "fallback", "feature_order", "candidate",
    "parameter", "random_seed", "final_refit_state",
)


@dataclass
class EventBuffer:
    events: list[dict[str, Any]] = field(default_factory=list)

    def emit(self, event_type: str, **payload: Any) -> None:
        if event_type not in EVENT_TYPES:
            raise ValueError(f"UNKNOWN_EVENT_TYPE: {event_type}")
        self.events.append({
            "event_index": len(self.events),
            "event_type": event_type,
            "payload": payload,
            "payload_hash": canonical_hash(payload),
            "execution_status": "no_fit_no_prediction",
        })

    def write(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            for event in self.events:
                handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")


class SourceTrace:
    """Observation-only Python trace for future authorized source calls."""

    def __init__(self, buffer: EventBuffer, source_filename: str):
        self.buffer = buffer
        self.source_filename = source_filename

    def _trace(self, frame, event, arg):
        if frame.f_code.co_filename == self.source_filename:
            if event == "exception":
                exc_type, exc_value, _ = arg
                self.buffer.emit("exception", function=frame.f_code.co_name, line=frame.f_lineno, exception_type=exc_type.__name__, message=str(exc_value))
            elif event == "return" and arg is None:
                self.buffer.emit("none_return", function=frame.f_code.co_name, line=frame.f_lineno)
        return self._trace

    def __enter__(self):
        sys.settrace(self._trace)
        return self

    def __exit__(self, *_exc):
        sys.settrace(None)


def wrap_observable(runtime, name: str, buffer: EventBuffer):
    original = runtime.function(name)
    if name == "build_corr_blocks":
        def wrapper(x_frame, *args, **kwargs):
            columns = list(x_frame.columns)
            buffer.emit("unordered_traversal", function=name, container="set", input_order=columns, input_order_hash=canonical_hash(columns))
            result = original(x_frame, *args, **kwargs)
            buffer.emit("unordered_traversal", function=name, result_order=result, result_order_hash=canonical_hash(result))
            return result
    elif name == "choose_within_tolerance":
        def wrapper(rows_df, *args, **kwargs):
            result = original(rows_df, *args, **kwargs)
            if len(rows_df):
                best = rows_df["score_obj"].max() if "score_obj" in rows_df else None
                ties = int((rows_df["score_obj"] == best).sum()) if best is not None else 0
                if ties > 1:
                    buffer.emit("tie_detected", function=name, tie_count=ties, best_score=best)
                    buffer.emit("tie_break", function=name, rule="score_obj desc; n_features asc; complexity_rank asc", selected=result)
            return result
    else:
        def wrapper(*args, **kwargs):
            try:
                result = original(*args, **kwargs)
            except Exception as exc:
                buffer.emit("exception", function=name, exception_type=type(exc).__name__, message=str(exc))
                raise
            if result is None:
                buffer.emit("none_return", function=name)
            return result
    runtime.namespace[name] = wrapper
    return wrapper
