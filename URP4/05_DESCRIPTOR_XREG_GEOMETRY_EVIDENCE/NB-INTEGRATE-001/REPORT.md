# NB-INTEGRATE-001 — versioned development import route controller

- Run: `NB-INTEGRATE-001-20260729-001`
- Index: `RUN-361 / DEC-366 / CHG-351 / LAB-CHG-320 / R09-BB-1321..1323`
- Runtime: `KMK312` — `C:\Users\chuck\Documents\Codex\2026-06-22\a2f23dee1d9a824b840a0175ca9a1f4b-https-app-notion-com-p\tools\envs\KMK312\python.exe` / Python `3.12.12`
- Scope: source-policy controller, fixture tests, status-only notebook and manifests. No slicing, descriptor extraction, y, model fit, prediction or source mutation.

## Delivered development integration

1. New module `urp4.route_policy.v0_1` implements ROUTE-VALID-004 as a strict preflight controller.
2. New notebook `NB-DEV v0.6` is a four-cell status/preflight notebook, with `RUN_PREFLIGHT=False` by default. It is neither NB-CURRENT nor a replacement for it.
3. A real hash-bound F1 raw STL preflight chooses development Route C and carries the mandatory `F1_Z400_UNRESOLVED` warning.
4. Every manifest records source SHA, policy SHA, config SHA, `sys.executable`, Python version, environment path and actual command.

## Fail-closed implementation

| Input condition | Controller result |
|---|---|
| paired-confirmed imported STL + exact SHA + approved config | development preflight approved; `execution_enabled=false` |
| F1 | same, plus persistent `F1_Z400_UNRESOLVED` |
| paired-likely, STL-only, orientation-held or hash mismatch | rejected before route dispatch |
| repair/hole-fill/proxy STEP setting | rejected |
| production request | rejected |

Route A/B/C science is not reimplemented here. Route C is referenced only as `IMP-STL-ORIENTED-NONZERO-DEVELOPMENT-ROUTE-C`; an additional scientific gate is necessary before any actual route execution.

## QA

- Controller fixture regression: `9/9 PASS`.
- Independent controller/notebook/hash regression: `13/13 PASS`; protected assets `31/31` unchanged.
- Independent notebook static QA: `8/8 PASS`.
- F1 real-source preflight: source SHA matches ROUTE-VALID-003; warning propagates; all geometry/slice/descriptor/y/model execution fields are false.

## Runtime discovery correction

The canonical environment is the project-local KMK312 runtime shown above. The interrupted duplicate directory `C:\Users\chuck\anaconda3\envs\KMK312` is marked noncanonical/partial and is not used. This correction does not alter or invalidate prior SLICE/R09 scientific outputs.

## Merge recommendation

**CONDITIONAL YES — versioned development scope only.** Merge this new module, new NB-DEV v0.6, contracts/fixtures/QA and documentation as an additive development integration. Do not modify or replace NB-CURRENT, NB-ORIG or LEGACY-PY. Keep scientific production qualification closed and retain `STRICT-F1-001` as a deferred resource-bound task.
