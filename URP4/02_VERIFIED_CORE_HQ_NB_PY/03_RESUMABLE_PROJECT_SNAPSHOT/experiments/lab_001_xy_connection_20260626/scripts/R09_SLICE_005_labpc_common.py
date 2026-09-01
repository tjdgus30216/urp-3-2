from __future__ import annotations

import csv
import hashlib
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path


KST = timezone(timedelta(hours=9))


def now_kst() -> str:
    return datetime.now(KST).isoformat(timespec="milliseconds")


def package_root() -> Path:
    return Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def atomic_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def safe_job_name(job_id: str) -> str:
    return job_id.replace("::", "__").replace(":", "_")


def directory_bytes(path: Path) -> int:
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


def verify_manifest(root: Path, manifest_path: Path) -> tuple[list[dict], bool]:
    rows = read_csv(manifest_path)
    checked: list[dict] = []
    for row in rows:
        path = root / row["path"]
        exists = path.is_file()
        size_ok = exists and path.stat().st_size == int(row["bytes"])
        hash_ok = size_ok and sha256(path) == row["sha256"]
        checked.append(
            {
                "path": row["path"],
                "exists": exists,
                "size_ok": size_ok,
                "hash_ok": hash_ok,
            }
        )
    return checked, bool(checked) and all(row["hash_ok"] for row in checked)
