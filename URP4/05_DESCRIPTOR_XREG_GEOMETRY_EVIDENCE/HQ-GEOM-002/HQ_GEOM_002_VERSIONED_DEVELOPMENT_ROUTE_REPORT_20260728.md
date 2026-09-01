---
work_id: HQ-GEOM-002_VERSIONED_DEVELOPMENT_ROUTE_INTEGRATION_AND_CONTRACT_TESTS_NO_Y
run_id: HQ-GEOM-002-20260728-001
status: passed_bounded_development_route
runtime: KMK312 Python 3.12.12
route_id: HQ-V0.3-GEN-N40-DEVELOPMENT
---

# HQ-GEOM-002 — versioned generated-N40 development route

## Conclusion

`HQ v0.3` now provides a **separate, development-only** route for a controlled generated STL that is topology-clean. It does not modify or replace HQ v0.1, NB-CURRENT, NB-ORIG, LEGACY-PY, or either original Excel workbook.

The Voxel representative passes the entire native P1000/Z801 image/pixel/component/RUN-139 chain after a preserved-original, centered-uniform 40 mm analysis derivative is created. Its derivative and primitive output tables are byte-for-byte/value-for-value consistent with the independently produced HQ-GEOM-001 Voxel reference.

## Contract

| Item | Frozen value |
|---|---|
| Route | `HQ-V0.3-GEN-N40-DEVELOPMENT` |
| Development revision | `HQ-GEOM-002/v0.3/r1` |
| Analysis domain | `40 × 40 × 40 mm` |
| Production pixels / slices | `1000 × 1000 px` / `801` |
| Image lifecycle | streaming PNG readback; retain `0` PNG after completion |
| Source operation | positions-only centered uniform affine transform; no repair/dedup/fill/winding rewrite |
| Permitted generated source | `topology_clean=true` only |

The route fails closed when source topology is not clean. This is deliberate: the prior three-family N40 calculation showed that Lattice A and TPMS retain `topology_clean=false`; they cannot be silently admitted through the Voxel-qualified route.

## Voxel evidence

| Evidence | Result |
|---|---:|
| Source SHA-256 | `ff1b64d5a9369d2d6a2e3dc3ea7a743ec77fc6afd40cbd1a176597f0b0324d43` |
| Source extent | `38 × 38 × 38 mm` |
| Uniform scale | `1.0526315789473684` |
| N40 derivative SHA-256 | `b8f8727d6b6f67b3ac3dd37b5faeb94ff2bbb283eee06954bb22d5f08534e68a` |
| Output rows | `801` slices, `800` overlays, `9` scalars |
| PNG readback mismatch / retained PNG | `0 / 0` |
| HQ-GEOM-001 reference parity | `6/6` |
| Protected asset audit | `31/31` |

The descriptor producer was resumed after the first full execution; it did not recalculate or overwrite the accepted result. The derivative hash remains exactly the HQ-GEOM-001 Voxel derivative hash.

## Independent contract and parity QA

`HQ_GEOM_002_contract_and_parity_QA.py` passes:

- valid topology-clean Voxel request;
- wrong source SHA rejection;
- non-40 mm target rejection;
- wrong route ID rejection;
- wrong image-policy rejection;
- non-clean Lattice source rejection;
- Voxel derivative plus four primitive tables and descriptor-result parity (`6/6`), with legitimate missing component-table fields compared using `equal_nan=True`;
- source identity, protected assets (`31/31`), and no-y/no-modeling scope checks.

## Claim boundary

- **confirmed:** Voxel can use the versioned N40 development route reproducibly.
- **likely:** this isolated route is a suitable integration pattern for other generated sources *after their own topology/domain contract passes*.
- **unresolved:** whether Lattice and TPMS source topology may be accepted, repaired under a registered policy, regenerated, or excluded; the physical interpretation of the generated 40 mm convention; exact LEGACY-PY/Excel parity.
- **rejected:** silently admitting non-clean Lattice/TPMS meshes, treating v0.3 as HQ v0.1, or claiming physical-canonical/modeling readiness.

## Artifacts

- Producer summary: `PRODUCER_SUMMARY.json`
- Independent QA: `INDEPENDENT_QA.json`
- Development geometry/output: `outputs/HQ_GEOM002/HQG3-cad3e072347b/`
- HQ-GEOM-001 Voxel baseline: `outputs/HQ_GEOM001/HQ-GEOM-001-20260728-001/VOX/`

## Next boundary

Before Lattice or TPMS is admitted to HQ v0.3, preregister `HQ-GEOM-003_GENERATED_LATTICE_TPMS_TOPOLOGY_EXCEPTION_CONTRACT_NO_Y`. That task must choose an explicit laboratory policy (accept, regenerate, repair with a separately validated method, or exclude) and must not infer equivalence from the Voxel result.
