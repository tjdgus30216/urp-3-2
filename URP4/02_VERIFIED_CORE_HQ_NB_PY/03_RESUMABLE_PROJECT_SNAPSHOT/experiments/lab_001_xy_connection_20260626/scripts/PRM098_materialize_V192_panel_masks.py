from __future__ import annotations

import hashlib
import json
import os
import tempfile
import time
from pathlib import Path

import numpy as np
import pandas as pd
import psutil
import vtk
from vtk.util.numpy_support import vtk_to_numpy

ROOT=Path(__file__).resolve().parents[3]
LAB=ROOT/"experiments"/"lab_001_xy_connection_20260626"; TABLES=LAB/"reports"/"tables"; FACTORY=LAB/"factories"/"PRM-098"; REPORTS=FACTORY/"reports"
MODELS=["B3","C1","L1","F1","T8","T9"]


def sha256(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()


def rasterize(stl_path:Path,n:int=192):
    pitch=40.0/n; origin=(pitch/2,)*3
    reader=vtk.vtkSTLReader(); reader.SetFileName(str(stl_path)); reader.Update(); poly=reader.GetOutput()
    if poly.GetNumberOfPolys()==0: raise RuntimeError("VTK read produced no triangles")
    image=vtk.vtkImageData(); image.SetSpacing(pitch,pitch,pitch); image.SetOrigin(*origin); image.SetDimensions(n,n,n); image.AllocateScalars(vtk.VTK_UNSIGNED_CHAR,1); vtk_to_numpy(image.GetPointData().GetScalars())[:]=1
    source=vtk.vtkPolyDataToImageStencil(); source.SetInputData(poly); source.SetOutputOrigin(*origin); source.SetOutputSpacing(pitch,pitch,pitch); source.SetOutputWholeExtent(image.GetExtent()); source.Update()
    stencil=vtk.vtkImageStencil(); stencil.SetInputData(image); stencil.SetStencilConnection(source.GetOutputPort()); stencil.ReverseStencilOff(); stencil.SetBackgroundValue(0); stencil.Update()
    flat=vtk_to_numpy(stencil.GetOutput().GetPointData().GetScalars()); volume=flat.reshape((n,n,n)).transpose(2,1,0).astype(bool,copy=False)
    return volume,pitch,int(poly.GetNumberOfPolys())


def main():
    canary=json.loads((REPORTS/"PRM098_V064_cost_canary_summary.json").read_text(encoding="utf-8"))
    if canary["groups_passed"]!="6/6": raise SystemExit("V192 mask creation blocked by cost canary")
    registry=pd.read_csv(TABLES/"PRM098_input_mask_source_registry.csv",dtype=str,keep_default_na=False)
    rows=[]; outroot=FACTORY/"intermediate"/"masks"; outroot.mkdir(parents=True,exist_ok=True)
    for model in MODELS:
        idx=registry.index[(registry.model_id==model)&(registry.resolution_id=="V192")][0]
        source_path=ROOT/registry.loc[idx,"asset_path"]; source_hash=registry.loc[idx,"expected_sha256"]
        if sha256(source_path)!=source_hash: raise RuntimeError(f"source hash mismatch {model}")
        outdir=outroot/model; outdir.mkdir(parents=True,exist_ok=True); target=outdir/"V192_mask.npz"
        t=time.perf_counter(); rss0=psutil.Process().memory_info().rss
        volume,pitch,triangles=rasterize(source_path,192)
        fd,tmp=tempfile.mkstemp(suffix=".npz",dir=outdir); os.close(fd)
        try: np.savez_compressed(tmp,volume=volume,pitch_mm=pitch,domain_mm=40.0); os.replace(tmp,target)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)
        elapsed=time.perf_counter()-t; mask_hash=sha256(target)
        v128_path=ROOT/registry.loc[(registry.model_id==model)&(registry.resolution_id=="V128"),"asset_path"].iloc[0]
        with np.load(v128_path) as z: vf128=float(z["volume"].mean())
        vf192=float(volume.mean()); rel=abs(vf192-vf128)/max(abs(vf128),1e-12)
        rows.append({"model_id":model,"resolution_id":"V192","mask_path":str(target.relative_to(ROOT)),"mask_sha256":mask_hash,"source_geometry_path":str(source_path.relative_to(ROOT)),"source_geometry_sha256":source_hash,"triangles":triangles,"occupied_voxels":int(volume.sum()),"volume_fraction":vf192,"V128_volume_fraction":vf128,"VF_relative_difference":rel,"runtime_s":elapsed,"rss_delta_gib":(psutil.Process().memory_info().rss-rss0)/1024**3,"status":"PASS" if rel<=.05 else "REVIEW"})
        registry.loc[idx,"source_geometry_path"]=str(source_path.relative_to(ROOT)); registry.loc[idx,"source_geometry_sha256"]=source_hash; registry.loc[idx,"asset_role"]="reuse_existing_mask"; registry.loc[idx,"asset_path"]=str(target.relative_to(ROOT)); registry.loc[idx,"expected_sha256"]=mask_hash; registry.loc[idx,"actual_sha256"]=mask_hash; registry.loc[idx,"hash_pass"]="True"; registry.loc[idx,"creation_authorized"]="False"
    result=pd.DataFrame(rows); result.to_csv(REPORTS/"PRM098_V192_mask_materialization.csv",index=False,encoding="utf-8-sig",lineterminator="\n"); registry.to_csv(TABLES/"PRM098_input_mask_source_registry.csv",index=False,encoding="utf-8-sig",lineterminator="\n")
    summary={"status":"PASS" if result.status.eq("PASS").all() else "REVIEW","masks":f"{result.status.eq('PASS').sum()}/{len(result)}","max_VF_relative_difference":float(result.VF_relative_difference.max()),"total_runtime_s":float(result.runtime_s.sum())}
    (REPORTS/"PRM098_V192_mask_materialization_summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary)); print(result[["model_id","volume_fraction","V128_volume_fraction","VF_relative_difference","runtime_s","status"]].to_string(index=False))
    if summary["status"]!="PASS": raise SystemExit(2)


if __name__=="__main__":main()
