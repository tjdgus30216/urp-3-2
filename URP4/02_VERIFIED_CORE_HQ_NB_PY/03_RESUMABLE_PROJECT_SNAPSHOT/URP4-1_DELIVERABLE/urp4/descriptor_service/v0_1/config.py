"""Immutable extraction configuration for the RUN-139 descriptor backend."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from urp4.contracts.v0_1.canonical import sha256_hex


@dataclass(frozen=True)
class ExtractionConfig:
    axis: str = "z"
    physical_size_mm: float = 40.0
    slice_count: int = 801
    slice_spacing_mm: float = 0.05
    pixel_width: int = 1000
    pixel_height: int = 1000
    area_per_pixel_mm2: float = 0.0016
    length_per_pixel_mm: float = 0.04
    connectivity: int = 8
    min_component_pixels: int = 2
    endpoint_nudge_mm: float = 1e-6
    png_compress_level: int = 1

    def validate(self) -> None:
        if self.axis != "z":
            raise ValueError("RUN-139 v0.1 supports only the frozen z-axis contract")
        if self.slice_count < 2 or self.pixel_width < 1 or self.pixel_height < 1:
            raise ValueError("invalid slice/pixel dimensions")
        if self.slice_spacing_mm <= 0 or self.area_per_pixel_mm2 <= 0 or self.length_per_pixel_mm <= 0:
            raise ValueError("physical resolution values must be positive")
        if self.connectivity not in (4, 8) or self.min_component_pixels < 1:
            raise ValueError("invalid connected-component contract")
        expected_span = (self.slice_count - 1) * self.slice_spacing_mm
        if abs(expected_span - self.physical_size_mm) > 1e-12:
            raise ValueError("slice_count and slice_spacing_mm must span physical_size_mm")
        expected_area = (self.physical_size_mm / self.pixel_width) * (self.physical_size_mm / self.pixel_height)
        if abs(expected_area - self.area_per_pixel_mm2) > 1e-15:
            raise ValueError("area_per_pixel_mm2 differs from the declared physical/pixel resolution")

    @property
    def config_sha256(self) -> str:
        self.validate()
        return sha256_hex(asdict(self))


RUN139_EXTRACTION_CONFIG = ExtractionConfig()
