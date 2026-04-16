package weather

import (
	"math"
	"math/rand"
	"sync"
	"time"
)

// WindVector represents a 3D wind vector at a specific point in space.
type WindVector struct {
	Lat       float64 `json:"lat"`
	Lon       float64 `json:"lon"`
	Alt       float64 `json:"alt"`
	SpeedMS   float64 `json:"speed_ms"`
	Direction float64 `json:"direction_deg"`
	Vx        float64 `json:"vx"`
	Vy        float64 `json:"vy"`
	Vz        float64 `json:"vz"`
}

// WindGrid holds the full 3D wind grid response.
type WindGrid struct {
	CenterLat float64      `json:"center_lat"`
	CenterLon float64      `json:"center_lon"`
	RadiusKm  float64      `json:"radius_km"`
	Timestamp string       `json:"timestamp"`
	Vectors   []WindVector `json:"vectors"`
}

// WindVectorService provides 3D wind vector grids.
type WindVectorService struct {
	mu    sync.RWMutex
	cache map[string]*WindGrid
	rng   *rand.Rand
}

// NewWindVectorService creates a new wind vector service.
func NewWindVectorService() *WindVectorService {
	return &WindVectorService{
		cache: make(map[string]*WindGrid),
		rng:   rand.New(rand.NewSource(time.Now().UnixNano())),
	}
}

// GetWindGrid generates a 3D wind vector grid around the given coordinates.
// In production, this would poll NOAA/OpenWeather APIs.
func (s *WindVectorService) GetWindGrid(lat, lon, alt, radiusKm float64) *WindGrid {
	s.mu.Lock()
	defer s.mu.Unlock()

	altLevels := []float64{50, 100, 150, 200, 300}
	gridStep := radiusKm / 3.0
	if gridStep < 0.5 {
		gridStep = 0.5
	}

	var vectors []WindVector

	for _, altLevel := range altLevels {
		if altLevel > alt+200 {
			break
		}
		for dLat := -radiusKm; dLat <= radiusKm; dLat += gridStep {
			for dLon := -radiusKm; dLon <= radiusKm; dLon += gridStep {
				dist := math.Sqrt(dLat*dLat + dLon*dLon)
				if dist > radiusKm {
					continue
				}

				ptLat := lat + dLat/111.0
				ptLon := lon + dLon/(111.0*math.Cos(lat*math.Pi/180.0))

				baseSpeed := 3.0 + altLevel*0.02
				speed := baseSpeed + s.rng.Float64()*4.0 - 2.0
				if speed < 0 {
					speed = 0.5
				}

				direction := math.Mod(220.0+s.rng.Float64()*40.0-20.0, 360.0)
				dirRad := direction * math.Pi / 180.0

				vectors = append(vectors, WindVector{
					Lat:       ptLat,
					Lon:       ptLon,
					Alt:       altLevel,
					SpeedMS:   math.Round(speed*100) / 100,
					Direction: math.Round(direction*10) / 10,
					Vx:        math.Round(speed*math.Sin(dirRad)*100) / 100,
					Vy:        math.Round(speed*math.Cos(dirRad)*100) / 100,
					Vz:        math.Round((s.rng.Float64()*0.6-0.3)*100) / 100,
				})
			}
		}
	}

	return &WindGrid{
		CenterLat: lat,
		CenterLon: lon,
		RadiusKm:  radiusKm,
		Timestamp: time.Now().UTC().Format(time.RFC3339),
		Vectors:   vectors,
	}
}
