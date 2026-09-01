# R2 preregistration — minimal packaging repair

## Identity and purpose

- Input: `URP4-1_PROFESSOR_HANDOFF_20260801_v1_1_r1.zip`
- Input SHA: `7135fab710b386f6d6cbef3fe02d8103cde2ffff31532db7153366542d5f8d7c`
- Input status: immutable; never overwrite.
- Planned output: `URP4-1_PROFESSOR_HANDOFF_20260801_v1_1_r2.zip`
- Schema: retain `PROJECT_SCHEMA v1.1`; r2 is a packaging/handoff revision, not a scientific schema revision.
- Purpose: repair delivery, current-state metadata, manifest scope, links and portability only.

## Prohibited work

- No new research calculation, descriptor extraction, C1/F1/all58 execution, Training fit/predict, feature selection, model promotion or inverse-design claim.
- No edits to NB-CURRENT, NB-ORIG, LEGACY-PY, original Excel/Training notebooks or geometry bytes.
- No overwrite of r1 or prior QA.
- No deletion of partial Drive folders without separate authorization and hash review.

## Build sequence

1. Extract r1 once to a new short-path r2 staging root.
2. Record r1 member manifest and protected scientific hash baseline.
3. Apply only `REPAIR_SCOPE.csv` R2-S01 through R2-S10.
4. Re-run state, parser, link and protected-asset preseal QA.
5. Freeze content. Generate explicit `SOURCE_CUTOFF_MANIFEST`, `PACKAGE_VIEW_MANIFEST`, scope map and `PACKAGE_CONTENT_SHA256` in that order; document the single self-exclusion.
6. Seal exactly one `URP4-1_PROFESSOR_HANDOFF_20260801_v1_1_r2.zip` with one package root; do not edit after sealing.
7. Outside the ZIP, generate:
   - `URP4-1_PROFESSOR_HANDOFF_20260801_v1_1_r2.zip.sha256`
   - `INDEPENDENT_PACKAGE_QA_v1_1_r2.json`
   - `EXTRACTED_SMOKE_QA_v1_1_r2.json`
   - `DELIVERY_BUNDLE_INDEX_v1_1_r2.json`
   - `DELIVERY_README_FIRST_v1_1_r2.md`
8. Upload r2, sidecars and exact geometry to the specified Drive folder; grant professor viewer access.
9. Download r2 from Drive into a clean short path and repeat final QA.
10. Run a new independent submission review. Stop before any scientific work.

## State synchronization contract

- Current C1: `completed_with_evidence`, 801/801 slices, 800/800 overlays, 40 scalars, IQA 9/9.
- Current Training: `closed_for_submission_as_blocked_with_evidence`; 9/9 audit, 1/9 replay, native runtime blocker.
- Historical C1 running text may exist only where explicitly tagged `historical` or `superseded`.
- Master ledger current summary must show running=0 for completed C1.
- Internal package state must distinguish `content_frozen` from external `delivery_finalized`.

## Manifest contract

- Source-cutoff manifest: authenticates immutable source cutoff files only; must match 22/22.
- Package-view manifest: authenticates the r2 package-map files after repairs; zero mismatch.
- Included/excluded manifest: every source/package pair either exact or explicitly mapped to an immutable snapshot/revision.
- Package content manifest: every payload file except itself; exactly one documented self-exclusion.
- External finalization receipt: authenticates the sealed ZIP itself and is delivered adjacent to it.

## Link and evidence contract

- Markdown relative missing links: 0.
- HTML local missing links: 0.
- Evidence Index must preserve historical hashes and add terminal/snapshot rows; no silent overwrite.
- The missing HQ-GEOM-003 source locator and two mutable-source drifts must resolve to immutable snapshot evidence or an explicit historical exception.

## Reproducibility contract

- Complete environment lock/export and checksum.
- Relative read-only launcher/path-map.
- Fresh/second-PC import and package-verifier smoke only.
- No environment binaries required inside ZIP; no research calculation during smoke.

## Drive contract

- Destination folder ID: `1kv63P0skzEYBgz6b51L1xRk8WBf8D6sk`.
- One canonical r2 ZIP plus five named sidecar/readme files.
- Geometry: exactly 67 files, 34 STL + 33 STP, 1,411,469,295 bytes, original filenames/bytes.
- Record remote IDs/URLs/size/permissions and verify a downloaded ZIP hash.
- Non-owner professor viewer access must pass.

## Protected evidence contract

Scientific reports, C1 evidence, Training evidence, AI-Lattice pilot evidence, route evidence and original assets must retain r1 hashes unless a path-only package reference must change. Every allowed exception must be enumerated before sealing. Scientific overclaim count must remain zero.

## Acceptance gate

- Critical findings: 0.
- Unresolved major packaging defects: 0.
- ZIP CRC/root/extraction: PASS.
- Source/package/member manifests: PASS under explicit scopes.
- State synchronization: PASS.
- REQ-010 delivery finalization: PASS through exact external sidecar contract.
- Broken links: 0.
- Protected scientific hashes: PASS.
- Drive delivery and non-owner access: PASS.
- Independent score: at least 90/100.

Any failure quarantines r2 and forbids canonical submission.
