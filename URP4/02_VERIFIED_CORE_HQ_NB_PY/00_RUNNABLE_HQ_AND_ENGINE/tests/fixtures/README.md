# HQ validation fixtures

These files make the HQ validation suite self-contained. They are validation
fixtures only; they are not generated training data and must not be edited.

| File | Provenance | SHA-256 |
|---|---|---|
| `L28_UBCCz_VF30_imported.stl` | Exact byte copy of doctor-provided `data/raw/STRICT-GEOM-001_L28_20260724/originals/L28. UBCCz_VF30.stl` | `75236D351D350D33796D74E35A04AF1D072483C641A14E70D5C3BCCC738A7E88` |
| `L28_UBCCz_VF30_original.stp` | Exact byte copy of doctor-provided `data/raw/STRICT-GEOM-001_L28_20260724/originals/L28. UBCCz_VF30.stp` | `83C6C925814326F86DC0674E26D46D5FD2A8DACAA06D74CC4AC6E994F67F7F94` |
| `generated_controlled_box_N40.stl` | Deterministic 40 mm controlled fixture used by the generated-STL route smoke | `EC1B527705B8045D5748A532519BF9EAE4AD3B7DDAD6081B85C3386669A8C15C` |

The local L28 copies were introduced after the scientific full-chain run. Their
hashes match the files used in that run, so changing test paths does not change
the geometry under test.
