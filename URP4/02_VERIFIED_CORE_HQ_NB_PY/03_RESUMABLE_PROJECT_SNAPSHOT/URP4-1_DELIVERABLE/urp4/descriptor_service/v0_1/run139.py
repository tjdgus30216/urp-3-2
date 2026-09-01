"""Read-only adapter for frozen RUN-139 primitive tables and observations."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from urp4.contracts.v0_1.canonical import sha256_file

from .models import DescriptorServiceError, PrimitiveTables
from .service import Run139DescriptorService


FROZEN_ASSET_HASHES = {
    "experiments/lab_001_xy_connection_20260626/scripts/R09_RESLICE_003_all58_resumable_factory.py": "8d2a65d6f1f0622a5256593823af457de2414a6bd3bf3227015b4addb346dcf3",
    "experiments/lab_001_xy_connection_20260626/scripts/R09_RESLICE_002_r1v2_pathsafe_native_smoke.py": "deb3070607721cb3480f9e2162b52aeb2e4e2203ecbe7a26b9aa34172a7cfd2d",
    "experiments/lab_001_xy_connection_20260626/reports/tables/R09-RESLICE-003_descriptor_result_20260715.csv": "d0f6167f59d76ba62b0ae0a55536a7251a52290a099bf2bc7d016f1b6b1fbe1b",
    "experiments/lab_001_xy_connection_20260626/reports/tables/R09-RESLICE-003_formula_registry_20260715.csv": "e254e8d2ded9baf0786e015fafe47cf7cf01cd90892c547713f616d6afd4ee1b",
    "experiments/lab_001_xy_connection_20260626/reports/tables/R09-DESC-001_descriptor_schema_v0_1_20260715.csv": "a9759a563a830b07f3d89ef31ec9e1a7321bcc26df58f4f5f14a4e51c83aef8b",
    "experiments/lab_001_xy_connection_20260626/reports/tables/R09-RESLICE-003_factory_freeze_20260715.json": "3ce5580a27360e2a201ed146c502980bac0b80ab7c713a4353cbca77f248d36d",
    "experiments/lab_001_xy_connection_20260626/reports/tables/R09-20260715_final_canonical_geometry_registry.csv": "49eb903a5eb63a6f017aaf2cf8af891d77d227de375d890a9b4ba889562a3314",
}

KEY_COLUMNS = ["model_id", "formula_id", "statistic"]
METADATA_COLUMNS = ["descriptor", "population_id", "unit", "population_n", "state"]


@dataclass(frozen=True)
class AttemptEvidence:
    model_id: str
    attempt_dir: Path
    source_sha256: str


class FrozenRun139Adapter:
    """Verify, load and replay the immutable RUN-139 all-58 evidence."""

    def __init__(self, project_root: str | Path, service: Run139DescriptorService | None = None):
        self.root = Path(project_root).resolve()
        self.lab = self.root / "experiments" / "lab_001_xy_connection_20260626"
        self.table_dir = self.lab / "reports" / "tables"
        self.run_root = self.lab / "runs" / "xrv1_s2" / "all58_20260715"
        self.models_root = self.run_root / "models"
        self.frozen_result_path = self.table_dir / "R09-RESLICE-003_descriptor_result_20260715.csv"
        self.freeze_path = self.table_dir / "R09-RESLICE-003_factory_freeze_20260715.json"
        self.service = service or Run139DescriptorService()

    def verify_frozen_assets(self) -> list[dict[str, str]]:
        rows: list[dict[str, str]] = []
        for relative_path, expected in FROZEN_ASSET_HASHES.items():
            path = self.root / relative_path
            actual = sha256_file(path) if path.is_file() else "missing"
            status = "passed" if actual == expected else "failed"
            rows.append(
                {
                    "relative_path": relative_path,
                    "expected_sha256": expected,
                    "actual_sha256": actual,
                    "status": status,
                }
            )
        failed = [row for row in rows if row["status"] != "passed"]
        if failed:
            raise DescriptorServiceError(f"frozen RUN-139 asset verification failed: {failed}")
        return rows

    def frozen_result(self) -> pd.DataFrame:
        frame = pd.read_csv(self.frozen_result_path)
        if len(frame) != 522 or frame["model_id"].nunique() != 58 or frame["formula_id"].nunique() != 8:
            raise DescriptorServiceError(
                "frozen result census mismatch; expected 58 models / 522 rows / 8 formula IDs"
            )
        counts = frame.groupby("model_id").size()
        if not (counts == 9).all():
            raise DescriptorServiceError("frozen result must contain nine scalar rows per model")
        if frame.duplicated(KEY_COLUMNS).any():
            raise DescriptorServiceError("frozen result contains duplicate semantic row keys")
        return frame

    def model_ids(self) -> list[str]:
        ids = self.frozen_result()["model_id"].astype(str).unique().tolist()
        return sorted(ids, key=lambda value: (value[0], int(value[1:])))

    def freeze(self) -> dict:
        return json.loads(self.freeze_path.read_text(encoding="utf-8"))

    def attempt(self, model_id: str) -> AttemptEvidence:
        candidates: list[tuple[Path, dict]] = []
        for path in sorted((self.models_root / model_id).glob("a*/complete.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            if payload.get("status") == "pass" and payload.get("model_id") == model_id:
                candidates.append((path.parent, payload))
        if not candidates:
            raise DescriptorServiceError(f"{model_id}: no completed passing RUN-139 attempt")
        attempt_dir, complete = candidates[-1]
        source_sha256 = str(complete["source_sha256"])
        expected_source = str(self.freeze()["source_hashes"].get(model_id, ""))
        if source_sha256 != expected_source:
            raise DescriptorServiceError(f"{model_id}: source hash differs from factory freeze")
        if int(complete.get("slice_rows", -1)) != 801 or int(complete.get("overlay_rows", -1)) != 800:
            raise DescriptorServiceError(f"{model_id}: complete.json primitive row census mismatch")
        if int(complete.get("descriptor_rows", -1)) != 9:
            raise DescriptorServiceError(f"{model_id}: complete.json descriptor row census mismatch")
        return AttemptEvidence(model_id=model_id, attempt_dir=attempt_dir, source_sha256=source_sha256)

    @staticmethod
    def _manifest_map(attempt_dir: Path) -> dict[str, str]:
        manifest_path = attempt_dir / "artifact_hash_manifest.csv"
        manifest = pd.read_csv(manifest_path, dtype=str, keep_default_na=False)
        return dict(zip(manifest["relative_path"], manifest["sha256"], strict=True))

    def load_primitive_tables(self, model_id: str) -> tuple[PrimitiveTables, list[dict[str, str]]]:
        evidence = self.attempt(model_id)
        manifest = self._manifest_map(evidence.attempt_dir)
        required = {
            "slice_pixels": "tables/slice_pixel_count_table.csv",
            "overlay_pixels": "tables/overlay_pixel_table.csv",
            "overlay_components": "tables/overlay_component_table.csv",
        }
        frames: dict[str, pd.DataFrame] = {}
        audit: list[dict[str, str]] = []
        for label, relative_path in required.items():
            path = evidence.attempt_dir / relative_path
            expected = manifest.get(relative_path, "manifest_entry_missing")
            actual = sha256_file(path) if path.is_file() else "missing"
            status = "passed" if actual == expected else "failed"
            audit.append(
                {
                    "model_id": model_id,
                    "attempt": evidence.attempt_dir.relative_to(self.root).as_posix(),
                    "table_role": label,
                    "relative_path": relative_path,
                    "expected_sha256": expected,
                    "actual_sha256": actual,
                    "status": status,
                }
            )
            if status != "passed":
                raise DescriptorServiceError(f"{model_id}/{relative_path}: primitive hash mismatch")
            frames[label] = pd.read_csv(path)
        return (
            PrimitiveTables(
                model_id=model_id,
                slice_pixels=frames["slice_pixels"],
                overlay_pixels=frames["overlay_pixels"],
                overlay_components=frames["overlay_components"],
            ),
            audit,
        )

    def replay_all(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        result_rows: list[dict] = []
        audit_rows: list[dict[str, str]] = []
        for model_id in self.model_ids():
            tables, audit = self.load_primitive_tables(model_id)
            result_rows.extend(scalar.to_row() for scalar in self.service.compute(tables))
            audit_rows.extend(audit)
        return pd.DataFrame(result_rows), pd.DataFrame(audit_rows)

    def compare(self, actual: pd.DataFrame) -> pd.DataFrame:
        expected = self.frozen_result()
        if actual.duplicated(KEY_COLUMNS).any():
            raise DescriptorServiceError("replayed result contains duplicate semantic row keys")
        merged = expected.merge(
            actual,
            on=KEY_COLUMNS,
            how="outer",
            suffixes=("_expected", "_actual"),
            indicator=True,
        )
        rows: list[dict] = []
        for _, row in merged.iterrows():
            identity_match = row["_merge"] == "both"
            metadata_match = identity_match and all(
                str(row[f"{column}_expected"]) == str(row[f"{column}_actual"])
                for column in ("descriptor", "population_id", "unit", "state")
            )
            population_match = identity_match and int(row["population_n_expected"]) == int(row["population_n_actual"])
            if identity_match:
                expected_value = float(row["value_expected"])
                actual_value = float(row["value_actual"])
                abs_error = abs(expected_value - actual_value)
            else:
                expected_value = np.nan
                actual_value = np.nan
                abs_error = np.inf
            status = "passed" if identity_match and metadata_match and population_match and abs_error <= 1e-12 else "failed"
            rows.append(
                {
                    "model_id": row["model_id"],
                    "formula_id": row["formula_id"],
                    "statistic": row["statistic"],
                    "row_identity_match": bool(identity_match),
                    "metadata_match": bool(metadata_match),
                    "population_n_match": bool(population_match),
                    "expected_value": expected_value,
                    "actual_value": actual_value,
                    "abs_error": abs_error,
                    "tolerance": 1e-12,
                    "status": status,
                }
            )
        return pd.DataFrame(rows)
