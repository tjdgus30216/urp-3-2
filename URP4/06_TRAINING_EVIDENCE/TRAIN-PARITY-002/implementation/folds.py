from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

from .contracts import INNER_SPLITS, INNER_TEST_SIZE, OUTER_REPEATS, OUTER_SEED_BASE, OUTER_TEST_SIZE
from .hashing import sha256_file


FOLD_COLUMNS = (
    "manifest_version", "target_id", "target_excel_col", "scope", "outer_repeat", "outer_seed",
    "inner_split", "inner_seed", "row_id", "original_excel_row", "group_id", "role", "order_in_role",
)


def build_fold_manifest(dataset, path: Path):
    frames = []
    y = dataset["y"]
    for policy, target_name in zip(dataset["target_policy"], y.columns):
        mask = y[target_name].notna().to_numpy()
        positions = np.flatnonzero(mask)
        groups = dataset["group_id"].to_numpy()[positions]
        rows = np.asarray(dataset["source_rows"])[positions]
        row_ids = np.asarray([f"EXCEL-ROW-{row:04d}" for row in rows])
        for repeat in range(OUTER_REPEATS):
            seed = OUTER_SEED_BASE + repeat
            splitter = GroupShuffleSplit(n_splits=1, test_size=OUTER_TEST_SIZE, random_state=seed)
            train_local, test_local = next(splitter.split(np.arange(len(positions)), groups=groups))
            for role, local_indices in (("train", train_local), ("test", test_local)):
                frames.append(pd.DataFrame({
                    "manifest_version": "TRAIN2NF-FOLDS-v0.1",
                    "target_id": policy["target_id"],
                    "target_excel_col": policy["excel_col"],
                    "scope": "outer",
                    "outer_repeat": repeat,
                    "outer_seed": seed,
                    "inner_split": -1,
                    "inner_seed": -1,
                    "row_id": row_ids[local_indices],
                    "original_excel_row": rows[local_indices],
                    "group_id": groups[local_indices],
                    "role": role,
                    "order_in_role": np.arange(len(local_indices)),
                }))
            outer_train_groups = groups[train_local]
            outer_train_rows = rows[train_local]
            outer_train_ids = row_ids[train_local]
            inner = GroupShuffleSplit(n_splits=INNER_SPLITS, test_size=INNER_TEST_SIZE, random_state=seed)
            for inner_id, (inner_train, inner_valid) in enumerate(inner.split(np.arange(len(train_local)), groups=outer_train_groups)):
                for role, local_indices in (("train", inner_train), ("valid", inner_valid)):
                    frames.append(pd.DataFrame({
                        "manifest_version": "TRAIN2NF-FOLDS-v0.1",
                        "target_id": policy["target_id"],
                        "target_excel_col": policy["excel_col"],
                        "scope": "inner",
                        "outer_repeat": repeat,
                        "outer_seed": seed,
                        "inner_split": inner_id,
                        "inner_seed": seed,
                        "row_id": outer_train_ids[local_indices],
                        "original_excel_row": outer_train_rows[local_indices],
                        "group_id": outer_train_groups[local_indices],
                        "role": role,
                        "order_in_role": np.arange(len(local_indices)),
                    }))
    manifest = pd.concat(frames, ignore_index=True)[list(FOLD_COLUMNS)]
    path.parent.mkdir(parents=True, exist_ok=True)
    manifest.to_csv(path, index=False, encoding="utf-8-sig")
    digest = sha256_file(path)
    meta = {
        "execution_status": "no_fit_no_prediction",
        "manifest_version": "TRAIN2NF-FOLDS-v0.1",
        "path": path.name,
        "sha256": digest,
        "rows": len(manifest),
        "targets": int(manifest["target_id"].nunique()),
        "outer_repeats": OUTER_REPEATS,
        "inner_splits_per_outer": INNER_SPLITS,
        "membership_level": "row_and_group",
    }
    path.with_suffix(".meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return manifest, meta


def consume_fold_manifest(path: Path, expected_hash: str):
    if not path.exists():
        raise FileNotFoundError("FOLD_MANIFEST_MISSING")
    actual = sha256_file(path)
    if actual != expected_hash:
        raise ValueError(f"FOLD_MANIFEST_HASH_MISMATCH: expected={expected_hash} actual={actual}")
    frame = pd.read_csv(path)
    if list(frame.columns) != list(FOLD_COLUMNS):
        raise ValueError("FOLD_MANIFEST_SCHEMA_MISMATCH")
    return frame
