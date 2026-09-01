# COMP-FACTORY-004 BCL FS4 technical pilot

- Run ID: `COMP-FACTORY-004-BCL-FS4-20260802-001`
- Status: `PASS`
- Runtime: `C:\Users\chuck\Documents\Codex\2026-06-22\a2f23dee1d9a824b840a0175ca9a1f4b-https-app-notion-com-p\tools\envs\KMK312\python.exe` / Python `3.12.12`
- Rows: `137`
- Outer split: `leave-one-B/C/L-family-out`
- Candidate features after provenance/Target-VF/zero-variance exclusions: `38`
- Targets: `16`
- Methods: `4`
- OOF predictions: `8768`
- Runtime seconds: `8.304`

## Highest screening results

| cohort   | target_id                 | target_name_raw     | best_method_by_pooled_r2   |   best_pooled_r2 |   best_pooled_mae |   best_pooled_rmse |   best_delta_rmse_vs_null |   median_outer_fold_r2 |   min_outer_fold_r2 | features_selected_in_all_outer_folds             | promotion_status   | interpretation       |
|:---------|:--------------------------|:--------------------|:---------------------------|-----------------:|------------------:|-------------------:|--------------------------:|-----------------------:|--------------------:|:-------------------------------------------------|:-------------------|:---------------------|
| bcl      | COMP-Y-AS                 | AS                  | FS4-METHOD-02              |         0.387309 |         5.32773   |         6.8465     |               -2.00552    |               0.511428 |           0.293824  | SFX004|SFX014|SFX019|SFX021|SFX028|SFX034|SFX038 | not_promoted       | technical pilot only |
| bcl      | COMP-Y-APS                | APS                 | FS4-METHOD-04              |         0.383361 |         6.2       |         7.8218     |               -2.20211    |               0.466221 |           0.288609  | SFX004|SFX014|SFX019|SFX021|SFX028|SFX034|SFX038 | not_promoted       | technical pilot only |
| bcl      | COMP-Y-MAX-PLATEAU-STRESS | Max. Plateau stress | FS4-METHOD-04              |         0.383361 |         6.2       |         7.8218     |               -2.20211    |               0.466221 |           0.288609  | SFX004|SFX014|SFX019|SFX021|SFX028|SFX034|SFX038 | not_promoted       | technical pilot only |
| bcl      | COMP-Y-YIELD-STRENGTH     | Yield strength      | FS4-METHOD-04              |         0.379569 |         4.61429   |         6.27902    |               -1.69305    |               0.415952 |           0.342761  | SFX004|SFX019|SFX021|SFX034|SFX038               | not_promoted       | technical pilot only |
| bcl      | COMP-Y-TOTAL-ENERGY       | Total energy        | FS4-METHOD-03              |         0.303993 |         1.90944   |         2.45977    |               -0.58441    |               0.247189 |          -0.0714178 | SFX004|SFX014|SFX028|SFX037                      | not_promoted       | technical pilot only |
| bcl      | COMP-Y-MODULUS            | Modulus             | FS4-METHOD-04              |         0.195282 |       108.355     |       135.189      |              -15.6983     |               0.21018  |           0.0178484 | SFX004|SFX019|SFX021|SFX034|SFX038               | not_promoted       | technical pilot only |
| bcl      | COMP-Y-YIELD-STRAIN       | Yield strain        | FS4-METHOD-04              |         0.186964 |         0.0056351 |         0.00819312 |               -0.00093107 |               0.18869  |          -0.0701039 | SFX004|SFX020|SFX022|SFX034|SFX037|SFX038        | not_promoted       | technical pilot only |
| bcl      | COMP-Y-COMP-STRAIN        | Com. strain         | FS4-METHOD-03              |         0.1716   |         0.241238  |         0.296258   |               -0.0344648  |               0.226172 |           0.0807759 | SFX008|SFX038                                    | not_promoted       | technical pilot only |

## Claim boundary

This is a grouped technical screening pilot. Feature selection is performed inside each outer training fold, and no feature, target, or method is promoted. The result is not a production model, physical optimum, or inverse-design validation.
