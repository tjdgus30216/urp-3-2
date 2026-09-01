from __future__ import annotations

"""Independent, y-blind QA for PRM-124 overlay phase-balance candidates."""

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "experiments/lab_001_xy_connection_20260626/reports/tables"
OUT = ROOT / "experiments/lab_001_xy_connection_20260626/factories/PRM-124/reports"
OUT.mkdir(parents=True, exist_ok=True)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_profile(model_id: str) -> dict[str, float]:
    path = ROOT / f".tmp/t4rs4/P1000_S801/{model_id}/tables/overlay_pixel_readback.csv"
    d = pd.read_csv(path).sort_values("pair_index")
    red = d.red_pixel_count.to_numpy(float)
    blue = d.blue_pixel_count.to_numpy(float)
    purple = d.purple_pixel_count.to_numpy(float)
    rb = np.maximum(red + blue, 1e-30)
    total = np.maximum(red + blue + purple, 1e-30)
    rr, bb, pp = red / total, blue / total, purple / total
    profiles = {
        "red_blue_absolute_balance": np.abs(red - blue) / rb,
        "red_blue_signed_balance": (red - blue) / rb,
        "phase_composition_entropy": -(
            rr * np.log(np.maximum(rr, 1e-30))
            + bb * np.log(np.maximum(bb, 1e-30))
            + pp * np.log(np.maximum(pp, 1e-30))
        ),
    }
    stats: dict[str, float] = {}
    for prefix, values in profiles.items():
        for suffix, value in {
            "mean": values.mean(),
            "population_std": values.std(ddof=0),
            "q10": np.quantile(values, 0.10),
            "q50": np.quantile(values, 0.50),
            "q90": np.quantile(values, 0.90),
            "iqr": np.quantile(values, 0.75) - np.quantile(values, 0.25),
        }.items():
            stats[f"RAW-X053::{prefix}_{suffix}"] = float(value)
    return stats


def result(check_id: str, ok: bool, detail: str) -> dict[str, object]:
    return {"check_id": check_id, "status": "PASS" if ok else "FAIL", "detail": detail}


def main() -> None:
    registry_path = TABLES / "PRM124_overlay_phase_balance_candidate_registry.csv"
    values_path = TABLES / "PRM124_overlay_phase_balance_values_long.csv"
    cross_path = TABLES / "PRM124_overlay_phase_balance_vs_XREG_v1_4_redundancy.csv"
    internal_path = TABLES / "PRM124_overlay_phase_balance_internal_redundancy.csv"
    collision_path = TABLES / "PRM124_overlay_phase_balance_collision_diagnostic.csv"
    registry = pd.read_csv(registry_path)
    values = pd.read_csv(values_path)
    cross = pd.read_csv(cross_path)
    internal = pd.read_csv(internal_path)
    collision = pd.read_csv(collision_path)
    models = sorted(values.model_id.unique())
    expected_ids = sorted(
        f"RAW-X053::{profile}_{stat}"
        for profile in ["red_blue_absolute_balance", "red_blue_signed_balance", "phase_composition_entropy"]
        for stat in ["mean", "population_std", "q10", "q50", "q90", "iqr"]
    )
    checks: list[dict[str, object]] = []
    checks.append(result("I124-01", len(models) == 58 and len(registry) == 18 and len(values) == 1044,
                         f"models={len(models)}, registry={len(registry)}, values={len(values)}"))
    checks.append(result("I124-02", sorted(registry.candidate_id.tolist()) == expected_ids,
                         "candidate IDs are the preregistered 3 profiles × 6 statistics"))
    checks.append(result("I124-03", registry.operational_grade.value_counts().to_dict() == {"B": 12, "C": 6},
                         f"grade counts={registry.operational_grade.value_counts().to_dict()}"))
    checks.append(result("I124-04", values.value.notna().all() and np.isfinite(values.value).all(),
                         "all 1,044 values finite"))
    source_paths = [ROOT / f".tmp/t4rs4/P1000_S801/{model}/tables/overlay_pixel_readback.csv" for model in models]
    checks.append(result("I124-05", len(source_paths) == 58 and all(path.is_file() for path in source_paths),
                         f"overlay source paths={len(source_paths)}, missing={sum(not path.is_file() for path in source_paths)}"))
    replay_rows = []
    for model in models:
        recalculated = source_profile(model)
        observed = values.loc[values.model_id.eq(model), ["candidate_id", "value"]].set_index("candidate_id").value.to_dict()
        replay_rows.append(max(abs(recalculated[candidate] - observed[candidate]) for candidate in expected_ids))
    checks.append(result("I124-06", max(replay_rows) <= 1e-12,
                         f"independent direct-table replay max_abs_error={max(replay_rows):.3e}"))
    checks.append(result("I124-07", len(cross) == 18 * 347 and len(internal) == 153 and len(collision) == 36,
                         f"cross={len(cross)}, internal={len(internal)}, collision={len(collision)}"))
    protected_terms = {"performance", "target", "response", "sea", "stress", "frf", "energy_absorption"}
    lineage_columns = [column for column in registry.columns if column not in {"y_evidence", "notes"}]
    inspected = " ".join(registry[lineage_columns].fillna("").astype(str).to_numpy().ravel().tolist()).lower()
    checks.append(result("I124-08", not any(term in inspected for term in protected_terms) and registry.y_evidence.eq(False).all(),
                         "candidate lineage contains no protected performance field and y_evidence is false"))
    qa = pd.DataFrame(checks)
    qa.to_csv(OUT / "PRM124_independent_QA.csv", index=False, encoding="utf-8-sig")
    summary = {
        "status": "PASS" if qa.status.eq("PASS").all() else "FAIL",
        "checks_passed": int(qa.status.eq("PASS").sum()),
        "checks_total": len(qa),
        "input_hashes": {path.name: sha256(path) for path in [registry_path, values_path, cross_path, internal_path, collision_path]},
        "max_replay_error": max(replay_rows),
        "y_access": False,
    }
    (OUT / "PRM124_independent_QA_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary))
    if summary["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
