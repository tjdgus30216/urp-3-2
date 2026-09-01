# Context and decision lineage
## Doctrine
- **Raw conversation/evidence** is lossless source when independently available, read-only.
- **Context lineage** preserves problem framing, corrections, alternatives, and rationale.
- **Canonical project state** is `PROJECT_SCHEMA.json`, backed by files/manifest/QA under the stated evidence hierarchy.
- **Active task prompt** is an instruction, not a substitute for any preceding layer.

## Availability boundary
The side session `019fb5c1-1a52-7323-9803-3ba7fd4b6a21` has no independently located raw JSONL in this cutoff. The following entries are faithful decision-lineage reconstruction, not verbatim transcript and not scientific evidence.

## Registered decisions
### CTX-HO-001
- **Problem**: Research-lab final day requires closing and handing off while C1 calculation remains active.
- **Final decision**: Freeze v1.0 as-of-cutoff with C1 registered as running and owned by the research control tower.
- **Rationale**: A running state is complete state information, not a documentation gap.
- **Impact**: Read-only C1 registration; no stop/rerun/QA/merge by handoff session.
- **Source availability**: `ephemeral_side_session_no_independent_rollout`; transcript path: `null`.
### CTX-HO-002
- **Problem**: Need a delivery form that lets a new reader understand and reproduce the project.
- **Final decision**: Email is entry; new Notion is human map; clean ZIP is runnable evidence; old page receives outdated pointer.
- **Rationale**: Different media have different authority roles.
- **Impact**: This cutoff produces portable HTML/MD/Excel/schema/evidence packet; it does not edit Notion.
- **Source availability**: `ephemeral_side_session_no_independent_rollout`; transcript path: `null`.
### CTX-HO-003
- **Problem**: Parallel tracks have different last-completed locations, so one overall 'complete' label misleads.
- **Final decision**: Map work packages on Level 1 pipeline and Level 2 tracks with independent status axes.
- **Rationale**: The next person must see where each branch stopped.
- **Impact**: WORK_PACKAGE_LEDGER separates execution, QA, scientific, NB integration, regression, and release.
- **Source availability**: `ephemeral_side_session_no_independent_rollout`; transcript path: `null`.
### CTX-HO-004
- **Problem**: Factory creation, calculation, QA, NB integration, and release need separate records for research literacy.
- **Final decision**: Use S0 problem through S9 release lifecycle alongside independent status axes.
- **Rationale**: Makes gaps visible to a first-time reader.
- **Impact**: Project map and workbook include lifecycle language and claim boundary.
- **Source availability**: `ephemeral_side_session_no_independent_rollout`; transcript path: `null`.
### CTX-HO-005
- **Problem**: The cutoff must be accurate enough to resume safely despite many old documents and fast-moving runs.
- **Final decision**: Actual file/SHA → manifest → QA → report → merge → logs → pointers is the evidence hierarchy.
- **Rationale**: Source provenance must outrank narrative convenience.
- **Impact**: Evidence Index and discrepancy audit preserve scope limits.
- **Source availability**: `ephemeral_side_session_no_independent_rollout`; transcript path: `null`.
### CTX-HO-006
- **Problem**: Need to distinguish the roles of HQ notebook, modules, data, geometry, ledgers, and evidence.
- **Final decision**: HQ is execution anchor; modules are engines; JSON/CSV are machine state; Excel/HTML/MD are views; QA/manifest are claims evidence.
- **Rationale**: Role separation improves reuse and traceability.
- **Impact**: Alias/path index and notebook/module inventory are generated from actual sources.
- **Source availability**: `ephemeral_side_session_no_independent_rollout`; transcript path: `null`.
### CTX-HO-007
- **Problem**: HQ should anchor project literacy without duplicating all history into notebook prose.
- **Final decision**: HQ anchors execution; PROJECT_SCHEMA is state authority; multiple human views are generated from schema.
- **Rationale**: One source of status truth allows reverse tracing.
- **Impact**: HTML, MD, SVG, and workbook use the same cutoff schema.
- **Source availability**: `ephemeral_side_session_no_independent_rollout`; transcript path: `null`.
### CTX-HO-008
- **Problem**: Narrative summaries alone may be wrong or stale.
- **Final decision**: Direct source/file audit with SHA is mandatory for current facts.
- **Rationale**: Project state is an evidence problem, not a writing problem.
- **Impact**: Schema includes direct notebook cell and Python AST audits; evidence hashes are indexed.
- **Source availability**: `ephemeral_side_session_no_independent_rollout`; transcript path: `null`.
### CTX-HO-009
- **Problem**: C1 running status could tempt delaying the final handoff or calling it draft.
- **Final decision**: Publish immutable v1.0, then create a v1.1 cutoff after C1 owner completion/QA.
- **Rationale**: Versioned cutoff keeps historic claims reproducible.
- **Impact**: C1 is registered running; no v1.0 overwrite after completion.
- **Source availability**: `ephemeral_side_session_no_independent_rollout`; transcript path: `null`.
### CTX-HO-010
- **Problem**: Conversation carries human reasoning, corrections, and rejected alternatives that a task prompt can lose.
- **Final decision**: Store decision lineage separately; link raw transcript if available; never substitute it for scientific evidence.
- **Rationale**: Future AI/human needs both intent and file-backed facts.
- **Impact**: Context lineage register and HTML view state transcript availability explicitly.
- **Source availability**: `ephemeral_side_session_no_independent_rollout`; transcript path: `null`.
