"""ROUTE-VALID-004 policy-only producer.

This script consumes only immutable ROUTE-VALID-001..003 evidence and the
quarantine record for 003A.  It performs no slicing, mesh edit, descriptor,
Excel, y, or model calculation.  It exists to make the route policy machine
readable and reproducible before any later NB versioned-development change.
"""
from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
RUN_ID = "ROUTE-VALID-004-20260729-001"
RESULT = LAB / "results" / "ROUTE-VALID-004" / RUN_ID
TABLES = LAB / "reports" / "tables"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def main() -> None:
    RESULT.mkdir(parents=True, exist_ok=False)
    TABLES.mkdir(parents=True, exist_ok=True)
    predecessors = {
        "route_valid_001": LAB / "results" / "ROUTE-VALID-001" / "ROUTE-VALID-001-20260729-001" / "INDEPENDENT_QA.json",
        "route_valid_002": LAB / "results" / "ROUTE-VALID-002" / "ROUTE-VALID-002-20260729-001" / "INDEPENDENT_QA.json",
        "route_valid_003": LAB / "results" / "ROUTE-VALID-003" / "ROUTE-VALID-003-20260729-002" / "INDEPENDENT_QA.json",
        "route_valid_003a_quarantine": LAB / "results" / "ROUTE-VALID-003A" / "ROUTE-VALID-003A-20260729-003" / "QUARANTINE_NOTE.md",
    }
    inputs = {}
    for key, path in predecessors.items():
        if not path.exists():
            raise FileNotFoundError(path)
        inputs[key] = {"path": str(path), "sha256": sha256(path)}
    for key in ("route_valid_001", "route_valid_002", "route_valid_003"):
        qa = json.loads(Path(inputs[key]["path"]).read_text(encoding="utf-8"))
        if qa.get("status") != "passed" or not all(qa.get("checks", {}).values()):
            raise RuntimeError(f"predecessor QA is not clean: {key}")
    quarantine = Path(inputs["route_valid_003a_quarantine"]["path"]).read_text(encoding="utf-8")
    if "not eligible for QA, merge" not in quarantine:
        raise RuntimeError("003A quarantine wording not found")

    source_rows = [
        {
            "source_type": "generated_controlled_stl_topology_clean",
            "eligibility": "development_only",
            "allowed_route": "Route G: existing generated-native deterministic slicer",
            "evidence_level": "likely",
            "development_integration": "allowed only with source/config/output hashes and topology_clean=true",
            "production_qualification": "blocked; separate generated descriptor/engineering qualification required",
            "fail_closed_trigger": "unknown source lineage, topology_clean=false, missing hash or unknown configuration",
            "notes": "This is not Route A/B/C and makes no imported-STL claim.",
        },
        {
            "source_type": "original_step_with_paired_confirmed_imported_stl",
            "eligibility": "paired_confirmed",
            "allowed_route": "A reference; B same-source diagnostic; C improved imported-STL winding route",
            "evidence_level": "likely cross-family selected-slice support",
            "development_integration": "allowed as a versioned, artifact-retaining imported route after hash/identity/config replay",
            "production_qualification": "blocked; selected-slice area parity is not full descriptor/formula/full-Z801 qualification",
            "fail_closed_trigger": "hash/identity mismatch, unknown grid/transform, source mutation, or a request to treat A-B as imported-STL evidence",
            "notes": "A-C only is the independent paired imported-STL comparison.",
        },
        {
            "source_type": "original_step_with_paired_likely_imported_stl",
            "eligibility": "paired_likely",
            "allowed_route": "A reference and C sensitivity route only",
            "evidence_level": "unresolved for source-accuracy judgment",
            "development_integration": "allowed only if metadata preserves source_identity=likely and output is explicitly sensitivity-labelled",
            "production_qualification": "blocked",
            "fail_closed_trigger": "attempt to label as confirmed pair or use as imported-STL accuracy proof",
            "notes": "B3/L1 belong here; no source identity promotion is implied.",
        },
        {
            "source_type": "stl_only_imported",
            "eligibility": "no_original_step_reference",
            "allowed_route": "C only, with improved imported-STL preflight",
            "evidence_level": "unresolved",
            "development_integration": "not enabled by this policy; requires source-local mesh QA, repeatability, phase/resolution and retained visual review contract",
            "production_qualification": "blocked; no A-C reference exists",
            "fail_closed_trigger": "attempted STEP comparison, absent mesh QA, changed STL bytes, or missing retained quality record",
            "notes": "L12-L20 and T1-T16 are in this lane.",
        },
        {
            "source_type": "orientation_held_pair",
            "eligibility": "crosswalk_hold",
            "allowed_route": "none until orientation crosswalk is accepted",
            "evidence_level": "unresolved",
            "development_integration": "blocked",
            "production_qualification": "blocked",
            "fail_closed_trigger": "missing or unresolved orientation transform",
            "notes": "T17 remains held.",
        },
        {
            "source_type": "missing_or_hash_mismatch",
            "eligibility": "invalid",
            "allowed_route": "none",
            "evidence_level": "rejected",
            "development_integration": "blocked",
            "production_qualification": "blocked",
            "fail_closed_trigger": "always",
            "notes": "ROUTE-VALID-001 found zero current cases; rule remains explicit.",
        },
    ]
    family_rows = [
        {"model_or_group":"C1", "family":"C", "source_status":"paired_confirmed", "evidence":"A-B/A-C exact at z-mid P1000", "route_policy":"development support only", "status":"likely", "production_status":"blocked"},
        {"model_or_group":"B1", "family":"B", "source_status":"paired_confirmed", "evidence":"A-B/A-C exact at z-mid P500/P1000", "route_policy":"development support only", "status":"likely", "production_status":"blocked"},
        {"model_or_group":"L7", "family":"L", "source_status":"paired_confirmed", "evidence":"A-B/A-C exact at z-mid P500/P1000", "route_policy":"development support only", "status":"likely", "production_status":"blocked"},
        {"model_or_group":"F1", "family":"F", "source_status":"paired_confirmed", "evidence":"F1 broad stress QA passes; z400 A-B/A-C co-residuals", "route_policy":"development integration allowed with unresolved warning", "status":"unresolved", "production_status":"blocked pending STRICT-F1-001"},
        {"model_or_group":"B3/L1", "family":"B/L", "source_status":"paired_likely", "evidence":"pair identity likely, not confirmed", "route_policy":"sensitivity only", "status":"unresolved", "production_status":"blocked"},
        {"model_or_group":"L12-L20/T1-T16", "family":"L/T", "source_status":"stl_only", "evidence":"no original STEP in inventory", "route_policy":"separate STL-only validation lane", "status":"unresolved", "production_status":"blocked"},
        {"model_or_group":"T17", "family":"T", "source_status":"orientation_held", "evidence":"orientation crosswalk unresolved", "route_policy":"no route", "status":"unresolved", "production_status":"blocked"},
    ]
    gate_rows = [
        {"scope":"NB versioned development integration", "decision":"conditional_yes", "allowed":"new import controller/route dispatch metadata, source hash and identity checks, route policy enforcement, warning/output manifest fields; Route C only for paired_confirmed eligible input", "not_allowed":"overwrite NB-CURRENT historical generated route; alter NB-ORIG/LEGACY-PY; declare science parity; y/training", "required_condition":"separate versioned notebook/module, immutable source, fail-closed preflight, retained output manifest", "003A_dependency":"not required"},
        {"scope":"scientific production qualification", "decision":"no", "allowed":"none beyond reading retained evidence", "not_allowed":"production descriptor claim, universal imported-STL claim, formula/full-Z801/Excel/LEGACY-PY/y equivalence claim", "required_condition":"resolved source-specific qualification including F1 z400 and descriptor/full-chain scope", "003A_dependency":"STRICT follow-up evidence may contribute but no automatic pass criterion is set"},
        {"scope":"F1 development route", "decision":"conditional_yes", "allowed":"hash-bound Route C technical development with persistent F1_Z400_UNRESOLVED warning", "not_allowed":"production qualification or removing warning", "required_condition":"warning flag must propagate to report and output manifest", "003A_dependency":"not required for technical integration"},
        {"scope":"F1 production route", "decision":"no", "allowed":"none", "not_allowed":"production descriptor release", "required_condition":"STRICT-F1-001 exact-A long-run plus explicitly declared deflection sensitivity or an accepted equivalent scientific contract", "003A_dependency":"003A quarantine remains unresolved-only evidence"},
    ]
    fallback_rows = [
        {"condition":"source hash missing/mismatch", "action":"stop before slice", "status":"fail_closed", "rationale":"cannot claim source identity"},
        {"condition":"source type/identity absent or conflict", "action":"stop before route dispatch", "status":"fail_closed", "rationale":"route eligibility is source-dependent"},
        {"condition":"paired_likely requested as confirmed", "action":"downgrade to sensitivity or stop", "status":"fail_closed", "rationale":"avoid false source-accuracy claim"},
        {"condition":"STL-only requested for STEP comparison", "action":"stop; use STL-only validation lane", "status":"fail_closed", "rationale":"no original STEP reference"},
        {"condition":"T17 orientation not crosswalked", "action":"stop", "status":"fail_closed", "rationale":"orientation can change slice result"},
        {"condition":"F1 z400 warning reaches production flag", "action":"stop production release; preserve development artifact only", "status":"fail_closed", "rationale":"attribution unresolved"},
        {"condition":"route B cited as independent imported STL", "action":"stop report/claim", "status":"fail_closed", "rationale":"B is tessellation of the same STEP"},
        {"condition":"mesh repair/hole fill/proxy STEP silently requested", "action":"stop and require a new strict contract", "status":"fail_closed", "rationale":"would alter source/route meaning"},
    ]
    judgments = [
        {"judgment_id":"R09-BB-1318", "blackbox":"003A quarantine and F1 z400 attribution", "status":"unresolved", "basis":"003A produced no official result because both exact-A attempts exceeded resources; ROUTE-VALID-003 remains QA-passed", "next_evidence":"STRICT-F1-001 exact-A long run and explicitly declared deflection sweep", "action":"do not use 003A as NB development prerequisite"},
        {"judgment_id":"R09-BB-1319", "blackbox":"versioned NB integration versus production qualification", "status":"confirmed", "basis":"001/002 selected-slice confirmed-pair evidence plus 003 F1 bounded warning support a technical route controller but not descriptor production parity", "next_evidence":"separate NB-INTEGRATE-001 implementation and later science qualification", "action":"conditional development integration; production remains closed"},
        {"judgment_id":"R09-BB-1320", "blackbox":"imported-STL Route C source policy", "status":"likely", "basis":"C1/B1/L7 exact A-C selected-slice observations on confirmed pairs; F1 not attributable to STL", "next_evidence":"additional approved positions or source-local full-chain qualification", "action":"allow only hash-bound paired-confirmed development route"},
    ]
    prefix = f"{RUN_ID}_"
    outputs = {
        "source_policy": TABLES / f"{prefix}source_type_route_policy.csv",
        "evidence": TABLES / f"{prefix}family_model_evidence_matrix.csv",
        "gate": TABLES / f"{prefix}nb_integration_gate.csv",
        "fallback": TABLES / f"{prefix}fail_closed_fallback.csv",
        "judgments": TABLES / f"{prefix}policy_judgment_register.csv",
    }
    write_csv(outputs["source_policy"], source_rows)
    write_csv(outputs["evidence"], family_rows)
    write_csv(outputs["gate"], gate_rows)
    write_csv(outputs["fallback"], fallback_rows)
    write_csv(outputs["judgments"], judgments)

    contract = {
        "work_id": "ROUTE-VALID-004_ROUTE_POLICY_DECISION_AND_NB_INTEGRATION_GATE_NO_Y",
        "run_id": RUN_ID,
        "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "runtime": "policy-only/no geometry or descriptor calculation",
        "predecessors": inputs,
        "predecessor_requirements": "ROUTE-VALID-001..003 independent QA passed; 003A has quarantine-only status",
        "prohibitions": ["new slicing", "mesh or source edit", "descriptor calculation", "Excel or y access", "feature selection", "model fit", "NB-ORIG/NB-CURRENT/LEGACY-PY edit"],
        "decisions": {"versioned_development_integration": "conditional_yes", "scientific_production_qualification": "no", "route_valid_003a_as_prerequisite": "no"},
        "strict_backlog": "STRICT-F1-001_EXACT_A_LONG_RUN_AND_DECLARED_DEFLECTION_SENSITIVITY_NO_Y",
        "outputs": {key: str(value) for key, value in outputs.items()},
    }
    write_text(RESULT / "POLICY_CONTRACT.json", json.dumps(contract, ensure_ascii=False, indent=2))

    report = f'''# ROUTE-VALID-004 — Route policy decision and NB integration gate (no-y)

- Work / run: `ROUTE-VALID-004_ROUTE_POLICY_DECISION_AND_NB_INTEGRATION_GATE_NO_Y` / `{RUN_ID}`
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

The route policy is machine-readable in [source policy](../../../reports/tables/{prefix}source_type_route_policy.csv). The key rule is: route eligibility is a property of the source identity and evidence level, not a convenience switch.

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

The [fallback table](../../../reports/tables/{prefix}fail_closed_fallback.csv) enumerates required hard stops. The controller must stop rather than choose a permissive route when source identity, hash, transform, orientation or required warning status is missing. A–B must never be converted into an independent imported-STL claim.

## Required next action

1. `NB-INTEGRATE-001_IMPORT_ROUTE_CONTROLLER_VERSIONED_DEVELOPMENT_NO_Y`: contract-build only, then test the controller against synthetic/fixture eligibility cases. No NB-CURRENT replacement.
2. Keep `STRICT-F1-001` in the STRICT queue for future resource availability.
3. Keep STL-only models and source-likely pairs out of production qualification until their separate contracts are completed.

## Status labels

- **confirmed:** the policy boundary itself; predecessor 001–003 QA status; source eligibility categories; 003A quarantine-only status.
- **likely:** selected-slice cross-family support for the paired-confirmed imported-STL development route.
- **unresolved:** F1 z400 attribution, full descriptor/full-Z801 behavior, STL-only route qualification, formula parity.
- **rejected:** treating 003A absence as a failed 003 result; treating A-B as independent STL validation; production promotion from selected slices.
'''
    write_text(RESULT / "REPORT.md", report)
    manifest_rows = []
    for path in [RESULT / "POLICY_CONTRACT.json", RESULT / "REPORT.md", *outputs.values()]:
        manifest_rows.append({"path": str(path.relative_to(ROOT)), "sha256": sha256(path), "bytes": path.stat().st_size, "role": "policy_output"})
    write_csv(RESULT / "OUTPUT_MANIFEST.csv", manifest_rows)
    packet = f'''# ROUTE-VALID-004 merge packet

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
'''
    write_text(RESULT / "MERGE_PACKET.md", packet)


if __name__ == "__main__":
    main()
