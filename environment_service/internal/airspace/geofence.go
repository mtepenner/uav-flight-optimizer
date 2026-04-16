package airspace

import (
	"math"
	"sync"
	"time"
)

// Geofence represents a no-fly zone or temporary flight restriction.
type Geofence struct {
	ID          string      `json:"id"`
	Type        string      `json:"type"`
	Name        string      `json:"name"`
	CenterLat   float64     `json:"center_lat"`
	CenterLon   float64     `json:"center_lon"`
	RadiusM     float64     `json:"radius_m"`
	FloorAltM   float64     `json:"floor_alt_m"`
	CeilingAltM float64     `json:"ceiling_alt_m"`
	Active      bool        `json:"active"`
	ExpiresAt   string      `json:"expires_at,omitempty"`
	Polygon     [][]float64 `json:"polygon,omitempty"`
}

// GeofenceResponse contains geofences within a search area.
type GeofenceResponse struct {
	CenterLat  float64    `json:"center_lat"`
	CenterLon  float64    `json:"center_lon"`
	RadiusKm   float64    `json:"radius_km"`
	Geofences  []Geofence `json:"geofences"`
	TotalCount int        `json:"total_count"`
}

// GeofenceService provides airspace restriction data.
type GeofenceService struct {
	mu    sync.RWMutex
	zones []Geofence
}

// NewGeofenceService creates a new geofence service with preloaded data.
// In production, this would cache FAA no-fly zones and TFRs.
func NewGeofenceService() *GeofenceService {
	s := &GeofenceService{}
	s.loadStaticZones()
	return s
}

func (s *GeofenceService) loadStaticZones() {
	s.zones = []Geofence{
		{
			ID:          "NFZ-001",
			Type:        "NO_FLY_ZONE",
			Name:        "Washington DC FRZ",
			CenterLat:   38.8977,
			CenterLon:   -77.0365,
			RadiusM:     25000,
			FloorAltM:   0,
			CeilingAltM: 5500,
			Active:      true,
		},
		{
			ID:          "NFZ-002",
			Type:        "NO_FLY_ZONE",
			Name:        "JFK Airport Class B",
			CenterLat:   40.6413,
			CenterLon:   -73.7781,
			RadiusM:     9260,
			FloorAltM:   0,
			CeilingAltM: 2134,
			Active:      true,
		},
		{
			ID:          "NFZ-003",
			Type:        "NO_FLY_ZONE",
			Name:        "LAX Airport Class B",
			CenterLat:   33.9425,
			CenterLon:   -118.4081,
			RadiusM:     9260,
			FloorAltM:   0,
			CeilingAltM: 3658,
			Active:      true,
		},
		{
			ID:          "TFR-001",
			Type:        "TFR",
			Name:        "Wildfire Temporary Restriction",
			CenterLat:   34.0522,
			CenterLon:   -118.2437,
			RadiusM:     5000,
			FloorAltM:   0,
			CeilingAltM: 1000,
			Active:      true,
			ExpiresAt:   time.Now().Add(48 * time.Hour).UTC().Format(time.RFC3339),
		},
		{
			ID:          "TFR-002",
			Type:        "TFR",
			Name:        "Stadium Event Restriction",
			CenterLat:   40.7580,
			CenterLon:   -73.9855,
			RadiusM:     3000,
			FloorAltM:   0,
			CeilingAltM: 915,
			Active:      true,
			ExpiresAt:   time.Now().Add(6 * time.Hour).UTC().Format(time.RFC3339),
		},
		{
			ID:          "NFZ-004",
			Type:        "NO_FLY_ZONE",
			Name:        "SFO Airport Class B",
			CenterLat:   37.6213,
			CenterLon:   -122.3790,
			RadiusM:     9260,
			FloorAltM:   0,
			CeilingAltM: 2438,
			Active:      true,
		},
	}
}

// GetGeofences returns all geofences within the given search radius.
func (s *GeofenceService) GetGeofences(lat, lon, radiusKm float64) *GeofenceResponse {
	s.mu.RLock()
	defer s.mu.RUnlock()

	var matched []Geofence
	for _, zone := range s.zones {
		dist := haversineKm(lat, lon, zone.CenterLat, zone.CenterLon)
		if dist <= radiusKm+(zone.RadiusM/1000.0) {
			matched = append(matched, zone)
		}
	}

	return &GeofenceResponse{
		CenterLat:  lat,
		CenterLon:  lon,
		RadiusKm:   radiusKm,
		Geofences:  matched,
		TotalCount: len(matched),
	}
}

func haversineKm(lat1, lon1, lat2, lon2 float64) float64 {
	const earthRadiusKm = 6371.0
	dLat := (lat2 - lat1) * math.Pi / 180.0
	dLon := (lon2 - lon1) * math.Pi / 180.0
	lat1Rad := lat1 * math.Pi / 180.0
	lat2Rad := lat2 * math.Pi / 180.0

	a := math.Sin(dLat/2)*math.Sin(dLat/2) +
		math.Cos(lat1Rad)*math.Cos(lat2Rad)*math.Sin(dLon/2)*math.Sin(dLon/2)
	c := 2 * math.Atan2(math.Sqrt(a), math.Sqrt(1-a))
	return earthRadiusKm * c
}
