# URP4-1 HQ v0.1 — global debug, validation and submission audit

Date: 2026-07-28 KST  
Runtime: `KMK312 / Python 3.12.12`  
Scope: `URP4-1_DELIVERABLE/` and its preserved validation evidence

## 1. Executive verdict

**HQ v0.1 is ready to submit to the doctor as an integration/technical-review build, with explicit limitations. It is not yet a scientifically complete production pipeline.**

The notebook and Python modules now execute the approved import/generate routes, image readback, nine RUN-139 scalar outputs, manifests and exports. The package fails closed for Training, feature selection, batch, direct STP descriptor extraction and unqualified descriptor scopes.

Submission language must distinguish:

- **technical chain passed**: code path executes and leaves reproducible trace artifacts;
- **scientific/production approval unresolved**: family-wide validity, geometry-domain policy, F-family behavior, STP direct extraction and modeling are not yet approved.

## 2. Defects found and corrected

| ID | defect | correction | regression evidence |
|---|---|---|---|
| DBG-001 | Test scripts depended on an externally set `PYTHONPATH`. | Added self-contained package-root bootstrap. | Direct KMK312 invocation succeeds. |
| DBG-002 | TPMS ignored Cell-1 `target_vf` and `expected_size_mm`. | Controller values now replace registry VF and TPMS size before request creation. | TPMS VF 0.50 smoke/full chain PASS; unqualified VF rejected. |
| DBG-003 | Run folders could collide within one second. | Timestamp includes microseconds; overwrite remains forbidden. | Repeated imported runs created separate folders. |
| DBG-004 | Generated `KEEP_FLAGGED` could silently behave like streaming. | Generated route now fails closed for this unsupported policy. | Controller contract rejection PASS. |
| DBG-005 | Several conflicting or empty Cell-1 settings were silently ignored. | Added fail-closed checks for identifiers, output root, slice/cell definition conflicts, generation source/path conflicts and Training method IDs. | Controller contract `40/40 PASS`. |
| DBG-006 | L28 tests depended on files outside the deliverable. | Added exact-hash STL/STP fixtures inside `tests/fixtures/`. | STL/STP hashes match originals byte-for-byte. |
| DBG-007 | TPMS/Voxel relative artifact paths resolved against the caller CWD. | Resolve serialized relative paths against the deliverable root. | Project-root CWD smoke `9/9 PASS`. |
| DBG-008 | Earlier report still described actual Type-A full runs as partial. | Replaced with final six-case full-chain evidence and scientific caveats. | Integration audit `10/10 PASS`. |

## 3. Final automated validation

| validation | result | evidence |
|---|---:|---|
| Python source syntax | 93/93 PASS | AST parse under KMK312 |
| HQ notebook structure | 13 cells, 11 code cells, valid nbformat | `URP4_1_HQ.ipynb` |
| Single user-edit cell | 1/1 PASS | `outputs/hq_audit/notebook_cell_tree.csv` |
| Controller acceptance/rejection contract | 40/40 PASS | `tests/controller_contract.py` |
| Fast generation/import/guard smoke | 9/9 PASS | `outputs/smoke/smoke_results.csv` |
| Full P1000/Z801 chain | 6/6 PASS | `outputs/smoke_full_descriptor/full_descriptor_smoke_results.csv` |
| Imported L28 repeat | exact across descriptor and four primitive CSVs | two completed L28 runs |
| Output manifests | 5/5 selected run manifests PASS | independent SHA/size replay |
| Immutable source identity | 14/14 PASS | `outputs/hq_audit/source_identity_audit.csv` |
| Integrated evidence gates | 10/10 PASS | `outputs/hq_audit/smoke_and_integration_audit.csv` |
| Potential hard-coded secret assignments | 0 detected in 808 scanned files | static pattern scan |

Every full-chain case produced 801 slice rows, 800 overlay rows, nine scalar rows, zero PNG readback mismatch and zero remaining temporary PNGs.

## 4. Requirement checklist summary

The machine-readable checklist is `URP4-1_HQ_SUBMISSION_REQUIREMENTS_CHECKLIST_20260728.csv`.

### Passed

