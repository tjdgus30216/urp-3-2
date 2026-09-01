from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import ndimage as ndi
from skimage.measure import euler_number

ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
FACTORY = LAB / "factories" / "PRM-098"
REPORTS = FACTORY / "reports"
TABLES = LAB / "reports" / "tables"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from PRM098_third_wave_formula_library import (  # noqa: E402
    binary_glcm_at_shift, ect_outputs, local_thickness_field,
    normal_harmonics_from_normals, phase_scale_outputs, skeleton_graph_outputs,
)


def metric(out, name):
    return float(out[next(k for k in out if k.endswith("::" + name))])


def brute_local_thickness(volume: np.ndarray, pitch: float) -> np.ndarray:
    padded = np.pad(volume, 1, constant_values=False)
    edt = ndi.distance_transform_edt(padded)
    centers = np.argwhere(padded); radii = edt[padded]
    result = np.zeros(padded.shape, dtype=float)
    for q in centers:
        d = np.linalg.norm(centers - q, axis=1)
        valid = radii + 1e-12 >= d
        result[tuple(q)] = 2 * radii[valid].max() * pitch
    return result[1:-1, 1:-1, 1:-1]


def graph_fixtures():
    out = []
    line = np.zeros((32, 32, 32), bool); line[5:20, 16, 16] = True
    out.append(("SYN-GRAPH-LINE", line, lambda r: metric(r, "node_count") == 2 and metric(r, "edge_count") == 1 and metric(r, "component_count") == 1 and metric(r, "cycle_rank") == 0 and metric(r, "endpoint_fraction") == 1, "V=2,E=1,C=1,cycle=0,endpoint_fraction=1"))
    y = np.zeros_like(line); c = np.array([16, 16, 16])
    for d in [(1, 0, 0), (-1, 1, 0), (-1, -1, 0)]:
        for t in range(8): y[tuple(c + t * np.asarray(d))] = True
    out.append(("SYN-GRAPH-Y", y, lambda r: metric(r, "node_count") == 4 and metric(r, "edge_count") == 3 and metric(r, "cycle_rank") == 0 and abs(metric(r, "endpoint_fraction") - 0.75) < 1e-12, "one degree-3 node, three endpoints, cycle=0"))
    ring = np.zeros_like(line); p = np.array([12, 6, 16])
    for d in [(1,0,0),(1,1,0),(0,1,0),(-1,1,0),(-1,0,0),(-1,-1,0),(0,-1,0),(1,-1,0)]:
        for _ in range(4): ring[tuple(p)] = True; p += np.asarray(d)
    out.append(("SYN-GRAPH-RING", ring, lambda r: metric(r, "component_count") == 1 and metric(r, "node_count") == 1 and metric(r, "edge_count") == 1 and metric(r, "cycle_rank") == 1 and metric(r, "endpoint_fraction") == 0, "pure-loop anchor/self-loop, C=1,cycle=1,no endpoints"))
    return out


def lt_fixtures():
    n = 40; g = np.indices((n, n, n)); c = (np.asarray([n, n, n]) - 1) / 2
    sphere = sum((g[i] - c[i])**2 for i in range(3)) <= 6**2
    cylinder = ((g[1]-c[1])**2 + (g[2]-c[2])**2 <= 4**2) & (g[0] >= 7) & (g[0] < 33)
    step = np.zeros_like(sphere)
    for lo, hi, radius in [(4, 15, 3), (15, 26, 5), (26, 37, 7)]:
        step[lo:hi] = ((g[1, lo:hi]-c[1])**2 + (g[2, lo:hi]-c[2])**2 <= radius**2)
    return [("SYN-LT-SPHERE", sphere), ("SYN-LT-CYLINDER", cylinder), ("SYN-LT-STEP", step)]


