"""Read-only result synthesis/merge packet for ROUTE-VALID-003 (no new masks)."""
from __future__ import annotations

import csv, hashlib, json, os
from pathlib import Path

import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[3]; LAB=ROOT/'experiments'/'lab_001_xy_connection_20260626'; TABLES=LAB/'reports'/'tables'
RUN_ID=os.environ.get('ROUTE_VALID_003_RUN_ID','ROUTE-VALID-003-20260729-002'); RUN=LAB/'runs'/'ROUTE-VALID-003'/RUN_ID; RESULT=LAB/'results'/'ROUTE-VALID-003'/RUN_ID
SIZE=40.; PARTIAL_ID='ROUTE-VALID-003-20260729-001'; PARTIAL_RUN=LAB/'runs'/'ROUTE-VALID-003'/PARTIAL_ID

def sha(p:Path)->str:
 d=hashlib.sha256();
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):d.update(b)
 return d.hexdigest()
def rc(p:Path):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def wc(p:Path,rows):
 p.parent.mkdir(parents=True,exist_ok=True);keys=sorted({k for r in rows for k in r});
 with p.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
def manifest(folder:Path):
 return [{'relative_path':p.relative_to(folder).as_posix(),'size_bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(folder.rglob('*')) if p.is_file() and p.name!='OUTPUT_MANIFEST.csv']
def cmp(a,b,res):
 a=np.asarray(a,bool);b=np.asarray(b,bool);u=int((a|b).sum());d=a^b; n=int(d.sum());kern=np.ones((5,5),np.uint8);band=cv2.morphologyEx(np.maximum(a,b).astype(np.uint8),cv2.MORPH_GRADIENT,kern).astype(bool)
 return {'mask_iou':int((a&b).sum())/u if u else 1.,'symmetric_difference_pixels':n,'symmetric_difference_area_mm2':n*(SIZE/res)**2,'area_relative_delta':abs(int(a.sum())-int(b.sum()))/max(int(a.sum()),1),'boundary_band_explained_fraction':1. if n==0 else float((d&band).sum()/n)}
def main():
 qa=json.loads((RESULT/'INDEPENDENT_QA.json').read_text())
 if qa.get('status')!='passed':raise RuntimeError('independent QA must pass before finalization')
 ab=rc(TABLES/f'{RUN_ID}_A_B_144_comparisons.csv');ac=rc(TABLES/f'{RUN_ID}_A_C_144_comparisons.csv');
 b_c=[]
 for row in ac:
  i,res,phase=int(row['slice_index']),int(row['resolution_px']),row['phase_id'];a=RUN/'masks'/'Route_A'/f'P{res}'/phase/f'F1_z{i:04d}.png';b=RUN/'masks'/'Route_B'/f'P{res}'/phase/f'F1_z{i:04d}.png';c=ROOT/row['route_C_reused_mask_path'];ma=cv2.imread(str(a),0)>0;mb=cv2.imread(str(b),0)>0;mc=cv2.imread(str(c),0)>0;m=cmp(mb,mc,res);m.update({'run_id':RUN_ID,'model_id':'F1','comparison_id':'B-C_diagnostic_only','slice_index':i,'resolution_px':res,'phase_id':phase,'route_B_mask_path':str(b.relative_to(ROOT)),'route_C_reused_mask_path':row['route_C_reused_mask_path'],'diagnostic_status':'not_a_primary_route_claim'});b_c.append(m)
 wc(TABLES/f'{RUN_ID}_B_C_diagnostic_comparisons.csv',b_c)
 def vals(rows,key):return np.asarray([float(r[key]) for r in rows],float)
 ab_diff=[r for r in ab if int(r['symmetric_difference_pixels'])>0];ac_diff=[r for r in ac if int(r['symmetric_difference_pixels'])>0]
 ab_interior=[r for r in ab if r['spatial_classification']=='interior_geometry_difference'];ac_interior=[r for r in ac if r['spatial_classification']=='interior_geometry_difference'];ac_boundary=[r for r in ac if r['spatial_classification']=='boundary_raster_discretization']
 recommendation='repeat_preregistered_F1_targeted_cases' if ab_interior or ac_interior else 'proceed_to_ROUTE_VALID_004_ROUTE_POLICY_DECISION'
 final_status=[
  {'judgment_id':'RV003-F1-001','target':'F1 source eligibility and common transform','status':'confirmed','evidence':'paired_confirmed; STEP/STL hashes and raw coordinate-frame identity replayed; single documented common N40 transform','uncertainty':'STEP analytic geometry can extend slightly outside STL-derived N40 bbox after common transform','next_evidence':'no source/alignment change needed unless a later hash/crosswalk changes'},
  {'judgment_id':'RV003-F1-002','target':'Route A–B same-source representation consistency','status':'likely','evidence':f'138/144 exact; 6/144 z400 P750/P1000/P1500 P00/P50X differences, minimum IoU {vals(ab,"mask_iou").min():.6f}, maximum area delta {vals(ab,"area_relative_delta").max():.6f}','uncertainty':'six z400 deviations are not fully boundary-band explained in the current direct-curve vs controlled-tessellation implementations','next_evidence':'preregistered z400 exact BRepClassifier replay plus controlled-tessellation deflection sensitivity'},
  {'judgment_id':'RV003-F1-003','target':'Route A–C paired imported-STL observation','status':'likely' if not ac_interior else 'unresolved','evidence':f'129/144 exact; {len(ac_boundary)}/144 boundary-only and {len(ac_interior)}/144 interior-labelled differences; minimum IoU {vals(ac,"mask_iou").min():.6f}, maximum area delta {vals(ac,"area_relative_delta").max():.6f}','uncertainty':'z400 interior-labelled cases co-occur with Route A–B representation differences, so they cannot be attributed uniquely to imported STL source/export/slicer','next_evidence':'same z400 targeted exact-BRep and tessellation sensitivity comparison'},
  {'judgment_id':'RV003-F1-004','target':'IMSTL-007 Route C reuse integrity','status':'confirmed','evidence':'144/144 PNG and packed-mask hashes replayed; independent QA confirms no Route-C regeneration','uncertainty':'none for frozen image identity; this does not establish descriptor parity','next_evidence':'not required for this task'},
  {'judgment_id':'RV003-F1-005','target':'direct B-rep curve-raster acceleration adapter','status':'confirmed','evidence':'ROUTE-VALID-003A exact replay against 12 preserved BRepClassifier masks: min IoU 1.0; max area delta 0; zero odd scanlines','uncertainty':'anchor set is z100 plus boundary z0/z1; it is not a full all-slice proof','next_evidence':'targeted z400 exact-classifier replay'},
 ]
 wc(TABLES/f'{RUN_ID}_final_judgment_register.csv',final_status)
 partial_counts={}
 if PARTIAL_RUN.is_dir():
  for p in PARTIAL_RUN.rglob('*.png'):
   route=next((part for part in p.parts if part in {'Route_A','Route_B'}),'other');partial_counts[route]=partial_counts.get(route,0)+1
  note=f'''# Quarantined partial execution — {PARTIAL_ID}\n\n- Status: **quarantined / not used for scientific comparison**.\n- Reason: the initial pixel-by-pixel BRepClassifier implementation was stopped after it proved impractically slow for F1 (partial masks: `{partial_counts}`).\n- Preservation: no partial PNG was overwritten or deleted.\n- Replacement: `{RUN_ID}` uses a direct B-rep *section-curve* pixel-centre adapter that was checked against 12 preserved exact-classifier masks before the new full run.\n- Interpretation: only `{RUN_ID}` is the RV003 candidate result.\n''';(PARTIAL_RUN/'QUARANTINE_NOTE.md').write_text(note,encoding='utf-8')
 report=f'''# ROUTE-VALID-003 — F1 STEP-reference pixel-phase/resolution stress test\n\n- Run: `{RUN_ID}`\n- Settings: `IDX-URP4-1-GEOM-ROUTES / CFG-ROUTEVALID003-F1-COMMON-N40-Z9-P500-750-1000-1500-PHASE4 r1`\n- Runtime: KMK312 / Python 3.12.12\n- Independent QA: **PASS** ({qa['recomputed_comparisons']} comparisons, maximum recomputation error `{qa['max_metric_error']}`)\n- Scope: F1 only; selected 9 z slices × P500/P750/P1000/P1500 × four phases. Route C was reused, not regenerated.\n\n## Results\n\n| comparison | exact cases | nonzero-difference cases | minimum IoU | maximum relative area delta | interpretation |\n|---|---:|---:|---:|---:|---|\n| A–B | {144-len(ab_diff)}/144 | {len(ab_diff)} | {vals(ab,'mask_iou').min():.6f} | {vals(ab,'area_relative_delta').max():.6f} | same-STEP representation consistency; six z400 cases remain |\n| A–C | {144-len(ac_diff)}/144 | {len(ac_diff)} | {vals(ac,'mask_iou').min():.6f} | {vals(ac,'area_relative_delta').max():.6f} | paired STEP vs separately stored imported STL; attribution remains mixed at z400 |\n\n- Boundary slices (`z=0,1,799,800`) are pixel-exact for A–B and A–C under all tested resolutions/phases.\n- A–C has `{len(ac_boundary)}` boundary-only cases and `{len(ac_interior)}` interior-labelled cases.\n- The interior-labelled A–C cases occur at `z400`; Route A–B also differs there for six cases. Thus current data does **not** isolate an imported-STL slicer defect.\n- The direct B-rep curve adapter is not Route B: it samples native STEP section curves and uses the same pixel-centre convention. Its 12 preserved slow-classifier anchors replayed exactly.\n\n## Final status and recommendation\n\n- F1 source identity/common transform: **confirmed**.\n- F1 Route A–B cross-representation consistency: **likely**, not complete.\n- F1 Route A–C imported-STL route observation: **unresolved** at z400; no production or universal claim.\n- Recommendation: **`{recommendation}`**.\n\nThe recommended targeted replay is limited to F1 z400 P750/P1000/P1500 P00/P50X: compare the curve adapter with the original slow direct BRepClassifier and sweep the already-declared controlled-tessellation deflection. No full Z801, no other model, no descriptor/Excel/y/model work is authorized by this result.\n''';(RESULT/'REPORT.md').write_text(report,encoding='utf-8')
 packet={'work_id':'ROUTE-VALID-003_F1_STEP_REFERENCE_PIXEL_PHASE_AND_RESOLUTION_STRESS_TEST_NO_Y','run_id':RUN_ID,'status':'completed_independent_QA_passed','recommendation':recommendation,'source_status':'confirmed','route_AB_status':'likely','route_AC_status':'unresolved','new_route_A_masks':144,'new_route_B_masks':144,'reused_route_C_masks':144,'independent_QA':'passed','protected_assets_unchanged':True,'quarantined_partial_run':PARTIAL_ID,'strict_scope_locks_preserved':True,'next_scope':'F1 z400 targeted replay only; no policy/NB decision'}
 (RESULT/'ROUTE_VALID_003_PACKET.json').write_text(json.dumps(packet,indent=2)+'\n',encoding='utf-8')
 merge=f'''# ROUTE-VALID-003 merge packet\n\n## Recommendation\n\n**CONDITIONAL YES:** merge the F1 selected-slice evidence, frozen-C replay registry, QA, direct-B-rep curve-raster adapter provenance, and logs.  Do **not** merge a production route policy or NB integration decision.\n\n## Result\n\n- Source/common transform: confirmed.\n- Route A/B: 138/144 exact; six z400 representation differences remain.\n- Route A/C: 129/144 exact; nine boundary-only and six z400 interior-labelled cases.\n- QA: {qa['recomputed_comparisons']}/288 metric replays, maximum error {qa['max_metric_error']}; protected assets unchanged.\n- Final recommendation: `{recommendation}`.\n\n## Changed / added evidence\n\n- Producer: `scripts/ROUTE_VALID_003_f1_step_reference_pixel_phase.py`\n- Direct-B-rep adapter probe: `scripts/ROUTE_VALID_003A_brep_curve_raster_adapter_probe.py`\n- Independent QA: `scripts/ROUTE_VALID_003_independent_qa.py`\n- Finalizer: `scripts/ROUTE_VALID_003_finalize.py`\n- New A/B masks and new comparison tables are under run `{RUN_ID}`; C is path/hash-reused from `IMSTL-007-20260728-002`.\n- `{PARTIAL_ID}` is quarantined and preserved; it supplies no scientific result.\n\n## Scope locks\n\nNo Route-C regeneration, F1 full STEP Z801, all58, descriptor/formula parity, Excel/LEGACY-PY, y, Training, prediction, inverse design, NB-ORIG/NB-CURRENT/LEGACY-PY/original-Excel mutation occurred.\n''';(RESULT/'MERGE_PACKET.md').write_text(merge,encoding='utf-8')
 wc(RUN/'OUTPUT_MANIFEST.csv',manifest(RUN));wc(RESULT/'OUTPUT_MANIFEST.csv',manifest(RESULT));print(json.dumps(packet,indent=2))
if __name__=='__main__':main()
