# Notion reference models — raw immutable staging

Scope fixed on 2026-07-01 from Chuck's professor discussion:

- `stp/`: only `.stp` attachments from the Notion STP page.
- `stl/`: every individual `.stl` attachment from the Notion printing page.
- `.inp` and archive attachments are intentionally excluded.
- Do not rename or edit files in this directory. Model-ID normalization and conversion belong in `data/interim/`.
- `R09_reference_model_manifest.csv` and `.json` record source page, Notion block ID, file hash, size, and download status.

These files are reference inputs for the next gate:

`external STP/STL -> current descriptor extraction -> Excel descriptor comparison`

