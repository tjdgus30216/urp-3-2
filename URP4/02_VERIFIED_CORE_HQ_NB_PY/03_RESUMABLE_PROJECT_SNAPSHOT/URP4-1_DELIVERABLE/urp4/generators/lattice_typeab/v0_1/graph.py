"""Type-A graph generation ported from notebook display Cells 3 and 5.

The mathematical and random-number operation order is intentionally preserved so
the CINT-04 harness can compare arrays against functions compiled directly from
the immutable notebook source.
"""

from __future__ import annotations

import math
from typing import Dict, Iterable, List, Tuple

import numpy as np
from scipy.spatial.distance import pdist, squareform

from .models import GenerationConfig, LatticeGraph


def _key3(point: np.ndarray, digits: int = 6) -> tuple[float, float, float]:
    return tuple(np.round(np.asarray(point, dtype=float), digits).tolist())


def deduplicate_nodes_edges(
    nodes: np.ndarray,
    edges: Iterable[Tuple[int, int]],
    digits: int = 6,
    min_edge_length: float = 0.05,
) -> tuple[np.ndarray, np.ndarray]:
    node_map: Dict[tuple[float, float, float], int] = {}
    new_nodes: List[np.ndarray] = []
    old_to_new: Dict[int, int] = {}
    for index, point in enumerate(np.asarray(nodes, dtype=float)):
        key = _key3(point, digits)
        if key not in node_map:
            node_map[key] = len(new_nodes)
            new_nodes.append(np.asarray(point, dtype=float))
        old_to_new[index] = node_map[key]
    new_nodes_array = np.asarray(new_nodes, dtype=float)
    edge_set: set[tuple[int, int]] = set()
    for first, second in edges:
        a, b = old_to_new[int(first)], old_to_new[int(second)]
        if a == b:
            continue
        if np.linalg.norm(new_nodes_array[a] - new_nodes_array[b]) < min_edge_length:
            continue
        edge_set.add(tuple(sorted((a, b))))
    if not edge_set:
        return new_nodes_array, np.zeros((0, 2), dtype=int)
    return new_nodes_array, np.asarray(sorted(edge_set), dtype=int)


def connected_components(n_nodes: int, edges: np.ndarray) -> list[list[int]]:
    parent = list(range(n_nodes))

    def find(value: int) -> int:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def union(first: int, second: int) -> None:
        root_a, root_b = find(first), find(second)
        if root_a != root_b:
            parent[root_b] = root_a

    for first, second in np.asarray(edges, dtype=int):
        union(int(first), int(second))
    components: dict[int, list[int]] = {}
    for index in range(n_nodes):
        components.setdefault(find(index), []).append(index)
    return list(components.values())


def ensure_connected(nodes: np.ndarray, edges: np.ndarray, max_components_to_repair: int = 50) -> np.ndarray:
    if len(nodes) == 0:
        return edges
    edge_list = [tuple(map(int, edge)) for edge in np.asarray(edges, dtype=int)]
    if not edge_list:
        return np.zeros((0, 2), dtype=int)
    components = connected_components(len(nodes), np.asarray(edge_list, dtype=int))
    if len(components) <= 1:
        return np.asarray(sorted(set(tuple(sorted(edge)) for edge in edge_list)), dtype=int)
    if len(components) > max_components_to_repair:
        return np.asarray(sorted(set(tuple(sorted(edge)) for edge in edge_list)), dtype=int)
    used = {tuple(sorted(edge)) for edge in edge_list}
    while True:
        components = connected_components(len(nodes), np.asarray(edge_list, dtype=int))
        if len(components) <= 1:
            break
        distances = squareform(pdist(nodes)) if len(nodes) > 1 else np.zeros((1, 1))
        best_pair = None
        best_distance = math.inf
        for ca in range(len(components)):
            for cb in range(ca + 1, len(components)):
                for i in components[ca]:
                    for j in components[cb]:
                        distance = distances[i, j]
                        pair = tuple(sorted((int(i), int(j))))
                        if pair not in used and distance < best_distance:
                            best_distance = float(distance)
                            best_pair = pair
        if best_pair is None:
            break
        edge_list.append(best_pair)
        used.add(best_pair)
    return np.asarray(sorted(set(tuple(sorted(edge)) for edge in edge_list)), dtype=int)


