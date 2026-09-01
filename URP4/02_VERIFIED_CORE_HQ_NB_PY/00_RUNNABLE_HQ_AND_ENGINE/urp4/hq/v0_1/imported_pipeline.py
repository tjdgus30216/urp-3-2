"""Image-readback descriptor adapter for the approved imported-STL route."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from urp4.descriptor_service.v0_1.component import component_features_for_pair
from urp4.descriptor_service.v0_1.models import PrimitiveTables
from urp4.descriptor_service.v0_1.pixel import (
    connected_components,
    read_mask,
    read_overlay_counts,
    save_mask,
    save_overlay,
)
from urp4.geometry_io.v0_4.imported_winding import ImportedSTLWindingConfig, imported_stl_mask_stream


@dataclass(frozen=True)
class ImportedExtractionOutput:
    tables: PrimitiveTables
    slice_components: pd.DataFrame
    qa: dict[str, object]
    output_dir: Path


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract_imported_stl(
    *,
    model_id: str,
    geometry_path: str | Path,
    output_dir: str | Path,
    config: ImportedSTLWindingConfig,
    image_policy: str,
    min_component_pixels: int = 2,
    connectivity: int = 8,
) -> ImportedExtractionOutput:
    """Run winding masks through saved-PNG readback and RUN-139 primitive tables."""

    target = Path(output_dir)
    if target.exists() and any(target.iterdir()):
        raise FileExistsError(f"refusing to overwrite non-empty imported extraction directory: {target}")
    mask_root = target / "images" / "masks"
    overlay_root = target / "images" / "overlays"
    table_root = target / "tables"
    mask_root.mkdir(parents=True, exist_ok=True)
    overlay_root.mkdir(parents=True, exist_ok=True)
    table_root.mkdir(parents=True, exist_ok=True)

    area_per_pixel = (config.expected_size_mm / config.pixel_resolution) ** 2
    length_per_pixel = config.expected_size_mm / config.pixel_resolution
    layer_height = config.expected_size_mm / (config.slice_count - 1)
    slice_rows: list[dict[str, object]] = []
    overlay_rows: list[dict[str, object]] = []
    slice_component_rows: list[dict[str, object]] = []
    overlay_component_rows: list[dict[str, object]] = []
    previous_mask = None
    png_created = png_deleted = mismatch_sum = flagged_count = 0
    source_hash = route_id = algorithm_revision = ""

    for payload in imported_stl_mask_stream(geometry_path, config):
        slice_index = int(payload["slice_index"])
        mask = payload["mask"]
        source_hash = str(payload["source_geometry_sha256"])
        route_id = str(payload["route_id"])
        algorithm_revision = str(payload["algorithm_revision"])
        mask_path = mask_root / f"m{slice_index:04d}.png"
        save_mask(mask, mask_path, compress_level=1)
        png_created += 1
        readback = read_mask(mask_path)
        mismatch = int((mask ^ readback).sum())
        mismatch_sum += mismatch
        components, _ = connected_components(readback, min_pixels=min_component_pixels, connectivity=connectivity)
        material_pixels = int(readback.sum())
        is_flagged = bool(mismatch or (0 < slice_index < config.slice_count - 1 and material_pixels == 0))
        flagged_count += int(is_flagged)
        slice_rows.append({
            "model_id": model_id,
            "slice_index": slice_index,
            "z_nominal_mm": float(slice_index * layer_height),
            "z_eval_mm": float(payload["z_mm"]),
            "endpoint_adjusted": bool(payload["endpoint_adjusted"]),
            "active_triangle_count": int(payload["z_active_triangle_count"]),
            "segment_count": int(payload["segment_count"]),
            "material_pixel_count": material_pixels,
            "material_area_mm2": material_pixels * area_per_pixel,
            "component_count": len(components),
            "odd_scanline_rows": 0,
            "filled_rows": int(payload["nonzero_row_count"]),
            "max_scanline_intersections": int(payload["max_abs_winding"]),
            "mask_sha256": _sha256(mask_path),
            "route_id": route_id,
            "algorithm_revision": algorithm_revision,
            "flagged": is_flagged,
        })
        for component in components:
            slice_component_rows.append({
                "model_id": model_id,
                "component_scope": "slice_mask",
                "slice_index_a": slice_index,
                "slice_index_b": "",
                **component,
                "area_mm2": component["pixel_count"] * area_per_pixel,
                "connectivity": connectivity,
                "min_component_pixels": min_component_pixels,
            })

        if previous_mask is not None:
            pair_index = slice_index - 1
            overlay_path = overlay_root / f"o{pair_index:04d}.png"
            expected = save_overlay(previous_mask, readback, overlay_path, compress_level=1)
            png_created += 1
            observed = read_overlay_counts(overlay_path)
            mismatch_sum += sum(abs(expected[key] - observed[key]) for key in expected)
            features, layer_counts = component_features_for_pair(
                previous_mask,
                readback,
                pair_index=pair_index,
                area_per_pixel=area_per_pixel,
                length_per_pixel=length_per_pixel,
                layer_height=layer_height,
                min_pixels=min_component_pixels,
                connectivity=connectivity,
            )
            overlay_rows.append({
                "model_id": model_id,
                "pair_index": pair_index,
                "slice_index_a": slice_index - 1,
                "slice_index_b": slice_index,
                **observed,
                "red_area_mm2": observed["red_pixel_count"] * area_per_pixel,
                "blue_area_mm2": observed["blue_pixel_count"] * area_per_pixel,
                "purple_area_mm2": observed["purple_pixel_count"] * area_per_pixel,
                "union_area_mm2": observed["union_pixel_count"] * area_per_pixel,
                "overlay_sha256": _sha256(overlay_path),
                "component_count_raw": layer_counts["component_count_raw"],
                "component_count_kept": layer_counts["component_count_kept"],
            })
            for feature in features:
                overlay_component_rows.append({
                    "model_id": model_id,
                    "component_scope": "overlay_union",
                    "slice_index_a": slice_index - 1,
                    "slice_index_b": slice_index,
                    **feature.to_row(),
                    "connectivity": connectivity,
                    "min_component_pixels": min_component_pixels,
                })
            keep_overlay = image_policy == "KEEP_ALL" or (image_policy == "KEEP_FLAGGED" and is_flagged)
            if not keep_overlay:
                overlay_path.unlink()
                png_deleted += 1
        previous_mask = readback
        keep_mask = image_policy == "KEEP_ALL" or (image_policy == "KEEP_FLAGGED" and is_flagged)
        if not keep_mask:
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
    remaining_png = len(list((target / "images").rglob("*.png")))
    qa = {
        "model_id": model_id,
        "source_geometry_sha256": source_hash,
        "route_id": route_id,
        "algorithm_revision": algorithm_revision,
        "image_policy": image_policy,
        "slice_rows": len(slice_frame),
        "overlay_rows": len(overlay_frame),
        "slice_component_rows": len(slice_component_frame),
        "overlay_component_rows": len(overlay_component_frame),
        "readback_mismatch_sum": mismatch_sum,
        "flagged_slice_count": flagged_count,
        "png_created": png_created,
        "png_deleted": png_deleted,
        "remaining_png": remaining_png,
        "status": "passed" if mismatch_sum == 0 and len(slice_frame) == 801 and len(overlay_frame) == 800 else "failed",
    }
    (target / "qa.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return ImportedExtractionOutput(
        tables=PrimitiveTables(model_id, slice_frame, overlay_frame, overlay_component_frame),
        slice_components=slice_component_frame,
        qa=qa,
        output_dir=target,
    )

