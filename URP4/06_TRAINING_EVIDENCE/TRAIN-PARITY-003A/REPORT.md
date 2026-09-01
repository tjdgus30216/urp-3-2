# TRAIN-PARITY-003A-20260801-001 — target identity and hold-policy repair (NO_FIT)

- Decision: **GO_FOR_TRAIN_PARITY_004_SENTINEL_EXECUTION**
- Execution: **NO_FIT / NO_PREDICTION**
- Canonical target crosswalk: **16/16 confirmed**
- Policy: **13 primary / 3 hold** (`GC`, `HE`, `HK`)
- Source runner preflight: **10/10 PASS**
- Adapter branch NO_FIT: **10/10 PASS**
- Independent QA: **23/23 PASS** (one committed QA execution; one earlier runner attempt aborted before QA artifact commit due to JSON packaging)

## Root cause and repair

P1 bound replay output names to the selected Excel columns by the wrong positional/name crosswalk. The target payload and frozen fold manifest remained column/hash keyed and valid. Version v0.2 therefore treats the canonical ID, Excel column, value hash, NaN-mask hash, group membership, and fold target ID as identity; the human-readable name is display metadata. The predecessor `FW/GA/HE` hold mapping is retained only as superseded audit evidence.

## Safety boundary

The ten numerical branch files and fold bytes are unchanged. The isolated source runner compiled protected notebook definitions directly, bound target/fold and dynamic state explicitly, and then stopped at the NO_FIT permit. No prediction or metric rows were created. P8 remains prohibited.

## Sentinel

`TRAIN2NF::HI` = `FRF 3000–6500 Hz AVG`, outer repeat `0`, is the sole preregistered sentinel for P0–P7. The permit is readiness metadata only and still requires explicit execution approval.
