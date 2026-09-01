# CURRENT PACKAGE OVERRIDE — HANDOFF-CUTOFF-20260802-002 / PROJECT_SCHEMA v1.3 / v1.4-r2

This banner is the authoritative current-state entry for this packaged snapshot.

- Current active run: **none**.
- `STRICT-STEP-026` C1: **completed_with_evidence** — 801/801 slices, 800/800 overlays, 40 scalars, independent QA 9/9.
- Training: **closed_for_submission_as_blocked_with_evidence**; numerical parity was not established because the native source runtime crashed.
- AI Lattice: **technical_pilot_completed_with_scientific_caution**; no feature/model promotion.
- B/C/L + Voronoi: **technical_pilot_completed_with_scientific_caution** — 167 exact joins, 10,688 grouped OOF predictions, both QA-v2 10/10 PASS_WITH_WARNINGS; no promotion.
- All earlier `running`, `active worker`, `wait for C1`, v1.0 or pre-finalization wording below is **historical/superseded context only** and must not be used as current state.
- Current machine-readable authority: `../01_PROJECT_MAP_AND_LEDGER/PROJECT_SCHEMA.json`.
- Current human authority: `../01_PROJECT_MAP_AND_LEDGER/URP4_1_MASTER_HANDOFF_LEDGER.xlsx`.
- Sealed archive authority: the adjacent external v1.4-r2 delivery index, package QA and `.sha256` receipt produced after final sealing.

---

# HISTORICAL SOURCE POINTER (read-only snapshot; superseded for current-state decisions)

# AI_START_HERE

Purpose: minimal bootstrap document for a new Codex session.

Read this first when starting work on URP4-1. Do not read every project document by default. Choose only the documents needed for the requested task.

## SESSION OWNERSHIP GATE — shared CWD, 2026-07-31

Two control-tower sessions share this same working directory. Their write scopes are disjoint.

| control tower | thread_id | write scope | read-only / prohibited scope |
| --- | --- | --- | --- |
| Research control tower | `019f403b-4486-7ee0-b1a0-e0754e134c1b` | `experiments/lab_001_xy_connection_20260626/`, official research logs and accepted research artifacts | must not modify `experiments/demo_labs/DEMO-OPT-001_STRUCTURAL_TARGET_LATTICE_20260730/` or `C:\Users\chuck\URP4F\` |
| UI control tower | `019fb1f6-6913-7020-92cb-852d57d4f8d1` | `experiments/demo_labs/DEMO-OPT-001_STRUCTURAL_TARGET_LATTICE_20260730/`, `C:\Users\chuck\URP4F\` | `experiments/lab_001_xy_connection_20260626/`, STRICT workers/results, NB-CURRENT, NB-ORIG, LEGACY-PY, original Excel/geometry are read-only |

- A generic request such as `다음 작업` must be resolved inside the current session's write scope. Do not select the other tower's roadmap merely because its files are newer.
- The UI tower may consume an accepted research manifest/report as read-only display data. It must not start, stop, resume, QA, merge, or log a `STRICT-*` run.
- The research tower owns the active `STRICT-STEP-026` C1 worker and the post-completion QA script. The UI tower owns the transparent factory/engineer-console work.
- If a requested task crosses these scopes, stop and hand it to the owning tower before changing files.

## CURRENT OVERRIDE — URP4-1 HQ v0.1 deliverable integrated and audited, 2026-07-28

- Deliverable: `URP4-1_DELIVERABLE/URP4_1_HQ.ipynb`; only Cell 1 `MASTER CONTROLLER` is user-editable.
- Explicit routes: generated STL → native; imported STL → oriented non-zero winding; original STP → strict/reference preflight. Silent STL→STEP fallback is rejected.
- KMK312 QA: fast smoke/guard `9/9`, immutable sources `14/14`, integration gates `6/6` PASS.
- Full evidence: imported L28 VF30 and a controlled generated fixture each complete P1000/Z801, 801 slices, 800 overlays, 9 scalar rows, zero PNG readback mismatch and zero retained PNG under streaming. L28 repeats exactly.
- Training/feature selection is interface-only and fail-closed OFF. No y, x-y, fitting, prediction or inverse-design execution occurred.
- Scientific boundary: imported route remains likely/screening on L28 and sampled B/C/L/T; F1, all58, direct STP descriptor, Type B input and production TPMS/Voxel policy remain unresolved.
- Next scientific task remains `IMSTL-007_F1_SELECTED_SLICE_RESOLUTION_AND_PIXEL_PHASE_DIAGNOSIS_NO_Y`.
- Read: `experiments/lab_001_xy_connection_20260626/results/URP4-1_HQ_FINALIZATION_20260728/URP4-1_HQ_FINALIZATION_REPORT_20260728.md`.
- Indices: `RUN-337 / DEC-350 / CHG-335 / LAB-CHG-304 / R09-BB-1303`.

## CURRENT OVERRIDE — STRICT-GEOM-020 proves all 192 nonincident curves have unique micro-chain paths, 2026-07-27

- Settings/run: `IDX-URP4-1-GEOM-LINEAGE / CFG-SG020-L28VF45-C-S325-FULLCOMP-PATHSPECTRUM r1`; `STRICT-GEOM-020 / RUN-327`.
- Population/QA: exact C0325 edges `2,604`, full components `36`, target observations `432`, target branches `192`; independent QA `8/8 PASS`.
- Connectivity: same-component nonlocal path `432/432`; disconnected/bridge-only/near-miss `0`. Every path is unique with one first incident edge; hop distribution is `272 × 1-hop + 160 × 2-hop`.
- Spectrum: exact path `0.0115968–0.0134964 mm`; Euclidean clearance `9.9067e-6–5.0020e-5 mm`; topological/Euclidean ratio `231.9–1176.0`.
- **confirmed:** all 192 branches are exact topological micro-chains, not disconnected artifacts. **unresolved:** combined 256-branch graph closure/raster eligibility. **rejected:** post-hoc Euclidean threshold selection.
- Next: `STRICT-GEOM-021_C_UNIQUE_MICROCHAIN_CONTINUATION_GRAPH_CLOSURE_AUDIT_NO_Y`.
- Read: `experiments/lab_001_xy_connection_20260626/results/SG020_L28/STRICT_GEOM_020_C_NONINCIDENT_CURVE_COMPONENT_AND_PATH_LENGTH_SPECTRUM_REPORT_20260727.md`.
- Indices: `RUN-327 / DEC-340 / CHG-325 / LAB-CHG-294 / R09-BB-1293`.

## CURRENT OVERRIDE — STRICT-GEOM-019 identifies every exact curve but leaves 192 nonincident branches, 2026-07-27

- Settings/run: `IDX-URP4-1-GEOM-LINEAGE / CFG-SG019-L28VF45-C-S325-CURVECHAIN-R2R5 r1`; `STRICT-GEOM-019 / RUN-326`.
- Population/QA: exact C0325 edges `2,604`, transitions `536`, branch tracks `256`; independent QA `8/8 PASS`.
- Curve identity: unique nearest exact section curve `536/536`; stable identity across radius `256/256`; nearest-face overlap `536/536`.
- Continuation: stable unique native-ray continuation `64/256`; remaining `192` branches have no exact path within both 0.002 and 0.005 mm windows.
- **confirmed:** exact curve identity resolves all 64 SG018 face-ambiguous branches. **unresolved:** full-component/path-length identity for 192 nonincident curves. **rejected:** extra angular sweep and local graph promotion.
- Next: `STRICT-GEOM-020_C_NONINCIDENT_CURVE_COMPONENT_AND_PATH_LENGTH_SPECTRUM_AUDIT_NO_Y`.
- Read: `experiments/lab_001_xy_connection_20260626/results/SG019_L28/STRICT_GEOM_019_C_EXACT_SECTION_CURVE_FACE_BOUNDARY_CONTINUATION_REPORT_20260727.md`.
- Indices: `RUN-326 / DEC-339 / CHG-324 / LAB-CHG-293 / R09-BB-1292`.

## CURRENT OVERRIDE — STRICT-GEOM-018 rejects unique native-ray continuation, 2026-07-27

- Settings/run: `IDX-URP4-1-GEOM-LINEAGE / CFG-SG018-L28VF45-C-S325-POLAR20-FACETRACK r1`; `STRICT-GEOM-018 / RUN-325`.
- Population/QA: SG017 problem populations `560 = 256 mixed + 96 finite boundary + 208 micro boundary`; refined transitions `536`, trace rows `4,904`, branch tracks `256`; independent QA `8/8 PASS`.
- Face lineage: all `536/536` transitions have trimmed original-STP face lineage.
- Continuation result: unique incident-ray face match `0`; no match `192`, ambiguous match `64` (`55` two-ray and `9` four-ray matches).
- **confirmed:** complete polar transition/face lineage. **rejected:** exact-face or exact-solid identity as a unique native-ray continuation rule. **unresolved:** exact section-curve half-edge continuation through coincident face partitions.
- Next: `STRICT-GEOM-019_C_EXACT_SECTION_CURVE_FACE_BOUNDARY_CONTINUATION_AUDIT_NO_Y`.
- Read: `experiments/lab_001_xy_connection_20260626/results/SG018_L28/STRICT_GEOM_018_C_POLAR_TRANSITION_AND_FACE_BRANCH_REPORT_20260727.md`.
- Indices: `RUN-325 / DEC-338 / CHG-323 / LAB-CHG-292 / R09-BB-1291`.

## CURRENT OVERRIDE — STRICT-GEOM-017 proves boundary branches move inside angular sectors, 2026-07-27

- Settings/run: `IDX-URP4-1-GEOM-LINEAGE / CFG-SG017-L28VF45-C-S325-N120-A9-R7-FACEPART r1`; `STRICT-GEOM-017 / RUN-324`.
- Population/QA: nodes `120`, angular samples `30,240`, boundary samples `4,082`, trimmed-face hits `6,314`; independent QA `8/8 PASS`.
- Exact parent replay: SG016 midpoint parity `3,360/3,360`. All boundary samples have source-face lineage; `2,232` hit two coincident faces.
- Multi-angle result: stable internal/external rays `176/32`, angular-unresolved/radius-unstable `128/144`; only `16/96` target nodes fully resolve.
- All 48 SG016 clean-control external rays become radius-unstable (`internal ×3 -> external ×4`). This is a scientific negative result, not an execution mismatch.
- **confirmed:** polar branch motion/source partitions. **unresolved:** 80 nodes. **rejected:** midpoint-clean generalization, fixed native-ray continuation and raster action.
- Next: `STRICT-GEOM-018_C_NODE_POLAR_BOUNDARY_TRANSITION_TRACKING_AND_FACE_BRANCH_CONTINUATION_AUDIT_NO_Y`.
- Read: `experiments/lab_001_xy_connection_20260626/results/SG017_L28/STRICT_GEOM_017_C_NODE_SECTOR_MULTIANGLE_AND_FACE_PARTITION_REPORT_20260727.md`.
- Indices: `RUN-324 / DEC-337 / CHG-322 / LAB-CHG-291 / R09-BB-1290`.

## CURRENT OVERRIDE — STRICT-GEOM-016 localizes the remaining C failure to angular boundary sectors, 2026-07-27

- Settings/run: `IDX-URP4-1-GEOM-LINEAGE / CFG-SG016-L28VF45-C-S325-ODD120-SECTOR-SEGMENT r1`; `STRICT-GEOM-016 / RUN-323`.
- Population/QA: odd nodes `120`, incident rays `480`, unique incident edges `360`, sector states `3,360`, fraction samples `7,560`; independent QA `8/8 PASS`.
- Primary ray roles: internal `128`, external `64`, sector-unresolved `224`, primary-radius-unstable `64`. Only `24/120` nodes have a clean two-external/two-internal pattern.
- The unresolved states are exact OCP `ON` boundary hits. The provisional graph retains `108` odd vertices, so it is diagnostic and noncanonical.
- **confirmed:** complete reproducible negative gate. **unresolved:** 96 angular node sectors. **rejected:** radius-only sweep, provisional graph promotion and raster action.
- Next: `STRICT-GEOM-017_C_NODE_SECTOR_MULTIANGLE_INTERIOR_SAMPLING_AND_COINCIDENT_FACE_PARTITION_AUDIT_NO_Y`.
- Read: `experiments/lab_001_xy_connection_20260626/results/SG016_L28/STRICT_GEOM_016_C_ODD_NODE_ENDPOINT_REFINEMENT_AND_EXACT_SEGMENT_LINEAGE_REPORT_20260727.md`.
- Indices: `RUN-323 / DEC-336 / CHG-321 / LAB-CHG-290 / R09-BB-1289`.

## CURRENT OVERRIDE — STRICT-GEOM-015 proves 40 C edges change material role along their length, 2026-07-27

- Settings/run: `IDX-URP4-1-GEOM-LINEAGE / CFG-SG015-L28VF45-C-U646-P9-LOCAL-CLEARANCE r1`; `STRICT-GEOM-015 / RUN-322`.
- Population/QA: unresolved edges `646`, samples `5,814`, state queries `206,984`, checkpoint shards `27`; independent QA `8/8 PASS`.
- Roles: uniform internal `606`, mixed along edge `40`. Every mixed edge is on slice 0325 and its external endpoint is one of the SG014 odd vertices.
- Slice-0325 odd nodes partition into three disjoint 40-node cohorts: mixed-edge endpoint, uniform-internal endpoint and no unresolved-edge incidence.
- **confirmed:** midpoint-only labeling fails for 40 edges. **unresolved:** exact segment continuation and node-local sectors. **rejected:** whole-edge promotion or raster action.
- Next: `STRICT-GEOM-016_C_ODD_NODE_ENDPOINT_REFINEMENT_AND_EXACT_SEGMENT_LINEAGE_AUDIT_NO_Y`.
- Read: `experiments/lab_001_xy_connection_20260626/results/SG015_L28/STRICT_GEOM_015_C_ALONG_EDGE_MULTIPOINT_AND_LOCAL_CLEARANCE_REPORT_20260727.md`.
- Indices: `RUN-322 / DEC-335 / CHG-320 / LAB-CHG-289 / R09-BB-1288`.

## CURRENT OVERRIDE — STRICT-GEOM-014 completes all-edge C classification but exposes a local-scale boundary problem, 2026-07-27

- Settings/run: `IDX-URP4-1-GEOM-LINEAGE / CFG-SG014-L28VF45-C-X2-FULL-UNION-BOUNDARY r1`; `STRICT-GEOM-014 / RUN-321`.
- Population/QA: C edges `5,208`, offset states `41,664`, SG012 parity `512/512`, independent QA `8/8 PASS`.
- Robust result: internal seams `4,104`, external boundaries `458`, offset instability `226`, sensitivity mismatch `420`.
- Slice 0174 robust graph closes with odd `0`; slice 0325 retains odd `120`. No tested global epsilon closes both slices.
- **confirmed:** full calculation and four deterministic scale-transition patterns. **unresolved:** along-edge role constancy and local adaptive clearance. **rejected:** fixed global epsilon and raster action.
- Next: `STRICT-GEOM-015_C_ALONG_EDGE_MULTIPOINT_AND_LOCAL_CLEARANCE_AUDIT_NO_Y` over the `646` unresolved edges.
- Read: `experiments/lab_001_xy_connection_20260626/results/SG014_L28/STRICT_GEOM_014_C_FULL_SECTION_EDGE_OWNER_UNION_BOUNDARY_CLASSIFICATION_REPORT_20260727.md`.
- Indices: `RUN-321 / DEC-334 / CHG-319 / LAB-CHG-288 / R09-BB-1287`.

## CURRENT OVERRIDE — STRICT-GEOM-013 proves the confirmed C seam subset is incomplete, 2026-07-26

- Settings/run: `IDX-URP4-1-GEOM-LINEAGE / CFG-SG013-L28VF45-C-X2-SEAM-GRAPH r1`; `STRICT-GEOM-013 / RUN-320`.
- Scope/QA: C source edges `5,208`, excluded SG012 seams `512`; independent QA `8/8 PASS`.
- Per slice, exclusion changes odd vertices `128 -> 256` and connected components `36 -> 52`; the registered subset does not form the complete external-boundary rule.
- **confirmed:** negative subset-sufficiency result. **retained:** SG012's local `512/512 internal_union_seam` labels. **unresolved:** full C edge classification and B volume.
- No raster, descriptor, y, route winner or protected-source change.
- Next: `STRICT-GEOM-014_C_FULL_SECTION_EDGE_OWNER_UNION_BOUNDARY_CLASSIFICATION_NO_Y` over all `5,208` C edges.
- Read: `experiments/lab_001_xy_connection_20260626/results/SG013_L28/STRICT_GEOM_013_C_SOLID_UNION_SEAM_EXCLUSION_GRAPH_CLOSURE_REPORT_20260726.md`.
- Indices: `RUN-320 / DEC-333 / CHG-318 / LAB-CHG-287 / R09-BB-1286`.

## CURRENT OVERRIDE — STRICT-GEOM-012 confirms C internal union seams; B proxy volume is incomplete, 2026-07-26

- Settings/run: `IDX-URP4-1-GEOM-LINEAGE / CFG-SG012-L28VF45-BC-X2-COINCIDENT-OWNER-PARITY r1`; `STRICT-GEOM-012 / RUN-319`.
- Population/QA: affected edges `1,168`, face contributors `1,248`, offset states `9,344`; independent QA `8/8 PASS`.
- C: all `512/512` affected residual/continuation edges have stable union material on both sides across the registered offsets and are `internal_union_seam`. Continuation face pairs are different solids with opposing normals `256/256`.
- B: all `656/656` affected edges are `volume_incomplete_unresolved`; locally relevant open/invalid proxy shells prevent a complete material verdict.
- **confirmed:** bounded C solid-union seam rule. **rejected:** B proxy volume verdict and immediate raster/descriptor action.
- No raster, descriptor, y or protected-source change. No route winner.
- Next: `STRICT-GEOM-013_C_SOLID_UNION_SEAM_EXCLUSION_GRAPH_CLOSURE_AUDIT_NO_Y`.
- Read: `experiments/lab_001_xy_connection_20260626/results/SG012_L28/STRICT_GEOM_012_COINCIDENT_FACEWISE_SECTION_MULTIMAP_AND_OWNER_PARITY_REPORT_20260726.md`.
- Indices: `RUN-319 / DEC-332 / CHG-317 / LAB-CHG-286 / R09-BB-1285`.

## CURRENT OVERRIDE — STRICT-GEOM-011 proves compound ancestor reattribution, not missing geometry, 2026-07-26

- Settings/run: `IDX-URP4-1-GEOM-LINEAGE / CFG-SG011-L28VF45-BC-X2-FACE-COMPOUND-REPLAY r1`; `STRICT-GEOM-011 / RUN-318`.
- Population/QA: `624` SG010 neighbor relations, `496` unique source faces and `16` separate B325 free-edge cases; independent QA `8/8 PASS`.
- Every tested face creates a positive-length individual section through the exact residual node. The compound section contains the same local tangent geometry for `624/624`, but assigns it to a different coincident source face.
- **confirmed:** `present_geometry_reattributed` `624/624`. **rejected:** compound suppression, tangent/noise deletion and single-ancestor identity as a complete owner rule.
- The separate `16` B325 cases are `free_or_single_face_edge`; do not mix them with reattribution.
- No raster, descriptor, y or protected-source change. No route winner.
- Next: `STRICT-GEOM-012_COINCIDENT_FACEWISE_SECTION_MULTIMAP_AND_OWNER_PARITY_AUDIT_NO_Y`.
- Read: `experiments/lab_001_xy_connection_20260626/results/SG011_L28/STRICT_GEOM_011_LOCAL_NEIGHBOR_FACE_SECTION_CONTINUATION_AND_COMPOUND_REPLAY_REPORT_20260726.md`.
- Indices: `RUN-318 / DEC-331 / CHG-316 / LAB-CHG-285 / R09-BB-1284`.

## CURRENT OVERRIDE — STRICT-GEOM-010 residual half-edges are transverse; deletion/raster remains blocked, 2026-07-26

- Settings/run: `IDX-URP4-1-GEOM-LINEAGE / CFG-SG010-L28VF45-BC-X2-RESIDUAL-TRANSVERSALITY r1`; `STRICT-GEOM-010 / RUN-317`.
- Population/QA: deterministic residual half-edges `640`, boundary-edge records `640`, neighbor-face relations `624`; independent QA `8/8 PASS`.
- All residual source-face normals are transverse to the slice plane; all residuals lie on a source boundary edge whose tangent crosses the plane. No near-parallel/tangent case was found.
- `624` residuals have an absent same-owner planar neighbor whose whole-face z-range crosses the plane; `16` B0325 cases have no missing same-owner neighbor under the registered rule.
- **rejected:** deleting residuals as grazing/noise or by short length. **unresolved:** local neighbor-face section continuation versus compound-section suppression/reattribution.
- No raster, descriptor, y or protected-source change. No route winner.
- Next: `STRICT-GEOM-011_LOCAL_NEIGHBOR_FACE_SECTION_CONTINUATION_AND_COMPOUND_REPLAY_NO_Y`.
- Read: `experiments/lab_001_xy_connection_20260626/results/SG010_L28/STRICT_GEOM_010_RESIDUAL_HALFEDGE_TRANSVERSALITY_AND_SOURCE_CONTACT_REPORT_20260726.md`.
- Indices: `RUN-317 / DEC-330 / CHG-315 / LAB-CHG-284 / R09-BB-1283`.

## CURRENT OVERRIDE — STRICT-GEOM-009 resolved most junctions by source ancestry; residual half-edges remain, 2026-07-26

- Settings/run: `IDX-URP4-1-GEOM-LINEAGE / CFG-SG009-L28VF45-BC-X3-ANCESTOR-FACE r1`; `STRICT-GEOM-009 / RUN-316`.
- Coverage/QA: source/cutter ancestry and source-face mapping `36,304/36,304`; `8,624` junctions and `52,000` candidate pairs; independent QA `8/8 PASS`.
- Source owners: B has `455` shells and no solids; C has `1,521` shells/solids. Every section edge maps to the appropriate owner population.
- Ancestry creates no multiple matching. Slice `0366` is unique in both routes; C's degree-four junctions at `0174/0325` are all unique.
- Residual: C has `128` degree-five no-complete-matching junctions per slice at `0174/0325`; B has `128` degree-three plus `32` degree-four incomplete junctions per slice.
- **rejected:** ancestry alone as a complete material-boundary solution and deleting unmatched edges as noise. **unresolved:** tangent/grazing versus true material/contact branch.
- No raster, descriptor, y or protected-source change. No B/C route winner.
- Next: `STRICT-GEOM-010_RESIDUAL_HALFEDGE_TRANSVERSALITY_AND_SOURCE_CONTACT_AUDIT_NO_Y`.
- Read: `experiments/lab_001_xy_connection_20260626/results/SG009_L28/STRICT_GEOM_009_SECTION_EDGE_ANCESTOR_FACE_AND_MATERIAL_BOUNDARY_LINEAGE_REPORT_20260726.md`.
- Indices: `RUN-316 / DEC-329 / CHG-314 / LAB-CHG-283 / R09-BB-1282`.

## CURRENT OVERRIDE — STRICT-GEOM-008 confirmed native junction topology; simple cycle decomposition rejected, 2026-07-26

- Settings/run: `IDX-URP4-1-GEOM-TOPOLOGY / CFG-SG008-L28VF45-BC-X3-JUNCTION-CYCLE r1`; `STRICT-GEOM-008 / RUN-315`.
- Result: B/C × slices `0174/0325/0366` were audited through OCP topological vertices, BRep vertex coordinates and curve-endpoint coordinates. Independent QA is `8/8 PASS`; no raster or descriptor was created.
- At primary `1e-6 mm`, all three graph representations agree. Maximum curve↔BRep-vertex mismatch is `6.61e-12 mm`, and duplicate geometric edge-signature groups are `0`.
- `0174/0325` have `128` odd-degree vertices in both routes, so a complete edge-only cycle cover is impossible without population change. `0366` is all-even but has `400` degree-four junctions, so cycle pairing is non-unique.
- Across `36` tolerance observations (`1e-9...1e-4 mm`), unique simple-cycle populations are `0/36`. **rejected:** simple quantization, duplicate signatures, tolerance-only retry and arbitrary Euler/angle pairing as an accepted material rule.
- **unresolved:** source face/solid/shell ownership and physical material-boundary pairing. B remains `STL2STP-PROXY`; C remains `ORIGINAL-STP-BREP`; no route winner exists.
- Next: `STRICT-GEOM-009_SECTION_EDGE_ANCESTOR_FACE_AND_MATERIAL_BOUNDARY_LINEAGE_AUDIT_NO_Y` before any raster retry.
- Read: `experiments/lab_001_xy_connection_20260626/results/SG008_L28/STRICT_GEOM_008_NATIVE_SECTION_JUNCTION_CYCLE_AUDIT_REPORT_20260726.md`.
- Indices: `RUN-315 / DEC-328 / CHG-313 / LAB-CHG-282 / R09-BB-1281`.

## CURRENT OVERRIDE — STRICT-GEOM-007 Phase B quarantined all six L28 shards, 2026-07-26

- Settings/run: `IDX-URP4-1-GEOM-RASTER / CFG-SG007-L28VF45-BC-P1000-X3-FACE-IN r1`; `STRICT-GEOM-007 Phase B / RUN-314`.
- Result: B/C × slices `0174/0325/0366` reached `6/6` terminal states; `0` passed masks and `6` `quarantined_uneligible_wire`. Independent QA is `8/8 PASS`; stderr is empty.
- Full native-edge accounting and OCP closure/connectivity checks pass. The blocking condition is coordinate endpoint-degree: affected wire fractions are B `64.45/65.03/26.47%`, C `85.05/80.49/29.55%`.
- **confirmed/rejected:** the SG006 all-degree-two simple-loop eligibility rule does not directly generalize to complex imported L28 section networks.
- **not inferred:** B/C physical invalidity, source truth, proxy adequacy, route winner, material mask or descriptor validity.
- No partial clean-wire mask was allowed because it would silently discard 26–85% of the wire population. No repair, fallback, face mask, descriptor or y artifact exists.
- Next: `STRICT-GEOM-008_NATIVE_SECTION_JUNCTION_AND_CYCLE_DECOMPOSITION_AUDIT_NO_Y`; audit topological versus coordinate incidence and possible no-repair planar cycle decomposition before another raster attempt.
- Read: `experiments/lab_001_xy_connection_20260626/results/SG007_L28/STRICT_GEOM_007_PHASE_B_SELECTED_SLICE_FACE_RASTERIZER_REPORT_20260726.md`.
- Indices: `RUN-314 / DEC-327 / CHG-312 / LAB-CHG-281 / R09-BB-1280`.

## CURRENT OVERRIDE — STRICT-GEOM-007 B/C selected-slice contract passed, 2026-07-26

- Settings: `IDX-URP4-1-GEOM-RASTER / CFG-SG007-L28VF45-BC-P1000-X3-FACE-IN r1`; provisional addendum to Master Ledger `09_FORMULA_CONFIG`, without overwriting the frozen XRV1 config.
- Contract/run: `STRICT-GEOM-007 / RUN-313`; design and independent contract QA only. L28 face-raster execution count remains `0`.
- Frozen scope: L28 UBCCz VF45, B `STL2STP-PROXY` and C `ORIGINAL-STP-BREP`, z-slices `0174/0325/0366`, N40 `40×40 mm`, `1000×1000 px`, primary `TopAbs_IN`; `TopAbs_ON` is diagnostic only.
- Eligibility: full native-edge accounting, zero closure/connectivity diagnostics, zero endpoint-degree anomalies at `1e-6 mm`, successful face build and preserved edge identity. Any failure quarantines the entire shard without repair or fallback.
- QA: `7/7 PASS`; SG006 correction/QA and all raw/processed/NB-CURRENT hashes replay; SG001 remains read-only; `derived_noncanonical` contains no L28 result.
- **confirmed:** the bounded comparison contract is reproducible and execution-safe. **unresolved:** L28 material truth, B/C source fidelity, proxy adequacy, canonical route and descriptor validity.
- Next: execute only `STRICT-GEOM-007_PHASE-B_BC_SELECTED_SLICE_FACE_RASTERIZER_SENSITIVITY_NO_Y` as six resumable noncanonical shards, then independently review before any descriptor action.
- Read: `experiments/lab_001_xy_connection_20260626/results/SG007_L28/STRICT_GEOM_007_BC_SELECTED_SLICE_FACE_RASTERIZER_SENSITIVITY_PREREGISTRATION_20260726.md`.
- Indices: `RUN-313 / DEC-326 / CHG-311 / LAB-CHG-280 / R09-BB-1279`.

## CURRENT OVERRIDE — STRICT-GEOM-006 Phase A face-rasterizer truth gate passed, 2026-07-25

- Contract/run: `STRICT-GEOM-006 / RUN-312`; KMK312 + OCP/OpenCascade. Analytic fixtures only—L28 was never executed and SG001 remains immutable.
- Outcome: closed square, cylinder, annulus and two-island fixtures pass component/hole/area truth at `500/1000/2000/4000 px`. Independent QA is `7/7 PASS`; protected raw STL/STP/NB-CURRENT hashes replay.
- Critical correction: `ShapeAnalysis_Wire.CheckClosed/CheckConnected` alone did not reject a known-open U. The gate now additionally requires zero native curve-endpoint degree anomalies at `1e-6 mm`; U has degree-one endpoints and is blocked **before** `MakeFace`, with zero material at every resolution.
- **confirmed, bounded:** this face-derived rasterizer passes the stated analytic truth and no-heal negative control.
- **unresolved:** L28 physical material semantics, ORIGINAL-STP truth, proxy adequacy, A/B/C route selection and descriptor validity. Fixture success is not a canonical-source verdict.
- Next: design only `STRICT-GEOM-007_BC_SELECTED_SLICE_FACE_RASTERIZER_SENSITIVITY_PREREGISTRATION`; any masks remain isolated/noncanonical and cannot overwrite SG001.
- Read: `experiments/lab_001_xy_connection_20260626/results/SG006_L28/SG006_PHASE_A_ENDPOINT_QUARANTINE_CORRECTION_REPORT_20260725.md` and `.../SG006_PHASE_A_INDEPENDENT_QA_20260725.md`.
- Indices: `RUN-312 / DEC-325 / CHG-310 / LAB-CHG-279 / R09-BB-1278`.

## CURRENT OVERRIDE — STRICT-GEOM-002 conditional pixel semantics gate passed, 2026-07-24

- Contract/run: `STRICT-GEOM-002 / RUN-307`; KMK312 + OCP/OpenCascade; bounded analytic fixtures and selected L28 slice re-rasterization only.
- Closed box/cylinder/annulus pass both A-style triangle and C-style B-rep routes at `500/1000/2000/4000 px`: expected component/hole identities hold and the worst 4000px area error is `0.06585%`.
- An intentionally open U contour still becomes a `400 mm²` filled foreground under the same even/odd rule at every resolution. Therefore foreground pixels have **conditional**, not unconditional, filled-material semantics: source-closure evidence is required first.
- L28 scope: slice `0174`, `0325`, and y-blind normal `0366`; A/B/C, four resolutions, four subpixel phases, 4/8 connectivity and one physical `0.0032 mm²` component filter. 0174/0325 A↔C disagreement persists at 4000px (`0.444565` / `0.099059` P00 IoU); 0366 remains high (`0.976053`). This is stability evidence, not causal attribution.
- Endpoint-degree diagnostics for L28 remain **unresolved** source/raster diagnostics; they cannot prove an open physical solid because triangle/B-rep section segmentation and quantization can create unmatched endpoints.
- QA: `8/8 PASS`; preserved 1000px/P00 IoUs exactly match SG001's retained all-slice data. Raw STL/STP and NB-CURRENT hashes pass unchanged. A MAX_PATH final-report write was recovered from complete stored CSVs by using short derived-output root `results/SG002_L28` only.
- Next: `STRICT-GEOM-003_SECTION_CLOSURE_TOLERANCE_AND_LOOP_AUDIT_NO_Y` — use existing SG001 segment artifacts to audit endpoint clustering/wire closure under a preregistered tolerance ladder before any route, resolution or FAST-path decision.
- Read: `experiments/lab_001_xy_connection_20260626/results/SG002_L28/STRICT_GEOM_002_PIXEL_SEMANTICS_AND_RESOLUTION_REPORT_20260724.md` and `experiments/lab_001_xy_connection_20260626/results/SG002_L28/SG002_INDEPENDENT_QA_20260724.md`.
- Indices: `RUN-307 / DEC-320 / CHG-305 / LAB-CHG-274 / R09-BB-1273`.

## CURRENT OVERRIDE — PRM-075 literature-guided descriptor focus, 2026-07-22

- Professor direction: labeled data are currently insufficient; pause further model-method expansion and focus on additional structure descriptors from papers and credible technical sources.
- Current-bank audit: `XREG-v0.1 431 + T3I 42 + T3O 22`; volume/surface/Euler/inertia and z-profile statistics already exist and must not be repackaged as new features.
- First implementation candidates: directional chord length, true 3D directional `S2`, lineal path, surface-normal fabric tensor and voxel Euler cross-check.
- Second lane: skeleton-graph topology and 3D local thickness/bottleneck; tortuosity/C2 are sensitivity; persistent homology/lacunarity are deferred.
- Modeling status: no new y read, fit, selection or promotion. New compression data remain an immutable future intake lane.
- Next: `PRM-076_L1_DESCRIPTOR_FORMULA_UNIT_SYNTHETIC_TRUTH_PREREGISTRATION`; freeze phase/axis/formula/unit and y-blind gates before code.
- QA: producer `12/12`, independent `18/18`, protected assets `29/29`.
- Read: `experiments/lab_001_xy_connection_20260626/results/R09-20260722-PRM075_LITERATURE_GUIDED_DESCRIPTOR_DISCOVERY_AND_PRIORITY.md`.
- Indices: `PRM-075 / RUN-220 / DEC-252 / CHG-239 / LAB-CHG-211 / R09-BB-909~921`.

## CURRENT OVERRIDE — R09-SLICE-005 LabPC USB factory ready; no cell executed, 2026-07-21

- Contract/run: `PRM-050 / RUN-195`; conditional execution behind a live LabPC doctor.
- Packet: `outputs/URP4-1_R09_SLICE005_LABPC_FACTORY_USB_20260721` (~167 MiB).
- Contents: 8 canonical N40 STL, 8 frozen RUN-139 baseline packets, 32 pending jobs, CINT-03 service, doctor/runner/verifier/collector and CMD 00→04.
- Integrity: immutable `160/160`, sources `8/8`, baselines `8/8`, jobs `32/32`, doctor `15/15`, package QA `24/24`, protected `29/29`.
- Runtime policy: KMK312 3.12.12; >=12 GiB available RAM; >=25 GiB free disk; sequential process isolation; max two immutable attempts; resume skips passed cells.
- Current state: USB not connected, copy pending, actual jobs `0/32`.
- Next: connect USB and copy packet; execute CMD 00→04 on LabPC; return ZIP + manifest for control-tower convergence review.
- Read: `experiments/lab_001_xy_connection_20260626/results/R09-20260721-SLICE-005_LABPC_USB_FACTORY_PREPARATION.md`.
- Indices: `PRM-050 / RUN-195 / DEC-227 / CHG-214 / LAB-CHG-186 / R09-BB-684~692`.

## CURRENT OVERRIDE — R09-SLICE-005 B3 duplicate canary passed; 32-cell execution still locked, 2026-07-21

- Contract/run: `PRM-047 -> PRM-048 -> PRM-049 / RUN-194`; KMK312 on Legion5.
- Accepted evidence: `B3-COARSE-E/F` only. Five retained table hashes and nine scalars are exact; independent 18-cell replay max delta `1.11e-16`.
- Resources: 65.556/65.225 s, max RSS 0.2324 GiB, 17.340 MiB retained each; transient PNG `1601/1601` deleted per attempt.
- Quarantine: A failed JSON bookkeeping after calculation; C failed stale contract guard before output. Scientific use is `none`; B/D never ran.
- QA: execution `16/16`, independent `20/20`, negative `5/5`, control `28/28`, visual `1/1`, protected `29/29`.
- Decision: deterministic/resource canary passed. Pixel/slice convergence is not yet tested and the 32 pending cells remain unauthorized.
- Next: freeze a separate live-hash LabPC execution contract; reuse eight RUN-139 baselines and run only 32 pending cells with atomic resume.
- Read: `experiments/lab_001_xy_connection_20260626/results/R09-20260721-SLICE-005_B3_COARSE_DUPLICATE_CANARY_CONTROL_REVIEW.md`.
- Indices: `PRM-049 / RUN-194 / DEC-226 / CHG-213 / LAB-CHG-185 / R09-BB-675~683`.

## CURRENT OVERRIDE — T3P mesh-native grouped-GM replay failed 0/8 gates, 2026-07-21

- Contract/run: `PRM-042 + PRM-043 / RUN-190`; one unchanged execution completed under KMK312.
- Scope: official GM YPOL-GM-v0.1, exact54, eight T3O mesh-native candidates, 5 outer / 20 inner folds.
- Fits: `586/670`; four outer folds selected `NONE`.
- Failure: `LOFO::L` selected `MN3D::inertia_fraction_mid`, then L RMSE was `931.244581` versus mean-null `114.632446`.
- Pooled result: R² `-21.589162`, RMSE `576.091420`, Spearman `-0.006780`; required gates `0/8`.
- Integrity: independent 586-fit replay matched all 54 predictions within `4.55e-13`; execution/independent/control/visual QA `12/12`, `12/12`, `21/21`, `2/2`; protected `29/29`.
- Decision: valid negative result under PRM-042 only. Do not retune, promote the candidate, generalize to all descriptors, claim inverse design or start the actual tournament.
- Next: separately preregister a no-fit support/range and family-transfer anatomy of frozen T3PX artifacts; continue STRICT image/pixel/component and configuration traceability in parallel.
- Read: `experiments/lab_001_xy_connection_20260626/results/R09-20260721-T3P_CONTROL_TOWER_REVIEW_AND_NEGATIVE_MERGE.md`.
- Indices: `PRM-043 / RUN-190 / DEC-222 / CHG-209 / LAB-CHG-181 / R09-BB-644~650`.

## PRIOR OVERRIDE — T3P mesh-native grouped evaluation preregistered; execution locked, 2026-07-21

- Contract/run: `PRM-042 / RUN-189`; no-y/no-fit preregistration accepted.
- Target/population: official GM YPOL-GM-v0.1 identity, exact54 family-summary z/default rows.
- Candidates: eight T3O mesh-native sensitivity identities; no feature promotion.
- Evaluation: 5 family-aware LOFO outer folds, 20 inner folds, 25 X-only partitions, minimum retained candidates 5.
- Future ceiling: 670 fits; all SG01–SG08 required, including 5% improvement over frozen T3JX RMSE.
- Integrity: main `12/12`, independent `12/12`, control `16/16`, protected `29/29`.
- Current lock: y reads/fits/predictions/promotions `0/0/0/0`; future execution is not authorized.
- Next: control decision to authorize or hold one unchanged T3P execution after live-hash validation.
- Read: `experiments/lab_001_xy_connection_20260626/results/R09-20260721-T3P_CONTROL_TOWER_REVIEW.md`.
- Indices: `PRM-042 / RUN-189 / DEC-221 / CHG-208 / LAB-CHG-180 / R09-BB-638~643`.

## PRIOR OVERRIDE — T3O mesh-native 3D census completed, 2026-07-21

- Contract/run: `PRM-041 / RUN-188`; 58 canonical N40 STL models, 22 candidates and 1,653 pairs.
- Candidate status: 8 sensitivity, 7 redundant hold, 3 constant hold, 4 source-QC.
- T8/T9: robust distance `1.559945`, rank `537/1653`; registered near-collision resolved under T3O.
- Gates/QA: TG `8/8`, independent `19/19`, control `20/20`, visual `2/2`, protected pre/post `29/29`.
- Runtime: unsafe partial attempt quarantined; valid result uses exact topology normalization, isolated KMK312 workers and atomic resume checkpoints.
- Decision: likely y-blind mesh-native representation value only; no predictive/causal/promotion claim.
- Read: `experiments/lab_001_xy_connection_20260626/results/R09-20260721-T3O_CONTROL_TOWER_REVIEW.md`.
- Indices: `PRM-041 / RUN-188 / DEC-220 / CHG-207 / LAB-CHG-179 / R09-BB-631~637`.

## CURRENT OVERRIDE — T3N confirms Lane K selection/generalization instability, 2026-07-21

- Run: `TOUR-C001-T3N-LANE-K-INSTABILITY-001 / PRM-039 / RUN-186`; frozen-artifact no-fit anatomy completed.
- Scope: T3MK 47 OOF rows, 15 outer selections and 1,800 candidate-branch summary cells; fits/refits/new predictions `0/0/0`.
- Generalization gap: confirmed. Inner-positive/outer-negative folds `60%`, families worse than mean null `3/3`, median outer/inner selected RMSE ratio `1.488`.
- Selection instability: confirmed. Ten selected candidates, normalized entropy `0.960`, maximum candidate share `20%`, Spearman(inner gain, outer gain) `-0.321`.
- Winner fragility: likely. Median top-2 relative RMSE margin `3.741%`; median NONE-passing cells `15`.
- Residual concentration: likely. T7/T15/L9/C6/C3 carry `50.407%` of OOF SSE; this does not authorize deletion.
- Schema correction: original census mixed branch-cell and fold counts; v2 separates them and passes `6/6` with no scientific or gate change.
- Integrity: execution `12/12`, correction `6/6`, independent `22/22`, control `22/22`, visual `3/3`, protected `29/29`; metric parity `1.11e-16`.
- Decision: runtime defect rejected; T3MK 1/8 failure preserved; adaptive modeling pauses.
- Next: `STRICT-L7-002_HISTORICAL_SOURCE_CONFIGURATION_CROSSWALK_AUDIT_NO_FIT`; reconstruct the historical L7 F008 discrepancy before any new model contract.
- Read: `experiments/lab_001_xy_connection_20260626/results/R09-20260721-T3N_CONTROL_TOWER_REVIEW.md`.
- Indices: `PRM-039 / RUN-186 / DEC-218 / CHG-205 / LAB-CHG-177 / R09-BB-615~623`.

## PRIOR OVERRIDE — T3M Lane K executed once and failed the frozen gate, 2026-07-21

- Run: `TOUR-C001-T3M-LANE-K-EXEC-001 / PRM-038 / RUN-185`; contract-valid known-family replay, scientifically failed without retuning.
- Scope: C14/L20/T13 = 47 rows, 15 outer / 50 inner folds, 30 equal-entry T3I candidates, four inherited branches.
- Execution: `5,552 / 6,080` fits; all 15 outer folds selected a candidate after the frozen single-family NONE rule.
- Result: OOF R² `-0.416715`, RMSE `145.653856`, Spearman `-0.019776`, mean-null improvement `-13.831%`.
- Family result: C/L/T all worsened versus their fold mean null; L improvement `-11.068%`.
- Frozen Lane G comparison: Lane K RMSE improvement `-21.636%`; known-family routing did not rescue the frozen unseen-family reference.
- Gates: `1/8`; only the worst-family degradation safety guard passed. Thresholds, candidates, folds and rows were not changed.
- T8/T9: actual T8−T9 gap `+10.2067`, predicted gap `-7.7006`; pair order reversed in this Lane K run.
- Integrity: execution `10/10`, negative `6/6`, independent `10/10`, control `20/20`, visual `3/3`, protected `29/29`; maximum independent OOF difference `1.14e-13`.
- Decision: reject this tested Lane K adaptive route under PRM-038. No descriptor promotion, family/theta identity injection, inverse-design claim or actual tournament.
- Next: no-fit `T3N_LANE_K_SELECTION_INSTABILITY_ANATOMY`, then return execution priority to STRICT historical Excel/LEGACY-PY/image/configuration parity. No new modeling before a new preregistration.
- Read: `experiments/lab_001_xy_connection_20260626/results/R09-20260721-T3M_LANE_K_CONTROL_TOWER_REVIEW.md`.
- Indices: `PRM-038 / RUN-185 / DEC-217 / CHG-204 / LAB-CHG-176 / R09-BB-607~614`.

## PRIOR OVERRIDE — T3M two-estimand replay contract merged, execution locked, 2026-07-21

- Run: `TOUR-C001-T3M-DOMAIN-CONDITIONAL-PREREG-001 / PRM-038 / RUN-184`; adaptive no-y/no-fit preregistration accepted.
- Lane K: new structure with an observed family; primary future population `C14 + L20 + T13 = 47`, frozen outer/inner folds `15 / 50`.
- Lane G: entirely unseen-family generalization; reuse frozen T3JX exact54 LOFO only as retrospective reference, never new independent evidence.
- Holds: B5 is low-n hold; F2 is descriptive only and cannot support a specialist inference.
- Candidate policy: all 30 T3I sensitivity candidates enter equally. T3L sign labels cannot preselect, exclude or reweight them.
- Identity policy: family/domain/theta/source identity is split/routing/reporting metadata only and is prohibited as predictor X.
- Preflight: 65/65 X-only partitions reproduced; minimum retained candidates/families `25 / 4`; T8/T9 remain one purge group and one test fold.
- Future fit ceiling: `6,080`; all `KG01`–`KG08` required. Passing would support Lane K utility only.
- Integrity: main `24/24`, independent `31/31`, control `23/23`, visual `1/1`, protected `29/29`.
- Current lock: y reads/fits/predictions/promotions `0/0/0/0`; execution, L/L10 deletion, inverse design and actual tournament remain prohibited.
- Next: `T3M_LANE_K_BOUNDED_EXECUTION_SEPARATE_AUTHORIZATION`; live hashes must be revalidated before one unchanged run. STRICT parity remains parallel.
- Read: `experiments/lab_001_xy_connection_20260626/results/R09-20260721-T3M_CONTROL_TOWER_REVIEW.md`.
- Indices: `PRM-038 / RUN-184 / DEC-216 / CHG-203 / LAB-CHG-175 / R09-BB-599~606`.

## PRIOR OVERRIDE — T3L L-family sign/source forensic merged, 2026-07-20

- Run: `TOUR-C001-T3L-L-SIGN-SOURCE-001 / PRM-037 / RUN-183`; post-hoc no-fit forensic accepted.
- Scope: exact54, frozen T3I 30 candidates, 20 L rows; fits/refits/deletions/promotions `0/0/0/0`.
- Broad result: `9/30` candidates reverse direction in L relative to B/C/T, across all four representation families; six are jackknife-robust.
- Global monotonicity: `0/30` candidates retain one non-neutral direction across B/C/L/T under frozen `|rho|>=0.10` rules.
- Selected candidate: L sign retention `0.95`, T retention `0.538`; descriptive L-opposite only, not globally stable.
- L10 source: geometry/hash/topology/isotropic N40/official row42/raw GM42 audit `13/13`; source-QC extremes `0/6`. Hard source failure rejected.
- L10 representation/target: only `3/30` X extremes and GM robust z `-2.311`, below frozen 3.5 breadth/outlier gates; do not delete or replace.
- Lower row141: z/name-x metadata ambiguity remains, but GM41 and GM141:GM144 are blank; official GM42 alone is populated.
- Integrity: execution `16/16`, independent `24/24`, control `19/19`, visual `3/3`.
- Next: no-fit `T3M_L_DOMAIN_CONDITIONAL_REPLAY_PREREGISTRATION_NO_FIT`; known-family interpolation and unseen-family generalization must remain separate. STRICT parity remains parallel.
- Read: `experiments/lab_001_xy_connection_20260626/results/R09-20260720-T3L_CONTROL_TOWER_REVIEW.md`.
- Indices: `PRM-037 / RUN-183 / DEC-215 / CHG-202 / LAB-CHG-174 / R09-BB-590~598`.

## PRIOR OVERRIDE — T3K ordering/generalization anatomy merged, 2026-07-20

- Run: `TOUR-C001-T3K-ORDERING-GENERALIZATION-001 / PRM-036 / RUN-182`; no-fit/no-refit anatomy accepted.
- Frozen evidence: 54 T3JX OOF rows and all 1,431 unordered model pairs; T3JX remains a preregistered overall failure.
- Ordering: global Spearman `0.161426`; within-family inversion `0.5027` exceeds cross-family `0.4260`, so cross-family calibration is not the dominant registered explanation.
- L concentration: within-L Spearman `-0.1774`, inversion `0.5632`; remove-L descriptive Spearman `0.3448`. This does not authorize excluding L.
- L10 fragility: `49/53` inversions and `15.41%` of total SSE; removing it descriptively raises Spearman to `0.2138`. Do not delete it without source/crosswalk evidence.
- Sign clue: the selected candidate has negative target association in B/C/F/T but positive association in L; status `likely`, not causal/canonical.
- T8/T9: correct order but predicted/actual gap ratio only `0.0527`; strong compression confirmed.
- Integrity: execution `12/12`, independent `35/35`, control `17/17`, visual `4/4`; fits/refits/retuning/promotions `0/0/0/0`.
- Next: no-fit `T3L_L_FAMILY_SIGN_STABILITY_AND_SOURCE_FORENSIC_NO_FIT`; STRICT historical parity remains parallel.
- Read: `experiments/lab_001_xy_connection_20260626/results/R09-20260720-T3K_CONTROL_TOWER_REVIEW.md`.
- Indices: `PRM-036 / RUN-182 / DEC-214 / CHG-201 / LAB-CHG-173 / R09-BB-582~589`.

## PRIOR OVERRIDE — T3JX grouped-GM representation replay reviewed, 2026-07-20

- Run: `TOUR-C001-T3J-GM-REPRESENTATION-REPLAY-001 / RUN-181`; contract-valid execution, preregistered overall failure.
- Scope: official GM exact54, T3I 30 candidates, 5 LOFO outer/20 inner folds, 2,350/2,430 fits.
- Result: OOF R² `0.081452`, RMSE `116.169545`, mean-null improvement `5.559%`, T3D RMSE improvement `17.553%`.
- Gates: `7/8`; only SG07 failed because Spearman `0.161426 < 0.20`. Do not lower the threshold.
- Stability: `simultaneous_exchange_fraction` selected 5/5; sensitivity-only, no promotion. B/C/F/T improved; L degraded 6.847%.
- T8/T9: correct order, but predicted delta `0.538044` vs actual `10.206734`.
- Integrity: 2,350/2,350 independent refits, 5/5 selections, 54/54 OOF; execution 15/15, independent 20/20, control 17/17, protected 29/29.
- Next: no-fit `T3K_ORDERING_FAILURE_AND_GENERALIZATION_ANATOMY`; STRICT parity remains parallel.
- Read: `experiments/lab_001_xy_connection_20260626/results/R09-20260720-T3JX_CONTROL_TOWER_REVIEW.md`.
- Indices: `PRM-035 / RUN-181 / DEC-213 / CHG-200 / LAB-CHG-172 / R09-BB-574~581`.

## PRIOR OVERRIDE — T3J grouped-GM representation replay preregistered, 2026-07-20

- Contract: `PRM-035 / TOUR-C001-T3J-GM-REPRESENTATION-PREREG-001`; accepted no-y/no-fit preregistration, execution locked.
- Frozen comparison: official GM, exact54 family-summary z rows, 5 LOFO outer folds, 20 inner folds, fixed F001 and inherited four branches.
- Only changed factor: T3D T3B 118 candidates → T3I 30 sensitivity candidates across four representation families.
- X-only preflight: every 25 training partitions retains 29–30 candidates and all four families.
- Future ceiling/gates: 2,430 fits; SG01–SG08 all required; T8/T9 report-only.
- Integrity: execution 15/15, independent 24/24, control 10/10, visual 2/2, protected 29/29.
- y magnitude / fits / predictions / promotions: `0 / 0 / 0 / 0`.
- Next: execute the frozen T3J contract once in a separate run after live hash validation. Continue STRICT historical parity in parallel.
- Read: `experiments/lab_001_xy_connection_20260626/results/R09-20260720-T3J_CONTROL_TOWER_REVIEW.md`.
- Indices: `PRM-035 / RUN-180 / DEC-212 / CHG-199 / LAB-CHG-171 / R09-BB-567~573`.

## PRIOR OVERRIDE — seven-model no-y detailed-signal audit merged, 2026-07-20

- Run: `TOUR-C001-T4R-SLICE-002`, KMK312 / Python 3.12.12, y/model fits/predictions `0/0/0`.
- Design: T8/T9 is adaptive discovery only; B3/C1/L1/F1/F2 is the independent no-y evaluation panel.
- Evidence: four unique angle/curvature dispersion identities pass 20/20 finite values, five distinct values per signal and nonzero-variation gates. Raw angle LIP/LTP outputs remain traceable but count once.
- Redundancy: four clusters remain. SIG-A/SIG-D has Spearman 1.00 on n=5 but fails proportional-copy by 26.23%; all-58 evidence is required.
- Decision: `GO_SEPARATE_ALL58_CONTRACT`; this is compute authorization only, not formula/feature promotion.
- Integrity: source reproduction 10/10, QA 9/9, manifest 16/16, tests 33/33, protected 29/29, visual QA 2/2.
- Next: freeze and run a resumable, x-only P1000_S801 all-58 detailed extraction; review before any fit. Continue L7 STRICT provenance in parallel.
- Locks: NB-CURRENT patch, promotion, roster, B/T specialist, T5, theta, inverse design and tournament.
- Canonical registry: `outputs/URP4-1_MASTER_LEDGER_20260719_v0_2.xlsx`.
- Read: `experiments/lab_001_xy_connection_20260626/results/R09-20260720-TOUR-C001_T4R_SLICE_002_SEVEN_MODEL_NOY_CONTROL_TOWER_REVIEW_20260720.md`.
- Indices: `RUN-167 / DEC-199 / CHG-186 / LAB-CHG-158 / R09-BB-471~476`.

## PRIOR OVERRIDE — T8/T9 detailed slice rescue merged, 2026-07-20

- Run: `TOUR-C001-T4R-SLICE-001`, KMK312 / Python 3.12.12, y/model fits/predictions `0/0/0`.
- Execution: six new model/config runs passed; slice/overlay/component rows `3,206/3,200/97,030`, readback mismatch `0`, transient PNG deleted `6,406/6,406`.
- Evidence: 40 detailed LEGACY-PY candidates across four configurations. Strong/robust/resolution-sensitive/weak rows are `3/2/4/31`.
- Likely rescue signals: global-weighted angle stdev, angle IP stdev, layer-mean angle stdev, curvature LTP stdev. LIP/LTP angle output rows are identical by LEGACY-PY-RESULT source logic and count as one signal.
- Hold: curvature IP stdev is resolution-sensitive; no formula canon, feature promotion, NB-CURRENT patch, fit, roster, T5, theta, inverse design or tournament.
- Integrity: manifest 12/12, QA 6/6, tests 33/33, protected assets 29/29, visual QA 3/3.
- Next: no-y/no-fit seven-model CINT-02 panel uniqueness/redundancy audit; parallel L7 historical provenance; then review minimal all-58 batch vs hold.
- Canonical registry: `outputs/URP4-1_MASTER_LEDGER_20260719_v0_2.xlsx`.
- Read: `experiments/lab_001_xy_connection_20260626/results/R09-20260720-TOUR-C001_T4R_SLICE_001_T8_T9_CONVERGENCE_CONTROL_TOWER_REVIEW_20260720.md`.
- Indices: `RUN-166 / DEC-198 / CHG-185 / LAB-CHG-157 / R09-BB-464~470`.

## PRIOR OVERRIDE — T4R-001 no-fit rescue audit merged, 2026-07-20

- Run: `TOUR-C001-T4R-001`, KMK312 / Python 3.12.12, predictive fits/predictions `0/0`.
- Integrity: parent 12/12, QA 12/12, output hashes 18/18, contract tests 55/55, visual QA 4/4; protected sources, Master Ledger v0.2 and Tournament HQ unchanged.
- T8/T9: generic PD-006 collision passes and population-SD stability is 6/6; GM gap `10.206734`. Bounded image-slice/configuration rescue preparation is `confirmed`.
- Scaling caveat: the narrow RMS `0.01` gate remains population-sensitive and was not retuned. F008 mean supplies 94.67% (all-58) to 99.52% (exact-54) of squared standardized pair distance.
- L7: LEGACY-PY direct F008 `0.977830` versus RUN-139 `0.977428`, relative difference `0.0411%`; current implementation parity is `confirmed`.
- Historical L7 Excel: `0.804591`, about 21.5% from both implementations; source/configuration/crosswalk discrepancy class is `likely`, exact cause `unresolved`.
- B/T F007 specialist: 18 rows / 17 purge groups / future budget <=34 fits; preregistered only and not executed.
- Locks: promotion/roster/T5/theta/inverse/tournament remain `0/0/0/0/0/0`.
- Next: bounded T8/T9 image → pixel → component → descriptor rescue packet, plus parallel L7 historical provenance audit. Review both before any specialist replay.
- Canonical registry: `outputs/URP4-1_MASTER_LEDGER_20260719_v0_2.xlsx`.
- Read: `experiments/lab_001_xy_connection_20260626/results/R09-20260720-TOUR-C001_T4R_001_NOFIT_RESCUE_CONTROL_TOWER_REVIEW_20260720.md`.
- Indices: `RUN-165 / DEC-197 / CHG-184 / LAB-CHG-156 / R09-BB-457~463`.

## PRIOR OVERRIDE — T4 no-fit failure anatomy merged, 2026-07-20

- Run: `TOUR-C001-T4-GM-003`, KMK312 / Python 3.12.12, zero predictive fits and predictions.
- Integrity: 21/21 artifact hashes, 11/11 QA, 55/55 contract tests, 5/5 visual QA; protected sources and Master Ledger v0.2 unchanged.
- Result: GM family eta-squared `0.032711`; strongest within-family centered rho `0.335183` for F007 `std_pop_ddof0`; family-blocked maxT passers `0/9`.
- Decision: F007-std is a `likely` B/T specialist **preregistration candidate**, not a promotion. Minimal-team and family-specific-team branches are rejected.
- STRICT: L7 source/parity audit is confirmed priority.
- RESCUE: T8/T9 is `unresolved / scaling-sensitive` because its standardized distance is `0.008142` on the 58-row T3 scale and `0.030111` on the exact-54 scale; do not retune.
- Locks: promotion/roster/T5/theta/inverse/tournament remain `0/0/0/0/0`.
- Next: `T4R-001_NO_FIT_RESCUE_PREREGISTRATION`, then review before any further fit.
- Canonical registry: `outputs/URP4-1_MASTER_LEDGER_20260719_v0_2.xlsx`.
- Read: `experiments/lab_001_xy_connection_20260626/results/R09-20260720-TOUR-C001_T4_GM_FAILURE_ANATOMY_CONTROL_TOWER_REVIEW_20260720.md`.
- Indices: `RUN-164 / DEC-196 / CHG-183 / LAB-CHG-155 / R09-BB-450~456`.

## PRIOR OVERRIDE — T4 GM replay failed its evidence gate, 2026-07-19

- Run: `TOUR-C001-T4-GM-002`, KMK312 / Python 3.12.12.
- Execution integrity: 370/375 fits, 54/54 unique OOF rows, 24/24 hashes, contract tests 55/55, visual QA 3/3.
- Scientific result: outer-OOF R² `-0.720458`, RMSE `158.987641`, null improvement `-29.249877%`, Spearman `-0.287822`, gates `0/6`.
- Stability: each outer family selected a different formula; maximum formula frequency `20%`.
- Decision: `merged_evidence_hold_no_promotion`; promotions/roster/T5/inverse/tournament remain `0/0/0/0`.
- Next: preregister no-promotion failure anatomy and decide specialist vs minimal-team vs new slice-descriptor rescue before fitting again.
- Parallel: STRICT Excel/LEGACY-PY/image-pixel parity continues; periodic-x/theta-x remains future P3.
- Canonical registry remains `outputs/URP4-1_MASTER_LEDGER_20260719_v0_2.xlsx` until the next anatomy/rescue contract is accepted.
- Read: `experiments/lab_001_xy_connection_20260626/results/R09-20260719-TOUR-C001_T4_GM_CONTROL_TOWER_REVIEW_20260719.md`.
- Indices: `RUN-163 / DEC-195 / CHG-182 / LAB-CHG-154 / R09-BB-444~449`.

## PRIOR OVERRIDE — Master Ledger v0.2 synchronized, exact GM preregistration next, 2026-07-19

- Canonical human/AI registry: `outputs/URP4-1_MASTER_LEDGER_20260719_v0_2.xlsx`.
- Preserved history: `outputs/URP4-1_MASTER_LEDGER_20260715_v0_1.xlsx`.
- Synchronized state: 58/58 models, 58 runs, 522 descriptor rows, 9 scalar players and 1,854 artifact rows.
- `21_T3_XX_EVIDENCE` records F005/F006 redundancy, T5/T6 and T8/T9 representation collisions, and no-y audit.
- Workbook QA: export/re-open pass, 23/23 sheets rendered, formula errors 0.
- Scientific boundary: this is registry synchronization only; parity and utility remain independent, and no feature/model/tournament was promoted or run.
- Next: exact GM join/group/null/control preregistration. STRICT parity remains parallel; periodic-x is future P3.
- Read: `experiments/lab_001_xy_connection_20260626/results/MASTER-LEDGER-v0.2_SYNC_REPORT_20260719.md`.
- Indices: `RUN-161 / DEC-193 / CHG-180 / LAB-CHG-152 / R09-BB-437`.

---

## Current control-tower handoff — CINT-07 local contract pass, external DLP release open, 2026-07-19

- Added `urp4/integration/theta_geometry_x/v0_1/` with `THETA-ACTIVITY-REGISTRY-v0.1` and the fail-closed `THETA-GEOMETRY-X-v0.1` join boundary.
- The new registry has 56 source-scoped Lattice/TPMS/Voxel controls split into primary, sensitivity, numerical, seed/leakage, hold and metadata roles. The older 242-row `parameter_json` registry remains a separate generated-candidate population.
- KMK312 ran 60 bounded in-memory OFAT probes: 42 changed the graph/mask/mesh, 17 did not change the tested fixture, and one TPMS connectivity-limit failure was quarantined.
- TPMS sampled component thickness is confirmed metadata-only in the current mask path. Strict-periodic Voxel max-thickness/opening are source-inactive; broader morphology no-effect findings remain unresolved/sensitivity-only.
- Seeds changed all four tested realization families but are excluded as predictors. VF siblings must share base/group identity, carry unique VF/hash, and remain in one split.
- Three CINT-04/05/06 geometry-only fixture joins passed with explicit `x_count=0`. `theta_geometry_x` requires exact DescriptorResult parent and geometry hash; y additionally requires material/process/test domain.
- KMK312 passed 15/15 local tests, 83/83 cross-CINT regression tests and 18/18 gates; protected assets/site are 28/28 unchanged. Official DLP x rows remain zero and five external gates remain open.
- No DLP batch, descriptor, DATASET, x-x, Training, inverse design or tournament ran.
- **Next non-blocked local task: CINT-08 Training-engine modularization without fitting models.** External lane: keep `CHUCK-DLP-X-001` open and intake the professor periodic release when received.
- Read: `experiments/lab_001_xy_connection_20260626/results/CINT-07_DLP_THETA_GEOMETRY_X_FREEZE_20260719.md`.
- Indices: `RUN-157 / DEC-189 / CHG-176 / LAB-CHG-148 / R09-BB-410~416`.

---

## 0. Required terminology

Use these terms from 2026-07-06 onward. Avoid the ambiguous phrase "main notebook" in new reports, logs, blackbox entries, and final answers.

```text
LEGACY-PY
  Professor/TA validated legacy Python scripts.
  Examples: 1._parameter_rawdata_0726.py, 2._Parameter_result_0727.py,
  3._parameter_angle_all_0727.py, Curvature_Extraction_New.py,
  Parameter_distribution_New.py.

NB-ORIG
  Original notebook-format integration attempt first received from the professor/TA.
  File: Model_generator_260506_descriptor_v5_boundary_symmetry_perfboost.ipynb
  Treat this as the original/early integration notebook, not the final authority.

NB-CURRENT
  Current working notebook/code path being validated against LEGACY-PY.
  This is the professor's P1 target: one integrated code path that reproduces
  the validated LEGACY-PY logic/results descriptor-by-descriptor and family-by-family.

R09-SCRIPT
  Codex-made validation/forensic scripts used before modifying NB-CURRENT.
  Examples: R09_020C_stdev_population_forensic.py,
  R09_020D_curvature_lineage_audit.py.
```

Current scientific rule:

```text
LEGACY-PY is the validated reference.
NB-CURRENT is the integration target under validation.
Excel is useful comparison/reference data, but the direct P1 integration
criterion is NB-CURRENT parity with LEGACY-PY first.
R09-SCRIPT outputs are evidence for what NB-CURRENT should implement;
they are not themselves NB-CURRENT.
```

## 1. Project in one sentence

URP4-1 follows the professor sequence last clarified through Chuck on 2026-07-01:

```text
P1 NB-CURRENT integration against LEGACY-PY                      [active/completed by implementation; still under descriptor parity validation]
P2 external STP/STL import + Excel descriptor validation        [active]
P3 new-model generation + theta-x database
P4 theta-x AI learning
P5 connect professor x-y asset + inverse design
```

P1 has a **98/100 technical strong pass in the disposable lab** for integration/implementation mechanics. However, NB-CURRENT should only be described as fully passed after descriptor/family parity against LEGACY-PY is sufficient. R09/P2 is now active: use the supplied 56+(2) figure as the naming authority, import individual STP/STL reference models, and compare current descriptors with matched Excel structural descriptors. The current professor comparison rule is `x = current parameters`, `y = Excel parameters`, same order, then inspect `y=x` / `y=a*x` similarity and standout rows rather than strict exact equality.

Long-term conceptual chain:

```text
generation parameters theta
→ generated geometry / STL / mesh G
→ structural descriptors x
→ performance metrics y
→ inverse design target y* → x* → theta*
```

Current critical path:

```text
raw STP/STL + hashes + model-ID registry
→ external-STL QA 33/33 + supplied-STL descriptor pilot 4/4       [done]
→ x_current versus x_excel first comparison 0/232 exact           [done; superseded as diagnostic only]
→ y=x / y=a*x similarity analysis                                 [done; point-global strong, slice families discrepant]
→ legacy audit: Excel point=INP nodes, slice=PNG overlays          [done; PPT slice settings now working authority]
→ professor source split: surface area=STL, slice descriptors=Ntop [done; 2026-07-02]
→ R09-SLICE: Python one-step Ntop-slice reproduction; start with B3 MassOri stdev
→ R09-SURF: STL-native surface area / normalized surface area scale validation
→ representative C/L/F/T formula generalization
→ trusted P2 gate
```

---

## Dashboard/telemetry handoff — TOUR-HQ-LIVE-007 isolated read-only SSE transport accepted, 2026-07-18

- **Scope:** dashboard/telemetry only. This handoff does not supersede CODE-MAP-001 scientific/source integration authority.
- **Observed:** preregistered attempt03 passed 55/55 owner-only production-browser paths: 20 UI diagnostics, 25 resume probes, five deleted-session and five tampered-session recoveries. Failures/runtime exceptions/official events were 0/0/0.
- **Browser security:** the long-lived staging bearer stays server-side. A same-origin intent-checked POST issues a 15-minute HMAC-signed `HttpOnly; Secure; SameSite=Strict` cookie. Browser JavaScript sends no Authorization header and stores no bearer.
- **Isolation:** one mock ledger hash, head sequence 4 and official event count 0. RUN-139 snapshot hash, source `official`, `is_mock=false`, sequence 0 and event count 0 were exact before/after.
- **Attempt audit:** attempt01 is inconclusive and attempt02 failed strict UI equality; neither was rewritten as a pass. Attempt03 is the only accepted evidence.
- **Production:** owner-only Sites v9 at `https://urp4-tournament-hq.velocity0842.chatgpt.site`; final recovered boundary recheck passed 25/25 requests after one transient immediate post-deploy HTTP 500.
- **Locks:** acceptance is limited to isolated read-only SSE transport. Official MODE-C, WebSocket, event publication and all Start/Pause/Retry/Promote/Merge/Edit-roster writes remain disabled/hold/prohibited. DATASET/x-x/roster/match remain unexecuted.
- **Read first:** `experiments/lab_001_xy_connection_20260626/results/TOUR-HQ-LIVE-007_RECONNECT_RESUME_OBSERVATION_AND_ACCEPTANCE_20260718.md`.
- **Next:** mandatory mock-SSE work is complete. Prefer a real append-only factory event-source authority/provenance contract when the factory is ready. Optional receive-only WebSocket remains two separately preregistered tasks.
- **Indices:** RUN-149 / DEC-181 / CHG-168 / LAB-CHG-140 / R09-BB-381.

## Previous dashboard/telemetry handoff — TOUR-HQ-LIVE-001 polling shadow, 2026-07-17

- **Scope:** dashboard/telemetry only. This handoff does not supersede CODE-MAP-001 scientific/source integration authority.
- **Actual shadow:** `RUN-139 / R09-RESLICE-003` is displayed as a completed upstream descriptor run: 58/58 technical pass, 522 rows, 9 scalar outputs/model.
- **Contract:** immutable same-origin snapshot, canonical snapshot SHA-256, six source-artifact hashes, exporter-owned sequence 0, and an empty runtime event history. No historical events were invented.
- **Isolation:** mock and actual snapshot/event state are separate. Polling is connected; SSE/WebSocket are disabled; Start/Pause/Retry/Promote/Merge/roster writes remain absent and locked.
- **Boundary:** DATASET-v0.1 not materialized, x-x not executed, roster not determined, match not executed. F001-F006 definition/artifact scope only; F007 historical identity rejected; F008 likely; F009-F012 hold.
- **Production v4:** `https://urp4-tournament-hq.velocity0842.chatgpt.site`. JSON/evidence hashes are exact. Cloudflare dynamically injects a challenge into rendered HTML; source/build/CSP/sandbox remain unchanged. `/original/tournament-factory-hq.exact.bin` is the published 73,104-byte exact-hash verification path.
- **Read first:** `outputs/URP4-1_TOUR_HQ_LIVE_001_READ_ONLY_POLLING_SHADOW_20260717.md` and `sites/tournament-factory-hq/docs/TOUR_HQ_LIVE_001.md`.
- **Next telemetry gate:** repeated polling stability → SSE read-only preregistration → reconnect/resume/gap validation → receive-only WebSocket after SSE. Never broaden this into execution authority.
- **Indices:** RUN-143 / DEC-175 / CHG-162 / LAB-CHG-134 / R09-BB-373~375.

## Current handoff override — CODE-MAP-001 code inventory and modular integration roadmap, 2026-07-16

- **Outcome:** 138 code files were mechanically inventoried and 30 core assets/asset families were assigned an authority, status, integration action and acceptance gate.
- **Integration policy:** do not concatenate professor/TA notebooks and scripts. Preserve immutable sources, wrap LEGACY-PY as reference/golden-test oracles, extract generator/training plugins, refactor the validated R09 backend after frozen-output replay, and make the next NB version a thin orchestrator.
- **Previous sources included:** LEGACY-PY six files, NB-ORIG, Training notebooks 1st~5th (nine files), new Lattice/TPMS generators, the embedded provisional Voxel path, NB-CURRENT variants and R09 code families.
- **Missing utility:** `get file lists.py` is not present in the workspace/alias registry. It is non-blocking and should be registered only if recovered.
- **Current boundary:** no source notebook, LEGACY-PY, NB variant, Excel, Training run, generator run, dataset, tournament, dashboard or site was modified/executed.
- **Read first:** `outputs/URP4-1_CODE_ASSET_MASTER_MAP_AND_INTEGRATION_PLAN_20260716.md` and `experiments/lab_001_xy_connection_20260626/reports/tables/CODE-MAP-001_code_asset_registry_20260716.csv`.
- **Next:** CINT-03 RUN-139 descriptor-service regression migration. CINT-02 LEGACY adapters/golden fixtures are complete. TPMS production config, Voxel source, Type-B Variables input and final delivery packaging remain external decisions.
- **Session boundary:** this original control-tower session owns source/integration authority. The separated tournament/dashboard session consumes only frozen/promoted identities and remains untouched here.
- **Indices:** PRM-028 / RUN-142 / DEC-174 / CHG-161 / LAB-CHG-133 / R09-BB-372.

## Previous handoff — PRM-028 generator/DLP intake complete, execution still stopped, 2026-07-16

- **Professor focus:** descriptor x accuracy and paired theta-to-x are the active focus; x-to-y remains a domain-aware refinement lane; final target is theta-to-x-to-y.
- **DLP plan:** periodic about 190 and aperiodic about 150 across VF30/45/60. No DLP release has been received; do not train or guess metadata.
- **Generator intake:** `GEN-LATTICE-TYPEAB-20260716` and `GEN-TPMS-MULTIWALL-VF50-20260716` are byte-identical read-only raw copies. Source delivery is confirmed, authorship likely, production config unresolved. No cell was executed.
- **Lattice finding:** independent from NB-ORIG/NB-CURRENT. COM/SOUND 1920x1080 printing slices are a separate `DLP-PRINT-SLICE` contract, not RUN-139 slicing.
- **TPMS finding:** NB-ORIG-derived; 98 current rows conflict with stale 64 expectation and 434-row output. Row VF is 0.45-0.55 while `vf_error` uses global 0.30; sampled thickness is not geometry-active; open-cell check is inactive.
- **Architecture:** keep Lattice/TPMS/Voxel as generator plugins and NB-CURRENT as future orchestrator. Do not merge whole notebooks.
- **Domain rule:** group VF siblings by `base_geometry_id`; never blindly pool legacy metal and DLP performance y.
- **Seven lanes:** DESC-ACCURACY, DESC-DIFF, GEN-MODULAR, DLP-INTAKE, THETA-X, X-Y-REFINE, TOURNAMENT-DESIGN.
- **Tournament packet:** detailed side-fork is `ready_for_merge` but non-authoritative. Do not modify `tournament-factory-hq`/site/prototype in this task.
- **Read first:** `outputs/URP4-1_MAIN_HANDOFF_PROFESSOR_DIRECTION_AND_MODULAR_GENERATOR_20260716.md`, `experiments/lab_001_xy_connection_20260626/results/GEN-INTAKE-001_GENERATOR_NOTEBOOK_IMMUTABLE_INTAKE_AND_SOURCE_AUDIT_20260716.md`, and `experiments/lab_001_xy_connection_20260626/results/GEN-MODULAR-001_GENERATION_DESCRIPTOR_ARCHITECTURE_SPEC_20260716.md`.
- **Alias registry:** use `outputs/URP4-1_file_alias_registry_20260716_GENERATOR_INTAKE_INTEGRATED.xlsx` / `REGISTRY-BOOK-v1.1`.
- **Next:** obtain TPMS production decisions and professor periodic-x metadata, then preregister a small matched differential validation. No DATASET/x-x/training/roster/tournament execution yet.
- **Indices:** PRM-028 / RUN-141 / DEC-173 / CHG-160 / LAB-CHG-132 / R09-BB-365~371.

## Previous handoff — FACTORY-PREP-001 passed, execution intentionally stopped, 2026-07-16

- **Upstream truth:** RUN-139 remains 58/58 technical pass with 522 descriptor rows and 9 scalar outputs/model.
- **Scientific boundary:** F008 is `likely` with 0.2561% median relative error and preserved L7/row36 21.4813% outlier. F007 mean/std are separate utility players, not historical Excel Thickness identity. F009~F012 remain hold/unresolved.
- **Taxonomy:** Main Leagues are Historical Parity and Predictive Utility. Auxiliary Tournaments are Configuration/Fidelity and Theta. ALL/BCL/F/T/domain-specific are Divisions. Specialist is a roster/team label, not a league.
- **Cycle/IDs:** use `TOUR-C001` / Cycle C001 and preserve existing `T0`~`T8` stage IDs.
- **Prepared only:** `experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/` now contains empty contract/registry/storage/quarantine/merge skeletons. No DATASET-v0.1 or x-x output exists.
- **Pending:** final primary roster scope, Z/AI/AY/AQ benchmark combination, redundancy/near-collision thresholds, starter/challenger counts, composite weights, and active roster.
- **Master Ledger:** v0.1 is immutable and synchronization-required. It has 58 pending extraction slots but only 22 models/198 materialized descriptor rows. Do not overwrite it.
- **Read first:** `outputs/URP4-1_DESCRIPTOR_TOURNAMENT_STEERING_ADDENDUM_RUN139_20260716.md`, `experiments/lab_001_xy_connection_20260626/results/FACTORY-PREP-001_MINIMAL_STEERING_AND_FACTORY_SKELETON_20260716.md`, and `experiments/lab_001_xy_connection_20260626/results/TOUR-C001_PREREGISTRATION_PENDING_DECISION_CHECKLIST_20260716.md`.
- **Next:** approve `TOUR-C001-PD-001~004`; only then assign the Data Factory run/config/code hashes and build DATASET-v0.1. Do not execute x-x until `PD-005~008` are approved.
- **Indices:** RUN-140 / DEC-172 / CHG-159 / LAB-CHG-131 / R09-BB-361~364.

## Previous handoff — R09-RESLICE-003 all-58 factory passed, 2026-07-15

- **Technical gate:** all 58 frozen N40 geometries passed the image → saved-PNG readback → pixel/component → F001~F008 → deletion pipeline under `KMK312`.
- **Frozen output:** 46,458 slice rows, 46,400 overlay rows, and 522 descriptor rows. Readback mismatch, kernel-parity failure, deletion failure, global temporary-file remainder, missing artifact, and SHA-256 replay mismatch are all zero.
- **Image policy:** 92,012 temporary PNGs were deleted after table/hash freeze and 846 deterministic audit PNGs retained. The interrupted C7/a01 attempt is explicitly recorded; its 131 temp PNGs were hashed/deleted and C7/a02 passed.
- **Schema:** every completed attempt carries DESCRIPTOR-SCHEMA-v0.1 hash `fd5db3fd34c9a1bc90a6fae6378cad0c6f4f90148494eb5d2471c195242b7eea`. F001-F006 remain confirmed definitions, not confirmed predictors.
- **F008 parity:** source-scoped comparison against `EXCEL_LEGACY_260212::External Overlay Mass Orientation::IP` has median relative difference 0.2561%, but L7/row36 is a 21.4813% outlier. F008 is `likely`, not canonical/confirmed. Without L7, model-mean Pearson r is 0.8958; the outlier is not removed from official evidence.
- **F007/F009~F012:** F007 remains rejected as the historical Excel Thickness identity but retained as a separate utility candidate. F009~F012 remain held/unresolved and were not calculated.
- **Representation:** T8/T9 remain near-colliding in all nine frozen F001~F008/stat rows despite diagnostic GM gap 10.2067335.
- **Missing y:** T5/T6/T10/T16 were extracted but retain blank one-to-one GM targets. Never split/copy the combined `T5-6` value.
- **Read first:** `experiments/lab_001_xy_connection_20260626/results/R09-20260715-RESLICE-003_ALL58_FINAL_QA_AND_PARITY_BRIEF.md` and `experiments/lab_001_xy_connection_20260626/reports/figures/R09-RESLICE-003_F008_yx_parity_dashboard_20260715.png`.
- **Next execution:** freeze `DATASET-v0.1`, then x-x uniqueness/collision and family coverage, then leakage-safe grouped x-y utility. Continue L7/F008 and F009~F012 STRICT audits in parallel.
- **Indices:** RUN-139 / DEC-171 / CHG-158 / LAB-CHG-130 / R09-BB-356~360.

2026-07-01 update: the PPT-setting slice reproduction lane has now been implemented and proven on B3-z at pilot scale. A cautious B3/C1/L1/F1 low-cost setting sweep showed that no tested setting alone was strong enough to justify true `ppt_full` on the research-lab PC. A later B3 one-model forensic replay found the stronger clue: legacy-v2 formulas from `2._Parameter_result_0727.py` sharply improve B3 `Thickness` and `Perimeter-to-area` against Excel. The next active step is `R09-20260701-007C`: classify B3 descriptor families by formula lineage before any heavy full-resolution run.

2026-07-02 update: Chuck completed a manual page-by-page textification of the parameter-extraction PPTX. From now on, use `outputs/manual_textification_templates/01_PPTX_PAGE_BY_PAGE_AI_DRAFT_파라미터_추출법_0724.md` as the working slice/parameter reference, and use the original PPTX only as a visual fallback. The corresponding analysis and next-step plan is `experiments/lab_001_xy_connection_20260626/results/R09_PPTX_TEXTIFICATION_REFERENCE_ANALYSIS_20260702.md`. The next active step is `R09-20260702-007E`: convert the reviewed PPTX rules into code-level crosswalks and isolate the B3 Mass orientation aggregation/stdev mismatch.

2026-07-02 professor follow-up update: Chuck confirmed two provenance facts with the professor. Normalized surface area used STL-measured surface area, but the professor said it is not fully accurate and needs improvement. Slice-based descriptors were generated in Ntop, and the goal is to reproduce them one-step in Python. Therefore split R09/P2 into `R09-SURF` and `R09-SLICE`: surface-area descriptors should validate STL-native scale and likely `(VF × 30³)^(2/3)` denominator candidates, while slice descriptors should reproduce the Ntop/PPTX pipeline in Python. Historical notes used `4000 px`; this is superseded as the immediate default by the 2026-07-03 update below.

2026-07-03 professor/PPT reinterpretation update: current R09-SLICE working standard is `1000×1000 px`, `40 mm × 40 mm`, `area_per_pixel=0.0016 mm²/pixel`, `0.05 mm`, `801 slices`, OpenCV connected components, and `min_pixels=2`. Treat 4000px as historical/sensitivity context, not the next default. PPT "pillar" = connected component. IP/LIP/LTP are now likely population definitions: IP=component-level pooling, LIP=layer-level population, LTP=weighted population. Curvature and Angle likely use area-derived effective length `L_eff`; exact formula/std remains unresolved. Main new report: `experiments/lab_001_xy_connection_20260626/results/R09_ppt_condition_reinterpretation_20260703.md`.

`R09-POINT` remains a provenance-tracking lane for Distribution descriptors: the reviewed PPTX and prior audit indicate an INP-node population, so exact STL-vertex parity should not be claimed unless original INP nodes are provided.

2026-07-02 Chuck clarification update: for the reviewed PPTX interpretation, start with `H = 0.05 mm`, treat “기둥” as an OpenCV connected component, apply the PPTX min-component rule of 2 pixels, and treat normalized surface area as `STL measured surface area / (VF × 30³)^(2/3)` unless superseded. The `IP/LIP/LTP-stdev` population remains unresolved and is the first B3 MassOri target.

2026-07-02 B3 MassOri update: targeted B3 tests show that slice spacing is a major mismatch source. `1000 px × 801 slices` moves MassOri strongly toward Excel, and the best current candidate is `xyz + all-overlay connected components + denominator-weighted MassOri` (`weight = 0.5×Red + 0.5×Blue + Purple`). It matches the 6 MassOri Excel rows with median abs diff `0.002183` and slope `0.997317`; averages are close, LIP/LTP stdev are close, but IP-stdev remains too high. Current strategy: adopt this as **MassOri v0.2 working candidate** for forward P2 work, but flag `MassOri_IP_stdev` as `unresolved / low-confidence` and track it in parallel. Do not block representative-family validation solely on IP-stdev. Main finding document: `experiments/lab_001_xy_connection_20260626/results/R09_B3_MASSORI_FINDINGS_20260702.md`.

2026-07-02 forensic factory update: to prepare for the final Friday lab day, a laptop-validated R09 forensic production line now exists. Use `tools/R09_FACTORY_00_DOCTOR.cmd` first, then `tools/R09_FACTORY_04_LAB_PC_MASSORI_801_RUN.cmd` on the research-lab PC for the main `B3/C1/F1/L1` MassOri v0.2 queue (`1000px x 801 slices`, `xyz`, weighted). Laptop verification already passed: doctor `PASS`, `legion_smoke` `3/3 success`, and `representative_low` `4/4 success`. Runbook: `experiments/lab_001_xy_connection_20260626/results/R09_FORENSIC_FACTORY_RUNBOOK_20260702.md`. Main new scripts: `scripts/R09_massori_v02_forensic.py` and `scripts/R09_forensic_factory.py`.

2026-07-02 USB transfer update: a minimal USB-ready factory package was prepared at `C:\Users\chuck\Documents\URP4-1_R09_FACTORY_USB_20260702` and zipped as `C:\Users\chuck\Documents\URP4-1_R09_FACTORY_USB_20260702.zip`. The package excludes the huge KMK312 environment and instead uses an improved `tools\run_kmk312_python.cmd` wrapper that auto-detects `%KMK312_PYTHON%`, bundled `tools\envs\KMK312`, or common Anaconda/Miniconda KMK312 paths including `C:\Users\Administrator\anaconda3\envs\KMK312\python.exe`.

2026-07-03 lab-PC USB result update: Chuck returned the USB results from the research-lab PC. The process-level factory run was `4/4 success`, but the scientific output was invalid: every MassOri component count was zero, all MassOri descriptor values were `nan`, and strict comparison files were empty. Root cause found during local reproduction: `trimesh` section curves can exist while `path2d.polygons_full` fails if dependencies such as `networkx`/`rtree` are missing; the old rasterizer swallowed that exception and returned empty masks. The returned USB result was preserved at `C:\Users\chuck\Documents\URP4-1_R09_FACTORY_USB_RESULT_20260703`. Main report: `experiments/lab_001_xy_connection_20260626/results/R09_LAB_PC_MASSORI_801_ANALYSIS_20260703.md`.

2026-07-03 safety update: `scripts/R09_forensic_factory.py` doctor now checks `shapely`, `rtree`, `networkx`, and `tabulate`; `scripts/R09_massori_v02_forensic.py` now raises an error if all MassOri `component_count` values are zero. Patched scripts compile and doctor passes under `tools/envs/KMK312/python.exe`. Before any new lab-PC run, refresh the USB package or copy the patched scripts, run the patched doctor on the exact lab-PC KMK312, and rerun B3 first. For direct Excel `slice_z_*` comparison, use `axis=z`; treat `axis=xyz` as diagonal slicing, not x/y/z combined. Corrected local `axis=z`, `1000px x 801`, weighted results show promising MassOri averages but unresolved stdev and a major F1 outlier.

2026-07-03 corrected USB package update: a new USB package was created directly at `D:\URP4-1_R09_FORENSIC_USB_20260703`. Use this instead of `D:\URP4-1_R09_FACTORY_USB_20260702`. It includes the patched doctor, zero-component guard, `axis=z` main queue, and `20260703` output paths. Recommended lab-PC order: `00_DOCTOR_FIRST.cmd` -> `01_RUN_B3_Z_FIRST.cmd` -> `02_RUN_MAIN_Z_801_B3_C1_F1_L1.cmd`. The USB package doctor passed with `%KMK312_PYTHON%` pointed to workspace KMK312, the generated manifest confirmed B3/C1/F1/L1 `--axes z`, and package scripts passed `py_compile`.

2026-07-04 R09-017 update: `R09-20260704-017` completed a B3-only 1000×801 z-axis component/layer runner. It generated raw component/layer tables and compared candidate formulas against Excel. Strong B3 survivor candidates are: MassOri avg = `mass_orientation_current + IP_component_weighted`, Angle = `angle_h_contact_sum`, P-A = `pa_pixel_unit_red_purple`, Thickness = `thickness_area_red_purple`, and Curvature avg = `curvature_current_contact_sum_over_2h`. Do **not** treat these as final canonical formulas yet. MassOri stdev and Curvature stdev remain unresolved, and new `R09-BB-021` tracks whether B3-only candidates generalize to other families. Next active gate: `R09-20260704-018 Representative-family survivor validation`.

2026-07-04 R09-018A update: Chuck asked to attack the two remaining weak channels directly before broad family expansion. `R09-20260704-018A` swept `73,872` MassOri/Curvature stdev-like candidates and `295,488` Excel comparisons using the existing B3 raw component/layer tables. Result: MassOri stdev and Curvature stdev are no longer vague failures; both have B3 survivor hypotheses. MassOri stdev likely depends on boundary/no-purple/noisy-component filtering or robust statistics. Curvature stdev likely has two channels: small-scale current curvature around `0.12–0.13` and large-scale area/contact-derived dispersion around `16.8`. Added `R09-BB-022 = unresolved`. Next active gate: `R09-20260704-018B Representative-family stdev survivor validation`.

## 1.1 Data-source interpretation update

Professor-side context relayed by Chuck through 2026-07-01, rewritten using the 2026-07-06 terminology:

```text
LEGACY-PY = professor's individually validated implementations.
NB-CURRENT = current integrated descriptor implementation being validated against LEGACY-PY.
Excel workbook = actual experimental/performance data plus reference structural descriptors.
56+(2) figure = model-family naming authority.
Geometry scope now = STP and STL only; INP excluded.
First learning relation = theta -> x. Existing x-y asset is downstream.
```

Therefore:

- keep the current NB-CURRENT candidate path frozen during evidence gathering unless a logged patch is explicitly requested;
- use matched Excel structural descriptors as the active P2 comparison target;
- interpret the active P2 comparison by `y=x` / `y=a*x` similarity and outlier review, not strict exact equality;
- use Chuck's reviewed textification `outputs/manual_textification_templates/01_PPTX_PAGE_BY_PAGE_AI_DRAFT_파라미터_추출법_0724.md` as the current slice/parameter authority. The original `파라미터 추출법_0724.pptx` is now a visual fallback only;
- treat descriptor scale/provenance as family-specific:
  - surface-area / normalized-surface-area lineage: STL-measured surface area, likely native 30 mm scale, accuracy-improvement target;
  - slice descriptor lineage: Ntop slice outputs, reproduce with Python one-step using reviewed-PPTX settings;
  - point/distribution lineage: INP-node population, not exact STL-vertex parity unless INP nodes are provided;
- treat B3 formula-lineage evidence as active: Excel `Thickness` and `Perimeter-to-area` likely follow legacy-v2 definitions more closely than the current/v3 path;
- preserve R03-R05 as exploratory lineage work;
- preserve R07/R08 as downstream assets, but pause production/search/inverse-design claims;
- do not locate or rebuild the existing x-y asset during P2;
- retain original T19/SC5 source names, record provisional T17/SC mappings separately, and compare them without silently renaming raw evidence.

---

## 2. Current active lab

Active disposable lab:

```text
experiments/lab_001_xy_connection_20260626/
```

Use the lab for experiments. Do not mutate original files unless explicitly asked.

Important lab files:

```text
experiments/lab_001_xy_connection_20260626/lab_manifest.md
experiments/lab_001_xy_connection_20260626/protocol.md
experiments/lab_001_xy_connection_20260626/runlog.md
experiments/lab_001_xy_connection_20260626/decision_log.md
experiments/lab_001_xy_connection_20260626/source/URP4-1/
experiments/lab_001_xy_connection_20260626/reference/
```

---

## 3. Read policy

Default minimal read set:

```text
AI_START_HERE.md
outputs/URP4-1_PROFESSOR_PROJECT_ROADMAP_20260629.md
outputs/URP4-1_ROADMAP.md
outputs/URP4-1_CHANGELOG.md
experiments/lab_001_xy_connection_20260626/lab_manifest.md
experiments/lab_001_xy_connection_20260626/runlog.md
```

If the task updates project progress, planning, status, or evaluation:

```text
outputs/URP4-1_ROADMAP.md
outputs/URP4-1_ROADMAP_LOG.md
outputs/URP4-1_CHANGELOG.md
```

If the task is x-y connection:

```text
outputs/input&output.md
experiments/lab_001_xy_connection_20260626/protocol.md
experiments/lab_001_xy_connection_20260626/source/URP4-1/압축+열+진동+구조인자_260212.xlsx
```

If the task is NB-ORIG / NB-CURRENT / forward pipeline:

```text
outputs/input&output.md
experiments/lab_001_xy_connection_20260626/source/URP4-1/Model_generator_260506_descriptor_v5_boundary_symmetry_perfboost.ipynb
```

If the task is current R09/P2 reference validation:

```text
experiments/lab_001_xy_connection_20260626/results/R09_reference_descriptor_validation_plan_20260701.md
experiments/lab_001_xy_connection_20260626/results/R09_model_family_registry_20260701.md
experiments/lab_001_xy_connection_20260626/data/raw/notion_reference_models_20260701/R09_reference_model_manifest.csv
experiments/lab_001_xy_connection_20260626/reports/tables/R03_column_map.csv
experiments/lab_001_xy_connection_20260626/results/R09_stl_quality_preflight_20260701.md
experiments/lab_001_xy_connection_20260626/results/R09_stl_reference_pilot_report_20260701.md
experiments/lab_001_xy_connection_20260626/results/R09_excel_pilot_comparison_report_20260701.md
experiments/lab_001_xy_connection_20260626/results/R09_legacy_preprocessing_recovery_20260701.md
experiments/lab_001_xy_connection_20260626/results/R09_y_equals_x_similarity_report_20260701.md
experiments/lab_001_xy_connection_20260626/results/R09_ppt_slice_reproduction_summary_20260701.md
outputs/manual_textification_templates/01_PPTX_PAGE_BY_PAGE_AI_DRAFT_파라미터_추출법_0724.md
experiments/lab_001_xy_connection_20260626/results/R09_PPTX_TEXTIFICATION_REFERENCE_ANALYSIS_20260702.md
```

If the task is explaining to the human:

```text
outputs/URP4-1_candidate_v0_2_flow_addendum/00_START_HERE_AND_TOC.md
experiments/lab_001_xy_connection_20260626/results/R06V2_P1_LEGACY_INTEGRATION_HANDOFF_20260630.md
outputs/ai_handoff_prompt_pack.md
outputs/workspace_file_roles.md
outputs/URP4-1_역설계_마이크로전략_20260625.md
```

Avoid reading all 13 study-book files unless the user specifically asks for teaching or book-level explanation.

---

## 4. Hard operating rules

1. Preserve original files.
2. Work inside `experiments/lab_*` for trial-and-error.
3. Keep logs:
   - global changes: `outputs/URP4-1_CHANGELOG.md`
   - lab runs: `experiments/<lab>/runlog.md`
   - lab decisions: `experiments/<lab>/decision_log.md`
4. Use English names for new code/analysis files.
5. Use real code terms where possible:
   - `theta`
   - `G`
   - `x`
   - `y`
   - `parameter_json`
   - `candidate_id`
   - `generator_type`
   - `structural_descriptors_full`
   - `generated_table_with_structural_descriptors`
6. If a task asks for diagnosis, do not implement fixes unless asked.
7. If a task asks for implementation, verify and log.
8. Compute placement:
   - Use Chuck's personal computer for code development, registry work, reports, and small smoke tests.
   - First planned research-lab-PC use is R07 batch sensitivity / multi-candidate descriptor extraction.
   - Use the research-lab computer for R08 broad candidate search and R11 geometry-level robustness runs.
   - Before the first lab-PC batch run, inventory its specs and compare one identical candidate against the personal-PC KMK312 result.
   - Do not assume GPU acceleration until the lab-PC hardware and the notebook's actual execution path are verified.
9. Search strategy is throughput-first:
   - generate/screen a large theta pool when compute permits;
   - use cheap checks/descriptors for the broad pool;
   - reserve slow point/interior/full descriptors for top-ranked candidates;
   - preserve IDs, seeds, configs, machine/runtime metadata, and final-candidate reproducibility.
10. Dual-computer workflow:
   - Legion is the control node and single source of truth.
   - The research-lab PC is a disposable compute worker; do not edit authoritative source files there.
   - Use immutable input bundles and copy completed result bundles back to Legion.
   - Read `outputs/R07_DUAL_COMPUTER_EXECUTION_PLAYBOOK_20260629.md` for the 2026-06-29 R07 startup sequence.
11. Current macro gate:
   - R09/P2 STP/STL + Excel descriptor validation is the active scientific critical path.
   - Do not modify NB-CURRENT/candidate evidence paths unless explicitly asked; build external STP support in a new candidate path.
   - Do not start R07 production until P2 provides a trusted descriptor path; do not start R08 inverse search until theta-x and x-y gates pass.
   - Existing R07/R08 outputs remain preserved as diagnostic and future-phase assets.

---

## 5. Most important source files

```text
outputs/URP4-1/Model_generator_260506_descriptor_v5_boundary_symmetry_perfboost.ipynb
outputs/URP4-1/압축+열+진동+구조인자_260212.xlsx
outputs/manual_textification_templates/01_PPTX_PAGE_BY_PAGE_AI_DRAFT_파라미터_추출법_0724.md
outputs/URP4-1/파라미터 추출법_0724.pptx
outputs/URP4-1/KakaoTalk_20260622_161101284.png
outputs/URP4-1/KakaoTalk_20260622_161416457.png
```

Legacy descriptor source files:

```text
outputs/URP4-1/Parameter_distribution_New.py
outputs/URP4-1/Curvature_Extraction_New.py
outputs/URP4-1/1._parameter_rawdata_0726.py
outputs/URP4-1/2._Parameter_result_0727.py
outputs/URP4-1/3._parameter_angle_all_0727.py
outputs/URP4-1/Extract_structure_variable.py
```

---

## 6. Recent completed actions

R05-20260626-001 completed:

```text
R05 ran an exploratory x-y relationship analysis on the actual-experiment Excel reference.

Key outputs:
- experiments/lab_001_xy_connection_20260626/results/R05_xy_baseline_report.md
- experiments/lab_001_xy_connection_20260626/reports/tables/R05_dataset_diagnostics.csv
- experiments/lab_001_xy_connection_20260626/reports/tables/R05_target_summary.csv
- experiments/lab_001_xy_connection_20260626/reports/tables/R05_feature_ranking.csv
- experiments/lab_001_xy_connection_20260626/reports/tables/R05_model_metrics.csv
- experiments/lab_001_xy_connection_20260626/reports/figures/R05_*
- experiments/lab_001_xy_connection_20260626/notebooks/R05_xy_baseline_analysis.ipynb

Observed scope:
- 4,664 x-y feature-target pairs evaluated.
- 42 baseline model runs completed.
- R05 score: 84/100, pass for its prior exploratory scope, not professor P3 completion.

Interpretation:
- The Excel values are actual experimental reference data.
- R05 remains exploratory because its official lineage, units, and relationship to the professor-provided downstream x-y asset are not yet established.
```

R06-20260626-001 completed:

```text
R06 performed safe static validation plus isolated dependency probe of the NB-ORIG/NB-CURRENT forward pipeline.

Key outputs:
- experiments/lab_001_xy_connection_20260626/results/R06_forward_pipeline_validation.md
- experiments/lab_001_xy_connection_20260626/reports/tables/R06_notebook_flow_map.csv
- experiments/lab_001_xy_connection_20260626/reports/tables/R06_function_inventory.csv
- experiments/lab_001_xy_connection_20260626/reports/tables/R06_dependency_check.csv
- experiments/lab_001_xy_connection_20260626/reports/tables/R06_output_artifact_validation.csv
- experiments/lab_001_xy_connection_20260626/reports/tables/R06_descriptor_output_schema.csv
- experiments/lab_001_xy_connection_20260626/reports/tables/R06_failure_log.csv

Observed scope:
- 19 notebook cells mapped.
- 178 function definitions inventoried.
- 142 static descriptor output keys extracted.
- 7 failures/risks logged.
- R06 score: 76/100, not pass yet.

Main blockers:
- The NB-ORIG default config can auto-run all 1000 candidates.
- Generation runner functions have duplicate definitions and execution-order risk.
- No preview STL/generation log/descriptor table has been generated in the lab yet.
- R06 notebook descriptor keys still need an alias/crosswalk to R04/R05 stable variable IDs.
```

R06-20260626-002 completed:

```text
Project-local environment was created and verified for R06/R07/R08.

Use:
- .\.venv\Scripts\python.exe
- Jupyter kernel: URP4-1 R06 (.venv) / urp4-1-r06

Key outputs:
- environment/ENVIRONMENT_SETUP_20260626.md
- environment/requirements-r06-core.txt
- environment/requirements-r06-analysis.txt
- environment/requirements-r06-lock.txt
- environment/r06_environment_import_check.json
- environment/r06_environment_command_check.json

Resolved:
- pandas, scipy, scikit-image, networkx, joblib, and related CPU analysis packages are installed and import successfully.
- R06 validation rerun now reports Critical missing modules: None.

Still limited:
- cupy is installed but not usable until CUDA Toolkit/DLL path/policy are fixed.
- vtk is installed but direct import is blocked by Windows application-control policy.
- open3d is unavailable for Python 3.14 from PyPI.
- FreeCAD/Mesh/Part require system/FreeCAD/conda setup, not ordinary pip.

R06 score remains 76/100 because preview generation + runtime descriptor extraction are still pending.
```

KMK312 environment update:

```text
Chuck later reported TA guidance:
Use KMK312 (Python 3.12.12) for NB-ORIG/NB-CURRENT because of Python-version compatibility.

Interpretation:
- .venv remains useful for support/static analysis/report generation.
- NB-ORIG/NB-CURRENT actual execution, preview generation, and descriptor extraction should be verified under KMK312.
- Do not treat .venv Python 3.14 as the authoritative notebook runtime.

Resolved Codex-session status:
- Chuck provided KMK312.zip.
- Extracted environment path:
  - tools/envs/KMK312
- Use wrapper:
  - tools/run_kmk312_python.cmd
- Registered kernel:
  - display name: KMK312 (Python 3.12.12) - URP4-1
  - kernel name: kmk312-urp4-1
- Do not run tools/envs/KMK312/python.exe directly for serious work; the wrapper/kernel sets the conda-style PATH.
- Core import check passed: tools/envs/KMK312_core_import_check.json
```

R06-20260626-005 completed:

```text
R06 controlled KMK312 preview execution passed.

NB-ORIG was not modified.
Safe lab copy:
- experiments/lab_001_xy_connection_20260626/notebooks/R06_KMK312_preview_safe.ipynb

Generation preview:
- kernel: kmk312-urp4-1
- output root: C:\URP4_R06
- preview candidates: 3
- safe settings:
  - auto_run_generation=False
  - run_generation_mode="none"
  - preview_n=3
  - cpu_workers=1
  - compute_backend="cpu"
- latest generation summary:
  - C:\URP4_R06\R06_KMK312_Preview_260626_225817\R06_KMK312_generation_preview_summary.json

Descriptor staged smoke:
- 7/7 descriptor stages passed on one preview lattice candidate.
- Report:
  - experiments/lab_001_xy_connection_20260626/results/R06_KMK312_runtime_smoke_report.md
- Table:
  - experiments/lab_001_xy_connection_20260626/reports/tables/R06_KMK312_descriptor_stage_smoke.csv

Important timing:
- S02 point_only: about 356 s for one candidate.
- S07 full_light_no_advanced_graph: about 427 s for one candidate.

Interpretation:
- KMK312 runtime is usable.
- Controlled preview generation is safe and fast.
- Descriptor extraction works, but full multi-candidate descriptor extraction is expensive and should be gated/optimized before large runs.
- R06 score: 86/100, pass for controlled preview validation.
```

---

## 7. Active next action

```text
Active: R09-20260701-007E Mass-orientation isolation and representative C/L/F/T generalization before any research-lab-PC true ppt_full run, plus direct STP import planning.
```

P1 result, preserved as completed:

- candidate v0.2 SHA-256: `29131CE5F3D8D59CF6A7211D963A23F85C14F950EA335BBD237B52A7FF76980F`;
- controlled parity: 93/93 pass;
- repeat extraction: 438/438 fields pass;
- three-family E2E: Lattice/TPMS/Voxel 3/3 pass;
- original notebook SHA-256 remains `47AA3889F61D7E4BFBCA37B65286E6B7AD81CF185AB4DD86EBDC263AF5D8B7B7`.

Use for handoff:

```text
experiments/lab_001_xy_connection_20260626/notebooks/R06V2_integrated_legacy_candidate_v0_2.ipynb
experiments/lab_001_xy_connection_20260626/results/R06V2_P1_gate_report.md
experiments/lab_001_xy_connection_20260626/results/R06V2_candidate_v0_2_family_e2e_report.md
```

Current P2 status:

```text
R09 score: 88/100, not passed.

Completed P2 evidence:
- external STL QA: 33/33 load/hash/surface, 32/33 solid/slice;
- B3/C1/L1/F1 supplied-STL pilot reached common descriptors;
- first exact comparison: 0/232 exact matches, now retained only as reproducibility evidence;
- professor y=x/y=a*x similarity rule applied;
- point-global descriptors align strongly;
- slice families remain discrepant;
- PPT-style B3-z direct slice lane implemented.
- 4-family low-cost setting sweep completed; no candidate is strong enough for lab-PC true ppt_full yet.
- B3 one-model formula-lineage replay and quick z/x formula-variant sweep completed; `Thickness` and `Perimeter-to-area` now have stable B3 leading candidates, while `Angle`, `Curvature`, and `Mass orientation` remain unresolved.
- B3 unresolved-family survivor sweep completed; `Angle` and `Curvature` now also have strong B3 candidates, while `Mass orientation` remains unresolved.

PPT-style slice reproduction proof:
- script: experiments/lab_001_xy_connection_20260626/scripts/R09_ppt_slice_setting_reproduction_probe.py
- human summary: experiments/lab_001_xy_connection_20260626/results/R09_ppt_slice_reproduction_summary_20260701.md
- B3-z ppt_layer_smoke: 801 slices, 512 px, 0.05 mm, 73.7 s on Legion;
- B3-z ppt_full_override: 41 slices, 4000 px, 1.0 mm override spacing, 118.7 s on Legion;
- Historical note: true ppt_full 4000x4000x801 was previously expected to be slow. As of `R09-20260703-016A`, 4000px is sensitivity/historical context; current working standard is 1000×1000 px, 801 slices, and area_per_pixel=0.0016 mm²/pixel.
- setting sweep report: experiments/lab_001_xy_connection_20260626/results/R09_ppt_slice_setting_validation_sweep_20260701.md
- B3 formula-variant summary: experiments/lab_001_xy_connection_20260626/results/R09_B3_formula_variant_sweep_20260701_quick_zx_summary.md
- B3 survivor summary: experiments/lab_001_xy_connection_20260626/results/R09_B3_formula_variant_sweep_20260701_007D_survivor_summary.md
```

Read only if reviewing P1 evidence:

```text
outputs/URP4-1_PROFESSOR_PROJECT_ROADMAP_20260629.md
outputs/URP4-1_ROADMAP.md
outputs/input&output.md
experiments/lab_001_xy_connection_20260626/source/URP4-1/Model_generator_260506_descriptor_v5_boundary_symmetry_perfboost.ipynb
experiments/lab_001_xy_connection_20260626/source/URP4-1/*.py
experiments/lab_001_xy_connection_20260626/results/R06_forward_pipeline_validation.md
experiments/lab_001_xy_connection_20260626/results/R06_KMK312_runtime_smoke_report.md
```

Paused but preserved:

- R07 generation assets: historical 82/100 for their prior scope.
- R08 inverse-design scaffold: historical 75/100, not passed.
- Research-PC probes/batches: now allowed for defined R09/P2 heavy slice jobs when machine permission is available.
- Do not start P3/P4/P5 or inverse-design claims until P2 provides a trusted descriptor path.

Latest lab-PC USB update:

```text
R09-20260703-008C
Active USB package: D:\URP4-1_R09_FORENSIC_USB_20260703
Lab-PC doctor failed because KMK312 was missing shapely, rtree, and tabulate.
USB now includes tools\wheelhouse and 00A_FIX_KMK312_PACKAGES.cmd.
Run 00A first on the lab PC, then 01_RUN_B3_Z_FIRST.cmd, then 02_RUN_MAIN_Z_801_B3_C1_F1_L1.cmd.
If doctor still fails after 00A, stop and bring back the full USB folder.
```

Latest result update:

```text
R09-20260703-009
Chuck ran 02_RUN_MAIN_Z_801_B3_C1_F1_L1.cmd on the lab PC.
Doctor PASS and factory 4/4 success.
The previous zero-component MassOri failure is fixed.
Analysis report: experiments/lab_001_xy_connection_20260626/results/R09_LAB_PC_RUN2_MASSORI_801_ANALYSIS_20260703.md
Core result: B3/L1 MassOri average strong, C1 average usable, F1 outlier, all stdev fields unresolved.
Local F1 quick axis/fit probe did not rescue F1.
Do not expand to all 60 families yet.
Next gate: R09-20260703-010 F1/F2 foam source audit.
Need: F2-Foam-Poroelastic_foam.stl from Notion STL ZIP or professor/TA.
Chuck input packet: experiments/lab_001_xy_connection_20260626/results/R09_CHUCK_INPUT_PACKET_F2_STL_20260703.md
Operational note: keep future run tags short because a long tag hit Windows path-length failure.
```

Latest source-audit update:

```text
R09-20260703-010
F2-Foam-Poroelastic_foam.stl was recovered from the Notion STL ZIP and staged into the raw STL folder.
Manifest was updated with the F2 STL row.
F2 MassOri v0.2 run completed under axis=z, 1000px x 801 slices, weighted.
Direct F2 strict Excel comparison has 0 rows because the pilot Excel comparison table currently contains B3/C1/F1/L1 only.
Cross-audit result: Excel F1 MassOri averages are much closer to F2-Poroelastic STL than to F1-Kelvin STL.
Median avg-field relative difference:
- F1 STL -> Excel F1: 9.60%
- F2 STL -> Excel F1: 0.58%
Closer rows: F2 is closer on 6/6 MassOri rows.
Main report: experiments/lab_001_xy_connection_20260626/results/R09_F1_F2_FOAM_SOURCE_AUDIT_20260703.md
Cross-audit table: experiments/lab_001_xy_connection_20260626/reports/tables/R09_F1_F2_foam_source_audit_20260703.csv
Interpretation: F1 outlier is now likely a source/model-family crosswalk issue, not a pure MassOri formula failure.
Do not expand to all families yet.
Next gate: R09-20260703-011 Foam family crosswalk audit.
```

Latest Excel-structure update:

```text
R09-20260703-011
Professor/TA clarification reflected:
- suffixes like B1-1, B1-2 are repeated measured specimens;
- x / -x / "(x axis)" means x-direction or side-face measurement, not a new geometry family by itself;
- F1/F2 manual Excel/file mismatch is unlikely but still possible, so Foam audit remains active.

Do not treat the workbook as one flat table anymore.
Use normalized row roles:
- family_summary
- replicate_sample
- extra_or_late_added

New outputs:
- experiments/lab_001_xy_connection_20260626/results/R09_excel_structure_interpretation_20260703.md
- experiments/lab_001_xy_connection_20260626/reports/tables/R09_excel_row_registry_20260703.csv
- experiments/lab_001_xy_connection_20260626/reports/tables/R09_excel_column_registry_20260703.csv
- experiments/lab_001_xy_connection_20260626/reports/tables/R09_excel_long_table_20260703.csv
- experiments/lab_001_xy_connection_20260626/results/R09_foam_crosswalk_next_plan_20260703.md

Observed normalization:
- family_summary rows: 68
- replicate_sample rows: 131
- extra_or_late_added rows: 5
- directions: z=167, x=34, y=3

Next gate:
R09-20260703-012 Foam summary/replicate MassOri comparison.
Compare F1/F2 STL calculations against F1/F2 family_summary rows, replicate individual rows, and replicate means. Keep MassOri avg and stdev judgments separate.
```

Latest Foam summary/replicate update:

```text
R09-20260703-012
Compared F1_STL and F2_STL MassOri values against Excel F1/F2 family_summary rows, replicate_sample rows, and virtual replicate_mean rows.

New outputs:
- experiments/lab_001_xy_connection_20260626/results/R09_foam_summary_replicate_massori_comparison_20260703.md
- experiments/lab_001_xy_connection_20260626/reports/tables/R09_foam_massori_excel_values_20260703.csv
- experiments/lab_001_xy_connection_20260626/reports/tables/R09_foam_massori_summary_replicate_comparison_20260703.csv
- experiments/lab_001_xy_connection_20260626/reports/tables/R09_foam_massori_summary_replicate_summary_20260703.csv
- experiments/lab_001_xy_connection_20260626/reports/tables/R09_foam_massori_best_source_by_excel_target_20260703.csv

Verified row counts:
- Excel target values: 48
- source-vs-target comparison rows: 96
- summary rows: 24
- best-source vote rows: 48

Key result:
- F1 family_summary avg: F2_STL closer than F1_STL, median relative difference 0.58% vs 9.60%.
- F1 replicate_mean avg: same pattern, F2_STL closer than F1_STL.
- F2 family_summary avg: F2_STL closer than F1_STL, median relative difference 0.88% vs 9.87%.
- F2 replicate_mean avg: same pattern, F2_STL closer than F1_STL.

Interpretation:
F2_STL is closer to both Excel F1 and Excel F2 average fields.
This keeps the F1/F2 crosswalk clue active, but it does not prove a simple F1/F2 swap.
Possible remaining explanations: Foam MassOri avg is weakly discriminative, F1 STL is the wrong revision/source, Excel F1 values were copied/curated, or there is a manual legacy crosswalk issue.
MassOri stdev remains unresolved and should not be used as decisive mapping evidence.

Next gate:
R09-20260703-013 Foam geometry/source discriminability check.
Before all-family expansion, compare non-MassOri descriptors and simple STL geometry metadata for F1/F2.
```

Latest R09/P2 decision-register rule:

```text
R09-20260703-012A
New blackbox decision register:
experiments/lab_001_xy_connection_20260626/results/R09_blackbox_decision_register_20260703.md

From this point forward, every R09/P2 forensic judgment should be tied to a blackbox ID and one of:
- confirmed
- likely
- unresolved
- rejected

Initial blackbox IDs:
- R09-BB-001 Excel row suffix such as B1-1 = repeated specimen: confirmed
- R09-BB-002 x / -x suffix = direction/side-face measurement: confirmed
- R09-BB-003 family_summary vs replicate_sample relationship: unresolved
- R09-BB-004 replicate-row structural x copied vs individually extracted: unresolved
- R09-BB-005 F1/F2 Excel row vs Notion STL/STP mapping: unresolved
- R09-BB-006 MassOri average formula: likely
- R09-BB-007 MassOri stdev definition/population: unresolved
- R09-BB-008 Thickness formula lineage: likely
- R09-BB-009 P-A formula lineage: likely
- R09-BB-010 Angle formula lineage: likely
- R09-BB-011 Curvature formula lineage: likely
- R09-BB-012 x-y learning row choice summary vs replicate: unresolved

Do not silently upgrade likely/unresolved judgments.
Any state change needs explicit evidence and log entry.
Next scientific gate remains:
R09-20260703-013 Foam geometry/source discriminability check.
```

Latest R09/P2 Foam geometry/source update:

```text
R09-20260703-013
Main report:
experiments/lab_001_xy_connection_20260626/results/R09_foam_geometry_source_discriminability_20260703.md

New evidence:
- F1 and F2 staged STL/STP source files are both present.
- F2 STL size is 4.94x F1.
- F2 raw face count is 4.94x F1.
- F2 merged vertex count is 5.64x F1.
- F1/F2 are both watertight single-component solids after duplicate STL vertex merge.
- Surface area and volume are similar in scale, but topology/file complexity is clearly different.
- Low-res non-MassOri slice descriptors distinguish F1/F2:
  - curvature median relative difference: 55.91%
  - perimeter-to-area: 18.90%
  - angle: 14.20%
  - thickness: 7.91%
- Excel F1/F2 structural groups also differ outside MassOri:
  - x_external_slice median relative difference: 27.27%
  - x_internal_heat: 27.44%
  - x_internal_sound: 25.54%

Blackbox status updates:
- R09-BB-005 F1/F2 Excel row vs Notion STL/STP mapping: unresolved -> unresolved
- R09-BB-006 MassOri average formula: likely -> likely
- R09-BB-007 MassOri stdev definition/population: unresolved -> unresolved
- R09-BB-013 F1/F2 staged STL duplicate/identical-source hypothesis: rejected
- R09-BB-014 Non-MassOri descriptors can discriminate staged F1/F2 Foam: likely

Interpretation:
The staged F1/F2 files are not duplicate or identical source meshes.
MassOri average alone is not enough to close the Foam crosswalk issue.
Exact Excel-to-file provenance remains unresolved.

Next gate:
R09-20260703-014 Foam non-MassOri Excel parity probe.
Do not expand to all families yet on MassOri alone.
```

Latest R09/P2 non-MassOri parity update:

```text
R09-20260703-014
Main report:
experiments/lab_001_xy_connection_20260626/results/R09_foam_nonmassori_excel_parity_probe_20260703.md

Question:
Can low-resolution non-MassOri descriptors map F1_STL -> Excel F1 and F2_STL -> Excel F2?

Design:
- compared F1_STL and F2_STL calculated fields against Excel F1/F2;
- used direct non-MassOri fields only:
  - Thickness IP/LIP/LTP avg/stdev
  - Curvature IP/LIP/LTP avg/stdev
  - Angle IP/LIP/LTP avg/stdev
  - P-A IP/LIP/LTP avg/stdev
- excluded Excel AVG/Std columns because aggregation definition is unconfirmed.

Result:
- cross rows: 384
- expected source wins: 18/48
- source wins: F1_STL=18, F2_STL=30
- P-A has very large scale mismatch under this low-resolution/current-lineage probe.

Blackbox status:
- R09-BB-005 remains unresolved.
- R09-BB-006 remains likely.
- R09-BB-007 remains unresolved.
- R09-BB-014 remains likely.
- R09-BB-015 added:
  Low-resolution non-MassOri Excel parity resolves Foam crosswalk = rejected.

Interpretation:
This probe did not resolve Foam mapping.
It shows that low-resolution non-MassOri parity is not decisive enough.

Next:
R09-20260703-015 Decide Foam crosswalk path:
source-provenance question vs higher-fidelity/best-lineage non-MassOri rerun.
```

Latest R09/P2 Foam higher-fidelity update:

```text
R09-20260703-015B
Main report:
experiments/lab_001_xy_connection_20260626/results/R09_foam_hifidelity_rerun_pilot_20260703.md

Question:
If F1/F2 are rerun closer to the professor/PPT slice conditions, does Excel-to-file mapping become clear?

Design:
- compared previous lowres run against 1000px×801 closer-to-PPT run;
- 1000px×801 settings:
  - 40 mm cube
  - 0.05 mm layer height
  - 801 slices
  - fit_max_extent_to_cube
  - endpoint slicing
  - z axis
- 2026-07-03 reinterpretation: 1000px×801 is now the current working standard, not merely a laptop-feasible intermediate; 4000px is sensitivity/historical context.

Result:
- expected source wins improved only from 16/40 to 18/40.
- 1000px×801 source wins: F1_STL=10, F2_STL=30.
- descriptor-family median relative error:
  - angle: 29.85% -> 19.03%
  - mass_orientation: 395.76% -> 39.85%
  - curvature: 68.46% -> 97.09%
  - perimeter_to_area: 2902.61% -> 2348.32%
  - thickness: 91.41% -> 93.77%

Blackbox status:
- R09-BB-005 remains unresolved.
- R09-BB-006 remains likely.
- R09-BB-007 remains unresolved.
- R09-BB-016 added:
  1000px×801 current working-standard rerun resolves Foam crosswalk = rejected.

Interpretation:
Current working-standard settings are useful but do not solve Foam F1/F2 crosswalk by themselves.
Do not run blind all-family/all-descriptor jobs or chase 4000px sensitivity yet.

Next:
R09-20260703-016 Selective high-fidelity/lineage split:
angle selective validation, MassOri isolated, P-A scale/lineage first, curvature/thickness lineage/source investigation.
```

Latest R09/P2 PPT-condition reinterpretation:

```text
R09-20260703-016A
Main report:
experiments/lab_001_xy_connection_20260626/results/R09_ppt_condition_reinterpretation_20260703.md

New working standard:
- 1000×1000 px
- 40 mm × 40 mm = 1600 mm²
- area_per_pixel = 0.0016 mm²/pixel
- layer_height = 0.05 mm
- slice_count = 801
- OpenCV connected component
- min_pixels = 2

Blackbox updates:
- R09-BB-017 1000×1000 px current working standard = confirmed
- R09-BB-018 PPT pillar as OpenCV connected component, min_pixels=2 = likely
- R09-BB-019 IP/LIP/LTP population family = likely
- R09-BB-007 remains unresolved but narrowed
- R09-BB-010 Angle remains likely; area-derived denominator L_eff unresolved
- R09-BB-011 Curvature remains likely; effective L_eff unresolved

Implication:
Do not frame the next task as "just raise to 4000px."
Use the 1000×1000 standard and test component/layer/weighted population plus area-derived L_eff variants first.
```

Latest R09/P2 selective lineage split:

```text
R09-20260704-016B
Main report:
experiments/lab_001_xy_connection_20260626/results/R09-20260704-016B_selective_lineage_split_report_20260704.md

Question:
Does the current PPT slice implementation fully satisfy the updated population/L_eff interpretation?

Answer:
No. It matches working settings, but not all population/formula definitions.

Matches:
- 1000×1000 px
- 801 slices
- 40 mm × 40 mm
- area_per_pixel=0.0016 mm²/pixel
- layer_height=0.05 mm
- OpenCV connected components
- min_pixels=2

Not fully settled:
- IP weighted vs unweighted component pooling
- LTP weighted physical contribution
- Angle area-derived L_eff denominator
- Curvature area/(H×L_eff)

Blackbox update:
- R09-BB-020 added:
  current PPT slice implementation fully satisfies updated population/L_eff interpretation = rejected

Descriptor priority:
1. angle
2. mass_orientation
3. perimeter_to_area
4. curvature
5. thickness

Completed next:
R09-20260704-017 Component-population and L_eff numeric runner.

Current next:
R09-20260704-018B Representative-family stdev survivor validation.
Use the B3 stdev survivor candidates, but do not treat them as canonical until representative-family evidence exists.
```

Latest R09/P2 representative-family stdev validation:

```text
R09-20260705-018B
Main report:
experiments/lab_001_xy_connection_20260626/results/R09-20260705-018B_representative_stdev_survivor_validation_report_20260705.md

Question:
Do the exact B3 MassOri/Curvature stdev survivor candidates generalize to C1/L1/F1/F2?

Answer:
No. They are useful forensic clues, but not global canonical formulas.

Model-level result:
- C1: all 9 tested rows failed
- L1: 2 usable, 1 weak, 6 failed
- F1: 1 strong, 2 weak, 6 failed
- F2: 1 strong, 7 weak, 1 failed

Blackbox update:
- R09-BB-022 changed to rejected:
  exact B3 stdev survivor candidates do not generalize as global canonical formulas.
- R09-BB-023 added as unresolved:
  true MassOri/Curvature stdev legacy definition still needs target decomposition.

Do not expand the exact R09-018A B3 stdev candidates to all families as final formulas.

Current next:
R09-20260705-019 stdev target decomposition and generalized search design.
Use train/validation family splits and separate formula questions from Excel column-lineage/source-provenance questions.
```

Latest R09/P2 generalized stdev forensic search:

```text
R09-20260705-019
Main report:
experiments/lab_001_xy_connection_20260626/results/R09-20260705-019_stdev_target_decomposition_generalized_search_report_20260705.md

Question:
Does the broad current candidate space contain one global MassOri/Curvature stdev formula that survives B3/C1/L1/F1/F2?

Answer:
No.

Search scale:
- Excel stdev targets: 40
- candidate model values: 369,360
- candidate-target comparisons: 1,477,440
- global candidate summaries: 186,624

Global result:
- global_usable: 0
- global_strong: 0
- partial_usable: 609
- partial_weak: 15,020
- failed_generalization: 170,995

Target decomposition:
- 7/8 target columns = per_model_fit_possible_but_not_general
- 1/8 target columns = partial_generalization_unresolved

Interpretation:
Per-model targets can be fit closely, but no single candidate definition survives across all representative families.
This points away from "just search more formulas" and toward Excel column lineage, explicit LIP/LTP stdev population definition, and source provenance.

Blackbox update:
- R09-BB-024 added as rejected:
  current broad candidate space contains one global formula across B3/C1/L1/F1/F2.
- R09-BB-025 added as confirmed:
  stdev targets can be fit closely per model within current candidate space.
- R09-BB-023 remains unresolved but narrowed.

Latest R09/P2 Excel stdev working relabel:

```text
R09-20260706-020A
Main report:
experiments/lab_001_xy_connection_20260626/results/R09-20260706-020A_excel_stdev_ltp_working_relabel_report_20260706.md

Chuck confirmed:
The duplicated LIP-stdev header after each LTP column is a typo.

Working labels from now:
- MassOri U = IP-stdev
- MassOri W = LIP-stdev
- MassOri Y = LTP-stdev
- MassOri AA = Std
- Curvature AC = IP-stdev
- Curvature AE = LIP-stdev
- Curvature AG = LTP-stdev
- Curvature AI = Std

Raw Excel and original registries are not modified.
Use working label tables:
- experiments/lab_001_xy_connection_20260626/reports/tables/R09-20260706-020A_excel_stdev_working_column_map_20260706.csv
- experiments/lab_001_xy_connection_20260626/reports/tables/R09-20260706-020A_excel_long_table_stdev_working_labels_20260706.csv

Blackbox update:
- R09-BB-026 = confirmed

Current next:
R09-20260706-020C stdev formula/population audit under explicit IP/LIP/LTP/Std labels.
Do not run all-family stdev expansion with current formulas as final formulas.
```
```

Latest R09/P2 PPTX interpretation reference:

```text
R09-20260706-020B
Main reference:
experiments/lab_001_xy_connection_20260626/results/R09_PPTX_COMPLETE_INTERPRETATION_20260706.md

Use this as the first reference before interpreting `파라미터 추출법_0724.pptx`.

It consolidates:
- Chuck+AI page-by-page PPTX textification;
- professor/PPT condition reinterpretation;
- 1000×1000 px / 801 slices / 0.05 mm working standard;
- Red/Blue/Purple and connected-component/pillar interpretation;
- descriptor formulas;
- IP/LIP/LTP/Std population hypotheses;
- current confirmed/likely/unresolved/rejected states.

Current next:
R09-20260706-020C stdev formula/population audit using this complete PPTX interpretation as the reference document.
```

Latest R09/P2 stdev population forensic:

```text
R09-20260706-020C
Main report:
experiments/lab_001_xy_connection_20260626/results/R09-20260706-020C_stdev_population_forensic_report_20260706.md

Script:
experiments/lab_001_xy_connection_20260626/scripts/R09_020C_stdev_population_forensic.py

Search:
- targets = 40
- candidate model values = 96,824
- comparisons = 386,984

Result:
- no strict global canonical stdev formula survived
- MassOri U/IP-stdev -> likely component-level
- MassOri W/LIP-stdev -> likely layer-level
- MassOri Y/LTP-stdev -> likely layer-total
- same-column replicate std rejected for current Std explanation
- Curvature AG/LTP-stdev and AI/Std remain unresolved

Blackbox:
- R09-BB-027 = likely
- R09-BB-028 = rejected
- R09-BB-029 = unresolved

Current next:
R09-20260706-020D Curvature LTP/Std source-lineage audit.
Do not run another blind broad sweep before checking LEGACY-PY curvature lineage and L_eff/source provenance.
```

Latest R09/P2 Curvature source-lineage audit:

```text
R09-20260706-020D
Main report:
experiments/lab_001_xy_connection_20260626/results/R09-20260706-020D_curvature_lineage_audit_report_20260706.md

Script:
experiments/lab_001_xy_connection_20260626/scripts/R09_020D_curvature_lineage_audit.py

Question:
Why do Curvature AG/LTP-stdev and AI/Std remain unresolved after the population audit?

Answer:
Curvature is not one source-lineage in the project.

Lineages now separated:
- LEGACY-PY `2._Parameter_result_0727.py` component/layer contact-style curvature
- LEGACY-PY `2._Parameter_result_0727.py` LTP sqrt-total-area curvature
- LEGACY-PY `3._parameter_angle_all_0727.py` weighted component contact curvature
- NB-CURRENT total-contact LTP curvature
- LEGACY-PY `Curvature_Extraction_New.py` mesh surface DDG curvature

Result:
- AG/LTP-stdev likely follows the LEGACY-PY `2._Parameter_result_0727.py` LTP sqrt-total-area family:
  (sqrt(sum_red_area) + sqrt(sum_blue_area)) / (2 * height)
- This clue is strong on B3/C1, usable on L1, weak on F2, but fails F1.
- AI/Std remains unresolved; best candidates are mixed and not one shared formula.
- Surface DDG curvature should not be mixed with overlay AG/AI unless source provenance proves it.

Blackbox:
- R09-BB-030 = confirmed
- R09-BB-031 = likely
- R09-BB-032 = unresolved

Current next:
R09-20260706-020E Curvature AG/AI targeted formula patch/sweep.
Add LEGACY-PY `2._Parameter_result_0727.py` LTP sqrt-total-area as an explicit candidate path, keep NB-CURRENT contact-LTP separate, keep LEGACY-PY `Curvature_Extraction_New.py` surface DDG separate, and retest B3/C1/L1/F1/F2 before all-family expansion.
```

Latest R09/P2 Curvature targeted formula sweep:

```text
R09-20260706-020E
Main report:
experiments/lab_001_xy_connection_20260626/results/R09-20260706-020E_curvature_targeted_formula_sweep_report_20260706.md

Script:
experiments/lab_001_xy_connection_20260626/scripts/R09_020E_curvature_targeted_formula_sweep.py

Purpose:
Do not modify NB-CURRENT yet.
Create evidence for what Curvature formula candidate NB-CURRENT should eventually implement.

Tested:
- LEGACY-PY 2._Parameter_result_0727.py LTP sqrt-total-area
- NB-CURRENT contact-LTP
- R09-SCRIPT area-derived L_eff variants
- LEGACY-PY 3._parameter_angle_all_0727.py weighted component std
- Excel provenance candidates

Search:
- candidate values = 601
- comparisons = 601
- direct y=x and scaled y=a*x both evaluated

Result:
- No single fixed Curvature formula/statistic explains AG/AI across B3/C1/L1/F1/F2.
- NB-CURRENT contact-LTP is rejected as a standalone AG/LTP-stdev explanation.
- LEGACY-PY 2._Parameter_result_0727.py sqrt-total-area remains an important AG lineage clue, but not a confirmed fixed cross-family statistic.
- R09-SCRIPT area-derived L_eff has the best scaled AG trend, but remains unresolved and should not be patched into NB-CURRENT.
- AI/Std remains unresolved; current tested formula/provenance candidates are rejected as explanations.

Blackbox:
- R09-BB-033 = rejected
- R09-BB-034 = rejected
- R09-BB-035 = unresolved
- R09-BB-036 = rejected

Current next:
R09-20260706-020F Curvature AG direct LEGACY-PY parity micro-test.
Do not replace NB-CURRENT Curvature with a canonical patch yet. Compare intermediate per-layer vectors between LEGACY-PY 2._Parameter_result_0727.py, NB-CURRENT contact-LTP, and R09-SCRIPT reconstructed vectors.
```

Latest R09/P2 Curvature AG direct LEGACY-PY parity micro-test:

```text
R09-20260706-020F
Main report:
experiments/lab_001_xy_connection_20260626/results/R09-20260706-020F_curvature_ag_legacy_py_parity_microtest_report_20260706.md

Script:
experiments/lab_001_xy_connection_20260626/scripts/R09_020F_curvature_ag_legacy_py_parity_microtest.py

Purpose:
Do not modify NB-CURRENT.
Confirm exactly what LEGACY-PY `2._Parameter_result_0727.py` computes for Curvature LTP,
then compare that exact per-layer vector against Excel AG/LTP-stdev and NB-CURRENT contact-LTP.

Source-line finding:
- line 85: red area = countNonZero(label_red) * area_per_pixel
- line 86: blue area = countNonZero(label_blue) * area_per_pixel
- line 99: areas = sums of already physical-area arrays
- line 103: LTP = (sqrt(sum_red_area_mm2) + sqrt(sum_blue_area_mm2)) / (2 * height)

State labels:
- R09-BB-037 = confirmed:
  LEGACY-PY-2 LTP uses physical-area sqrt, not raw pixel-count sqrt.
- R09-BB-038 = rejected:
  NB-CURRENT contact-LTP is not vector-equivalent to LEGACY-PY-2 sqrt-area LTP.
- R09-BB-039 = unresolved:
  Excel AG exact parity to LEGACY-PY-2 all-layer std_pop is not globally solved.
- R09-BB-040 = likely:
  F1 is now a likely source/crosswalk/provenance outlier.

Exact LEGACY-PY-2 all-layer AG/std_pop comparison:
- B3: strong, 1.43% diff
- C1: strong, 0.83% diff
- L1: usable, 5.54% diff
- F2: weak, 28.63% diff
- F1: failed, 271.72% diff

Important:
Do not patch NB-CURRENT with contact-LTP.
Carry LEGACY-PY-2 sqrt-area LTP as the leading AG implementation candidate, but do not call it canonical until F1/source provenance and exact execution parity are resolved.

Current next:
R09-20260706-020G F1/source-provenance and exact LEGACY-PY execution parity plan.
Prioritize exact source/provenance and vector-to-vector parity over another broad formula sweep.
```

Latest R09/P2 F1 source/provenance gate:

```text
R09-20260706-020G
Main report:
experiments/lab_001_xy_connection_20260626/results/R09-20260706-020G_f1_source_provenance_exact_legacy_py_parity_report_20260706.md

Script:
experiments/lab_001_xy_connection_20260626/scripts/R09_020G_f1_source_provenance_exact_legacy_py_parity.py

Purpose:
Do not modify NB-CURRENT.
Decide whether F1 Curvature AG/LTP-stdev failure should trigger a formula patch,
or whether source/crosswalk/provenance must be audited first.

Results:
- F1/F2 current staged STL/STP files exist and match current manifest hashes.
- F1/F2 checked replicate descriptor rows duplicate family_summary values for MassOri/Curvature slice columns.
- LEGACY-PY-2 reconstructed AG:
  - F1 staged source -> Excel F1 AG: failed, rel_diff = 2.717
  - F2 staged source -> Excel F1 AG: usable, rel_diff = 0.067
  - F2 staged source -> Excel F2 AG: weak, rel_diff = 0.286
- Direct LEGACY-PY image execution is blocked because no F1/F2 color-combine PNG folder is currently available.

State labels:
- R09-BB-041 = confirmed:
  current F1/F2 staged source file presence and identity.
- R09-BB-042 = confirmed:
  F1/F2 checked replicate rows are duplicate summary evidence, not independent descriptor evidence.
- R09-BB-043 = likely:
  F1 AG failure is more likely source/crosswalk/provenance risk than immediate formula patch trigger.
- R09-BB-044 = unresolved:
  exact direct LEGACY-PY image execution parity requires PNG folders.

Important:
Do not patch NB-CURRENT solely to fit F1.
Keep LEGACY-PY `2._Parameter_result_0727.py` sqrt-total-area LTP as leading AG formula lineage.

Current next:
R09-20260706-020H direct LEGACY-PY image execution adapter / color-combine PNG source generation.
```

Latest R09/P2 direct LEGACY-PY PNG execution gate:

```text
R09-20260707-020H
Main report:
experiments/lab_001_xy_connection_20260626/results/R09-20260707-020H_direct_legacy_py_image_execution_report_20260707.md

Night preflight summary:
experiments/lab_001_xy_connection_20260626/results/R09-20260707-020H_all_staged_night_preflight_summary_20260707.md

Script:
experiments/lab_001_xy_connection_20260626/scripts/R09_020H_direct_legacy_py_image_execution.py

Run helper:
experiments/lab_001_xy_connection_20260626/scripts/R09_020H_RUN_ALL_STAGED.cmd

Purpose:
Do not modify NB-CURRENT.
Generate current color-combine PNG folders from staged STL models,
run LEGACY-PY `2._Parameter_result_0727.py::massorientation_curvature()` directly,
and separate PNG-adapter/runtime issues from Excel/source/formula mismatch issues.

Results:
- All 33 staged STL model IDs completed direct LEGACY-PY execution with zero failures.
- Generated/reused 26,400 PNGs at:
  - z axis
  - 1000×1000 px
  - 801 slices / 800 adjacent-layer pairs
  - cube = 40 mm
  - layer height = 0.05 mm
  - area_per_pixel = 0.0016 mm²
- PNG cache size ≈ 0.87 GB.
- Direct-vs-CSV/layer_raw LTP parity is confirmed for B3/C1/L1/F1/F2.
- Direct-vs-Excel remains mixed/unresolved:
  - strong = 4
  - usable = 33
  - weak = 60
  - failed = 131

State labels:
- R09-BB-044 = confirmed:
  direct LEGACY-PY image execution is feasible on current generated PNGs.
- R09-BB-045 = confirmed:
  all-staged current PNG generation coverage.
- R09-BB-046 = confirmed:
  direct LEGACY-PY PNG vs CSV/layer_raw LTP parity.
- R09-BB-047 = unresolved:
  direct LEGACY-PY PNG vs Excel global parity.
- R09-BB-048 = unresolved:
  MassOri stdev current direct execution vs Excel.

Important:
Do not patch NB-CURRENT yet.
Use 020H as the current generated-PNG direct LEGACY-PY baseline.
Continue using CSV/layer_raw for fast LTP-level formula forensics.
Treat remaining Excel mismatches as source/provenance, direction/replicate convention, or descriptor-specific formula/population issues.
Keep Curvature AG/LTP-stdev and MassOri stdev separate.

Current next:
R09-20260707-020I Excel mismatch bucketization.
Classify direct-vs-Excel mismatches into source/provenance likely, direction/replicate convention likely, formula/population likely, and unresolved.
```

Latest R09/P2 Excel mismatch triage:

```text
R09-20260707-020I
Main report:
experiments/lab_001_xy_connection_20260626/results/R09-20260707-020I_excel_mismatch_bucketization_report_20260707.md

Script:
experiments/lab_001_xy_connection_20260626/scripts/R09_020I_excel_mismatch_bucketization.py

Purpose:
Do not modify NB-CURRENT.
Take the 020H direct LEGACY-PY PNG-vs-Excel comparison and bucketize mismatches before formula patching.

Results:
input_rows = 228
B01 direction_variant_not_comparable_to_z_run = 36
B02 near_match_validation_anchor = 36
B03 foam_source_provenance_likely = 12
B04 massori_stdev_formula_population_likely = 78
B05 curvature_ag_lineage_near_solved_or_outlier = 22
B06 curvature_ip_lip_population_likely = 44

State labels:
- R09-BB-049 = confirmed:
  x-direction Excel rows are not apples-to-apples evidence against z-axis direct LEGACY-PY runs.
- R09-BB-050 = confirmed:
  strong/usable non-direction z rows are validation anchors.
- R09-BB-051 = confirmed:
  020I bucketization is the current mismatch triage layer.
- R09-BB-052 = likely:
  Curvature AG/LTP has anchors and near-lineage rows, but outliers remain.

Important:
Do not patch NB-CURRENT from x-direction rows, Foam outliers, or MassOri stdev rows.
Use the 020I bucketized CSV to choose narrow next runs.

Current next:
R09-20260707-020J Curvature AG/LTP-stdev source/provenance split and anchor/outlier table.
```

Latest R09/P2 visualization protocol:

```text
R09-20260707-020I-VIS
Main report:
experiments/lab_001_xy_connection_20260626/results/R09-20260707-020I-VIS_yx_visualization_pack_report_20260707.md

Protocol:
experiments/lab_001_xy_connection_20260626/results/R09_yx_visualization_protocol_20260707.md

Script:
experiments/lab_001_xy_connection_20260626/scripts/R09_020I_yx_visualization_pack.py

Purpose:
Do not modify NB-CURRENT.
Convert comparable validation rows into y-x visual artifacts so Chuck can inspect progress visually.

Axis convention:
x = current/direct LEGACY-PY value
y = Excel value

Created figures:
- reports/figures/R09-20260707-020I-VIS_all_rows_log_20260707.png
- reports/figures/R09-20260707-020I-VIS_facet_descriptor_population_20260707.png
- reports/figures/R09-20260707-020I-VIS_curvature_ltp_focus_20260707.png
- reports/figures/R09-20260707-020I-VIS_massori_stdev_focus_20260707.png
- reports/figures/R09-20260707-020I-VIS_bucket_counts_20260707.png

Key results:
input_rows = 228
plot_count = 5
metric_group_count = 12

State labels:
- R09-BB-048 = unresolved:
  MassOri stdev formula search is exhausted enough for now, but column-lineage/provenance/population definition remains unresolved.
- R09-BB-053 = confirmed:
  major R09 validation updates should include y=x / y=a*x plots and fit metrics whenever comparable current/reference values exist.

Important:
Do not restart blind MassOri stdev broad sweeps.
Do not count x-direction rows as z-axis formula failures.
Do not patch NB-CURRENT from Foam outliers.
Keep Curvature AG/LTP-stdev and MassOri stdev separate.

Current next:
1. R09-20260707-020J Curvature AG/LTP-stdev source/provenance split and anchor/outlier table.
2. R09-20260707-020K MassOri stdev column-lineage/provenance/population audit.
```

Latest R09/P2 Curvature AG/LTP split:

```text
R09-20260707-020J
Main report:
experiments/lab_001_xy_connection_20260626/results/R09-20260707-020J_curvature_ag_anchor_outlier_split_report_20260707.md

Script:
experiments/lab_001_xy_connection_20260626/scripts/R09_020J_curvature_ag_anchor_outlier_split.py

Purpose:
Do not modify NB-CURRENT.
Split Curvature AG/LTP-stdev into anchors, near-lineage rows, outliers, direction holdouts, and Foam source/provenance holdouts.

Results:
J01 validation anchors = 8
J02 near-lineage 5-10% = 12
J03 upper weak 10-20% = 4
J04 z non-Foam outliers 20-50% = 5
J05 z non-Foam extreme outlier >50% = 1
J06 x-direction holdouts = 6
J07 Foam provenance holdouts = 2

Key metric:
z_nonfoam_anchor_plus_near_0_10:
  n = 20
  slope_origin_y_eq_a_x ≈ 1.004
  R² ≈ 0.94
  median_abs_rel_to_y_eq_x ≈ 0.0567

State labels:
- R09-BB-052 = likely:
  Curvature AG/LTP has anchors and near-lineage rows but is not solved.
- R09-BB-054 = likely:
  Curvature AG/LTP anchor-plus-near-lineage core supports LEGACY-PY-2 physical-area sqrt-total-area LTP lineage.
- R09-BB-055 = unresolved:
  C12/L5/L8/L2/B5/C8 remain true z/non-Foam outlier audit targets.

Important:
Curvature AG/LTP is the strongest current descriptor lane, but not canonical yet.
Do not patch NB-CURRENT from the AG lane until outliers are audited or explicitly held out.
Use J01/J02 rows as guardrails/support.
Exclude x-direction rows from z-axis formula claims.
Hold Foam rows for source/provenance.

Latest completed:
R09-20260707-020K MassOri stdev column-lineage/provenance/population audit.

Report:
experiments/lab_001_xy_connection_20260626/results/R09-20260707-020K_massori_stdev_lineage_audit_report_20260707.md

Key outputs:
experiments/lab_001_xy_connection_20260626/scripts/R09_020K_massori_stdev_lineage_audit.py
experiments/lab_001_xy_connection_20260626/reports/tables/R09-20260707-020K_population_summary_20260707.csv
experiments/lab_001_xy_connection_20260626/reports/tables/R09-20260707-020K_mapping_permutation_summary_20260707.csv
experiments/lab_001_xy_connection_20260626/reports/figures/R09-20260707-020K_massori_core_yx_20260707.png
experiments/lab_001_xy_connection_20260626/reports/figures/R09-20260707-020K_massori_ratio_heatmap_20260707.png

020K result:
- 114 MassOri stdev rows audited across 32 model IDs.
- all_massori: slope Excel/current ≈ 0.652, R² ≈ -0.024, median relative difference ≈ 0.358.
- core z non-Foam: slope Excel/current ≈ 0.801, R² ≈ 0.110, median relative difference ≈ 0.260.
- simple global U/W/Y column swap is rejected as the main explanation.
- 020C population-lineage clues remain likely:
  - U/IP ≈ component-level;
  - W/LIP ≈ layer-level;
  - Y/LTP ≈ layer-total.
- current direct generated-PNG versus Excel MassOri parity remains unresolved.
- AA/Std remains unresolved and separate from U/W/Y.

State labels:
- R09-BB-056 = likely:
  MassOri U/W/Y population lineage is likely but not confirmed.
- R09-BB-057 = rejected:
  simple global MassOri U/W/Y column swap is not the main explanation.
- R09-BB-058 = unresolved:
  current MassOri generated-PNG direct-vs-Excel mismatch remains source/population/provenance unresolved.
- R09-BB-059 = unresolved:
  MassOri AA/Std definition remains separate and unresolved.

Current next:
1. R09-20260707-020L exact MassOri raw-population extraction adapter / 020C candidate replay on generated image intermediates.
2. Optional R09-20260707-020J2 Curvature AG outlier root-cause probe for C12/L5/L8/L2/B5/C8.
```

Latest completed:

```text
R09-20260707-020L
MassOri exact raw-population replay / 020C candidate replay on generated image intermediates.

Report:
experiments/lab_001_xy_connection_20260626/results/R09-20260707-020L_massori_exact_population_replay_report_20260707.md

Script:
experiments/lab_001_xy_connection_20260626/scripts/R09_020L_massori_exact_population_replay.py

Key figures:
experiments/lab_001_xy_connection_20260626/reports/figures/R09-20260707-020L_direct_vs_strict_best_yx_20260707.png
experiments/lab_001_xy_connection_20260626/reports/figures/R09-20260707-020L_fixed_candidates_yx_20260707.png
experiments/lab_001_xy_connection_20260626/reports/figures/R09-20260707-020L_rel_error_comparison_20260707.png

020L result:
- Replay coverage currently has component/layer raw data for 5 models:
  B3, C1, L1, F1, F2.
- 020H generated PNG/direct coverage exists for 33 staged STL IDs, but full 33-model raw-population replay still needs KMK312/OpenCV component_raw export or saved raw tables.
- Direct LEGACY-PY plain MassOri stdev is rejected for representative Excel parity:
  U median relative error ≈ 5.476
  W median relative error ≈ 1.945
  Y median relative error ≈ 1.939
- Per-model strict best candidates fit U/W/Y much better:
  U ≈ 0.0249
  W ≈ 0.0593
  Y ≈ 0.000791
  AA ≈ 0.792
- Fixed global candidate replay is still weak:
  U ≈ 0.132
  W ≈ 0.191
  Y ≈ 0.149
  AA ≈ 0.893

State labels:
- R09-BB-056 = likely:
  MassOri U/W/Y population lineage remains likely but not confirmed.
- R09-BB-060 = rejected:
  direct LEGACY-PY plain MassOri stdev is not the Excel parity formula for the representative replay set.
- R09-BB-061 = unresolved:
  one fixed MassOri statistic/filter family is not yet found.
- R09-BB-062 = unresolved:
  full 33-model raw-population replay coverage requires KMK312/OpenCV export.

Important:
Do not patch NB-CURRENT from 020L alone.
Treat per-model strict best as overfit diagnostics, not canonical formulas.
Keep AA/Std separate from U/W/Y.

Current next:
1. R09-20260707-020M MassOri candidate-family clustering / fixed-formula narrowing.
2. KMK312/OpenCV all-model component_raw export from 020H generated PNGs if Chuck wants production-scale validation first.
3. Optional R09-20260707-020J2 Curvature AG outlier root-cause probe for C12/L5/L8/L2/B5/C8.
```

Latest completed:

```text
R09-20260707-020M
MassOri candidate-family clustering / fixed-formula narrowing.

Report:
experiments/lab_001_xy_connection_20260626/results/R09-20260707-020M_massori_candidate_family_clustering_report_20260707.md

Script:
experiments/lab_001_xy_connection_20260626/scripts/R09_020M_massori_candidate_family_clustering.py

Key tables:
experiments/lab_001_xy_connection_20260626/reports/tables/R09-20260707-020M_population_semantic_conflict_20260707.csv
experiments/lab_001_xy_connection_20260626/reports/tables/R09-20260707-020M_rule_cluster_summary_20260707.csv
experiments/lab_001_xy_connection_20260626/reports/tables/R09-20260707-020M_model_target_best_matrix_20260707.csv
experiments/lab_001_xy_connection_20260626/reports/tables/R09-20260707-020M_decision_table_20260707.csv

Key figures:
experiments/lab_001_xy_connection_20260626/reports/figures/R09-20260707-020M_semantic_conflict_20260707.png
experiments/lab_001_xy_connection_20260626/reports/figures/R09-20260707-020M_model_target_strict_best_heatmap_20260707.png
experiments/lab_001_xy_connection_20260626/reports/figures/R09-20260707-020M_rule_cluster_error_bars_20260707.png

020M result:
- Input comparison rows = 109,328.
- Fixed candidate rows = 21,872.
- Rule cluster rows = 2,288.
- U/IP-stdev:
  expected population = component_level;
  numeric best and semantic best agree;
  best semantic fixed median_rel ≈ 0.132;
  state = likely_partial.
- W/LIP-stdev:
  expected population = layer_level;
  numeric best uses component_level;
  best numeric median_rel ≈ 0.160;
  best semantic median_rel ≈ 0.191;
  state = unresolved semantic conflict.
- Y/LTP-stdev:
  expected population = layer_total;
  best semantic median_rel ≈ 0.149;
  max_rel ≈ 12.168;
  state = unresolved source/outlier-sensitive.
- AA/Std:
  tested summary-level candidates median_rel ≈ 0.893;
  tested summary candidates rejected;
  true definition remains unresolved.
- Best all5 shared U/W/Y rule:
  trimmed_std_1_99||trimmed||trim0__weight_ge_6;
  median_rel ≈ 0.199;
  max_rel ≈ 11.833;
  failed = 6/15;
  worst = F1/Y;
  state = unresolved.

State labels:
- R09-BB-063 = likely:
  MassOri U/IP component-level lane is likely_partial.
- R09-BB-064 = unresolved:
  MassOri W/LIP semantic population conflict.
- R09-BB-065 = rejected:
  tested MassOri AA/Std summary-level candidates rejected; true AA definition still unresolved under R09-BB-059.
- R09-BB-066 = unresolved:
  one shared all5 U/W/Y statistic-filter rule is not canonical.

Important:
Do not patch NB-CURRENT from MassOri stdev evidence.
Do not collapse U/W/Y/AA into one stdev problem.
Keep AA/Std separate from U/W/Y.

Current next:
1. R09-20260707-020N MassOri W/LIP and Y/LTP source/population split.
2. KMK312/OpenCV all-model component_raw export if production-scale validation is preferred first.
3. Optional R09-20260707-020J2 Curvature AG outlier root-cause probe.
```
## Latest handoff override — 2026-07-07 R09-20260707-020N

Use this block as the current R09/P2 handoff if older “Latest completed” sections conflict.

Latest completed:

```text
R09-20260707-020N
MassOri W/LIP and Y/LTP source/population split.
```

Primary report:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260707-020N_massori_w_y_source_population_split_report_20260707.md
```

Script:

```text
experiments/lab_001_xy_connection_20260626/scripts/R09_020N_massori_w_y_source_population_split.py
```

Key figures:

```text
experiments/lab_001_xy_connection_20260626/reports/figures/R09-20260707-020N_w_y_excel_direct_pair_audit_20260707.png
experiments/lab_001_xy_connection_20260626/reports/figures/R09-20260707-020N_w_y_population_scope_bars_20260707.png
experiments/lab_001_xy_connection_20260626/reports/figures/R09-20260707-020N_w_y_leave_one_out_heatmap_20260707.png
experiments/lab_001_xy_connection_20260626/reports/figures/R09-20260707-020N_w_y_best_scope_yx_20260707.png
```

020N result:

```text
Excel W/Y near-duplicate relation:
  likely.
  B3, F1, F2, L1 have W≈Y within 0.5%.
  C1 is distinct with W/Y≈0.826.

W/LIP nonF1 layer-total/LTP-like lane:
  likely clue, not confirmed.
  median_rel≈0.104, max_rel≈0.251.

Y/LTP layer-total lane:
  unresolved/source-sensitive.
  median_rel≈0.0899, max_rel≈0.876.

NB-CURRENT MassOri stdev patch:
  rejected for now.
```

Current next:

```text
1. R09-20260707-020O MassOri W/Y column-lineage and C1/F1 holdout audit.
2. KMK312/OpenCV all-model component_raw export if production-scale validation is preferred.
3. Keep NB-CURRENT unchanged for MassOri stdev.
```
## Latest handoff override — 2026-07-07 R09-20260707-020O

Use this block as the current R09/P2 handoff if older “Latest completed” sections conflict.

Latest completed:

```text
R09-20260707-020O
MassOri W/Y column-lineage and C1/F1 holdout audit.
```

Primary report:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260707-020O_massori_w_y_column_lineage_holdout_audit_report_20260707.md
```

Script:

```text
experiments/lab_001_xy_connection_20260626/scripts/R09_020O_massori_w_y_column_lineage_holdout_audit.py
```

Key figures:

```text
experiments/lab_001_xy_connection_20260626/reports/figures/R09-20260707-020O_excel_w_y_all_rows_20260707.png
experiments/lab_001_xy_connection_20260626/reports/figures/R09-20260707-020O_direct_w_y_all_models_20260707.png
experiments/lab_001_xy_connection_20260626/reports/figures/R09-20260707-020O_direct_excel_focus_b3_c1_f1_f2_l1_20260707.png
experiments/lab_001_xy_connection_20260626/reports/figures/R09-20260707-020O_summary_replicate_copy_audit_20260707.png
```

020O result:

```text
Excel W/Y global copy hypothesis:
  rejected.
  W/Y near-duplicate within 0.5% = 68/196 rows.
  family_summary near-duplicate within 0.5% = 24/68 rows.

Direct LEGACY-PY LIP/LTP coupling:
  strong but not global.
  near-duplicate within 0.5% = 13/33 models.
  close within 5% = 25/33 models.

Excel summary→replicate MassOri stdev x copy:
  confirmed for parsed U/W/Y/AA fields.
  exact-equal pairs = 118/118.

C1:
  likely true W/Y distinct holdout.

F1:
  likely source/provenance risk.

NB-CURRENT:
  keep unchanged for MassOri stdev.
```

Current next:

```text
1. Optional R09-20260707-020P broad descriptor summary→replicate x-copy audit.
2. C1/F1 source and row-lineage audit.
3. KMK312/OpenCV all-model component_raw export if production-scale MassOri replay is prioritized.
```
## Latest handoff override — 2026-07-07 R09-20260707-020P

Use this block as the current R09/P2 handoff if older “Latest completed” sections conflict.

Latest completed:

```text
R09-20260707-020P
Broad descriptor summary→replicate x-copy audit.
```

Primary report:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260707-020P_broad_descriptor_summary_replicate_xcopy_audit_report_20260707.md
```

Script:

```text
experiments/lab_001_xy_connection_20260626/scripts/R09_020P_broad_descriptor_summary_replicate_xcopy_audit.py
```

Key figures:

```text
experiments/lab_001_xy_connection_20260626/reports/figures/R09-20260707-020P_x_numeric_copy_rate_by_group_20260707.png
experiments/lab_001_xy_connection_20260626/reports/figures/R09-20260707-020P_x_pair_copy_rate_hist_20260707.png
experiments/lab_001_xy_connection_20260626/reports/figures/R09-20260707-020P_x_vs_y_control_copy_rate_context_20260707.png
```

020P result:

```text
Numeric structural descriptor x values:
  confirmed copied from family summary rows to replicate rows.
  present-in-both numeric x exact equal = 17,936 / 17,936.

Replicate pairs with numeric x:
  118 / 118 all exact copied.

y-control values:
  0 / 4,383 comparable cells exact equal.

Maxwell:
  lower replicate block is a layout artifact/missing-x case.
  do not use Maxwell lower-block differences as formula evidence.

Modeling implication:
  replicate rows are not independent x feature vectors.
  treat them as repeated y/specimen rows sharing copied x unless raw provenance proves otherwise.

NB-CURRENT:
  keep unchanged.
```

Current next:

```text
1. Create/update x-y modeling policy document before R05/R08 modeling resumes.
2. Confirm y replicate semantics and units.
3. Continue C1/F1 source/provenance audit or all-model component_raw export.
```

## Latest handoff override — 2026-07-07 R09-20260707-020Q

Use this block as the current R09/P2 handoff if older “Latest completed” sections conflict.

Latest completed:

```text
R09-20260707-020Q
x-y modeling policy after x-copy audit.
```

Primary report:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260707-020Q_xy_modeling_policy_after_xcopy_audit_20260707.md
```

020Q result:

```text
020P proved:
  numeric structural descriptor x values are copied from family summary rows to replicate rows.

020Q policy:
  replicate rows are rejected as independent x feature vectors.

Default leakage-safe group_id:
  family_id + direction.

Rejected:
  random row split / random replicate split for R05/R08.

First approved baseline:
  family/direction-level aggregated y.

Allowed secondary baseline:
  replicate-level y only with grouped validation and sample_weight = 1/n_replicates_in_group.

NB-CURRENT:
  keep unchanged.
```

Current next:

```text
1. R09-20260707-020R y replicate semantics and target-selection audit.
2. Confirm first official y target, units, row role, aggregation policy, and inclusion/exclusion rules.
3. After 020R, resume leakage-safe R05 baseline modeling or continue C1/F1/source provenance depending on target readiness.
```

## Latest handoff override — 2026-07-07 R09-20260707-020R

Use this block as the current R09/P2 handoff if older “Latest completed” sections conflict.

Latest completed:

```text
R09-20260707-020R
y replicate semantics and target-selection audit.
```

Primary report:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260707-020R_y_replicate_semantics_target_selection_audit_report_20260707.md
```

020R result:

```text
Numeric y cells audited:
  3,059

Y columns audited:
  43

Y row semantics:
  y_compression_raw = family-summary-heavy in current normalized table
  y_compression_summary = family-summary-heavy in current normalized table
  y_thermal = family-summary-heavy in current normalized table
  y_vibration = family_summary + replicate_sample values, especially FRF AVG channels

Top data-readiness candidates:
  GP/GR/GT/GV vibration FRF AVG columns

Important:
  data-readiness ranking is not official scientific target selection.
```

Current next:

```text
1. R09-20260707-020S official y-target selection packet / R05 baseline dataset builder.
2. Choose primary y target and optional secondary y target.
3. For selected target, define objective direction, unit convention, aggregation rule, grouped split rule, and row exclusions.
4. Then build the first leakage-safe R05 baseline dataset.
```

## Latest handoff override — 2026-07-07 R09-20260707-020S

Use this block as the current R09/P2 handoff if older “Latest completed” sections conflict.

Latest completed:

```text
R09-20260707-020S
official y-target selection packet / R05 baseline dataset builder.
```

Primary report:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260707-020S_official_y_target_selection_packet_20260707.md
```

Chuck input packet:

```text
experiments/lab_001_xy_connection_20260626/results/R09_CHUCK_INPUT_PACKET_Y_TARGET_SELECTION_20260707.md
```

020S result:

```text
Target options prepared:
  YT-COMP-SEA
  YT-COMP-STRENGTH
  YT-COMP-STIFFNESS
  YT-THERM-CONDUCTIVITY
  YT-THERM-TRANSIENT
  YT-VIB-FRF-AVG
  YT-VIB-DAMPING
  YT-MULTI-OBJECTIVE

Decision:
  Do not choose official y target automatically from data-readiness ranking.

Current blocker:
  Chuck/professor must choose primary y target and modeling direction.
```

Current next:

```text
1. Chuck asks professor/TA or chooses first official target using R09_CHUCK_INPUT_PACKET_Y_TARGET_SELECTION_20260707.md.
2. Once answered, run R09-20260707-020T build selected R05 leakage-safe baseline dataset.
3. If waiting for professor, continue safe parallel work: C1/F1 source provenance, descriptor confidence filtering, or all-model component_raw export.
```

## Latest handoff override — 2026-07-08 R09-20260708-020T_ALL_Y_XY_ATLAS planned

Use this block as the current R09/P2 handoff if older “Latest completed” or “Current next” sections conflict.

Latest completed planning update:

```text
R09-20260708 roadmap correction and 020T_ALL_Y_XY_ATLAS planning.
```

Plan document:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260708-020T_ALL_Y_XY_ATLAS_plan_20260708.md
```

Output schema:

```text
experiments/lab_001_xy_connection_20260626/reports/tables/R09-20260708-020T_ALL_Y_XY_ATLAS_output_schema_20260708.csv
```

Corrected interpretation:

```text
020S:
  y candidate / decision packet.

Not allowed:
  020S -> automatically choose one y -> selected-y model.

Current active next:
  R09-20260708-020T_ALL_Y_XY_ATLAS.

Purpose:
  inspect all candidate y variables,
  map x -> y relationship feasibility,
  rank y candidates by readiness and x-explainability,
  then choose selected-y for R05.
```

Corrected next sequence:

```text
020T_ALL_Y_XY_ATLAS
→ 020U_SELECTED_Y_R05_BASELINE
→ 020V selected-y x->y baseline model
→ 020W selected-y inverse-search y->x pilot
```

Current next action:

```text
Execute R09-20260708-020T_ALL_Y_XY_ATLAS.
```

## Latest handoff override — 2026-07-08 R09-20260708-020T_ALL_Y_XY_ATLAS completed

Use this block as the current R09/P2 handoff if older “Latest completed” or “Current next” sections conflict.

Latest completed:

```text
R09-20260708-020T_ALL_Y_XY_ATLAS
all-y x->y relationship atlas.
```

Primary report:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260708-020T_ALL_Y_XY_ATLAS_report_20260708.md
```

Key outputs:

```text
experiments/lab_001_xy_connection_20260626/reports/tables/R09-20260708-020T_ALL_Y_XY_ATLAS_y_readiness_20260708.csv
experiments/lab_001_xy_connection_20260626/reports/tables/R09-20260708-020T_ALL_Y_XY_ATLAS_x_feature_readiness_20260708.csv
experiments/lab_001_xy_connection_20260626/reports/tables/R09-20260708-020T_ALL_Y_XY_ATLAS_xy_preliminary_metrics_20260708.csv
experiments/lab_001_xy_connection_20260626/reports/tables/R09-20260708-020T_ALL_Y_XY_ATLAS_recommendations_20260708.csv
experiments/lab_001_xy_connection_20260626/reports/figures/R09-20260708-020T_ALL_Y_XY_ATLAS_top_xy_scatter_examples_20260708.svg
```

020T result:

```text
Eligible family/direction groups: 74
X feature candidates in registry: 158
X features included in atlas: 157
High/likely confidence X included: 133
Y variables with numeric values: 43
X-Y metric rows generated: 6751
```

Candidate interpretation:

```text
GP:
  best data-ready / vibration / first-MVP candidate.

GH:
  current best compression candidate among 020S official target-option columns.

GN:
  current best thermal candidate among 020S official target-option columns,
  but objective direction is unresolved.
```

Hard guardrail:

```text
020T is exploratory x->y atlas work.
It does not select the official y target automatically.
It does not authorize inverse design.
It does not authorize NB-CURRENT edits.
Random row split remains forbidden.
```

Current next:

```text
1. Chuck/professor choose the primary y target and exact Excel column.
2. Define objective direction, row policy, direction-variant policy, and source-risk exclusions.
3. Then run R09-20260708-020U_SELECTED_Y_R05_BASELINE.
```

If target choice is delayed:

```text
Continue safe parallel work:
  source provenance audit,
  x-confidence filtering,
  C1/F1 source-risk follow-up,
  or descriptor-row audit.
```

## Latest handoff override — 2026-07-08 R09-20260708-020TA_X_X_DESCRIPTOR_RELATION_ATLAS completed

Use this block as the current R09/P2 handoff if older “Latest completed” or “Current next” sections conflict.

Latest completed:

```text
R09-20260708-020T_ABCD_RESEARCH_ATLAS_INSERTION
R09-20260708-020TA_X_X_DESCRIPTOR_RELATION_ATLAS
```

Inserted route before selected-y baseline:

```text
020T completed:
  all-y x->y relationship atlas

020T-A completed:
  x-x descriptor relation atlas

020T-B next:
  y-y performance relation atlas

020T-C:
  family-aware x-y atlas refinement

020T-D:
  experiment design matrix and selected-y decision basis

020U:
  selected-y R05 leakage-safe baseline dataset
```

Primary 020T-A report:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260708-020TA_X_X_DESCRIPTOR_RELATION_ATLAS_report_20260708.md
```

Roadmap insertion plan:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260708-020T_ABCD_RESEARCH_ATLAS_INSERTION_PLAN_20260708.md
experiments/lab_001_xy_connection_20260626/reports/tables/R09-20260708-020T_ABCD_stage_registry_20260708.csv
```

020T-A result:

```text
family/direction groups: 74
included x features: 157
likely-confidence included x features: 133
unresolved included x features: 24
correlation pair rows: 12246
strong pairs |Spearman| >= 0.75: 523
high-redundancy cluster edges |Spearman| >= 0.90: 128
x feature clusters: 81
multi-feature redundancy clusters: 40
```

Current decision:

```text
Do not proceed directly to 020U yet.
020U now requires 020T-B, 020T-C, and 020T-D or an explicit override.
```

Current next:

```text
R09-20260708-020TB_Y_Y_PERFORMANCE_RELATION_ATLAS
```

Hard guardrail:

```text
Original Excel, NB-CURRENT, and LEGACY-PY remain unchanged.
No inverse-design claim.
No random row split.
No automatic y selection.
Do not use "main notebook"; use LEGACY-PY, NB-ORIG, NB-CURRENT, R09-SCRIPT.
```

## Latest handoff override — 2026-07-08 R09-20260708-020TB_Y_Y_PERFORMANCE_RELATION_ATLAS completed

Use this block as the current R09/P2 handoff if older “Latest completed” or “Current next” sections conflict.

Latest completed:

```text
R09-20260708-020TB_Y_Y_PERFORMANCE_RELATION_ATLAS
```

Primary report:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260708-020TB_Y_Y_PERFORMANCE_RELATION_ATLAS_report_20260708.md
```

Key outputs:

```text
experiments/lab_001_xy_connection_20260626/reports/tables/R09-20260708-020TB_y_y_correlation_pairs_20260708.csv
experiments/lab_001_xy_connection_20260626/reports/tables/R09-20260708-020TB_y_target_group_registry_20260708.csv
experiments/lab_001_xy_connection_20260626/reports/tables/R09-20260708-020TB_y_representative_target_candidates_20260708.csv
experiments/lab_001_xy_connection_20260626/reports/tables/R09-20260708-020TB_y_tradeoff_candidates_20260708.csv
experiments/lab_001_xy_connection_20260626/reports/tables/R09-20260708-020TB_y_row_policy_by_target_group_20260708.csv
```

020T-B result:

```text
family/direction groups: 74
y variables: 43
y-y pair rows: 903
strong y-y pairs |Spearman| >= 0.65: 113
high y-y cluster edges |Spearman| >= 0.85: 51
near-duplicate y-y pairs |Spearman| >= 0.95: 13
y target groups: 21
multi-y target groups: 8
possible/weak trade-off candidates: 12
objective-direction-unresolved y variables: 18
```

Current decision:

```text
Selected-y must be chosen from target groups, not isolated columns.
Data readiness alone is not enough.
020U remains paused.
```

Current next:

```text
R09-20260708-020TC_FAMILY_AWARE_X_Y_ATLAS
```

## Latest handoff override — 2026-07-08 R09-20260708-020TC_FAMILY_AWARE_X_Y_ATLAS completed

Use this block as the current R09/P2 handoff if older “Latest completed” or “Current next” sections conflict.

Latest completed:

```text
R09-20260708-020TC_FAMILY_AWARE_X_Y_ATLAS
```

Primary report:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260708-020TC_FAMILY_AWARE_X_Y_ATLAS_report_20260708.md
```

Key outputs:

```text
experiments/lab_001_xy_connection_20260626/reports/tables/R09-20260708-020TC_xy_family_specific_metrics_20260708.csv
experiments/lab_001_xy_connection_20260626/reports/tables/R09-20260708-020TC_xy_family_generalization_summary_20260708.csv
experiments/lab_001_xy_connection_20260626/reports/tables/R09-20260708-020TC_xy_feature_group_to_target_group_matrix_20260708.csv
experiments/lab_001_xy_connection_20260626/reports/tables/R09-20260708-020TC_selected_y_candidate_family_sensitivity_20260708.csv
experiments/lab_001_xy_connection_20260626/reports/figures/R09-20260708-020TC_global_vs_family_sensitivity_20260708.svg
experiments/lab_001_xy_connection_20260626/reports/figures/R09-20260708-020TC_xcluster_ygroup_matrix_heatmap_20260708.svg
experiments/lab_001_xy_connection_20260626/reports/figures/R09-20260708-020TC_selected_y_family_sensitivity_panel_20260708.svg
```

020T-C result:

```text
x-y pair rows analyzed: 6751
family-group long rows: 40506
direction long rows: 20253
x-cluster/y-target-group matrix rows: 1701
selected-y representative target rows: 21
likely_global x-y pairs: 758
likely_family_specific x-y pairs: 283
likely_direction_sensitive x-y pairs: 31
weak_global x-y pairs: 5345
```

New confirmed/relevant decisions:

```text
R09-BB-116 = confirmed: 020T-C was executed and logged.
R09-BB-117 = likely: global x-y candidates exist after family-aware check.
R09-BB-118 = confirmed: family/direction-sensitive x-y relations exist.
R09-BB-119 = confirmed: 020U remains blocked after 020T-C.
R09-BB-120 = rejected: selected-y cannot be chosen by global correlation alone.
DEC-076 = confirmed: selected-y must use family-aware x-y evidence before 020U.
```

Current next:

```text
R09-20260708-020U-E_TRAINING_CODE_CROSSWALK_AND_FEATURE_SELECTION_POLICY_NO_TRAINING
```

Current 020U-prep status:

```text
CTRL-20260708-M01 completed.
FORK-A conditionally accepted as 020T-D draft selected-y basis.
FORK-B accepted as descriptor-validation guardrail.
FORK-C conditionally accepted as batch-prep manifest only.
FORK-D partially accepted as theta discovery/schema draft only.
R09-20260708-020U-PREP selected-y and feature policy completed.
First-pass MVP selected-y candidate: YG002 / FX / Max. Plateau stress / compression / maximize.
Secondary: YG004. Vibration follow-up: YG018/YG019. Caution: YG006.
R09-20260708-020U-A completed.
YG002-A core blueprint: Y_FX + X_AJ + X_DL.
YG002-B sensitivity blueprint: YG002-A + X_AB.
YG002-C Maxwell control subset: YG002-A + X_G.
No model training was run.
R09-20260708-020U-B completed.
Decision: GO-CONDITIONAL for constrained YG002 leakage-safe baseline dry-run.
Readiness score: 84 / 100.
YG002-A/YG002-B are frozen for the next constrained baseline step.
R09-20260708-020U-C completed.
Decision after dry-run: conditional_continue.
YG002-A baseline improved over null.
YG002-B Curvature sensitivity improved slightly.
YG002-C Maxwell subset was numerically best but remains control subset only due TPMS exclusion.
R09-20260708-020U-D professor/TA alignment and Training intake completed.
Training source folder: C:\Users\chuck\Downloads\Training.
Highest-priority notebook candidate: Training_260508_Alltogether-5th_method_FIXED.ipynb.
Critical warning: Training output column letters differ from previous registry; semantic y-column crosswalk is required.
```

Hard guardrail:

```text
Original Excel, NB-CURRENT, and LEGACY-PY remain unchanged.
Do not patch NB-CURRENT MassOri/Curvature stdev.
Do not run full 020U modeling yet.
Only next allowed work: YG002 baseline result review and next-gate decision.
Do not run broad model search.
No random row split.
Do not continue y-specific modeling against Training until workbook/code crosswalk is built.
```

## Latest handoff override — 2026-07-08 R09-20260708-020U-E completed

Use this block as the current state if older 020U sections conflict.

Latest completed:

```text
R09-20260708-020U-E_TRAINING_CODE_CROSSWALK_AND_FEATURE_SELECTION_POLICY_NO_TRAINING
```

Primary report:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260708-020U-E_TRAINING_CODE_CROSSWALK_AND_FEATURE_SELECTION_POLICY_NO_TRAINING_20260708.md
```

Key generated tables:

```text
reports/tables/R09-20260708-020U-E_training_output_semantic_crosswalk_20260708.csv
reports/tables/R09-20260708-020U-E_training_column_drift_hotspots_20260708.csv
reports/tables/R09-20260708-020U-E_training_feature_block_policy_20260708.csv
reports/tables/R09-20260708-020U-E_training_stage_scope_policy_20260708.csv
reports/tables/R09-20260708-020U-E_training_next_gate_queue_20260708.csv
```

Current facts:

```text
Training FX = Com. Strength.
Training GM = Max. Plateau stress.
Training Summary Z = Max. Plateau stress.
Training AB = Thickness LIP.
Training AJ = Mass Orientation IP-stdev.
Training DL = Curvature LTP.
Training_260508_Alltogether-5th_method_FIXED.ipynb is the highest-priority future integration source.
```

Current interpretation:

```text
Previous 020U-C remains useful as a historical constrained dry-run, but its Y_FX/X_AJ/X_DL/X_AB column-letter assumptions cannot be promoted into the Training branch.
Use semantic meaning plus workbook/sheet/column provenance for every selected y and x.
I:Y is added lattice/partial feature block.
Z:FU is safer all-family legacy core.
I:FU is output-wise candidate only.
Methods 1/2/3/4/5 are output-dependent method families, not a version ladder.
```

Current next:

```text
R09-20260708-020U-F_TRAINING_TARGET_SELECTION_AND_METHOD_POLICY_GATE_NO_BROAD_TRAINING
```

Hard guardrail:

```text
No full 020U modeling.
No broad Training model search.
No NB-CURRENT patch.
No LEGACY-PY edit.
No original Excel edit.
No random row split.
Resolve selected-y semantic target crosswalk and selected-x semantic feature policy first.
```

## Latest handoff override — 2026-07-08 R09-SLICE direction alignment completed

Use this block as the current descriptor-validation state if older R09/020U blocks conflict.

Latest completed:

```text
R09-20260708-SLICE_DIRECTION_ALIGNMENT
```

Primary report:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260708-SLICE_DIRECTION_ALIGNMENT_20260708.md
```

Key tables:

```text
reports/tables/R09-20260708_slice_artifact_schema_20260708.csv
reports/tables/R09-20260708_slice_doe_variable_table_20260708.csv
reports/tables/R09-20260708_descriptor_traceability_checklist_20260708.csv
reports/tables/R09-20260708_updated_parallel_next_action_queue_20260708.csv
```

Current confirmed decisions:

```text
Official descriptor extraction validation must be based on image slicing + pixel read + connected-component/pixel descriptor artifacts.
CSV x-x/y-y/x-y analysis remains useful as strategy/forensic support.
Pixel size, slice count, slice spacing, threshold, and connected-component rules are DOE variables.
```

Current likely/unresolved:

```text
likely: 30x30 vs 40x40 scale mismatch should be handled by y=a*x / correlation / dimensional scaling review.
unresolved: exact "avg에 대한 std" population.
```

Current next:

```text
R09-SLICE-001_IMAGE_SLICING_PIXEL_READ_PIPELINE_SPEC
```

Parallel lane:

```text
R09-20260708-020U-F_TRAINING_TARGET_SELECTION_AND_METHOD_POLICY_GATE_NO_BROAD_TRAINING
```

Interpretation:

```text
020U-F is modeling strategy.
R09-SLICE-001/003/002/004 is descriptor validation evidence.
Do not let one lane pretend to replace the other.
```

Hard guardrail:

```text
No CSV-only descriptor-validation pass.
No NB-CURRENT / LEGACY-PY / NB-ORIG edits.
No original Excel or Training source edits.
No full extraction batch until artifact schema and DOE plan are defined.
```

## Latest handoff override — 2026-07-08 R09-SLICE-001 completed

Use this block as the current descriptor-validation control state.

Latest completed:

```text
R09-SLICE-001_IMAGE_SLICING_PIXEL_READ_PIPELINE_SPEC
```

Primary report:

```text
experiments/lab_001_xy_connection_20260626/results/R09-SLICE-001_IMAGE_SLICING_PIXEL_READ_PIPELINE_SPEC_20260708.md
```

Key official tables:

```text
reports/tables/R09-SLICE-001_pipeline_stage_contract_20260708.csv
reports/tables/R09-SLICE-001_run_manifest_fields_20260708.csv
reports/tables/R09-SLICE-001_artifact_directory_plan_20260708.csv
reports/tables/R09-SLICE-001_validation_gate_checklist_20260708.csv
reports/tables/R09-SLICE-001_b3_pilot_minimum_packet_20260708.csv
reports/tables/R09-SLICE-001_claim_gate_matrix_20260708.csv
reports/tables/R09-SLICE-001_descriptor_trace_rules_20260708.csv
reports/tables/R09-SLICE-001_subagent_merge_review_20260708.csv
```

Current confirmed decisions:

```text
Official R09-SLICE runs must follow S00-S09 stage gates.
Every run needs source/config hash, run manifest, artifact hash manifest, images, pixel tables, component tables, descriptor results, comparison outputs, and confidence labels.
B3 pilot is one-model/one-axis first.
R09-SLICE-003 must define DOE seed settings before R09-SLICE-002 B3 pilot.
```

Current unresolved:

```text
MassOri stdev.
Curvature stdev.
Exact population behind "avg에 대한 std".
Descriptor-specific dimensional scaling classes.
```

Current next:

```text
R09-SLICE-003_PIXEL_SIZE_SLICE_SPACING_DOE_PLAN
```

Parallel lane:

```text
R09-20260708-020U-F_TRAINING_TARGET_SELECTION_AND_METHOD_POLICY_GATE_NO_BROAD_TRAINING
```

Hard guardrail:

```text
No image/full-family extraction batch yet.
No NB-CURRENT / NB-ORIG / LEGACY-PY edits.
No original Excel or Training source edits.
No MassOri/Curvature stdev patch.
```

## Latest handoff override — 2026-07-08 R09-SLICE-003 completed

Use this block as the current R09-SLICE execution-control state.

Latest completed:

```text
R09-SLICE-003_PIXEL_SIZE_SLICE_SPACING_DOE_PLAN
```

Primary report:

```text
experiments/lab_001_xy_connection_20260626/results/R09-SLICE-003_PIXEL_SIZE_SLICE_SPACING_DOE_PLAN_20260708.md
```

Key official tables:

```text
reports/tables/R09-SLICE-003_doe_factor_table_20260708.csv
reports/tables/R09-SLICE-003_doe_run_matrix_20260708.csv
reports/tables/R09-SLICE-003_validation_metric_table_20260708.csv
reports/tables/R09-SLICE-003_promotion_gate_table_20260708.csv
reports/tables/R09-SLICE-003_legion_labpc_execution_policy_20260708.csv
reports/tables/R09-SLICE-003_b3_seed_policy_20260708.csv
reports/tables/R09-SLICE-003_next_action_queue_20260708.csv
```

Current B3 seed candidate:

```text
model: B3
axis: z
pixel_resolution: 1000x1000
slice_count: 801
slice_spacing_mm: 0.05
connected_component: 8-connectivity
min_component_pixels: 2
threshold/fill/source/scale: explicitly log in R09-SLICE-002
```

Current next:

```text
R09-SLICE-002A_LOCK_B3_SOURCE_GEOMETRY_AND_HASH
```

Hard guardrail:

```text
No full-family extraction.
No untracked image run.
No high-resolution/lab-PC run before source lock and smoke pass.
No NB-CURRENT / NB-ORIG / LEGACY-PY / original Excel / Training source edits.
No MassOri/Curvature stdev patch.
```

## Latest handoff override — 2026-07-09 R09-SLICE-002A completed

Use this block as the current B3 pilot source-lock state.

Latest completed:

```text
R09-SLICE-002A_LOCK_B3_SOURCE_GEOMETRY_AND_HASH
```

Primary report:

```text
experiments/lab_001_xy_connection_20260626/results/R09-SLICE-002A_LOCK_B3_SOURCE_GEOMETRY_AND_HASH_20260709.md
```

Key official tables:

```text
reports/tables/R09-SLICE-002A_b3_source_candidate_registry_20260709.csv
reports/tables/R09-SLICE-002A_b3_source_selection_20260709.csv
reports/tables/R09-SLICE-002A_b3_geometry_preflight_20260709.csv
reports/tables/R09-SLICE-002A_b3_run_manifest_seed_20260709.csv
reports/tables/R09-SLICE-002A_next_action_queue_20260709.csv
```

Locked primary source:

```text
source_id: B3SRC-STL-001
format: STL
path: experiments/lab_001_xy_connection_20260626/data/raw/notion_reference_models_20260701/stl/B3-Basic_Cubic-BCC_Lattice.stl
sha256: a272cdb9222309756d52e07d7bd10bf5c2eb7ebe3b216005fec40c6653843a30
bbox_size_mm: [30.0, 30.0, 29.999999046325684]
```

Alternate source:

```text
B3SRC-STP-001 is hash-locked but held for R09-STP-001/direct STP proof.
```

Current next:

```text
R09-SLICE-002C-POLICY-DECISION
```

Latest completed:

```text
R09-SLICE-002B completed on 2026-07-09.
Report: experiments/lab_001_xy_connection_20260626/results/R09-SLICE-002B_CREATE_B3_RUN_MANIFEST_AND_DIRECTORY_SKELETON_20260709.md
Run packet: experiments/lab_001_xy_connection_20260626/runs/r09_slice_runs/R09S002_B3_z1000x801_srca272cdb92223_cfg66979db936/
run_id: R09S002_B3_z1000x801_srca272cdb92223_cfg66979db936
config_hash10: 66979db936
threshold_rule: filled_material_mask_gt_0
inside_fill_rule: closed_contour_fill_from_watertight_STL_section_required
```

Latest smoke result:

```text
R09-SLICE-002C completed with caveat on 2026-07-09.
Accepted environment: tools/envs/KMK312/python.exe
Report: experiments/lab_001_xy_connection_20260626/results/R09-SLICE-002C_B3_SMOKE_IMAGE_PIXEL_COMPONENT_PACKET_20260709.md
KMK312 run packet: experiments/lab_001_xy_connection_20260626/runs/r09_slice_runs/B3_002C_KMK312_cfg66979d/

Generated:
- 20 smoke slice rows
- 10 overlay rows
- 838 component rows
- 38 hashed artifacts

Important correction:
The first 002C run used Codex bundled Python and is provisional only.
Chuck pointed out KMK312 was installed; Codex found project-local KMK312 and reran the smoke.

Blocking caveat before 002D:
source bbox is about 30mm but 801 slices at 0.05mm span 40mm.
Do not run full 002D until slice-position/scale policy is selected.
```

Hard guardrail:

```text
No official full 801-slice image run yet.
002D is on hold pending policy decision.
No hidden threshold/fill/scale rule; use the 002B manifest policy.
No STP-as-primary until direct STP/B-rep proof.
No NB-CURRENT / NB-ORIG / LEGACY-PY / original Excel / Training source edits.
```

## Latest audit note — Excel aliases and model scale, 2026-07-09

Use these aliases:

```text
EXCEL_LEGACY_260212 = outputs/URP4-1/압축+열+진동+구조인자_260212.xlsx
EXCEL_TRAINING_TOTAL_260503 = C:/Users/chuck/Downloads/Training/Total data_260503.xlsx
```

Key findings:

```text
Summary sheet: identical between the two Excel files.
총정리 sheet: different structure; Training Total adds/reorganizes new feature columns.
Notion STL preflight: 32/33 files are 30x30x30 within 1e-3.
F1-Foam-Kelvin_foam.stl is the STL scale exception.
STP approximate bbox is mixed but may include construction/control points; direct STP/B-rep proof is still needed.
```

## Latest policy decision — N40_BBOX_EXACT processed STL branch, 2026-07-09

Chuck reported that the professor approved converting STL geometry to `40 × 40 × 40 mm`.

Use this processed branch for the next official image/pixel artifact run:

```text
branch_id: N40_BBOX_EXACT
report: experiments/lab_001_xy_connection_20260626/results/R09_N40_BBOX_EXACT_STL_NORMALIZATION_20260709.md
processed_dir: experiments/lab_001_xy_connection_20260626/data/processed/notion_reference_models_20260709_n40_bbox_exact/stl/
manifest: experiments/lab_001_xy_connection_20260626/reports/tables/R09_N40_BBOX_EXACT_processed_stl_manifest_20260709.csv
```

Result:

```text
34/34 raw STL files processed.
failure_count = 0.
Independent bbox check: every processed STL is exact [0,0,0] to [40,40,40] mm.
Raw STL/STP sources were not modified.
```

B3 source for `R09-SLICE-002D`:

```text
experiments/lab_001_xy_connection_20260626/data/processed/notion_reference_models_20260709_n40_bbox_exact/stl/B3__a272cdb922__N40_BBOX_EXACT.stl
processed_sha256: 4de71cd09afc92b7dc00859130fa4314fcb43dba7ec0da9a2244c51691a8da30
```

Updated next:

```text
R09-SLICE-002D_B3_STANDARD_SEED_FULL_ARTIFACT_PACKET
```

## Latest communication aid — file alias registry, 2026-07-09

Use this workbook as the shared file naming reference:

```text
outputs/URP4-1_file_alias_registry_20260709.xlsx
```

Current updated workbook:

```text
outputs/URP4-1_file_alias_registry_20260709_UPDATED.xlsx
```

Why UPDATED exists:

```text
The original alias workbook was locked/open, so Codex could not overwrite it.
Use UPDATED as current until the original is closed and replaced.
```

Training files copied into workspace:

```text
origin: C:\Users\chuck\Downloads\Training
workspace copy: experiments/lab_001_xy_connection_20260626/data/raw/professor_training_20260709/
manifest: experiments/lab_001_xy_connection_20260626/reports/tables/R09_training_source_workspace_copy_manifest_20260709.csv
result: 10/10 files copied, 10/10 SHA-256 match
```

Human reading map:

```text
outputs/URP4-1_파일_alias와_읽기지도_20260709.md
```

Important wording:

```text
Training code is not fully analyzed yet.
Completed: inventory/crosswalk/no-training intake.
Remaining: execution parity, line-by-line study, selected-y feature-selection reproduction.
```

The NB-CURRENT cell-level explanation document Chuck was looking for is:

```text
experiments/lab_001_xy_connection_20260626/results/R06V2_P1_LEGACY_INTEGRATION_HANDOFF_20260630.md
```

## Latest support update — Training line-by-line textbooks, 2026-07-09

Current canonical alias workbook:

```text
outputs/URP4-1_file_alias_registry_20260709_UPDATED.xlsx
```

Important cleanup:

```text
outputs/URP4-1_file_alias_registry_20260709.xlsx was deleted at Chuck's request.
Use the UPDATED workbook as the current alias registry.
```

Training line-by-line study pack:

```text
index:
experiments/lab_001_xy_connection_20260626/results/training_line_by_line/TRAINING_LINE_BY_LINE_INDEX_20260709.md

doc directory:
experiments/lab_001_xy_connection_20260626/results/training_line_by_line/

registry:
experiments/lab_001_xy_connection_20260626/reports/tables/R09_training_line_by_line_doc_registry_20260709.csv
```

Coverage:

```text
9/9 Training notebooks documented.
Total code lines covered: 27,864.
Alias workbook sheet 02_READ_THIS_FIRST has READ-013 through READ-022 for these documents.
```

Status wording:

```text
Training line-by-line textbookization is complete as first-pass static code-reading support.
Do not claim Training notebooks have been executed or numerically validated yet.
Remaining: KMK312 execution parity, selected-y feature-selection reproduction, and output-specific model policy validation.
```

## Latest macro alignment — Professor roadmap v0.8, 2026-07-09

Updated macro roadmap:

```text
outputs/URP4-1_PROFESSOR_PROJECT_ROADMAP_20260629.md
```

Current professor-level interpretation:

```text
Primary priority remains descriptor validation.
Official proof = image slicing -> pixel read -> connected component/pixel descriptor trace.
CSV x-x/y-y/x-y is strategy/forensic/feature-selection support, not a standalone descriptor-validation pass.
Scale-aware Excel comparison is acceptable: y=x, y=a*x, correlation, and standout/outlier review.
40x40x40 STL normalization is professor-approved as a separate processed branch.
Training code is a parallel feature-selection/modeling strategy asset.
```

Immediate primary next task:

```text
R09-SLICE-002D_B3_STANDARD_SEED_FULL_ARTIFACT_PACKET
```

Use processed B3 STL:

```text
experiments/lab_001_xy_connection_20260626/data/processed/notion_reference_models_20260709_n40_bbox_exact/stl/B3__a272cdb922__N40_BBOX_EXACT.stl
```

Parallel support task:

```text
R09-TRAIN-001 / 020U-F_TRAINING_TARGET_SELECTION_AND_METHOD_POLICY_GATE_NO_BROAD_TRAINING
```

Use:

```text
experiments/lab_001_xy_connection_20260626/results/training_line_by_line/TRAINING_LINE_BY_LINE_INDEX_20260709.md
outputs/URP4-1_file_alias_registry_20260709_UPDATED.xlsx
```

Do not:

```text
Do not patch NB-CURRENT yet.
Do not edit LEGACY-PY, NB-ORIG, original Excel, Training source, raw STL/STP.
Do not run broad Training/model search yet.
Do not jump to large generated-model streaming until the B3 artifact proof is accepted.
```

## Latest handoff override — 2026-07-09 R09-SLICE-002D completed

Use this block as the current descriptor-validation execution state.

Completed:

```text
R09-SLICE-002D_B3_STANDARD_SEED_FULL_ARTIFACT_PACKET
```

Report:

```text
experiments/lab_001_xy_connection_20260626/results/R09-SLICE-002D_B3_STANDARD_SEED_FULL_ARTIFACT_PACKET_20260709.md
```

Run root:

```text
experiments/lab_001_xy_connection_20260626/runs/r09_slice_runs/B3_002D_N40_z1000x801_cc8m2_cfgb623aef192/
```

Important outputs:

```text
801 mask PNGs.
800 overlay PNGs.
801 slice table rows.
800 overlay table rows.
37627 connected-component rows.
1611 artifact files hashed.
Runtime 545.569 s under tools/envs/KMK312/python.exe.
```

State wording:

```text
002D passes as artifact-generation evidence.
Do not claim descriptor correctness, Excel similarity, LEGACY-PY parity, or NB-CURRENT validation from 002D alone.
```

Caveats to carry forward:

```text
odd_scanline_rows_total = 1.
odd scanline location = slice_index 796, z≈39.8 mm.
endpoint_adjusted_count = 2.
Endpoint nudge is 1e-6 mm on first/last z slices only.
```

Next primary task:

```text
R09-SLICE-002E_descriptor_calculation_and_excel_comparison
```

## Latest handoff override — 2026-07-09 R09-SLICE-002E completed

Use this block as the current descriptor-validation execution state.

Completed:

```text
R09-SLICE-002E_descriptor_calculation_and_excel_comparison
```

Report:

```text
experiments/lab_001_xy_connection_20260626/results/R09-SLICE-002E_DESCRIPTOR_CALCULATION_AND_EXCEL_COMPARISON_20260709.md
```

Key tables:

```text
experiments/lab_001_xy_connection_20260626/reports/tables/R09-SLICE-002E_overlay_component_features_20260709.csv
experiments/lab_001_xy_connection_20260626/reports/tables/R09-SLICE-002E_candidate_descriptors_long_20260709.csv
experiments/lab_001_xy_connection_20260626/reports/tables/R09-SLICE-002E_excel_comparison_20260709.csv
experiments/lab_001_xy_connection_20260626/reports/tables/R09-SLICE-002E_best_by_descriptor_stat_20260709.csv
experiments/lab_001_xy_connection_20260626/reports/tables/R09-SLICE-002E_formula_family_summary_20260709.csv
```

Figures:

```text
experiments/lab_001_xy_connection_20260626/reports/figures/R09-SLICE-002E_yx_scatter_by_descriptor_20260709.png
experiments/lab_001_xy_connection_20260626/reports/figures/R09-SLICE-002E_best_rel_diff_bar_20260709.png
experiments/lab_001_xy_connection_20260626/reports/figures/R09-SLICE-002E_formula_family_heatmap_20260709.png
```

State wording:

```text
002E is B3 artifact-backed descriptor calculation and Excel comparison.
Do not claim canonical formula proof or patch NB-CURRENT yet.
```

Important result:

```text
MassOri stdev closely matches B3 Excel in the 002E image-artifact path.
This differs from R09-017 and reinforces that image/fill/backend lineage must be validated.
```

Next primary task:

```text
R09-SLICE-002F_B3_SENSITIVITY_AND_REPRESENTATIVE_GATE
```

## Latest handoff override — 2026-07-09 R09-SLICE-002F completed

Use this block as the current descriptor-validation execution state.

Completed:

```text
R09-SLICE-002F_B3_SENSITIVITY_AND_REPRESENTATIVE_GATE
```

Report:

```text
experiments/lab_001_xy_connection_20260626/results/R09-SLICE-002F_B3_SENSITIVITY_AND_REPRESENTATIVE_GATE_20260709.md
```

Key tables:

```text
experiments/lab_001_xy_connection_20260626/reports/tables/R09-SLICE-002F_sensitivity_summary_20260709.csv
experiments/lab_001_xy_connection_20260626/reports/tables/R09-SLICE-002F_target_stability_20260709.csv
experiments/lab_001_xy_connection_20260626/reports/tables/R09-SLICE-002F_decision_matrix_20260709.csv
experiments/lab_001_xy_connection_20260626/reports/tables/R09-SLICE-002F_next_action_queue_20260709.csv
```

Figures:

```text
experiments/lab_001_xy_connection_20260626/reports/figures/R09-SLICE-002F_target_survivor_sensitivity_20260709.png
experiments/lab_001_xy_connection_20260626/reports/figures/R09-SLICE-002F_filter_stability_summary_20260709.png
```

State wording:

```text
002F passes the B3 sensitivity gate.
Do not claim canonical formula proof or patch NB-CURRENT yet.
```

Important result:

```text
Endpoint, odd-scanline, and small boundary-trim filters did not destabilize the B3 survivors enough to block representative-family expansion.
Gate metrics:
max_value_delta_vs_baseline = 0.0243228
max_rel_diff_delta_vs_baseline = 0.022603
max_median_best_drift = 0.00229434
```

Next primary task:

```text
R09-SLICE-002G_C1_L1_REPRESENTATIVE_ARTIFACT_PACKETS_AND_COMPARISON
```

## Latest handoff override — 2026-07-09 R09-SLICE-002G completed

Use this block as the current descriptor-validation execution state.

Completed:

```text
R09-SLICE-002G_C1_L1_REPRESENTATIVE_ARTIFACT_PACKETS_AND_COMPARISON
```

Report:

```text
experiments/lab_001_xy_connection_20260626/results/R09-SLICE-002G_C1_L1_REPRESENTATIVE_ARTIFACT_PACKETS_AND_COMPARISON_20260709.md
```

Key tables:

```text
experiments/lab_001_xy_connection_20260626/reports/tables/R09-SLICE-002G_summary_20260709.json
experiments/lab_001_xy_connection_20260626/reports/tables/R09-SLICE-002G_qc_summary_20260709.csv
experiments/lab_001_xy_connection_20260626/reports/tables/R09-SLICE-002G_excel_comparison_20260709.csv
experiments/lab_001_xy_connection_20260626/reports/tables/R09-SLICE-002G_best_by_descriptor_stat_20260709.csv
experiments/lab_001_xy_connection_20260626/reports/tables/R09-SLICE-002G_b3_survivor_cross_family_check_20260709.csv
experiments/lab_001_xy_connection_20260626/reports/tables/R09-SLICE-002G_representative_gate_matrix_20260709.csv
```

Figures:

```text
experiments/lab_001_xy_connection_20260626/reports/figures/R09-SLICE-002G_representative_best_rel_diff_20260709.png
experiments/lab_001_xy_connection_20260626/reports/figures/R09-SLICE-002G_representative_best_yx_scatter_20260709.png
experiments/lab_001_xy_connection_20260626/reports/figures/R09-SLICE-002G_b3_survivor_transfer_20260709.png
```

State wording:

```text
002G completed with finalizer caveat.
C1/L1 representative best-row stability passes.
B3 survivor cross-family transfer is caution, not pass.
Do not claim canonical formula proof or patch NB-CURRENT yet.
```

Important result:

```text
C1 median_best_rel_diff = 0.0237099.
L1 median_best_rel_diff = 0.0205417.
B3 survivor transfer: pass=10, caution=6, fail=6 out of 22.
```

Next primary task:

```text
R09-SLICE-002G-REVIEW_descriptor_specific_failures_and_patch_policy
```

## Latest handoff override — 2026-07-10 R09-SLICE-002G-REVIEW completed

Use this block as the current descriptor-policy state.

Completed:

```text
R09-SLICE-002G-REVIEW_descriptor_specific_failures_and_patch_policy
```

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-SLICE-002G_REVIEW_DESCRIPTOR_SPECIFIC_FAILURES_AND_PATCH_POLICY_20260710.md
experiments/lab_001_xy_connection_20260626/reports/tables/R09-SLICE-002G_REVIEW_descriptor_policy_matrix_20260710.csv
experiments/lab_001_xy_connection_20260626/reports/tables/R09-SLICE-002G_REVIEW_nb_current_patch_queue_20260710.csv
experiments/lab_001_xy_connection_20260626/reports/tables/R09-SLICE-002G_REVIEW_next_action_queue_20260710.csv
```

State wording:

```text
Descriptor formula policy is descriptor/population-specific.
The raw second LIP-stdev columns P/Y/AG/AO/AW are working LTP-stdev targets.
9/15 avg targets are likely candidates for LEGACY-PY parity.
15/15 stdev targets remain unresolved.
Do not patch NB-CURRENT and do not claim canonical formula proof.
```

Next primary task:

```text
R09-SLICE-002H_TARGET_COLUMN_REMAP_AND_CACHED_RECOMPARE
```

## Latest handoff override — 2026-07-10 R09-SLICE-002H completed

Use this block as the current target-lineage state.

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-SLICE-002H_TARGET_COLUMN_REMAP_AND_CACHED_RECOMPARE_20260710.md
experiments/lab_001_xy_connection_20260626/reports/tables/R09-SLICE-002H_target_audit_20260710.csv
experiments/lab_001_xy_connection_20260626/reports/tables/R09-SLICE-002H_review_parity_delta_20260710.csv
```

State wording:

```text
P/Y/AG/AO/AW are working LTP-stdev columns in R09-SCRIPT.
Cached R09-SCRIPT recomparison matches 002G-REVIEW in all 420 rows.
Do not treat this as LEGACY-PY parity or a license to patch NB-CURRENT.
```

Next primary task:

```text
R09-SLICE-002I_LEGACY_PY_PARITY_SELECTED_AVG
```

## Latest handoff override — 2026-07-10 R09-SLICE-002I completed

Use this block as the current descriptor-validation state.

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-SLICE-002I_LEGACY_PY_PARITY_SELECTED_AVG_20260710.md
experiments/lab_001_xy_connection_20260626/reports/tables/R09-SLICE-002I_selected_avg_parity_20260710.csv
experiments/lab_001_xy_connection_20260626/reports/figures/R09-SLICE-002I_selected_avg_legacy_parity_yx_20260710.png
```

State wording:

```text
Use LEGACY-PY, not Excel, as the immediate integration reference.
The direct image-artifact route is confirmed for B3/C1/L1 selected averages.
Angle/MassOri/Thickness LIP are likely source-lineage candidates but must pass inclusion/fallback sensitivity before any NB-CURRENT patch proposal.
P/A and every stdev population remain unresolved.
Do not patch NB-CURRENT, NB-ORIG, LEGACY-PY, raw STL/STP, or original Excel.
```

Next primary task:

```text
R09-SLICE-002J_SELECTED_AVG_INCLUSION_AND_FALLBACK_SENSITIVITY_GATE
```

## Latest handoff override — 2026-07-10 R09-SLICE-002J completed

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-SLICE-002J_SELECTED_AVG_INCLUSION_AND_FALLBACK_SENSITIVITY_20260710.md
experiments/lab_001_xy_connection_20260626/reports/tables/R09-SLICE-002J_direct_legacy_reconstruction_parity_20260710.csv
experiments/lab_001_xy_connection_20260626/reports/tables/R09-SLICE-002J_patch_eligibility_20260710.csv
```

State wording:

```text
Direct LEGACY-PY reconstruction is confirmed: 21/21 checks exact_or_roundoff.
Only MassOri and Thickness LIP may enter a read-only patch proposal gate.
Angle, P/A, and all stdev definitions remain unresolved.
Do not patch NB-CURRENT yet.
```

Next primary task:

```text
R09-SLICE-002K_DESCRIPTOR_SPECIFIC_PATCH_PROPOSAL_GATE_FOR_MASSORI_AND_THICKNESS_ONLY
```

## Latest handoff override — 2026-07-10 R09-SLICE-002K completed

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-SLICE-002K_DESCRIPTOR_SPECIFIC_PATCH_PROPOSAL_GATE_20260710.md
experiments/lab_001_xy_connection_20260626/reports/tables/R09-SLICE-002K_massori_thickness_policy_20260710.csv
experiments/lab_001_xy_connection_20260626/reports/tables/R09-SLICE-002K_proposal_accept_reject_checklist_20260710.csv
```

State wording:

```text
Do not patch NB-CURRENT-E2E-SAFE in place. NB-CURRENT is a separate registry alias and was not the 002K static source-review file.
Only a disposable, artifact-backed, versioned legacy-PNG compatibility helper may be prototyped for MassOri and Thickness LIP.
Angle/P-A/stdev and native mesh slicer parity remain unresolved.
```

Next primary task:

```text
R09-SLICE-002M_NB_COMPAT_DISPATCH_E2E_NONINTERFERENCE_TEST
```

## AUTHORITATIVE LATEST HANDOFF — 2026-07-11 after R09-SURF-004

This section supersedes older `Next primary task` text above.

```text
RUN-114 R09-SLICE-002M complete
RUN-115 R09-TRAIN-002 policy complete; no model fit
RUN-116 R09-POINT-001 complete; historical INP source parity blocked
RUN-117 R09-AREA-001 complete; exact image source rule unresolved
RUN-118 R09-SURF-002 complete as hold gate
RUN-119 R09-SURF-003 DOE/factory prep complete
RUN-120 R09-SURF-004 all-tier sensitivity complete
```

Latest surface result:

```text
35 attempted; 16 completed; 8 guard-skip; 11 QA-reject; 0 errors.
plateau pass 0/7; family-generalization fail/hold.
Surface DDG is excluded from primary modeling and NB-CURRENT patching.
Do not rerun unchanged.
```

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-SURF-004_MULTI_RESOLUTION_SIMPLIFICATION_SENSITIVITY_EXECUTION_20260711.md
experiments/lab_001_xy_connection_20260626/results/R09-SURF-004_CHUCK_INPUT_PACKET_PROVENANCE_AND_MESH_DECISIONS_20260711.md
experiments/lab_001_xy_connection_20260626/results/R09-TRAIN-002_CURRENT_DATA_FIVE_OUTPUT_FEATURE_SELECTION_PILOT_SPEC_20260711.md
```

Next autonomous lane:

```text
Prepare/freeze the leakage-safe GM Max. Plateau stress baseline dataset only after the versioned target policy is adopted.
Do not include surface DDG, unresolved Initial Area source rules, or INP/STL-population-mixed Point features.
```

Current indices:

```text
PRM-026 / RUN-120 / DEC-152 / CHG-139 / LAB-CHG-111 / R09-BB-244~253
```

## Overnight control-tower handoff — 2026-07-11

Completed under KMK312:

```text
RUN-114 R09-SLICE-002M
RUN-115 R09-TRAIN-002 (policy only; no training)
RUN-116 R09-POINT-001
RUN-117 R09-AREA-001
RUN-118 R09-SURF-002
```

Authoritative latest state:

```text
Slice compatibility dispatch passed without altering generic-native fields; candidate stays validated_disposable.
Point Distribution formula core is resolved, but historical INP source parity is externally blocked.
Initial Area is three separate pixel-quantized x inputs; its exact source image/layer/direction rule is unresolved.
Surface DDG formula tests pass, but raw-versus-simplified convergence passed 0/5; it remains excluded from primary modeling.
First no-training modeling candidate is EXCEL_TRAINING_TOTAL_260503:총정리!GM / Max. Plateau stress, after dataset freeze and exact-target adoption.
```

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-SURF-002_SURFACE_CURVATURE_MESH_QA_OUTLIER_CONVERGENCE_GATE_20260711.md
experiments/lab_001_xy_connection_20260626/results/R09-POINT-001_CHUCK_INPUT_PACKET_HISTORICAL_INP_20260711.md
experiments/lab_001_xy_connection_20260626/results/R09-TRAIN-002_CURRENT_DATA_FIVE_OUTPUT_FEATURE_SELECTION_PILOT_SPEC_20260711.md
```

Next AI primary:

```text
R09-SURF-003_MULTI_RESOLUTION_SIMPLIFICATION_REMESH_DOE_SPEC_AND_FACTORY_PREP
```

Current indices:

```text
PRM-026 / RUN-118 / DEC-150 / CHG-137 / LAB-CHG-109 / R09-BB-238~243
```

## R09-SLICE-002M completed — 2026-07-11

```text
NB-COMPAT-LEGACY-PNG-V0-1 Cell 8F dispatch passed under KMK312.
Generic-native fields: 408/408 unchanged.
Approved compatibility fields: 30/30 exact-or-roundoff.
Invalid-axis request: fail-closed; generic output unchanged.
```

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-SLICE-002M_NB_COMPAT_DISPATCH_E2E_NONINTERFERENCE_TEST_20260711.md
```

Boundary:

```text
NB-COMPAT-LEGACY-PNG-V0-1 remains validated_disposable and is not promoted to NB-CURRENT.
Native STL-to-archived-PNG equivalence, Angle, P/A and canonical stdev remain unresolved.
```

Current work:

```text
Primary: R09-POINT-001_POINT_MASS_DISTRIBUTION_SOURCE_AND_POPULATION_CROSSWALK
Parallel no-training policy: R09-TRAIN-002_CURRENT_DATA_FIVE_OUTPUT_FEATURE_SELECTION_PILOT_SPEC
```

## R09-TRAIN-002 completed — 2026-07-11

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-TRAIN-002_CURRENT_DATA_FIVE_OUTPUT_FEATURE_SELECTION_PILOT_SPEC_20260711.md
```

Current policy:

```text
First-pass targets: YG002/GM, YG004/GX, YG018/HE, YG019/HF, YG006/GU.
This is a likely/versioned candidate set, not professor-confirmed final truth.
Only HE is in TRAIN-5TH-FIXED's current 16-output selection.
Do not modify or execute TRAIN-5TH-FIXED unchanged for these five.
First MVP recommendation: GM Max. Plateau stress, family-summary z rows.
No random row split; HE includes 131 replicate rows.
```

Next:

```text
Primary: R09-POINT-001
Training: TRAIN002-Q01 exact-five confirmation/version adoption, then separate GM dataset/run-config freeze
```

## R09-POINT-001 completed — 2026-07-11

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-POINT-001_POINT_MASS_DISTRIBUTION_SOURCE_AND_POPULATION_CROSSWALK_20260711.md
```

Key state:

```text
LEGACY-PY-PARAMDIST = INP-node population.
NB-CURRENT point_legacy_mesh_nodes = STL-vertex population with the same formula core.
PNT-001 formula parity = 29/29 exact.
Excel alias Distribution parity = 5,488 shared exact + 112 Training-only values.
No INP file exists in the workspace; source parity is unresolved.
```

Current work:

```text
AI primary: R09-AREA-001_INITIAL_AREA_SOURCE_COLUMN_UNIT_LINEAGE
Chuck input: results/R09-POINT-001_CHUCK_INPUT_PACKET_HISTORICAL_INP_20260711.md
Training parallel: TRAIN002-Q01 then GM dataset/run-config freeze
```

## R09-AREA-001 completed — 2026-07-11

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-AREA-001_INITIAL_AREA_SOURCE_COLUMN_UNIT_LINEAGE_20260711.md
```

Critical correction:

```text
Initial Area = x input, not y unit.
Legacy AZ/DQ/FF; Training BO/EF/FU.
35 old 020U-E y labels inherited Initial Area incorrectly; use the AREA-001 correction CSV.
NB-CURRENT has no Initial Area output.
```

Current work:

```text
AI primary: R09-SURF-002_SURFACE_CURVATURE_MESH_QA_OUTLIER_CONVERGENCE_GATE
Chuck inputs: POINT historical INP packet + AREA exact slice/lane rule
Training: TRAIN002-Q01 then GM dataset/run-config freeze
```

## Professor call direction — 2026-07-11 / PRM-026

Source alias:

```text
CALL-DOCTOR-20260710-155723
```

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260711_DOCTOR_CALL_INTERPRETATION_AND_ROADMAP_ALIGNMENT_20260711.md
outputs/URP4-1_PROFESSOR_PROJECT_ROADMAP_20260629.md
outputs/URP4-1_ROADMAP.md
```

Current execution map:

```text
Primary descriptor lane:
R09-SLICE-002M
→ R09-POINT-001
→ R09-AREA-001 (Initial Area term is provisional until code/column lock)
→ R09-SURF-002 mesh-QA/outlier gate

Parallel modeling lane:
R09-TRAIN-002 current-data approximately-five-output feature-selection pilot spec

Event lane:
new STL → alias/hash/family duplicate intake
new compression y → R09-YDATA-001 versioned intake and retraining comparison
```

State wording:

```text
Training Excel is a schema-enriched variant of the original dataset, not an independent source.
Use only current Excel descriptors with traceable columns in the first pilot.
Use family-aware grouped-CV R² as primary; training R² alone is not success evidence.
Surface curvature was historically excluded because of mesh-related outliers but is intended for final inclusion after QA.
The exact five targets, Initial Area code/column identity, future STL list, and future compression metadata remain unresolved.
```

Indices:

```text
PRM-026 / RUN-113 / DEC-145 / CHG-132 / LAB-CHG-104 / R09-BB-216~221
```

## Alias correction — 2026-07-10

```text
For R09-SLICE-002K, use NB-CURRENT-E2E-SAFE exactly.
NB-CURRENT is a distinct canonical-v0.2 registry alias; it was not the 002K static-review source and was not modified.
Use the file alias registry as the authority whenever notebook variants are involved.
```

## R09-SLICE-002L completed — 2026-07-10

```text
NB-COMPAT-LEGACY-PNG-V0-1 is a separate, validated_disposable notebook candidate.
It replays only the fixed archived-PNG contract and adds new compatibility fields without replacing generic native fields.

B3/C1/L1 approved MassOri + Thickness LIP = 30/30 exact-or-roundoff against R09-SLICE-002I direct LEGACY-PY evidence.
```

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-SLICE-002L_DISPOSABLE_LEGACY_PNG_COMPATIBILITY_ADAPTER_PROTOTYPE_20260710.md
experiments/lab_001_xy_connection_20260626/reports/tables/R09-SLICE-002L_nb_compat_parity_comparison_20260710.csv
experiments/lab_001_xy_connection_20260626/reports/tables/R09-SLICE-002L_nb_compat_build_manifest_20260710.json
```

Next primary task:

```text
R09-SLICE-002M_NB_COMPAT_DISPATCH_E2E_NONINTERFERENCE_TEST
```

## FINAL CURRENT POINTER — 2026-07-11 05:20 KST

The older next-task text immediately above is historical. The authoritative current state is:

```text
Latest completed: RUN-120 / R09-SURF-004
Surface DDG: HOLD; plateau pass 0/7; primary modeling excluded
Next Chuck input: R09-SURF-004_CHUCK_INPUT_PACKET_PROVENANCE_AND_MESH_DECISIONS_20260711.md
Next AI modeling lane after policy adoption: leakage-safe GM Max. Plateau stress dataset freeze
Do not rerun SURF-004 unchanged
```

Target-policy unblock packet:

```text
experiments/lab_001_xy_connection_20260626/results/R09-TRAIN-002_CHUCK_INPUT_PACKET_FIRST_TARGET_POLICY_ADOPTION_20260711.md
Expected Chuck reply: YPOL-GM-v0.1 채택
```

## AUTHORITATIVE LATEST HANDOFF — 2026-07-13 / RUN-122

```text
YPOL-GM-v0.1: confirmed.
R09-TRAIN-003: 55-row GM dataset frozen; zero-model leakage pass.
R09-TRAIN-004: nested LOSO null/Ridge/ElasticNet baseline complete.
Best ElasticNet: pooled OOF R2=0.0627, MAE=89.255, RMSE=116.469.
Interpretation: weak signal; C/T transfer fails; inverse design not authorized.
```

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-TRAIN-003_GM_TARGET_DATASET_FREEZE_AND_LEAKAGE_AUDIT_20260713.md
experiments/lab_001_xy_connection_20260626/results/R09-TRAIN-004_GM_INTERPRETABLE_GROUPED_BASELINE_20260713.md
```

Next task:

```text
R09-TRAIN-005_ADD_AQ_SLICE_CURVATURE_IP_SENSITIVITY
Use identical rows/folds/models and add only X_AQ.
```

Current indices:

```text
PRM-026 / RUN-122 / DEC-154 / CHG-141 / LAB-CHG-113 / R09-BB-254~265
```

## AUTHORITATIVE LATEST HANDOFF — 2026-07-13 / RUN-123

```text
R09-TRAIN-005 added only X_AQ on identical RUN-122 rows/folds/models.
ElasticNet delta: R2 +0.0037; RMSE -0.23 (0.20%).
C/T RMSE both worsened; promotion gate failed.
AQ status: mixed_keep_sensitivity_only; not primary.
T8/T9 remain identical in Z/AI/AY/AQ.
```

Next:

```text
R09-TRAIN-006_C_T_RESIDUAL_AND_INFORMATION_GAP_DIAGNOSIS_NO_NEW_MODEL
No new model or feature promotion; exploratory candidates require future-data confirmation.
```

Current indices:

```text
PRM-026 / RUN-123 / DEC-155 / CHG-142 / LAB-CHG-114 / R09-BB-266~271
```

## AUTHORITATIVE LATEST HANDOFF — 2026-07-13 / RUN-124

```text
R09-TRAIN-006 fit no new model and diagnosed existing OOF errors.
C: mean residual +47.42; RMSE 112.13; far-neighbor 0/14. Primary extrapolation explanation rejected; missing information/family mapping likely.
T: mean residual +47.92; RMSE 150.41; far-neighbor 9/14; outside-range 6/14. Extrapolation confirmed as material.
AQ worsens both C and T and remains sensitivity-only.
Residual-feature rankings are adaptive diagnostics only.
```

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-TRAIN-006_C_T_RESIDUAL_AND_INFORMATION_GAP_DIAGNOSIS_NO_NEW_MODEL_20260713.md
```

Next:

```text
R09-TRAIN-007_NESTED_ONE_ADDITIONAL_FEATURE_SELECTION
Select within each outer training fold; never globally from RUN-124 residuals.
```

Current indices:

```text
PRM-026 / RUN-124 / DEC-156 / CHG-143 / LAB-CHG-115 / R09-BB-272~278
```

## AUTHORITATIVE LATEST HANDOFF — 2026-07-13 / RUN-127

```text
PILOT audit independently reproduced the negative RUN-126 result; AB/AK/AM stay rejected.
VALID reproduced the 45-candidate T8/T9 result but found a held-only metadata defect:
50/81 stdev/Std statistic_variant labels are misparsed. TRAIN-007 is unaffected; patch before broad reuse.

The canonical 1,000-candidate parameter_json snapshot now has a 26,108-row unique theta long extraction and a corrected 242-row registry.
Legacy-55 exact theta links: 0. Proxy 51, missing F1/F2 2, unresolved T5-6/T17 2.
No numeric theta may be inferred from family names. Legacy y=f(theta) and y=f(x,theta) remain blocked.
No new model was fit and no inverse-design claim is authorized.
```

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260713-CTRL_FAST_PILOT_VALID_THETA_MERGE_REPORT_20260713.md
experiments/parallel_forks/20260713_fast_pilot_valid_theta_harness/FORK_THETA_active_parameter_long_crosswalk/artifacts/R09-THETA-001_FORK_REPORT_20260713.md
```

Next:

```text
R09-THETA-002_LEGACY_GENERATION_PROVENANCE_SEARCH_AND_JOIN_GATE
Parallel maintenance: R09-VALID-008_FEATURE_METADATA_PARSER_AND_LINEAGE_PATCH_NO_MODEL
```

Current indices:

```text
PRM-026 / RUN-127 / DEC-159 / CHG-146 / LAB-CHG-118 / R09-BB-290~297
```

## AUTHORITATIVE LATEST HANDOFF — 2026-07-14 / RUN-128~129

```text
THETA-002 provenance search completed.
Exact legacy performance-row theta identity: 0/55.
The 1000-row generated campaign is a separate population; 3 preview candidates have exact candidate_id -> theta -> STL lineage.

Important correction:
- blocked: direct legacy y=f(theta) and y=f(x,theta);
- allowed: new generated theta -> geometry -> x cohort;
- allowed separately: guarded legacy/professor x -> y;
- not yet allowed: end-to-end/inverse-design claim before descriptor transportability and support-overlap gates.

VALID-008 metadata correction completed without model refit.
50/81 stdev labels and 6 dissipation boundary labels were corrected in versioned v2 metadata.
TRAIN-007 execution pool, decisions, values, and protected outputs are unchanged.
Formula lineage and repeated-header scientific identity remain unresolved.
```

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260714-THETA-002_LEGACY_PROVENANCE_AND_SEPARATE_COHORT_GATE_20260714.md
experiments/lab_001_xy_connection_20260626/results/R09-VALID-008_FEATURE_METADATA_PARSER_AND_LINEAGE_PATCH_20260714.md
```

Next:

```text
R09-THETA-X-001_PRIMARY3_STRATIFIED_GENERATED_PILOT
Smoke-test the 3 realized candidates, then pre-register a small stratified cohort.
Use immutable candidate_id/theta/geometry hashes and the canonical image/pixel trace.
Do not use legacy y or run the full 1000-candidate factory yet.
```

Current indices:

```text
PRM-026 / RUN-129 / DEC-161 / CHG-148 / LAB-CHG-120 / R09-BB-298~309
```

## AUTHORITATIVE LATEST HANDOFF — PRM-027 / 2026-07-14 11:33 KST

Professor direction relayed by Chuck changes the immediate priority for a 72-hour sprint.

```text
FAST: use existing/versioned x for structure discrimination and grouped x-y utility.
STRICT: continue Excel/LEGACY-PY/image-pixel parity in parallel.
RESCUE: if existing x fails, freshly slice matched geometries and create a new x schema.
```

Key rules:

- Excel mismatch alone is not a feature-exclusion rule.
- Maintain separate `reference_parity_status` and `predictive_utility_status`.
- Do not automatically add generation theta; it can expand the domain and legacy exact theta is 0/55.
- THETA-X-001 remains future P3 but is not the immediate 72-hour task.
- No random-row leakage, identity encoding, proxy theta, or training-fit-only success claim.

Next:

```text
R09-SPRINT-001_FAST_XY_FEATURE_BLOCK_AND_METHOD_TOURNAMENT_PREREG
Deadline: 2026-07-17 11:33 KST
```

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260714-PRM027_DUAL_TRACK_THREE_DAY_EXECUTION_ALIGNMENT_20260714.md
experiments/lab_001_xy_connection_20260626/reports/tables/R09-20260714_PRM027_three_day_execution_queue.csv
```

Current indices:

```text
PRM-027 / RUN-130 / DEC-162 / CHG-149 / LAB-CHG-121 / R09-BB-310~316
```

## AUTHORITATIVE LATEST HANDOFF — R09-SPRINT-001 G1 / 2026-07-14

The three-agent Wave 1 preregistration and Wave 2 FAST tournament are complete.

```text
Dataset: GMFREEZE-v0.1 / 55 family_summary z rows.
ALL55 V4: R2=0.031488, RMSE improvement=2.891%, below minimum.
BCL39/FB-D: all folds null fallback, 0% improvement.
C: 8.7597% worse than null.
T: only 0.3251% better, negative R2/Spearman.
T8/T9: true-y gap 10.206734, prediction gap 0.
Integrity: FAST self-QA + STRICT + QA pass.
```

No feature, method, physical unit, causal relation, or inverse-design route is promoted. `spca_ridge` and `direct_ard` are recorded as KMK312 SciPy-LAPACK runtime-incompatible, not scientifically rejected.

Next:

```text
R09-RESLICE-001_STANDARDIZED_MATCHED_GEOMETRY_X_REEXTRACTION
Bounded activation only: exact geometry-y registry, X_RESLICE_V1 contract, small matched pilot.
No full batch until R1 gate.
```

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-SPRINT-001_FAST_XY_FEATURE_BLOCK_AND_METHOD_TOURNAMENT_PREREG_20260714.md
experiments/parallel_forks/20260714_prm027_three_day_sprint_harness/G1_MERGE_DECISION.md
experiments/parallel_forks/20260714_prm027_three_day_sprint_harness/FORK_C_QA_RED_TEAM/artifacts/REPORT_WAVE2_QA.md
```

Current indices:

```text
PRM-027 / RUN-132 / DEC-164 / CHG-151 / LAB-CHG-123 / R09-BB-317~323
```

## AUTHORITATIVE LATEST HANDOFF — R09-RESLICE-001 R1 / 2026-07-14

RESCUE preparation was completed and independently audited, but the pilot must not run.

```text
Exact geometry-y: 29 = B4/C14/L11.
Likely: B1/F1/F2/T17; excluded.
Unresolved: 22.
Exact T: 0.
T8/T9 exact pair: unavailable.
R1: fail_preparation_only.
Smoke scientific artifacts: 0.
```

The `X_RESLICE_V1` image/pixel/component/deletion contract is frozen. Native full-trace references are 002D/002G; the rescue-local adapter is still blocked. Four formula groups (`XRV1-F009~F012`) must be split or excluded.

Next requires Chuck input:

```text
T8 Diamond A original STL + row-67 provenance
T9 Diamond B original STL + row-68 provenance
```

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-RESLICE-001_X_RESLICE_V1_MATCHED_GEOMETRY_PILOT_PREP_20260714.md
experiments/lab_001_xy_connection_20260626/results/R09-RESLICE-001_CHUCK_INPUT_PACKET_EXACT_T_GEOMETRY_20260714.md
experiments/parallel_forks/20260714_prm027_three_day_sprint_harness/R1_MERGE_DECISION.md
```

Current indices:

```text
PRM-027 / RUN-133 / DEC-165 / CHG-152 / LAB-CHG-124 / R09-BB-324~327
```

## AUTHORITATIVE LATEST HANDOFF — Notion geometry recovery prepared / 2026-07-14

Chuck duplicated the `3D Model` page into a personal Notion area. The duplicate is readable and the missing-family source route is now concrete.

```text
Primary: C30 VF30 압축_인장stl_T1-18.zip (T8/T9 candidates included).
Primary: C30 VF30 압축_인장stl_L12-20.zip.
Cross-check: previous-model T8.stl/T9.stl.
Cross-check: 5x5x5, 8 mm-cell DiamondA_Vf30.stl/DiamondB_Vf30.stl likely 40 mm alternates.
Direct missing-family STP: not found in the visible C30 STP page.
```

The token pasted into chat is exposed and must not be used. Chuck must revoke it and run the prepared hidden-input helper with a replacement token. The token value stays only at `C:\Users\chuck\.config\secrets\notion_urp4_token.txt`.

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260714_CHUCK_INPUT_PACKET_NOTION_TOKEN_ROTATION.md
experiments/lab_001_xy_connection_20260626/results/R09-20260714_NOTION_GEOMETRY_RECOVERY_INVENTORY.md
experiments/lab_001_xy_connection_20260626/reports/tables/R09-20260714_notion_geometry_recovery_inventory.csv
```

Next after `새 키 저장 완료`:

```text
KMK312 official-API download + safe extraction -> hash/dimension/mesh/cross-source audit
-> provisional T8/T9 crosswalk decision -> N40 derivatives -> independent STRICT R1 re-audit.
```

Current indices:

```text
PRM-027 / RUN-134 / DEC-166 / CHG-153 / LAB-CHG-125 / R09-BB-328~330
```

## AUTHORITATIVE LATEST HANDOFF — Missing-family STL acquisition complete / 2026-07-14

```text
C30 archives: 2/2 downloaded.
Archive members: 28/28 extracted and size-matched.
Required coverage: T1-T16 + L12-L20 = 25/25.
Recovery root: 48 STL + 2 ZIP.
Direct T8/T9 and L12-L20 STP: not found; nonblocking for STL-native RESCUE.
```

T8/T9 are physically available from three source classes: C30 archive, previous-model individual files, and alternate Diamond A/B files. These sources are not byte-identical. Therefore acquisition is complete, but exact Excel row 67/68 identity remains unresolved.

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260714_NOTION_GEOMETRY_RECOVERY_COMPLETION.md
experiments/lab_001_xy_connection_20260626/reports/tables/R09-20260714_notion_archive_member_hash_manifest.csv
experiments/lab_001_xy_connection_20260626/reports/tables/R09-20260714_notion_geometry_recovery_coverage.csv
```

Next:

```text
T8/T9 source-variant geometry audit -> crosswalk decision -> N40 derivatives -> independent STRICT R1 re-audit.
Do not start full slicing yet.
```

Current indices:

```text
PRM-027 / RUN-135 / DEC-167 / CHG-154 / LAB-CHG-126 / R09-BB-331~333
```

## AUTHORITATIVE LATEST HANDOFF — All-58 geometry gate passed / 2026-07-15

```text
Audited: 82 STL + 33 STEP.
Canonical raw STL: 58/58.
Raw/N40 topology: 58/58 closed 2-manifold, zero boundary/non-manifold edges.
Direct STEP: 33/33 available files import as one Inventor solid B-rep.
N40_BBOX_EXACT_20260715: 58/58, about 4.149 GB.
Historical Excel provenance: confirmed 29 / likely 29, separate from geometry readiness.
```

Key source decisions:

```text
C30 T7/T8/T9 ↔ alternate 40 mm: confirmed scale-equivalent.
individual_legacy_1cell 15x15x5 mm slabs: not full specimens.
T17 uses T19 revision 23294ad4 provisionally; alias remains likely.
T8/T9 are likely congruent under cube symmetry, so average-descriptor collision is structurally plausible.
```

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260715_GEOMETRY_SOURCE_FULL_VALIDATION_AND_CANONICAL_FREEZE.md
experiments/lab_001_xy_connection_20260626/reports/tables/R09-20260715_final_canonical_geometry_registry.csv
experiments/lab_001_xy_connection_20260626/reports/tables/R09-20260715_n40_canonical_processed_manifest.csv
experiments/lab_001_xy_connection_20260626/reports/figures/R09-20260715_geometry_validation_dashboard.png
```

Next:

```text
R1 re-review v2: rebuild geometry-y registry with execution/provenance separation,
split/exclude XRV1-F009~F012, validate a path-safe saved-PNG readback/deletion adapter,
then bounded C1/T8/T9/B3/L1 smoke. Full batch remains prohibited until that gate passes.
```

Current indices:

```text
PRM-027 / RUN-136 / DEC-168 / CHG-155 / LAB-CHG-127 / R09-BB-334~341
```

## AUTHORITATIVE LATEST HANDOFF — R1 v2 native smoke passed / 2026-07-15

```text
Models: B3, C1, L1, T8, T9.
Native slice/overlay readbacks: 4,005 / 4,000.
Readback, kernel-parity, deletion, temp-file, artifact-hash failures: all 0.
Deleted temporary PNG: 7,933; retained audit PNG: 72.
B3/C1/L1 prior native pixel lineage: exact parity 3/3.
```

Formula decision:

```text
F001-F006: confirmed new-schema traceable descriptors.
F007 Thickness: keep as utility candidate; reject as current historical-Excel parity formula/population.
F008 MassOri avg: likely parity candidate; five-model Excel rel-diff max 0.286%.
F009-F012: excluded/unresolved.
T8/T9: all nine F001-F008 rows remain within 1%; representation ambiguity persists.
```

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-RESLICE-002_R1V2_PATH_SAFE_NATIVE_SMOKE_20260715.md
experiments/lab_001_xy_connection_20260626/reports/tables/R09-RESLICE-002_model_gate_summary_20260715.csv
experiments/lab_001_xy_connection_20260626/reports/tables/R09-RESLICE-002_descriptor_result_20260715.csv
experiments/lab_001_xy_connection_20260626/reports/tables/R09-RESLICE-002_T8_T9_descriptor_collision_audit_20260715.csv
experiments/lab_001_xy_connection_20260626/reports/figures/R09-RESLICE-002_native_smoke_dashboard_20260715.png
```

Next:

```text
Prepare and run an all-58 resumable F001-F008 extraction factory in resource-aware chunks,
then perform x-x uniqueness/family coverage and grouped x-y utility analysis.
Do not add theta as an identity patch and do not execute F009-F012 yet.
```

Current indices:

```text
PRM-027 / RUN-137 / DEC-169 / CHG-156 / LAB-CHG-128 / R09-BB-342~348
```

## AUTHORITATIVE LATEST HANDOFF — CINT-08 local static pass / 2026-07-19

```text
runtime: KMK312 / Python 3.12.12
Training source notebooks: 9, immutable, JSON/AST audit only
method families: 5, output-specific and nonordinal
feature policy: B/C/L lattice-only blocks excluded from F/T; no zero imputation
evaluation: base_geometry_id-aware groups; nested/fixed selection
ensemble: complete outer-OOF predictions only
target policy: YPOL-GM-v0.1 confirmed; model_fit_authorized=false
numeric x/y: 0/0
model fit/prediction: 0/0
tests: 31/31 local, 114/114 cross-CINT, 21/21 harness
protected assets: 28/28 unchanged
status: local_static_contract_pass_model_replay_blocked
```

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/CINT-08_TRAINING_ENGINE_MODULARIZATION_NO_FIT_20260719.md
experiments/lab_001_xy_connection_20260626/factories/CINT-08/MERGE_PACKET.md
experiments/lab_001_xy_connection_20260626/reports/tables/CINT-08_training_method_plugin_registry_20260719.csv
experiments/lab_001_xy_connection_20260626/reports/tables/CINT-08_training_feature_block_registry_20260719.csv
experiments/lab_001_xy_connection_20260626/reports/tables/CINT-08_external_training_replay_gates_20260719.csv
```

Next:

```text
Local lane: CINT-09 thin orchestrator skeleton; no production execution.
External lane: approve official DatasetManifest and output-specific grouped replay.
Do not run DATASET-v0.1, x-x, selection, fit, inverse design or tournament.
```

Current indices:

```text
PRM-028 / RUN-158 / DEC-190 / CHG-177 / LAB-CHG-149 / R09-BB-417~423
```

## AUTHORITATIVE LATEST HANDOFF — CINT-09 local orchestrator pass / 2026-07-19

```text
runtime: KMK312 / Python 3.12.12
orchestrator: URP4-ORCHESTRATOR-v0.1
state: URP4-ORCHESTRATION-STATE-v0.1
CINT-01~08 local interfaces: 8/8 passed
DatasetManifest/model replay: 2/2 blocked external gates
resume: 0 validator calls for passed stages
quarantine/downstream block/independent progress/recovery: passed
tests: 33/33 local, 147/147 cross-CINT, 21/21 harness
protected assets: 28/28 unchanged
status: local_contract_pass_external_gates_open
```

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/CINT-09_THIN_ORCHESTRATOR_NO_PRODUCTION_EXECUTION_20260719.md
experiments/lab_001_xy_connection_20260626/factories/CINT-09/MERGE_PACKET.md
experiments/lab_001_xy_connection_20260626/reports/tables/CINT-09_stage_registry_20260719.csv
experiments/lab_001_xy_connection_20260626/reports/tables/CINT-09_external_gate_registry_20260719.csv
```

Next — control-tower correction:

```text
1. FAST: RUN-139 -> DATASET-XRV1-v0.1 -> y-blind T3 x-x.
2. STRICT: Excel/LEGACY-PY/image-pixel parity continues in parallel.
3. RESCUE: add slice/descriptor candidates only from measured representation gaps.
4. FUTURE P3: periodic-x/theta-x intake when provenance-complete data arrives.

Chuck authorized the bounded DATASET/X-X lane on 2026-07-19.
Model fit, feature promotion, inverse design and actual tournament remain locked.
```

Current indices:

```text
PRM-028 / RUN-159 / DEC-191 / CHG-178 / LAB-CHG-150 / R09-BB-424~429
```

## AUTHORITATIVE LATEST HANDOFF — DATASET-XRV1-v0.1 + T3 x-x / 2026-07-19

```text
runtime: KMK312 / Python 3.12.12
dataset: DATASET-XRV1-v0.1
manifest: DATASET::DATASET-XRV1-V0.1::sha256-35af779aff22
models / canonical rows / scalar players: 58 / 522 / 9
coverage: every player 58/58, B/C/L/F/T
feature redundancy: F005/F006 inverse-rank near-duplicate cluster
model near-collisions: T5/T6 and T8/T9
exact model duplicates: 0
y values / fits / predictions / promotions: 0 / 0 / 0 / 0
Dataset QA / output hashes / protected: 9/9 / 22/22 / 28/28 pass
status: passed_no_y_evidence_ready_for_control_tower_review
```

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260719-TOUR-C001_DATASET_XRV1_T3_XX_REPORT_20260719.md
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/data_factory/frozen/DATASET-XRV1-v0.1_manifest.json
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/analysis_factory/frozen/TOUR-C001-T3-001_candidate_xx_evidence.csv
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/analysis_factory/frozen/TOUR-C001-T3-001_collision_candidates.csv
```

Next:

```text
Preregister exact GM join/group/null/control policy, then run one bounded grouped
x-y replay. Do not promote a roster or claim inverse design yet. STRICT parity
continues in parallel; RESCUE targets measured gaps; periodic-x is future P3.
```

Current indices:

```text
PRM-028 / RUN-160 / DEC-192 / CHG-179 / LAB-CHG-151 / R09-BB-430~436
```

## PRIOR HANDOFF — T4 exact GM no-fit contract / 2026-07-19

```text
runtime: KMK312 / Python 3.12.12
run: TOUR-C001-T4-GM-001
dataset: DATASET-XRV1-GM-PREP-v0.1
dataset hash: b1a62ac1ee59a452e212fbac40025d11cf281b9fbbf6908d60db670279e372e4
X rows / exact GM rows: 58 / 54
excluded x-only: T5, T6, T10, T16
outer / inner folds: 5 / 20
candidate / promoted / active roster: 9 / 0 / not decided
QA / protected / unit contracts: 16/16 / 28/28 / 55/55
x-y metrics / fits / predictions: 0 / 0 / 0
status: merged_no_fit_one_bounded_T4_replay_next
```

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260719-TOUR-C001_T4_GM_XY_PREREGISTRATION_REPORT_20260719.md
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/contracts/TOUR-C001_T4_GM_XY_PREREGISTRATION_20260719.json
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/data_factory/frozen/DATASET-XRV1-GM-PREP-v0.1_manifest.json
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/merge/MERGE_PACKET_T4_GM_PREREG_20260719.md
```

Next: execute one bounded T4 grouped replay under this fixed contract. Do not
change thresholds, use random-row split, impute missing y, run a broad method
sweep, promote a feature, start T5+, or claim inverse design in that execution.
Master Ledger v0.2 remains canonical until replay review.

Current indices:

```text
PRM-028 / RUN-162 / DEC-194 / CHG-181 / LAB-CHG-153 / R09-BB-438~443
```

## AUTHORITATIVE LATEST HANDOFF — source-matched detailed-signal gate / 2026-07-20

```text
runtime: KMK312 / Python 3.12.12
run: TOUR-C001-T4R-SLICE-003A
models: B3 / C1 / L1 / F1 / F2
geometry: canonical N40, exact path/hash 5/5
configuration: P1000_S801 / 40 mm / z / endpoint / 0.05 mm
technical runs: 5/5 passed
slice / overlay / mapped rows: 4,005 / 4,000 / 200
selected values / applicable signals / clusters: 20 / 4 / 4
transient PNG deleted / remaining / audit retained: 8,005 / 0 / 30
decision: GO_SEPARATE_ALL58_SOURCE_MATCHED_CONTRACT
y / fits / predictions / promotions: 0 / 0 / 0 / 0
```

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260720-TOUR-C001_T4R_SLICE_003A_MATCHED_SOURCE_FIVE_MODEL_CONTROL_TOWER_REVIEW_20260720.md
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/contracts/TOUR-C001_T4R_SLICE_003A_MATCHED_SOURCE_FIVE_MODEL_PREREGISTRATION_20260720.json
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/analysis_factory/frozen/TOUR-C001-T4R-SLICE-003A_all58_go_hold_decision.csv
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/merge/MERGE_PACKET_T4R_SLICE_003A_20260720.md
```

Next:

```text
Freeze, then execute a resumable all-58 source-matched x-only exact image batch.
Keep each model's canonical geometry hash, PNG readback, component/pixel trace,
audit images and deletion ledger. Stop for x-only review before any y fit or
feature promotion. Continue L7 STRICT provenance in parallel.
```

Current indices:

```text
PRM-028 / RUN-168 / DEC-200 / CHG-187 / LAB-CHG-159 / R09-BB-477~482
```

## AUTHORITATIVE LATEST HANDOFF — all-58 source-matched exact x packet / 2026-07-20

```text
runtime: KMK312 / Python 3.12.12
run: TOUR-C001-T4R-SLICE-004
geometry/config: canonical N40 / P1000_S801 / 40 mm / z / endpoint / 0.05 mm
models: 58/58 complete (7 reused, 51 newly sliced)
slice / overlay / component rows: 46,458 / 46,400 / 3,279,507
candidate values: 2,320 = 58 × 40; finite 2,320/2,320
readback mismatch / transient PNG remaining: 0 / 0
independent QA / protected / manifest: 19/19 / 29/29 / 833/833
decision: accepted technical/source x packet; no scientific promotion
y / fits / selections / promotions: 0 / 0 / 0 / 0
```

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260720-TOUR-C001_T4R_SLICE_004_ALL58_SOURCE_MATCHED_EXACT_EXTRACTION_REPORT_20260720.md
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/contracts/TOUR-C001_T4R_SLICE_004_ALL58_SOURCE_MATCHED_EXACT_EXTRACTION_20260720.json
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/analysis_factory/frozen/TOUR-C001-T4R-SLICE-004_all58_direct_legacy_candidate_values.csv
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/analysis_factory/reports/TOUR-C001-T4R-SLICE-004_independent_QA.csv
```

Next: stop for review. All-58 x-only census, x-x, Excel parity, x-y, selection
and fitting require a separate task. Master Ledger v0.2 remains unchanged.

Current indices:

```text
PRM-028 / RUN-169 / DEC-201 / CHG-188 / LAB-CHG-160 / R09-BB-483~487
```

## AUTHORITATIVE LATEST HANDOFF — T3B all-58 x-only candidate census / 2026-07-20

```text
parent: SLICE-004 passed 19/19 QA, 29/29 protected, 833/833 manifest
runtime: KMK312 / Python 3.12.12
run: TOUR-C001-T3B
models / candidate schema / values: 58 / 240 / 13,920
lineage: 40 direct + 192 distribution-derived + 8 z-profile
missing: 0
primary / sensitivity / hold / rejected: 0 / 118 / 91 / 31
T8/T9: different on 108/118 combined coordinates but still rank-1 near collision
integrity: 13/13 QA, 29/29 protected, 20/20 manifest
y / x-y / selection / fits / promotions: 0 / 0 / 0 / 0 / 0
```

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260720-TOUR-C001_T3B_CONTROL_TOWER_REVIEW_20260720.md
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/contracts/TOUR-C001_T3B_ALL58_CANDIDATE_ENRICHMENT_AND_XONLY_CENSUS_20260720.json
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/analysis_factory/frozen/TOUR-C001-T3B_candidate_registry.csv
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/analysis_factory/frozen/TOUR-C001-T3B_all58_candidate_matrix.csv
experiments/lab_001_xy_connection_20260626/results/R09-20260720-TOUR-C001-T3B_NEXT_NESTED_FEATURE_SELECTION_PREREGISTRATION_DRAFT_20260720.md
```

Next: preserve T3B and review its draft. Any y access or nested selection needs
a new frozen y/row/group/split/holdout/fit-budget contract. Master Ledger v0.2
remains unchanged.

Current indices:

```text
PRM-028 / RUN-170 / DEC-202 / CHG-189 / LAB-CHG-161 / R09-BB-488~493
```

## AUTHORITATIVE LATEST HANDOFF — T3C exact-GM nested-selection preregistration / 2026-07-20

```text
run: TOUR-C001-T3C-GM-001
target: YPOL-GM-v0.1 / EXCEL_TRAINING_TOTAL_260503 / 총정리!GM
semantic: Max. Plateau stress / compression / maximize
row policy: 54 exact family_summary z rows; T5/T6/T10/T16 x-only
folds: 5 outer LOFO / 20 inner grouped
eligible candidates: 118 = direct 36 + distribution 74 + z-profile 8
hold / rejected / primary: 91 / 31 / 0
future fit ceiling: 9,470
integrity: 14/14 QA, 29/29 protected, 11/11 manifest
semantic y reads / x-y / selection / fits / promotion: 0 / 0 / 0 / 0 / 0
execution: locked; preregistration only
```

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260720-TOUR-C001_T3C_GM_CONTROL_TOWER_REVIEW_20260720.md
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/contracts/TOUR-C001_T3C_GM_NESTED_CANDIDATE_SELECTION_PREREGISTRATION_20260720.json
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/registries/TOUR-C001-T3C-GM-001_candidate_policy.csv
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/registries/TOUR-C001-T3C-GM-001_nested_selection_protocol.csv
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/registries/TOUR-C001-T3C-GM-001_fit_budget.csv
```

Next: do not read y automatically. A separate task must recheck contract/input
hashes, build the exact 54-row modeling view and authorize the bounded replay.
Master Ledger v0.2 remains unchanged.

Current indices:

```text
PRM-029 / RUN-171 / DEC-203 / CHG-190 / LAB-CHG-162 / R09-BB-494~500
```

## AUTHORITATIVE LATEST HANDOFF — T3D exact-GM bounded replay / 2026-07-20

```text
run: TOUR-C001-T3D-GM-NESTED-001
runtime: KMK312 / Python 3.12.12
target / exact rows: YPOL-GM-v0.1 / 54
candidates / fits: 118 sensitivity / 8,302 of 9,470
outer / inner folds: 5 / 20
selected OOF R2 / RMSE / Spearman: -0.351295 / 140.901739 / 0.133219
mean-null RMSE improvement: -14.5468%
descriptive gates: 3/6
candidate/config stability: 60% / 40%
T8/T9 observed/predicted delta: +10.206734 / -0.285713
integrity: independent QA 46/46; run manifest 22/22; parent/protected 58/58
promotion / roster / theta / inverse / tournament: 0 / 0 / 0 / 0 / 0
```

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260720-TOUR-C001_T3D_GM_CONTROL_TOWER_REVIEW_20260720.md
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/contracts/TOUR-C001_T3D_GM_BOUNDED_NESTED_REPLAY_EXECUTION_20260720.json
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/analysis_factory/frozen/TOUR-C001-T3D-GM-NESTED-001_outer_OOF_predictions.csv
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/analysis_factory/frozen/TOUR-C001-T3D-GM-NESTED-001_outer_selection.csv
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/analysis_factory/reports/TOUR-C001-T3D-GM-NESTED-001_independent_QA.csv
```

Next: preserve T3D and do not retune it. A new contract must choose between
L/domain-shift diagnosis, detailed T8/T9 rescue, or a family/next-y evaluation.
STRICT historical parity stays parallel. Master Ledger v0.2 remains unchanged.

Current indices:

```text
PRM-029 / RUN-172 / DEC-204 / CHG-191 / LAB-CHG-163 / R09-BB-501~507
```

## AUTHORITATIVE LATEST HANDOFF — T3E L-domain and angle-lineage diagnosis / 2026-07-20

```text
run: TOUR-C001-T3E-L-DOMAIN-ANGLE-001
runtime: KMK312 / Python 3.12.12
boundary: frozen T3D read-only diagnosis; no retuning
new fits / predictions / promotions: 0 / 0 / 0
L support shift: rejected as primary cause
purple q25 L / non-L centered Spearman: +0.287218 / -0.542857
L row / selected OOF SSE share: 37.037% / 59.263%
L selected-to-mean-null SSE: 2.41748
Angle IP/LIP: distinct related summaries
Angle LIP/LTP: exact duplicate lineage
T8/T9: unresolved; observed/predicted delta +10.206734 / -0.285713
integrity: run QA 10/10; independent 13/13; manifest 22/22; protected 58/58; control 24/24
```

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260720-TOUR-C001_T3E_L_DOMAIN_ANGLE_CONTROL_TOWER_REVIEW_20260720.md
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/contracts/TOUR-C001_T3E_L_DOMAIN_ANGLE_DIAGNOSIS_20260720.json
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/analysis_factory/reports/TOUR-C001-T3E-L-DOMAIN-ANGLE-001_diagnostic_verdicts.csv
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/analysis_factory/reports/TOUR-C001-T3E-L-DOMAIN-ANGLE-001_L_relation_direction.csv
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/analysis_factory/reports/TOUR-C001-T3E-L-DOMAIN-ANGLE-001_independent_QA.csv
```

Next: preregister `TOUR-C001-T3F_FAMILY_DOMAIN_ARCHITECTURE_PREREGISTRATION`
without fitting. Preserve T3D/T3E, keep Angle IP sensitivity-only, keep T8/T9
rescue and STRICT parity parallel, and do not inject theta/family ID, patch
NB-CURRENT, claim inverse design or start an actual tournament.

Current indices:

```text
PRM-030 / RUN-173 / DEC-205 / CHG-192 / LAB-CHG-164 / R09-BB-508~515
```

## AUTHORITATIVE LATEST HANDOFF — T3F family/domain architecture preregistration / 2026-07-20

```text
run: TOUR-C001-T3F-ARCH-001
runtime: KMK312 / Python 3.12.12
target identity: inherited YPOL-GM-v0.1; semantic value reads 0
future rows: exact 54 = B5/C14/F2/L20/T13
Lane G: unseen-family LOFO B/C/F/L/T
Lane K: known-family interpolation C/L/T; B/F insufficient
domain routes: B/C/L=BCL_LATTICE; F/T=FT_NONLATTICE
architectures: A0 null / A1 shared / A2 domain-gated / A3 shared+residual
backbones: B0 fixed F001 / B1 adaptive T3E diagnostic-4
future E1 fit ceiling: 420
E2 118-candidate search: locked
integrity: QA 16/16; independent 23/23; manifest 13/13; protected 58/58; control 25/25
y reads / fits / predictions / promotions: 0 / 0 / 0 / 0
```

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260720-TOUR-C001_T3F_FAMILY_DOMAIN_ARCHITECTURE_CONTROL_TOWER_REVIEW_20260720.md
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/contracts/TOUR-C001_T3F_FAMILY_DOMAIN_ARCHITECTURE_PREREGISTRATION_20260720.json
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/registries/TOUR-C001-T3F-ARCH-001_evaluation_lane_policy.csv
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/registries/TOUR-C001-T3F-ARCH-001_architecture_registry.csv
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/analysis_factory/reports/TOUR-C001-T3F-ARCH-001_independent_QA.csv
```

Next: only a separately authorized
`TOUR-C001-T3F-E1_BOUNDED_ARCHITECTURE_DIAGNOSTIC` may fit. Revalidate all
hashes and preserve the two lanes, backbones, architecture rules and 420-fit
ceiling. E2, theta/family-ID injection, promotion, NB-CURRENT/LEGACY-PY patch,
inverse design and actual tournament remain locked.

Current indices:

```text
PRM-031 / RUN-174 / DEC-206 / CHG-193 / LAB-CHG-165 / R09-BB-516~524
```

## AUTHORITATIVE LATEST HANDOFF — T3F-E1 bounded architecture diagnostic / 2026-07-20

```text
run: TOUR-C001-T3F-E1-ARCH-001
runtime: KMK312 / Python 3.12.12
fits / ceiling: 250 / 420
OOF rows / residual provenance: 202 / 558
Lane G: unseen-family LOFO B/C/F/L/T
Lane K: known-family interpolation C/L/T
A1: relative winner 4/4, descriptive only, not promoted
A2/A3: 12/12 challenger gates fail
T8/T9: unresolved; minimum delta error 10.206544
integrity: run 20/20; negative 20/20; independent 30/30; manifest 24/24; protected 58/58
E2 fits / promotions: 0 / 0
```

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260720-TOUR-C001_T3F_E1_CONTROL_TOWER_REVIEW_20260720.md
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/analysis_factory/reports/TOUR-C001-T3F-E1-ARCH-001_macro_architecture_summary.csv
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/analysis_factory/reports/TOUR-C001-T3F-E1-ARCH-001_success_gate_results.csv
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/analysis_factory/reports/TOUR-C001-T3F-E1-ARCH-001_independent_QA.csv
```

Next: no-fit
`TOUR-C001-T3G_REPRESENTATION_VS_TARGET_FAILURE_DECISION_PREREGISTRATION`.
Do not launch E2 automatically. Preserve parallel T8/T9 detailed-signal rescue
and STRICT historical parity. Theta/family identity, promotion,
NB-CURRENT/LEGACY-PY patch, inverse design and actual tournament remain locked.

Current indices:

```text
PRM-031 / RUN-175 / DEC-207 / CHG-194 / LAB-CHG-166 / R09-BB-525~533
```

## AUTHORITATIVE LATEST HANDOFF — T3G post-E1 strategy decision / 2026-07-20

```text
run: TOUR-C001-T3G-DECISION-001
runtime: KMK312 / Python 3.12.12
selected next: EXCEL_TRAINING_TOTAL_260503 / 총정리 / GX = Average stress
role: diagnostic target transfer; GM remains official objective
scores: GX 93 / representation design 78 / STRICT 70 / GM E2 40
future T3H: A0/A1, fixed B0/B1, Lane G/K separate, expected 40, ceiling 64
integrity: run 15/15; negative 12/12; independent 38/38; manifest 15/15; protected 58/58; control 39/39
new y reads / fits / predictions / promotions: 0 / 0 / 0 / 0
```

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260720-TOUR-C001_T3G_CONTROL_TOWER_REVIEW_20260720.md
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/registries/TOUR-C001-T3G-DECISION-001_branch_scorecard.csv
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/registries/TOUR-C001-T3G-DECISION-001_T3H_GX_target_transfer_draft.csv
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/analysis_factory/reports/TOUR-C001-T3G-DECISION-001_independent_QA.csv
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/merge/CONTROL_TOWER_MERGE_PACKET_TOUR-C001-T3G-DECISION-001.md
```

Next: `TOUR-C001-T3H_GX_TARGET_TRANSFER_PREREGISTRATION` only. Freeze eligible
GX rows, missingness and success gates before target-value access. Immediate
E2, broad target sweep, theta/family identity, promotion, protected-code patch,
inverse design and actual tournament remain locked.

Current indices:

```text
PRM-032 / RUN-176 / DEC-208 / CHG-195 / LAB-CHG-167 / R09-BB-534~542
```

## AUTHORITATIVE LATEST HANDOFF — T3H GX exact51 preregistration / 2026-07-20

```text
run: TOUR-C001-T3H-GX-PREREG-001
runtime: KMK312 / Python 3.12.12
target: EXCEL_TRAINING_TOTAL_260503 / 총정리 / GX = Average stress / MPa
role: diagnostic only; official GM objective preserved
source / GX-present / exact primary rows: 72 / 58 / 51
family counts: B5 C14 F2 L17 T13
held: L11/L12/L15 direction; T5-6 identity; L18-2/T10/T16 extras
future design: Lane G/K, A0/A1, fixed B0/B1, expected 40, ceiling 64
integrity: run 25/25; negative 20/20; independent 51/51; manifest 20/20; protected 58/58; control 52/52
accepted GX magnitudes / fits / predictions / promotions: 0 / 0 / 0 / 0
execution: locked
```

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260720-TOUR-C001_T3H_GX_CONTROL_TOWER_REVIEW_20260720.md
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/contracts/TOUR-C001_T3H_GX_TARGET_TRANSFER_PREREGISTRATION_20260720.json
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/registries/TOUR-C001-T3H-GX-PREREG-001_exact51_eligible_row_registry.csv
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/registries/TOUR-C001-T3H-GX-PREREG-001_success_interpretation_gates.csv
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/analysis_factory/reports/TOUR-C001-T3H-GX-PREREG-001_independent_QA.csv
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/merge/CONTROL_TOWER_MERGE_PACKET_TOUR-C001-T3H-GX-PREREG-001.md
```

Next: separate authorization may execute only
`TOUR-C001-T3H-GX-TARGET-TRANSFER-001` after hash revalidation. Do not alter
exact51, splits, gates, features or 64-fit ceiling. GM E2, broad target sweep,
direction/identity copying, promotion, inverse design and actual tournament
remain locked.

Current indices:

```text
PRM-033 / RUN-177 / DEC-209 / CHG-196 / LAB-CHG-168 / R09-BB-543~552
```

## AUTHORITATIVE LATEST HANDOFF — T3H GX bounded execution / 2026-07-20

```text
run: TOUR-C001-T3H-GX-TARGET-TRANSFER-001
runtime: KMK312 / Python 3.12.12
target: EXCEL_TRAINING_TOTAL_260503 / 총정리 / GX = Average stress / MPa
population: exact51 / B5 C14 F2 L17 T13
fits / ceiling: 40 / 64
G B0 / B1 R2: -0.066529 / -0.648777
K B0 / B1 R2: -0.077067 / -0.447063
verdict: likely_representation_wide_failure (adaptive, not universal)
integrity: execution 18/18; independent 26/26; refit 40/40; control 21/21; visual 4/4; protected 58/58
official target: GM Max. Plateau stress preserved
promotions: 0
```

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260720-TOUR-C001_T3H_GX_CONTROL_TOWER_REVIEW_20260720.md
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/analysis_factory/reports/TOUR-C001-T3H-GX-TARGET-TRANSFER-001_metrics.csv
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/analysis_factory/reports/TOUR-C001-T3H-GX-TARGET-TRANSFER-001_gate_results.csv
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/analysis_factory/figures/TOUR-C001-T3H-GX-TARGET-TRANSFER-001_lane_G_observed_vs_OOF.png
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/merge/CONTROL_TOWER_MERGE_PACKET_TOUR-C001-T3H-GX-TARGET-TRANSFER-001.md
```

Next: no-fit, y-blind topology/connectivity/z-profile representation and
source-lineage preregistration. Use existing raw slice/component tables; do not
fit, select or promote yet. Continue STRICT parity in parallel. Do not launch a
new target sweep, GM E2, theta/identity injection, NB-CURRENT/LEGACY-PY patch,
inverse design or actual tournament.

Current indices:

```text
PRM-033 / RUN-178 / DEC-210 / CHG-197 / LAB-CHG-169 / R09-BB-553~559
```

## AUTHORITATIVE LATEST HANDOFF — T3I representation/source diagnosis / 2026-07-20

```text
run: TOUR-C001-T3I-REPRESENTATION-SOURCE-001
preregistration: PRM-034
runtime: KMK312 / Python 3.12.12
input: retained SLICE-004 58-model slice/overlay tables; no new slicing
candidates: 42 = 30 sensitivity + 6 redundant hold + 6 source-QC only
T8/T9: T3B 0.075799 -> expanded 0.489332; rank 3/1653; still bottom-1%
source lane: 7 reused / 51 new-exact; 0 strong |Cliff's delta|>=0.8
integrity: execution 14/14; independent 17/17; formula 580/580; control 10/10; visual 2/2; protected 29/29
y access / fits / promotions: 0 / 0 / 0
```

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260720-T3I_CONTROL_TOWER_REVIEW.md
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/contracts/TOUR-C001_T3I_REPRESENTATION_SOURCE_DIAGNOSIS_20260720.json
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/analysis_factory/frozen/T3I_registry.csv
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/analysis_factory/frozen/T3I_matrix.csv
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/analysis_factory/reports/T3I_T8_T9.csv
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/merge/CONTROL_TOWER_MERGE_PACKET_T3I.md
```

Next: no-fit `TOUR-C001-T3J_GROUPED_GM_REPRESENTATION_REPLAY_PREREGISTRATION`.
Freeze the 30 technical candidates, grouped family-aware evaluation, nested
reduction/selection, null comparator, T8/T9 diagnostic and stop gates before
any y read or fit. Continue STRICT historical parity. Do not claim true 3D
connectivity, promote a feature, launch GM E2/target sweep, inject theta/ID,
patch protected code, start inverse design or execute the tournament.

Current indices:

```text
PRM-034 / RUN-179 / DEC-211 / CHG-198 / LAB-CHG-170 / R09-BB-560~566
```

## AUTHORITATIVE LATEST HANDOFF — STRICT-L7-002 evidence ceiling / 2026-07-21

```text
contract / run: PRM-040 / STRICT-L7-002
runtime: KMK312 / Python 3.12.12
frozen current models / comparable z models: 58 / 54
NB-CURRENT vs direct LEGACY-PY IP difference: 0.04111%
direct LEGACY-PY vs historical Excel IP difference: 21.53127%
direct LEGACY-PY vs historical Excel LTP difference: 0.001682%
formula defect / simple row swap: rejected / rejected
historical component/threshold/population provenance: likely
exact historical source/configuration: unresolved
new slicing / y / fits / deletions / promotions: 0 / 0 / 0 / 0 / 0
execution / independent / protected QA: 8/8 / 13/13 / 29/29
```

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260721-STRICT_L7_002_CONTROL_TOWER_REVIEW.md
experiments/lab_001_xy_connection_20260626/results/R09-20260721-STRICT_L7_002_HISTORICAL_SOURCE_CONFIGURATION_CROSSWALK_AUDIT_NOFIT.md
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/contracts/STRICT_L7_002_HISTORICAL_SOURCE_CONFIGURATION_CROSSWALK_AUDIT_NOFIT_20260721.json
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/analysis_factory/reports/STRICT_L7_002_summary.json
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/merge/MERGE_PACKET_STRICT_L7_002.md
```

Next: run `STRICT-L7-003` only if historical L7 slice PNGs, component table,
exact source revision or execution configuration is recovered. Otherwise close
the strict branch at its evidence ceiling, keep the L7 provenance flag and
preregister the next no-fit data/representation task. Do not change
NB-CURRENT/LEGACY-PY, delete L7, fit a new adaptive model, inject theta/identity,
claim inverse design or execute the tournament without a new contract.

Current indices:

```text
PRM-040 / RUN-187 / DEC-219 / CHG-206 / LAB-CHG-178 / R09-BB-624~630
```

## AUTHORITATIVE LATEST HANDOFF — T3Q frozen T3PX support/range anatomy / 2026-07-21

```text
contract / run: PRM-044 / RUN-191
runtime: KMK312 / Python 3.12.12
mode: frozen-artifact no-fit anatomy
selected fold / candidate: LOFO::L / MN3D::inertia_fraction_mid
L outside non-L training range: 12/20
range overlap / max robust-z: 0.036064 / 836365.142
frozen training scale: 1.021507e-4
prediction outside training-y range: 20%
held RMSE / mean-null ratio: 8.123743
top-two inner RMSE margin: 0.241731%
support/range extrapolation: confirmed
family transfer instability / winner fragility: likely / likely
new fit / refit / prediction / promotion: 0 / 0 / 0 / 0
QA: execution 12/12; independent 20/20; tables 8/8; control 26/26
```

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260721-T3Q_CONTROL_TOWER_REVIEW_AND_MERGE.md
experiments/lab_001_xy_connection_20260626/results/R09-20260721-T3Q_T3PX_SUPPORT_RANGE_FAMILY_TRANSFER_ANATOMY_NOFIT.md
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/contracts/T3Q_T3PX_SUPPORT_RANGE_FAMILY_TRANSFER_ANATOMY_NOFIT_20260721.json
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/analysis_factory/frozen/T3Q_selected_fold_decomposition.csv
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/analysis_factory/frozen/T3Q_L_selected_candidate_detail.csv
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/merge/MERGE_PACKET_T3Q_CONTROL.md
```

Next: preregister, but do not yet execute, a support-aware abstention/fallback
safety policy. Any replay on the same exact54 data is exploratory because T3Q
already inspected the failure. Continue STRICT image/pixel/component and
configuration traceability in parallel. Do not retrofit PRM-042, clip frozen
predictions, promote a feature, inject identity/theta as X, claim inverse
design or execute the actual tournament.

Current indices:

```text
PRM-044 / RUN-191 / DEC-223 / CHG-210 / LAB-CHG-182 / R09-BB-651~658
```

## AUTHORITATIVE LATEST HANDOFF — T3R support-aware safety policy / 2026-07-21

```text
contract / run: PRM-045 / RUN-192
runtime: KMK312 / Python 3.12.12
status: policy-only preregistration; execution locked
guard / evidence lanes / future gates / claims: 12 / 4 / 10 / 7
primary unsafe action: abstain with reason codes
sensitivity fallback: fold-training mean null
same exact54 validation: rejected; exploratory mechanism only
confirmatory lane: untouched structures + independently measured y
support-aware safety utility: unresolved
target read / fit / refit / prediction: 0 / 0 / 0 / 0
QA: prereg 12/12; negative 10/10; independent 18/18; control 20/20; visual 1/1
```

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260721-T3R_CONTROL_TOWER_REVIEW_AND_PREREGISTRATION_MERGE.md
experiments/lab_001_xy_connection_20260626/results/R09-20260721-T3R_SUPPORT_AWARE_SAFETY_POLICY_PREREGISTRATION_NOFIT.md
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/contracts/T3R_SUPPORT_AWARE_SAFETY_POLICY_PREREGISTRATION_NOFIT_20260721.json
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/registries/T3R_support_guard_policy.csv
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/registries/T3R_evidence_lane_policy.csv
experiments/lab_001_xy_connection_20260626/factories/TOUR-C001/merge/MERGE_PACKET_T3R_CONTROL.md
```

Next: do not execute T3R without a new authorization and do not treat exact54
as validation. Reconcile the already completed R09-SLICE-003 pixel/slice DOE
with canonical RUN-139/CINT-03 artifacts, then preregister one bounded STRICT
convergence execution. Do not repeat the DOE design or all-58 extraction.

Current indices:

```text
PRM-045 / RUN-192 / DEC-224 / CHG-211 / LAB-CHG-183 / R09-BB-659~666
```

## AUTHORITATIVE LATEST HANDOFF — R09-SLICE-005 STRICT convergence / 2026-07-21

```text
contract / run: PRM-046 / RUN-193
runtime: KMK312 / Python 3.12.12
status: bounded convergence preregistration merged; execution locked
panel: B3/C1/L1/L7/F1/F2/T8/T9
design: pixel 500/1000/2000 and slice 401/801/1601 as separate OFAT
cells: 40 total / 8 RUN-139 reuse / 32 pending
formula scope: F001-F006 primary; F007-F008 sensitivity; F009-F012 excluded
estimated new runtime: 5.42 h single-worker; hard ceiling 8 h
QA: 12/12; 10/10; 20/20; fixtures 5/5; control 20/20; visual 1/1
protected: 29/29
slice / Excel / y / fit / prediction: 0 / 0 / 0 / 0 / 0
```

Read first:

```text
experiments/lab_001_xy_connection_20260626/results/R09-20260721-SLICE-005_CONTROL_TOWER_REVIEW_AND_PREREGISTRATION_MERGE.md
experiments/lab_001_xy_connection_20260626/results/R09-20260721-SLICE-005_STRICT_CONVERGENCE_PREREGISTRATION_NOEXEC.md
experiments/lab_001_xy_connection_20260626/factories/R09-SLICE-005/contracts/R09-SLICE-005_STRICT_CONVERGENCE_PREREGISTRATION_NOEXEC_20260721.json
experiments/lab_001_xy_connection_20260626/reports/tables/R09-SLICE-005_execution_matrix_20260721.csv
experiments/lab_001_xy_connection_20260626/reports/tables/R09-SLICE-005_convergence_gates_20260721.csv
experiments/lab_001_xy_connection_20260626/factories/R09-SLICE-005/merge/MERGE_PACKET_R09-SLICE-005_CONTROL.md
```

Next: create a separate live-hash execution addendum. Run one duplicated B3 coarse canary on Legion5 before any LabPC factory. Do not recompute the eight RUN-139 baseline cells or execute the 32 pending cells without that gate. Passing later means resolution stability only.

Current indices:

```text
PRM-046 / RUN-193 / DEC-225 / CHG-212 / LAB-CHG-184 / R09-BB-667~674
```

## Current execution handoff — R09-SLICE-005 LabPC Google Drive factory

Use only the R1 packet:

`G:\내 드라이브\labfactory\URP4-1_R09_SLICE005_LABPC_FACTORY_GDRIVE_20260721_R1`

Run `00_DOCTOR_FIRST.cmd -> 01_INSTALL_LOCAL_FACTORY.cmd -> 02_RUN_OR_RESUME_FACTORY.cmd -> 03_CHECK_STATUS_AND_VERIFY.cmd -> 04_COLLECT_RESULTS_TO_GOOGLE_DRIVE.cmd`.

The packet computes on LabPC local storage and returns a verified ZIP plus manifest to `G:\내 드라이브\labfactory\returned_results`. It requires KMK312, `G:` and >=10 GiB Drive free at collection. Do not use the noncanonical first Drive copy. Actual cells remain 0/32; all convergence and downstream claims remain locked pending independent return audit.

Current indices: `PRM-050 / RUN-196 / DEC-228 / CHG-215 / LAB-CHG-187 / R09-BB-693~696`.

## Dual-track current state

- T3Q is already complete at `PRM-044 / RUN-191`; do not rerun it.
- STRICT: use the canonical Google Drive R1 LabPC packet; 0/32 cells have run.
- FAST/UTILITY: T3B bank 240 is frozen. `PRM-051` inventories 20 formula groups / 198 estimated candidates but authorizes zero value generation and zero y/fit/selection.
- STRICT and FAST are nonblocking and cannot overwrite each other's evidence. Direct 40 candidates are reproducible but remain not canonical.
- Next FAST task is a separate PRM-052 no-y execution contract, followed by an x-only census. Inverse design and actual tournament remain locked.

Current indices: `PRM-051 / RUN-197 / DEC-229 / CHG-216 / LAB-CHG-188 / R09-BB-697~704`.

## Current execution handoff — PRM-053 FAST x-only census merged

- PRM-052 is immutable failure evidence: duplicate FSE-003/FSE-019 candidate identity, zero values generated.
- PRM-053 generated 152 unique candidates × 58 models = 8,816 values and preserved the existing T3B 240-candidate bank. Combined x matrix: 392 candidates.
- New status: 95 sensitivity, 51 hold, 6 rejected. These are not an active roster.
- T8/T9 distance improved from 0.075799 in the existing space to 0.676258 in the new-only space, but combined distance 0.455142 remains rank 2/1653 and bottom 1%; ambiguity is reduced, not solved.
- Internal QA 12/12, formula replay 60/60, collision replay 3/3, independent QA 12/12 and protected assets 29/29 passed.
- y/fit/selection/promotion/inverse/tournament remain zero. PRM-054 is a no-execution planning draft only.
- STRICT remains independent and 0/32. Chuck's next physical action is Drive R1 CMD 00→04 on LabPC; AI's next task is to resolve and freeze PRM-054 before any FAST fit.

Current indices: `PRM-053 / RUN-198 / DEC-230 / CHG-217 / LAB-CHG-189 / R09-BB-705~710`.

## Current execution handoff — PRM-054 FAST no-fit contract merged

- Contract: `PRM-054_FAST_NESTED_ONE_ADDITIONAL_FEATURE_PREREGISTRATION_NOFIT_20260721.json`.
- Exact54 X-only experiment: fixed `X_Z/X_AI/X_AY` plus exactly one of 95 new PRM-053 sensitivity candidates.
- The prior T3B 118 candidates are excluded from repetition because T3D already tested them.
- Outer eligibility: B/C/F/L/T = 87/87/86/82/84; 82 candidates survive every outer fold.
- Future ceiling 5,770 fits; actual target magnitudes/fits/predictions/selections/promotions remain zero.
- QA: main 15/15, independent 16/16, negatives 10/10, control 20/20; protected 29/29; STRICT 0/32.
- Next AI task: PRM-055 live-hash execution authorization. Do not execute PRM-054 directly or change its contract.
- Next Chuck task: on LabPC run the canonical Drive R1 CMD 00→04 sequence for the independent STRICT lane.

Current indices: `PRM-054 / RUN-199 / DEC-231 / CHG-218 / LAB-CHG-190 / R09-BB-711~718`.

## Current execution handoff — PRM-055 valid negative merged

- PRM-055 ran once under live-hash authorization: 5,182/5,770 fits, exact54 outer LOFO and 20 inner folds.
- Dominant feature: `blue_fraction_union::tail_ratio_q90_q10`, selected in B/F/L/T; C chose `blue_area_mm2::tail_ratio_q90_q10`.
- Pooled R² -0.059099; RMSE 124.741119; Spearman 0.406366.
- Selected RMSE is worse than mean-null/backbone by 1.409%/6.302%; held-L is 45.128% worse than backbone.
- Mandatory gates 5/9. This is a valid negative result; no feature was promoted.
- Independent QA 14/14, control 22/22, visual 2/2, protected 29/29; STRICT 0/32.
- Next AI task: PRM-056 no-fit tail-ratio/source/support anatomy using frozen outputs only. Do not refit or change PRM-055.
- Next Chuck task: LabPC canonical Drive R1 CMD 00→04 for the independent STRICT lane.

Current indices: `PRM-055 / RUN-200 / DEC-232 / CHG-219 / LAB-CHG-191 / R09-BB-719~726`.

## Current execution handoff — PRM-056 no-fit tail-ratio anatomy merged

- Replayed both PRM-055 selected candidates from 58 retained `overlay_pixel_readback.csv` files, 800 layer-pairs each. Max value delta: fraction `5.68e-14`, area `2.91e-11`.
- Exact54 selected rows with q10 exactly zero and epsilon-bound denominator: `10/54`.
- Support attribution: none 26, tail-ratio-only 14, backbone-only 10, both 4. Aggregate PRM-055 support reproduces 54/54.
- Held-L RMSE stays `145.504068` selected versus `100.258810` backbone; L7 is the dominant failure.
- Formula implementation and numerical amplification are confirmed. Predictive promotion and unchanged tail-ratio reuse are rejected. Physical formula invalidity remains unresolved.
- QA: production 14/14, independent 14/14, control 25/25, visual 3/3, protected 29/29. STRICT remains 0/32.
- Next AI task: PRM-057 no-y/no-fit zero-aware engineering-definition preregistration or explicit rescue-branch closure; do not backcast/fit in that step.
- Next Chuck task: LabPC canonical Drive R1 CMD 00→04 for the independent STRICT lane.

Current indices: `PRM-056 / RUN-201 / DEC-233 / CHG-220 / LAB-CHG-192 / R09-BB-727~732`.

## Current execution handoff — PRM-057 zero-aware definition merged

- PRM-057 is definition-only: 39 definitions = 14 reversal-invariant core, 24 directional members in 12 mandatory red/blue pair blocks and one signed-balance hold.
- Exact zero occurrence is separated from positive-only magnitude. Epsilon, clipping, learned thresholds and zero imputation are prohibited; positive summaries need at least 80/800 layer-pairs.
- Candidate values, performance-y reads, fits, predictions and promotions are all zero. The adaptive schema is not confirmatory on current GM data.
- QA: main 20/20, independent 20/20, negative 8/8, control 25/25, visual 3/3, protected 29/29. STRICT remains 0/32.
- Next AI task: freeze a separate PRM-058 live-hash all-58 no-y value-generation and x-only census contract; do not execute PRM-057 directly.
- Next Chuck task: LabPC canonical Drive R1 CMD 00→04 for the independent STRICT lane.

Current indices: `PRM-057 / RUN-202 / DEC-234 / CHG-221 / LAB-CHG-193 / R09-BB-733~741`.

## Current directive handoff — descriptor expansion + import switch + FS merge + incoming compression

- Confirmed new directions: add structure descriptors broadly; add an early STL Import-path branch controlled by True/False; merge four feature-selection code families; prepare for new models plus compression-test results.
- The current laboratory computation is running externally. Do not modify its notebook/source/configuration; exact run identity remains unresolved until artifacts return.
- Broad candidate calculation is allowed, but formula/population/unit/applicability/missingness/confidence lineage and x-only QA are mandatory. All-candidate direct fitting is prohibited.
- New external packet provisional alias: `DATA-INCOMING-COMP-001`. Register/hash/crosswalk it before target inspection.
- Next AI task: PRM-058 live-hash all58 no-y zero-aware value generation and x-only census.
- Later order: candidate-bank integration -> NB-CURRENT development copy with STL import switch -> grouped/nested four-code feature-selection merge.

Current indices: `RUN-203 / DEC-235 / CHG-222 / LAB-CHG-194 / R09-BB-742~749`.

## Current execution handoff — PRM-058 all58 zero-aware x-only census merged

- PRM-058 calculated 38 executable definitions on 58 retained 800-pair overlay tables: 2,204 values and a 430-calculated-candidate combined bank.
- Status: 9 technical sensitivity / 30 hold. B1/B2 each lack >=80 positive pairs for 29 positive-summary candidates; values remain missing, never imputed.
- The nine technical candidates do not distinguish T8/T9: new-only distance 0. Combined distance 0.445821 remains rank 2/1653 and is slightly below existing 0.455142.
- QA: main 15/15, independent 10/10, formula replay 2204/2204, negative 8/8, control 20/20, visual 3/3, protected 29/29.
- y/fit/selection/promotion/new slicing/NB-CURRENT edit/laboratory-run mutation are all zero.
- Next AI task: no-y reconciliation of the 430 calculated candidates into a versioned formula/population/unit/applicability registry.
- Parallel later: development-copy STL Import True/False; grouped/nested four-code FS merge; immutable `DATA-INCOMING-COMP-001` intake.

Current indices: `PRM-058 / RUN-204 / DEC-236 / CHG-223 / LAB-CHG-195 / R09-BB-750~758`.

## Current execution handoff — XREG-v0.1 reconciliation merged

- PRM-059 failed closed before reconciliation output because exact dataframe equality was sensitive to CSV precision and row order; failure evidence is preserved.
- PRM-060 repaired only that comparator. Prefix parity passes after immutable model alignment with maximum delta `3.64e-12` under frozen `1e-10` tolerance.
- XREG-v0.1 has 431 registered identities, 430 calculated columns and 58 models. Its matrix is byte-identical to PRM-058.
- Governance: 220 technical sensitivity, 171 hold, 37 rejected, two redundant hold and one uncalculated orientation hold; 12 directional pair blocks are inseparable.
- QA: producer 17/17, independent 20/20, negative 5/5, control 10/10, protected 29/29.
- No y, fit, selection, promotion, new slicing, NB-CURRENT edit or running SLICE-005 mutation occurred.
- Current external job observed: `STRICT-CV::L7::CFG-P1000-S1601`; do not mutate its source/configuration. Await the returned manifest for authoritative identity.
- Next AI task: no-training four-code feature-selection method crosswalk and grouped/nested integration contract.
- NB development task: STL Import True/False branch remains blocked until the running-job identity is captured.
- Chuck/external input: return SLICE-005 artifacts; later deliver/register `DATA-INCOMING-COMP-001` when received from the doctor.

Current indices: `PRM-059 failed / PRM-060 / RUN-205 / DEC-237 / CHG-224 / LAB-CHG-196 / R09-BB-759~767`.

## Current execution handoff — PRM-061 FS4 static integration merged

- Reused CINT-08 and revalidated 9/9 immutable Training notebook hashes plus its 31/31 unit tests under KMK312.
- Confirmed methods 1–4 as four base competitors with 5/10/18/1 source recipes.
- `TRAIN-5TH-ALLTOGETHER/FIXED` is `FS4-COORDINATOR-05`: orchestration/reference only, not a fifth base competitor.
- Existing 5th CV winner scores are not final performance evidence; all future choices require a new outer family/group wrapper.
- XREG-v0.1 FS4 interface is 431 registered, 220 technical inner-fold candidates and 12 inseparable directional pair blocks. Future selection ceiling is six blocks/twelve scalar columns.
- Added `urp4/training/v0_2` and `FS4-INTEGRATION-v0.2` no-fit policies. QA is producer 18/18, independent 21/21, negative 10/10, control 15/15, protected 29/29.
- y/fit/prediction/selection/promotion/source edit/running SLICE mutation = 0/0/0/0/0/0/0.
- Next AI task: `FS4-002_XREG_GM_DATASET_MANIFEST_AND_JOIN_QA_NO_FIT`.
- Parallel external: SLICE-005 continues. Its returned identity blocks NB STL Import implementation only, not FS4 manifest preparation.
- Future execution: FS4-P1 representative pilot requires a separate live-hash authorization; P2/P3 remain conditional.

Current indices: `PRM-061 / RUN-206 / DEC-238 / CHG-225 / LAB-CHG-197 / R09-BB-768~777`.

## Current execution handoff — PRM-062 FS4 XREG-GM DatasetManifest merged

- Dataset object: `DATASET::DATASET-XREG-GM-FS4-V0.1::sha256-33aa35ce6c7f`.
- Trace/modeling preparation: 58×430 and exact54×technical220. Missing GM rows T5/T6/T10/T16 remain X-only; no imputation or replicate expansion.
- The technical view is finite 54×220. Exact X collisions are zero; T8/T9 are distinguishable but remain `PURGE::T8_T9`.
- A01/A02 failures are retained. A03 accepts schema vocabulary plus `1e-11` X / `1e-12` GM serialization tolerance and model-ID order-independent comparison only.
- QA: A03 10/10, independent 25/25, negative 8/8, control 10/10, protected 29/29.
- Fit/prediction/x-y metric/selection/promotion/source edit/SLICE mutation = 0.
- Next AI task: `FS4-P1_REPRESENTATIVE_COMPATIBILITY_EXECUTION_PREREGISTRATION` only; do not execute or select a winner.
- Parallel external: SLICE-005 continues; NB STL Import implementation waits for returned identity. Intake `DATA-INCOMING-COMP-001` immediately on delivery.

Current indices: `PRM-062 / RUN-207 / DEC-239 / CHG-226 / LAB-CHG-198 / R09-BB-778~786`.

## Current execution handoff — PRM-063 FS4-P1 no-execution preregistration merged

- Dataset remains `DATASET::DATASET-XREG-GM-FS4-V0.1::sha256-33aa35ce6c7f`, exact54×technical220.
- Four frozen compatibility probes: `weighted_blend_top2`, `stability_lasso_ridge`, `direct_omp_ridge`, `featureaware_partial_missing_ensemble`. They are not winners; method 5 remains coordinator/reference.
- Split identity: five leave-one-family-out outer folds and 20 deterministic inner grouped partitions. T8/T9 remain `PURGE::T8_T9`.
- Hard ceilings: 100 high-level evaluations, 4,000 estimator fits, six feature blocks and twelve scalar columns.
- QA: producer 24/24, independent 24/24, negative 10/10, control 12/12, protected 29/29.
- y read/fit/prediction/selection/promotion/execution authorization = 0/0/0/0/0/0.
- Next AI task: implement and unit/negative-test the four representative adapters without y access or fit, then freeze hashes for a separate execute-or-stop review.
- Parallel external: SLICE-005 continues; NB STL Import development still waits for returned run identity.

Current indices: `PRM-063 / RUN-208 / DEC-240 / CHG-227 / LAB-CHG-199 / R09-BB-787~795`.

## Current execution handoff — PRM-064 FS4-P1 no-fit adapters merged

- New isolated package: `urp4/training/p1_adapter_v0_1`; professor Training notebooks and frozen `v0_2` remain unchanged.
- Four static adapters compile A weighted-blend, B stability-Lasso/Ridge, C OMP/Ridge and D feature-aware partial-missing plans. No executable estimator layer exists in this version.
- Dataset/fold/candidate/pair/missingness guards fail closed. Methods A–C use common features; D may route a B/C/L specialist separately and never gives F/T zero-imputed lattice values.
- Plans: 20 real frozen-fold plans plus one synthetic routing fixture. Future conservative fit budget: `1,535/4,000`; actual y read/fit/prediction/selection/promotion: `0/0/0/0/0`.
- QA: unit 18/18, producer 24/24, independent 24/24, negative 9/9, control 12/12, protected 29/29.
- Next AI task: `FS4-P1-LIVE-HASH-EXECUTE-OR-STOP-REVIEW`. Review only; do not execute automatically.
- Parallel external: SLICE-005 remains running/observed only. NB STL Import development waits for returned run identity. New compression packet remains external-waiting.

Current indices: `PRM-064 / RUN-209 / DEC-241 / CHG-228 / LAB-CHG-200 / R09-BB-796~804`.

## Current execution handoff — PRM-065 stop-current decision merged

- Live identities `32/32`, protected originals `29/29`, KMK312/resources `10/10`, DatasetManifest/payload and 5 outer/20 inner folds all pass.
- Decision: `STOP_CURRENT_EXECUTION`. This is not a project stop.
- Blocking reasons: `AUTH-G12` executable estimator layer absent; `AUTH-G14` PRM-063/064 execution authority false.
- Active SLICE-005 chain was observed read-only as five process rows; it is a later resource-isolation hold, not a hash/source failure.
- Next authorized task: `FS4-P1-EXEC-LAYER-IMPLEMENTATION-NO-FIT` only. Implement constructors and fit-ledger guards without reading y, fitting or predicting.
- After executable-layer QA, repeat live-hash authorization. No real P1 run, P2/P3, winner selection or promotion before an explicit second GO.
- QA: producer/independent/negative/control `24/24·24/24·8/8·12/12`; actual y/fit/prediction `0/0/0`.

Current indices: `PRM-065 / RUN-210 / DEC-242 / CHG-229 / LAB-CHG-201 / R09-BB-805~813`.

## Current execution handoff — PRM-066 FS4-P1 executable layer merged, AUTH2 still locked

- New isolated package: `urp4/training/p1_exec_layer_v0_1` (`FS4-P1-EXEC-LAYER-v0.1`).
- Four guarded estimator families and 20 frozen method×outer-fold graphs now construct and clone.
- Every fit/predict path checks AUTH2 first; independent AST and sentinel checks pass `8/8` and `8/8`.
- Future fit ledger remains `1,535/4,000`; actual performance-y read, fit and prediction remain `0/0/0`.
- QA: unit/producer/independent/negative/control `13/13·24/24·24/24·8/8·12/12`; protected originals `29/29`.
- No permit is bundled. Next AI task: `FS4-P1-AUTH2-LIVE-HASH-REVIEW` only. Recheck live hashes/resources and issue explicit GO or STOP; do not execute automatically.
- Parallel lanes stay unchanged: active SLICE-005 is read-only, NB import work waits for returned run identity, and `DATA-INCOMING-COMP-001` remains external-waiting.

Current indices: `PRM-066 / RUN-211 / DEC-243 / CHG-230 / LAB-CHG-202 / R09-BB-814~822`.

## Current execution handoff — PRM-067 AUTH2 scientific PASS, resource HOLD

- Current live identities `36/36`, scientific/data/code gates `12/12`, protected assets `29/29`, PRM-066 postmerge `37/37`.
- Four adapters, 20 executable graphs and 8/8 authorization-first fit/predict methods are ready; future budget remains `1,535/4,000`.
- Five active SLICE-005 process rows were observed read-only on Legion5.
- Decision: `STOP_CURRENT_EXECUTION_RESOURCE_HOLD`. This is neither scientific failure nor permanent stop.
- No permit exists; actual performance-y read, fit and prediction remain `0/0/0`.
- Next AI task: `FS4-P1-AUTH2-RETRY-WHEN-SLICE005-IDLE`. Use a fresh process/resource snapshot; never reuse PRM-067 as a future permit.
- Alternative LabPC execution requires its own environment doctor and hash binding.

Current indices: `PRM-067 / RUN-212 / DEC-244 / CHG-231 / LAB-CHG-203 / R09-BB-823~831`.

## Current execution handoff — PRM-068 AUTH2 GO, bounded P1 not yet executed

- External SLICE-005 completed `32/32` cells and `160/160` table hashes; active compute is zero. Three paused wrappers are recorded noncompute shells.
- Current P1 scientific/data/code and resource gates pass `16/16`.
- Exact-file-hash permit: `FS4-P1-AUTH2-GO-20260722-001`; SHA-256 `016cf67b640e0c4e0ec414292070520444ae825ee9f5c4ac694b519ac1b2cb62`.
- Permit scope is frozen: `DATASET-XREG-GM-FS4-v0.1`, five outer/twenty inner grouped folds, methods 01–04, `FS4-P1-ADAPTER-v0.1`, `FS4-P1-EXEC-LAYER-v0.1`, max 1,535 prospective fits.
- QA: producer/independent/negative/control `24/24·24/24·10/10·12/12`; protected `29/29`.
- PRM-068 is permission only: actual performance-y read/fit/prediction `0/0/0`.
- Next AI task: `FS4-P1-RUN-BOUNDED-4METHOD`. Load the exact permit, run once under frozen limits, then stop for control-tower review.
- Parallel next: immutable SLICE-005 result intake/audit; NB Import development continues to wait for that frozen identity.

Current indices: `PRM-068 / RUN-213 / DEC-245 / CHG-232 / LAB-CHG-204 / R09-BB-832~841`.

## Current execution handoff — PRM-069 SLICE-005 return technically accepted; scientific review pending

- Returned ZIP: `G:\내 드라이브\labfactory\returned_results\R09_SLICE005_LABPC_RESULTS_Legion5_2026-07-22T010629_941+0900.zip`.
- Exact SHA-256: `5f68795816fe20151796ac50cbe3f8accf609fa252879c0922105b2b55b26e42`; ZIP CRC PASS.
- Content: 32/32 new cells, 8/8 frozen baselines, 160/160 raw table hashes, 40 cells × 9 scalars = 360 rows.
- Models: B3/C1/F1/F2/L1/L7/T8/T9. New configs: P500-S801, P1000-S401, P1000-S1601, P2000-S801; frozen P1000-S801 baselines retained.
- Original verifier fails because new rows use `scientific_state/config_sha256` and baseline rows use `population_id/state`. A standalone 18-field union-schema repair changed only the derived aggregate and zero raw descriptors.
- Manifest `bytes` is 37,894 smaller than the synchronized file, but exact SHA and CRC pass. Treat size as nonbinding metadata; do not edit the original manifest.
- QA: recovery 9/9, technical producer 24/24, archive readback 12/12.
- Scientific convergence, historical Excel parity and feature/model claims remain pending; y read/fit/prediction `0/0/0`.
- Next strict task: `SLICE005-CONVERGENCE-CONTROL-REVIEW` without y. NB-DEV STL Import is unblocked. PRM-068 bounded P1 remains authorized as a parallel next task.

Current indices: `PRM-069 / RUN-214 / DEC-246 / CHG-233 / LAB-CHG-205 / R09-BB-842~850`.

## Current execution handoff — PRM-070 SLICE convergence policy merged

- Frozen review population: B3/C1/F1/F2/L1/L7/T8/T9 under P500/P1000/P2000 and S401/S801/S1601 comparisons.
- Pixel convergence: strict `9/9`; slice convergence: strict `8/9`.
- Retain P1000-S801 for F001, F002 std, F003, F004 std, F006, F007 mean/std and F008 on this panel.
- Hold raw `XRV1-F005::mean`: it is a slice-step-dependent quantity. `F005/Δz` is a likely post-result diagnostic only and needs a new preregistration.
- P2000 is not the universal default for the current scalars; P500 remains an efficiency challenger.
- T8/T9 near-collision persists and L7 historical F008 outlier is not explained by pixel/slice resolution.
- QA: producer/independent/control `24/24·24/24·12/12`; figures `3/3`. y read/fit/prediction/promotion `0/0/0/0`.
- Next AI task: `FS4-P1-RUN-BOUNDED-4METHOD` under the exact PRM-068 permit. Stop after the frozen run for control-tower review.
- Parallel tasks: preregister F005-per-mm; NB-CURRENT development-copy STL Import. Do not delay P1 for either.

Current indices: `PRM-070 / RUN-215 / DEC-247 / CHG-234 / LAB-CHG-206 / R09-BB-851~861`.

## Current execution handoff — PRM-071 FS4-P1 completed; no winner and no P2

- Exact run: 54 models, five leave-one-family-out folds, four source-mapped compatibility methods, 216 OOF predictions.
- Fit accounting: 350 accepted reported fits / 1,535 prospective; three failed pre-result KMK312 processes may add at most three partial Ridge fits and produced no result artifacts.
- All four methods lost to the outer-train-mean null on pooled MAE and RMSE; pooled R² is negative for A/B/C/D.
- B and T improve locally, while held-L reverses all six selected-feature signs and degrades by about 50–51 MAE. F has only two rows.
- Method D is `common_only_degraded_probe_official_lattice_input_absent`; Method B retains numerical-stability warnings.
- QA: independent/control `24/24·12/12`; protected `29/29`; figures `2/2` reviewed.
- Decision: `STOP_P1_NO_WINNER_NO_P2`. No method/feature promotion, P2/P3 authorization or inverse-design claim.
- Next AI task: `PRM072_P1_FAILURE_ANATOMY_AND_P1B_PREREGISTRATION_NO_FIT`. Do not fit; first separate family/representation, numerical and missing-input causes.
- Parallel lanes remain separate: F005-per-mm y-blind preregistration; development-copy STL Import; incoming compression packet wait.

Current indices: `PRM-071 / RUN-216 / DEC-248 / CHG-235 / LAB-CHG-207 / R09-BB-862~873`.

## Current execution handoff — PRM-072 stops repeat P1; P1B-D conditionally locked

- Model activity: `0 fit / 0 refit / 0 new prediction`.
- All six pooled PRM-071 method-prediction pairs have Pearson `r ≥ 0.988036`; do not expand the optimizer grid on the same representation.
- Held-L: strong selected-feature sign conflict `4/4`; sign-transfer failure `confirmed`, support/range contribution `likely`.
- Selected-set median Jaccard is `0.267`; residual concentration remains explicit and no model row was removed.
- Same-data known-family replay is rejected: T3M failed `1/8` after 5,552 fits and T3N confirmed instability/generalization gap.
- Conditional contract: `FS4-P1B-D-LATTICE-SPECIALIST-INCREMENTAL-v0.1`; `execution_authorized=false` until official Type-B structural variables plus model-ID crosswalk arrive.
- QA: producer/independent/control `24/24·24/24·12/12`; protected `29/29`; figures `2/2`.
- Next AI task: `PRM073_NB_DEV_STL_IMPORT_TRUE_FALSE_IMPLEMENTATION` on a development copy. Do not edit approved NB-CURRENT or LEGACY-PY.
- Parallel: F005-per-mm no-y preregistration; `DATA-INCOMING-COMP-001` immutable intake when delivered.

Current indices: `PRM-072 / RUN-217 / DEC-249 / CHG-236 / LAB-CHG-208 / R09-BB-874~886`.

## Current execution handoff — PRM-073 NB-DEV STL Import True/False passed

- Approved `NB-CURRENT v0.2` is unchanged at SHA-256 `29131ce5…6980f`.
- New alias `NB-DEV`: `experiments/lab_001_xy_connection_20260626/notebooks/NB_DEV_v0_3_STL_IMPORT_TRUE_FALSE.ipynb`, SHA-256 `2b510e0d…e9b7a`.
- `STL_IMPORT_CONFIG["enabled"]=True`: external STL only, generation forcibly bypassed, source hash/bounds/size recorded.
- `False`: generated-candidate route retained; automatic generation is safe/off by default in the development copy.
- Real B3 reached the integrated descriptor runner: `descriptor_status=ok`, 27 numeric surface scalars, zero source mutation.
- Canonical N40 intake: 58/58 unique IDs, 58/58 40 mm, 58/58 path/hash gates.
- QA: unit/independent/protected `5/5·20/20·29/29`; full descriptor batch/y/fit/prediction `0/0/0/0`.
- Cross-ledger/Obsidian postmerge synchronization: `36/36 PASS`.
- `NB-DEV` is validated development, not a new approved canonical notebook.
- Next AI task: `PRM-074_F005_PER_MM_YBLIND_PREREGISTRATION`.
- Parallel external gates: official Type-B structural variables for locked P1B-D; immutable intake of promised new model/compression data.

Current indices: `PRM-073 / RUN-218 / DEC-250 / CHG-237 / LAB-CHG-209 / R09-BB-887~898`.

## Current execution handoff — PRM-074 F005/Δz replay passed as sensitivity only

- Candidate: `DER::overlay_layer_pair_variable::change_fraction_union::mean_per_mm`.
- Formula/unit: `XRV1-F005::mean / slice_spacing_mm`, `1/mm`; source adjacent-pair population preserved.
- Raw F005 remains a separate per-step scalar on `hold`.
- Slice fine median/q90/max SRD: raw `65.4157%/65.8798%/66.3426%`; normalized `1.4039%/2.6274%/3.4405%`.
- Normalized pixel/slice axes: `strict / strict`.
- Status: `likely / sensitivity_candidate`; primary/canonical promotion `0/0` because this is same-panel replay of a post-result hypothesis.
- QA: `24/24·20/20·12/12·29/29`; figures `2/2` inspected. y/fit/prediction/selection/new slicing `0/0/0/0/0`.
- Cross-ledger/Obsidian postmerge synchronization: `36/36 PASS`.
- Next AI task: preregister the next professor-priority NB-DEV integration/regression action; do not rerun this same F005 panel. Keep incoming compression data immutable and P1B-D locked pending official Type-B input.

Current indices: `PRM-074 / RUN-219 / DEC-251 / CHG-238 / LAB-CHG-210 / R09-BB-899~908`.

## Current execution handoff — PRM-076 broad literature pool and equal-qualification contract passed

- PRM-075 discovery has been widened beyond materials mechanics to stochastic/integral geometry, topology, graph theory, mathematical morphology, spectral geometry, harmonic analysis and computer vision.
- Registered evidence: `34` sources and `33` candidate groups (`LIT-X001~X033`). Literature registration is not technical qualification.
- Six first-wave formulas are frozen: `X001/X002/X003/X004/X005/X016`.
- Every candidate is locked behind the same y-blind gates: lineage, units, synthetic truth, independent replay, representative panel, resolution, full-58 coverage/variation, redundancy and collision.
- Current equal-qualified candidates: `0`; active roster/promotion: `0/0`; performance-y/model fit: `0/0`.
- QA: producer/independent/protected `21/21·28/28·29/29`.
- Next AI task: `PRM-077_FIRST_WAVE_SYNTHETIC_TRUTH_AND_COST_CANARY`. Do not calculate all 33 groups or full 58 before the canary review.

Current indices: `PRM-076 / RUN-221 / DEC-253 / CHG-240 / LAB-CHG-212 / R09-BB-922~934`.

## Current execution handoff — PRM-077 first-wave synthetic truth and cost canary passed

- Executed only formula-frozen `LIT-X001/X002/X003/X004/X005/X016` on 10 synthetic fixtures and one noncanonical B3 cost canary.
- Synthetic truth `102/102`; axis permutation `7/7`; B3 total canary `6.032738 s`.
- Attempt A01 stopped at `13/15`: corrected a two-cavity complement Euler oracle and float32 fabric accumulation; thresholds and candidate formulas were unchanged. A02 is accepted.
- Producer/independent/protected QA: `15/15·24/24·29/29`.
- This is synthetic/axis/cost evidence only. Equal-qualified/active/promoted remain `0/0/0`; y/fit remain `0/0`.
- Next AI task: `PRM-078_FIRST_WAVE_FIXED_DOMAIN_REPRESENTATIVE_PANEL`. Use B3/C1/F1/F2/L1/L7/T8/T9 and review before V128/V192 or full-58.

Current indices: `PRM-077 / RUN-222 / DEC-254 / CHG-241 / LAB-CHG-213 / R09-BB-935~943`.

## Deferred research incubator — IDEA-INC-001 network and deformation-path descriptors

- Chuck's side-session hypothesis is preserved in the internal roadmap, not the professor roadmap.
- Static graph/spatial/multiscale ideas already overlap PRM-076; do not duplicate them as new candidates without a lineage crosswalk.
- New future lane: `theta -> G0 -> G(strain,time) -> x(strain,time) -> y`, including buckling/contact event timing and graph/path robustness changes.
- Status: static overlap `confirmed`; dynamic discrimination value `likely`; data source, graph identity and cost `unresolved`; immediate nano/full-dynamic expansion `rejected for current scope`.
- Do not activate before traceable deformation snapshots and frozen family-specific graph/synthetic/resolution contracts exist.
- Active next task remains `PRM-078_FIRST_WAVE_FIXED_DOMAIN_REPRESENTATIVE_PANEL`.

Incubator indices: `IDEA-INC-001 / DEC-255 / CHG-242 / LAB-CHG-214 / R09-BB-944~946`.

## Current execution handoff — PRM-078 fixed-domain representative panel passed

- Executed canonical B3/C1/F1/F2/L1/L7/T8/T9 at fixed 40 mm V64/V96 only; 16 masks and 1,392 scalar rows.
- Producer/independent/protected QA `25/25·28/28·29/29`; exact mask/value replay `16/16·192/192`.
- `LIT-X004`: `panel_pair_stable_not_final`; it does not separate T8/T9.
- `LIT-X001/X003/X005/X016`: `panel_pair_unresolved`; preserve rather than reject whole groups.
- `LIT-X002`: `formula_physical_scale_patch_required`; raw index-based outputs remain diagnostic and must not be silently overwritten.
- T8/T9 all-wave RMS `0.111346`, but rank `1/28`; resolution-unresolved X005 fabric drives separation, so collision status remains unresolved.
- Equal-qualified/active/promoted `0/0/0`; y/fit/selection `0/0/0`; V128/V192/full58 not executed.
- Next AI task: `PRM-079_FIRST_WAVE_FAILURE_ANATOMY_AND_V128_PREREGISTRATION`. Freeze X002 physical-lag lineage and fabric invariant policy before authorizing bounded V128.

Current indices: `PRM-078 / RUN-223 / DEC-256 / CHG-243 / LAB-CHG-215 / R09-BB-947~953`.

## Current execution handoff — PRM-079 failure anatomy and V128 preregistration passed

- Classified all `87/87` PRM-078 outputs into explicit numerical failure mechanisms; judgments are `26 confirmed / 55 likely / 6 unresolved`.
- Versioned `LIT-X002-PHYS-v0.1` without overwriting the PRM-077 index lineage. Common `0:2.5:20 mm` lags are exact integer shifts at V64/V96/V128.
- Reused the 16 retained masks only: `288` child diagnostic rows and `18` output summaries; no new raster was generated.
- X002 physical units are fixed, but `S2_i(r=5 mm)` remains resolution-sensitive/near-zero for C1 and especially T8/T9. Do not claim convergence.
- Versioned `LIT-X005-COND-v0.1`: eigenvalues/FA core, diagonals/guarded DA sensitivity, off-diagonals/v1/trace diagnostic.
- Producer/independent/protected QA `29/29·30/30·29/29`; independent X002 replay `288/288`.
- Attempts A01/A02 preflight-rejected, A03 QA-rejected, A04 logic-rejected, A05 accepted; quarantines preserved.
- V128/V192/full58/y/fit/selection/promotion executed `0/0/0/0/0/0/0`.
- Next AI task: `PRM-080_FIRST_WAVE_CHILD_TRUTH_AND_BOUNDED_V128_CONFIRMATION`. Run X002 child truth first, then exactly eight V128 models if preflight passes.

Current indices: `PRM-079 / RUN-224 / DEC-257 / CHG-244 / LAB-CHG-216 / R09-BB-954~960`.

## Current execution handoff — PRM-080 truth-first bounded V128 passed

- `LIT-X002-PHYS-v0.1` passed independent analytic truth `78/78` and slab axis permutation `16/16` before canonical geometry access.
- Exactly B3/C1/F1/F2/L1/L7/T8/T9 were rasterized at fixed-domain V128; outputs are 8 masks, 696 preserved parent rows and 144 physical-lag child rows.
- Representative V64/V96/V128 group gate: X001/X002/X003/X004/X016 `panel_triplet_confirmed`; X005 `panel_triplet_unresolved` because core fraction is 3/4 (`lambda3` top-2 overlap 0.5).
- Independent QA: `25/25`; exact masks `8/8`; parent anchors `160/160`; X002 child values `144/144`; protected assets `29/29`.
- T8/T9 remains the nearest all-core pair (`RMS=0.0075237374`, rank `1/28`); representation collision is not resolved.
- Attempts A01/A02 are `rejected_partial`, A03 accepted. A01 artifacts are quarantined; no formula, lag, threshold, model scope or resolution contract changed.
- Equal-qualified/active/promoted remain `0/0/0`; V192/full58/y/fit/selection executed `0/0/0/0/0`.
- Next AI task: `PRM-081_FIRST_WAVE_FULL58_YBLIND_CENSUS_PREREGISTRATION`. Freeze eligible outputs, coverage/redundancy/collision rules and stop conditions; do not execute full58 in the preregistration task.

Current indices: `PRM-080 / RUN-225 / DEC-258 / CHG-245 / LAB-CHG-217 / R09-BB-961~967`.

## Current execution handoff — PRM-081 full-58 y-blind census contract passed

- Froze the canonical population at `58` models: B5/C14/F2/L20/T17, fixed-domain V128, 40 mm, pitch 0.3125 mm.
- Froze `89` persisted outputs/model (`5,162` future rows): 38 core outputs, of which 30 are `census_primary` and 8 remain explicit holds; 34 sensitivity and 17 diagnostic outputs are trace-only.
- The later census must compare all 38 core outputs against the frozen 430-candidate XREG-v0.1 bank and report coverage, variation, exact/proportional/correlation redundancy, family support and all 1,653 model-pair distances.
- Frozen near-collision threshold: robust RMS `<=0.10`; this is a diagnostic flag, not a success target. T8/T9 remains a mandatory diagnostic pair.
- Family shards B/C/F/L/T may resume per model, but incomplete or hash-mismatched shards cannot merge. The eight PRM-080 masks may be reused only by exact hash; 50 new masks require a separately indexed execution authorization.
- Producer/independent QA `24/24·29/29`; roster replay `89/89`; negative fail-closed fixtures `12/12`; geometry/protected hashes `58/58·29/29`.
- New masks/descriptor values/y/fit/selection/promotion remain `0/0/0/0/0/0`; execution authorization is `false`.
- Next AI task: `PRM-082_FIRST_WAVE_FULL58_RUNNER_IMPLEMENTATION_AND_LIVE_HASH_AUTHORIZATION_NO_EXECUTION`. Implement and test the runner, bind live hashes, and perform an execute-or-stop review without running the full-58 census.

Current indices: `PRM-081 / RUN-226 / DEC-259 / CHG-246 / LAB-CHG-218 / R09-BB-968~974`.

## Current execution handoff — PRM-082 guarded full-58 runner and live-hash permit passed

- Implemented a KMK312-only, fixed-domain V128 runner for the frozen 58-model/89-output PRM-081 contract. It is family-sharded B/C/F/L/T and resumes only from hash-valid per-model atomic markers.
- The eight PRM-080 masks are reused only at exact hash. The remaining 50 models are rasterized only inside a permitted PRM-083 `run-shard` action.
- The runner preserves partial blocks in quarantine, rejects source/mask/config/code drift and rejects merge unless all 58 blocks contain exactly 89 unique candidate rows.
- Merge implementation includes 5,162 all-output rows, 2,204 core rows, XREG-v0.1 cross-bank redundancy and 1,653 pair distances for both primary30 and core38 representations.
- Producer/independent QA `25/25·25/25`; negative permits `7/7`; B3 parity `89/89`; eight-mask independent formula parity `712/712`; protected assets `29/29`.
- A01's `24/25` was a verifier-semantics error for two Git directory guards; A02 is accepted without any scientific-code or source change.
- Resource preflight: estimated full run about `7.66 min` at 1.5x safety factor, free disk `87.85 GiB`, other Python jobs `0`.
- PRM-083 exact-hash permit decision is `GO_NEXT_INDEXED_EXECUTION`; PRM-082 itself generated no new mask/value and did not access y, fit, select or promote.
- Next AI task: `PRM-083_FIRST_WAVE_FULL58_YBLIND_EXECUTION_AND_CENSUS`. Execute B/C/F/L/T shards under the exact permit, independently replay, merge only complete blocks, then stop for scientific review.

Current indices: `PRM-082 / RUN-227 / DEC-260 / CHG-247 / LAB-CHG-219 / R09-BB-975~981`.

## Current execution handoff — PRM-083 full-58 y-blind census completed

- Executed the frozen B/C/F/L/T shards under the exact-hash permit: `58/58` model blocks, eight exact mask reuses, 50 new V128 rasters, no retry/quarantine/failure.
- Merged `5,162` all-output rows and `2,204` core rows. Independent replay passed masks `58/58`, formula anchors `1102/1102`, X002 children `1044/1044`, coverage `89/89`, collisions `3306/3306`, redundancy `278/278` and protected assets `29/29` (`15/15` QA).
- All 30 `census_primary` outputs pass finite coverage and variation over all 58 models. This is technical full-population support, not feature promotion.
- Raw cross-bank redundancy reports 266 proportional matches, but all are zero-slope degeneracies against seven all-zero XREG columns; interpretable varying-XREG redundancy is `0`.
- Primary30 retains five near-collision pairs. T8/T9 is closest at robust RMS `0.000840`; T5/T6 is second at `0.001222`.
- Adding eight held outputs removes threshold-level collisions, but `LIT-X005::lambda2` accounts for `99.94%` of T8/T9 core squared distance. X005 remains resolution-held and cannot be promoted yet.
- Performance y / fitting / selection / promotion remain `0/0/0/0`.
- Next AI task: `PRM-084_FIRST_WAVE_CANDIDATE_LEVEL_TECHNICAL_QUALIFICATION_AND_X005_RESOLUTION_RESCUE_PREREGISTRATION`. Freeze the candidate-level qualification and X005 resolution-rescue contract; do not access y or promote features.

Current indices: `PRM-083 / RUN-228 / DEC-261 / CHG-248 / LAB-CHG-220 / R09-BB-982~989`.

## Current execution handoff — PRM-084 candidate/X005 rescue contract frozen

- Separated X005 group status from individual-output status. The group remains unresolved because `lambda3` is unresolved, while `lambda2` itself was individually strict on the existing V64/V96/V128 panel.
- Disclosed `lambda2` as a post-result confirmatory target: it was chosen after PRM-083 showed `99.94%` T8/T9 core-distance contribution; that observation is not independent proof.
- Preserved all 89 candidates. Thirty primaries enter candidate-level technical review, but none is technically qualified, selected or promoted in PRM-084.
- Converted the 12 interpretable internal relations into mandatory redundancy blocks for later leakage-safe candidate handling.
- Frozen a 13-model rescue panel: prior eight anchors plus L13/L17/L18/T5/T6. A future separately permitted run may create only ten masks (V64/V96 for those five models); all V128 and prior-anchor masks must be exact reuses.
- Frozen candidate gates CQ01~CQ06 and rescue gates XR01~XR08, including tensor physics, 13/13 lambda2 V96-V128 stability, rank preservation and T8/T9 plus T5/T6 rescue above RMS 0.10 at all three resolutions.
- Producer/independent/negative/protected QA: `13/13·20/20·12/12·13/13`. New masks/values/y/fit/selection/promotion are all zero; execution authorization false.
- Next AI task: `PRM-085_X005_LAMBDA2_COLLISION_PANEL_RESOLUTION_RESCUE_RUNNER_AND_LIVE_HASH_REVIEW_NO_EXECUTION`. Implement/test/hash-bind only; do not generate masks yet.

Current indices: `PRM-084 / RUN-229 / DEC-262 / CHG-249 / LAB-CHG-221 / R09-BB-990~997`.

## Current execution handoff — PRM-085 guarded X005 rescue runner ready

- Implemented a KMK312-only, permit-gated runner for the frozen 13-model × V64/V96/V128 X005 panel: 39 cells, 29 exact artifact reuses and at most 10 future masks.
- The runner emits only the 13 `LIT-X005` surface-normal fabric scalars and requires atomic markers plus a 507-row complete merge. Partial work quarantines; source/mask/config/code drift fails closed.
- Guard review corrected the frozen gate to literal top 2 and made pair-level delta gates row-order independent. Live scope content, the exact ordered 39-cell permit roster and the ten-mask cap are independently bound.
- Producer/independent QA `11/11·24/24`; formula parity `377/377` with maximum absolute error `2.220446049250313e-16`; negative authorization/config tests `8/8·15/15`; protected inputs `12/12`.
- PRM-085 created no mask/value and did not read y, fit, select or promote. Lambda2 remains a disclosed post-result confirmatory hypothesis, not a qualified feature.
- Next AI task: `PRM-086_X005_LAMBDA2_COLLISION_PANEL_RESOLUTION_RESCUE_EXECUTION_AND_REVIEW`. Execute only the exact permit, merge all 39 valid blocks, independently replay and stop for scientific review.

Current indices: `PRM-085 / RUN-230 / DEC-263 / CHG-250 / LAB-CHG-222 / R09-BB-998~1005`.

## Current execution handoff — PRM-086 lambda2 collision rescue rejected and held

- Executed the exact 13-model × V64/V96/V128 permit: `39/39` atomic cells, 29 reuse paths, exactly ten new masks and `507/507` merged X005 values.
- Independent replay passed `15/15`: marker hashes `39/39`, X005 formulas `507/507`, and source-STL reraster of all generated masks `10/10` with zero voxel mismatches.
- Frozen gate pattern: `XR01 PASS · XR02 PASS · XR03 PASS · XR04 FAIL · XR05 FAIL · XR06 FAIL · XR07 PASS · XR08 PASS`.
- Lambda2 is individually stable from V96 to V128 (`13/13`, maximum SRD below 0.70%), but the top-2 set changes and nearly equal pair differences are unstable.
- T8/T9 keeps delta sign but magnitude SRD is `189.97%/118.01%` and V96 fails rescue. T5/T6 passes magnitude at each resolution but changes delta sign and has `44.04%` V96–V128 magnitude SRD.
- Decision: reject lambda2 as a stable general collision-rescue feature; retain it only as diagnostic/sensitivity hold. X005 remains unresolved. y/fit/selection/promotion remain zero.
- Next AI task: `PRM-087_SECOND_WAVE_REPRESENTATION_RESCUE_PREREGISTRATION_NO_Y`. Return to the literature registry and preregister orthogonal topology/connectivity/spatial-distribution candidates before calculating them.

Current indices: `PRM-086 / RUN-231 / DEC-264 / CHG-251 / LAB-CHG-223 / R09-BB-1006~1015`.

## Current execution handoff — PRM-087 second-wave representation policy frozen

- Returned to the pre-existing PRM-075/076 literature registry after the X005/lambda2 rescue failed; no post-result candidate was invented from T8/T9 or T5/T6 alone.
- Frozen four orthogonal starter groups and 37 scalar outputs: `LIT-X017` Betti/topology 6, `LIT-X009` exact same-cluster correlation 18, `LIT-X012` lacunarity 5, and `LIT-X023` structure factor 8.
- `LIT-X028` is retained only as an expected-S2-redundancy negative control. `LIT-X033` and higher-cost skeleton/PH/ECT/mincut routes remain deferred.
- Frozen exact 40 mm domain, phase/connectivity/boundary policies, 2.5/5/10 mm physical lags or windows, 18 synthetic fixtures, 15 technical gates and the missing scalar-pass/rank-pair-fail outcome branch.
- T8/T9 and T5/T6 remain mandatory diagnostics but cannot select a candidate by themselves. X017↔X004 and X023↔X002 redundancy audits are mandatory.
- Producer/independent/negative/protected QA: `12/12·25/25·12/12·10/10`. New real-model masks/values/y/fit/selection/promotion are all zero; execution authorization false.
- Next AI task: `PRM-088_SECOND_WAVE_SYNTHETIC_TRUTH_AND_COST_CANARY_EXECUTION`. Execute synthetic fixtures and runtime/memory canaries only, then stop for review before any real model.

Current indices: `PRM-087 / RUN-232 / DEC-265 / CHG-252 / LAB-CHG-224 / R09-BB-1016~1025`.

## Current execution handoff — PRM-088 synthetic truth and cost canary passed

- Executed only the 23 frozen V64 synthetic variants and 12 synthetic cost cells across V64/V96/V128; no real project geometry was read.
- All 18/18 analytic, exact-policy, ordering and axis truth fixtures pass for LIT-X017/X009/X012/X023.
- Determinism and axis behavior pass `4/4·4/4`. Independent implementations reproduce `228/228` scalar values and independently re-evaluate `18/18` truth fixtures.
- The homometric X009 fixture holds S2 equal at all three frozen x-lags while C2 differs, establishing synthetic connectivity information beyond S2.
- All 12/12 cost canaries stay below the frozen 120 s / 8 GiB safety stops. These are synthetic canaries, not a full-58 runtime promise.
- Q01 is preserved as a rejected verifier-only attempt: paired NaN axis outputs were initially treated as unequal; Q02 fixes only the equality predicate and changes no mask, formula, threshold or value.
- All four groups are `likely` and eligible for a separately preregistered real-model resolution panel. No group is selected or promoted, and PRM-089 is not automatically authorized.
- Next AI task: `PRM-089_SECOND_WAVE_13MODEL_RESOLUTION_PANEL_PREREGISTRATION_AND_RUNNER_NO_EXECUTION`.

Current indices: `PRM-088 / RUN-233 / DEC-266 / CHG-253 / LAB-CHG-225 / R09-BB-1026~1034`.

## Current execution handoff — PRM-089 second-wave panel prepared; PRM-090 permit not executed

- The frozen real-panel scope is `B3,C1,F1,F2,L1,L7,T8,T9,L13,L17,L18,T5,T6` at V64/V96/V128: 39 cells, 13 fixed-40 source STL, 39 existing hash-verified masks, **zero** new-mask allowance.
- The runner will emit 37 formula-frozen LIT-X017/X009/X012/X023 outputs per cell, so the only permitted complete merge has 1,443 rows. It writes atomic cell markers, quarantines incomplete blocks and rejects partial merge/source/mask/permit/hash drift.
- Formula-gate policy is frozen: 6 topology values need exact V96=V128 agreement across all 13 finite models; 31 continuous values need ≥11 common models, median/p90 SRD ≤5%/10%, and Spearman ≥0.90. Undefined values must have a declared population reason; no imputation.
- Preparation/live-hash/independent QA passed `12/12·7/7·30/30`; 14 permit/config mutation attempts fail closed. The PRM-090 permit is valid but no `run-cell` or `merge` action has been executed.
- This is technical execution readiness, **not** qualification, selection, Excel parity or x–y evidence. T8/T9 and T5/T6 are mandatory diagnostics only, never sole selectors.
- Next AI task: `PRM-090_SECOND_WAVE_13MODEL_RESOLUTION_PANEL_EXECUTION_AND_REVIEW`. Use KMK312, rerun `doctor`, execute exactly the permit scope, independently replay and stop for scientific review.

Current indices: `PRM-089 / RUN-234 / DEC-267 / CHG-254 / LAB-CHG-226 / R09-BB-1035~1043`.

## Current execution handoff — PRM-090 second-wave real-panel technical review complete

- The exact KMK312 permit executed `39/39` fixed-40 V64/V96/V128 reuse-only cells and merged `1,443/1,443` LIT-X017/X009/X012/X023 values. New masks, y access, fitting, selection and promotion remain zero.
- Independent code reproduces markers/formulas/resolution/pairs `39/39·1,443/1,443·37/37·74/74`; QA is `13/13`. No cell was quarantined.
- Resolution result: 19 outputs are `likely_resolution_stable_not_qualified`; 18 are `hold_resolution_or_rank_gate`. X012 lacunarity is 5/5 stable. X009 has six stable C2 values, while Q values are held because constant vectors make Spearman undefined. X017 has beta0 only; X023 has six stable outputs but holds low-k and entropy.
- T8/T9 and T5/T6 each have zero complete pair-diagnostic passes (`0/37`). This is unresolved representation evidence, not grounds for post-hoc threshold retuning, a whole-group rejection or feature selection.
- Next AI task: `PRM-091_TECHNICAL_QUALIFICATION_POLICY_PREREGISTRATION_NO_Y_NO_FIT`. Freeze how technical stability, variation, named redundancy, pair diagnostics and a potential full58 expansion will be handled. Do not run full58 or x–y modeling automatically.

Current indices: `PRM-090 / RUN-235 / DEC-268 / CHG-255 / LAB-CHG-227 / R09-BB-1044~1051`.

## Current execution handoff — PRM-091 policy frozen; second-wave full58 remains locked

- PRM-091 is a policy-only result: it rerouted the 37 completed PRM-090 outputs without reading performance `y`. The 19 resolution passes are `likely_resolution_stable_not_qualified`; the 18 resolution/rank failures remain explicit holds. Neither group is a selected feature roster.
- All `58/58` PRM-082 V128 source/mask markers are hash-valid for reuse. A future technical census would be exactly `58 models × 19 routed outputs = 1,102` values on existing masks only; this calculation has **not** been authorized or executed.
- The two LIT-X017 beta0 outputs were constant on the 13-model panel, so they remain trace-only until full58 coverage/variation is proven. The 171 direct cohort redundancy rows, named X017↔X004/X023↔X002 comparisons and T8/T9/T5/T6 diagnostics are nonselection evidence only.
- Policy/independent QA passed `12/12·14/14`; 69 frozen direct-input/marker hashes match. PRM-091 has no scientific intermediate artifacts. y/fit/selection/promotion/new masks remain zero.
- Next AI task: `PRM-092_SECOND_WAVE_FULL58_V128_RUNNER_AND_EXECUTE_OR_STOP_REVIEW_NO_EXECUTION`. Prepare a separately hash-bound runner, resource preflight and authorization decision only; do **not** calculate the 1,102 values until a distinct PRM-092 permit exists.

Current indices: `PRM-091 / RUN-236 / DEC-269 / CHG-256 / LAB-CHG-228 / R09-BB-1052~1058`.

## Current execution handoff — PRM-092 full58 V128 runner prepared; PRM-093 permit required

- PRM-092 has prepared, but not executed, the exact future technical census: 58 hash-valid PRM-082 fixed-40 `V128` source/mask pairs × 19 PRM-091 routed outputs = `1,102` values. The 18 held outputs remain outside scope and no candidate is selected or promoted.
- The runner supports a future atomic model-level calculation, quarantine/resume and complete-only merge. Its future outputs are coverage/variation, direct redundancy and T8/T9/T5/T6 diagnostic tables only; it has no performance-y, fitting or feature-selection path.
- Preparatory proof: 66 frozen input hashes match; doctor validates `58/58` source/mask cells; existing PRM-090 V128 output subset maps `13×19=247` rows; preparer/independent QA pass `12/12·15/15`.
- Execution boundary: the only action run is `doctor`. `run-cell` and `merge` were deliberately attempted without a permit and fail closed. No PRM-092 `intermediate/` or authorization artifact exists; values/new masks/y/fit/selection/promotion remain zero.
- Next AI task: `PRM-093_SECOND_WAVE_FULL58_V128_EXECUTE_OR_STOP_PERMIT_REVIEW_NO_EXECUTION`. Rerun KMK312 doctor, verify hashes/resources/independent QA and decide whether to issue an exact-hash permit. Do **not** generate the 1,102 values automatically.

Current indices: `PRM-092 / RUN-237 / DEC-270 / CHG-257 / LAB-CHG-229 / R09-BB-1059~1065`.

## Current execution handoff — PRM-093 exact permit issued; no cell executed

- A fresh KMK312 execute-or-stop review passed `12/12`: live runner/config/contract hashes, 58/58 sources/masks, PRM-092 manifest `20/20`, all upstream QA, zero competing Python processes and RAM/disk `14.48/86.77 GiB`.
- The exact PRM-093 permit is valid in the runner doctor. It authorizes only the ordered 58 V128 reuse cells and 19 routed outputs (`1,102` values), `run-cell`/`merge`, zero new masks and inherited no-y/no-fit/no-selection/no-promotion locks.
- Independent QA is `15/15`; 11/11 altered permits fail closed. Q01's repeated full doctor timed out harmlessly; Q02 tests only already-invalid permits at the first run-cell guard. The valid permit has never been used for `run-cell` or `merge`.
- Actual cells, merges and descriptor values remain `0/0/0`; no intermediate directory exists.
- Next AI task: `PRM-094_SECOND_WAVE_FULL58_V128_EXECUTION_AND_INDEPENDENT_TECHNICAL_REVIEW`. Fresh-preflight the valid permit, execute only its 58 cells, complete-only merge and independently replay all values/gates. Keep performance y and modeling locked.

Current indices: `PRM-093 / RUN-238 / DEC-271 / CHG-258 / LAB-CHG-230 / R09-BB-1066~1072`.

## Current execution handoff — PRM-094 full58 technical census complete and independently reproduced

- The exact PRM-093 permit executed all `58/58` existing fixed-40 V128 cells and complete-only merged `1,102/1,102` values for the 19 routed second-wave outputs. There were no failures, quarantines, retries or new masks.
- Independent code reproduced markers/formulas/coverage/redundancy/pairs `58/58·1,102/1,102·114/114·171/171·38/38`; QA is `15/15` and maximum absolute formula error is `4.44e-16`.
- All 19 outputs are finite across all 58 models. Seventeen vary and are `likely_full58_technical_candidate_not_selected`. `beta0_count` and `beta0_density` are low-variation trace holds and a confirmed proportional duplicate.
- B/C/L/F/T all have complete numeric coverage, but F has only two models. T8/T9 and T5/T6 each have 14/19 non-zero deltas; those are diagnostics, not a pair-rescue or feature-selection result.
- y access, fitting, selection, promotion and new slicing remain `0/0/0/0/0`.
- Next AI task: `PRM-095_FULL58_SECOND_WAVE_TECHNICAL_ROUTING_AND_CROSSBANK_REDUNDANCY_POLICY_NO_Y`. Compare the 17 variable outputs to the existing full58 x bank and preregister later nested entry rules. Do not open y.

Current indices: `PRM-094 / RUN-239 / DEC-272 / CHG-259 / LAB-CHG-231 / R09-BB-1073~1081`.

## Current execution handoff — PRM-095 cross-bank technical routing complete, y still locked

- All 17 variable PRM-094 outputs were compared with all 89 existing PRM-082 x outputs on the identical 58-model fixed-40 V128 population: `1,513/1,513` pair relations.
- No exact or proportional duplicate exists. Ten high-redundancy edges involve six LIT-X009 C2 outputs and LIT-X002 S2 outputs. Five C2 candidates challenge existing-primary blocks; one challenges a resolution-held block.
- All five LIT-X012 lacunarity and all six LIT-X023 structure-factor outputs are standalone later challengers under the frozen ≥0.98 Pearson-and-Spearman relation rule. Total later blocks: 15. No block representative is selected.
- Thirty-four pairs are explicit 57-common comparisons because two existing C2 e-fold outputs are undefined at L10. Seventeen pairs use nonvarying X005 trace and are isolated as degenerate references. No imputation or zero-slope duplicate claim is allowed.
- Producer/independent/negative QA is `15/15·20/20·6/6`; relation labels reproduce `1,513/1,513`. y/fit/selection/promotion/new masks/slicing remain zero.
- Next AI task: `PRM-096_LATER_NESTED_EVALUATION_CONTRACT_OR_PARALLEL_DESCRIPTOR_WORK_DECISION`. Default to no-y descriptor-bank consolidation/third-wave planning because new performance data are pending; do not open y automatically.

Current indices: `PRM-095 / RUN-240 / DEC-273 / CHG-260 / LAB-CHG-232 / R09-BB-1082~1091`.

## Current execution handoff — PRM-096 XREG-v0.2 technical bank consolidated; no-y third-wave route selected

- PRM-082의 89개 출력과 PRM-094의 19개 출력을 해시 고정된 source lineage로 합쳐 `XREG-v0.2-TECHNICAL`을 만들었다: `108 outputs × 58 models = 6,264 values`.
- 12개 first-wave 내부 관계, 10개 C2↔S2 cross-bank 관계, beta0 count↔density 1개를 합쳐 23 edge와 89 unified blocks를 재구성했다. 15개 multi-member block과 74개 singleton이 있으며 대표는 하나도 선택하지 않았다.
- 문헌 후보군 33개를 전수 라우팅했다: completed 10, third-wave preregister 5, negative control 1, conditional 11, hold 4, rejected-current-scope 2.
- 다음 bounded wave는 `LIT-X006`, `X008`, `X019`, `X024`, `X031`과 negative-control `X028`이다. PRM-096은 수식 실행·full58 계산을 허가하지 않는다.
- PRM-095의 later-y gate 8개를 그대로 보존했다. producer/independent/negative QA는 `15/15·18/18·6/6`; y/fit/selection/promotion은 `0/0/0/0`이다.
- Next AI task: `PRM-097_THIRD_WAVE_FORMULA_AND_SYNTHETIC_TRUTH_PREREGISTRATION_NO_EXECUTION`. 정확한 수식·population·단위·경계/해상도 정책·synthetic fixtures·대표 panel·비용 중단 기준만 동결하고 실제 full58/y 작업은 하지 말 것.

Current indices: `PRM-096 / RUN-241 / DEC-274 / CHG-261 / LAB-CHG-233 / R09-BB-1092~1102`.

## Current execution handoff — PRM-097 third-wave formula/test contracts frozen; no execution

- Frozen scope: `LIT-X006/X008/X019/X024/X031` plus `X028` negative control.
- Registry: `6 groups / 72 outputs / 17 formula contracts / 22 synthetic fixtures / 36 representative-panel cells / 24 resolution rows`.
- Scientific boundary: candidate calculation/full58/y/fit/selection/promotion are `0/0/0/0/0/0`; every panel and resolution authorization remains false.
- Independent review: producer `15/15`, independent `20/20`, negative fixtures `10/10`. Q01 was a verifier prose-token mismatch only and changed no scientific contract.
- Next AI task: `PRM-098_BOUNDED_THIRD_WAVE_SYNTHETIC_TRUTH_COST_CANARY_AND_REPRESENTATIVE_PANEL`. Execute synthetic truth first, then one serial V64 cost canary per surviving group, then only permitted representative-panel cells. Return before full58.

Current indices: `PRM-097 / RUN-242 / DEC-275 / CHG-262 / LAB-CHG-234 / R09-BB-1103~1113`.

## Current execution handoff — PRM-098 bounded third-wave review complete; six technical outputs return for permit decision

- Synthetic truth/cost/independent QA: `22/22 fixtures`, `6/6 V64 canaries`, `22/22 checks`, `60/60 lineage`, `10,062/10,062 ECT curve points`.
- Representative panel: `139/144` cells passed. `LIT-X006/C1/V192` timed out and four later X006/V192 cells were not run under the frozen group stop.
- Frozen resolution gate: 37 technical outputs were judged; only four X019 q50 phase-scale ratios and two X024 normalized direction-mean ECT summaries passed (`6/37`).
- Holds: X006 resource cost; X008 and X031 resolution instability; X028 remains a completed negative control. T8/T9 is not rescued.
- C1 V192 is a valid same-STL input with deterministic voxel-grid resonance; it remains in the gate and no threshold was changed.
- Scientific locks: performance y / fit / selection / promotion / full58 expansion are `0/0/0/0/0`.
- Next AI task: `PRM-099_THIRD_WAVE_TECHNICAL_RETURN_AND_FULL58_PERMIT_DECISION_NO_Y`. Decide whether only the six likely outputs merit a hash-bound full58 permit; do not execute, read y, select or promote.

Current indices: `PRM-098 / RUN-243 / DEC-276 / CHG-263 / LAB-CHG-235 / R09-BB-1114~1126`.

## Current execution handoff — PRM-099 exact-hash full58 permit issued; execution remains zero

- Exact future scope: PRM-098's six likely/unselected outputs × 58 V128 models = `348` values.
- X019 route: four q50 phase-scale ratios derive from existing full58 X001/X016 parents; representative parity `24/24`, so no new mask calculation.
- X024 route: two normalized direction-mean ECT summaries from 58 existing V128 masks; projected serial safety wall time `5.58 min`, peak panel RSS `0.162 GiB`.
- Small-panel x-only overlap: `648/648` relations independently replayed; 10 high-redundancy warnings, especially X024 versus X004 Euler outputs. This is diagnostic, not selection.
- Permit review/mutation/independent QA: `12/12 · 10/10 · 20/20`; 58/58 mask hashes. Valid permit doctor passes.
- Execution boundary: full58 cells/merge/values and y/fit/selection/promotion are `0/0/0 · 0/0/0/0`.
- Next AI task: `PRM-100_THIRD_WAVE_FULL58_V128_SIX_OUTPUT_EXECUTION_AND_XONLY_REVIEW`. Execute only the exact permit, merge 348 values complete-only, run no-y redundancy/pair review, then return.

Current indices: `PRM-099 / RUN-244 / DEC-277 / CHG-264 / LAB-CHG-236 / R09-BB-1127~1133`.

## Current execution handoff — PRM-100 third-wave full58 x-only census complete

- Exact permit execution: all `58/58` serial cells passed once; complete-only merge contains exactly `58×6=348` finite no-y values.
- Parent/formula replay: X019 q50 phase-scale ratios replay `232/232`; X024 final Euler endpoints replay `58/58`; independent QA is `14/14`.
- Full58 utility-neutral facts: all six have finite 58-model coverage. Four X019 ratios have zero exact/proportional/high-redundancy relation to XREG-v0.2. X024 total variation likewise has none. X024 absolute-AUC has two high-redundancy diagnostic edges only, both with the existing X004 Euler-characteristic scalar player.
- Difficult pairs: T8/T9 and T5/T6 remain identical for the four X019 ratios; X024 deltas are negligible relative to full58 variation. This wave does not rescue either pair.
- Boundary: y / fit / feature selection / promotion / prediction / inverse-design remain `0/0/0/0/0/0`. All six are `likely_resolution_qualified_not_selected`.
- Next AI task: `PRM-101_XREG_V0_3_THIRD_WAVE_FULL58_CONSOLIDATION_AND_BLOCK_POLICY_NO_Y`. Consolidate only the no-y registry/block policy and decide the next descriptor route; do not start y work.

Current indices: `PRM-100 / RUN-245 / DEC-278 / CHG-265 / LAB-CHG-237 / R09-BB-1134~1142`.

## Current handoff — PRM-101 XREG-v0.3 no-y consolidation complete

- `XREG-v0.3-TECHNICAL` contains `114` candidates and `6,612` values across the existing 58 models; all six PRM-100 outputs retain direct/derived lineage and remain unselected.
- Four X019 ratios and X024 total variation are retained as likely technical candidates. X024 absolute-AUC is preserved only inside the expanded `U096-BLK-044` redundancy block with the two X004 solid-Euler scalars.
- QA: producer `10/10`, independent `20/20`. The v0.2 snapshot remains immutable; its two inherited missing values remain two, and the six appended candidates add no missingness.
- Boundary: y / fit / selection / promotion / prediction / inverse-design remain `0/0/0/0/0/0`.
- Next AI task: `PRM-102_DESCRIPTOR_FOURTH_WAVE_ROUTE_AND_PREREGISTRATION_NO_Y`.

Current indices: `PRM-101 / RUN-246 / DEC-279 / CHG-266 / LAB-CHG-238 / R09-BB-1143~1147`.

## Current handoff — PRM-102 B/C raw-table batch proves the fast candidate lane

- Official grades: A = new raw/resolution-risk algorithm with strict representative gate; B = 10–30 new statistics from verified raw tables with automated full58 QA; C = derived value/profile summaries with lineage/x-only QA. Selection remains prohibited in every grade.
- PRM-102 reused 116 hash-frozen SLICE-004 tables, generated `29×58=1,682` finite values (B23/C6), and passed producer/independent `8/8·12/12`.
- x-only: 0 exact/proportional/high edges to XREG-v0.3. Two internal component-count redundancy pairs are recorded as blocks. T8/T9 and T5/T6 are separated by 23/29 and 21/29 values respectively.
- Boundary: y / fit / selection / promotion / prediction / inverse-design remain `0/0/0/0/0/0`.
- Next AI task: `PRM-103_BC_BATCH_CONSOLIDATION_AND_BLOCK_POLICY_NO_Y`.

Current indices: `PRM-102 / RUN-247 / DEC-280 / CHG-267 / LAB-CHG-239 / R09-BB-1148~1153`.

## Current handoff — PRM-103 XREG-v0.4 B/C cohort consolidation complete

- XREG-v0.4: 143 candidates, 8,294 rows, 8,292 finite values and two inherited missing values; producer/independent QA `8/8·17/17`.
- PRM-102's 29 B/C candidates all remain unselected. Two internal component-count pairs are recorded as `U103-BLK-095/096`; the other 25 are singleton blocks.
- Boundary: y / fit / selection / promotion / prediction / inverse-design remain `0/0/0/0/0/0`.
- Next AI task: `PRM-104_BC_SECOND_RAW_TABLE_COHORT_NO_Y` — choose 10–30 additional existing-table statistics, not a new raw algorithm.

Current indices: `PRM-103 / RUN-248 / DEC-281 / CHG-268 / LAB-CHG-240 / R09-BB-1154~1158`.

## Current handoff — PRM-104 overlay phase-profile B/C batch complete

- PRM-104 reused exactly 58 hash-frozen `SLICE-004` `overlay_pixel_readback.csv` tables (800 overlay pairs per model), with no new image/mask/mesh/slice creation.
- The batch adds `RAW-X036` (25 Grade B count-profile statistics) and `RAW-X037` (3 Grade C phase-composition means): `28×58=1,624` finite values. Producer/independent QA `8/8·8/8` PASS.
- x-only result: no exact/proportional crossbank duplicate; six crossbank high-redundancy warnings and ten internal warnings must be preserved as later block constraints. T8/T9 and T5/T6 differ on all 28 candidates, which is descriptor-space evidence only.
- Boundary: y / fit / selection / promotion / prediction / inverse-design remain `0/0/0/0/0/0`.
- Next AI task: `PRM-105_XREG_V0_5_OVERLAY_PHASE_BATCH_CONSOLIDATION_AND_BLOCK_POLICY_NO_Y`.

Current indices: `PRM-104 / RUN-249 / DEC-282 / CHG-269 / LAB-CHG-241 / R09-BB-1159~1164`.

## Current handoff — PRM-105 XREG-v0.5 overlay-phase consolidation complete

- `XREG-v0.5-TECHNICAL` now has `171` candidates, `9,918` value rows, `9,916` finite values, two inherited missing cells, `135` blocks and `43` edges. PRM-104's 28 candidates are all retained and unselected.
- The 16 PRM-104 high-redundancy edges become six crossbank and ten internal block constraints. New phase fractions are explicitly a three-member compositional block; no winner or active roster exists.
- QA: producer/independent `8/8·8/8`. One independent verifier was revised only to allow `1e-12` CSV serialization precision after finding last-bit round-trip deltas; no source value, formula, scope or scientific threshold changed.
- Boundary: y / fit / selection / promotion / prediction / inverse-design remain `0/0/0/0/0/0`.
- Next AI task: `PRM-106_BC_THIRD_RAW_TABLE_COHORT_NO_Y`.

Current indices: `PRM-105 / RUN-250 / DEC-283 / CHG-270 / LAB-CHG-242 / R09-BB-1165~1168`.

## Current handoff — PRM-106 profile-dynamics B/C cohort complete

- PRM-106 reused 116 frozen SLICE-004 raw tables and created 22 traceable candidates (`RAW-X038/039/040`) × 58 = `1,276` finite values. Producer/independent QA `8/8·8/8` PASS.
- x-only result: two crossbank proportional duplicates (union-pixel versus total-overlay-area dynamics), two internal exact duplicates (peak-to-mean versus range-over-mean with zero profile minima), and one internal high-redundancy edge. These are block evidence, not deletion/selection evidence.
- T8/T9 differs on 22/22; T5/T6 on 18/22. No performance meaning is inferred.
- Boundary: y / fit / selection / promotion / prediction / inverse-design remain `0/0/0/0/0/0`.
- Next AI task: `PRM-107_XREG_V0_6_PROFILE_DYNAMICS_CONSOLIDATION_AND_BLOCK_POLICY_NO_Y`.

Current indices: `PRM-106 / RUN-251 / DEC-284 / CHG-271 / LAB-CHG-243 / R09-BB-1169~1174`.

## Current handoff — PRM-107 XREG-v0.6 consolidation complete

- XREG-v0.6 contains `193` candidates, `11,194` value rows, `11,192` finite values, two inherited missing cells, `152` blocks and `48` edges. PRM-106's 22 candidates remain completely preserved and unselected.
- The five PRM-106 relations are encoded as two crossbank proportional, two internal exact and one internal high-redundancy edge. Cohort policy: 2 crossbank-block members, 4 exact-block members, 2 high-block members and 14 singleton candidates.
- Producer/independent QA `8/8·8/8`; predecessor and cohort values replay within the fixed 1e-12 CSV serialization bound.
- Boundary: y / fit / selection / promotion / prediction / inverse-design remain `0/0/0/0/0/0`.
- Next AI task: `PRM-108_BC_FOURTH_CANDIDATE_COHORT_NO_Y`.

Current indices: `PRM-107 / RUN-252 / DEC-285 / CHG-272 / LAB-CHG-244 / R09-BB-1175~1178`.

## Current handoff — PRM-108 axial-distribution/reflection-symmetry B/C cohort complete

- PRM-108 reused 116 hash-frozen SLICE-004 slice/overlay tables and created 24 dimensionless candidates (`RAW-X041~044`) × 58 models = `1,392` finite values. No image, mask, mesh or slice was regenerated.
- Producer/independent QA is `8/8·8/8`. The first attempt stopped before output because one preregistered hash had a duplicated character; only that contract transcription was corrected and the complete run was repeated.
- X-only result: no exact/proportional/high relation to the 193-candidate XREG-v0.6 bank. One internal red/blue overlay reflection-asymmetry pair is highly redundant and must become a non-selecting block edge.
- T8/T9 differs on 24/24 candidates; T5/T6 on 23/24. This is descriptor-space evidence only.
- Boundary: y / fit / selection / promotion / prediction / inverse-design remain `0/0/0/0/0/0`.
- Next AI task: `PRM-109_XREG_V0_7_AXIAL_DISTRIBUTION_SYMMETRY_CONSOLIDATION_NO_Y`.

Current indices: `PRM-108 / RUN-253 / DEC-286 / CHG-273 / LAB-CHG-245 / R09-BB-1179~1184`.

## Current handoff — PRM-109 XREG-v0.7 consolidation complete

- XREG-v0.7 contains `217` candidates, `12,586` value rows, `12,584` finite values, two inherited L10 missing cells, `175` blocks and `49` edges.
- All 193 XREG-v0.6 candidates and 11,194 predecessor rows replay within `1e-12`; all 24 PRM-108 candidates and 1,392 values replay within the same bound.
- All 152 predecessor block IDs are unchanged. The cohort creates 22 singleton candidates and one two-member red/blue reflection-asymmetry block (`U109-BLK-019` / `U109-EDGE-049`).
- Producer/independent QA `8/8·8/8`; active/promoted/y-evidence/representative counts remain `0/0/0/0`.
- Next AI task: `PRM-110_BC_FIFTH_CANDIDATE_COHORT_NO_Y`.

Current indices: `PRM-109 / RUN-254 / DEC-287 / CHG-274 / LAB-CHG-246 / R09-BB-1185~1189`.

## Current handoff — PRM-110 axial-position shape/entropy B/C cohort complete

- PRM-110 reused 116 frozen slice/overlay tables and created 24 candidates (`RAW-X045/046`) × 58 models = `1,392` finite values. Metrics are weighted axial-position skewness/kurtosis, normalized profile entropy and center–edge mass contrast.
- Producer/independent QA is `8/8·8/8`; six B3 formulas replay independently. No image, mask, mesh or slice was created.
- X-only result: three crossbank high relations, all entropy versus `LIT-X023::axis_power_fraction_z`; seven internal high relations across matched kurtosis/entropy profiles. Exact/proportional duplicates are zero.
- T8/T9 differs on 24/24; T5/T6 on 22/24. This is descriptor-space evidence only.
- Boundary: y / fit / selection / promotion / prediction / inverse-design remain `0/0/0/0/0/0`.
- Next AI task: `PRM-111_XREG_V0_8_AXIAL_SHAPE_ENTROPY_CONSOLIDATION_NO_Y`.

Current indices: `PRM-110 / RUN-255 / DEC-288 / CHG-275 / LAB-CHG-247 / R09-BB-1190~1195`.

## Current handoff — PRM-111 XREG-v0.8 consolidation complete

- XREG-v0.8 contains `241` candidates, `13,978` value rows, `13,976` finite values, two inherited L10 missing cells, `193` blocks and `59` edges.
- All predecessor and PRM-110 cohort values replay within `1e-12`; producer/independent QA is `8/8·8/8`.
- The 24-candidate cohort becomes 16 singletons, three crossbank-high and five internal-high blocks. No representative is selected.
- One predecessor (`LIT-X023::axis_power_fraction_z`) joins the entropy graph component, so its successor block ID changes; all other predecessor block identities remain unchanged.
- Boundary: y / fit / selection / promotion / prediction / inverse-design remain `0/0/0/0/0/0`.
- Next AI task: `PRM-112_BC_SIXTH_CANDIDATE_COHORT_NO_Y`.

Current indices: `PRM-111 / RUN-256 / DEC-289 / CHG-276 / LAB-CHG-248 / R09-BB-1196~1200`.

## Current handoff — PRM-112 axial weighted-quantile location B cohort complete

- PRM-112 reused 116 frozen slice/overlay tables and created 24 direct q10/q25/q75/q90 axial-location candidates (`RAW-X047`) × 58 models = `1,392` finite values. No image, mask, mesh or slice was created.
- Producer/independent QA is `8/8·8/8`; six independent B3 cumulative-quantile probes pass.
- X-only result: exact/proportional/high relation to XREG-v0.8 is `0/0/0`; one internal q75 purple-overlay/material-area relation is high and must become a non-selecting block edge.
- T8/T9 differs on 13/24; T5/T6 on 15/24. This is descriptor-space evidence only.
- Boundary: y / fit / selection / promotion / prediction / inverse-design remain `0/0/0/0/0/0`.
- Next AI task: `PRM-113_XREG_V0_9_WEIGHTED_QUANTILE_LOCATION_CONSOLIDATION_NO_Y`.

Current indices: `PRM-112 / RUN-257 / DEC-290 / CHG-277 / LAB-CHG-249 / R09-BB-1201~1206`.

## Current handoff — PRM-113 XREG-v0.9 consolidation complete

- XREG-v0.9 contains `265` candidates, `15,370` value rows, `15,368` finite values, two inherited L10 missing cells, `216` blocks and `60` edges.
- All predecessor and PRM-112 cohort values replay within `1e-12`; producer/independent QA is `8/8·8/8`.
- The 24-candidate cohort becomes 22 singletons and one two-member internal-high block. No representative is selected.
- All 241 predecessor block IDs remain unchanged.
- Boundary: y / fit / selection / promotion / prediction / inverse-design remain `0/0/0/0/0/0`.
- Next AI task: bounded `PRM-114_BC_SEVENTH_CANDIDATE_COHORT_NO_Y`.

Current indices: `PRM-113 / RUN-258 / DEC-291 / CHG-278 / LAB-CHG-250 / R09-BB-1207~1211`.

## Current handoff — PRM-114 overlay component inequality/concentration B/C cohort complete

- PRM-114 reused 58 frozen overlay component-population tables and created 12 `RAW-X048` candidates × 58 models = `696` finite values. No image, mask, mesh or slice was created.
- Producer/independent QA is `8/8·8/8`; six independent B3 formula probes pass.
- X-only result: exact/proportional/high relation to XREG-v0.9 is `0/0/0`; cohort internal relation is also `0/0/0`.
- T8/T9 and T5/T6 differ on all 12 candidates. This is descriptor-space evidence only.
- Boundary: y / fit / selection / promotion / prediction / inverse-design remain `0/0/0/0/0/0`.
- Next AI task: `PRM-115_XREG_V1_0_COMPONENT_INEQUALITY_CONSOLIDATION_NO_Y`.

Current indices: `PRM-114 / RUN-259 / DEC-292 / CHG-279 / LAB-CHG-251 / R09-BB-1212~1217`.

## Current handoff — PRM-115 XREG-v1.0 consolidation complete

- XREG-v1.0 contains `277` candidates, `16,066` value rows, `16,064` finite values, two inherited L10 missing cells, `228` blocks and unchanged `60` edges.
- All predecessor and PRM-114 cohort values replay within `1e-12`; producer/independent QA is `8/8·8/8`.
- The 12-candidate cohort becomes twelve singleton blocks; no representative is selected and all predecessor block IDs remain unchanged.
- Boundary: y / fit / selection / promotion / prediction / inverse-design remain `0/0/0/0/0/0`.
- Next AI task: bounded `PRM-116_BC_EIGHTH_CANDIDATE_COHORT_NO_Y`.

Current indices: `PRM-115 / RUN-260 / DEC-293 / CHG-280 / LAB-CHG-252 / R09-BB-1218~1222`.

## Current handoff — PRM-116 component-filter-sensitivity B/C cohort complete

- PRM-116 reused 58 frozen overlay pixel-read tables and created 11 RAW-X049 candidates × 58 models = 638 finite values; no image, mask, mesh or slice was created.
- Producer/independent QA is `8/8·8/8`; five high crossbank raw-count links and zero internal high links are recorded for block policy.
- Boundary: y / fit / selection / promotion / prediction / inverse-design remain `0/0/0/0/0/0`.
- Next AI task: `PRM-117_XREG_V1_1_COMPONENT_FILTER_SENSITIVITY_CONSOLIDATION_NO_Y`.

Current indices: `PRM-116 / RUN-261 / DEC-294 / CHG-281 / LAB-CHG-253 / R09-BB-1223~1228`.

## Current handoff — PRM-117 XREG-v1.1 consolidation complete

- XREG-v1.1 contains `288` candidates, `16,704` rows, `16,702` finite values, `235` blocks and `65` edges.
- Producer/independent QA `8/8·8/8`; all values replay within `1e-12`.
- Five high crossbank edges are retained; five predecessor members change block label by graph closure only. No candidate is selected.
- Next AI task: bounded `PRM-118_BC_NINTH_CANDIDATE_COHORT_NO_Y`.

Current indices: `PRM-117 / RUN-262 / DEC-295 / CHG-282 / LAB-CHG-254`.

## Current handoff — PRM-118 slice component-filter-sensitivity B/C cohort complete

- PRM-118 reused 58 frozen 801-slice pixel-read tables and created 11 `RAW-X050` candidates × 58 models = `638` finite values; no image, mask, mesh or slice was created.
- Producer/independent QA is `8/8·8/8`; two exact and nine high crossbank raw-count relations are explicitly retained, while cohort-internal exact/proportional/high is `0/0/0`.
- The min2-removal delta/fraction statistics are lineage-traceable candidates only. T8/T9 and T5/T6 differ on 6/11 values, without performance interpretation.
- Boundary: y / fit / selection / promotion / prediction / inverse-design remain `0/0/0/0/0/0`.
- Next AI task: `PRM-119_XREG_V1_2_SLICE_COMPONENT_FILTER_SENSITIVITY_CONSOLIDATION_NO_Y`.

Current indices: `PRM-118 / RUN-263 / DEC-296 / CHG-283 / LAB-CHG-255 / R09-BB-1229~1234`.

## Current handoff — PRM-119 XREG-v1.2 consolidation complete

- XREG-v1.2 contains `299` candidates, `17,342` rows, `17,340` finite values, `240` blocks and `76` edges; only the two inherited L10 cells remain missing.
- Producer/independent QA is `8/8·8/8`; all XREG-v1.1 predecessor and PRM-118 cohort values replay within `1e-12`.
- Two exact and nine high crossbank relations are retained. Eleven predecessor block labels change by graph closure only; no candidate is selected or promoted.
- Boundary: y / fit / selection / promotion / prediction / inverse-design remain `0/0/0/0/0/0`.
- Next AI task: bounded `PRM-120_BC_TENTH_CANDIDATE_COHORT_NO_Y`.

Current indices: `PRM-119 / RUN-264 / DEC-297 / CHG-284 / LAB-CHG-256 / R09-BB-1235~1239`.

## Current handoff — PRM-120 overlay-pair component-composition B/C cohort complete

- PRM-120 reused 58 frozen 800-pair component-population tables and created 24 `RAW-X051` candidates × 58 models = `1,392` finite values; no image, mask, mesh or slice was created.
- Producer/independent QA is `8/8·8/8`; three high crossbank and two high cohort-internal relations are explicitly retained for graph policy.
- T8/T9 and T5/T6 differ numerically on 24/24 candidates, without performance interpretation. No candidate is selected or promoted.
- Boundary: y / fit / selection / promotion / prediction / inverse-design remain `0/0/0/0/0/0`.
- Next AI task: `PRM-121_XREG_V1_3_OVERLAY_PAIR_COMPONENT_COMPOSITION_CONSOLIDATION_NO_Y`.

Current indices: `PRM-120 / RUN-265 / DEC-298 / CHG-285 / LAB-CHG-257 / R09-BB-1240~1245`.

## Current handoff — PRM-121 XREG-v1.3 consolidation complete

- XREG-v1.3 contains `323` candidates, `18,734` rows, `18,732` finite values, `259` blocks and `81` edges; only the two inherited L10 cells remain missing.
- Producer/independent QA is `8/8·8/8`; all XREG-v1.2 predecessor and PRM-120 cohort values replay within `1e-12`.
- Three crossbank and two internal high relations are retained. Five predecessor block labels change by graph closure only; no candidate is selected or promoted.
- Boundary: y / fit / selection / promotion / prediction / inverse-design remain `0/0/0/0/0/0`.
- Next AI task: bounded `PRM-122_BC_ELEVENTH_CANDIDATE_COHORT_NO_Y`.

Current indices: `PRM-121 / RUN-266 / DEC-299 / CHG-286 / LAB-CHG-258 / R09-BB-1246~1250`.

## Current handoff — PRM-122 profile jump-and-turn B/C cohort complete

- PRM-122 reused 58 frozen ordered slice/overlay profiles and created 24 `RAW-X052` candidates × 58 models = `1,392` finite values; producer/independent QA is `8/8·8/8`.
- Crossbank/internal high relations are `2/3`; all candidates remain unselected and y/fit/selection/promotion remain zero.
- Next AI task: `PRM-123_XREG_V1_4_PROFILE_JUMP_AND_TURN_CONSOLIDATION_NO_Y`.

Current indices: `PRM-122 / RUN-267 / DEC-300 / CHG-287 / LAB-CHG-259`.

## Current handoff — PRM-123 XREG-v1.4 consolidation complete

- XREG-v1.4 contains `347` candidates, `20,126` values, `20,124` finite values, `278` blocks and `86` edges.
- Producer scope QA and independent QA are `PASS·8/8`; predecessor/cohort values replay within `1e-12` and y/fit/selection/promotion remain zero.
- Next AI task: bounded `PRM-124_BC_TWELFTH_CANDIDATE_COHORT_NO_Y`.

## Current handoff — PRM-124 overlay phase-balance B/C cohort complete

- `RAW-X053` adds 18 unselected candidates from frozen 800-pair overlay colour-count readbacks: 12 Grade-B red/blue balance summaries and 6 Grade-C normalized three-phase entropy summaries.
- Full58 output is `1,044/1,044` finite values; producer and independent QA pass `1/1·8/8`, including direct source-table replay within `2.22e-16`.
- Crossbank exact/proportional/high is `0/0/0`; internal high is `2`. All are x-only evidence. T8/T9 and T5/T6 differ numerically on every candidate, without any y claim.
- Next AI task: `PRM-125_XREG_V1_5_OVERLAY_PHASE_BALANCE_CONSOLIDATION_NO_Y`.

## Current handoff — PRM-125 XREG-v1.5 consolidation complete

- XREG-v1.5 contains `365` technical candidates, `21,170` values (`21,168` finite), `294` non-selecting blocks and `88` x-only edges.
- All 347 XREG-v1.4 predecessor values and blocks are unchanged; all 18 RAW-X053 values replay. Independent QA is `8/8 PASS`.
- Next AI task: bounded `PRM-126_BC_THIRTEENTH_CANDIDATE_COHORT_NO_Y` from verified existing raw tables/XREG-v1.5 quantities only.

## Current handoff — PRM-126 overlay component-density B/C cohort complete

- `RAW-X054` adds 24 unselected component-density/retention summaries from frozen overlay readbacks: `1,392/1,392` finite values.
- Producer/independent QA pass `1/1·8/8`; direct replay max error is `2.27e-13`. Crossbank high is `0`, internal high is `7`.
- Next AI task: `PRM-127_XREG_V1_6_OVERLAY_COMPONENT_DENSITY_CONSOLIDATION_NO_Y`.

## Current handoff — PRM-127 XREG-v1.6 consolidation complete

- XREG-v1.6: `389` candidates, `22,562` values (`22,560` finite), `311` non-selecting blocks and `95` x-only edges.
- Producer/independent QA passes `1/1·8/8`; predecessor/cohort replay passes and y/selection remain locked.
- Next: `PRM-128_BC_FOURTEENTH_CANDIDATE_COHORT_NO_Y`.

## Current handoff — PRM-128 overlay phase cross-correlation cohort complete

- RAW-X055 adds `12×58=696` finite unselected zero/one-lag colour-phase correlation values from frozen overlay readbacks.
- Producer PASS; independent direct replay `5/5`, max error `1.11e-16`; y/selection locks remain active.
- Next: PRM-129 immutable XREG-v1.7 consolidation.

## Current handoff — PRM-129 XREG-v1.7 consolidation complete

- XREG-v1.7: `401` candidates, `23,258` values (`23,256` finite), `322` blocks and `96` x-only edges; independent QA `8/8` PASS.
- Next: bounded `PRM-130_BC_FIFTEENTH_CANDIDATE_COHORT_NO_Y` from verified raw tables or XREG-v1.7-derived quantities.

## Current handoff — PRM-130 overlay-fraction quantile cohort complete

- RAW-X056 adds `15×58=870` finite unselected fraction-distribution values; producer PASS and independent direct replay `3/3` pass.
- Next: PRM-131 immutable XREG-v1.8 consolidation; y/selection locks remain active.

## Current handoff — PRM-131~137 batch-autopilot complete

- Official FAST technical snapshot is XREG-v2.1: `452` candidates / `26,216` values (`26,214` finite) / `345` blocks / `143` x-only edges.
- PRM131 consolidation plus PRM132→133, PRM134→135 and PRM136→137 completed; all three independent predecessor/cohort replay checks pass.
- No strict-parity conclusion and no y/modeling work occurred. Next decision: bounded FAST expansion versus STRICT evidence focus.

## Current handoff — PRM-138~143 batch-autopilot complete

- Official FAST technical snapshot is XREG-v2.4: `494` candidates / `28,652` values (`28,650` finite) / `375` blocks / `157` x-only edges.
- Three B/C cycles added 42 unselected candidates; independent predecessor/cohort replay is `3/3 PASS`.
- STRICT parity remains unresolved; no y/modeling work occurred.

## Current handoff — FAST-CAP-001 x-only capacity audit complete

- XREG-v2.7 audit passes: `542` candidates, `540` full58-finite, `411` blocks, `175` x-only edges.
- T8/T9 are nonzero on `440` candidates and exact-zero on `102`; no performance inference is permitted.
- Next: only a genuinely distinct FAST raw-table family, otherwise pivot effort to STRICT parity evidence.

## Current handoff — PRM-144~149 batch-autopilot complete

- Official FAST technical snapshot is XREG-v2.7: `542` candidates / `31,436` values (`31,434` finite) / `411` blocks / `175` x-only edges.
- Three B/C cycles added 48 unselected candidates; independent predecessor/cohort replay is `3/3 PASS`.
- STRICT parity remains unresolved; no y/modeling work occurred.

## Current handoff — STRICT-REC-001 parity re-entry evidence inventory complete

- `STRICT-REC-001` did not execute new descriptor calculations. It inventories the existing CINT-02 legacy-adapter evidence, CINT-03 RUN-139 frozen replay, the N40 source set, and the protected historical comparison workbook without reading any workbook cells.
- A bounded `STRICT-PARITY-P1` can now be prepared: B3 golden PNG fixture → named `LEGACY-PY-RESULT`/`LEGACY-PY-ANGLE-ALL` outputs → mapped `NB-CURRENT` entrypoint. The required next artifact is a notebook cell/function-to-output mapping, not another all58 FAST batch.
- Historical Excel parity is still separate and blocked for point distribution, surface-DDG mesh policy, and unresolved MassOri/Curvature stdev populations. No y/fit/selection/prediction/inverse-design action occurred.

## Current handoff — STRICT-PARITY-P1 NB-CURRENT entrypoint audit complete

- `NB-CURRENT` v0.2 is byte-identical to its protected hash. Effective config precedence is `STL → 96³ voxel mask → 200 px / 100 slices / z·x·y / min-component 2`; Cell 1 user config overrides Cell 9's 160 px default, and Cell 16 resets only slice count. The frozen LEGACY-PY fixture is `40 mm → 1000 px / 801 z PNG pairs`.
- Direct full-notebook parity is therefore **blocked by an input-contract mismatch**, not failed. Changing slice count alone would not fix the source/raster/population mismatch.
- Next AI task: `STRICT-PARITY-P1A_GOLDEN_PNG_TO_NB_FUNCTION_COMPATIBILITY_ADAPTER`, a disposable read-only adapter that evaluates NB-CURRENT Cell-12 formula functions on the same B3 PNG-derived masks. No y/modeling action is allowed.

## Current handoff — STRICT-PARITY-P1A B3 formula compatibility complete

- The same frozen B3 `1000 px × 801 z` colour-combine PNG pairs were supplied to extracted `NB-CURRENT` Cell-12 functions and to `LEGACY-PY-ANGLE-ALL`; no notebook orchestration was run or modified.
- MassOri, Thickness, Angle and Curvature each matched across `35,520` component values, all `800` pair arrays and final weighted mean/std summaries.
- P/A has an explicit unit difference: LEGACY-PY uses `px⁻¹`, NB-CURRENT returns `mm⁻¹`. With the declared factor `25` and the area-weight transform `0.0016`, all `800` values and final summaries agree; transformed weight roundoff is at most `1.82e-12`.
- This is **formula-level shared-input parity only**. Native NB-CURRENT orchestration, LEGACY-PY-RESULT comparison, and historical Excel parity remain separate unresolved scopes.
- Next AI task: optional `STRICT-PARITY-P1B_LOCKED_7MODEL_FORMULA_PANEL` under the same no-y / protected-source locks.

## Current handoff — STRICT-PARITY-P1B-v2 seven-model formula panel complete

- B3/C1/L1/F1/F2/T8/T9 each contributed `800` frozen hash-checked PNG pairs. Under the matched LEGACY-PY component population (`min_pixels=1`), all `7/7` model panels and `35/35` metric summaries pass.
- T8/T9 initially exposed a configuration difference, not a formula failure: NB-CURRENT's default `min_pixels=2` removes singleton components while LEGACY-PY-ANGLE-ALL has no such filter. The preliminary P1B run is retained as superseded evidence; v2 uses the explicit Cell-12 parameter `1` for a like-for-like formula comparison.
- Keep NB-CURRENT native `min_pixels=2` and its STL→voxel route as a separate, unresolved native-configuration lineage. This result does not establish LEGACY-PY-RESULT or historical Excel parity.
- Next AI task: prepare a distinct native-route contract; do not patch NB-CURRENT on the basis of formula-only evidence.

## Current handoff — STRICT-PARITY-P2 native route contract preregistered

- Native NB-CURRENT is now explicitly separated as `hash-pinned STL → voxel mask → oriented binary slices → Cell-12 descriptors`.
- Before any native run, source geometry identity, pre/post Cell-16 config, voxel backend/grid/pitch, slice/raster/component-filter settings and pair-population outputs must be captured.
- The first eventual pilot is one untouched-config B3 N40 STL baseline. It is a native-lineage observation, never a P1B-v2 or historical-Excel parity claim.
- Next AI task: create a no-execution native pilot packet/launcher only after the P2 fields are reviewed; do not calculate descriptors yet.

## Current handoff — STRICT-PARITY-P2A B3 native preflight passed

- Protected NB-CURRENT/LEGACY-PY hashes, B3 N40 STL hash (`beb368e9…afc`) and exact `40×40×40 mm` bbox pass under KMK312.
- Effective config precedence is confirmed: Cell 1 user settings override Cell 9 defaults, then Cell 16 resets execution fields. B3 native contract is `96³ voxel / 100 slices / 200 px / z·x·y / step 1 / min-component 2`.
- Derived physical settings are `0.4040404 mm` layer height, `0.04 mm²/pixel`, `0.2 mm/pixel`, `297` nominal pair evaluations. This is materially different from P1B-v2's legacy fixture.
- P2-G01/G02/G03/G07 pass; G04/G05/G06 remain pending. The launcher rejects `--mode execute`, so no voxelization/slicing/descriptor calculation occurred.
- Next AI task: `STRICT-PARITY-P2B_B3_NATIVE_TRACE_EXECUTION`, one B3 packet only, with voxel/slice/descriptor trace capture.

## Current handoff — STRICT-PARITY-P2B B3 native trace passed

- The hash-pinned B3 N40 STL ran through the exact AST-extracted NB-CURRENT Cell-9/Cell-12 native functions under KMK312: `trimesh voxelized/fill/resize → 96³ mask → 100×200 px z/x/y slices → 297 pair evaluations → descriptor aggregation`.
- The final mask has SHA-256 `917715e8…f55`, `389,040` solid voxels and relative density `0.4397243923611111`. All `300` slice records, `297/297` valid pair records and `1,161,060` component records were retained.
- Exact entrypoint output and an independently reconstructed aggregation compared across `366` fields with `0` mismatches at `1e-12`; QA passed `7/7`, and the output manifest covers `10/10` files with matching hashes. Two consecutive executions produced the same mask hash.
- This confirms a reproducible **B3 native technical lineage only**. It does not establish P1B-v2 shared-PNG equivalence, LEGACY-PY-RESULT parity, historical Excel parity, family generalization, feature utility or inverse design.
- Next AI task: `STRICT-PARITY-P2C_LOCKED_7MODEL_NATIVE_TRACE_EXPANSION_CONTRACT`, a no-execution contract/preflight for B3/C1/L1/F1/F2/T8/T9 before any multi-model native calculation.

## Current handoff — STRICT-PARITY-P2C locked seven-model native expansion preflight passed

- B3/C1/L1/F1/F2/T8/T9 are frozen to seven unique hash-pinned canonical binary N40 STL files; every source matches its T3O registry and has a `40×40×40 mm` bbox.
- B3 reuses the immutable P2B packet and is not recalculated. Future P2D creates six isolated shards in order `C1 → L1 → F1 → F2 → T8 → T9`.
- P2C QA passed `8/8`. Current free space is `88.93 GiB` against a `10 GiB` gate; the six new shards reserve `3.0 GiB`. The planning-only runtime band is `10.1–50.5 min` and is not a benchmark.
- P2C performed no voxelization, slicing, component extraction or descriptor calculation. It imports no NB-CURRENT functions and changes no protected source.
- Next AI task: `STRICT-PARITY-P2D_LOCKED_7MODEL_NATIVE_TRACE_EXPANSION`, using the P2C shard/manifest policy. Reuse B3 and execute only C1/L1/F1/F2/T8/T9 under KMK312.

## Current handoff — STRICT-PARITY-P2D locked seven-model native panel passed

- B3 reuses immutable P2B; C1/L1/F1/F2/T8/T9 completed as six isolated KMK312 shards under one code/config hash. Every shard passed `7/7` QA and `12/12` manifest files; the merged panel passed `8/8`.
- Panel evidence totals `2,100` slice rows, `2,079` pair rows, `8,385,756` component-value rows and `2,562` exact/manual comparison fields with `0` mismatches. Six new shards took `602.0 s` (`10.0 min`) and the P2D pack occupies about `272.6 MB`.
- T8/T9 have distinct source hashes, distinct 96³ mask hashes and `37/197` shared finite numeric output fields different at `1e-12`. The native route therefore does not collapse them into an exact descriptor collision, but predictive usefulness remains unresolved.
- This confirms a representative native technical/x-only panel only. It does not establish LEGACY-PY-RESULT, historical Excel parity, feature selection, prediction or inverse design.
- Next AI task: `STRICT-PARITY-P2E_NATIVE_VS_GOLDEN_CONFIGURATION_DELTA_AUDIT`, a no-y/no-fit comparison that quantifies native P2D versus P1B-v2 frozen-PNG summaries after explicit unit mapping without treating the two input populations as identical.

## Current handoff — STRICT-PARITY-P2E configuration-delta audit passed

- P1B-v2 and P2D use the same hash-pinned N40 STL per B3/C1/L1/F1/F2/T8/T9 (`7/7`). They remain unlike descriptor populations: P1B-v2 is `z / 1000×1000 / 801 / 0.05 mm / frozen colour PNG / min1`, while the P2D proxy is `z / 200×200 / 100 / 0.4040404 mm / 96³ voxel binary / min2`.
- Thus P2E is a configuration-delta description, never an equality/parity test. It contains `70` proxy rows and passes `7/7` QA without creating geometry, images, masks, slices or descriptors and without any y/Excel/model access.
- Under the frozen P2D native z-LTP population, only MassOri and Thickness vary across the seven models. Angle is exactly `90` for every model; Curvature and P/A are exactly `0`; all three are explicitly `degenerate_hold`, not a cross-model bridge or a rejected formula.
- MassOri/Thickness P1B↔P2D values are only descriptive x-to-x `n=7` associations. They do not establish feature utility, prediction, historical-Excel parity, LEGACY-PY-RESULT parity or any feature promotion.
- Next AI task: `STRICT-PARITY-P2F_NATIVE_Z_LTP_DEGENERACY_ROOT_CAUSE_AUDIT`, reading existing P2D pair/component traces only to identify why native z-LTP Angle/Curvature/P-A are constant. No re-slicing, no protected-source modification and no y access.

## Current handoff — STRICT-STEP-001 professor-directed STEP-preferred route passed

- Professor direction (2026-07-24): prefer STP/STEP for image slicing/descriptor extraction; when only STL exists, convert it to STEP first; expose import True/False. The earlier `NB-DEV v0.3` implemented only STL intake and is superseded for new work by development-only `NB-DEV v0.4`.
- `NB-DEV v0.4` keeps approved NB-CURRENT v0.2 byte-identical. With import `True`, direct STEP/STP is selected first; STL-only rows go through an explicit `stl_to_step_proxy` route. Generated and imported populations remain exclusive.
- Full inventory is `58/58`: `33` direct STEP B-reps (B1–B5/C1–C14/L1–L11/F1–F2/T17) and `25` STL-derived STEP proxies (L12–L20/T1–T16 including T8/T9). All 25 source STL files are watertight volumes after in-memory vertex merging, so conversion is technically eligible.
- KMK312 now has the audited `cadquery-ocp 7.9.3.1.1` backend. A B3 direct STEP B-rep normalized to 40 mm and reached the existing slice extractor with `99` valid z pairs. The old raw-STL native route is no longer the preferred source route.
- Important boundary: v0.4 uses B-rep as source authority, then controlled transient tessellation and the existing voxel-mask slicer. A facet-derived STEP proxy cannot recreate lost analytical CAD surfaces. Exact B-rep plane-section rasterization is still the next technical task.
- Next AI task: `STRICT-STEP-002_BREP_PLANE_SECTION_RASTERIZER_PROTOTYPE` on B3 direct STEP. P2F remains a historical STL-native diagnostic, not the new canonical route.

## Current handoff — STRICT-GEOM-001 L28 UBCCz VF45 three-path audit complete; semantic gate pending

- A/B/C each complete `801` masks, `800` overlays and descriptor packets under the same N40 analysis coordinate. Raw/source/config/image-hash/z-index checks pass. This is x-only geometry evidence; it does not define L28's original fabrication size.
- The routes demonstrably disagree: all-slice mean IoU is A↔B `0.968830`, A↔C `0.916337`, B↔C `0.943015` (empty/empty endpoints are agreement). Slice 0174 A/C has IoU `0.443112` and `16,627` XOR pixels. That confirms route-dependent masks at the same z, not one cause.
- B remains a faceted proxy fallback (`0` solids / `455` shells), not recovered CAD. Non-manifold topology → slice artifact → descriptor-bias causality is unresolved. DIRECT-STL FAST-path use is neither accepted nor rejected.
- Pixel semantics is also unresolved: 0174 is line-like with median horizontal foreground span `2 px`; existing artifacts cannot distinguish thin/grazing material from a contour/fill-defect candidate.
- Next AI task: do not expand VF30/VF60. Await approval for the design-only `STRICT-GEOM-002_PIXEL_SEMANTICS_AND_RESOLUTION_STABILITY_GATE`, beginning with analytic fixtures, then selected 0174/normal anomaly resolution/phase checks.

## Current handoff — L28 original-STP descriptor validation package passed

- `L28-DESCVAL-PKG-20260727-002` reuses the immutable SG027 original-STP per-solid archive for L28 UBCCz VF30/VF45/VF60. It replays all `2,403` mask identities, `2,403` slice rows, `2,400` overlays and connected-component counts; all Phase 1–4 and independent invariant gates pass.
- Eleven candidates and `26,418` raw profile values are traceable. D002 sqrt-total-area and D003 MassOri are likely L28-stable; D004 Curvature/D005 Angle remain unresolved; D007–D011 are confirmed-formula derived candidates that remain unselected; D001/D006 retain population/parity holds.
- The 92 high robust-z flags are not demonstrated defects: all are adjacent-area excursions with zero hash, odd-scanline, tiny-component or near-full corroboration. Representative masks are coherent. Use all-slice as reference and filtered values only as sensitivity perturbations.
- Scope remains L28-only. No y, feature selection, model fitting, inverse-design claim, canonical promotion or 58-model expansion is authorized.
- Indices: `RUN-328 / DEC-341 / CHG-326 / LAB-CHG-295 / R09-BB-1294`.
- Next AI task: `L28-SLICE-QA-002_GEOMETRY_AWARE_ANOMALY_CLASSIFIER_NO_Y`, reusing preserved artifacts only.

## Current handoff — L28 STL→STEP and P500/P1000 conclusion closed

- `L28-STL2STP-RESCONV-20260727-001` completed under KMK312 with QA pass. Settings: `IDX-URP4-1-GEOM-L28-TRIAD / CFG-L28-STL2STP-B0-B1-C-P500-P1000-CONCLUSION r1`.
- Reject B0 facet-sewn shell STEP and B1 solidized STEP as both strict and screening replacements for L28. B0 is only relatively better; it is not approved. Original-STP per-solid P1000 remains strict.
- VF45 full-801 diagnosis: A direct STL↔B0 `0.968830`, A↔C `0.805592`, B0↔C `0.801040`. A format conversion does not recover the original CAD/B-rep section identity.
- P500 is not strict. D002–D011 are screening-eligible on the L28 triad; D001 is P1000-required. D004/D005 formula lineage remains unresolved regardless of resolution stability.
- Human review registry: `outputs/L28_VISUAL_REVIEW/L28-QA-REGISTRY-20260727-001/L28_slice_visual_review_registry_20260727.xlsx`; 193 IDs, confirmed noise zero.
- Indices: `RUN-329 / DEC-342 / CHG-327 / LAB-CHG-296 / R09-BB-1295`.
- Next controlled choice: human visual labeling of `L28-QA-####`, or a new Grade A STL repair/reconstruction preregistration. Do not expand the rejected B0/B1 route to 58 models.

## Current handoff — Professor-confirmed generated/imported STL split

- Use `generated_stl`, `imported_stl`, and `original_stp`; do not say “STL route” without the source type.
- `generated_stl` is NB-CURRENT controlled output. Keep `GEN-STL-NATIVE-CONTROLLED` unchanged and use it as a regression guard.
- `imported_stl` is external geometry linked to experimental y. Develop only `IMP-STL-ROBUST-DEV`: mesh preflight → robust triangle-plane intersection → contour/outer/hole/material classification → connected-component-preserving raster → per-slice QA.
- L28 B0/B1 rejection applies only to `IMP-STL-STEP-PROXY-B0/B1`. It does not reject generated STL. A facet STEP does not reconstruct missing solid/topology information.
- `IMP-STP-PERSOLID-REFERENCE` is the paired L28 ground reference for selected-slice and full-triad verification.
- Policy: `outputs/URP4-1_STL_SOURCE_TYPE_AND_IMPORTED_SLICER_POLICY_20260727.md`.
- Indices: `RUN-330 / DEC-343 / CHG-328 / LAB-CHG-297 / R09-BB-1296`.
- Next AI task: `IMSTL-001_IMPORTED_STL_SOURCE_ROUTER_AND_PREFLIGHT_CONTRACT`; no NB-CURRENT edit or y/modeling action.

## Current handoff — IMSTL-001 source router/preflight passed

- `IMSTL-001-20260727-001` passes producer QA and independent `10/10` QA under KMK312. Exact source types/routes are enforced by `urp4.geometry_io.v0_3`; generic ambiguous `stl` fails closed.
- Pilot population: one CINT-04 generated fixture, L28 imported STL VF30/VF45/VF60 and their three paired original STPs. All seven hashes replay; no source mutated.
- Generated fixture: 80 duplicate triangles, 202 non-manifold edges, controlled route retained. Imported L28 each: 14,400 duplicate triangles, 28,460 non-manifold edges, zero boundary edges, zero orientation conflicts, consistent winding.
- Original STP: valid B-rep, 1,521 solids each; paired STL/STP extents agree within ~`3.3e-7 mm`.
- Scientific implication: non-manifold is a diagnostic, not a universal failure label. IMSTL-002 must test duplicate triangle/segment and contour semantics first; no arbitrary hole fill or normal flip.
- Indices: `RUN-331 / DEC-344 / CHG-329 / LAB-CHG-298 / R09-BB-1297`.
- Next AI task: `IMSTL-002_L28_SELECTED_SLICE_ROBUST_INTERSECTION_CONTOUR_PROTOTYPE`; NB-CURRENT, generated route and y remain locked.

## Current handoff — IMSTL-002 selected-slice prototype completed

- `IMSTL-002-20260727-001`; independent QA `10/10 PASS`.
- Historical raw-STL masks replay bit-for-bit. Face/segment deduplication raises mean IoU only `0.414139 → 0.433459`; worst remains `0.020879`. No route advanced.
- Error slices have zero degree-1 endpoints but 192 junctions/128 odd-degree vertices; do not gap-fill, hole-fill or normal-flip.
- Likely target: global even-odd cancellation across overlapping primitives versus original-STP per-solid union.
- Indices: `RUN-332 / DEC-345 / CHG-330 / LAB-CHG-299 / R09-BB-1298`.
- Next: `IMSTL-003_L28_ORIENTED_NONZERO_WINDING_AND_MATERIAL_REGION_DOE`; same frozen 3×3 panel, no NB-CURRENT/y/full-58 action.

## Current handoff — IMSTL-003 algorithm development succeeded

- Scientific run `IMSTL-003-20260727-002`; infrastructure-only `-001` is quarantined. Independent QA `10/10 PASS`.
- `ORIENTED_NONZERO_RAW` improves mean/p05/worst IoU from `0.414139/0.047762/0.019231` to `0.976876/0.971931/0.971267`; mean area difference `1.711%`.
- Do not deduplicate faces before winding and do not add one-pixel dilation; both worsen agreement.
- State: likely primary development candidate, not canonical and not integrated.
- Indices: `RUN-333 / DEC-346 / CHG-331 / LAB-CHG-300 / R09-BB-1299`.
- Next: `IMSTL-004_L28_FULL801_ORIENTED_WINDING_VALIDATION_AND_GENERATED_REGRESSION`; freeze route, no retuning, no y/full58/NB-CURRENT patch.

## Current handoff — IMSTL-004 full L28 validation completed

- Run `IMSTL-004-20260728-001`; KMK312; frozen `ORIENTED_NONZERO_RAW`; all `2,403` masks, `2,400` overlays and `99,269` component rows completed.
- Independent QA `14/14 PASS`; generated-STL regression PASS; NB-CURRENT SHA-256 unchanged.
- All VF30/VF45/VF60 routes pass the frozen screening gate (mean IoU about `0.979`) but fail strict original-STP equivalence. Worst disagreement is concentrated at tiny near-boundary sections; this diagnostic does not alter the strict FAIL.
- Descriptor policy: screening-ready D001/D002/D003/D005/D008/D010/D011; sensitivity D004/D006/D009; hold D007 component-area CV.
- State: imported-STL screening candidate, not canonical and not exact STP replacement. No y/full58 action is authorized.
- Indices: `RUN-334 / DEC-347 / CHG-332 / LAB-CHG-301 / R09-BB-1300`.
- Next: `IMSTL-005_NB_DEV_SOURCE_ROUTER_INTEGRATION`; modify an NB-DEV copy only, preserve generated route, require regression and explicit qualification flags.

## Current handoff — IMSTL-005 NB-DEV integration passed

- Scientific run: `IMSTL-005-20260728-002`; path-length-only `-001` is quarantined.
- Notebook: `NB_DEV_v0_5_IMPORTED_STL_WINDING_ROUTER.ipynb`, SHA-256 `02982c5b...e109`; NB-CURRENT remains unchanged.
- True/imported: L28 VF30 P1000/Z801 completed, 801 trace rows, 800 pairs, 121 numeric slice outputs; transient masks by default.
- False/generated: exact parent native slice-function source and isolated dispatch.
- Independent QA `16/16 PASS`; STL-only normalization replay min IoU `0.997344` across 21 cases.
- State: NB-DEV integration only, L28 screening-qualified; not STP-exact, canonical, full58-generalized or NB-CURRENT-promoted.
- Indices: `RUN-335 / DEC-348 / CHG-333 / LAB-CHG-302 / R09-BB-1301`.
- Next: `IMSTL-006_SMALL_IMPORTED_STL_GENERALIZATION_PREREGISTRATION`; no y/full58 before its small-panel gate.

## Current handoff — IMSTL-006 selected-first generalization partially passed

- Scientific run: `IMSTL-006-20260728-002`; earlier `-001` is an interrupted/quarantined non-result.
- Settings: `IDX-URP4-1-GEOM-IMPORTED-STL / CFG-IMSTL006-SELECTED-GATE-THEN-P1000-Z801 r1`.
- Selected gate pass: B3/C1/L1/T1/T8/T9. Fail: F1 at slices 200/600, IoU `0.949045` versus frozen `0.95` threshold.
- Passed-only full: six models at P1000/Z801; 801 traces, 800 pairs and 15/15 finite average/stdev fields each; catastrophic flags zero.
- Independent QA: all 63 selected P1000/P500 masks reproduce exact hashes; NB-CURRENT/NB-DEV unchanged; no y/all58/training.
- Interpretation: sampled B/C/L/T operation confirmed. F remains unresolved; all-family and physical/STP parity are not claimed.
- Indices: `RUN-336 / DEC-349 / CHG-334 / LAB-CHG-303 / R09-BB-1302`.
- Next: `IMSTL-007_F1_SELECTED_SLICE_RESOLUTION_AND_PIXEL_PHASE_DIAGNOSIS_NO_Y`; do not run F1 full or all58 first.

## Current handoff — HQ v0.1 globally audited and packaged for doctor review

- Indices: `RUN-338 / DEC-351 / CHG-336 / LAB-CHG-305 / R09-BB-1304`.
- Entry point: `URP4-1_DELIVERABLE/URP4_1_HQ.ipynb`; Cell 1 only.
- Final QA under KMK312: AST `93/93`, Controller `40/40`, smoke `9/9`, sources `14/14`, integration `10/10`, full P1000/Z801 `6/6`.
- Clean submission: `URP4-1_SUBMISSION_20260728_v0_1.zip`; SHA-256 `7E6FD75715961BB3653E20333F8BDA1D140B78D3B01EAC8CB604402D481ECB9C`.
- Claim boundary: technical/integration review ready, not scientific production ready. Generated bbox/domain/topology policy, F1/all58, direct STP, Type B and modeling remain open.
- Next AI task: `IMSTL-007_F1_SELECTED_SLICE_RESOLUTION_AND_PIXEL_PHASE_DIAGNOSIS_NO_Y`.
- Chuck input packet: ask the doctor what “40 mm” means for generated families (design domain vs mesh bbox vs final outer solid), whether Type B and direct STP extraction are required in this milestone, and whether F1 may remain explicitly held for the first review.

## Current handoff — HQ v0.1 conditionally merged by the control tower

- Control ID and indices: `CTRL-20260728-M01 / RUN-339 / DEC-352 / CHG-337 / LAB-CHG-306 / R09-BB-1305`.
- Independent replay passed in the live and submission folders: Controller `40/40`, smoke `9/9`, integration `10/10`.
- Clean release identity: ZIP SHA `7E6FD75715961BB3653E20333F8BDA1D140B78D3B01EAC8CB604402D481ECB9C`; restored folder `285/285` exact; manifest `284/284` PASS.
- Official meaning: HQ technical integration accepted; scientific production approval is not granted.
- Locks: F1/all58, direct STP descriptor, Type B, generated 40 mm canonical policy, batch, feature selection, Training and inverse design.
- Next AI task: `IMSTL-007_F1_SELECTED_SLICE_RESOLUTION_AND_PIXEL_PHASE_DIAGNOSIS_NO_Y`.

## Current handoff — IMSTL-007 resolved the bounded F1 gate

- Accepted run and indices: `IMSTL-007-20260728-002 / RUN-340 / DEC-353 / CHG-338 / LAB-CHG-307 / R09-BB-1306`.
- Settings: `IDX-URP4-1-GEOM-IMPORTED-STL / CFG-IMSTL007-F1-P500-750-1000-1500-PHASE4-SELECTED r1`; KMK312.
- Exact replay: prior F1 P500/P1000 P00 masks `18/18`; independent QA replays 144 masks and 432 metrics, max error `1.11e-16`; protected assets `26/26` unchanged.
- Verdict: former slice-200/600 IoU misses are confirmed benign boundary discretization/pixel-phase sensitivity. High-resolution IoUs are `0.973985/0.971320`; all registered gates pass.
- Scope: F1 imported-STL route is screening-qualified for separately authorized P1000/Z801 full extraction. P1500 is diagnostic only.
- Locks: exact STP, all-F/all58, canonical descriptor promotion, y, Training, feature selection, NB-CURRENT edits.
- Next AI task: `IMSTL-008_F1_FULL_P1000_Z801_AND_FAMILY_NONREGRESSION_NO_Y`.

## Current handoff — HQ Blueprint v0.2 full-pipeline skeleton completed

- Indices: `RUN-341 / DEC-354 / CHG-339 / LAB-CHG-308 / R09-BB-1307`.
- Official relationship: `URP4_1_HQ.ipynb` v0.1 remains official; `URP4_1_HQ_BLUEPRINT_v0_2.ipynb` is a development/status-only blueprint, not a replacement or submission build.
- Backbone: semantic `HQ-CELL-00..21`; READY `9`, EXPERIMENTAL `7`, LOCKED `5`, PLANNED `1`; Type B is a BLOCKED sub-capability inside the experimental geometry stage.
- Controller: only `HQ-CELL-01` is the public edit surface. `HQ-CELL-02` requires KMK312, derives/fixes 40 mm/P1000/Z801 values, hashes the config and fails closed on unsupported execution.
- Analysis geometry policy: target `40×40×40 mm`, source preserved, normalized derivative separate. Generated normalization stays blocked under `HQ-GEOM-001`.
- Descriptor policy: RUN-139 nine scalars = minimal service; XREG-v2.7 = 542 unselected FAST no-y candidates; full unselected X and later Feature Selection are separate.
- QA: protected `31/31`; HQ v0.1 Controller/smoke/audit/source `40/40 · 9/9 · 10/10 · 14/14`.
- Locks: IMSTL-008/F1 full/all58/y/x-y/selection/training/ensemble/inverse/protected-source edits.
- Next AI task: `IMSTL-008_F1_FULL_P1000_Z801_AND_FAMILY_NONREGRESSION_NO_Y`.

## Current handoff — IMSTL-008 F1 full P1000/Z801 completed

- Indices: `RUN-342 / DEC-355 / CHG-340 / LAB-CHG-309 / R09-BB-1308`.
- Accepted run: `IMSTL-008-20260728-002`; `-001` is an infrastructure-only Windows path-length quarantine.
- F1 producer: 801 slices / 800 overlays / 39,506 slice components / 38,187 overlay components / nine RUN-139 scalars; PNG mismatch and remaining PNG `0`.
- Independent QA: scalar replay `9/9` at max error `7.11e-15`; F1 selected masks `9/9 exact`; prior B/C/L/T masks `54/54 exact`; protected `31/31`.
- Scientific boundary: F1 full technical route confirmed; F001–F006 confirmed lineage; F007/F008 likely; exact STP, other F/all58, canonical descriptor and performance utility unresolved.
- Locks: y/x-y, Feature Selection, Training, fit, prediction, all58, NB-CURRENT/LEGACY-PY/Excel edits and inverse design.
- Next AI task: `HQ-GEOM-001_GENERATED_FAMILY_40MM_NORMALIZATION_IMPLEMENTATION_AND_REGRESSION_NO_Y`.

## Current handoff — HQ-GEOM-001 technical computation passed; official merge held

- Indices: `RUN-343 / DEC-356 / CHG-341 / LAB-CHG-310 / R09-BB-1309`.
- Completed: isolated generated-STL 40 mm analysis-copy writer (`urp4.geometry_io.v0_5`), source/derivative provenance, Lattice A/TPMS/Voxel native RUN-139 P1000/Z801 `3/3`, independent scalar replay `27/27` (`1.42e-14` max error).
- Geometry: source bboxes `41.407375/39.5/38.0 mm` become exact N40 with uniform scales `0.966011482/1.012658228/1.052631579`. Source bytes/topology counters are preserved; Lattice and TPMS stay `topology_clean=false` and are not repaired.
- Audit correction: the first new verifier omitted byte size from the established tree identity and falsely reported `28/31`. Corrected relative-path + SHA-256 + byte-size audit is `31/31`, and local manifests are `3/3` valid. No protected source, result tree, release artifact or baseline changed.
- Next AI task: `HQ-GEOM-002_VERSIONED_DEVELOPMENT_ROUTE_INTEGRATION_AND_CONTRACT_TESTS_NO_Y` (add the passed route only to a new development revision; do not patch HQ v0.1).
- Locks: no HQ v0.1 controller change, no physical-canonical claim, no y/x-y/selection/training/all58/direct-STP/NB-CURRENT/LEGACY-PY/Excel change.

## Current handoff — HQ-GEOM-002 Voxel N40 development route passed

- Indices: `RUN-344 / DEC-357 / CHG-342 / LAB-CHG-311 / R09-BB-1310`.
- Added only `URP4-1_DELIVERABLE/urp4/hq/v0_3/`: a development-only N40 route; HQ v0.1 and Blueprint v0.2 are unchanged.
- Voxel (`topology_clean=true`) repeats the HQ-GEOM-001 N40 derivative exactly and passes native P1000/Z801 `801/800/9`, PNG mismatch/remaining `0/0`. Contract `6/6`, reference parity `6/6`, protected audit `31/31`.
- Safety boundary: Lattice A/TPMS are rejected before extraction because source `topology_clean=false`. This is not repair or a scientific rejection; it is a required separate topology-policy decision.
- Next AI task: `HQ-GEOM-003_GENERATED_LATTICE_TPMS_TOPOLOGY_EXCEPTION_CONTRACT_NO_Y` (preregister only; no Lattice/TPMS calculation until the policy is explicitly set).
- Locks: no HQ v0.1 change, y/x-y, Feature Selection, Training, fitting, prediction, inverse design, all58, NB-CURRENT/LEGACY-PY/Excel or physical-canonical claim.

## Current handoff — HQ-GEOM-003 Lattice/TPMS topology policy is pending

- Indices: `RUN-345 / DEC-358 / CHG-343 / LAB-CHG-312 / R09-BB-1311`.
- Read-only preflight: Lattice A is non-clean (`6,798` non-manifold edges; `8,392` components; non-watertight), TPMS Gyroid is non-clean (`103` non-manifold edges; `73` orientation conflicts; one component). Source hashes and protected audit `31/31` pass.
- Current policy: hold both sources from HQ v0.3. Automatic exception is rejected. `regenerate` is likely preferred if the controlled generator can emit a clean STL; `repair` needs its own hash-bound contract; `exclude` is a fallback.
- Chuck input packet: `results/HQ-GEOM-003/HQ-GEOM-003-20260728-001/CHUCK_INPUT_PACKET_TOPOLOGY_POLICY_20260728.md`.
- Next AI task: after the doctor decides Lattice/TPMS each as regenerate, repair, or exclude, preregister only that matching validation work.

## Current handoff — STRICT-STEP-002 B3 direct B-rep prototype passed

- Indices: `RUN-346 / DEC-359 / CHG-344 / LAB-CHG-313 / R09-BB-1312`.
- Original B3 STEP is direct input authority: N40 z-mid native section `150` edges → `25` closed face-eligible wires → `25` components at both P500/P1000. Area `202.4448/202.5216 mm²`, holes `0`, and the 2-pixel filter changes no pixel.
- QA: direct-source hash, four saved image hashes/pixel counts, component population and protected `31/31` all pass. No STL/proxy, full descriptor, y/modeling or protected-source action.
- Next AI task: `STRICT-STEP-003_B3_DIRECT_BREP_SELECTED_SLICE_RESOLUTION_PHASE_AND_ROUTE_DELTA_CONTRACT_NO_Y`; preregister only before an 801-slice direct-STEP run.
- Separate pending input: Lattice/TPMS topology treatment remains in `HQ-GEOM-003` Chuck input packet.

## Current handoff — STRICT-STEP-003 direct-STEP selected-slice contract passed

- Indices: `RUN-347 / DEC-360 / CHG-345 / LAB-CHG-314 / R09-BB-1313`.
- Status: contract-only QA PASS (`8/8`); source and protected assets `31/31` pass. No new raster/image/descriptor output exists by design.
- Locked next panel: B3 original direct STEP; N40 z `10/20/30`, P500/P1000/P1500, pixel phase `00/HH`, direct B-rep versus same-source controlled tessellation (`36` cases).
- Policy: direct noneligible wires are quarantined (never healed); all future masks/tables/diagnostics must be retained; no automatic route winner.
- Next AI task: `STRICT-STEP-004_B3_DIRECT_BREP_SELECTED_SLICE_RESOLUTION_PHASE_AND_ROUTE_DELTA_EXECUTION_NO_Y`.
- Locks: no Z801, descriptor aggregation, y/x-y, feature selection, training, all58 or protected-source modification.

## Current handoff — STRICT-STEP-004 B3 panel completed; route review required

- Indices: `RUN-348 / DEC-361 / CHG-346 / LAB-CHG-315 / R09-BB-1314`.
- Evidence: accepted `-002` has all `36` planned cases and `72` hash-valid raw/filtered masks; independent artifact QA passes. `-001` timeout is quarantine only; CSV recovery did not rerasterize images.
- Result: direct-B-rep versus controlled-tessellation IoU spans `0.924340–0.997717`.
- Next: `STRICT-STEP-005_B3_ROUTE_DELTA_VISUAL_FORENSICS_AND_STOP_GATE_NO_Y`; review low-IoU cases before any direct-STEP Z801/descriptor action.

## Current handoff — STRICT-STEP-005 phase-dominated route delta

- `RUN-349` completed no-y forensic review of existing B3 masks. PHASE-00 route IoU is `0.99668–0.99772`; PHASE-HH is `0.92434–0.97589`.
- Hold: PHASE-00 is only a candidate production convention; no direct Z801/descriptor authorization yet.
- Next: `STRICT-STEP-006_B3_PHASE00_DIRECT_STEP_OVERLAY_TRACE_CONTRACT_NO_Y`.

## Current handoff — STRICT-STEP-006 overlay-trace contract passed

- `RUN-350`: six local B3 overlay traces are preregistered at P1000/PHASE-00 with 0.05 mm spacing; direct B-rep and controlled-tessellation will retain masks, overlays and component/wire traces.
- Next: `STRICT-STEP-007_B3_PHASE00_OVERLAY_TRACE_EXECUTION_AND_ROUTE_DELTA_NO_Y`.

## Current handoff — STRICT-STEP-007 local overlays retained

- `RUN-351`: six B3 local PHASE-00 overlay traces retained (`18` masks, `12` overlays). Naming-only recovery did not rerasterize artifacts.
- Next: `STRICT-STEP-008_B3_OVERLAY_COMPONENT_DELTA_REVIEW_AND_Z801_STOP_GATE_NO_Y`; analyze purple/component deltas before direct Z801.

## Current handoff — STRICT-STEP-008 holds direct Z801 on red/blue population sensitivity

- `RUN-352`: purple topology stable (all six matched component counts; max pixel delta `0.318%`), but red/blue component deltas reach `47`.
- Next: `STRICT-STEP-009_B3_CHANGE_REGION_COMPONENT_SENSITIVITY_CONTRACT_NO_Y`, not Z801.

## Current handoff — STRICT-STEP-009 preserves the 2-pixel rule

- `RUN-353`: red/blue count delta is tiny-fragment dominated, but raising the 2 px threshold changes retained population; no threshold patch is allowed.
- Next: `STRICT-STEP-010_B3_DIRECT_VS_TESS_OVERLAY_DESCRIPTOR_SENSITIVITY_CONTRACT_NO_Y`.

## Current handoff — STRICT-STEP-010 local metric contract passed

- `RUN-354`: fixed six local red/blue/purple/component/MassOri-style sensitivity metrics over existing B3 overlays; no canonical descriptor claim.
- Next: `STRICT-STEP-011_B3_LOCAL_OVERLAY_DESCRIPTOR_SENSITIVITY_EXECUTION_NO_Y`.

## Current handoff — STRICT-STEP-011 splits area versus component route stability

- `RUN-355`: local MassOri-style area ratio is route-stable (`0.0352%` max); red/blue component counts are not (`12.63%` max).
- Next: `STRICT-STEP-012_B3_AREA_ONLY_DIRECT_STEP_TRACE_SCOPE_DECISION_NO_Y`; no general direct-STEP Z801 permission.

## Current handoff — STRICT-STEP-012 area-only scope is separated

- `RUN-356`: A001 primitive areas and A002 MassOri-style ratio are candidate traceable; component-derived outputs remain held.
- Next: `STRICT-STEP-013_B3_P1000_Z801_AREA_PRIMITIVE_TRACE_CONTRACT_NO_Y`.

## Current handoff — STRICT-STEP-014 running checkpointed B3 Z801 area trace

- The KMK312 `RUN_STRICT_STEP_014.cmd` launcher is active. Checkpoint target is `1602` route×slice rows; current task may be resumed from its run folder.
- Scope remains primitive areas and MassOri-style ratio only; component/Angle/Curvature/full descriptor/y remain blocked.
- Completion QA is prepared but intentionally not run until checkpoint `1602/1602`.

## Current handoff — ROUTE-VALID-001 fixes source eligibility before imported-STL claims

- `RUN-357 / DEC-362`: actual asset SHA audit is `24 paired_confirmed / 9 paired_likely / 25 stl_only`, with zero mismatch. C1 is confirmed; B3/L1 are sensitivity-only; T17 is orientation-held; `L12–L20/T1–T16` have no original STEP comparison route.
- Terminology lock: Route A–B is original STEP direct B-rep vs controlled tessellation from the same STEP; it is **not** imported-STL validation. Route A–C is original STEP vs separately stored paired imported STL.
- C1 P1000 z-mid A–B and A–C both exact: IoU `1.0`, symmetric difference `0 px`, area delta `0`. The documented N40 grid adapter handles C1's `1.2716e-6 mm` STL-export micro-anisotropy without source mutation; general adoption remains likely/unresolved.
- Next: review C1 packet, then preregister B1/L7/F1 confirmed-pair selected-slice extension only. No full Z801, descriptors, y, learning or NB-CURRENT edits.

## Current handoff — ROUTE-VALID-002 supports B/C/L confirmed-pair selected slices

- `RUN-358 / DEC-363`: B1 and L7 passed fresh source SHA contracts and completed Route A/B/C at N40 z-mid PHASE-00, P500/P1000. All eight route comparisons are exact: IoU `1.0`, symmetric difference `0 px`, area delta `0`; QA `14/14 PASS`.
- B1 uses a run-local explicit N40 grid adapter because its paired STL has a `2.5431e-6 mm` export residual. L7 needs no adapter. A–B remains same-source STEP representation consistency, while A–C is the actual paired imported-STL observation.
- Next: `ROUTE-VALID-003_F1_STRESS_TEST`. Do not launch full Z801, descriptor/Excel/LEGACY-PY parity, y, model fitting, all58 or NB integration.

## Current handoff — ROUTE-VALID-003 narrows F1 to one z400 attribution test

- `RUN-359 / DEC-364`: F1 completed N40 z `[0,1,100,200,400,600,700,799,800]` × P500/P750/P1000/P1500 × four pixel phases. Route A/B each have 144 new hash-registered masks; Route C reuses 144 frozen IMSTL-007 masks. Independent QA is `11/11 PASS`, with 288 metrics replayed at max error `0.0`.
- Result: A–B is exact in `138/144` cases and A–C in `129/144`. All boundary slices are exact. The six non-boundary A–C residuals co-occur with A–B residuals at z400, so they are **not** evidence of an imported-STL slicer defect. F1 route status is unresolved, not failed.
- Next: only `ROUTE-VALID-003A_F1_Z400_TARGETED_ATTRIBUTION_REPLAY_NO_Y` (P750/P1000/P1500, phases 00/50X): slow exact-BRepClassifier anchor comparison plus preregistered tessellation deflection sensitivity. Route C must be reused, not regenerated. Full Z801, descriptors, Excel/LEGACY-PY, y, fitting, all58 and NB changes remain locked.

## Current handoff — ROUTE-VALID-004 opens only a versioned development gate

- `RUN-360 / DEC-365`: ROUTE-VALID-003A is now explicitly an operational quarantine, not a scientific failure. It contributes no official result, does not reject ROUTE-VALID-003 and does not block technical route-controller development. F1 z400 remains `F1_Z400_UNRESOLVED`.
- `paired_confirmed` imported STL may enter only a new versioned controller with source/config/output hashes, identity status, explicit route/grid configuration, retained warnings and fail-closed preflight. `paired_likely` is sensitivity-only; STL-only and orientation-held sources remain outside this integration gate.
- Production science is still closed: do not claim descriptor/full-Z801/Excel/LEGACY-PY/y parity or replace NB-CURRENT. Deferred STRICT work is `STRICT-F1-001_EXACT_A_LONG_RUN_AND_DECLARED_DEFLECTION_SENSITIVITY_NO_Y`.
- Next: `NB-INTEGRATE-001_IMPORT_ROUTE_CONTROLLER_VERSIONED_DEVELOPMENT_NO_Y` contract-build and fixture verification only; no source/notebook mutation until separately approved.

## Current handoff — NB-INTEGRATE-001 development controller is merged; scientific execution remains locked

- `RUN-361 / DEC-366`: `urp4.route_policy.v0_1` plus NB-DEV v0.6 implement the ROUTE-VALID-004 policy as a fail-closed, status-only preflight. NB-CURRENT, NB-ORIG and LEGACY-PY were not modified.
- Only a hash-bound `paired_confirmed` imported STL gets a Route-C development decision. F1 includes `F1_Z400_UNRESOLVED`. Every approved decision has `execution_enabled=false`; the controller cannot authorize slice/descriptor/y/model work.
- QA: `9/9` controller fixtures, `13/13` independent, `8/8` notebook static, protected `31/31`, manifest `22/22`. Runtime is canonical project-local `tools/envs/KMK312/python.exe` / Python 3.12.12. A partial duplicate profile environment is quarantined and unused.
- Stop point: conditional development merge is complete. Do not auto-run a next task. `STRICT-F1-001` remains a later scientific resource task.

## Current handoff — STRICT-STEP-021/022 make B3 descriptor populations inspectable

- `RUN-362`: B3 original STEP Route-A Z801 raw primitive extraction is complete and independently QA-passed `9/9`: `801` slices, `800` overlays, `36,535` slice-component rows and `35,876` overlay-component rows. The quarantined concurrent-worker run is never a scientific input.
- `RUN-363 / DEC-367`: LEGACY2 and replayable LEGACY3 formula populations were recomputed from those raw tables only (`38` scalar values, QA `9/9`). This is **code-formula replay**, not Excel/Ntop/physical parity. LEGACY2 Curvature/LTP includes 16 empty-overlay zeros; LEGACY3 P/A remains artifact-gap unresolved.
- Next: preregister `STRICT-STEP-023_B3_TEMPORARY_PNG_DIRECT_LEGACY_PY_IMAGE_EXECUTION_PARITY_NO_Y`; do not regenerate without the isolated temporary-artifact/eviction contract. No y/Training/NB-CURRENT edits.

## Current handoff — B3 Route-A direct image-code parity is now closed

- `RUN-364 / DEC-368`: original B3 STEP Route-A temporary PNGs reproduce accepted raw pixel totals exactly (`801/800`). After correcting two LEGACY2 empty-population semantics in 022-003, actual unmodified LEGACY2/LEGACY3 PNG execution matches all `38/38` replayable scalars (≤`1e-10`); recovery QA `7/7 PASS`.
- LEGACY3 red∪purple P/A is directly available for B3 (`0.054791 px^-1` weighted avg, `0.008234 px^-1` population std). Bulk temporary images (`1,601`) were evicted after success; 9 anchors remain. The original failed gate is preserved as a diagnostic record.
- Next: `STRICT-STEP-024_B3_HISTORICAL_X_ONLY_CROSSWALK_NO_Y` — map historical Excel B3 rows/columns explicitly and compare descriptor values scale-aware. No fitting, feature promotion, y, all58 or protected-source edits.

## Current handoff — B3 historical x-only crosswalk is complete

- `RUN-365 / DEC-369`: `총정리!row9` B3 family-summary `K:AY` was mapped to 40 current direct LEGACY-PY descriptor values, QA `8/8 PASS`. Scale factors are approximately one and Pearson r is ≥`0.999146` per descriptor; figure and exact cell-level CSV are retained.
- This supports B3 lineage only. Historical Thickness LTP is closer to a non-empty slice population; MassOri stdev ratios are denominator-sensitive. It does not unlock physical/Excel general parity, y, fitting, selection or all58.
- Next: prepare a small C/L/F/T x-only panel selection using asset eligibility and existing route evidence. Choose models before running any new expensive PNG/direct-legacy calculation.

## Current handoff — immutable whole-project evidence cutoff v1.0

- `HANDOFF-CUTOFF-20260731-001` is a read-only global reconciliation package at `experiments/lab_001_xy_connection_20260626/results/HANDOFF-SYNC-001/HANDOFF-CUTOFF-20260731-001/`.
- Independent cutoff QA passes `34/34`; it is a consistency/reproducibility handoff, not a production-science, y/Training, or inverse-design claim.
- `STRICT-STEP-026` remains a research-control-tower-owned **running** worker. This cutoff did not touch or QA it. After owner completion/QA, create a new cutoff/revision instead of overwriting v1.0.
