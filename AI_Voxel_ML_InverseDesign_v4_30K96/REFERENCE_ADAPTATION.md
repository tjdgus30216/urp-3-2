# Reference adaptation summary

## Com_Training_Visualization_v22.ipynb
Adapted concepts: multi-workbook curve ingestion, common strain grid, event-aware densification/property extraction, design-group-safe validation, curve + scalar-property surrogate separation, uncertainty-aware validation, persistent stage outputs.

## Com_Optimization_v19.ipynb
Adapted concepts: target-weighted surrogate optimization, uncertainty/OOD penalties, diverse candidate generation, optimization-to-manufacturing export and experimental validation loop.

## Deliberately not copied as the primary inverse geometry engine
The v19 geometry mutation operates on line/strut `LatticeGraph` objects. The Voxel workflow instead optimizes continuous generator parameters and latent spectral/Fourier morphology controls, then regenerates the true Voxel/STL/DLP geometry for validation.
