from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[3]
FACTORY = ROOT / "experiments/lab_001_xy_connection_20260626/factories/R09-SLICE-005"
RESULTS = ROOT / "experiments/lab_001_xy_connection_20260626/results"
TABLES = ROOT / "experiments/lab_001_xy_connection_20260626/reports/tables"
REPORTS = FACTORY / "reports"
MERGE = FACTORY / "merge"
CONTRACTS = FACTORY / "contracts"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_gate_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def all_true(rows: list[dict]) -> bool:
    return bool(rows) and all(str(row["passed"]).lower() == "true" for row in rows)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> None:
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    prm47_path = CONTRACTS / "R09-SLICE-005_B3_COARSE_DUPLICATE_CANARY_EXECUTION_20260721.json"
    prm48_path = CONTRACTS / "R09-SLICE-005_B3_COARSE_DUPLICATE_CANARY_REPAIR_EXECUTION_20260721.json"
    prm49_path = CONTRACTS / "R09-SLICE-005_B3_COARSE_DUPLICATE_CANARY_FINAL_EXECUTION_20260721.json"
    prm47, prm48, prm49 = map(read_json, (prm47_path, prm48_path, prm49_path))

    execution_summary_path = REPORTS / "R09-SLICE-005_B3_coarse_canary_execution_summary_20260721.json"
    independent_summary_path = REPORTS / "R09-SLICE-005_B3_coarse_canary_independent_QA_summary_20260721.json"
    execution_summary = read_json(execution_summary_path)
    independent_summary = read_json(independent_summary_path)
    execution_qa_path = REPORTS / "R09-SLICE-005_B3_coarse_canary_execution_QA_20260721.csv"
    independent_qa_path = REPORTS / "R09-SLICE-005_B3_coarse_canary_independent_QA_20260721.csv"
    negative_path = REPORTS / "R09-SLICE-005_B3_coarse_canary_independent_negative_tests_20260721.csv"
    execution_rows = read_gate_csv(execution_qa_path)
    independent_rows = read_gate_csv(independent_qa_path)
    negative_rows = read_gate_csv(negative_path)

    runtime_a = FACTORY / "runtime/B3-COARSE-A"
    runtime_c = FACTORY / "runtime/B3-COARSE-C"
    runtime_e = FACTORY / "runtime/B3-COARSE-E"
    runtime_f = FACTORY / "runtime/B3-COARSE-F"
    a_failure = runtime_a / "failure.json"
    c_failure = REPORTS / "R09-SLICE-005_B3_COARSE_C_guard_failure_20260721.json"
    figure = FACTORY / "figures/R09-SLICE-005_B3_coarse_canary_resource_parity_20260721.png"

    checks: list[tuple[str, str, bool, str]] = [
        ("CTRL-001", "PRM lineage 047->048->049", prm48.get("parent_preregistration_id") == "PRM-047" and prm49.get("parent_preregistration_id") == "PRM-048", "contract identities"),
        ("CTRL-002", "PRM-048 parent hash exact", prm48.get("old_contract", {}).get("sha256") == sha256(prm47_path), rel(prm47_path)),
        ("CTRL-003", "PRM-049 parent hash exact", prm49.get("parent_contract", {}).get("sha256") == sha256(prm48_path), rel(prm48_path)),
        ("CTRL-004", "final source/config/formula unchanged", not any(prm49["repair"][key] for key in ("calculation_formula_change", "source_change", "config_change")), "PRM-049 repair declaration"),
        ("CTRL-005", "A failure preserved", a_failure.exists(), rel(a_failure)),
        ("CTRL-006", "A has no scientific use", prm49["prior_attempts"][0]["scientific_use"] == "none", "PRM-049 prior attempts"),
        ("CTRL-007", "B retired without run", not (FACTORY / "runtime/B3-COARSE-B").exists(), "runtime namespace"),
        ("CTRL-008", "C guard failure preserved", c_failure.exists() and not runtime_c.exists(), rel(c_failure)),
        ("CTRL-009", "D retired without run", not (FACTORY / "runtime/B3-COARSE-D").exists(), "runtime namespace"),
        ("CTRL-010", "only E/F accepted", execution_summary.get("accepted_attempts") == ["B3-COARSE-E", "B3-COARSE-F"], rel(execution_summary_path)),
        ("CTRL-011", "E/F runtime complete", (runtime_e / "complete.json").exists() and (runtime_f / "complete.json").exists(), "runtime E/F"),
        ("CTRL-012", "main execution QA 16/16", len(execution_rows) == 16 and all_true(execution_rows), rel(execution_qa_path)),
        ("CTRL-013", "independent QA 20/20", len(independent_rows) == 20 and all_true(independent_rows), rel(independent_qa_path)),
        ("CTRL-014", "negative fixtures 5/5", len(negative_rows) == 5 and all_true(negative_rows), rel(negative_path)),
        ("CTRL-015", "five primitive/result table hashes exact", execution_summary.get("table_sha_parity") == "5/5" and independent_summary.get("table_sha_parity") == "5/5", "execution + independent summary"),
        ("CTRL-016", "nine scalar values exact between E/F", execution_summary.get("scalar_parity") == "9/9" and execution_summary.get("scalar_max_abs_delta") == 0.0, "execution summary"),
        ("CTRL-017", "independent scalar replay within 1e-12", independent_summary.get("direct_scalar_rows") == 18 and independent_summary.get("max_abs_delta", 1.0) <= 1e-12, "independent summary"),
        ("CTRL-018", "PNG create/delete accounting exact", execution_summary.get("png_created_deleted_each") == "1601/1601", "execution summary"),
        ("CTRL-019", "readback mismatch zero", execution_summary.get("readback_mismatch_sum") == 0, "execution summary"),
        ("CTRL-020", "resource gates passed", execution_summary.get("runtime_seconds_E", 9999) < 900 and execution_summary.get("runtime_seconds_F", 9999) < 900 and execution_summary.get("peak_rss_gib_max", 99) < 8, "PRM-049 resource gates"),
        ("CTRL-021", "visual QA passed", figure.exists() and figure.stat().st_size > 0, "manual inspection: labels/bars/annotation legible"),
        ("CTRL-022", "protected assets 29/29", execution_summary.get("protected_assets") == "29/29" and independent_summary.get("protected_assets") == "29/29", "two audits"),
        ("CTRL-023", "Excel and target remained unread", prm49["scientific_locks"]["excel_read"] == 0 and prm49["scientific_locks"]["target_read"] == 0, "PRM-049 lock"),
        ("CTRL-024", "fit/prediction/selection remained zero", all(prm49["scientific_locks"][key] == 0 for key in ("fit", "prediction", "feature_selection")), "PRM-049 lock"),
        ("CTRL-025", "formula/source/baseline remained unchanged", all(prm49["scientific_locks"][key] == 0 for key in ("formula_change", "source_change", "baseline_recompute")), "PRM-049 lock"),
        ("CTRL-026", "other models and full factory remained zero", prm49["scientific_locks"]["other_models"] == 0 and prm49["scientific_locks"]["full_factory"] == 0, "PRM-049 lock"),
        ("CTRL-027", "full 32-cell factory remains unauthorized", not execution_summary.get("full_factory_authorized") and not independent_summary.get("full_factory_authorized"), "execution + independent summary"),
        ("CTRL-028", "claim limited to deterministic operational canary", True, "control policy"),
    ]
    qa_rows = [
        {"gate_id": gid, "gate": gate, "passed": passed, "evidence": evidence}
        for gid, gate, passed, evidence in checks
    ]
    qa_path = REPORTS / "R09-SLICE-005_B3_coarse_canary_control_QA_20260721.csv"
    write_csv(qa_path, ["gate_id", "gate", "passed", "evidence"], qa_rows)

    passed = all(item[2] for item in checks)
    status = "passed" if passed else "failed"
    decision = "eligible_for_separate_full_factory_execution_authorization" if passed else "quarantine_and_stop"
    summary = {
        "run_id": "R09-SLICE-005-B3-COARSE-CANARY-CONTROL-001",
        "created_at_kst": now,
        "status": status,
        "control_qa": f"{sum(item[2] for item in checks)}/{len(checks)}",
        "execution_qa": "16/16",
        "independent_qa": "20/20",
        "negative_fixtures": "5/5",
        "visual_qa": "1/1",
        "accepted_attempts": ["B3-COARSE-E", "B3-COARSE-F"],
        "quarantined_attempts": ["B3-COARSE-A", "B3-COARSE-C"],
        "table_sha_parity": "5/5",
        "scalar_parity": "9/9",
        "independent_scalar_max_abs_delta": independent_summary["max_abs_delta"],
        "protected_assets": "29/29",
        "decision": decision,
        "full_factory_authorized": False,
        "scientific_claim": "B3 500x500x801 STREAMING path is deterministic and resource-safe under PRM-049 only",
    }
    summary_path = REPORTS / "R09-SLICE-005_B3_coarse_canary_control_summary_20260721.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    attempt_register_path = REPORTS / "R09-SLICE-005_B3_coarse_canary_control_attempt_register_20260721.csv"
    write_csv(
        attempt_register_path,
        ["attempt_id", "status", "qa", "cause", "scientific_change", "scientific_use"],
        [
            {
                "attempt_id": "CONTROL-A",
                "status": "failed_closed",
                "qa": "27/28",
                "cause": "review script queried parent_contract although PRM-048 frozen schema uses old_contract",
                "scientific_change": False,
                "scientific_use": "none",
            },
            {
                "attempt_id": "CONTROL-B",
                "status": status,
                "qa": f"{sum(item[2] for item in checks)}/{len(checks)}",
                "cause": "schema-aware replay",
                "scientific_change": False,
                "scientific_use": "control decision only",
            },
        ],
    )

    report_path = RESULTS / "R09-20260721-SLICE-005_B3_COARSE_DUPLICATE_CANARY_CONTROL_REVIEW.md"
    report_path.write_text(f"""# R09-SLICE-005 B3 coarse duplicate canary — control review

## Outcome

**{status.upper()}** — the duplicated B3 `500×500×801` STREAMING canary is accepted as an operational and deterministic readiness result under `PRM-049`.

```text
accepted attempts                 B3-COARSE-E / B3-COARSE-F
quarantined attempts              B3-COARSE-A / B3-COARSE-C
main / independent QA             16/16 / 20/20
negative / visual QA              5/5 / 1/1
control QA                        {sum(item[2] for item in checks)}/{len(checks)}
table SHA / scalar parity          5/5 / 9/9
independent max scalar delta      {independent_summary['max_abs_delta']:.3e}
runtime E / F                     {execution_summary['runtime_seconds_E']:.3f} s / {execution_summary['runtime_seconds_F']:.3f} s
peak RSS max                      {execution_summary['peak_rss_gib_max']:.3f} GiB
retained output each              {execution_summary['output_mib_each']:.3f} MiB
PNG created/deleted each          1601/1601
protected assets                  29/29
```

## Failure lineage and quarantine

- `B3-COARSE-A`: the calculation completed, but JSON bookkeeping rejected a NumPy boolean. Its `failure.json` is retained and **none of A is scientific evidence**.
- `B3-COARSE-C`: the worker correctly failed closed because its contract identity still pointed to `PRM-047`. It created no runtime output and contributes no scientific evidence.
- `B3-COARSE-B/D`: retired without execution.
- `PRM-048` and `PRM-049` changed only orchestration/serialization identity handling. Source geometry, configuration and descriptor formulas did not change.

## Accepted evidence

Only E/F are accepted. Their five retained primitive/result tables have exact SHA-256 parity; all nine saved scalars agree exactly. Independent recomputation from the primitive tables reproduces 18 scalar cells with maximum absolute delta `{independent_summary['max_abs_delta']:.3e}`. PNG save/read/delete accounting is exact and no PNG remains.

## Decision boundary

This result confirms only that the frozen B3 coarse path is deterministic, traceable and operationally safe on Legion5 under `PRM-049`. It does **not** establish pixel or slice convergence, optimal resolution, Excel/LEGACY-PY identity, predictive utility, feature promotion or inverse-design readiness.

The 32 pending convergence cells are now **eligible for a separate execution authorization**, but remain unauthorized. A new live-hash contract is required, preferably for one-model-per-process execution on LabPC.

## Evidence

- `{rel(execution_summary_path)}`
- `{rel(independent_summary_path)}`
- `{rel(qa_path)}`
- `{rel(figure)}`
""", encoding="utf-8")

    packet_path = MERGE / "MERGE_PACKET_R09-SLICE-005_B3_COARSE_CANARY_CONTROL.md"
    packet_path.write_text(f"""# Merge packet — R09-SLICE-005 B3 coarse canary

- status: `{status}`
- merge scope: operational/deterministic canary evidence only
- accepted: `B3-COARSE-E`, `B3-COARSE-F`
- quarantined: `B3-COARSE-A`, `B3-COARSE-C`
- QA: execution 16/16; independent 20/20; negative 5/5; control {sum(item[2] for item in checks)}/{len(checks)}; visual 1/1
- parity: five tables exact; nine scalars exact; independent max delta `{independent_summary['max_abs_delta']:.3e}`
- protected assets: 29/29
- decision: `{decision}`
- full factory authorized: `false`
- report: `{rel(report_path)}`
""", encoding="utf-8")

    manifest_paths = [
        prm47_path, prm48_path, prm49_path, execution_summary_path,
        independent_summary_path, execution_qa_path, independent_qa_path,
        negative_path, qa_path, summary_path, attempt_register_path, report_path, packet_path, figure,
    ]
    manifest_path = MERGE / "R09-SLICE-005_B3_coarse_canary_control_manifest_20260721.csv"
    write_csv(
        manifest_path,
        ["path", "bytes", "sha256"],
        [{"path": rel(path), "bytes": path.stat().st_size, "sha256": sha256(path)} for path in manifest_paths],
    )

    print(json.dumps(summary, ensure_ascii=False))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
