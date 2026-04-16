"""Converts 3D space into a searchable graph of nodes for pathfinding."""

import math
import networkx as nx
from ..physics.aerodynamics import WindVector
from ..physics.energy_model import calculate_segment_energy, haversine_m
from ..core.drone_profiles import DroneProfile


class GraphBuilder:
    """Builds a 3D graph from environment data for pathfinding."""

    def __init__(self, profile: DroneProfile):
        self.profile = profile
        self.graph = nx.DiGraph()

    def build_graph(
        self,
        start: tuple[float, float, float],
        end: tuple[float, float, float],
        elevation_data: list[dict] | None = None,
        wind_data: list[dict] | None = None,
        geofences: list[dict] | None = None,
        grid_resolution_km: float = 0.5,
        altitude_levels: list[float] | None = None,
    ) -> nx.DiGraph:
        """Build a 3D navigation graph between start and end points."""
        if altitude_levels is None:
            altitude_levels = [50, 100, 150, 200]

        if geofences is None:
            geofences = []

        lat_min = min(start[0], end[0]) - 0.02
        lat_max = max(start[0], end[0]) + 0.02
        lon_min = min(start[1], end[1]) - 0.02
        lon_max = max(start[1], end[1]) + 0.02

        step_deg = grid_resolution_km / 111.0

        nodes = []

        # Add start and end nodes
        start_id = self._node_id(start[0], start[1], start[2])
        end_id = self._node_id(end[0], end[1], end[2])
        self.graph.add_node(start_id, lat=start[0], lon=start[1], alt=start[2])
        self.graph.add_node(end_id, lat=end[0], lon=end[1], alt=end[2])
        nodes.append((start[0], start[1], start[2], start_id))
        nodes.append((end[0], end[1], end[2], end_id))

        # Generate grid nodes
        lat = lat_min
        while lat <= lat_max:
            lon = lon_min
            while lon <= lon_max:
                for alt in altitude_levels:
                    if self._is_in_geofence(lat, lon, alt, geofences):
                        lon += step_deg
                        continue
                    nid = self._node_id(lat, lon, alt)
                    self.graph.add_node(nid, lat=lat, lon=lon, alt=alt)
                    nodes.append((lat, lon, alt, nid))
                lon += step_deg
            lat += step_deg

        # Build edges between nearby nodes
        wind_map = self._build_wind_map(wind_data) if wind_data else {}
        max_edge_dist_km = grid_resolution_km * 2.5

        for i, (lat1, lon1, alt1, nid1) in enumerate(nodes):
            for j, (lat2, lon2, alt2, nid2) in enumerate(nodes):
                if i == j:
                    continue
                hdist = haversine_m(lat1, lon1, lat2, lon2) / 1000.0
                vdist = abs(alt2 - alt1) / 1000.0
                dist_3d = math.sqrt(hdist**2 + vdist**2)

                if dist_3d > max_edge_dist_km:
                    continue

                wind = self._get_nearest_wind(lat1, lon1, alt1, wind_map)
                segment = calculate_segment_energy(
                    lat1, lon1, alt1, lat2, lon2, alt2, self.profile, wind
                )

                self.graph.add_edge(
                    nid1, nid2,
                    weight=segment["energy_j"],
                    distance_m=segment["distance_m"],
                    duration_s=segment["duration_s"],
                    power_w=segment["power_w"],
                )

        return self.graph

    def _node_id(self, lat: float, lon: float, alt: float) -> str:
        return f"{lat:.4f}_{lon:.4f}_{alt:.0f}"

    def _is_in_geofence(self, lat: float, lon: float, alt: float, geofences: list[dict]) -> bool:
        for gf in geofences:
            clat = gf.get("center_lat", 0)
            clon = gf.get("center_lon", 0)
            radius_m = gf.get("radius_m", 0)
            floor_alt = gf.get("floor_alt_m", 0)
            ceiling_alt = gf.get("ceiling_alt_m", float("inf"))

            if floor_alt <= alt <= ceiling_alt:
                dist = haversine_m(lat, lon, clat, clon)
                if dist <= radius_m:
                    return True
        return False

    def _build_wind_map(self, wind_data: list[dict]) -> dict:
        wind_map = {}
        for w in wind_data:
            key = self._node_id(w.get("lat", 0), w.get("lon", 0), w.get("alt", 0))
            wind_map[key] = WindVector(
                vx=w.get("vx", 0),
                vy=w.get("vy", 0),
                vz=w.get("vz", 0),
            )
        return wind_map

    def _get_nearest_wind(self, lat: float, lon: float, alt: float, wind_map: dict) -> WindVector:
        if not wind_map:
            return WindVector()

        best_key = None
        best_dist = float("inf")
        for key in wind_map:
            parts = key.split("_")
            wlat, wlon, walt = float(parts[0]), float(parts[1]), float(parts[2])
            d = math.sqrt((lat - wlat) ** 2 + (lon - wlon) ** 2 + ((alt - walt) / 10000) ** 2)
            if d < best_dist:
                best_dist = d
                best_key = key

        return wind_map.get(best_key, WindVector()) if best_key else WindVector()
