package airspace

import (
	"testing"
)

func TestNewGeofenceService(t *testing.T) {
	svc := NewGeofenceService()
	if svc == nil {
		t.Fatal("expected non-nil service")
	}
}

func TestGetGeofencesNearDC(t *testing.T) {
	svc := NewGeofenceService()
	resp := svc.GetGeofences(38.9, -77.0, 50.0)

	if resp == nil {
		t.Fatal("expected non-nil response")
	}
	if resp.TotalCount == 0 {
		t.Error("expected geofences near Washington DC")
	}

	foundDC := false
	for _, g := range resp.Geofences {
		if g.ID == "NFZ-001" {
			foundDC = true
			if !g.Active {
				t.Error("DC FRZ should be active")
			}
		}
	}
	if !foundDC {
		t.Error("expected to find DC FRZ geofence")
	}
}

func TestGetGeofencesRemoteArea(t *testing.T) {
	svc := NewGeofenceService()
	resp := svc.GetGeofences(0.0, 0.0, 10.0)

	if resp == nil {
		t.Fatal("expected non-nil response")
	}
	if resp.TotalCount != 0 {
		t.Errorf("expected no geofences at 0,0 with small radius, got %d", resp.TotalCount)
	}
}

func TestHaversineKm(t *testing.T) {
	dist := haversineKm(40.7128, -74.0060, 40.7128, -74.0060)
	if dist != 0 {
		t.Errorf("distance from point to itself should be 0, got %f", dist)
	}

	dist = haversineKm(40.7128, -74.0060, 34.0522, -118.2437)
	if dist < 3900 || dist > 4000 {
		t.Errorf("NYC to LA should be ~3944km, got %f", dist)
	}
}