def phase_fixtures():
    gap = np.zeros((24, 24, 24), bool); gap[:, :, 2:7] = True; gap[:, :, 12:17] = True
    stripes = np.zeros_like(gap)
    for start in range(0, 24, 6): stripes[:, :, start:start+2] = True
    return [("SYN-GAP", gap), ("SYN-PHASE-STRIPES", stripes)]


def ect_fixtures():
    n = 28; g = np.indices((n, n, n)); c = (np.asarray([n, n, n]) - 1) / 2
    empty = np.zeros((n, n, n), bool); full = np.ones_like(empty)
    two = np.zeros_like(empty); two[3:9, 3:9, 3:9] = True; two[18:24, 18:24, 18:24] = True
    rho = np.sqrt((g[0]-c[0])**2 + (g[1]-c[1])**2)
    torus = (rho - 7.0)**2 + (g[2]-c[2])**2 <= 2.2**2
    cavity = np.zeros_like(empty); cavity[3:25, 3:25, 3:25] = True; cavity[9:19, 9:19, 9:19] = False
    shifted = np.zeros_like(empty); shifted[5:11, 8:14, 10:16] = True
    return [("SYN-EMPTY", empty), ("SYN-FULL", full), ("SYN-2BODY", two), ("SYN-TORUS", torus), ("SYN-CAVITY", cavity), ("SYN-ECT-SHIFT", shifted)]


def fibonacci_normals(n=4000):
    i = np.arange(n); z = 1 - 2*(i+0.5)/n; phi = np.pi*(3-math.sqrt(5))*i; r = np.sqrt(1-z*z)
    return np.column_stack([r*np.cos(phi), r*np.sin(phi), z])


