"""Generated-STL analysis-copy normalization (HQ-GEOM-001).

This package is deliberately separate from the protected HQ v0.1 controller.
It creates immutable, hash-addressed *analysis derivatives*; it never repairs
or overwrites the generated source STL.
"""

from .generated_normalization import GeneratedNormalizationConfig, normalize_generated_stl

__all__ = ["GeneratedNormalizationConfig", "normalize_generated_stl"]
