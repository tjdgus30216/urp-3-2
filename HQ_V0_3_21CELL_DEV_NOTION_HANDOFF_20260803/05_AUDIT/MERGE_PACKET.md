# MERGE_PACKET — HQ-INTEGRATE-003

## Scope

Additive versioned development HQ only. No existing HQ, submission ZIP, protected notebook, LEGACY-PY, original data, or source geometry was changed.

## Included

- 21-cell notebook and deterministic builder
- v0.3 explicit stage runtime
- KMK312 smoke test
- source audit and QA records

## QA

- Python compilation: PASS
- Frozen replay scalar parity: PASS, max error 0.0
- ARTIFACT_FULL ↔ STREAMING exploratory table/scalar parity: PASS, max scalar error 0.0
- strict v0.1 regression: PASS, 0.0 over 9 scalar rows
- STEP direct descriptor, XREG HQ API, y/Training/model/forward/inverse: intentionally fail-closed

## Boundary

Do not merge this as a replacement for submitted HQ v0.1 or as a scientific production release. It is a next-developer execution map. Test output directories are explicitly excluded.

