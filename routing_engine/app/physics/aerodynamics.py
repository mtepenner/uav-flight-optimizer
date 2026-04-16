"""Aerodynamic drag force calculations based on airspeed and wind vectors."""

import math
from dataclasses import dataclass


AIR_DENSITY_KG_M3 = 1.225


@dataclass
class WindVector:
    vx: float = 0.0
    vy: float = 0.0
    vz: float = 0.0


def calculate_drag_force(
    airspeed_ms: float,
    frontal_area_m2: float,
    drag_coefficient: float,
    air_density: float = AIR_DENSITY_KG_M3,
) -> float:
    """Calculate aerodynamic drag force using the drag equation: F = 0.5 * rho * v^2 * Cd * A."""
    return 0.5 * air_density * airspeed_ms**2 * drag_coefficient * frontal_area_m2


def calculate_effective_airspeed(
    ground_speed_ms: float,
    heading_rad: float,
    wind: WindVector,
) -> float:
    """Calculate the effective airspeed by subtracting wind component along flight path."""
    drone_vx = ground_speed_ms * math.sin(heading_rad)
    drone_vy = ground_speed_ms * math.cos(heading_rad)

    relative_vx = drone_vx - wind.vx
    relative_vy = drone_vy - wind.vy
    relative_vz = -wind.vz

    return math.sqrt(relative_vx**2 + relative_vy**2 + relative_vz**2)


def calculate_heading(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate bearing between two geographic points in radians."""
    lat1_r = math.radians(lat1)
    lat2_r = math.radians(lat2)
    dlon = math.radians(lon2 - lon1)

    x = math.sin(dlon) * math.cos(lat2_r)
    y = math.cos(lat1_r) * math.sin(lat2_r) - math.sin(lat1_r) * math.cos(lat2_r) * math.cos(dlon)

    return math.atan2(x, y)


def calculate_thrust_required(
    drag_force_n: float,
    mass_kg: float,
    climb_angle_rad: float,
) -> float:
    """Calculate total thrust required to maintain flight including climb/descent."""
    gravity_component = mass_kg * 9.81 * math.sin(climb_angle_rad)
    hover_component = mass_kg * 9.81 * math.cos(climb_angle_rad)
    return drag_force_n + gravity_component + hover_component
