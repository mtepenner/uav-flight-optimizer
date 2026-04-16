package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"

	"github.com/gorilla/mux"
	"github.com/mtepenner/uav-flight-optimizer/environment_service/internal/airspace"
	"github.com/mtepenner/uav-flight-optimizer/environment_service/internal/topography"
	"github.com/mtepenner/uav-flight-optimizer/environment_service/internal/weather"
)

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8081"
	}

	windService := weather.NewWindVectorService()
	elevationService := topography.NewElevationService()
	geofenceService := airspace.NewGeofenceService()

	r := mux.NewRouter()

	// Health check
	r.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]string{"status": "healthy"})
	}).Methods("GET")

	// Wind vectors endpoint
	r.HandleFunc("/api/v1/wind", func(w http.ResponseWriter, r *http.Request) {
		lat, _ := strconv.ParseFloat(r.URL.Query().Get("lat"), 64)
		lon, _ := strconv.ParseFloat(r.URL.Query().Get("lon"), 64)
		alt, _ := strconv.ParseFloat(r.URL.Query().Get("alt"), 64)
		radius, _ := strconv.ParseFloat(r.URL.Query().Get("radius"), 64)
		if radius == 0 {
			radius = 10.0
		}

		grid := windService.GetWindGrid(lat, lon, alt, radius)
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(grid)
	}).Methods("GET")

	// Elevation endpoint
	r.HandleFunc("/api/v1/elevation", func(w http.ResponseWriter, r *http.Request) {
		lat, _ := strconv.ParseFloat(r.URL.Query().Get("lat"), 64)
		lon, _ := strconv.ParseFloat(r.URL.Query().Get("lon"), 64)
		radius, _ := strconv.ParseFloat(r.URL.Query().Get("radius"), 64)
		resolution, _ := strconv.ParseFloat(r.URL.Query().Get("resolution"), 64)
		if resolution == 0 {
			resolution = 30.0
		}
		if radius == 0 {
			radius = 10.0
		}

		grid := elevationService.GetElevationGrid(lat, lon, radius, resolution)
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(grid)
	}).Methods("GET")

	// Geofence endpoint
	r.HandleFunc("/api/v1/geofences", func(w http.ResponseWriter, r *http.Request) {
		lat, _ := strconv.ParseFloat(r.URL.Query().Get("lat"), 64)
		lon, _ := strconv.ParseFloat(r.URL.Query().Get("lon"), 64)
		radius, _ := strconv.ParseFloat(r.URL.Query().Get("radius"), 64)
		if radius == 0 {
			radius = 50.0
		}

		zones := geofenceService.GetGeofences(lat, lon, radius)
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(zones)
	}).Methods("GET")

	// Combined environment data for a bounding box
	r.HandleFunc("/api/v1/environment", func(w http.ResponseWriter, r *http.Request) {
		lat, _ := strconv.ParseFloat(r.URL.Query().Get("lat"), 64)
		lon, _ := strconv.ParseFloat(r.URL.Query().Get("lon"), 64)
		alt, _ := strconv.ParseFloat(r.URL.Query().Get("alt"), 64)
		radius, _ := strconv.ParseFloat(r.URL.Query().Get("radius"), 64)
		if radius == 0 {
			radius = 10.0
		}
		if alt == 0 {
			alt = 100.0
		}

		result := map[string]interface{}{
			"wind_grid":      windService.GetWindGrid(lat, lon, alt, radius),
			"elevation_grid": elevationService.GetElevationGrid(lat, lon, radius, 30.0),
			"geofences":      geofenceService.GetGeofences(lat, lon, radius),
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(result)
	}).Methods("GET")

	// CORS middleware
	handler := corsMiddleware(r)

	log.Printf("Environment Service starting on port %s", port)
	if err := http.ListenAndServe(fmt.Sprintf(":%s", port), handler); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}

func corsMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
		if r.Method == "OPTIONS" {
			w.WriteHeader(http.StatusOK)
			return
		}
		next.ServeHTTP(w, r)
	})
}
