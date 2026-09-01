# ROUTE-VALID-004 merge packet

## Recommendation

**CONDITIONAL YES — policy merge only.** Merge the route-policy contract, tables and log synchronization. This does not modify NB-CURRENT, NB-ORIG, LEGACY-PY, source geometry or original Excel.

## Decision

- Versioned development integration: `conditional_yes`.
- Scientific production qualification: `no`.
- ROUTE-VALID-003A prerequisite: `rejected`.

## Evidence

- ROUTE-VALID-001 QA `13/13 PASS`
- ROUTE-VALID-002 QA `14/14 PASS`
- ROUTE-VALID-003 QA `11/11 PASS`; 288 metrics replayed exactly.
- ROUTE-VALID-003A is quarantine-only after two resource-limited exact-A attempts. It has no official calculation, QA or source-attribution result.

## Required preservation

- F1 `z400` remains `unresolved` and must propagate as a development warning.
- The exact-A long run and declared deflection sweep remain a STRICT later track, not a prerequisite for technical development integration.
- Source identity and hash checks must fail closed.

## Next separately authorized work

`NB-INTEGRATE-001_IMPORT_ROUTE_CONTROLLER_VERSIONED_DEVELOPMENT_NO_Y` — build/test an isolated controller contract only. No production release, y, model training, or NB-CURRENT overwrite.
