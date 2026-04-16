"""API routes for flight route optimization."""

import math
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ...core.drone_profiles import get_profile, list_profiles
from ...pathfinding.graph_builder import GraphBuilder
from ...pathfinding.a_star_3d import a_star_3d

router = APIRouter()


class OptimizeRequest(BaseModel):
    start_lat: float = Field(..., ge=-90, le=90)
    start_lon: float = Field(..., ge=-180, le=180)
    start_alt: float = Field(default=100.0, ge=0, le=5000)
    end_lat: float = Field(..., ge=-90, le=90)
    end_lon: float = Field(..., ge=-180, le=180)
    end_alt: float = Field(default=100.0, ge=0, le=5000)
    drone_profile: str = Field(default="quadcopter_medium")
    grid_resolution_km: float = Field(default=0.5, ge=0.1, le=5.0)
    altitude_levels: list[float] = Field(default=[50, 100, 150, 200])


class OptimizeResponse(BaseModel):
    status: str
    route: dict
    geojson: dict
    drone_profile: dict


@router.post("/optimize", response_model=OptimizeResponse)
async def optimize_route(request: OptimizeRequest):
    """Calculate energy-optimized 3D flight route between two points."""
    try:
        profile = get_profile(request.drone_profile)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    start = (request.start_lat, request.start_lon, request.start_alt)
    end = (request.end_lat, request.end_lon, request.end_alt)

    dist_km = _haversine_km(start[0], start[1], end[0], end[1])
    if dist_km > 50:
        raise HTTPException(status_code=400, detail="Route distance exceeds 50km maximum")
    if dist_km < 0.01:
        raise HTTPException(status_code=400, detail="Start and end points are too close")

    builder = GraphBuilder(profile)
    graph = builder.build_graph(
        start=start,
        end=end,
        grid_resolution_km=request.grid_resolution_km,
        altitude_levels=request.altitude_levels,
    )

    start_id = builder._node_id(*start)
    end_id = builder._node_id(*end)

    try:
        result = a_star_3d(graph, start_id, end_id, profile.battery_capacity_wh)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    geojson = _to_geojson(result)

    return OptimizeResponse(
        status="success",
        route=result,
        geojson=geojson,
        drone_profile={
            "id": request.drone_profile,
            "name": profile.name,
            "mass_kg": profile.mass_kg,
            "battery_capacity_wh": profile.battery_capacity_wh,
        },
    )


@router.get("/profiles")
async def get_profiles():
    """List available drone profiles."""
    return {"profiles": list_profiles()}


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "routing-engine"}


def _to_geojson(result: dict) -> dict:
    coordinates = [
        [wp["lon"], wp["lat"], wp["alt"]]
        for wp in result["waypoints"]
    ]

    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": coordinates,
                },
                "properties": {
                    "total_energy_j": result["total_energy_j"],
                    "total_distance_m": result["total_distance_m"],
                    "total_duration_s": result["total_duration_s"],
                    "battery_used_pct": result["battery_used_pct"],
                },
            },
            *[
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [wp["lon"], wp["lat"], wp["alt"]],
                    },
                    "properties": {
                        "battery_pct": wp["battery_pct"],
                        "cumulative_energy_j": wp["cumulative_energy_j"],
                    },
                }
                for wp in result["waypoints"]
            ],
        ],
    }


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
