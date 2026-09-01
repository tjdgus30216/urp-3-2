# COMP-FACTORY-003 B/C/L + Voronoi intake

- Run ID: `COMP-FACTORY-003-BCL-VORONOI-20260802-001`
- Status: `PASS`
- Runtime: `C:\Users\chuck\Documents\Codex\2026-06-22\a2f23dee1d9a824b840a0175ca9a1f4b-https-app-notion-com-p\tools\envs\KMK312\python.exe` / Python `3.12.12`
- B/C/L performance rows: `198`
- Voronoi performance rows: `30`
- Relevant structural rows: `170`
- Exact x-y joins: `167` (`B/C/L=137`, `Voronoi=30`)
- Crosswalk statuses: `{"eligible_exact_model_label_join": 167, "x_only_missing_performance": 3, "y_only_missing_structural_factors": 61}`

## Source decision

`New_VF30/45/60.xlsx` is the primary B/C/L performance source because it contains explicit B1–T17 labels and populated cached formula outputs. `Compression_Worked_VF30/45/60.xlsx` and the small summary workbooks are retained as reference-only lineage assets; their generic trailing rows are not used as the current B/C/L model crosswalk.

`Voronoi_Summary.xlsx / Raw data` provides 30 explicit identifiers and is used as the Voronoi performance source. The worked workbook is retained for cross-check provenance.

## Claim boundary

This run performs source audit, explicit ID normalization, x-y joining, and QA only. It does not promote features, select a final model, claim production prediction, or claim inverse-design success.
