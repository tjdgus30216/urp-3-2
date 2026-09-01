"""Geometry-to-primitive-table pipeline with artifact and streaming modes."""

from __future__ import annotations

import hashlib
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd

from .component import component_features_for_pair
from .config import ExtractionConfig, RUN139_EXTRACTION_CONFIG
from .geometry import geometry_bounds, load_binary_stl_vertices
from .models import PrimitiveTables
from .pixel import connected_components, read_mask, read_overlay_counts, save_mask, save_overlay
from .slicing import rasterize_segments_scanline, vectorized_segments


ExecutionMode = Literal["ARTIFACT-FULL", "STREAMING"]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


@dataclass(frozen=True)
class ExtractionOutput:
    tables: PrimitiveTables
    slice_components: pd.DataFrame
    qa: dict
    output_dir: Path


class Run139ExtractionPipeline:
    """Execute the frozen geometry/slicing/pixel/component backend.

    ``ARTIFACT-FULL`` retains every PNG in ``output_dir/images``.
    ``STREAMING`` still performs the required PNG save/readback, then deletes
    each PNG immediately after its primitive row and hash have been captured.
    """

    def __init__(self, config: ExtractionConfig = RUN139_EXTRACTION_CONFIG):
        config.validate()
        self.config = config

    def extract(
        self,
        *,
        model_id: str,
        geometry_path: str | Path,
        output_dir: str | Path,
        mode: ExecutionMode,
        expected_geometry_sha256: str | None = None,
        overwrite: bool = False,
    ) -> ExtractionOutput:
        if mode not in ("ARTIFACT-FULL", "STREAMING"):
            raise ValueError(f"unsupported execution mode: {mode}")
        target = Path(output_dir)
        if target.exists():
            if not overwrite:
                raise FileExistsError(f"output directory already exists: {target}")
            shutil.rmtree(target)
        image_root = target / "images"
        mask_root = image_root / "mask"
        overlay_root = image_root / "overlay"
        table_root = target / "tables"
        for path in (mask_root, overlay_root, table_root):
            path.mkdir(parents=True, exist_ok=True)

        triangles = load_binary_stl_vertices(geometry_path, expected_sha256=expected_geometry_sha256)
        bbox_min, bbox_max = geometry_bounds(triangles)
        cfg = self.config
        z_eval = bbox_min[2] + np.arange(cfg.slice_count, dtype=float) * cfg.slice_spacing_mm
        z_eval[0] += cfg.endpoint_nudge_mm
        z_eval[-1] -= cfg.endpoint_nudge_mm
        z_min = triangles[:, :, 2].min(axis=1)
        z_max = triangles[:, :, 2].max(axis=1)
        starts = np.searchsorted(z_eval, z_min - 1e-9, side="left")
        ends = np.searchsorted(z_eval, z_max + 1e-9, side="right")
        valid_triangles = np.flatnonzero(starts < ends)
        start_order = valid_triangles[np.argsort(starts[valid_triangles], kind="stable")]
        end_order = valid_triangles[np.argsort(ends[valid_triangles], kind="stable")]
        start_pointer = 0
        end_pointer = 0
        active: set[int] = set()
        previous_mask: np.ndarray | None = None

        slice_rows: list[dict] = []
        overlay_rows: list[dict] = []
        slice_component_rows: list[dict] = []
        overlay_component_rows: list[dict] = []
        readback_mismatch_sum = 0
        png_created = 0
        png_deleted = 0

        for slice_index, z in enumerate(z_eval):
            while end_pointer < len(end_order) and ends[end_order[end_pointer]] <= slice_index:
                active.discard(int(end_order[end_pointer]))
                end_pointer += 1
            while start_pointer < len(start_order) and starts[start_order[start_pointer]] <= slice_index:
                active.add(int(start_order[start_pointer]))
                start_pointer += 1
            active_indices = np.fromiter(active, dtype=np.int64, count=len(active))
            active_indices.sort()
            segments = vectorized_segments(triangles[active_indices], float(z))
            mask, fill_stats = rasterize_segments_scanline(
                segments,
                bbox_min_xy=(float(bbox_min[0]), float(bbox_min[1])),
                bbox_max_xy=(float(bbox_max[0]), float(bbox_max[1])),
                width=cfg.pixel_width,
                height=cfg.pixel_height,
            )
            mask_path = mask_root / f"m{slice_index:04d}.png"
            save_mask(mask, mask_path, compress_level=cfg.png_compress_level)
            png_created += 1
            mask_hash = _sha256(mask_path)
            readback = read_mask(mask_path)
            readback_mismatch_sum += int(np.count_nonzero(mask ^ readback))
            components, _labels = connected_components(
                readback,
                min_pixels=cfg.min_component_pixels,
                connectivity=cfg.connectivity,
            )
            material_pixels = int(readback.sum())
            slice_rows.append(
                {
                    "model_id": model_id,
                    "slice_index": slice_index,
                    "z_nominal_mm": float(bbox_min[2] + slice_index * cfg.slice_spacing_mm),
                    "z_eval_mm": float(z),
                    "endpoint_adjusted": slice_index in {0, cfg.slice_count - 1},
                    "active_triangle_count": int(len(active_indices)),
                    "segment_count": int(len(segments)),
                    "material_pixel_count": material_pixels,
                    "material_area_mm2": material_pixels * cfg.area_per_pixel_mm2,
                    "component_count": len(components),
                    "odd_scanline_rows": int(fill_stats["odd_scanline_rows"]),
                    "filled_rows": int(fill_stats["filled_rows"]),
                    "max_scanline_intersections": int(fill_stats["max_intersections"]),
                    "mask_sha256": mask_hash,
                }
            )
            for component in components:
                slice_component_rows.append(
                    {
                        "model_id": model_id,
                        "component_scope": "slice_mask",
                        "slice_index_a": slice_index,
                        "slice_index_b": "",
                        **component,
                        "area_mm2": component["pixel_count"] * cfg.area_per_pixel_mm2,
                        "connectivity": cfg.connectivity,
                        "min_component_pixels": cfg.min_component_pixels,
                    }
                )

            if previous_mask is not None:
                pair_index = slice_index - 1
                overlay_path = overlay_root / f"o{pair_index:04d}.png"
                expected_counts = save_overlay(
                    previous_mask,
                    readback,
                    overlay_path,
                    compress_level=cfg.png_compress_level,
                )
                png_created += 1
                overlay_hash = _sha256(overlay_path)
                observed_counts = read_overlay_counts(overlay_path)
                readback_mismatch_sum += sum(
                    abs(expected_counts[key] - observed_counts[key]) for key in expected_counts
                )
                features, layer_counts = component_features_for_pair(
                    previous_mask,
                    readback,
                    pair_index=pair_index,
                    area_per_pixel=cfg.area_per_pixel_mm2,
                    length_per_pixel=cfg.length_per_pixel_mm,
                    layer_height=cfg.slice_spacing_mm,
                    min_pixels=cfg.min_component_pixels,
                    connectivity=cfg.connectivity,
                )
                overlay_rows.append(
                    {
                        "model_id": model_id,
                        "pair_index": pair_index,
                        "slice_index_a": slice_index - 1,
                        "slice_index_b": slice_index,
                        **observed_counts,
                        "red_area_mm2": observed_counts["red_pixel_count"] * cfg.area_per_pixel_mm2,
                        "blue_area_mm2": observed_counts["blue_pixel_count"] * cfg.area_per_pixel_mm2,
                        "purple_area_mm2": observed_counts["purple_pixel_count"] * cfg.area_per_pixel_mm2,
                        "union_area_mm2": observed_counts["union_pixel_count"] * cfg.area_per_pixel_mm2,
                        "overlay_sha256": overlay_hash,
                        "component_count_raw": layer_counts["component_count_raw"],
                        "component_count_kept": layer_counts["component_count_kept"],
                    }
                )
                for feature in features:
                    overlay_component_rows.append(
                        {
                            "model_id": model_id,
                            "component_scope": "overlay_union",
                            "slice_index_a": slice_index - 1,
                            "slice_index_b": slice_index,
                            **feature.to_row(),
                            "connectivity": cfg.connectivity,
                            "min_component_pixels": cfg.min_component_pixels,
                        }
                    )
                if mode == "STREAMING":
                    overlay_path.unlink()
                    png_deleted += 1
            previous_mask = readback
            if mode == "STREAMING":
                mask_path.unlink()
                png_deleted += 1

        slice_frame = pd.DataFrame(slice_rows)
        overlay_frame = pd.DataFrame(overlay_rows)
        slice_component_frame = pd.DataFrame(slice_component_rows)
        overlay_component_frame = pd.DataFrame(overlay_component_rows)
        slice_frame.to_csv(table_root / "slice_pixel_count_table.csv", index=False, encoding="utf-8-sig")
        overlay_frame.to_csv(table_root / "overlay_pixel_table.csv", index=False, encoding="utf-8-sig")
        slice_component_frame.to_csv(table_root / "slice_component_table.csv", index=False, encoding="utf-8-sig")
        overlay_component_frame.to_csv(table_root / "overlay_component_table.csv", index=False, encoding="utf-8-sig")
        remaining_png = len([path for path in image_root.rglob("*.png") if path.is_file()])
        qa = {
            "model_id": model_id,
            "mode": mode,
            "slice_rows": len(slice_frame),
            "overlay_rows": len(overlay_frame),
            "slice_component_rows": len(slice_component_frame),
            "overlay_component_rows": len(overlay_component_frame),
            "readback_mismatch_sum": readback_mismatch_sum,
            "png_created": png_created,
            "png_deleted": png_deleted,
            "remaining_png": remaining_png,
            "config_sha256": cfg.config_sha256,
            "status": "passed"
            if readback_mismatch_sum == 0
            and (mode == "ARTIFACT-FULL" or remaining_png == 0)
            else "failed",
        }
        (target / "qa.json").write_text(__import__("json").dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return ExtractionOutput(
            tables=PrimitiveTables(model_id, slice_frame, overlay_frame, overlay_component_frame),
            slice_components=slice_component_frame,
            qa=qa,
            output_dir=target,
        )
