"""Resume only the failed Voxel smoke case and consolidate prior evidence."""

from __future__ import annotations

import json
from dataclasses import replace

import pandas as pd

from smoke_hq import OUTPUT, ROOT, base
from urp4.hq.v0_1 import run_hq


def main() -> None:
    prior_path = OUTPUT / "smoke_results.csv"
    prior = pd.read_csv(prior_path)
    cfg = replace(
        base(),
        geometry=replace(base().geometry, model_id="SMOKE-VOXEL"),
        generator=replace(base().generator, family="voxel"),
    )
    try:
        status = run_hq(cfg, ROOT)
        replacement = {
            "case": "voxel",
            "expected": "passed",
            "observed": status["status"],
            "route": status["route_id"],
            "run_dir": status["run_dir"],
            "error": "",
        }
    except Exception as exc:
        replacement = {
            "case": "voxel",
            "expected": "passed",
            "observed": "failed",
            "route": "",
            "run_dir": "",
            "error": f"{type(exc).__name__}: {exc}",
        }
    frame = pd.concat([prior.loc[prior["case"] != "voxel"], pd.DataFrame([replacement])], ignore_index=True)
    frame.to_csv(prior_path, index=False, encoding="utf-8-sig")
    ok = (frame["expected"] == frame["observed"]).all()
    summary = {
        "status": "passed" if ok else "failed",
        "case_count": len(frame),
        "passed_case_count": int((frame["expected"] == frame["observed"]).sum()),
        "resume_scope": "voxel_only_after_missing_reference_source_copy",
        "results_csv": str(prior_path),
    }
    (OUTPUT / "smoke_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(frame.to_string(index=False))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
