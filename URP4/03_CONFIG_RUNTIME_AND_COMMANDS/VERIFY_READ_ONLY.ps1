$ErrorActionPreference = 'Stop'
$PackageRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Python = if ($env:URP4_KMK312_PYTHON) { $env:URP4_KMK312_PYTHON } else { 'python' }
& $Python (Join-Path $PackageRoot '10_MANIFEST_SHA256_AND_QA\verify_package_read_only.py') $PackageRoot
exit $LASTEXITCODE
