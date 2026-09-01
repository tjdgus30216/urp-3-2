from __future__ import annotations
import importlib.util,json
from pathlib import Path
R=Path(__file__).resolve().parents[3];T=R/'experiments/lab_001_xy_connection_20260626/reports/tables';F=R/'experiments/lab_001_xy_connection_20260626/factories'
spec=importlib.util.spec_from_file_location('factory',R/'experiments/lab_001_xy_connection_20260626/scripts/PRM132_137_fast_batch_autopilot.py');factory=importlib.util.module_from_spec(spec);spec.loader.exec_module(factory)
def main():
 b=factory.pd.read_csv(T/'PRM137_xreg_v2_1_candidate_bank.csv');v=factory.pd.read_csv(T/'PRM137_xreg_v2_1_values_long.csv');e=factory.pd.read_csv(T/'PRM137_unified_redundancy_edge_registry.csv');out=[]
 for prm,grp,kind,ver in [(138,'RAW-X060','raw_component_area','XREG-v2.2-TECHNICAL'),(140,'RAW-X061','slice_density','XREG-v2.3-TECHNICAL'),(142,'RAW-X062','pair_area','XREG-v2.4-TECHNICAL')]:b,v,e,q=factory.wave(prm,grp,kind,b,v,e,ver);out.append(q)
 (F/'PRM-138').mkdir(parents=True,exist_ok=True);(F/'PRM-138'/'PRM138_143_AUTOPILOT_SUMMARY.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
