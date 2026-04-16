"""Tests for the A* 3D pathfinding algorithm."""

import pytest
from app.core.drone_profiles import get_profile
from app.pathfinding.graph_builder import GraphBuilder
from app.pathfinding.a_star_3d import a_star_3d, energy_heuristic


def test_simple_route():
    profile = get_profile("quadcopter_medium")
    builder = GraphBuilder(profile)

    start = (40.70, -74.00, 100.0)
    end = (40.71, -74.00, 100.0)

    graph = builder.build_graph(
        start=start,
        end=end,
        grid_resolution_km=0.5,
        altitude_levels=[100],
    )

    start_id = builder._node_id(*start)
    end_id = builder._node_id(*end)

    result = a_star_3d(graph, start_id, end_id, profile.battery_capacity_wh)

    assert result["node_count"] >= 2
    assert result["total_energy_j"] > 0
    assert result["total_distance_m"] > 0
    assert result["battery_used_pct"] > 0
    assert result["battery_remaining_pct"] < 100
    assert len(result["waypoints"]) >= 2
    assert len(result["battery_curve"]) >= 2

    # First waypoint should be start
    assert result["waypoints"][0]["lat"] == start[0]
    assert result["waypoints"][0]["lon"] == start[1]

    # Last waypoint should be end
    assert result["waypoints"][-1]["lat"] == end[0]
    assert result["waypoints"][-1]["lon"] == end[1]


def test_route_with_altitude_change():
    profile = get_profile("quadcopter_medium")
    builder = GraphBuilder(profile)

    start = (40.70, -74.00, 50.0)
    end = (40.71, -74.00, 200.0)

    graph = builder.build_graph(
        start=start,
        end=end,
        grid_resolution_km=0.5,
        altitude_levels=[50, 100, 150, 200],
    )

    start_id = builder._node_id(*start)
    end_id = builder._node_id(*end)

    result = a_star_3d(graph, start_id, end_id, profile.battery_capacity_wh)
    assert result["node_count"] >= 2


def test_geofence_avoidance():
    profile = get_profile("quadcopter_medium")
    builder = GraphBuilder(profile)

    start = (40.70, -74.00, 100.0)
    end = (40.72, -74.00, 100.0)

    geofences = [
        {
            "center_lat": 40.71,
            "center_lon": -74.00,
            "radius_m": 500,
            "floor_alt_m": 0,
            "ceiling_alt_m": 300,
        }
    ]

    graph = builder.build_graph(
        start=start,
        end=end,
        geofences=geofences,
        grid_resolution_km=0.3,
        altitude_levels=[100, 200],
    )

    start_id = builder._node_id(*start)
    end_id = builder._node_id(*end)

    result = a_star_3d(graph, start_id, end_id, profile.battery_capacity_wh)
    assert result["node_count"] >= 2


def test_no_path_raises():
    """Test that an isolated start node raises ValueError."""
    import networkx as nx

    graph = nx.DiGraph()
    graph.add_node("start", lat=40.0, lon=-74.0, alt=100)
    graph.add_node("end", lat=41.0, lon=-74.0, alt=100)

    with pytest.raises(ValueError, match="No viable path"):
        a_star_3d(graph, "start", "end", 250)


def test_invalid_start_node():
    import networkx as nx

    graph = nx.DiGraph()
    graph.add_node("end", lat=41.0, lon=-74.0, alt=100)

    with pytest.raises(ValueError, match="Start node"):
        a_star_3d(graph, "nonexistent", "end", 250)
