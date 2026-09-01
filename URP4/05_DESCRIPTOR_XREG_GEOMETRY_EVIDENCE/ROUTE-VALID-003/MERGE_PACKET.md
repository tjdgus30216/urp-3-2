# ROUTE-VALID-003 merge packet

## Recommendation

**CONDITIONAL YES:** merge the F1 selected-slice evidence, frozen-C replay registry, QA, direct-B-rep curve-raster adapter provenance, and logs.  Do **not** merge a production route policy or NB integration decision.

## Result

- Source/common transform: confirmed.
- Route A/B: 138/144 exact; six z400 representation differences remain.
- Route A/C: 129/144 exact; nine boundary-only and six z400 interior-labelled cases.
- QA: 288/288 metric replays, maximum error 0.0; protected assets unchanged.
- Final recommendation: `repeat_preregistered_F1_targeted_cases`.

## Changed / added evidence

- Producer: `scripts/ROUTE_VALID_003_f1_step_reference_pixel_phase.py`
- Direct-B-rep adapter probe: `scripts/ROUTE_VALID_003A_brep_curve_raster_adapter_probe.py`
- Independent QA: `scripts/ROUTE_VALID_003_independent_qa.py`
- Finalizer: `scripts/ROUTE_VALID_003_finalize.py`
- New A/B masks and new comparison tables are under run `ROUTE-VALID-003-20260729-002`; C is path/hash-reused from `IMSTL-007-20260728-002`.
- `ROUTE-VALID-003-20260729-001` is quarantined and preserved; it supplies no scientific result.

## Scope locks

No Route-C regeneration, F1 full STEP Z801, all58, descriptor/formula parity, Excel/LEGACY-PY, y, Training, prediction, inverse design, NB-ORIG/NB-CURRENT/LEGACY-PY/original-Excel mutation occurred.
