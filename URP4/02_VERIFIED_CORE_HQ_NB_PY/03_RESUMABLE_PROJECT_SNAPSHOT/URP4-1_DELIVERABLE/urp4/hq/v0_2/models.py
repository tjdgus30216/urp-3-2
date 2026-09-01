"""Typed public contract for the HQ v0.2 development blueprint.

This module does not execute geometry, descriptors, y intake, training or
inverse design.  It only describes and freezes the public research settings
that a future validated implementation may consume.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


BLUEPRINT_VERSION = "URP4-HQ-BLUEPRINT-v0.2"
STATUS_ONLY_MODE = "blueprint_status_only"


@dataclass(frozen=True)
class BlueprintController:
    """The only public configuration surface in the blueprint notebook."""

    execution_mode: str = STATUS_ONLY_MODE
    geometry_mode: str = "status_only"  # status_only | import | generate
    input_file: str = ""
    input_directory: str = ""
    source_type: str = "imported_stl"  # generated_stl | imported_stl | original_stp
    model_family: str = "unspecified"
    generation_parameters: dict[str, Any] = field(default_factory=dict)

    normalize_all_analysis_geometry: bool = True
    normalization_target_mm: float = 40.0
    normalization_method: str = "centered_uniform_bbox_to_40mm"
    enable_generated_normalization: bool = False

    slicing_axis: str = "z"
    pixel_resolution: int = 1000
    slice_count: int = 801
    slice_spacing_mm: float = 0.05
    threshold_rule: str = "binary_nonzero_png_readback"
    connectivity: int = 8
    min_component_pixels: int = 2

    descriptor_scope: tuple[str, ...] = ("run139_minimal_9_scalar",)
    candidate_registry_version: str = "XREG-v2.7-TECHNICAL"
    batch_enabled: bool = False
    resume_enabled: bool = True

    y_target: str = ""
    feature_selection_method: str = "LOCKED"
    training_method: str = "LOCKED"
    ensemble_policy: str = "LOCKED"
    enable_y_intake: bool = False
    enable_feature_selection: bool = False
    enable_training: bool = False
    enable_ensemble: bool = False
    enable_forward_performance: bool = False
    enable_inverse_design: bool = False

    artifact_policy: str = "STREAMING_TEMP_PNG"
    retain_selected_review_images: bool = True
    output_directory: str = "outputs/blueprint_status"

