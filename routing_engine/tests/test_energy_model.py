"""Tests for energy model module."""

import pytest
from app.physics.energy_model import (
    calculate_segment_energy,
    estimate_battery_usage,
    haversine_m,
)
from app.core.drone_profiles import get_profile


def test_haversine_same_point():
    dist = haversine_m(40.0, -74.0, 40.0, -74.0)
    assert dist == 0.0


def test_haversine_known_distance():
    dist = haversine_m(40.7128, -74.0060, 34.0522, -118.2437)
    assert 3900_000 < dist < 4000_000


def test_segment_energy_zero_distance():
    profile = get_profile("quadcopter_medium")
    result = calculate_segment_energy(40.0, -74.0, 100.0, 40.0, -74.0, 100.0, profile)
    assert result["energy_j"] == 0.0
    assert result["distance_m"] == 0.0


def test_segment_energy_positive():
    profile = get_profile("quadcopter_medium")
    result = calculate_segment_energy(40.7, -74.0, 100.0, 40.71, -74.0, 100.0, profile)
    assert result["energy_j"] > 0
    assert result["distance_m"] > 0
    assert result["duration_s"] > 0
    assert result["power_w"] > 0


def test_segment_energy_climb_costs_more():
    profile = get_profile("quadcopter_medium")
    level = calculate_segment_energy(40.7, -74.0, 100.0, 40.71, -74.0, 100.0, profile)
    climb = calculate_segment_energy(40.7, -74.0, 100.0, 40.71, -74.0, 200.0, profile)
    assert climb["energy_j"] > level["energy_j"]


def test_battery_usage():
    usage = estimate_battery_usage(360000, 250)
    assert abs(usage - 40.0) < 0.01


def test_battery_usage_full():
    usage = estimate_battery_usage(900000, 250)
    assert usage == 100.0


def test_battery_usage_zero():
    usage = estimate_battery_usage(0, 250)
    assert usage == 0.0
