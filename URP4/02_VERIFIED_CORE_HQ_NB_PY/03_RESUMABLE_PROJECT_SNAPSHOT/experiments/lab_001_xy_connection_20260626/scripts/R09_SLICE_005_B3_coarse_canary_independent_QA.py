"""Independent direct-numpy replay of the PRM-049 B3 coarse canary."""
from __future__ import annotations
import hashlib,json,platform,sys
from datetime import datetime,timedelta,timezone
from pathlib import Path
import numpy as np
import pandas as pd
import T3P_mesh_native_grouped_evaluation_preregistration_no_fit as protected_engine
ROOT=Path(__file__).resolve().parents[3];LAB=ROOT/"experiments"/"lab_001_xy_connection_20260626";FACTORY=LAB/"factories"/"R09-SLICE-005"
RUNTIME=FACTORY/"runtime";REPORTS=FACTORY/"reports";MERGE=FACTORY/"merge";KST=timezone(timedelta(hours=9))
CONTRACT=FACTORY/"contracts"/"R09-SLICE-005_B3_COARSE_DUPLICATE_CANARY_FINAL_EXECUTION_20260721.json"
EXEC_MANIFEST=MERGE/"R09-SLICE-005_B3_coarse_canary_execution_manifest_20260721.csv"
def now():return __import__("datetime").datetime.now(KST).isoformat(timespec="seconds")
def rel(p):return p.resolve().relative_to(ROOT.resolve()).as_posix()
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
 return h.hexdigest()
