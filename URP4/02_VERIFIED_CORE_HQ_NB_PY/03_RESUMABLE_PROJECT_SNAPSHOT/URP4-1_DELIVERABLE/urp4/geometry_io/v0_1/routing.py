"""Fail-closed switch between generated rows and imported STL rows."""

from __future__ import annotations

import pandas as pd

from .models import GeometryImportError, STLImportConfig
from .stl_import import build_stl_import_table


def route_geometry_inputs(
    *,
    import_enabled: bool,
    import_config: STLImportConfig | None,
    generated_table: pd.DataFrame | None,
) -> tuple[pd.DataFrame, str]:
    """Return exactly one descriptor input population.

    ``False`` preserves the generated candidate population. ``True`` bypasses
    generation and builds a table from external STL files.  The function never
    concatenates both populations implicitly.
    """

    if bool(import_enabled):
        if import_config is None:
            raise GeometryImportError("STL import is enabled but import_config is missing")
        imported = build_stl_import_table(import_config)
        if imported.empty:
            raise GeometryImportError("STL import is enabled but the imported table is empty")
        return imported, "import_stl"
    if generated_table is None or generated_table.empty:
        raise GeometryImportError("generation route selected but generated candidate table is empty")
    generated = generated_table.copy()
    if "source_mode" not in generated.columns:
        generated["source_mode"] = "generated"
    if "import_enabled" not in generated.columns:
        generated["import_enabled"] = False
    return generated, "generated"

