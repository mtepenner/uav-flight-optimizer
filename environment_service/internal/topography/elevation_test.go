package topography

import (
	"testing"
)

func TestNewElevationService(t *testing.T) {
	svc := NewElevationService()
	if svc == nil {
		t.Fatal("expected non-nil service")
	}
}

func TestGetElevationGrid(t *testing.T) {
	svc := NewElevationService()
	grid := svc.GetElevationGrid(40.7128, -74.0060, 1.0, 100.0)

	if grid == nil {
		t.Fatal("expected non-nil grid")
	}
	if grid.CenterLat != 40.7128 {
		t.Errorf("expected center lat 40.7128, got %f", grid.CenterLat)
	}
	if len(grid.Points) == 0 {
		t.Error("expected non-empty elevation points")
	}
	if grid.MinElevation > grid.MaxElevation {
		t.Errorf("min elevation %f > max elevation %f", grid.MinElevation, grid.MaxElevation)
	}

	for _, p := range grid.Points {
		if p.Elevation < 0 {
			t.Errorf("elevation should be non-negative, got %f", p.Elevation)
		}
		if p.Slope < 0 {
			t.Errorf("slope should be non-negative, got %f", p.Slope)
		}
	}
}

func TestGenerateElevation(t *testing.T) {
	e1 := generateElevation(40.0, -74.0)
	e2 := generateElevation(40.0, -74.0)
	if e1 != e2 {
		t.Error("elevation should be deterministic for same coordinates")
	}
	if e1 < 0 {
		t.Errorf("elevation should be non-negative, got %f", e1)
	}
}

func TestCalculateSlope(t *testing.T) {
	slope := calculateSlope(40.0, -74.0)
	if slope < 0 || slope > 90 {
		t.Errorf("slope should be [0,90] degrees, got %f", slope)
	}
}
