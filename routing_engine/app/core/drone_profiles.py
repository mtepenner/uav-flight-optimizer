"""Drone aerodynamic profiles for energy modeling."""

from dataclasses import dataclass


@dataclass
class DroneProfile:
    name: str
    mass_kg: float
    frontal_area_m2: float
    drag_coefficient: float
    battery_capacity_wh: float
    max_speed_ms: float
    hover_power_w: float
    motor_efficiency: float = 0.85
    propulsive_efficiency: float = 0.75


DRONE_PROFILES = {
    "quadcopter_small": DroneProfile(
        name="Small Quadcopter",
        mass_kg=1.5,
        frontal_area_m2=0.03,
        drag_coefficient=1.2,
        battery_capacity_wh=80,
        max_speed_ms=15.0,
        hover_power_w=120,
    ),
    "quadcopter_medium": DroneProfile(
        name="Medium Quadcopter",
        mass_kg=4.0,
        frontal_area_m2=0.06,
        drag_coefficient=1.1,
        battery_capacity_wh=250,
        max_speed_ms=18.0,
        hover_power_w=280,
    ),
    "quadcopter_heavy": DroneProfile(
        name="Heavy Lift Quadcopter",
        mass_kg=12.0,
        frontal_area_m2=0.12,
        drag_coefficient=1.0,
        battery_capacity_wh=800,
        max_speed_ms=14.0,
        hover_power_w=750,
    ),
    "fixed_wing": DroneProfile(
        name="Fixed Wing",
        mass_kg=3.0,
        frontal_area_m2=0.04,
        drag_coefficient=0.3,
        battery_capacity_wh=300,
        max_speed_ms=25.0,
        hover_power_w=0,
        motor_efficiency=0.90,
        propulsive_efficiency=0.80,
    ),
}


def get_profile(profile_id: str) -> DroneProfile:
    if profile_id not in DRONE_PROFILES:
        raise ValueError(f"Unknown drone profile: {profile_id}. Available: {list(DRONE_PROFILES.keys())}")
    return DRONE_PROFILES[profile_id]


def list_profiles() -> list[dict]:
    return [
        {
            "id": pid,
            "name": p.name,
            "mass_kg": p.mass_kg,
            "battery_capacity_wh": p.battery_capacity_wh,
            "max_speed_ms": p.max_speed_ms,
        }
        for pid, p in DRONE_PROFILES.items()
    ]
