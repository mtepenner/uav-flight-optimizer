"""Tests for aerodynamics module."""

import math
import pytest
from app.physics.aerodynamics import (
    calculate_drag_force,
    calculate_effective_airspeed,
    calculate_heading,
    calculate_thrust_required,
    WindVector,
)


def test_drag_force_zero_speed():
    force = calculate_drag_force(0.0, 0.05, 1.0)
    assert force == 0.0


def test_drag_force_increases_with_speed():
    f1 = calculate_drag_force(5.0, 0.05, 1.0)
    f2 = calculate_drag_force(10.0, 0.05, 1.0)
    assert f2 > f1


def test_drag_force_quadratic():
    f1 = calculate_drag_force(10.0, 0.05, 1.0)
    f2 = calculate_drag_force(20.0, 0.05, 1.0)
    assert abs(f2 / f1 - 4.0) < 0.01


def test_effective_airspeed_no_wind():
    airspeed = calculate_effective_airspeed(10.0, 0.0, WindVector())
    assert abs(airspeed - 10.0) < 0.01


def test_effective_airspeed_headwind():
    airspeed = calculate_effective_airspeed(10.0, 0.0, WindVector(vx=0, vy=-5, vz=0))
    assert airspeed > 10.0


def test_effective_airspeed_tailwind():
    airspeed = calculate_effective_airspeed(10.0, 0.0, WindVector(vx=0, vy=5, vz=0))
    assert airspeed < 10.0


def test_heading_north():
    heading = calculate_heading(40.0, -74.0, 41.0, -74.0)
    assert abs(heading) < 0.01


def test_heading_east():
    heading = calculate_heading(40.0, -74.0, 40.0, -73.0)
    assert abs(heading - math.pi / 2) < 0.1


def test_thrust_level_flight():
    thrust = calculate_thrust_required(5.0, 2.0, 0.0)
    assert thrust > 0


def test_thrust_increases_with_climb():
    t_level = calculate_thrust_required(5.0, 2.0, 0.0)
    t_climb = calculate_thrust_required(5.0, 2.0, math.radians(15))
    assert t_climb > t_level
