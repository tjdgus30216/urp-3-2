"""Independent read-only QA for ROUTE-VALID-003A."""
from __future__ import annotations
import csv, hashlib, json, sys
from pathlib import Path
import cv2, numpy as np

ROOT=Path(__file__).resolve().parents[3]; LAB=ROOT/'experiments'/'lab_001_xy_connection_20260626'; TABLES=LAB/'reports'/'tables'; RUN_ID='ROUTE-VALID-003A-20260729-002'; RUN=LAB/'runs'/'ROUTE-VALID-003A'/RUN_ID; RESULT=LAB/'results'/'ROUTE-VALID-003A'/RUN_ID; PREV=LAB/'runs'/'ROUTE-VALID-003'/'ROUTE-VALID-003-20260729-002'; PROTECTED=LAB/'results'/'HQ-BLUEPRINT-001'/'PROTECTED_ASSET_BASELINE.json'
def sha(p):
 d=hashlib.sha256();
 with p.open('rb') as h:
  for b in iter(lambda:h.read(1048576),b''):d.update(b)
 return d.hexdigest()
def rc(p):
 with p.open(encoding='utf-8-sig',newline='') as h:return list(csv.DictReader(h))
def wm(p,x):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def mask(p):
 a=cv2.imread(str(p),cv2.IMREAD_GRAYSCALE)
 if a is None or not set(np.unique(a).tolist()).issubset({0,255}):raise RuntimeError(f'invalid mask {p}')
 return a>0
def packed(a):return hashlib.sha256(np.packbits(a.astype(np.uint8).reshape(-1),bitorder='big').tobytes()).hexdigest()
def metrics(a,b):
 inter=int(np.logical_and(a,b).sum());union=int(np.logical_or(a,b).sum());diff=np.logical_xor(a,b)
 return {'mask_iou':inter/union if union else 1.0,'symmetric_difference_pixels':int(diff.sum()),'relative_area_delta':abs(int(a.sum())-int(b.sum()))/max(int(a.sum()),1),'signed_solid_pixel_difference_candidate_minus_reference':int(b.sum())-int(a.sum())}
def main():
 if 'kmk312' not in str(Path(sys.executable).resolve()).lower() or sys.version_info[:2]!=(3,12):raise RuntimeError('KMK312 Python 3.12.12 required')
 audit=json.loads((RUN/'PREREGISTRATION_AUDIT.json').read_text(encoding='utf-8')); exact=rc(TABLES/f'{RUN_ID}_exact_A_mask_registry.csv'); reused=rc(TABLES/f'{RUN_ID}_reused_FastA_B_C_mask_registry.csv'); comps=rc(TABLES/f'{RUN_ID}_all_pair_comparison.csv'); defl=json.loads((RUN/'DEFLECTION_SWEEP_CONTRACT.json').read_text(encoding='utf-8'))
 checks={}; checks['run_id']=audit['run_id']==RUN_ID; checks['six_exact_masks']=len(exact)==6; checks['eighteen_reused_masks']=len(reused)==18; checks['thirtysix_comparisons']=len(comps)==36; checks['missing_deflection_status']=audit['stop_reason']=='missing_preregistered_deflection_values' and defl['sweep_values_mm']==[] and defl['new_tessellation_masks_created']==0
 exact_map={}; route_map={}
 for r in exact:
  p=ROOT/r['mask_path'];a=mask(p);exact_map[(int(r['resolution_px']),r['phase_id'])]=a;checks.setdefault('exact_mask_integrity',True);checks['exact_mask_integrity'] &= sha(p)==r['png_sha256'] and packed(a)==r['packed_mask_sha256'] and a.shape==(int(r['resolution_px']),int(r['resolution_px']))
 for r in reused:
  p=ROOT/r['mask_path'];a=mask(p);route_map[(int(r['resolution_px']),r['phase_id'],r['route'])]=a;checks.setdefault('reused_mask_integrity',True);checks['reused_mask_integrity'] &= sha(p)==r['png_sha256'] and packed(a)==r['packed_mask_sha256']
 maxerr=0.0
 for r in comps:
  key=(int(r['resolution_px']),r['phase_id']);a=exact_map[key] if r['reference_route']=='ExactA' else route_map[(key[0],key[1],r['reference_route'])];b=exact_map[key] if r['candidate_route']=='ExactA' else route_map[(key[0],key[1],r['candidate_route'])];m=metrics(a,b)
  for f,v in m.items():maxerr=max(maxerr,abs(float(r[f])-float(v)))
 checks['comparison_replay']=maxerr==0.0
 checks['predecessor_manifest_unchanged']=sha(PREV/'OUTPUT_MANIFEST.csv')==audit['predecessor']['run_output_manifest_sha256']
 baseline=json.loads(PROTECTED.read_text(encoding='utf-8')); checks['protected_assets_unchanged']=all((ROOT/a['path']).is_file() and sha(ROOT/a['path'])==a['before_sha256'] for a in baseline['assets'])
 checks['no_route_c_regeneration']=all(r['route']!='C' or 'IMSTL-007-20260728-002' in r['source_run_id'] for r in reused)
 payload={'work_id':'ROUTE-VALID-003A_F1_Z400_TARGETED_ATTRIBUTION_REPLAY_NO_Y','run_id':RUN_ID,'status':'partial_passed_independent_QA' if all(checks.values()) else 'failed','stop_reason':audit['stop_reason'],'checks':checks,'recomputed_comparisons':len(comps),'max_metric_error':maxerr,'scope':'read-only QA; no Route C regeneration, no sweep, no y/descriptor/NB mutation'};wm(RESULT/'INDEPENDENT_QA.json',payload);print(json.dumps(payload,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
