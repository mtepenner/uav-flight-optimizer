"""Custom 3D A* algorithm weighted by energy consumption."""

import math
import heapq
import networkx as nx
from ..physics.energy_model import haversine_m


def energy_heuristic(
    graph: nx.DiGraph, current: str, target: str, avg_power_w: float = 200.0, speed_ms: float = 12.0
) -> float:
    """Heuristic estimating minimum energy to reach target from current node."""
    c = graph.nodes[current]
    t = graph.nodes[target]

    hdist = haversine_m(c["lat"], c["lon"], t["lat"], t["lon"])
    vdist = abs(t["alt"] - c["alt"])
    dist_3d = math.sqrt(hdist**2 + vdist**2)

    estimated_time = dist_3d / speed_ms
    return avg_power_w * estimated_time * 0.5


def a_star_3d(
    graph: nx.DiGraph,
    start_id: str,
    end_id: str,
    battery_capacity_wh: float = 250.0,
) -> dict:
    """Run energy-weighted A* pathfinding on a 3D graph.

    Returns a dict with path nodes, total energy, distance, duration, and battery usage.
    """
    if start_id not in graph.nodes:
        raise ValueError(f"Start node {start_id} not in graph")
    if end_id not in graph.nodes:
        raise ValueError(f"End node {end_id} not in graph")

    battery_capacity_j = battery_capacity_wh * 3600

    open_set = []
    heapq.heappush(open_set, (0.0, start_id))

    came_from = {}
    g_score = {start_id: 0.0}
    f_score = {start_id: energy_heuristic(graph, start_id, end_id)}
    energy_used = {start_id: 0.0}

    closed_set = set()

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == end_id:
            return _reconstruct_path(graph, came_from, current, g_score, energy_used, battery_capacity_wh)

        if current in closed_set:
            continue
        closed_set.add(current)

        for neighbor in graph.neighbors(current):
            if neighbor in closed_set:
                continue

            edge = graph.edges[current, neighbor]
            tentative_g = g_score[current] + edge["weight"]
            tentative_energy = energy_used[current] + edge["weight"]

            if tentative_energy > battery_capacity_j:
                continue

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                energy_used[neighbor] = tentative_energy
                f = tentative_g + energy_heuristic(graph, neighbor, end_id)
                f_score[neighbor] = f
                heapq.heappush(open_set, (f, neighbor))

    raise ValueError("No viable path found within battery constraints")


def _reconstruct_path(
    graph: nx.DiGraph,
    came_from: dict,
    current: str,
    g_score: dict,
    energy_used: dict,
    battery_capacity_wh: float,
) -> dict:
    """Reconstruct the optimal path and compute summary statistics."""
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()

    waypoints = []
    total_distance = 0.0
    total_duration = 0.0
    cumulative_energy = 0.0
    battery_curve = []

    for i, node_id in enumerate(path):
        node = graph.nodes[node_id]
        segment_energy = 0.0
        segment_distance = 0.0
        segment_duration = 0.0
        segment_power = 0.0

        if i > 0:
            edge = graph.edges[path[i - 1], node_id]
            segment_energy = edge["weight"]
            segment_distance = edge["distance_m"]
            segment_duration = edge["duration_s"]
            segment_power = edge["power_w"]

        cumulative_energy += segment_energy
        total_distance += segment_distance
        total_duration += segment_duration
        battery_pct = max(0, 100 - (cumulative_energy / (battery_capacity_wh * 3600)) * 100)

        waypoints.append({
            "lat": node["lat"],
            "lon": node["lon"],
            "alt": node["alt"],
            "cumulative_energy_j": round(cumulative_energy, 2),
            "segment_power_w": round(segment_power, 2),
            "battery_pct": round(battery_pct, 2),
        })

        battery_curve.append({
            "distance_m": round(total_distance, 2),
            "battery_pct": round(battery_pct, 2),
            "altitude_m": node["alt"],
        })

    battery_capacity_j = battery_capacity_wh * 3600

    return {
        "waypoints": waypoints,
        "total_energy_j": round(cumulative_energy, 2),
        "total_distance_m": round(total_distance, 2),
        "total_duration_s": round(total_duration, 2),
        "battery_used_pct": round((cumulative_energy / battery_capacity_j) * 100, 2),
        "battery_remaining_pct": round(max(0, 100 - (cumulative_energy / battery_capacity_j) * 100), 2),
        "battery_curve": battery_curve,
        "node_count": len(path),
    }
