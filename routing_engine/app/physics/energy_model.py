"""Energy consumption model for UAV flight segments."""

import math
from ..core.drone_profiles import DroneProfile
from .aerodynamics import (
    WindVector,
    calculate_drag_force,
    calculate_effective_airspeed,
    calculate_heading,
    calculate_thrust_required,
)


def calculate_segment_energy(
    lat1: float, lon1: float, alt1: float,
    lat2: float, lon2: float, alt2: float,
    profile: DroneProfile,
    wind: WindVector | None = None,
    ground_speed_ms: float | None = None,
) -> dict:
    """Calculate energy consumed traversing a 3D flight segment.

    Returns dict with energy_j, power_w, duration_s, and distance_m.
    """
    if wind is None:
        wind = WindVector()
    if ground_speed_ms is None:
        ground_speed_ms = profile.max_speed_ms * 0.7

    distance_horizontal = haversine_m(lat1, lon1, lat2, lon2)
    distance_vertical = alt2 - alt1
    distance_3d = math.sqrt(distance_horizontal**2 + distance_vertical**2)

    if distance_3d < 0.01:
        return {"energy_j": 0.0, "power_w": profile.hover_power_w, "duration_s": 0.0, "distance_m": 0.0}

    climb_angle = math.atan2(distance_vertical, distance_horizontal)
    heading = calculate_heading(lat1, lon1, lat2, lon2)

    airspeed = calculate_effective_airspeed(ground_speed_ms, heading, wind)
    airspeed = max(airspeed, 1.0)

    drag = calculate_drag_force(airspeed, profile.frontal_area_m2, profile.drag_coefficient)
    thrust = calculate_thrust_required(drag, profile.mass_kg, climb_angle)

    power_propulsion = thrust * airspeed / profile.propulsive_efficiency
    power_total = power_propulsion / profile.motor_efficiency + profile.hover_power_w * 0.3

    duration_s = distance_3d / ground_speed_ms
    energy_j = power_total * duration_s

    return {
        "energy_j": round(energy_j, 2),
        "power_w": round(power_total, 2),
        "duration_s": round(duration_s, 2),
        "distance_m": round(distance_3d, 2),
    }


def estimate_battery_usage(energy_j: float, battery_capacity_wh: float) -> float:
    """Return battery usage as a percentage (0-100)."""
    battery_capacity_j = battery_capacity_wh * 3600
    if battery_capacity_j == 0:
        return 100.0
    return min(100.0, round((energy_j / battery_capacity_j) * 100, 2))


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in meters between two geographic points."""
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c
