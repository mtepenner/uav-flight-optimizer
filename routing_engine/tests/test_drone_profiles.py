"""Tests for drone profiles."""

import pytest
from app.core.drone_profiles import get_profile, list_profiles, DRONE_PROFILES


def test_get_known_profile():
    profile = get_profile("quadcopter_medium")
    assert profile.name == "Medium Quadcopter"
    assert profile.mass_kg == 4.0


def test_get_unknown_profile():
    with pytest.raises(ValueError, match="Unknown drone profile"):
        get_profile("nonexistent")


def test_list_profiles():
    profiles = list_profiles()
    assert len(profiles) == len(DRONE_PROFILES)
    for p in profiles:
        assert "id" in p
        assert "name" in p
        assert "mass_kg" in p


def test_all_profiles_valid():
    for pid, profile in DRONE_PROFILES.items():
        assert profile.mass_kg > 0
        assert profile.frontal_area_m2 > 0
        assert profile.battery_capacity_wh > 0
        assert profile.max_speed_ms > 0
        assert 0 < profile.motor_efficiency <= 1.0
        assert 0 < profile.propulsive_efficiency <= 1.0
