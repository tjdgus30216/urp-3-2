from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[3]; LAB=ROOT/"experiments"/"lab_001_xy_connection_20260626"; TABLES=LAB/"reports"/"tables"; REPORTS=LAB/"factories"/"PRM-098"/"reports"
sys.path.insert(0,str(Path(__file__).resolve().parent))
from PRM098_materialize_V192_panel_masks import rasterize  # noqa:E402


def main():
    registry=pd.read_csv(TABLES/"PRM098_input_mask_source_registry.csv",dtype=str,keep_default_na=False); source=ROOT/registry.loc[(registry.model_id=="C1")&(registry.resolution_id=="V192"),"source_geometry_path"].iloc[0]
    rows=[]
    for n in [64,96,128,160,192,224,256]:
        t=time.perf_counter(); v,_,_=rasterize(source,n); vf=float(v.mean())
        existing=registry.loc[(registry.model_id=="C1")&(registry.resolution_id==f"V{n:03d}")]
        stored_vf=np.nan; exact_replay=True
        if len(existing) and existing.iloc[0].asset_role=="reuse_existing_mask":
            with np.load(ROOT/existing.iloc[0].asset_path) as z: stored_vf=float(z["volume"].mean())
            exact_replay=abs(stored_vf-vf)<1e-15
        rows.append({"model_id":"C1","voxels_per_axis":n,"pitch_mm":40/n,"rerasterized_volume_fraction":vf,"stored_volume_fraction":stored_vf,"exact_replay_if_stored":exact_replay,"runtime_s":time.perf_counter()-t})
    frame=pd.DataFrame(rows); frame.to_csv(REPORTS/"PRM098_C1_mask_alias_resolution_sweep.csv",index=False,encoding="utf-8-sig",lineterminator="\n")
    summary={"status":"PASS_WITH_RESOLUTION_WARNING" if frame.exact_replay_if_stored.all() else "FAIL","stored_resolutions_exactly_replayed":bool(frame.exact_replay_if_stored.all()),"interpretation":"same-source deterministic voxel-grid resonance/aliasing; V192 mask is valid input but C1 descriptor-resolution stability must be judged by unchanged EQG-11","threshold_changed":False,"panel_continuation_authorized":bool(frame.exact_replay_if_stored.all())}
    (REPORTS/"PRM098_C1_mask_alias_audit_summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary)); print(frame.to_string(index=False))
    if not summary["panel_continuation_authorized"]: raise SystemExit(1)


if __name__=="__main__":main()