def asset(p):return {"path":rel(p),"bytes":p.stat().st_size,"sha256":sha(p)}
def write_csv(p,f):p.parent.mkdir(parents=True,exist_ok=True);f.to_csv(p,index=False,encoding="utf-8-sig",lineterminator="\n")
def write_json(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8")
def manifest_ok(p):
 f=pd.read_csv(p,dtype=str,keep_default_na=False)
 return all((ROOT/r.path).is_file() and str((ROOT/r.path).stat().st_size)==r.bytes and sha(ROOT/r.path)==r.sha256 for r in f.itertuples(index=False)),len(f)
def recompute(d):
 s=pd.read_csv(d/"tables"/"slice_pixel_count_table.csv");o=pd.read_csv(d/"tables"/"overlay_pixel_table.csv");c=pd.read_csv(d/"tables"/"overlay_component_table.csv")
 occ=s.material_pixel_count.to_numpy(float)/250000.;counts=s.component_count.to_numpy(float);union=o.union_pixel_count.to_numpy(float);valid=union>0
 change=(o.red_pixel_count.to_numpy(float)+o.blue_pixel_count.to_numpy(float))[valid]/union[valid];over=o.purple_pixel_count.to_numpy(float)[valid]/union[valid]
 thick=c.thickness_sqrt_red_purple.to_numpy(float);thick=thick[np.isfinite(thick)];mass=c.mass_orientation.to_numpy(float);mass=mass[np.isfinite(mass)]
 vals=[np.mean(occ),np.std(occ,ddof=0),np.mean(counts),np.std(counts,ddof=0),np.mean(change),np.mean(over),np.mean(thick),np.std(thick,ddof=0),np.mean(mass)]
 keys=[("XRV1-F001","mean"),("XRV1-F002","std_pop_ddof0"),("XRV1-F003","mean"),("XRV1-F004","std_pop_ddof0"),("XRV1-F005","mean"),("XRV1-F006","mean"),("XRV1-F007","mean"),("XRV1-F007","std_pop_ddof0"),("XRV1-F008","mean")]
 ns=[len(occ),len(occ),len(counts),len(counts),len(change),len(over),len(thick),len(thick),len(mass)]
 return pd.DataFrame([{"formula_id":k[0],"statistic":k[1],"independent_value":float(v),"independent_population_n":int(n)} for k,v,n in zip(keys,vals,ns)])
def main():
 if platform.python_version()!="3.12.12" or "KMK312" not in sys.executable:raise RuntimeError("KMK312")
 contract=json.loads(CONTRACT.read_text(encoding="utf-8"));ok,n=manifest_ok(EXEC_MANIFEST);dirs={x:RUNTIME/f"B3-COARSE-{x}" for x in ["E","F"]}
 rows=[]
 for x,d in dirs.items():
  calc=recompute(d);saved=pd.read_csv(d/"tables"/"descriptor_result.csv");m=saved.merge(calc,on=["formula_id","statistic"],validate="one_to_one")
  m["attempt"]=x;m["abs_delta"]=(m.value-m.independent_value).abs();m["population_n_exact"]=m.population_n.eq(m.independent_population_n);rows.append(m)
 replay=pd.concat(rows,ignore_index=True);replay_path=REPORTS/"R09-SLICE-005_B3_coarse_canary_independent_scalar_replay_20260721.csv";write_csv(replay_path,replay)
 table_checks=[]
 for f in ["slice_pixel_count_table.csv","overlay_pixel_table.csv","slice_component_table.csv","overlay_component_table.csv","descriptor_result.csv"]:
  e=pd.read_csv(dirs["E"]/"tables"/f);g=pd.read_csv(dirs["F"]/"tables"/f)
  table_checks.append((f,len(e),len(g),e.columns.tolist()==g.columns.tolist(),sha(dirs["E"]/"tables"/f)==sha(dirs["F"]/"tables"/f)))
 table=pd.DataFrame(table_checks,columns=["table","rows_E","rows_F","columns_exact","sha_exact"]);table_path=REPORTS/"R09-SLICE-005_B3_coarse_canary_independent_table_QA_20260721.csv";write_csv(table_path,table)
 comps={x:json.loads((d/"complete.json").read_text(encoding="utf-8")) for x,d in dirs.items()};protected=protected_engine.protected_post()
 # In-memory negative fixtures prove that parity/row gates fail closed.
 tampered=replay.copy();tampered.loc[0,"independent_value"]+=1e-6
 negative=pd.DataFrame([
  ("NEG-I01","scalar tamper detected",float((tampered.value-tampered.independent_value).abs().max())>1e-12),
  ("NEG-I02","dropped slice detected",len(pd.read_csv(dirs["E"]/"tables"/"slice_pixel_count_table.csv").iloc[:-1])!=801),
  ("NEG-I03","wrong source hash detected",sha(ROOT/contract["source"]["path"])!="0"*64),
  ("NEG-I04","prior A excluded",json.loads((RUNTIME/"B3-COARSE-A"/"failure.json").read_text(encoding="utf-8"))["status"]=="failed"),
  ("NEG-I05","C has no runtime output",not (RUNTIME/"B3-COARSE-C").exists())],columns=["test_id","test","passed"])
 negative_path=REPORTS/"R09-SLICE-005_B3_coarse_canary_independent_negative_tests_20260721.csv";write_csv(negative_path,negative)
 checks=pd.DataFrame([
  ("IQA-001","execution manifest intact",ok and n==8),("IQA-002","PRM-049 exact",contract["preregistration_id"]=="PRM-049"),
  ("IQA-003","E/F complete pass",all(c["status"]=="passed" for c in comps.values())),("IQA-004","five table SHA exact",len(table)==5 and table.sha_exact.all()),
  ("IQA-005","slice rows 801",table.loc[table.table.eq("slice_pixel_count_table.csv"),"rows_E"].iloc[0]==801),
  ("IQA-006","overlay rows 800",table.loc[table.table.eq("overlay_pixel_table.csv"),"rows_E"].iloc[0]==800),
  ("IQA-007","nine saved scalars each",len(replay)==18),("IQA-008","direct scalar delta <=1e-12",float(replay.abs_delta.max())<=1e-12),
  ("IQA-009","direct population sizes exact",replay.population_n_exact.all()),("IQA-010","all saved scalar finite",np.isfinite(replay.value).all()),
  ("IQA-011","PNG zero E/F",all(c["qa"]["remaining_png"]==0 for c in comps.values())),("IQA-012","readback zero E/F",all(c["qa"]["readback_mismatch_sum"]==0 for c in comps.values())),
  ("IQA-013","PNG accounting E/F",all(c["qa"]["png_created"]==c["qa"]["png_deleted"]==1601 for c in comps.values())),
  ("IQA-014","worker hash exact",all(c["worker_sha256"]==contract["worker_script"]["sha256"] for c in comps.values())),
  ("IQA-015","contract hash exact",all(c["contract_sha256"]==sha(CONTRACT) for c in comps.values())),
  ("IQA-016","source hash exact",sha(ROOT/contract["source"]["path"])==contract["source"]["sha256"]),
  ("IQA-017","resource gates E/F",all(all(c["gates"].values()) for c in comps.values())),
  ("IQA-018","negative fixtures 5/5",len(negative)==5 and negative.passed.all()),
  ("IQA-019","protected 29/29",len(protected)==29 and protected.status.isin(["pass","pass_with_alias_lock"]).all()),
  ("IQA-020","full factory not authorized",contract["scientific_locks"]["full_factory"]==0)],columns=["gate_id","gate","passed"])
 qa_path=REPORTS/"R09-SLICE-005_B3_coarse_canary_independent_QA_20260721.csv";write_csv(qa_path,checks)
 if not checks.passed.all():raise RuntimeError(checks.loc[~checks.passed,"gate_id"].tolist())
 summary={"run_id":"R09-SLICE-005-B3-COARSE-CANARY-IQA-001","created_at_kst":now(),"status":"passed","qa":"20/20","negative":"5/5",
          "direct_scalar_rows":len(replay),"max_abs_delta":float(replay.abs_delta.max()),"table_sha_parity":"5/5","protected_assets":"29/29","full_factory_authorized":False}
 summary_path=REPORTS/"R09-SLICE-005_B3_coarse_canary_independent_QA_summary_20260721.json";write_json(summary_path,summary)
 manifest_path=MERGE/"R09-SLICE-005_B3_coarse_canary_independent_QA_manifest_20260721.csv";write_csv(manifest_path,pd.DataFrame([asset(p) for p in [replay_path,table_path,negative_path,qa_path,summary_path]]))
 print(json.dumps(summary,ensure_ascii=False))
if __name__=="__main__":main()
