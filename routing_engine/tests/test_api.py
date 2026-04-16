"""Tests for the FastAPI routes."""

import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_root():
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert "service" in data


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


def test_get_profiles():
    resp = client.get("/api/v1/profiles")
    assert resp.status_code == 200
    data = resp.json()
    assert "profiles" in data
    assert len(data["profiles"]) > 0


def test_optimize_route():
    resp = client.post("/api/v1/optimize", json={
        "start_lat": 40.70,
        "start_lon": -74.00,
        "end_lat": 40.71,
        "end_lon": -74.00,
        "start_alt": 100,
        "end_alt": 100,
        "drone_profile": "quadcopter_medium",
        "grid_resolution_km": 0.5,
        "altitude_levels": [100],
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "route" in data
    assert "geojson" in data
    assert data["geojson"]["type"] == "FeatureCollection"


def test_optimize_invalid_profile():
    resp = client.post("/api/v1/optimize", json={
        "start_lat": 40.70,
        "start_lon": -74.00,
        "end_lat": 40.71,
        "end_lon": -74.00,
        "drone_profile": "nonexistent",
    })
    assert resp.status_code == 400


def test_optimize_too_far():
    resp = client.post("/api/v1/optimize", json={
        "start_lat": 40.70,
        "start_lon": -74.00,
        "end_lat": 41.70,
        "end_lon": -74.00,
    })
    assert resp.status_code == 400


def test_optimize_same_point():
    resp = client.post("/api/v1/optimize", json={
        "start_lat": 40.70,
        "start_lon": -74.00,
        "end_lat": 40.70,
        "end_lon": -74.00,
    })
    assert resp.status_code == 400
