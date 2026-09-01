from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

from .hashing import verify_file_hash


def inventory_source_functions(notebook_path: Path, expected_hash: str):
    verify_file_hash(notebook_path, expected_hash, "SOURCE")
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    rows = []
    for cell_index, cell in enumerate(notebook["cells"]):
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        tree = ast.parse(source)
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            segment = ast.get_source_segment(source, node) or ast.unparse(node)
            rows.append({
                "cell_index": cell_index,
                "symbol": node.name,
                "symbol_type": type(node).__name__,
                "source_sha256": hashlib.sha256(segment.encode("utf-8")).hexdigest(),
                "lineno": node.lineno,
                "end_lineno": node.end_lineno,
                "execution_status": "source_ast_frozen_not_executed",
            })
    return rows


def find_unordered_traversal(notebook_path: Path):
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    findings = []
    for cell_index, cell in enumerate(notebook["cells"]):
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        for line_number, line in enumerate(source.splitlines(), start=1):
            if "set(" in line or "next(iter(" in line or ".items()" in line:
                findings.append({"cell_index": cell_index, "line_number": line_number, "source": line.strip()})
    return findings
