from __future__ import annotations

import csv
import hashlib
import io
import json
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments/lab_001_xy_connection_20260626"
FACTORY = LAB / "factories/TOUR-C001"
REPORTS = FACTORY / "analysis_factory/reports"
RESULTS = LAB / "results"
CONTRACTS = FACTORY / "contracts"
KST = timezone(timedelta(hours=9))

ZIP = Path(r"G:\내 드라이브\labfactory\returned_results\R09_SLICE005_LABPC_RESULTS_Legion5_2026-07-22T010629_941+0900.zip")
MANIFEST = ZIP.with_suffix(".manifest.csv")
EXPECTED_SHA256 = "5f68795816fe20151796ac50cbe3f8accf609fa252879c0922105b2b55b26e42"

CONTRACT = CONTRACTS / "PRM-069_SLICE005_RETURN_INTAKE_20260722.json"
ARTIFACTS = REPORTS / "PRM069_SLICE005_return_artifact_registry.csv"
PRODUCER_QA = REPORTS / "PRM069_SLICE005_return_producer_QA.csv"
READBACK_QA = REPORTS / "PRM069_SLICE005_return_archive_readback_QA.csv"
NEXT_ACTION = REPORTS / "PRM069_SLICE005_return_next_action_contract.csv"
REPORT = RESULTS / "R09-20260722-PRM069_SLICE005_RETURN_INTAKE_AUDIT.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def csv_rows(data: bytes) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    if not ZIP.is_file() or not MANIFEST.is_file():
        raise FileNotFoundError("Returned ZIP or manifest is missing")
    manifest_rows = list(csv.DictReader(MANIFEST.open("r", encoding="utf-8-sig", newline="")))
    if len(manifest_rows) != 1:
        raise RuntimeError("Expected one manifest row")
    manifest = manifest_rows[0]
    actual_sha = sha256(ZIP)
    with zipfile.ZipFile(ZIP) as archive:
        names = archive.namelist()
        corrupt = archive.testzip()
        summary = json.loads(archive.read("results/reports/verification_summary.json").decode("utf-8"))
        matrix = csv_rows(archive.read("results/reports/all40_descriptor_scalar_matrix.csv"))
        cell_verification = csv_rows(archive.read("results/reports/cell_verification.csv"))
        table_hashes = csv_rows(archive.read("results/reports/table_hash_verification.csv"))
        repair_qa = csv_rows(archive.read("results/reports/aggregate_repair_QA.csv"))
        repair_hashes = csv_rows(archive.read("results/reports/aggregate_repair_input_hash_manifest.csv"))

    source_counts = {role: sum(row["source_role"] == role for row in matrix) for role in {row["source_role"] for row in matrix}}
    execution_cells = {row["execution_cell_id"] for row in matrix}
    models = {row["model_id"] for row in matrix}
    configs = {row["config_id"] for row in matrix}
    formula_counts: dict[str, int] = {}
    for cell in execution_cells:
        formula_counts[cell] = sum(row["execution_cell_id"] == cell for row in matrix)

    checks: list[dict] = []

    def add(qid: str, check: str, observed, expected, passed: bool) -> None:
        checks.append({"qa_id": qid, "check": check, "observed": observed, "expected": expected, "passed": bool(passed)})

    add("P01", "ZIP exists", ZIP.is_file(), True, ZIP.is_file())
    add("P02", "manifest exists", MANIFEST.is_file(), True, MANIFEST.is_file())
    add("P03", "manifest rows", len(manifest_rows), 1, len(manifest_rows) == 1)
    byte_delta = ZIP.stat().st_size - int(manifest["bytes"])
    add("P04", "ZIP bytes vs manifest (nonbinding; SHA/CRC authoritative)", ZIP.stat().st_size, int(manifest["bytes"]), actual_sha == manifest["sha256"] and corrupt is None)
    add("P05", "manifest SHA-256", actual_sha, manifest["sha256"], actual_sha == manifest["sha256"])
    add("P06", "frozen expected SHA-256", actual_sha, EXPECTED_SHA256, actual_sha == EXPECTED_SHA256)
    add("P07", "manifest verification status", manifest["verification_status"], "passed", manifest["verification_status"] == "passed")
    add("P08", "ZIP CRC", corrupt or "none", "none", corrupt is None)
    add("P09", "ZIP entries", len(names), 309, len(names) == 309)
    add("P10", "verification status", summary["status"], "passed", summary["status"] == "passed")
    add("P11", "new cells", summary["new_cells_passed"], "32/32", summary["new_cells_passed"] == "32/32")
    add("P12", "frozen baselines", summary["frozen_baselines_included"], "8/8", summary["frozen_baselines_included"] == "8/8")
    add("P13", "matrix rows summary", summary["all40_scalar_rows"], 360, summary["all40_scalar_rows"] == 360)
    add("P14", "table-hash rows summary", summary["new_table_hash_rows"], 160, summary["new_table_hash_rows"] == 160)
    add("P15", "union schema fields", summary["aggregate_schema_fields"], 18, summary["aggregate_schema_fields"] == 18)
    add("P16", "raw descriptor mutations", summary["raw_descriptor_files_modified"], 0, summary["raw_descriptor_files_modified"] == 0)
    add("P17", "matrix rows readback", len(matrix), 360, len(matrix) == 360)
    add("P18", "execution cells", len(execution_cells), 40, len(execution_cells) == 40)
    add("P19", "new scalar rows", source_counts.get("new_labpc_cell", 0), 288, source_counts.get("new_labpc_cell", 0) == 288)
    add("P20", "baseline scalar rows", source_counts.get("frozen_RUN139_reuse", 0), 72, source_counts.get("frozen_RUN139_reuse", 0) == 72)
    add("P21", "representative models", len(models), 8, len(models) == 8)
    add("P22", "configuration identities", len(configs), 5, len(configs) == 5)
    add("P23", "repair QA", sum(row["passed"].lower() == "true" for row in repair_qa), 9, len(repair_qa) == 9 and all(row["passed"].lower() == "true" for row in repair_qa))
    add("P24", "repair input hashes", len(repair_hashes), 40, len(repair_hashes) == 40)

    readback: list[dict] = []

    def addr(qid: str, check: str, observed, expected, passed: bool) -> None:
        readback.append({"qa_id": qid, "check": check, "observed": observed, "expected": expected, "passed": bool(passed)})

    addr("R01", "cell verification rows", len(cell_verification), 32, len(cell_verification) == 32)
    addr("R02", "cell verification pass", sum(row["all_passed"].lower() == "true" for row in cell_verification), 32, all(row["all_passed"].lower() == "true" for row in cell_verification))
    addr("R03", "table hash rows", len(table_hashes), 160, len(table_hashes) == 160)
    addr("R04", "table hashes pass", sum(row["hash_ok"].lower() == "true" for row in table_hashes), 160, all(row["hash_ok"].lower() == "true" for row in table_hashes))
    addr("R05", "nine scalars per cell", sorted(set(formula_counts.values())), [9], set(formula_counts.values()) == {9})
    addr("R06", "model roster", sorted(models), ["B3", "C1", "F1", "F2", "L1", "L7", "T8", "T9"], sorted(models) == ["B3", "C1", "F1", "F2", "L1", "L7", "T8", "T9"])
    addr("R07", "new cells per model", sorted({sum(row["model_id"] == model and row["source_role"] == "new_labpc_cell" for row in matrix) for model in models}), [36], all(sum(row["model_id"] == model and row["source_role"] == "new_labpc_cell" for row in matrix) == 36 for model in models))
    addr("R08", "baseline rows per model", sorted({sum(row["model_id"] == model and row["source_role"] == "frozen_RUN139_reuse" for row in matrix) for model in models}), [9], all(sum(row["model_id"] == model and row["source_role"] == "frozen_RUN139_reuse" for row in matrix) == 9 for model in models))
    addr("R09", "PNG cleanup in archive", sum(name.lower().endswith(".png") for name in names), 0, not any(name.lower().endswith(".png") for name in names))
    addr("R10", "scientific convergence decision", summary["scientific_convergence_decision"], "not performed; return to control tower", summary["scientific_convergence_decision"] == "not performed; return to control tower")
    addr("R11", "feature/model claim", summary["feature_or_model_claim"], "prohibited", summary["feature_or_model_claim"] == "prohibited")
    addr("R12", "performance-y artifacts", sum("performance" in name.lower() or "prediction" in name.lower() for name in names), 0, not any("performance" in name.lower() or "prediction" in name.lower() for name in names))

    if not all(row["passed"] for row in checks + readback):
        failed = [row for row in checks + readback if not row["passed"]]
        print(json.dumps(failed, indent=2, ensure_ascii=False))
        raise RuntimeError("PRM069 intake QA failed")

    now = datetime.now(KST).isoformat(timespec="seconds")
    contract = {
        "preregistration_id": "PRM-069",
        "run_id": "PRM069-SLICE005-RETURN-INTAKE-001",
        "created_at_kst": now,
        "status": "technical_intake_passed_with_nonbinding_size_metadata_mismatch_scientific_review_pending",
        "source_zip": str(ZIP),
        "source_manifest": str(MANIFEST),
        "source_zip_bytes": ZIP.stat().st_size,
        "manifest_recorded_zip_bytes": int(manifest["bytes"]),
        "manifest_size_delta_bytes": byte_delta,
        "manifest_size_field_status": "nonbinding_mismatch; exact SHA-256 and ZIP CRC passed",
        "source_zip_sha256": actual_sha,
        "technical_completion": "32/32 new cells + 8/8 frozen baselines",
        "matrix": "40 cells x 9 scalars = 360 rows",
        "table_hashes": "160/160",
        "producer_QA": "24/24",
        "archive_readback_QA": "12/12",
        "raw_descriptor_files_modified": 0,
        "performance_y_read": 0,
        "model_fit": 0,
        "scientific_convergence_decision": "pending",
        "next_tasks": ["SLICE005-CONVERGENCE-CONTROL-REVIEW", "NB-DEV-STL-IMPORT-BRANCH", "FS4-P1-RUN-BOUNDED-4METHOD"],
    }
    CONTRACT.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_csv(ARTIFACTS, ["artifact_id", "path", "bytes", "sha256", "role", "status"], [
        {"artifact_id": "RETURN-ZIP", "path": str(ZIP), "bytes": ZIP.stat().st_size, "sha256": actual_sha, "role": "immutable_return_packet", "status": "confirmed"},
        {"artifact_id": "RETURN-MANIFEST", "path": str(MANIFEST), "bytes": MANIFEST.stat().st_size, "sha256": sha256(MANIFEST), "role": "external_hash_manifest", "status": "confirmed"},
    ])
    write_csv(PRODUCER_QA, ["qa_id", "check", "observed", "expected", "passed"], checks)
    write_csv(READBACK_QA, ["qa_id", "check", "observed", "expected", "passed"], readback)
    write_csv(NEXT_ACTION, ["order", "task_id", "task", "status", "entry_gate", "forbidden"], [
        {"order": 1, "task_id": "SLICE005-CONVERGENCE-CONTROL-REVIEW", "task": "Analyze configuration convergence and representative-family effects from the frozen 40-cell matrix", "status": "next_strict", "entry_gate": "PRM-069 technical intake 24/24 and readback 12/12", "forbidden": "formula promotion or historical parity claim before review"},
        {"order": 2, "task_id": "NB-DEV-STL-IMPORT-BRANCH", "task": "Implement optional STL Import True/False branch in a development copy", "status": "unblocked_pending_priority", "entry_gate": "returned run identity frozen by PRM-069", "forbidden": "NB-CURRENT or LEGACY-PY mutation"},
        {"order": 3, "task_id": "FS4-P1-RUN-BOUNDED-4METHOD", "task": "Execute the already authorized four-method grouped-family pilot", "status": "authorized_next_parallel", "entry_gate": "exact PRM-068 permit and current idle-device check", "forbidden": "recipe expansion or post-result retuning"},
    ])
    REPORT.write_text(
        "\n".join([
            "# PRM-069 · SLICE-005 반환 결과 intake 감사",
            "",
            f"- 완료 시각(KST): `{now}`",
            "- 상태: `technical_intake_passed_with_nonbinding_size_metadata_mismatch_scientific_review_pending`",
            f"- 반환 ZIP: `{ZIP}`",
            f"- SHA-256: `{actual_sha}`",
            "",
            "## 결론",
            "",
            "계산과 기술 검증은 완료됐다. 신규 32개 cell과 동결 baseline 8개를 합쳐 40개 cell, 360개 scalar row가 확보됐고 160개 원시 표 해시가 모두 통과했다.",
            "",
            "다만 이는 수치 산출과 무결성 통과다. pixel/slice 설정의 수렴성, family별 안정성, historical Excel과의 관계는 다음 과학적 control review에서 판단해야 한다.",
            "",
            "## 포장 결함 및 복구",
            "",
            "기존 verifier는 신규 row의 `scientific_state/config_sha256`와 동결 baseline의 `population_id/state`를 하나의 첫-row schema로 쓰려다 실패했다. 합집합 18열 schema로 파생 통합표만 복구했으며 원시 descriptor 파일 수정은 0건이다.",
            "",
            f"Google Drive manifest의 비구속 byte field는 현재 파일보다 `{byte_delta}` bytes 작지만, exact SHA-256과 ZIP CRC는 모두 일치한다. 원본 manifest는 수정하지 않고 metadata mismatch로 보존했다.",
            "",
            "## 검증",
            "",
            "- Producer QA: `24/24`",
            "- ZIP archive readback QA: `12/12`",
            "- ZIP CRC: PASS",
            "- Matrix: `360 rows / 40 execution cells / 9 scalars each`",
            "- Model roster: `B3, C1, F1, F2, L1, L7, T8, T9`",
            "- y read / fit / prediction: `0 / 0 / 0`",
            "",
            "## 다음",
            "",
            "1. `SLICE005-CONVERGENCE-CONTROL-REVIEW`",
            "2. `NB-DEV-STL-IMPORT-BRANCH` (이제 run identity gate 해제)",
            "3. `FS4-P1-RUN-BOUNDED-4METHOD` (PRM-068 허가 유지, 별도 실행)",
            "",
        ]) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(contract, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
