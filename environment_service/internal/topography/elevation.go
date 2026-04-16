package topography

import (
	"math"
	"sync"
)

// ElevationPoint represents elevation at a geographic coordinate.
type ElevationPoint struct {
	Lat       float64 `json:"lat"`
	Lon       float64 `json:"lon"`
	Elevation float64 `json:"elevation_m"`
	Slope     float64 `json:"slope_deg"`
}

// ElevationGrid contains the elevation data response.
type ElevationGrid struct {
	CenterLat    float64          `json:"center_lat"`
	CenterLon    float64          `json:"center_lon"`
	RadiusKm     float64          `json:"radius_km"`
	ResolutionM  float64          `json:"resolution_m"`
	Points       []ElevationPoint `json:"points"`
	MinElevation float64          `json:"min_elevation_m"`
	MaxElevation float64          `json:"max_elevation_m"`
}

// ElevationService provides elevation data from terrain tiles.
type ElevationService struct {
	mu    sync.RWMutex
	cache map[string]*ElevationGrid
}

// NewElevationService creates a new elevation service.
func NewElevationService() *ElevationService {
	return &ElevationService{
		cache: make(map[string]*ElevationGrid),
	}
}

// GetElevationGrid generates an elevation grid around the given coordinates.
// In production, this would parse GeoTIFF/SRTM tiles.
func (s *ElevationService) GetElevationGrid(lat, lon, radiusKm, resolutionM float64) *ElevationGrid {
	s.mu.Lock()
	defer s.mu.Unlock()

	stepDeg := resolutionM / 111000.0
	radiusDeg := radiusKm / 111.0

	var points []ElevationPoint
	minElev := math.MaxFloat64
	maxElev := -math.MaxFloat64

	for dLat := -radiusDeg; dLat <= radiusDeg; dLat += stepDeg {
		for dLon := -radiusDeg; dLon <= radiusDeg; dLon += stepDeg {
			ptLat := lat + dLat
			ptLon := lon + dLon

			dist := math.Sqrt(dLat*dLat + dLon*dLon)
			if dist > radiusDeg {
				continue
			}

			elevation := generateElevation(ptLat, ptLon)
			slope := calculateSlope(ptLat, ptLon)

			if elevation < minElev {
				minElev = elevation
			}
			if elevation > maxElev {
				maxElev = elevation
			}

			points = append(points, ElevationPoint{
				Lat:       math.Round(ptLat*1e6) / 1e6,
				Lon:       math.Round(ptLon*1e6) / 1e6,
				Elevation: math.Round(elevation*10) / 10,
				Slope:     math.Round(slope*10) / 10,
			})
		}
	}

	return &ElevationGrid{
		CenterLat:    lat,
		CenterLon:    lon,
		RadiusKm:     radiusKm,
		ResolutionM:  resolutionM,
		Points:       points,
		MinElevation: math.Round(minElev*10) / 10,
		MaxElevation: math.Round(maxElev*10) / 10,
	}
}

// generateElevation uses a deterministic procedural function to simulate terrain.
func generateElevation(lat, lon float64) float64 {
	base := 200.0
	val := base +
		80.0*math.Sin(lat*50.0)*math.Cos(lon*50.0) +
		40.0*math.Sin(lat*150.0+lon*100.0) +
		20.0*math.Cos(lat*300.0)*math.Sin(lon*200.0)
	if val < 0 {
		val = 0
	}
	return val
}

// calculateSlope estimates slope at a coordinate using finite differences.
func calculateSlope(lat, lon float64) float64 {
	delta := 0.0001
	e1 := generateElevation(lat+delta, lon)
	e2 := generateElevation(lat-delta, lon)
	e3 := generateElevation(lat, lon+delta)
	e4 := generateElevation(lat, lon-delta)

	dEdLat := (e1 - e2) / (2.0 * delta * 111000.0)
	dEdLon := (e3 - e4) / (2.0 * delta * 111000.0 * math.Cos(lat*math.Pi/180.0))

	slopeRad := math.Atan(math.Sqrt(dEdLat*dEdLat + dEdLon*dEdLon))
	return slopeRad * 180.0 / math.Pi
}
