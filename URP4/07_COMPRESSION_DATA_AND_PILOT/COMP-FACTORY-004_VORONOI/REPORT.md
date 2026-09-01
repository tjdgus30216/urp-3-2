# COMP-FACTORY-004 VORONOI FS4 technical pilot

- Run ID: `COMP-FACTORY-004-VORONOI-FS4-20260802-001`
- Status: `PASS`
- Runtime: `C:\Users\chuck\Documents\Codex\2026-06-22\a2f23dee1d9a824b840a0175ca9a1f4b-https-app-notion-com-p\tools\envs\KMK312\python.exe` / Python `3.12.12`
- Rows: `30`
- Outer split: `leave-one-VF-group-out`
- Candidate features after provenance/Target-VF/zero-variance exclusions: `41`
- Targets: `16`
- Methods: `4`
- OOF predictions: `1920`
- Runtime seconds: `8.312`

## Highest screening results

| cohort   | target_id              | target_name_raw   | best_method_by_pooled_r2   |   best_pooled_r2 |   best_pooled_mae |   best_pooled_rmse |   best_delta_rmse_vs_null |   median_outer_fold_r2 |   min_outer_fold_r2 | features_selected_in_all_outer_folds      | promotion_status   | interpretation       |
|:---------|:-----------------------|:------------------|:---------------------------|-----------------:|------------------:|-------------------:|--------------------------:|-----------------------:|--------------------:|:------------------------------------------|:-------------------|:---------------------|
| voronoi  | COMP-Y-COMP-STRAIN     | Com. strain       | FS4-METHOD-02              |         0.730353 |          0.143018 |           0.175941 |                -0.164432  |              0.758672  |           0.666006  | SFX011|SFX015|SFX016                      | not_promoted       | technical pilot only |
| voronoi  | COMP-Y-DENSIF-STRENGTH | Densif. strength  | FS4-METHOD-01              |         0.677358 |          0.67947  |           0.789904 |                -0.601576  |              0.7979    |           0.071499  | SFX008|SFX012|SFX015|SFX016               | not_promoted       | technical pilot only |
| voronoi  | COMP-Y-YIELD-STRENGTH  | Yield strength    | FS4-METHOD-04              |         0.667935 |          1.59514  |           1.97811  |                -2.7773    |              0.0644437 |          -2.2781    | SFX020|SFX022                             | not_promoted       | technical pilot only |
| voronoi  | COMP-Y-SEA             | SEA               | FS4-METHOD-04              |         0.613074 |          0.811378 |           1.04018  |                -0.65488   |              0.649533  |           0.509324  | SFX008|SFX012|SFX016|SFX018|SFX030        | not_promoted       | technical pilot only |
| voronoi  | COMP-Y-TOTAL-ENERGY    | Total energy      | FS4-METHOD-04              |         0.592182 |          0.657414 |           0.866375 |                -0.644744  |              0.485053  |           0.430897  | SFX008|SFX012|SFX016|SFX020|SFX022|SFX030 | not_promoted       | technical pilot only |
| voronoi  | COMP-Y-MODULUS         | Modulus           | FS4-METHOD-02              |         0.455345 |         33.556    |          40.5766   |               -33.3158    |             -0.759573  |          -0.97548   | SFX040|SFX041                             | not_promoted       | technical pilot only |
| voronoi  | COMP-Y-DENSIFI-STRAIN  | Densifi. strain   | FS4-METHOD-03              |         0.40078  |          0.115501 |           0.139533 |                -0.0446919 |              0.402645  |          -0.0179199 | SFX008|SFX012|SFX016|SFX030               | not_promoted       | technical pilot only |
| voronoi  | COMP-Y-EAS             | EAS               | FS4-METHOD-03              |         0.345389 |          0.126016 |           0.152876 |                -0.0404755 |              0.323549  |          -0.158611  | SFX008|SFX012|SFX016                      | not_promoted       | technical pilot only |

## Claim boundary

This is a grouped technical screening pilot. Feature selection is performed inside each outer training fold, and no feature, target, or method is promoted. The result is not a production model, physical optimum, or inverse-design validation.
