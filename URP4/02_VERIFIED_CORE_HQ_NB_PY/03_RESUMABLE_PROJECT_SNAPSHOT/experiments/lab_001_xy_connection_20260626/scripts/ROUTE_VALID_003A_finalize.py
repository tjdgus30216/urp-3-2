"""Finalize ROUTE-VALID-003A without upgrading partial evidence."""
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];LAB=ROOT/'experiments'/'lab_001_xy_connection_20260626';TABLES=LAB/'reports'/'tables';RID='ROUTE-VALID-003A-20260729-002';RUN=LAB/'runs'/'ROUTE-VALID-003A'/RID;RESULT=LAB/'results'/'ROUTE-VALID-003A'/RID
def rc(p):
 with p.open(encoding='utf-8-sig',newline='') as h:return list(csv.DictReader(h))
def sha(p):
 d=hashlib.sha256();
 with p.open('rb') as h:
  for b in iter(lambda:h.read(1048576),b''):d.update(b)
 return d.hexdigest()
def main():
 qa=json.loads((RESULT/'INDEPENDENT_QA.json').read_text(encoding='utf-8'))
 if qa['status']!='partial_passed_independent_QA':raise RuntimeError('QA is not a passed partial result')
 rows=rc(TABLES/f'{RID}_all_pair_comparison.csv');attrs=rc(TABLES/f'{RID}_case_attribution.csv')
 def s(name):
  x=[r for r in rows if r['comparison_id']==name];return f"{sum(r['exact']=='True' for r in x)}/{len(x)} exact; min IoU={min(float(r['mask_iou']) for r in x):.6f}"
 report=f'''# ROUTE-VALID-003A — F1 z400 targeted Exact-A attribution replay\n\n- Run: `{RID}`\n- Status: **partial, independent QA passed**\n- Stop reason: `missing_preregistered_deflection_values`\n- New data: six Exact A slow pixel-by-pixel `BRepClass3d_SolidClassifier` masks only.\n- Reused unchanged: six Fast A, six baseline Route B (`0.1 mm`), six frozen Route C masks.\n- Route C: never regenerated.\n\n## What this establishes\n\n- {s('ExactA-FastA')}\n- {s('ExactA-B')}\n- {s('ExactA-C')}\n- All 36 pair metrics were independently replayed with maximum error `{qa['max_metric_error']}`.\n\n## Interpretation boundary\n\nThe required deflection sweep values were not found in reproducible preregistration material. Per contract, no new deflection was invented. Exact-A anchor evidence is preserved, but it cannot by itself distinguish controlled-tessellation deflection from a z400 representation interaction. No imported-STL defect, production route, descriptor parity, Excel/LEGACY-PY parity, y, Training, full Z801, or NB conclusion is made.\n\n## Final decision\n\n**`partial_missing_preregistered_deflection_values`**\n'''
 (RESULT/'REPORT.md').write_text(report,encoding='utf-8')
 judgment=[{'judgment_id':'RV003A-F1-001','target':'F1 Exact A six-case execution','status':'confirmed','evidence':'six new exact pixel-centre solid-classifier masks and QA replay','uncertainty':'does not by itself test deflection convergence'}, {'judgment_id':'RV003A-F1-002','target':'controlled-tessellation deflection attribution','status':'unresolved','evidence':'baseline B=0.1 mm is available','uncertainty':'no reproducible preregistered sweep values found'}, {'judgment_id':'RV003A-F1-003','target':'imported STL defect claim','status':'rejected','evidence':'partial run cannot isolate Route C after missing sweep','uncertainty':'none claimed'}]
 keys=sorted({k for r in judgment for k in r});
 with (TABLES/f'{RID}_final_judgment_register.csv').open('w',encoding='utf-8-sig',newline='') as h:w=csv.DictWriter(h,fieldnames=keys);w.writeheader();w.writerows(judgment)
 packet=f'''# ROUTE-VALID-003A merge packet\n\n## Recommendation\n\n**CONDITIONAL YES — merge only the partial exact-anchor evidence, QA, missing-preregistration finding, and logs.** Do not merge a route-policy or imported-STL conclusion.\n\n- Decision: `partial_missing_preregistered_deflection_values`\n- Exact A masks: 6 new, retained.\n- Reused masks: Fast A/B/C = 18; Route C regeneration = false.\n- QA: {qa['status']}; {qa['recomputed_comparisons']} comparison replays; maximum error {qa['max_metric_error']}.\n- Next authority required: locate/approve a deflection sweep contract before another attribution run.\n'''
 (RESULT/'MERGE_PACKET.md').write_text(packet,encoding='utf-8')
 manifest=[]
 for p in sorted(RESULT.rglob('*')):
  if p.is_file() and p.name!='OUTPUT_MANIFEST.csv':manifest.append({'relative_path':p.relative_to(RESULT).as_posix(),'size_bytes':p.stat().st_size,'sha256':sha(p)})
 with (RESULT/'OUTPUT_MANIFEST.csv').open('w',encoding='utf-8-sig',newline='') as h:w=csv.DictWriter(h,fieldnames=['relative_path','size_bytes','sha256']);w.writeheader();w.writerows(manifest)
 print(json.dumps({'run_id':RID,'decision':'partial_missing_preregistered_deflection_values','qa':qa['status']},ensure_ascii=False))
if __name__=='__main__':main()
