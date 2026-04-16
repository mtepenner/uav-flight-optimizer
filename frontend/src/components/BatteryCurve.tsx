import React from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine,
} from 'recharts';

interface BatteryCurvePoint {
  distance_m: number;
  battery_pct: number;
  altitude_m: number;
}

interface BatteryCurveProps {
  batteryCurve: BatteryCurvePoint[];
}

const BatteryCurve: React.FC<BatteryCurveProps> = ({ batteryCurve }) => {
  const data = batteryCurve.map((p) => ({
    distance: Math.round(p.distance_m),
    battery: Math.round(p.battery_pct * 10) / 10,
  }));

  return (
    <div style={{ width: '100%', height: '100%' }}>
      <h4 style={{ margin: '0 0 4px 8px', color: '#ccc', fontSize: '12px' }}>
        Battery Drain
      </h4>
      <ResponsiveContainer width="100%" height="85%">
        <LineChart data={data} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#333" />
          <XAxis
            dataKey="distance"
            stroke="#888"
            fontSize={10}
            tickFormatter={(v) => `${(v / 1000).toFixed(1)}km`}
          />
          <YAxis stroke="#888" fontSize={10} domain={[0, 100]} tickFormatter={(v) => `${v}%`} />
          <Tooltip
            contentStyle={{ background: '#1a1a2e', border: '1px solid #333', fontSize: '12px' }}
            labelFormatter={(v) => `Distance: ${(Number(v) / 1000).toFixed(2)} km`}
            formatter={(value: number) => [`${value}%`, 'Battery']}
          />
          <ReferenceLine y={20} stroke="#ff4444" strokeDasharray="5 5" label={{ value: 'Low Battery', fill: '#ff4444', fontSize: 10 }} />
          <Line
            type="monotone"
            dataKey="battery"
            stroke="#e94560"
            strokeWidth={2}
            dot={{ r: 3 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default BatteryCurve;
