"""Execute only STRICT-STEP-006's six PHASE-00 B3 overlay traces; no descriptor/y."""
from __future__ import annotations
import csv,hashlib,importlib.util,json,sys
from pathlib import Path
import cv2,numpy as np
ROOT=Path(__file__).resolve().parents[3];LAB=ROOT/'experiments/lab_001_xy_connection_20260626';OUT=LAB/'results/STRICT-STEP-007'/'STRICT-STEP-007-20260728-001';TAB=LAB/'reports/tables';SRC=LAB/'data/raw/notion_reference_models_20260701/stp/B3-Basic_Cubic-BCC_Lattice.stp';SHA='b17a3c9a4ee56cf55b87204e6f7021b39f18c87a2657d4480cfda5b29fe8e0fe';SG=LAB/'scripts/STRICT_GEOM_006_phase_a_face_rasterizer_fixtures.py';CON=LAB/'results/STRICT-STEP-006'/'STRICT-STEP-006-20260728-001'/'CONTRACT.json'
sys.path.insert(0,str(ROOT/'URP4-1_DELIVERABLE'))
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.gp import gp_Trsf,gp_Vec,gp_Pnt2d
from OCP.BRepClass import BRepClass_FaceClassifier
from OCP.TopAbs import TopAbs_IN
from urp4.contracts.v0_1.canonical import sha256_file
from urp4.geometry_io.v0_2.step_import import GeometryRouteConfig,_normalize_shape,_ocp_modules,_read_step_shape,_shape_bbox,_shape_to_arrays
from urp4.descriptor_service.v0_1.slicing import vectorized_segments,rasterize_segments_scanline
def wc(p,rs):
 fs=sorted({k for r in rs for k in r});
 with p.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fs);w.writeheader();w.writerows(rs)
def loadsg():
 s=importlib.util.spec_from_file_location('ss007sg',SG);m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m
def fmask(sg,faces,res=1000):
 d=40/res; o=np.zeros((res,res),bool)
 for r in faces:
  xmin,xmax,ymin,ymax=r['bounds'];c0=max(0,int(np.ceil(xmin/d-.5))-1);c1=min(res-1,int(np.floor(xmax/d-.5))+1);r0=max(0,int(np.ceil((40-ymax)/d-.5))-1);r1=min(res-1,int(np.floor((40-ymin)/d-.5))+1);u0,ux,uy,v0,vx,vy=sg.uv_affine(r['face'])
  for row in range(r0,r1+1):
   y=40-(row+.5)*d
   for col in range(c0,c1+1):
    x=(col+.5)*d
    if BRepClass_FaceClassifier(r['face'],gp_Pnt2d(u0+ux*x+uy*y,v0+vx*x+vy*y),1e-9).State()==TopAbs_IN:o[row,col]^=True
 return o
def overlay(a,b):
 out=np.zeros((*a.shape,3),np.uint8);out[a&~b]=(0,0,255);out[~a&b]=(255,0,0);out[a&b]=(255,0,255);return out
def iou(a,b):
 u=int((a|b).sum());return int((a&b).sum())/u if u else 1.
def main():
 if 'kmk312' not in str(Path(sys.executable).resolve()).lower() or sha256_file(SRC)!=SHA or json.loads(CON.read_text())['status']!='preregistered_ready_for_execution_review':raise RuntimeError('contract')
 OUT.mkdir(parents=True,exist_ok=True);sg=loadsg();ocp=_ocp_modules();s=_read_step_shape(SRC,ocp);n,_,_=_normalize_shape(s,GeometryRouteConfig.from_values(input_paths=[str(SRC)],normalize_to_size_mm=40,allow_stl_to_step_proxy=False),ocp);b=_shape_bbox(n,ocp);tr=gp_Trsf();tr.SetTranslation(gp_Vec(-b[0],-b[1],-b[2]));loc=BRepBuilderAPI_Transform(n,tr,True).Shape();V,F=_shape_to_arrays(loc,GeometryRouteConfig.from_values(input_paths=[str(SRC)],normalize_to_size_mm=None,tessellation_deflection_mm=.1,tessellation_angle_rad=.35,allow_stl_to_step_proxy=False),ocp);tri=V[F]
 masks={}; sl=[]; ov=[]
 for z in (9.95,10.,10.05,19.95,20.,20.05,29.95,30.,30.05):
  for route in ('BREP','TESS'):
   if route=='BREP':
    sg.Z_MM=z;ed=sg.section_edge_sequence([loc]);ws,_=sg.connect_wires(ed);rec=[sg.face_record(w,i) for i,w in enumerate(ws,1)];faces=[r for r in rec if r['eligible'] and r['face_build_done']];mask=fmask(sg,faces);diag={'native_edges':int(ed.Length()),'eligible_wires':len(faces),'quarantined_wires':len(rec)-len(faces)}
   else:
    seg=vectorized_segments(tri,z);mask,diag=rasterize_segments_scanline(seg,(0.,0.),(40.,40.),1000,1000);diag['segment_count']=len(seg)
   masks[(z,route)]=mask;p=OUT/f'B3_Z{z:05.2f}_{route}_MASK.png';cv2.imwrite(str(p),mask.astype('uint8')*255);sl.append({'z_mm':z,'route':route,'pixels':int(mask.sum()),'area_mm2':mask.sum()*.0016,'path':str(p),'sha256':sha256_file(p),**diag})
 for a,b,label in [(9.95,10.,'LOWER_TO_ANCHOR'),(10.,10.05,'ANCHOR_TO_UPPER'),(19.95,20.,'LOWER_TO_ANCHOR'),(20.,20.05,'ANCHOR_TO_UPPER'),(29.95,30.,'LOWER_TO_ANCHOR'),(30.,30.05,'ANCHOR_TO_UPPER')]:
  anchor=round((a+b)/2/.05)*.05
  for route in ('BREP','TESS'):
   x,y=masks[(a,route)],masks[(b,route)];im=overlay(x,y);p=OUT/f'B3_Z{anchor:05.2f}_{label}_{route}_OVERLAY.png';cv2.imwrite(str(p),im);ov.append({'anchor_z_mm':anchor,'pair':label,'route':route,'red_pixels':int((x&~y).sum()),'blue_pixels':int((~x&y).sum()),'purple_pixels':int((x&y).sum()),'path':str(p),'sha256':sha256_file(p)})
 delta=[]
 for a in (10.,20.,30.):
  for label in ('LOWER_TO_ANCHOR','ANCHOR_TO_UPPER'):
   x=next(v for v in ov if v['anchor_z_mm']==a and v['pair']==label and v['route']=='BREP');y=next(v for v in ov if v['anchor_z_mm']==a and v['pair']==label and v['route']=='TESS');delta.append({'anchor_z_mm':a,'pair':label,'red_delta':abs(x['red_pixels']-y['red_pixels']),'blue_delta':abs(x['blue_pixels']-y['blue_pixels']),'purple_delta':abs(x['purple_pixels']-y['purple_pixels'])})
 wc(TAB/'STRICT-STEP-007-20260728-001_slice_trace.csv',sl);wc(TAB/'STRICT-STEP-007-20260728-001_overlay_trace.csv',ov);wc(TAB/'STRICT-STEP-007-20260728-001_overlay_route_delta.csv',delta);q={'run_id':'STRICT-STEP-007-20260728-001','slice_mask_count':len(sl),'overlay_count':len(ov),'trace_count':6,'status':'passed_pending_independent_qa'};(OUT/'PRODUCER_SUMMARY.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))
if __name__=='__main__':main()
