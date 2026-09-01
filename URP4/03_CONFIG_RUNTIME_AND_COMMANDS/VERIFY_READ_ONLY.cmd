@echo off
setlocal
set "PKG=%~dp0.."
if defined URP4_KMK312_PYTHON (
  set "PY=%URP4_KMK312_PYTHON%"
) else (
  set "PY=python"
)
"%PY%" "%PKG%\10_MANIFEST_SHA256_AND_QA\verify_package_read_only.py" "%PKG%"
exit /b %ERRORLEVEL%
