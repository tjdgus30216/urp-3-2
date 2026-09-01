"""Canonical serialization and filesystem identity helpers.

Canonical JSON is UTF-8, key-sorted, compact, and rejects non-finite numbers.
Timestamps, local paths, notes, and review state are deliberately omitted by the
object-specific identity builders in :mod:`urp4.contracts.v0_1.ids`.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path, PurePosixPath
from typing import Any


SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class CanonicalizationError(ValueError):
    """Raised when a value cannot be represented in canonical contract JSON."""


def _assert_finite(value: Any, path: str = "$") -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise CanonicalizationError(f"non-finite number at {path}")
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str):
                raise CanonicalizationError(f"non-string mapping key at {path}")
            _assert_finite(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _assert_finite(child, f"{path}[{index}]")
    elif isinstance(value, Path):
        raise CanonicalizationError(f"Path objects must be normalized to strings at {path}")


def canonical_json_bytes(value: Any) -> bytes:
    """Return deterministic UTF-8 JSON bytes for an identity payload."""

    _assert_finite(value)
    try:
        text = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise CanonicalizationError(str(exc)) from exc
    return text.encode("utf-8")


def sha256_hex(value: Any) -> str:
    """Hash a canonical JSON value."""

    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_sha256(value: str) -> str:
    if not SHA256_PATTERN.fullmatch(value):
        raise ValueError(f"expected lowercase SHA-256, got {value!r}")
    return value


def normalize_relative_path(value: str | Path) -> str:
    """Normalize a portable project-relative path and reject traversal/absolute paths."""

    raw = str(value).replace("\\", "/").strip()
    if not raw:
        raise ValueError("relative path cannot be empty")
    if raw.startswith("/") or re.match(r"^[A-Za-z]:/", raw):
        raise ValueError(f"absolute path is not portable: {value!r}")
    path = PurePosixPath(raw)
    if any(part in ("", ".", "..") for part in path.parts):
        raise ValueError(f"path traversal or ambiguous segment: {value!r}")
    return path.as_posix()