def _base_unit_nodes(length: float) -> list[list[float]]:
    nodes: list[list[float]] = []
    for x in (0.0, length):
        for y in (0.0, length):
            for z in (0.0, length):
                nodes.append([x, y, z])
    half = length / 2.0
    nodes += [
        [0.0, half, half], [length, half, half],
        [half, 0.0, half], [half, length, half],
        [half, half, 0.0], [half, half, length],
    ]
    nodes.append([half, half, half])
    return nodes


def generate_type_a_unit_cell(config: GenerationConfig, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    length = config.cell_size_mm
    nodes = _base_unit_nodes(length)
    interior_count = int(rng.integers(config.random_interior_nodes_min, config.random_interior_nodes_max + 1))
    margin = 0.12 * length
    for _ in range(interior_count):
        nodes.append(rng.uniform(margin, length - margin, size=3).tolist())
    face_pair_count = int(rng.integers(config.random_face_pair_nodes_min, config.random_face_pair_nodes_max + 1))
    for _ in range(face_pair_count):
        axis = int(rng.integers(0, 3))
        uv = rng.uniform(0.18 * length, 0.82 * length, size=2)
        p0, p1 = np.zeros(3), np.zeros(3)
        other_axes = [item for item in range(3) if item != axis]
        p0[axis], p1[axis] = 0.0, length
        p0[other_axes], p1[other_axes] = uv, uv
        nodes.extend([p0.tolist(), p1.tolist()])
    nodes_array, _ = deduplicate_nodes_edges(np.asarray(nodes, dtype=float), [], config.merge_round_digits)
    distances = squareform(pdist(nodes_array))
    np.fill_diagonal(distances, np.inf)
    count = len(nodes_array)
    degree = np.zeros(count, dtype=int)
    edges: set[tuple[int, int]] = set()
    minimum_length = max(0.18 * length, config.min_edge_length_mm)
    maximum_length = 1.15 * length
    target_degree = rng.integers(config.min_degree, config.max_degree + 1, size=count)
    random_penalty = rng.uniform(0.0, 0.18 * length, size=distances.shape)
    order_matrix = distances + random_penalty
    for i in rng.permutation(count):
        for j in np.argsort(order_matrix[i]):
            if degree[i] >= target_degree[i]:
                break
            if degree[j] >= config.max_degree:
                continue
            distance = distances[i, j]
            if not minimum_length <= distance <= maximum_length:
                continue
            pair = tuple(sorted((int(i), int(j))))
            if pair in edges:
                continue
            edges.add(pair)
            degree[i] += 1
            degree[j] += 1
    candidate_pairs: list[tuple[float, tuple[int, int]]] = []
    for i in range(count):
        for j in range(i + 1, count):
            distance = distances[i, j]
            if 0.45 * length <= distance <= math.sqrt(3) * length:
                candidate_pairs.append((float(distance + rng.uniform(0, 0.35 * length)), (i, j)))
    candidate_pairs.sort(key=lambda item: item[0])
    for _, pair in candidate_pairs:
        if rng.random() > 0.12:
            continue
        i, j = pair
        if degree[i] >= config.max_degree or degree[j] >= config.max_degree:
            continue
        edges.add(pair)
        degree[i] += 1
        degree[j] += 1
    nodes_array, edge_array = deduplicate_nodes_edges(
        nodes_array, edges, config.merge_round_digits, config.min_edge_length_mm
    )
    return nodes_array, ensure_connected(nodes_array, edge_array)


def standardize_unit_cell(nodes: np.ndarray, cell_size: float) -> np.ndarray:
    nodes = np.asarray(nodes, dtype=float).copy()
    minimum = nodes.min(axis=0)
    span = nodes.max(axis=0) - minimum
    maximum_span = float(np.max(span))
    if maximum_span <= 1e-9:
        raise ValueError("Cannot standardize a unit cell with zero coordinate span.")
    nodes = nodes - minimum
    nodes *= cell_size / maximum_span
    return np.clip(nodes, 0.0, cell_size)


def tile_unit_cell(unit_nodes: np.ndarray, unit_edges: np.ndarray, config: GenerationConfig) -> tuple[np.ndarray, np.ndarray]:
    unit_nodes = standardize_unit_cell(unit_nodes, config.cell_size_mm)
    cell_size = config.cell_size_mm
    all_nodes: list[np.ndarray] = []
    all_edges: list[tuple[int, int]] = []
    node_map: dict[tuple[float, float, float], int] = {}

    def add_node(point: np.ndarray) -> int:
        key = _key3(point, config.merge_round_digits)
        if key not in node_map:
            node_map[key] = len(all_nodes)
            all_nodes.append(np.asarray(point, dtype=float))
        return node_map[key]

    for ix in range(config.cells_per_axis):
        for iy in range(config.cells_per_axis):
            for iz in range(config.cells_per_axis):
                shift = np.array([ix * cell_size, iy * cell_size, iz * cell_size], dtype=float)
                local_to_global = [add_node(point + shift) for point in unit_nodes]
                for first, second in unit_edges:
                    a, b = local_to_global[int(first)], local_to_global[int(second)]
                    if a != b:
                        all_edges.append(tuple(sorted((a, b))))
    nodes, edges = deduplicate_nodes_edges(
        np.asarray(all_nodes, dtype=float), all_edges, config.merge_round_digits, config.min_edge_length_mm
    )
    nodes = nodes - config.total_length_mm / 2.0
    return nodes, ensure_connected(nodes, edges)


def strut_lengths(nodes: np.ndarray, edges: np.ndarray) -> np.ndarray:
    return np.linalg.norm(nodes[edges[:, 1]] - nodes[edges[:, 0]], axis=1)


def calculate_volume_fraction(
    nodes: np.ndarray, edges: np.ndarray, radii: np.ndarray, total_length: float
) -> float:
    volume = float(np.sum(math.pi * radii**2 * strut_lengths(nodes, edges)))
    return volume / total_length**3


def assign_uniform_radius_for_vf(
    nodes: np.ndarray, edges: np.ndarray, target_vf: float, total_length: float
) -> tuple[np.ndarray, float]:
    if not 0 < target_vf <= 1:
        raise ValueError("target_vf must be in (0, 1]")
    total_strut_length = float(np.sum(strut_lengths(nodes, edges)))
    if total_strut_length <= 1e-12:
        raise ValueError("Cannot assign radius because total strut length is zero.")
    radius = math.sqrt(max(target_vf * total_length**3 / (math.pi * total_strut_length), 1e-12))
    radii = np.full(len(edges), radius, dtype=float)
    return radii, calculate_volume_fraction(nodes, edges, radii, total_length)


def create_type_a_model(target_vf: float, config: GenerationConfig, rng: np.random.Generator) -> LatticeGraph:
    unit_nodes, unit_edges = generate_type_a_unit_cell(config, rng)
    nodes, edges = tile_unit_cell(unit_nodes, unit_edges, config)
    radii, actual_vf = assign_uniform_radius_for_vf(nodes, edges, target_vf, config.total_length_mm)
    model = LatticeGraph(
        nodes=nodes,
        edges=edges,
        radii=radii,
        source_type="A",
        target_vf=target_vf,
        actual_vf=actual_vf,
        source_name="random_unit_cell",
    )
    model.validate()
    return model

