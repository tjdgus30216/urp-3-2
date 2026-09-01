"""Read-only static inspection of immutable professor/TA Training notebooks."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from .models import NotebookAudit, TrainingPolicyError, TrainingSourceSpec


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _literal_assignments(tree: ast.AST) -> dict[str, object]:
    values: dict[str, object] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            targets = node.targets
            value_node = node.value
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
            value_node = node.value
        else:
            continue
        try:
            value = ast.literal_eval(value_node)
        except (ValueError, TypeError):
            continue
        for target in targets:
            if isinstance(target, ast.Name):
                values[target.id] = value
    return values


def audit_notebook(root: Path, spec: TrainingSourceSpec) -> NotebookAudit:
    path = (root / spec.relative_path).resolve()
    if not path.is_file():
        raise TrainingPolicyError(f"Training source missing: {spec.relative_path}")
    observed_hash = sha256_file(path)
    notebook = json.loads(path.read_text(encoding="utf-8"))
    cells = list(notebook.get("cells", []))
    code_cells = [cell for cell in cells if cell.get("cell_type") == "code"]
    markdown_cells = [cell for cell in cells if cell.get("cell_type") == "markdown"]
    source = "\n".join("".join(cell.get("source", [])) for cell in code_cells)
    sanitized = "\n".join(
        ("pass  # notebook magic omitted from static AST" if line.lstrip().startswith(("%", "!")) else line)
        for line in source.splitlines()
    )
    try:
        tree = ast.parse(sanitized, filename=spec.relative_path)
    except SyntaxError as exc:
        raise TrainingPolicyError(f"Training source AST failed: {spec.alias_id}: {exc}") from exc
    functions = sorted(
        node.name for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    )
    classes = sorted(node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    assignments = _literal_assignments(tree)
    output_columns = tuple(str(value) for value in assignments.get("OUTPUT_COLUMNS", ()))
    function_hash = hashlib.sha256("\n".join(functions).encode("utf-8")).hexdigest()
    structure_ok = (
        len(cells) == spec.expected_cells
        and len(code_cells) == spec.expected_code_cells
        and len(markdown_cells) == spec.expected_markdown_cells
        and len(functions) == spec.expected_functions
        and len(classes) == spec.expected_classes
        and output_columns == spec.output_columns
    )
    return NotebookAudit(
        alias_id=spec.alias_id,
        relative_path=spec.relative_path,
        expected_sha256=spec.sha256,
        observed_sha256=observed_hash,
        size_bytes=path.stat().st_size,
        total_cells=len(cells),
        code_cells=len(code_cells),
        markdown_cells=len(markdown_cells),
        function_count=len(functions),
        class_count=len(classes),
        import_roots=tuple(sorted(imports)),
        function_names_sha256=function_hash,
        output_columns=output_columns,
        source_identity_status="confirmed" if observed_hash == spec.sha256 else "rejected_hash_mismatch",
        structure_status="confirmed" if structure_ok else "rejected_structure_drift",
    )


def audit_sources(root: Path, specs: Iterable[TrainingSourceSpec]) -> tuple[NotebookAudit, ...]:
    rows = tuple(audit_notebook(root, spec) for spec in specs)
    if any(row.source_identity_status != "confirmed" or row.structure_status != "confirmed" for row in rows):
        raise TrainingPolicyError("one or more immutable Training sources failed identity/structure audit")
    return rows


def definition_inventory(root: Path, spec: TrainingSourceSpec) -> tuple[dict[str, Any], ...]:
    """Return function/class names and source locations without executing code."""

    path = (root / spec.relative_path).resolve()
    notebook = json.loads(path.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    for cell_index, cell in enumerate(notebook.get("cells", [])):
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        sanitized = "\n".join(
            ("pass  # notebook magic omitted from static AST" if line.lstrip().startswith(("%", "!")) else line)
            for line in source.splitlines()
        )
        tree = ast.parse(sanitized, filename=f"{spec.relative_path}::cell-{cell_index}")
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                rows.append(
                    {
                        "alias_id": spec.alias_id,
                        "method_family": spec.method_family,
                        "cell_index": cell_index,
                        "definition_type": "class" if isinstance(node, ast.ClassDef) else "function",
                        "definition_name": node.name,
                        "cell_line_start": node.lineno,
                        "cell_line_end": getattr(node, "end_lineno", node.lineno),
                        "execution_status": "not_executed_static_ast",
                    }
                )
    return tuple(rows)
