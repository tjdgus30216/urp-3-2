from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    run = Path(args.run_dir).resolve()
    manifest = json.loads((run / "MANIFEST.json").read_text(encoding="utf-8"))
    y_rows = read_csv(run / "performance_y_wide_all.csv")
    x_rows = read_csv(run / "structural_x_wide_relevant.csv")
    joined = read_csv(run / "xy_eligible_exact_join.csv")
    registry = read_csv(run / "row_registry.csv")
    targets = read_csv(run / "target_registry.csv")
    features = read_csv(run / "feature_registry.csv")
    sources = read_csv(run / "source_audit.csv")

    checks: list[dict] = []

    def add(check_id: str, check: str, passed: bool, observed: object) -> None:
        checks.append({"check_id": check_id, "check": check, "passed": passed, "observed": observed})

    add("IQA-01", "manifest status PASS", manifest["status"] == "PASS", manifest["status"])
    add("IQA-02", "all source hashes passed", all(row["status"] == "PASS" for row in sources), f"{sum(row['status'] == 'PASS' for row in sources)}/{len(sources)}")
    add("IQA-03", "performance rows 228", len(y_rows) == 228, len(y_rows))
    add("IQA-04", "structural rows 170", len(x_rows) == 170, len(x_rows))
    add("IQA-05", "eligible exact joins 167", len(joined) == 167, len(joined))
    add("IQA-06", "BCL joins 137", sum(row["source_group"] == "bcl" for row in joined) == 137, sum(row["source_group"] == "bcl" for row in joined))
    add("IQA-07", "Voronoi joins 30", sum(row["source_group"] == "voronoi" for row in joined) == 30, sum(row["source_group"] == "voronoi" for row in joined))
    status_counts = {status: sum(row["crosswalk_status"] == status for row in registry) for status in sorted({row["crosswalk_status"] for row in registry})}
    add("IQA-08", "row registry partition", status_counts == {"eligible_exact_model_label_join": 167, "x_only_missing_performance": 3, "y_only_missing_structural_factors": 61}, status_counts)
    add("IQA-09", "16 targets", len(targets) == 16, len(targets))
    y_columns = ["y__" + row["target_name_raw"] for row in targets]
    missing = sum(row[column] == "" for row in joined for column in y_columns)
    add("IQA-10", "joined y values complete", missing == 0, missing)
    add("IQA-11", "feature registry 45", len(features) == 45, len(features))
    add("IQA-12", "no feature promotion", all(row["status"] in {"available_unselected", "excluded"} for row in features), sorted({row["status"] for row in features}))
    add("IQA-13", "joined model keys unique", len({row["model_key"] for row in joined}) == len(joined), len({row["model_key"] for row in joined}))
    add("IQA-14", "Voronoi key format", all(row["model_key"].startswith(("VF30_VF30_", "VF45_VF45_", "VF60_VF60_")) for row in joined if row["source_group"] == "voronoi"), "normalized explicit IDs")

    manifest_mismatch = []
    for item in manifest["outputs"]:
        path = run / item["file"]
        if not path.exists() or path.stat().st_size != item["bytes"] or sha256(path) != item["sha256"]:
            manifest_mismatch.append(item["file"])
    add("IQA-15", "producer output manifest matches", not manifest_mismatch, "|".join(manifest_mismatch) if manifest_mismatch else "all")

    passed = all(bool(row["passed"]) for row in checks)
    write_csv(run / "independent_QA.csv", checks)
    result = {"status": "PASS" if passed else "FAIL", "checks_passed": sum(bool(row["passed"]) for row in checks), "checks_total": len(checks), "run_dir": str(run)}
    (run / "independent_QA.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not passed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
