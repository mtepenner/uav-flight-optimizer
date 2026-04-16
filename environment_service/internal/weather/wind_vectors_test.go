package weather

import (
	"testing"
)

func TestNewWindVectorService(t *testing.T) {
	svc := NewWindVectorService()
	if svc == nil {
		t.Fatal("expected non-nil service")
	}
}

func TestGetWindGrid(t *testing.T) {
	svc := NewWindVectorService()
	grid := svc.GetWindGrid(40.7128, -74.0060, 150.0, 5.0)

	if grid == nil {
		t.Fatal("expected non-nil grid")
	}
	if grid.CenterLat != 40.7128 {
		t.Errorf("expected center lat 40.7128, got %f", grid.CenterLat)
	}
	if grid.CenterLon != -74.0060 {
		t.Errorf("expected center lon -74.0060, got %f", grid.CenterLon)
	}
	if len(grid.Vectors) == 0 {
		t.Error("expected non-empty vectors")
	}

	for _, v := range grid.Vectors {
		if v.SpeedMS < 0 {
			t.Errorf("wind speed should be non-negative, got %f", v.SpeedMS)
		}
		if v.Direction < 0 || v.Direction >= 360 {
			t.Errorf("direction should be [0,360), got %f", v.Direction)
		}
	}
}

func TestGetWindGridSmallRadius(t *testing.T) {
	svc := NewWindVectorService()
	grid := svc.GetWindGrid(34.0522, -118.2437, 100.0, 1.0)

	if grid == nil {
		t.Fatal("expected non-nil grid")
	}
	if len(grid.Vectors) == 0 {
		t.Error("expected non-empty vectors for small radius")
	}
}
