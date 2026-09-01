from __future__ import annotations

import ast
import copy
import inspect
import json
from pathlib import Path
from types import FunctionType
from typing import Any

from .contracts import SOURCE_SHA256
from .hashing import require_hash, sha256_text


DEFINITION_CELLS = (2, 4, 5, 6, 7)
IMPORT_CELLS = (1, 7)
LITERAL_CONFIG_CELL = 1


class SourceExactRuntime:
    """Compile protected source definitions without executing notebook workflow cells.

    Function/class AST nodes are compiled byte-for-byte from the hash-bound
    notebook.  No function is called by construction.  Fit-dependent calls are
    reachable only through the separate branch adapter permit gate.
    """

    def __init__(self, notebook_path: Path):
        require_hash(notebook_path, SOURCE_SHA256, "SOURCE")
        self.notebook_path = notebook_path
        self.notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
        self.namespace: dict[str, Any] = {"__name__": "train2nf_source_exact_runtime"}
        self.symbol_lineage: list[dict[str, Any]] = []
        self.branch_lineage: dict[str, dict[str, Any]] = {}

    def _cell_source(self, index: int) -> str:
        return "".join(self.notebook["cells"][index].get("source", []))

    def compile(self) -> "SourceExactRuntime":
        import_nodes = []
        for index in IMPORT_CELLS:
            tree = ast.parse(self._cell_source(index))
            import_nodes.extend(copy.deepcopy(node) for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom)))
        import_module = ast.fix_missing_locations(ast.Module(body=import_nodes, type_ignores=[]))
        exec(compile(import_module, str(self.notebook_path), "exec"), self.namespace)

        config_tree = ast.parse(self._cell_source(LITERAL_CONFIG_CELL))
        for node in config_tree.body:
            if not isinstance(node, ast.Assign) or len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
                continue
            try:
                value = ast.literal_eval(node.value)
            except Exception:
                continue
            self.namespace[node.targets[0].id] = value
        self.namespace["FAMILY_MT_DATA"] = {}

        definition_nodes = []
        for cell_index in DEFINITION_CELLS:
            source = self._cell_source(cell_index)
            tree = ast.parse(source)
            for node in tree.body:
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    continue
                segment = ast.get_source_segment(source, node) or ast.unparse(node)
                self.symbol_lineage.append({
                    "cell_index": cell_index,
                    "source_symbol": node.name,
                    "source_lineno": node.lineno,
                    "source_end_lineno": node.end_lineno,
                    "source_ast_hash": sha256_text(ast.dump(node, include_attributes=False)),
                    "source_text_hash": sha256_text(segment),
                })
                definition_nodes.append(copy.deepcopy(node))
        definition_module = ast.fix_missing_locations(ast.Module(body=definition_nodes, type_ignores=[]))
        exec(compile(definition_module, str(self.notebook_path), "exec"), self.namespace)
        self._inventory_branches()
        return self

    def _inventory_branches(self) -> None:
        source = self._cell_source(7)
        tree = ast.parse(source)
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "evaluate_method_train_test")
        mapping = {
            "baseline_stability": "baseline_stability",
            "stability_lasso_ridge": "stability_lasso_ridge",
            "spca_ridge": "spca_ridge",
            "spca_huber": "spca_huber",
            "spca_pls": "spca_pls",
            "block_pca_ridge": "block_pca_ridge",
            "bagged_subspace_ridge": "bagged_subspace_ridge",
            "multitask_screen_ridge": "multitask_screen_ridge",
            "multitask_screen_pls": "multitask_screen_pls",
            "minimal_class_average": "minimal_class_average",
        }
        for node in ast.walk(function):
            if not isinstance(node, ast.If):
                continue
            test_text = ast.get_source_segment(source, node.test) or ast.unparse(node.test)
            body_text = ast.get_source_segment(source, node) or ast.unparse(node)
            for branch, token in mapping.items():
                if repr(token) in test_text or f'"{token}"' in test_text:
                    self.branch_lineage[branch] = {
                        "source_cell_index": 7,
                        "source_function": "evaluate_method_train_test",
                        "condition": test_text,
                        "branch_ast_hash": sha256_text(ast.dump(node, include_attributes=False)),
                        "branch_text_hash": sha256_text(body_text),
                        "source_lineno": node.lineno,
                        "source_end_lineno": node.end_lineno,
                    }

    def function(self, name: str) -> FunctionType:
        value = self.namespace.get(name)
        if not callable(value):
            raise KeyError(f"SOURCE_SYMBOL_NOT_CALLABLE: {name}")
        return value

    def signature(self, name: str) -> str:
        return str(inspect.signature(self.function(name)))

    def bind_dynamic_state(self, **state: Any) -> None:
        allowed = {"DATA_BY_OUTPUT", "FAMILY_MT_DATA"}
        unknown = set(state) - allowed
        if unknown:
            raise KeyError(f"UNKNOWN_DYNAMIC_STATE: {sorted(unknown)}")
        self.namespace.update(state)
