import { useState, useEffect, useCallback } from 'react';

interface DroneProfileSummary {
  id: string;
  name: string;
  mass_kg: number;
  battery_capacity_wh: number;
  max_speed_ms: number;
}

interface RouteResult {
  waypoints: Array<{
    lat: number;
    lon: number;
    alt: number;
    cumulative_energy_j: number;
    segment_power_w: number;
    battery_pct: number;
  }>;
  total_energy_j: number;
  total_distance_m: number;
  total_duration_s: number;
  battery_used_pct: number;
  battery_remaining_pct: number;
  battery_curve: Array<{
    distance_m: number;
    battery_pct: number;
    altitude_m: number;
  }>;
  node_count: number;
}

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const DEFAULT_PROFILES: DroneProfileSummary[] = [
  { id: 'quadcopter_small', name: 'Small Quadcopter', mass_kg: 1.5, battery_capacity_wh: 80, max_speed_ms: 15 },
  { id: 'quadcopter_medium', name: 'Medium Quadcopter', mass_kg: 4.0, battery_capacity_wh: 250, max_speed_ms: 18 },
  { id: 'quadcopter_heavy', name: 'Heavy Lift Quadcopter', mass_kg: 12.0, battery_capacity_wh: 800, max_speed_ms: 14 },
  { id: 'fixed_wing', name: 'Fixed Wing', mass_kg: 3.0, battery_capacity_wh: 300, max_speed_ms: 25 },
];

export function useFlightPlanner() {
  const [startPoint, setStartPoint] = useState<[number, number] | null>(null);
  const [endPoint, setEndPoint] = useState<[number, number] | null>(null);
  const [droneProfile, setDroneProfile] = useState('quadcopter_medium');
  const [profiles, setProfiles] = useState<DroneProfileSummary[]>(DEFAULT_PROFILES);
  const [route, setRoute] = useState<RouteResult | null>(null);
  const [geojson, setGeojson] = useState<GeoJSON.FeatureCollection | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/api/v1/profiles`)
      .then((r) => r.json())
      .then((data) => {
        if (data.profiles && data.profiles.length > 0) {
          setProfiles(data.profiles);
        }
      })
      .catch(() => {
        // Use defaults if API unavailable
      });
  }, []);

  const optimizeRoute = useCallback(async () => {
    if (!startPoint || !endPoint) {
      setError('Please set both start and end points');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/api/v1/optimize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          start_lat: startPoint[1],
          start_lon: startPoint[0],
          end_lat: endPoint[1],
          end_lon: endPoint[0],
          start_alt: 100,
          end_alt: 100,
          drone_profile: droneProfile,
          grid_resolution_km: 0.5,
          altitude_levels: [50, 100, 150, 200],
        }),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Optimization failed');
      }

      const data = await response.json();
      setRoute(data.route);
      setGeojson(data.geojson);
    } catch (err: any) {
      setError(err.message || 'Failed to optimize route');
    } finally {
      setLoading(false);
    }
  }, [startPoint, endPoint, droneProfile]);

  return {
    startPoint,
    endPoint,
    setStartPoint,
    setEndPoint,
    droneProfile,
    setDroneProfile,
    profiles,
    route,
    geojson,
    loading,
    error,
    optimizeRoute,
  };
}
