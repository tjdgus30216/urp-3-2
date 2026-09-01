# ROUTE-VALID-004 — Route policy decision and NB integration gate (no-y)

- Work / run: `ROUTE-VALID-004_ROUTE_POLICY_DECISION_AND_NB_INTEGRATION_GATE_NO_Y` / `ROUTE-VALID-004-20260729-001`
- Settings address: `IDX-URP4-1-GEOM-ROUTES / CFG-ROUTEVALID004-POLICY-r1`
- Runtime: policy-only read of immutable evidence. **No geometry/slice/descriptor calculation was run**, so no non-KMK computational result is introduced.
- Scope: Route policy and NB integration gate only. NB-ORIG, NB-CURRENT, LEGACY-PY, original Excel, geometry assets and images remain unchanged.

## Verdict

| Decision | Status | Meaning |
|---|---|---|
| Versioned development integration | **CONDITIONAL YES** | A new, separately versioned NB/module may add import route dispatch, hash/identity checks, warning propagation and artifact manifests. It must not overwrite the existing NB-CURRENT generated-STL path. |
| Scientific production qualification | **NO / closed** | Selected-slice evidence does not establish full descriptor, formula, full-Z801, Excel/LEGACY-PY or performance parity. |
| ROUTE-VALID-003A as a technical-integration prerequisite | **rejected** | 003A is quarantine-only due to resource limits. It contributes no official result and does not invalidate ROUTE-VALID-003. |

## Evidence used and its boundary

1. ROUTE-VALID-001: source eligibility is hash-audited (`24 paired_confirmed / 9 paired_likely / 25 stl_only`); C1 A-C selected slice is exact.
2. ROUTE-VALID-002: B1/L7 confirmed pairs support exact A-C masks at selected z-mid positions and P500/P1000.
3. ROUTE-VALID-003: F1's broad selected-slice panel is technically traceable and independently replayed. At z400, the same six interior residuals occur in A-B and A-C, so an imported-STL defect is **not identified**.
4. ROUTE-VALID-003A: two exact-A attempts were quarantined for resource exhaustion without an official result. It is **not a failure of 003** and only preserves the F1 z400 cause as unresolved.

Route A is original STEP direct B-rep; Route B is a controlled tessellation of that *same STEP*; Route C is a separately stored paired imported STL. A-B is representation consistency only. A-C is the only paired imported-STL observation.

## Source-type policy

The route policy is machine-readable in [source policy](../../../reports/tables/ROUTE-VALID-004-20260729-001_source_type_route_policy.csv). The key rule is: route eligibility is a property of the source identity and evidence level, not a convenience switch.

- `paired_confirmed`: Route C may enter a **versioned development** import pathway after hash, identity, transform, config and output-manifest replay. It is not production-qualified.
- `paired_likely`: sensitivity only; metadata must retain `source_identity=likely`. It cannot be reported as imported-STL accuracy evidence.
- `stl_only`: no STEP comparison may be fabricated. A separate mesh/preflight/repeatability/visual-review lane is required before technical admission.
- orientation-held and hash-mismatched assets stop before slice dispatch.

## F1 z400 warning

`F1_Z400_UNRESOLVED` is a mandatory persistent warning for the F1 imported-STL development route. It must appear in its output manifest and downstream report. It blocks production qualification, but it does **not** block the technical route-controller integration because current evidence does not attribute the residual to imported STL.

The STRICT backlog is deliberately separated: `STRICT-F1-001_EXACT_A_LONG_RUN_AND_DECLARED_DEFLECTION_SENSITIVITY_NO_Y`. It covers a long exact-A run and an explicitly declared deflection sweep when suitable compute is available. It is not retroactively made a condition of ROUTE-VALID-003 or the versioned-development integration.

## NB integration boundary

**Allowed in a new versioned development layer only**:

- input selector (`generated` vs `imported`), `source_type`, `source_identity_status`, `route_id` and a hash-bound import manifest;
- fail-closed preflight before any slice; explicit transform/grid/route-config hashes;
- Route C dispatcher for eligible `paired_confirmed` imported STL only; and
- persistent warnings, including F1 z400, in result manifest and handoff report.

**Explicitly held**:

- direct edit/replacement of NB-CURRENT's historical generated-STL route;
- NB-ORIG or LEGACY-PY edits; source repair, proxy STEP, hole filling or silent mesh modification;
- any scientific production claim, all58 import rollout, full descriptor/formula equivalence, Excel/LEGACY-PY/y/Training claim.

## Fail-closed behavior

The [fallback table](../../../reports/tables/ROUTE-VALID-004-20260729-001_fail_closed_fallback.csv) enumerates required hard stops. The controller must stop rather than choose a permissive route when source identity, hash, transform, orientation or required warning status is missing. A–B must never be converted into an independent imported-STL claim.

## Required next action

1. `NB-INTEGRATE-001_IMPORT_ROUTE_CONTROLLER_VERSIONED_DEVELOPMENT_NO_Y`: contract-build only, then test the controller against synthetic/fixture eligibility cases. No NB-CURRENT replacement.
2. Keep `STRICT-F1-001` in the STRICT queue for future resource availability.
3. Keep STL-only models and source-likely pairs out of production qualification until their separate contracts are completed.

## Status labels

- **confirmed:** the policy boundary itself; predecessor 001–003 QA status; source eligibility categories; 003A quarantine-only status.
- **likely:** selected-slice cross-family support for the paired-confirmed imported-STL development route.
- **unresolved:** F1 z400 attribution, full descriptor/full-Z801 behavior, STL-only route qualification, formula parity.
- **rejected:** treating 003A absence as a failed 003 result; treating A-B as independent STL validation; production promotion from selected slices.
