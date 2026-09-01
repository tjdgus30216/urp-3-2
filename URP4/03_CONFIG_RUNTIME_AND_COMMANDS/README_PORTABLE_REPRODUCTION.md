# Portable reproduction contract — package v1.3-r2

## Purpose

This package does not bundle the multi-GB KMK312 environment. It supplies two complete package locks plus a path-rebinding contract so another Windows laboratory PC can recreate or bind a compatible environment without running research calculations.

## Environment recreation

1. Install Miniconda/Anaconda on the target Windows PC.
2. From this directory, create a fresh environment with `conda create --prefix <TARGET> --file KMK312_CONDA_EXPLICIT_LOCK.txt`.
3. Set `URP4_KMK312_PYTHON=<TARGET>\python.exe`.
4. Verify the lock receipts in `ENVIRONMENT_LOCK_SHA256.json`.
5. Run `VERIFY_READ_ONLY.cmd` or `VERIFY_READ_ONLY.ps1`. The verifier parses package artifacts and hashes only; it must not execute descriptors, Training or model fitting.

`KMK312_PIP_FREEZE.txt` is a cross-check, not the primary solver contract. `KMK312_CONDA_META_LOCK.json` preserves name/version/build/source/checksum metadata for audit.

## Geometry placement

Download the external geometry delivery asset adjacent to this handoff, verify its SHA/receipt, and extract it so that `<GEOMETRY_ROOT>/stl` and `<GEOMETRY_ROOT>/stp` exist. Set `URP4_GEOMETRY_ROOT=<GEOMETRY_ROOT>`. The contract is exactly 67 immutable files: 34 STL + 33 STP, total 1,411,469,295 bytes.

## Absolute paths

Chuck-specific paths in historical evidence are provenance, not portable execution paths. New launchers bind by package root and environment variables. Do not edit original evidence simply to replace historical paths.

## Scope boundary

The portable smoke is read-only. It does not authorize C1/F1/all58, Training fit/predict, descriptor extraction, feature selection or inverse design.
