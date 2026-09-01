"""Probe a faster direct-B-rep section-curve raster adapter against preserved exact B-rep masks.

The adapter samples exact 2-D curves from a B-rep plane section and performs
an even-odd raster at the same pixel centres.  It is not Route B: no 3-D
controlled tessellation is used.  The only benchmark masks are the preserved,
slow BRepClassifier outputs from the interrupted RV003-001 run; nothing is
overwritten and this probe cannot promote a production route.
"""
from __future__ import annotations

import csv, hashlib, importlib.util, json, sys, time
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.BRepBuilderAPI import BRepBuilderAPI_GTransform, BRepBuilderAPI_Transform
from OCP.GCPnts import GCPnts_QuasiUniformDeflection
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.gp import gp_GTrsf, gp_Mat, gp_Trsf, gp_Vec, gp_XYZ

ROOT=Path(__file__).resolve().parents[3]; LAB=ROOT/'experiments'/'lab_001_xy_connection_20260626'; SCRIPTS=LAB/'scripts'; TABLES=LAB/'reports'/'tables'
RUN_ID='ROUTE-VALID-003A-20260729-001'; RESULT=LAB/'results'/'ROUTE-VALID-003A'/RUN_ID; RUN=LAB/'runs'/'ROUTE-VALID-003A'/RUN_ID
PREV=LAB/'runs'/'ROUTE-VALID-003'/'ROUTE-VALID-003-20260729-001'; CONTRACT=PREV/'COMMON_RASTER_CONTRACT.json'
STEP=LAB/'data/raw/notion_reference_models_20260701/stp/F1-Foam-Kelvin_foam.stp'; SS7=SCRIPTS/'STRICT_STEP_007_overlay_trace_execution.py'
SELECTED_INDEX=100; RES=(500,750,1000); PHASES={'P00':(0.,0.),'P50X':(.5,0.),'P50Y':(0.,.5),'P50XY':(.5,.5)}; SIZE=40.; COUNT=801

def sha(p:Path)->str:
 d=hashlib.sha256();
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):d.update(b)
 return d.hexdigest()
def wc(p:Path,rows:list[dict[str,object]]):
 p.parent.mkdir(parents=True,exist_ok=True);k=sorted({x for r in rows for x in r});
 with p.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=k);w.writeheader();w.writerows(rows)
def load_tools():
 s=importlib.util.spec_from_file_location('rv003a_ss7',SS7);m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m
def sample_segments(wires:list[Any],deflection:float)->tuple[np.ndarray,dict[str,int]]:
 pieces=[];fallback=0;point_count=0
 for wire in wires:
  ex=TopExp_Explorer(wire,TopAbs_EDGE)
  while ex.More():
   curve=BRepAdaptor_Curve(TopoDS.Edge_s(ex.Current())); pts=[]
   sampler=GCPnts_QuasiUniformDeflection(curve,deflection,curve.FirstParameter(),curve.LastParameter())
   if sampler.IsDone() and sampler.NbPoints()>=2:
    pts=[(float(sampler.Value(i).X()),float(sampler.Value(i).Y())) for i in range(1,sampler.NbPoints()+1)]
   else:
    fallback+=1; a,b=curve.Value(curve.FirstParameter()),curve.Value(curve.LastParameter());pts=[(float(a.X()),float(a.Y())),(float(b.X()),float(b.Y()))]
   arr=np.asarray(pts,float);point_count+=len(arr)
   if len(arr)>=2: pieces.append(np.column_stack((arr[:-1],arr[1:])))
   ex.Next()
 seg=np.vstack(pieces) if pieces else np.empty((0,4),float)
 return seg,{'curve_sample_point_count':point_count,'curve_sample_segment_count':len(seg),'curve_sampling_fallback_edges':fallback}
def even_odd_raster(seg:np.ndarray,res:int)->tuple[np.ndarray,dict[str,int]]:
 mask=np.zeros((res,res),bool); d=SIZE/res
 if not len(seg):return mask,{'odd_intersection_rows':0,'filled_rows':0}
 x1,y1,x2,y2=seg.T; keep=np.abs(y2-y1)>1e-12;x1,y1,x2,y2=x1[keep],y1[keep],x2[keep],y2[keep]
 lo,hi=np.minimum(y1,y2),np.maximum(y1,y2)
 start=np.floor((SIZE-hi)/d-.5).astype(int)+1;end=np.floor((SIZE-lo)/d-.5).astype(int)
 start=np.clip(start,0,res-1);end=np.clip(end,-1,res-1);counts=np.maximum(0,end-start+1);valid=counts>0
 start,counts,x1,y1,x2,y2=start[valid],counts[valid],x1[valid],y1[valid],x2[valid],y2[valid]
 if not len(counts):return mask,{'odd_intersection_rows':0,'filled_rows':0}
 offsets=np.repeat(np.cumsum(counts)-counts,counts);rows=np.repeat(start,counts)+(np.arange(int(counts.sum()))-offsets);ix=np.repeat(np.arange(len(counts)),counts)
 yy=SIZE-(rows+.5)*d;xs=x1[ix]+(yy-y1[ix])*(x2[ix]-x1[ix])/(y2[ix]-y1[ix]);order=np.lexsort((xs,rows));rows,xs=rows[order],xs[order]
 starts=np.r_[0,np.flatnonzero(np.diff(rows))+1];stops=np.r_[starts[1:],len(rows)];odd=filled=0
 for a,b in zip(starts,stops,strict=True):
  r=int(rows[a]);v=np.sort(xs[a:b]);
  if len(v)%2:odd+=1;v=v[:-1]
  for left,right in zip(v[0::2],v[1::2],strict=True):
   c0=max(0,min(res-1,int(np.ceil(left/d-.5))));c1=max(0,min(res-1,int(np.floor(right/d-.5))))
   if c1>=c0:mask[r,c0:c1+1]^=True;filled+=1
 return mask,{'odd_intersection_rows':odd,'filled_rows':filled}