def main():
    REPORTS.mkdir(parents=True, exist_ok=True)
    permit = json.loads((FACTORY / "contracts" / "PRM-098_BOUNDED_EXECUTION_PERMIT_20260723.json").read_text(encoding="utf-8"))
    if permit["status"] != "authorized_bounded_progressive_execution": raise SystemExit("permit not active")
    rows = []
    group_start = time.perf_counter()
    for fid, volume, predicate, expected in graph_fixtures():
        t = time.perf_counter(); r = skeleton_graph_outputs(volume, 1.0); passed = bool(predicate(r.outputs))
        rows.append({"fixture_id": fid, "candidate_group_id": "LIT-X006", "status": "PASS" if passed else "FAIL", "observed": json.dumps(r.outputs, sort_keys=True), "expected": expected, "independent_check": "integer graph identities", "max_abs_error": 0.0 if passed else math.nan, "runtime_s": time.perf_counter()-t})

    for fid, volume in lt_fixtures():
        t=time.perf_counter(); field, _ = local_thickness_field(volume, 1.0, max_seconds=60); brute = brute_local_thickness(volume, 1.0); err=float(np.max(np.abs(field[volume]-brute[volume])))
        vals=field[volume]; q=np.quantile(vals,[.1,.5,.9]); edt=ndi.distance_transform_edt(np.pad(volume,1))[1:-1,1:-1,1:-1]
        if fid=="SYN-LT-SPHERE": predicate=abs(np.max(vals)-2*np.max(edt))<1e-6 and np.all(vals>0)
        elif fid=="SYN-LT-CYLINDER": predicate=abs(np.quantile(vals,.5)-2*np.max(edt))<=1.0
        else: predicate=q[0] < q[1] < q[2] and q[0]/q[1] < 1
        rows.append({"fixture_id":fid,"candidate_group_id":"LIT-X008","status":"PASS" if predicate and err<1e-6 else "FAIL","observed":json.dumps({"q10":q[0],"q50":q[1],"q90":q[2],"max":float(vals.max())}),"expected":"maximal-ball brute replay; fixture-specific truth","independent_check":"all-center brute-force containing-sphere enumeration","max_abs_error":err,"runtime_s":time.perf_counter()-t})

    for fid, volume in phase_fixtures():
        t=time.perf_counter(); r=phase_scale_outputs(volume,1.0); vals=r.outputs
        direct=phase_scale_outputs(volume.copy(),2.0).outputs  # independent scale-invariance check
        err=max(abs(vals[k]-direct[k]) for k in vals if math.isfinite(vals[k]))
        passed=err<1e-12 and all(math.isfinite(x) and x>0 for x in vals.values())
        rows.append({"fixture_id":fid,"candidate_group_id":"LIT-X019","status":"PASS" if passed else "FAIL","observed":json.dumps(vals,sort_keys=True),"expected":"matched same-mask solid/void parent quotient and pitch invariance","independent_check":"repeat with common pitch multiplied by two","max_abs_error":err,"runtime_s":time.perf_counter()-t})

    ect_cache={}
    for fid, volume in ect_fixtures():
        t=time.perf_counter(); r=ect_outputs(volume,40/volume.shape[0],max_seconds=120); curve=r.artifacts["ECT_curve_26x129"]; final=metric(r.outputs,"ect_final_chi_solid_density_trace_per_mm3"); chi=int(euler_number(volume,connectivity=3)) if volume.any() else 0
        expected_final=chi/64000; final_err=abs(final-expected_final)
        if fid=="SYN-EMPTY": passed=np.all(curve==0)
        elif fid=="SYN-FULL": passed=final_err<1e-12 and chi==1
        elif fid=="SYN-2BODY": passed=final_err<1e-12 and chi==2
        elif fid=="SYN-TORUS": passed=final_err<1e-12 and chi==0
        elif fid=="SYN-CAVITY": passed=final_err<1e-12 and chi==2
        else:
            base=np.zeros_like(volume); base[10:16,8:14,10:16]=True; b=ect_outputs(base,40/base.shape[0],max_seconds=120); passed=abs(metric(b.outputs,"ect_final_chi_solid_density_trace_per_mm3")-final)<1e-12 and not np.allclose(b.artifacts["ECT_curve_26x129"],curve)
        ect_cache[fid]=curve
        rows.append({"fixture_id":fid,"candidate_group_id":"LIT-X024","status":"PASS" if passed else "FAIL","observed":json.dumps({"chi":chi,"final_density":final}),"expected":"final Euler identity and fixture-specific topology/translation truth","independent_check":"direct full-mask skimage Euler number","max_abs_error":final_err,"runtime_s":time.perf_counter()-t})

    n=20; zero=np.zeros((n,n,n),bool); one=np.ones_like(zero); checker=np.indices((n,n,n)).sum(axis=0)%2==0; stripes=np.indices((n,n,n))[0]%2==0
    glcm_cases=[("SYN-GLCM-ZERO",zero), ("SYN-GLCM-ONE",one), ("SYN-GLCM-CHECKER",checker), ("SYN-GLCM-STRIPES",stripes)]
    for fid,volume in glcm_cases:
        t=time.perf_counter(); allv=[binary_glcm_at_shift(volume,a,1) for a in range(3)]
        if fid=="SYN-GLCM-ZERO": passed=all(abs(v[k]-e)<1e-12 for v in allv for k,e in {"P11":0,"contrast":0,"entropy":0,"homogeneity":1,"asm":1}.items())
        elif fid=="SYN-GLCM-ONE": passed=all(abs(v[k]-e)<1e-12 for v in allv for k,e in {"P11":1,"contrast":0,"entropy":0,"homogeneity":1,"asm":1}.items())
        elif fid=="SYN-GLCM-CHECKER": passed=all(abs(v[k]-e)<1e-12 for v in allv for k,e in {"P11":0,"contrast":1,"homogeneity":.5,"asm":.5,"entropy":math.log(2)}.items())
        else: passed=allv[0]["contrast"]==1 and allv[1]["contrast"]==0 and allv[2]["contrast"]==0
        identity=max(abs(v["homogeneity"]-(1-v["contrast"]/2)) for v in allv)
        rows.append({"fixture_id":fid,"candidate_group_id":"LIT-X028","status":"PASS" if passed and identity<1e-12 else "FAIL","observed":json.dumps(allv,sort_keys=True),"expected":"binary analytic GLCM truth","independent_check":"closed-form binary distribution identity","max_abs_error":identity,"runtime_s":time.perf_counter()-t})

    odf=[]
    axisz=np.array([[0,0,1],[0,0,-1]],float); odf.append(("SYN-ODF-AXIS-Z",axisz,np.ones(2)))
    cubic=np.array([[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]],float); odf.append(("SYN-ODF-CUBIC",cubic,np.ones(6)))
    iso=fibonacci_normals(); odf.append(("SYN-ODF-ISOTROPIC",iso,np.ones(len(iso))))
    base=np.array([[1,0,0],[0.2,.9,.3],[-.4,.1,.8]],float); base/=np.linalg.norm(base,axis=1)[:,None]; odf.append(("SYN-ODF-ROTATE",base,np.array([1.,2.,3.])))
    for fid,normals,area in odf:
        t=time.perf_counter(); vals=normal_harmonics_from_normals(normals,area)
        if fid=="SYN-ODF-AXIS-Z": passed=all(abs(v-1)<1e-12 for v in vals.values()); err=max(abs(v-1) for v in vals.values())
        elif fid=="SYN-ODF-CUBIC": err=max(abs(vals["LIT-X031::surface_normal_H2"]),abs(vals["LIT-X031::surface_normal_Q2_z"])); passed=err<1e-12
        elif fid=="SYN-ODF-ISOTROPIC": err=max(abs(v) for v in vals.values()); passed=err<1e-3
        else:
            angle=.73; R=np.array([[math.cos(angle),-math.sin(angle),0],[math.sin(angle),math.cos(angle),0],[0,0,1]])
            rotated=normal_harmonics_from_normals(normals@R.T,area); inverted=normal_harmonics_from_normals(-normals,area)
            err=max(max(abs(vals[f"LIT-X031::surface_normal_H{l}"]-rotated[f"LIT-X031::surface_normal_H{l}"]) for l in (2,4,6)),max(abs(vals[k]-inverted[k]) for k in vals)); passed=err<1e-12
        rows.append({"fixture_id":fid,"candidate_group_id":"LIT-X031","status":"PASS" if passed else "FAIL","observed":json.dumps(vals,sort_keys=True),"expected":"harmonic analytic/rotation/sign truth","independent_check":"closed-form axis/cubic or transformed normal set","max_abs_error":err,"runtime_s":time.perf_counter()-t})

    result=pd.DataFrame(rows)
    expected=pd.read_csv(TABLES/"PRM097_synthetic_truth_fixture_registry.csv")
    if set(result.fixture_id)!=set(expected.fixture_id): raise RuntimeError("fixture roster mismatch")
    result.to_csv(REPORTS/"PRM098_synthetic_truth_results.csv",index=False,encoding="utf-8-sig",lineterminator="\n")
    group=result.groupby("candidate_group_id").agg(fixtures=("fixture_id","size"),passed=("status",lambda s:int((s=="PASS").sum())),runtime_s=("runtime_s","sum"),max_abs_error=("max_abs_error","max")).reset_index()
    group["group_gate"]=np.where(group.fixtures==group.passed,"PASS","HOLD")
    group.to_csv(REPORTS/"PRM098_synthetic_group_gate.csv",index=False,encoding="utf-8-sig",lineterminator="\n")
    summary={"status":"PASS" if result.status.eq("PASS").all() else "FAIL","fixtures":f"{result.status.eq('PASS').sum()}/{len(result)}","groups_passed":f"{group.group_gate.eq('PASS').sum()}/{len(group)}","runtime_s":time.perf_counter()-group_start}
    (REPORTS/"PRM098_synthetic_summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary))
    if summary["status"]!="PASS":
        print(result.loc[result.status.ne("PASS"),["fixture_id","observed","expected"]].to_string(index=False)); raise SystemExit(1)


if __name__=="__main__": main()
