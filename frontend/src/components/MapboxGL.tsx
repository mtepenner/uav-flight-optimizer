import React, { useEffect, useRef, useCallback } from 'react';
import mapboxgl from 'mapbox-gl';

interface MapboxGLProps {
  startPoint: [number, number] | null;
  endPoint: [number, number] | null;
  onSetStart: (point: [number, number]) => void;
  onSetEnd: (point: [number, number]) => void;
  geojson: GeoJSON.FeatureCollection | null;
}

const MAPBOX_TOKEN = process.env.REACT_APP_MAPBOX_TOKEN || 'pk.placeholder';

const MapboxGL: React.FC<MapboxGLProps> = ({ startPoint, endPoint, onSetStart, onSetEnd, geojson }) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const startMarker = useRef<mapboxgl.Marker | null>(null);
  const endMarker = useRef<mapboxgl.Marker | null>(null);

  useEffect(() => {
    if (!mapContainer.current) return;

    mapboxgl.accessToken = MAPBOX_TOKEN;

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/outdoors-v12',
      center: [-74.006, 40.7128],
      zoom: 12,
      pitch: 45,
    });

    map.current.addControl(new mapboxgl.NavigationControl(), 'top-right');

    return () => {
      map.current?.remove();
    };
  }, []);

  const handleClick = useCallback((e: mapboxgl.MapMouseEvent) => {
    onSetStart([e.lngLat.lng, e.lngLat.lat]);
  }, [onSetStart]);

  const handleContextMenu = useCallback((e: mapboxgl.MapMouseEvent) => {
    e.preventDefault();
    onSetEnd([e.lngLat.lng, e.lngLat.lat]);
  }, [onSetEnd]);

  useEffect(() => {
    if (!map.current) return;
    map.current.on('click', handleClick);
    map.current.on('contextmenu', handleContextMenu);
    return () => {
      map.current?.off('click', handleClick);
      map.current?.off('contextmenu', handleContextMenu);
    };
  }, [handleClick, handleContextMenu]);

  useEffect(() => {
    if (!map.current) return;
    if (startMarker.current) startMarker.current.remove();
    if (startPoint) {
      startMarker.current = new mapboxgl.Marker({ color: '#4ecca3' })
        .setLngLat(startPoint)
        .setPopup(new mapboxgl.Popup().setText('Start'))
        .addTo(map.current);
    }
  }, [startPoint]);

  useEffect(() => {
    if (!map.current) return;
    if (endMarker.current) endMarker.current.remove();
    if (endPoint) {
      endMarker.current = new mapboxgl.Marker({ color: '#e94560' })
        .setLngLat(endPoint)
        .setPopup(new mapboxgl.Popup().setText('End'))
        .addTo(map.current);
    }
  }, [endPoint]);

  useEffect(() => {
    if (!map.current || !geojson) return;

    const m = map.current;

    const addRoute = () => {
      if (m.getSource('route')) {
        (m.getSource('route') as mapboxgl.GeoJSONSource).setData(geojson);
      } else {
        m.addSource('route', { type: 'geojson', data: geojson });
        m.addLayer({
          id: 'route-line',
          type: 'line',
          source: 'route',
          filter: ['==', '$type', 'LineString'],
          layout: { 'line-join': 'round', 'line-cap': 'round' },
          paint: {
            'line-color': '#e94560',
            'line-width': 4,
            'line-opacity': 0.85,
          },
        });
        m.addLayer({
          id: 'route-points',
          type: 'circle',
          source: 'route',
          filter: ['==', '$type', 'Point'],
          paint: {
            'circle-radius': 5,
            'circle-color': '#4ecca3',
            'circle-stroke-color': '#fff',
            'circle-stroke-width': 1,
          },
        });
      }
    };

    if (m.isStyleLoaded()) {
      addRoute();
    } else {
      m.on('load', addRoute);
    }
  }, [geojson]);

  return <div ref={mapContainer} style={{ width: '100%', height: '100%' }} />;
};

export default MapboxGL;
