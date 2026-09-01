"""C1 Route-A direct STEP -> temporary PNG -> unmodified LEGACY-PY x-only run."""
from __future__ import annotations
import csv,hashlib,importlib.util,json,shutil,sys,time
from pathlib import Path
import cv2,numpy as np,pandas as pd
from openpyxl import load_workbook
ROOT=Path(__file__).resolve().parents[3];LAB=ROOT/'experiments'/'lab_001_xy_connection_20260626';OUT=LAB/'results'/'STRICT-STEP-026'/'STRICT-STEP-026-20260731-001';STEP=LAB/'data'/'raw'/'notion_reference_models_20260701'/'stp'/'C1-Cubic_truss_lattice-SC-FCC.stp';STEP_SHA='3c47641d340e85acd9d2464dc46d665676c90895141e0c3c7c04a3b23ffdc73c';S21=LAB/'scripts'/'STRICT_STEP_021_b3_route_a_z801_raw_primitives.py';L2=ROOT/'outputs'/'URP4-1'/'2._Parameter_result_0727.py';L3=ROOT/'outputs'/'URP4-1'/'3._parameter_angle_all_0727.py';XLSX=ROOT/'outputs'/'URP4-1'/'압축+열+진동+구조인자_260212.xlsx';ANCH={0,200,400,600,800};W=40;P=1000;H=.05
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def csvout(p,rows):
 with p.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def state(**k):(OUT/'RUN_STATE.json').write_text(json.dumps({'run_id':'STRICT-STEP-026-20260731-001',**k},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 rt=Path(sys.executable).resolve()
 if 'kmk312' not in str(rt).lower() or sys.version_info[:2]!=(3,12):raise RuntimeError('canonical KMK312 required')
 if OUT.exists():raise RuntimeError('immutable output exists')
 if sha(STEP)!=STEP_SHA:raise RuntimeError('C1 STEP SHA mismatch')
 OUT.mkdir(parents=True);temp=OUT/'temporary_pngs';sd=temp/'slices';cd=temp/'colorcombine';ad=OUT/'anchor_pngs';sd.mkdir(parents=True);cd.mkdir();ad.mkdir();state(status='running',completed_slices=0,completed_overlays=0)
 manifest={'run_id':'STRICT-STEP-026-20260731-001','runtime':str(rt),'source_step':str(STEP),'source_step_sha256':STEP_SHA,'config':'Route A original STEP direct B-rep / N40 / z / P1000 / PHASE-00 / Z801','scope':'x-only direct LEGACY-PY execution; no y/training/feature selection/NB or source mutation'};(OUT/'CONTRACT_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 s21=load('s26_s21',S21);helper=s21.load_helper();sg=helper.loadsg();ocp=helper._ocp_modules();shape=helper._read_step_shape(STEP,ocp);norm,_,_=helper._normalize_shape(shape,helper.GeometryRouteConfig.from_values(input_paths=[str(STEP)],normalize_to_size_mm=40.0,allow_stl_to_step_proxy=False),ocp);b=helper._shape_bbox(norm,ocp);t=helper.gp_Trsf();t.SetTranslation(helper.gp_Vec(-b[0],-b[1],-b[2]));local=helper.BRepBuilderAPI_Transform(norm,t,True).Shape();zs=np.linspace(np.nextafter(0.,40.),np.nextafter(40.,0.),801);prev=None;sr=[];orr=[];start=time.perf_counter()
 try:
  for i,z in enumerate(zs):
   mask,_=s21.direct_mask(helper,sg,local,float(z));fg=int(mask.sum());sp=sd/f'{i:04d}.png';cv2.imwrite(str(sp),mask.astype(np.uint8)*255)
   if i in ANCH:shutil.copy2(sp,ad/f'slice_{i:04d}.png')
   sr.append({'slice_index':i,'z_mm':float(z),'foreground_pixels':fg,'png_sha256':sha(sp)})
   if prev is not None:
    r=prev&~mask;bl=~prev&mask;pu=prev&mask;bgr=np.zeros((P,P,3),np.uint8);bgr[r]=(0,0,255);bgr[bl]=(255,0,0);bgr[pu]=(255,0,255);op=cd/f'{i-1:04d}.png';cv2.imwrite(str(op),bgr)
    if i in ANCH:shutil.copy2(op,ad/f'overlay_{i-1:04d}_{i:04d}.png')
    orr.append({'pair_index':i-1,'red_pixels':int(r.sum()),'blue_pixels':int(bl.sum()),'purple_pixels':int(pu.sum()),'png_sha256':sha(op)})
   prev=mask
   if i%25==0:state(status='running',completed_slices=i+1,completed_overlays=i,elapsed_seconds=round(time.perf_counter()-start,2))
  csvout(OUT/'slice_png_manifest.csv',sr);csvout(OUT/'overlay_png_manifest.csv',orr)
  l2=load('s26_l2',L2);th=l2.thickness(str(sd),.0016);mc=l2.massorientation_curvature(str(cd),.0016,H,.04);rows=[]
  for vals,ds in [(th,'Thickness')]:
   for v,(a,s) in zip(vals,[(a,s) for a in ['IP','LIP','LTP'] for s in ['avg','stdev_population_ddof0']],strict=True):rows.append({'lineage':'LEGACY2 direct PNG','descriptor':ds,'aggregation':a,'statistic':s,'value':float(v)})
  for off,ds in enumerate(['MassOri','Curvature','Angle','PerimeterArea']):
   for v,(a,s) in zip(mc[off*6:(off+1)*6],[(a,s) for a in ['IP','LIP','LTP'] for s in ['avg','stdev_population_ddof0']],strict=True):rows.append({'lineage':'LEGACY2 direct PNG','descriptor':ds,'aggregation':a,'statistic':s,'value':float(v)})
  l3=load('s26_l3',L3);rr=l3.process_all(str(cd),W,H,.30,P)
  for k,d in [('angle','Angle'),('thickness','Thickness'),('massori','MassOri'),('curvature','Curvature'),('pta','PerimeterArea')]:
   v=np.concatenate([q[k][0] for q in rr]);w=np.concatenate([q[k][1] for q in rr]);a,s=l3.weighted_avg_std(v,w);rows += [{'lineage':'LEGACY3 direct PNG','descriptor':d,'aggregation':'weighted_component','statistic':'avg','value':float(a)},{'lineage':'LEGACY3 direct PNG','descriptor':d,'aggregation':'weighted_component','statistic':'stdev_population_ddof0','value':float(s)}]
  csvout(OUT/'direct_legacy_scalar_table.csv',rows); bulk=sum(1 for _ in temp.rglob('*.png'));shutil.rmtree(temp);state(status='completed',completed_slices=801,completed_overlays=800,direct_scalar_rows=len(rows),bulk_pngs_evicted=bulk,anchor_pngs_retained=len(list(ad.glob('*.png')),),elapsed_seconds=round(time.perf_counter()-start,2))
 except Exception as e:state(status='failed',error=str(e),temporary_pngs_retained=True,elapsed_seconds=round(time.perf_counter()-start,2));raise
if __name__=='__main__':main()
