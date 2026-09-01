# HQ-GEOM-003 — topology exception preregistration

`HQ-GEOM-003-20260728-001` is a read-only, no-y preregistration. It makes no geometry derivative, mesh repair, slice, raster, descriptor, training, or source mutation.

## Confirmed evidence

| Source | Non-manifold edges | Orientation conflicts | Watertight after weld | Components | Decision |
|---|---:|---:|---|---:|---|
| Lattice A | 6,798 | 0 | No | 8,392 | hold |
| TPMS Gyroid | 103 | 73 | Yes | 1 | hold |

Both source hashes are locked. They have distinct non-clean topology signatures, so one generic repair must not be assumed correct. Existing native route execution does not prove that topology-changing repair or automatic N40 admission preserves descriptor meaning.

## Frozen policy

- `G3-P0-HOLD` — confirmed current policy.
- `G3-P1-REGENERATE` — likely preferred if the controlled generator can emit a clean mesh.
- `G3-P2-REPAIR` — unresolved; needs an isolated hash-bound repair, named settings and selected-slice/full-chain regression.
- `G3-P3-EXCEPTION` — rejected as an automatic shortcut.
- `G3-P4-EXCLUDE` — unresolved fallback.

## QA

- source evidence `2/2` PASS;
- automatic exception rejected;
- protected assets `31/31` PASS;
- no geometry or descriptor calculation occurred.

## Required laboratory answer

```text
Lattice A: regenerate / repair / exclude
TPMS Gyroid: regenerate / repair / exclude
If repair: permitted tool or method, if known
40 mm meaning: analysis coordinate only / physical geometry requirement / other
```

See `CHUCK_INPUT_PACKET_TOPOLOGY_POLICY_20260728.md` and `TOPOLOGY_EXCEPTION_CONTRACT.json` in this folder for the complete contract.
