"""Start/End graph descriptors extracted from notebook display Cell 5."""

from __future__ import annotations

import math
import statistics
from collections import defaultdict

import numpy as np

from .graph import connected_components
from .models import GenerationConfig, LatticeGraph


def _mean(values: list[float]) -> float:
    finite = [float(value) for value in values if math.isfinite(float(value))]
    return statistics.mean(finite) if finite else math.nan


def _sample_std(values: list[float]) -> float:
    finite = [float(value) for value in values if math.isfinite(float(value))]
    return statistics.stdev(finite) if len(finite) > 1 else (0.0 if len(finite) == 1 else math.nan)


def _weighted(values: list[float], weights: list[float]) -> tuple[float, float]:
    pairs = [(float(v), float(w)) for v, w in zip(values, weights) if math.isfinite(float(v)) and float(w) > 0]
    if not pairs:
        return math.nan, math.nan
    weight_sum = sum(weight for _, weight in pairs)
    average = sum(value * weight for value, weight in pairs) / weight_sum
    std = math.sqrt(sum(weight * (value - average) ** 2 for value, weight in pairs) / weight_sum)
    return average, std


def _axis_angles(first: np.ndarray, second: np.ndarray) -> tuple[float, float, float, float]:
    delta = np.asarray(first) - np.asarray(second)
    length = float(np.linalg.norm(delta))
    if length <= 1e-12:
        return 0.0, math.nan, math.nan, math.nan
    angle = lambda value: math.degrees(math.asin(max(0.0, min(1.0, abs(float(value)) / length))))
    return length, angle(delta[2]), angle(delta[0]), angle(delta[1])


def extract_start_end_structural_factors(model_id: str, graph: LatticeGraph, config: GenerationConfig) -> dict[str, object]:
    node_to_struts: dict[tuple[float, float, float], list[dict[str, object]]] = defaultdict(list)
    unique: dict[tuple[tuple[float, float, float], tuple[float, float, float]], dict[str, object]] = {}
    for (first_id, second_id), radius in zip(graph.edges, graph.radii):
        first, second = graph.nodes[int(first_id)], graph.nodes[int(second_id)]
        length, angle_z, angle_x, angle_y = _axis_angles(first, second)
        if length <= config.min_edge_length_mm:
            continue
        key_a = tuple(np.round(first, config.merge_round_digits).tolist())
        key_b = tuple(np.round(second, config.merge_round_digits).tolist())
        pair = tuple(sorted((key_a, key_b)))
        item = {
            "length": length, "radius": float(radius), "diameter": 2.0 * float(radius),
            "l_over_d": length / (2.0 * float(radius)), "angle_z": angle_z,
            "angle_x": angle_x, "angle_y": angle_y, "p1": first, "p2": second,
        }
        unique.setdefault(pair, item)
        node_to_struts[key_a].append(item)
        node_to_struts[key_b].append(item)
    struts = list(unique.values())
    nodes = sorted(node_to_struts)
    lengths = [float(item["length"]) for item in struts]
    radii = [float(item["radius"]) for item in struts]
    degrees = [len(node_to_struts[node]) for node in nodes]

    def global_angle(key: str) -> tuple[float, float]:
        return _weighted([float(item[key]) for item in struts], lengths)

    def node_stat(key: str, weighted: bool = False) -> tuple[float, float]:
        averages: list[float] = []
        for node in nodes:
            local = node_to_struts[node]
            if weighted:
                averages.append(_weighted([float(item[key]) for item in local], [float(item["length"]) for item in local])[0])
            else:
                averages.append(_mean([float(item[key]) for item in local]))
        return _mean(averages), _sample_std(averages)

    gaz, gazs = global_angle("angle_z")
    gax, gaxs = global_angle("angle_x")
    gay, gays = global_angle("angle_y")
    naz, nazs = node_stat("angle_z", True)
    nax, naxs = node_stat("angle_x", True)
    nay, nays = node_stat("angle_y", True)
    nlen, nlens = node_stat("length")
    nld, nlds = node_stat("l_over_d")
    centers = np.asarray([(np.asarray(item["p1"]) + np.asarray(item["p2"])) * 0.5 for item in struts])
    # Preserve the notebook's Python ``sum(list)`` accumulation order. NumPy's
    # pairwise reduction changes the final surface-area bit at ~1.8e-12.
    volume_terms = [math.pi * float(item["radius"]) ** 2 * float(item["length"]) for item in struts]
    surface_terms = [2.0 * math.pi * float(item["radius"]) * float(item["length"]) for item in struts]
    volumes = np.asarray(volume_terms, dtype=float)
    solid_volume = float(sum(volume_terms))
    surface_area = float(sum(surface_terms))
    mass_center = np.sum(centers * (volumes / volumes.sum())[:, None], axis=0)
    node_array = np.asarray(nodes)
    return {
        "model_id": model_id, "source_type": graph.source_type, "source_name": graph.source_name,
        "target_vf": graph.target_vf, "actual_vf": graph.actual_vf,
        "node_count": len(nodes), "strut_count": len(struts),
        "global_degree_avg": _mean(degrees), "global_degree_stdev": _sample_std(degrees),
        "global_length_avg_mm": _mean(lengths), "global_length_stdev_mm": _sample_std(lengths),
        "global_angle_z_weighted_avg_deg": gaz, "global_angle_z_weighted_stdev_deg": gazs,
        "node_length_avg_mm": nlen, "node_length_stdev_mm": nlens,
        "node_angle_z_weighted_avg_deg": naz, "node_angle_z_weighted_stdev_deg": nazs,
        "global_l_over_d_avg": _mean([float(item["l_over_d"]) for item in struts]),
        "global_l_over_d_stdev": _sample_std([float(item["l_over_d"]) for item in struts]),
        "node_l_over_d_avg": nld, "node_l_over_d_stdev": nlds,
        "global_angle_x_weighted_avg_deg": gax, "global_angle_x_weighted_stdev_deg": gaxs,
        "node_angle_x_weighted_avg_deg": nax, "node_angle_x_weighted_stdev_deg": naxs,
        "global_angle_y_weighted_avg_deg": gay, "global_angle_y_weighted_stdev_deg": gays,
        "node_angle_y_weighted_avg_deg": nay, "node_angle_y_weighted_stdev_deg": nays,
        "connected_components": len(connected_components(len(graph.nodes), graph.edges)),
        "maxwell_index_m_3d": len(struts) - 3 * len(nodes) + 6,
        "total_strut_length_mm": sum(lengths), "mean_radius_mm": _mean(radii),
        "std_radius_mm": _sample_std(radii), "mean_diameter_mm": 2.0 * _mean(radii),
        "surface_area_mm2": surface_area,
        "surface_to_solid_volume_1_per_mm": surface_area / solid_volume,
        "solid_volume_mm3_approx": solid_volume,
        "bbox_x_mm": float(np.ptp(node_array[:, 0])), "bbox_y_mm": float(np.ptp(node_array[:, 1])),
        "bbox_z_mm": float(np.ptp(node_array[:, 2])),
        "mass_center_x_mm": float(mass_center[0]), "mass_center_y_mm": float(mass_center[1]),
        "mass_center_z_mm": float(mass_center[2]),
    }
