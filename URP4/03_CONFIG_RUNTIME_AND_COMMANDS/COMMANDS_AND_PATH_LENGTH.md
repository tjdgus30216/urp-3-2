# Runtime and read-only commands

- Canonical Python: `C:\Users\chuck\Documents\Codex\2026-06-22\a2f23dee1d9a824b840a0175ca9a1f4b-https-app-notion-com-p\tools\envs\KMK312\python.exe`
- Python: 3.12.12 packaged by Anaconda
- Environment itself is not bundled.

## Inspect only

```powershell
& "C:\Users\chuck\Documents\Codex\2026-06-22\a2f23dee1d9a824b840a0175ca9a1f4b-https-app-notion-com-p\tools\envs\KMK312\python.exe" -m json.tool .\01_PROJECT_MAP_AND_LEDGER\PROJECT_SCHEMA.json > $null
& "C:\Users\chuck\Documents\Codex\2026-06-22\a2f23dee1d9a824b840a0175ca9a1f4b-https-app-notion-com-p\tools\envs\KMK312\python.exe" .\10_MANIFEST_SHA256_AND_QA\verify_package_read_only.py .
```

Do not run Training fit/predict, C1, F1, all58, or inverse-design calculations from this submission package. On Windows, extract near a short path such as `C:\URP4H\` to avoid MAX_PATH issues.
