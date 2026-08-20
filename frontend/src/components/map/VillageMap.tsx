import { useEffect, useRef, useState } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { villageApi } from '../../services/api';
import type { Village, LayerVisibility } from '../../types/village';

interface VillageMapProps {
  village: Village;
  layerVisibility: LayerVisibility;
}

export default function VillageMap({ village, layerVisibility }: VillageMapProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Initialize map
  useEffect(() => {
    if (!mapContainer.current) return;
    if (map.current) return; // Map already initialized

    const initMap = async () => {
      try {
        setLoading(true);
        setError(null);

        // Get village bounds
        const { bounds } = await villageApi.getVillageBounds(village.id);

        // Initialize map
        map.current = new maplibregl.Map({
          container: mapContainer.current!,
          style: {
            version: 8,
            sources: {
              'osm-tiles': {
                type: 'raster',
                tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
                tileSize: 256,
                attribution: '© OpenStreetMap contributors',
              },
            },
            layers: [
              {
                id: 'osm-tiles-layer',
                type: 'raster',
                source: 'osm-tiles',
                minzoom: 0,
                maxzoom: 19,
              },
            ],
          },
          center: bounds.center,
          zoom: 14,
          maxZoom: 19,
        });

        // Add navigation controls
        map.current.addControl(new maplibregl.NavigationControl(), 'top-right');

        // Add scale
        map.current.addControl(
          new maplibregl.ScaleControl({ unit: 'metric' }),
          'bottom-left'
        );

        map.current.on('load', () => {
          loadVillageLayers();
        });

        map.current.on('error', (e) => {
          console.error('Map error:', e);
        });

      } catch (err) {
        console.error('Error initializing map:', err);
        setError('Failed to initialize map');
      }
    };

    initMap();

    return () => {
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, [village.id]);

  // Load village layers
  const loadVillageLayers = async () => {
    if (!map.current) return;

    try {
      const layers = ['boundary', 'parcels', 'roads', 'water_bodies', 'buildings', 'facilities'];

      for (const layerName of layers) {
        try {
          const geojson = await villageApi.getVillageLayer(village.id, layerName);

          // Add source
          if (!map.current.getSource(layerName)) {
            map.current.addSource(layerName, {
              type: 'geojson',
              data: geojson,
            });
          }

          // Add layers based on geometry type
          if (layerName === 'boundary') {
            map.current.addLayer({
              id: `${layerName}-line`,
              type: 'line',
              source: layerName,
              paint: {
                'line-color': '#2563eb',
                'line-width': 3,
              },
            });
            map.current.addLayer({
              id: `${layerName}-fill`,
              type: 'fill',
              source: layerName,
              paint: {
                'fill-color': '#3b82f6',
                'fill-opacity': 0.1,
              },
            });
          } else if (layerName === 'buildings') {
            map.current.addLayer({
              id: layerName,
              type: 'fill',
              source: layerName,
              paint: {
                'fill-color': '#dc2626',
                'fill-opacity': 0.6,
              },
            });
            map.current.addLayer({
              id: `${layerName}-outline`,
              type: 'line',
              source: layerName,
              paint: {
                'line-color': '#991b1b',
                'line-width': 1,
              },
            });
          } else if (layerName === 'parcels') {
            map.current.addLayer({
              id: layerName,
              type: 'line',
              source: layerName,
              paint: {
                'line-color': '#9ca3af',
                'line-width': 1,
                'line-dasharray': [2, 2],
              },
            });
          } else if (layerName === 'roads') {
            map.current.addLayer({
              id: layerName,
              type: 'line',
              source: layerName,
              paint: {
                'line-color': '#f59e0b',
                'line-width': 2,
              },
            });
          } else if (layerName === 'water_bodies') {
            map.current.addLayer({
              id: layerName,
              type: 'fill',
              source: layerName,
              paint: {
                'fill-color': '#3b82f6',
                'fill-opacity': 0.5,
              },
            });
          } else if (layerName === 'facilities') {
            map.current.addLayer({
              id: layerName,
              type: 'circle',
              source: layerName,
              paint: {
                'circle-radius': 8,
                'circle-color': '#10b981',
                'circle-stroke-width': 2,
                'circle-stroke-color': '#ffffff',
              },
            });

            // Add facility labels
            map.current.addLayer({
              id: `${layerName}-labels`,
              type: 'symbol',
              source: layerName,
              layout: {
                'text-field': ['get', 'name'],
                'text-size': 12,
                'text-offset': [0, 1.5],
                'text-anchor': 'top',
              },
              paint: {
                'text-color': '#065f46',
                'text-halo-color': '#ffffff',
                'text-halo-width': 2,
              },
            });
          }
        } catch (err) {
          console.warn(`Layer ${layerName} not available:`, err);
        }
      }

      setLoading(false);
    } catch (err) {
      console.error('Error loading village layers:', err);
      setError('Failed to load village layers');
      setLoading(false);
    }
  };

  // Update layer visibility
  useEffect(() => {
    if (!map.current) return;

    Object.entries(layerVisibility).forEach(([layerName, visible]) => {
      const visibility = visible ? 'visible' : 'none';

      // Handle different layer configurations
      if (layerName === 'boundary') {
        if (map.current?.getLayer(`${layerName}-line`)) {
          map.current.setLayoutProperty(`${layerName}-line`, 'visibility', visibility);
        }
        if (map.current?.getLayer(`${layerName}-fill`)) {
          map.current.setLayoutProperty(`${layerName}-fill`, 'visibility', visibility);
        }
      } else if (layerName === 'buildings') {
        if (map.current?.getLayer(layerName)) {
          map.current.setLayoutProperty(layerName, 'visibility', visibility);
        }
        if (map.current?.getLayer(`${layerName}-outline`)) {
          map.current.setLayoutProperty(`${layerName}-outline`, 'visibility', visibility);
        }
      } else if (layerName === 'facilities') {
        if (map.current?.getLayer(layerName)) {
          map.current.setLayoutProperty(layerName, 'visibility', visibility);
        }
        if (map.current?.getLayer(`${layerName}-labels`)) {
          map.current.setLayoutProperty(`${layerName}-labels`, 'visibility', visibility);
        }
      } else {
        if (map.current?.getLayer(layerName)) {
          map.current.setLayoutProperty(layerName, 'visibility', visibility);
        }
      }
    });
  }, [layerVisibility]);

  return (
    <div className="relative w-full h-full">
      <div ref={mapContainer} className="w-full h-full" />
      
      {loading && (
        <div className="absolute inset-0 bg-white bg-opacity-90 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading village map...</p>
          </div>
        </div>
      )}

      {error && (
        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-red-50 border border-red-200 rounded-lg p-4 shadow-lg">
          <p className="text-red-800 flex items-center gap-2">
            <span>⚠️</span>
            <span>{error}</span>
          </p>
        </div>
      )}
    </div>
  );
}
