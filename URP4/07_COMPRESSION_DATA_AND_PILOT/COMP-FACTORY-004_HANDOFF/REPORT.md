# B/C/L + Voronoi compression intake and grouped pilot handoff

- Date: `2026-08-02 KST`
- Index: `RUN-366 / DEC-370 / CHG-355 / LAB-CHG-321 / R09-BB-1324`
- Runtime: project-local `tools/envs/KMK312/python.exe` / Python `3.12.12`
- Status: `TECHNICAL_PIPELINE_COMPLETE_WITH_WARNINGS`
- Scientific promotion: `NO`

## 1. Source preservation and source decision

The eleven received Excel workbooks are preserved byte-for-byte under
`data/raw/doctor_compression_data_20260802/`. The copy manifest records the
original path, preserved path, byte size and SHA-256; all `11/11` copy hashes
match. None of the original workbooks was modified.

The B/C/L source audit found that `New_VF30.xlsx`, `New_VF45.xlsx` and
`New_VF60.xlsx` contain explicit model labels and populated cached compression
outputs. They are therefore the primary B/C/L performance sources. The three
`Compression_Worked_VF*.xlsx` files and three small
`Compression_VF*_Summary.xlsx` files remain reference-only: their generic
trailing rows cannot provide a safe current model-ID crosswalk.

For Voronoi, `Voronoi_Summary.xlsx / Raw data` contains 30 explicit IDs and is
the primary performance source. `Compression_Worked_Voronoi.xlsx` is retained
for provenance and later cross-checking.

## 2. Exact x-y intake

The intake joins performance rows to `Structural_Factors_All.xlsx` only through
explicit normalized IDs; no row-order inference is used.

| Cohort | Performance rows | Exact x-y joins | y-only missing x | x-only missing y |
|---|---:|---:|---:|---:|
| B/C/L and extended labels | 198 | 137 | 61 | 3 |
| Voronoi | 30 | 30 | 0 | 0 |
| Total | 228 | 167 | 61 | 3 |

- Finite target candidates: `16`
- Structural-factor registry: `45` columns
- Producer QA: `PASS`
- Independent intake QA: `15/15 PASS`

The 61 y-only rows are retained in the crosswalk registry rather than silently
dropped. They include structures for which the received structural-factor
workbook has no exact matching row. The three x-only rows are likewise retained
as explicit missing-performance cases.

## 3. Grouped four-method technical pilots

Feature selection was performed inside each outer training fold. Random-row
splitting, automatic winner promotion and inverse-design claims were not used.

### B/C/L

- Rows: `137`
- Outer split: leave one of `B / C / L` out
- Eligible features: `38`
- Targets / methods: `16 / 4`
- OOF predictions: `8,768`
- Independent QA-v2: `10/10 PASS_WITH_WARNINGS`
- Promotion: `none`

Strongest screening signals include `AS` (pooled R2 `0.3873`), `APS` and
`Max. Plateau stress` (`0.3834`), and `Yield strength` (`0.3796`). These are
screening values only. `LCC` is numerically unstable for all four methods, with
extreme negative R2, and is excluded from interpretation until its source and
scale are diagnosed.

### Voronoi

- Rows: `30`
- Outer split: leave one of `VF30 / VF45 / VF60` out
- Eligible features: `41`
- Targets / methods: `16 / 4`
- OOF predictions: `1,920`
- Independent QA-v2: `10/10 PASS_WITH_WARNINGS`
- Promotion: `none`

The strongest bounded screening results are `Com. strain` (pooled R2 `0.7304`,
minimum held-VF R2 `0.6660`), `SEA` (`0.6131`, minimum `0.5093`) and
`Total energy` (`0.5922`, minimum `0.4309`). `Yield strength` and `Modulus`
show high pooled values but poor held-VF behavior and therefore remain warning
cases rather than candidates for promotion. The cohort has only 30 rows.

## 4. Claim boundary

Confirmed:

- all eleven received sources were preserved with matching hashes;
- explicit model-ID intake produced 167 exact x-y joins;
- both grouped pilots completed under KMK312 and their QA-v2 checks pass;
- all predictions, fold registries, feature-selection traces, metrics, warnings,
  figures and manifests are retained.

Likely:

- some compression targets contain useful structure-factor signal under the
  current grouped contracts.

Unresolved:

- target units and several target semantics;
- B/C/L y-only rows lacking structural factors;
- the B/C/L `LCC` numerical failure;
- convergence/constant-input warnings;
- the stability of the apparent signal under a target-specific nested review;
- whether the 30-row Voronoi cohort is sufficient for generalization.

Rejected:

- automatic promotion of a feature, method or target;
- production prediction, physical optimum or inverse-design success;
- treating pooled R2 alone as held-family or held-VF generalization.

## 5. Evidence paths

- Raw source manifest: `data/raw/doctor_compression_data_20260802/SOURCE_MANIFEST.csv`
- Intake: `data/processed/COMP-FACTORY-003/COMP-FACTORY-003-BCL-VORONOI-20260802-001/`
- B/C/L pilot: `data/processed/COMP-FACTORY-004/COMP-FACTORY-004-BCL-FS4-20260802-001/`
- Voronoi pilot: `data/processed/COMP-FACTORY-004/COMP-FACTORY-004-VORONOI-FS4-20260802-001/`
- Factory status: `factories/COMP-FACTORY-001/FACTORY_STATUS.json`

## 6. Next gate

Preregister a target-specific nested stability review. Start with one target at
a time, preserve grouped holdouts, examine fold-to-fold feature stability and
diagnose warnings before any promotion. The pooled winner must not be adopted
automatically.

