import React from 'react';
import MapboxGL from './components/MapboxGL';
import ElevationProfile from './components/ElevationProfile';
import BatteryCurve from './components/BatteryCurve';
import { useFlightPlanner } from './hooks/useFlightPlanner';

const App: React.FC = () => {
  const {
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
  } = useFlightPlanner();

  return (
    <div style={{ fontFamily: 'system-ui, sans-serif', height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <header style={{
        background: '#1a1a2e',
        color: '#fff',
        padding: '12px 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
      }}>
        <h1 style={{ margin: 0, fontSize: '20px' }}>🚁 UAV Flight Optimizer</h1>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <select
            value={droneProfile}
            onChange={(e) => setDroneProfile(e.target.value)}
            style={{ padding: '6px 12px', borderRadius: '4px', border: 'none' }}
          >
            {profiles.map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
          <button
            onClick={optimizeRoute}
            disabled={loading || !startPoint || !endPoint}
            style={{
              padding: '8px 20px',
              background: loading ? '#666' : '#e94560',
              color: '#fff',
              border: 'none',
              borderRadius: '4px',
              cursor: loading ? 'wait' : 'pointer',
              fontWeight: 'bold',
            }}
          >
            {loading ? 'Optimizing...' : 'Optimize Route'}
          </button>
        </div>
      </header>

      {error && (
        <div style={{ background: '#ff4444', color: '#fff', padding: '8px 24px', fontSize: '14px' }}>
          {error}
        </div>
      )}

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <div style={{ flex: 1, position: 'relative' }}>
          <MapboxGL
            startPoint={startPoint}
            endPoint={endPoint}
            onSetStart={setStartPoint}
            onSetEnd={setEndPoint}
            geojson={geojson}
          />
          <div style={{
            position: 'absolute',
            top: '10px',
            left: '10px',
            background: 'rgba(26,26,46,0.9)',
            color: '#fff',
            padding: '10px 14px',
            borderRadius: '8px',
            fontSize: '12px',
            lineHeight: '1.6',
          }}>
            <strong>Instructions:</strong><br />
            Click to set <span style={{ color: '#4ecca3' }}>Start</span> point<br />
            Right-click to set <span style={{ color: '#e94560' }}>End</span> point<br />
            Then click <strong>Optimize Route</strong>
          </div>

          {route && (
            <div style={{
              position: 'absolute',
              top: '10px',
              right: '10px',
              background: 'rgba(26,26,46,0.9)',
              color: '#fff',
              padding: '12px 16px',
              borderRadius: '8px',
              fontSize: '13px',
              lineHeight: '1.8',
            }}>
              <strong>Route Summary</strong><br />
              Distance: {(route.total_distance_m / 1000).toFixed(2)} km<br />
              Duration: {(route.total_duration_s / 60).toFixed(1)} min<br />
              Energy: {(route.total_energy_j / 1000).toFixed(1)} kJ<br />
              Battery Used: {route.battery_used_pct.toFixed(1)}%<br />
              Battery Left: {route.battery_remaining_pct.toFixed(1)}%
            </div>
          )}
        </div>
      </div>

      {route && (
        <div style={{
          display: 'flex',
          height: '200px',
          borderTop: '2px solid #1a1a2e',
          background: '#0f0f23',
        }}>
          <div style={{ flex: 1, padding: '8px' }}>
            <ElevationProfile batteryCurve={route.battery_curve} />
          </div>
          <div style={{ flex: 1, padding: '8px' }}>
            <BatteryCurve batteryCurve={route.battery_curve} />
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
