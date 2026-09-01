---
work_id: HQ-GEOM-003_GENERATED_LATTICE_TPMS_TOPOLOGY_EXCEPTION_CONTRACT_NO_Y
run_id: HQ-GEOM-003-20260728-001
status: preregistered_pending_lab_policy
runtime: KMK312 Python 3.12.12
---

# HQ-GEOM-003 — Lattice/TPMS topology-exception contract preregistration

## Conclusion

HQ-GEOM-002 established a safe N40 development route only for topology-clean generated STL. This read-only task confirms that the frozen Lattice A and TPMS Gyroid source meshes do **not** satisfy that entry condition. No normalization, mesh repair, slicing, rasterization, descriptor extraction, y access, or model fitting was performed here.

The correct immediate state is therefore **hold pending laboratory policy**, not automatic repair and not broad rejection of either material family.

## Read-only source evidence

| Source | Triangle count | Boundary edges | Non-manifold edges | Orientation conflicts | Watertight after weld | Components | State |
|---|---:|---:|---:|---:|---|---:|---|
| Lattice A | 253,184 | 0 | 6,798 | 0 | No | 8,392 | confirmed non-clean |
| TPMS Gyroid | 168,584 | 0 | 103 | 73 | Yes | 1 | confirmed non-clean |

Both hashes match the frozen HQ-GEOM-001 source identities. The two sources have different failure signatures, so one generic repair rule must not be presumed valid for both.

## Important interpretation

Existing generated-STL full-chain success shows that the current native route can technically slice these files under its own controlled conditions. It does **not** establish that a new N40 development route may silently admit their non-clean topology or that a topology-changing repair preserves descriptor meaning.

## Frozen policy choices

| Policy | Status | Meaning |
|---|---|---|
| `G3-P0-HOLD` | confirmed current policy | Keep both sources out of HQ v0.3 N40 execution. |
| `G3-P1-REGENERATE` | likely preferred if feasible | Generate a new, clean STL from locked parametric generator inputs; keep original as provenance. |
| `G3-P2-REPAIR` | unresolved | Produce a separate, hash-bound repair derivative only after a named repair algorithm/settings and regression contract are approved. |
| `G3-P3-EXCEPTION` | rejected as automatic policy | Never use non-clean admission as a shortcut. It would require separate laboratory authorization and validation. |
| `G3-P4-EXCLUDE` | unresolved fallback | Exclude the affected generated family from this milestone if a trustworthy source cannot be produced. |

## Required evidence before any follow-on calculation

### If regeneration (`G3-P1`) is chosen

1. frozen generator notebook/function, parameter set and runtime;
2. new generated source hash and a topology-clean preflight;
3. explicit statement whether it is intended to be geometrically equivalent to the old source;
4. selected-slice and P1000/Z801 regression under a new run ID.

### If repair (`G3-P2`) is chosen

1. exact repair library/version/parameters and original→derivative hash lineage;
2. topology delta: triangles, edges, components, volume and bbox;
3. selected-slice visual/metric regression against the approved reference criterion;
4. independent descriptor replay; no source overwrite.

## QA

- two source hashes locked: PASS;
- both sources confirmed non-clean: PASS;
- automatic exception route rejected: PASS;
- protected assets: `31/31` PASS;
- no geometry or descriptor execution: PASS.

## Pending laboratory decision

Choose the treatment for each source independently:

```text
Lattice A: G3-P1 regenerate / G3-P2 repair / G3-P4 exclude
TPMS Gyroid: G3-P1 regenerate / G3-P2 repair / G3-P4 exclude
```

`G3-P3` is not selectable without an explicitly documented exception and validation plan.

## Artifacts

- [Frozen contract](TOPOLOGY_EXCEPTION_CONTRACT.json)
- [Source topology evidence](../LINK_TARGETS_R2/HQ-GEOM-003-20260728-001_source_topology_evidence.csv)
- [Policy options](../LINK_TARGETS_R2/HQ-GEOM-003-20260728-001_policy_options.csv)
- [Independent preregistration QA](INDEPENDENT_PREREG_QA.json)
