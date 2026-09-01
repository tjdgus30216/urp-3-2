from __future__ import annotations

import argparse
import json
import socket
import zipfile
from pathlib import Path

from R09_SLICE_005_labpc_common import (
    now_kst,
    package_root,
    read_json,
    sha256,
    write_csv,
)


ROOT = package_root()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--destination", required=True)
    parser.add_argument("--allow-partial", action="store_true")
    args = parser.parse_args()
    summary_path = ROOT / "results/reports/verification_summary.json"
    if not summary_path.is_file():
        raise FileNotFoundError("run 03_VERIFY_RESULTS.cmd first")
    summary = read_json(summary_path)
    if summary.get("status") != "passed" and not args.allow_partial:
        raise RuntimeError("verification is not passed; use --allow-partial only for emergency recovery")
    destination = Path(args.destination).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    stamp = now_kst().replace(":", "").replace("+09:00", "KST").replace(".", "_")
    zip_path = destination / f"R09_SLICE005_LABPC_RESULTS_{socket.gethostname()}_{stamp}.zip"
    included: list[Path] = []
    for relative in ["results", "preflight", "contracts", "config", "PACKAGE_MANIFEST.csv", "README_FIRST.md"]:
        path = ROOT / relative
        if path.is_file():
            included.append(path)
        elif path.is_dir():
            included.extend(item for item in path.rglob("*") if item.is_file())
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as archive:
        for path in sorted(set(included)):
            archive.write(path, path.relative_to(ROOT).as_posix())
    manifest_path = zip_path.with_suffix(".manifest.csv")
    write_csv(
        manifest_path,
        ["zip_path", "bytes", "sha256", "verification_status", "created_at_kst"],
        [
            {
                "zip_path": zip_path.name,
                "bytes": zip_path.stat().st_size,
                "sha256": sha256(zip_path),
                "verification_status": summary.get("status"),
                "created_at_kst": now_kst(),
            }
        ],
    )
    print(
        json.dumps(
            {
                "status": "collected",
                "zip": str(zip_path),
                "bytes": zip_path.stat().st_size,
                "sha256": sha256(zip_path),
                "manifest": str(manifest_path),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