def iou(a,b):
 u=int((a|b).sum());return int((a&b).sum())/u if u else 1.
def main():
 if 'kmk312' not in str(Path(sys.executable).resolve()).lower() or RUN.exists() or RESULT.exists():raise RuntimeError('runtime or overwrite guard')
 c=json.loads(CONTRACT.read_text(encoding='utf-8'));t=c['common_transform'];scale=np.asarray(t['scale_xyz'],float);trans=np.asarray(t['translation_xyz_mm'],float)
 tools=load_tools();sg=tools.loadsg();ocp=tools._ocp_modules();raw=tools._read_step_shape(STEP,ocp);g=gp_GTrsf();g.SetVectorialPart(gp_Mat(float(scale[0]),0,0,0,float(scale[1]),0,0,0,float(scale[2])));g.SetTranslationPart(gp_XYZ(float(trans[0]),float(trans[1]),float(trans[2])));shape=BRepBuilderAPI_GTransform(raw,g,True).Shape();z=np.linspace(0.,40.,COUNT);z[0]=np.nextafter(0.,40.);z[-1]=np.nextafter(40.,0.);zmm=float(z[SELECTED_INDEX]);RUN.mkdir(parents=True);RESULT.mkdir(parents=True);rows=[]
 for res in RES:
  d=SIZE/res;deflection=d/2
  for pid,(px,py) in PHASES.items():
   tr=gp_Trsf();tr.SetTranslation(gp_Vec(px*d,py*d,0));local=shape if not(px or py) else tools.BRepBuilderAPI_Transform(shape,tr,True).Shape();sg.Z_MM=zmm;edges=sg.section_edge_sequence([local]);wires,_=sg.connect_wires(edges);rec=[sg.face_record(w,i) for i,w in enumerate(wires,1)];eligible=[r for r in rec if r['eligible'] and r['face_build_done']]
   started=time.perf_counter();seg,sd=sample_segments([wires[int(r['wire_index'])-1] for r in eligible],deflection);mask,rd=even_odd_raster(seg,res);elapsed=time.perf_counter()-started;old_path=PREV/'masks'/'Route_A'/f'P{res}'/pid/f'F1_z{SELECTED_INDEX:04d}.png';old=cv2.imread(str(old_path),cv2.IMREAD_GRAYSCALE)>0
   diff=int((old^mask).sum());out=RUN/'masks'/f'P{res}'/pid/f'F1_z{SELECTED_INDEX:04d}.png';out.parent.mkdir(parents=True,exist_ok=True);cv2.imwrite(str(out),mask.astype(np.uint8)*255)
   rows.append({'run_id':RUN_ID,'slice_index':SELECTED_INDEX,'z_mm':zmm,'resolution_px':res,'phase_id':pid,'pixel_size_mm':d,'curve_deflection_mm':deflection,'eligible_face_count':len(eligible),'exact_classifier_mask_path':str(old_path.relative_to(ROOT)),'curve_adapter_mask_path':str(out.relative_to(ROOT)),'exact_solid_pixels':int(old.sum()),'adapter_solid_pixels':int(mask.sum()),'iou_vs_exact_classifier':iou(old,mask),'symmetric_difference_pixels':diff,'area_relative_delta':abs(int(old.sum())-int(mask.sum()))/max(int(old.sum()),1),'adapter_runtime_s':elapsed,**sd,**rd})
 wc(TABLES/f'{RUN_ID}_exact_brep_vs_curve_adapter_probe.csv',rows);payload={'run_id':RUN_ID,'status':'completed','case_count':len(rows),'min_iou':min(r['iou_vs_exact_classifier'] for r in rows),'max_area_delta':max(r['area_relative_delta'] for r in rows),'max_odd_rows':max(r['odd_intersection_rows'] for r in rows),'total_runtime_s':sum(r['adapter_runtime_s'] for r in rows),'scope':'direct STEP B-rep section curves vs preserved exact BRepClassifier masks; no Route C/y/descriptor'};(RESULT/'PRODUCER_PACKET.json').write_text(json.dumps(payload,indent=2)+'\n');print(json.dumps(payload,indent=2))
if __name__=='__main__':main()
