"""Qualified imported-STL oriented-winding slicer.

This version is intentionally separate from generated-STL routing.  It is
screening-qualified on the L28 VF30/VF45/VF60 triad and is not an exact STEP
or general imported-STL replacement.
"""

from .imported_winding import (
    active_triangle_subsets_z,
    ImportedSTLWindingConfig,
    imported_stl_mask_stream,
    load_imported_stl_triangles,
    mask_packedbits_sha256,
    oriented_section_z,
    winding_raster,
)

__all__ = [
    "ImportedSTLWindingConfig",
    "active_triangle_subsets_z",
    "imported_stl_mask_stream",
    "load_imported_stl_triangles",
    "mask_packedbits_sha256",
    "oriented_section_z",
    "winding_raster",
]