- One visible Controller cell and frozen hash-addressed configuration.
- Import/generate XOR and explicit route selection.
- Lattice Type A, TPMS and Voxel generation-to-descriptor technical chain.
- Imported L28 STL robust route and exact two-run reproduction.
- Original STP strict/reference preflight.
- Image creation, PNG readback, pixel/component tables, nine scalar results and export.
- Non-overwriting run folders and per-run manifests.
- Source identity protection and fail-closed unsupported scopes.
- Self-contained L28 test fixtures and caller-CWD-independent smoke execution.

### Passed conditionally

- Imported STL route: L28 and sampled B/C/L/T evidence exists, but F1 and all58 are not cleared.
- Generator routes: full technical execution passed, but production geometry/printability policy is not approved.
- Original STP: preflight/reference works; direct descriptor extraction does not.

### Not complete

- Lattice Type B generation because the identity-locked `Variables.xlsx` is unavailable.
- F1 pixel-phase/resolution diagnosis and F-family imported-STL clearance.
- All58 imported-STL generalization.
- Direct STP/STEP-to-descriptor adapter.
- Batch execution, feature selection, Training, x-y modeling and inverse design.
- Point, surface, lattice and candidate descriptor scopes in the HQ UI.

## 5. Scientific risks that must accompany submission

### SR-001 — generated 40 mm domain policy

The full technical runs reported the following source mesh bbox extents:

| family | extent (x/y/z) | topology_clean |
|---|---:|---|
| controlled fixture | 40.0 / 40.0 / 40.0 mm | true |
| Lattice Type A | 41.4074 / 41.4074 / 41.4074 mm | false |
| TPMS | 39.5 / 39.5 / 39.5 mm | false |
| Voxel | 38.0 / 38.0 / 38.0 mm | true |

The chain executed, but these are not equivalent definitions of a 40 mm analysis domain. The doctor should confirm whether the correct policy is domain-coordinate slicing, uniform normalization, generator correction, or family-specific treatment. Until then, these generated full runs are technical evidence, not canonical descriptor values.

### SR-002 — topology policy

Lattice Type A and TPMS passed the current native route despite `topology_clean=false`. The current default does not reject topology risk. That is intentional for source-replay testing, but production acceptance criteria are unresolved.

### SR-003 — imported-STL generalization

F1 missed the representative IoU threshold by a narrow boundary-sensitive margin and remains held. The L28 route cannot be called universal before F1 and broader-family evidence are resolved.

## 6. Doctor-submission recommendation

Submit these four items together:

1. `URP4_1_HQ.ipynb`
2. `README_RUN.md`
3. this audit and the CSV checklist
4. the clean `URP4-1_SUBMISSION_20260728_v0_1` package/ZIP without historical failed runs or cache files

The clean package was independently exercised from its copied files: Controller contract `40/40`, fast smoke `9/9`, and integrated audit `10/10` all passed.

Recommended claim:

> HQ v0.1 integrates the current generation/import routes, image-based slice descriptor extraction and traceable export in KMK312. L28 repeatability and generated Lattice A/TPMS/Voxel technical chains pass. Training, batch, direct STP descriptor extraction, Type B and unresolved scientific policies remain fail-closed or explicitly listed for the next stage.

Do not claim:

- universal imported-STL correctness;
- direct STP structure-factor extraction;
- production-ready Lattice/TPMS/Voxel geometry;
- completed feature selection, Training or inverse design.

## 7. Inputs/questions for the doctor

1. Is Lattice Type B required in this submission, and can the identity-locked `Variables.xlsx` be provided?
2. For generated families, should 40 mm mean the design domain, the mesh bounding box, or the final solid outer envelope?
3. Must v0.1 directly extract descriptors from STP, or is STP reference/preflight plus imported-STL extraction acceptable for this milestone?
4. Should F1 be resolved before review, or may it remain an explicitly held family case?
5. When the new compression dataset arrives, may the fail-closed Training/feature-selection gate be opened under grouped evaluation?

## 8. Next execution order

1. `IMSTL-007_F1_SELECTED_SLICE_RESOLUTION_AND_PIXEL_PHASE_DIAGNOSIS_NO_Y`
2. generated-family 40 mm domain/topology policy decision and regression fixture
3. Type B workbook intake or formal scope exclusion
4. direct STP descriptor adapter decision
5. all58 imported route audit
6. official y intake, leakage-safe feature selection and method integration
