from __future__ import annotations

from .contracts import METHOD_BRANCHES, STAGE_SPECS


def stage_graph_rows():
    return [
        {
            "stage_id": stage_id,
            "stage": stage,
            "source_cell_index": cell,
            "source_symbol": symbol,
            "adapter_handler": handler,
            "coverage_status": status,
            "execution_status": "no_fit_no_prediction",
        }
        for stage_id, stage, cell, symbol, handler, status in STAGE_SPECS
    ]


def method_branch_rows():
    return [
        {
            "branch_id": f"TRAIN2NF-BRANCH-{index:02d}",
            "source_method_name": name,
            "branch_spec_implemented": True,
            "numerical_execution_adapter": False,
            "status": "source_ast_bound_no_fit_execution",
        }
        for index, name in enumerate(METHOD_BRANCHES, start=1)
    ]
