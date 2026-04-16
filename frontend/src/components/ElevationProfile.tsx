import React from 'react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';

interface BatteryCurvePoint {
  distance_m: number;
  battery_pct: number;
  altitude_m: number;
}

interface ElevationProfileProps {
  batteryCurve: BatteryCurvePoint[];
}

const ElevationProfile: React.FC<ElevationProfileProps> = ({ batteryCurve }) => {
  const data = batteryCurve.map((p) => ({
    distance: Math.round(p.distance_m),
    altitude: Math.round(p.altitude_m),
  }));

  return (
    <div style={{ width: '100%', height: '100%' }}>
      <h4 style={{ margin: '0 0 4px 8px', color: '#ccc', fontSize: '12px' }}>
        Elevation Profile
      </h4>
      <ResponsiveContainer width="100%" height="85%">
        <AreaChart data={data} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#333" />
          <XAxis
            dataKey="distance"
            stroke="#888"
            fontSize={10}
            tickFormatter={(v) => `${(v / 1000).toFixed(1)}km`}
          />
          <YAxis stroke="#888" fontSize={10} tickFormatter={(v) => `${v}m`} />
          <Tooltip
            contentStyle={{ background: '#1a1a2e', border: '1px solid #333', fontSize: '12px' }}
            labelFormatter={(v) => `Distance: ${(Number(v) / 1000).toFixed(2)} km`}
            formatter={(value: number) => [`${value} m`, 'Altitude']}
          />
          <Area
            type="monotone"
            dataKey="altitude"
            stroke="#4ecca3"
            fill="#4ecca3"
            fillOpacity={0.3}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ElevationProfile;
