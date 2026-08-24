import { useEffect, useRef, useState, useCallback } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { villageApi } from '../../services/api';
import type { Village, LayerVisibility } from '../../types/village';
import type { Candidate } from '../../types/optimization';
import type { VillageMetrics } from '../../types/analysis';

interface VillageMapProps {
  village: Village;
  layerVisibility: LayerVisibility;
  threshold: number;
  candidates: Candidate[];
  onSelectCandidate?: (candidate: Candidate) => void;
  proposedLocation: [number, number] | null;
  onUpdateProposedLocation?: (loc: [number, number]) => void;
  isPlacingProposed?: boolean;
  metrics: VillageMetrics | null;
  isLeftSidebarOpen?: boolean;
  isRightPanelOpen?: boolean;
}

// Generate circular GeoJSON polygon for coverage buffers (geodesic math)
function createGeoJSONCircle(
  center: [number, number],
  radiusInMeters: number,
  points: number = 64
): [number, number][] {
  const [lng, lat] = center;
  const km = radiusInMeters / 1000;
  const coords: [number, number][] = [];
  const distanceX = km / (111.32 * Math.cos((lat * Math.PI) / 180));
  const distanceY = km / 110.574;

  for (let i = 0; i <= points; i++) {
    const theta = (i / points) * (2 * Math.PI);
    const x = distanceX * Math.cos(theta);
    const y = distanceY * Math.sin(theta);
    coords.push([lng + x, lat + y]);
  }

  return coords;
}

export default function VillageMap({
  village,
  layerVisibility,
  threshold,
  candidates,
  onSelectCandidate,
  proposedLocation,
  onUpdateProposedLocation,
  isPlacingProposed,
  metrics,
  isLeftSidebarOpen,
  isRightPanelOpen,
}: VillageMapProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [mapReady, setMapReady] = useState(false);

  // Markers refs
  const candidateMarkersRef = useRef<maplibregl.Marker[]>([]);
  const proposedMarkerRef = useRef<maplibregl.Marker | null>(null);
  const existingFacilitiesDataRef = useRef<GeoJSON.FeatureCollection | null>(null);
  const boundsRef = useRef<{ west: number; south: number; east: number; north: number; center: [number, number] } | null>(null);
  const popupRef = useRef<maplibregl.Popup | null>(null);

  // *** CRITICAL: Refs to keep callback-accessed props always current ***
  // This prevents stale closures in map event handlers
  const isPlacingProposedRef = useRef(isPlacingProposed);
  const onUpdateProposedLocationRef = useRef(onUpdateProposedLocation);
  const layerVisibilityRef = useRef(layerVisibility);
  const thresholdRef = useRef(threshold);
  const proposedLocationRef = useRef(proposedLocation);
  const metricsRef = useRef(metrics);

  // Keep refs in sync with props on every render
  useEffect(() => { isPlacingProposedRef.current = isPlacingProposed; });
  useEffect(() => { onUpdateProposedLocationRef.current = onUpdateProposedLocation; });
  useEffect(() => { layerVisibilityRef.current = layerVisibility; });
  useEffect(() => { thresholdRef.current = threshold; });
  useEffect(() => { proposedLocationRef.current = proposedLocation; });
  useEffect(() => { metricsRef.current = metrics; });

  // Helper to safely check if a layer exists
  const safeSetVisibility = useCallback((mapInst: maplibregl.Map, layerId: string, visible: boolean) => {
    try {
      if (mapInst.getLayer(layerId)) {
        mapInst.setLayoutProperty(layerId, 'visibility', visible ? 'visible' : 'none');
      }
    } catch {
      // Layer may not exist yet
    }
  }, []);

  // Helper to remove all custom layers and sources
  const removeCustomLayers = useCallback((mapInstance: maplibregl.Map) => {
    const layerIds = [
      'coverage-buffers-line',
      'coverage-buffers-fill',
      'underserved-clusters-line',
      'underserved-clusters-fill',
      'facilities-labels',
      'facilities-glow',
      'facilities',
      'buildings-outline',
      'buildings',
      'water_bodies',
      'parcels',
      'boundary-line',
      'boundary-casing',
      'boundary-fill',
    ];

    layerIds.forEach((id) => {
      try {
        if (mapInstance.getLayer(id)) {
          mapInstance.removeLayer(id);
        }
      } catch { /* ignore */ }
    });

    const sourceIds = [
      'coverage-buffers',
      'underserved-clusters',
      'facilities',
      'buildings',
      'water_bodies',
      'parcels',
      'boundary',
    ];

    sourceIds.forEach((id) => {
      try {
        if (mapInstance.getSource(id)) {
          mapInstance.removeSource(id);
        }
      } catch { /* ignore */ }
    });
  }, []);

  // =====================================================================
  // 1. INITIALIZE MAP (runs once on mount, cleaned up on unmount)
  // =====================================================================
  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    let isCancelled = false;

    const initMap = async () => {
      try {
        setLoading(true);
        setError(null);

        const { bounds } = await villageApi.getVillageBounds(village.id);
        if (isCancelled) return;
        boundsRef.current = bounds;

        // Clean container
        if (mapContainer.current) {
          mapContainer.current.innerHTML = '';
        }

        const newMap = new maplibregl.Map({
          container: mapContainer.current!,
          style: {
            version: 8,
            sources: {
              'osm-tiles': {
                type: 'raster',
                tiles: [
                  'https://a.tile.openstreetmap.org/{z}/{x}/{y}.png',
                  'https://b.tile.openstreetmap.org/{z}/{x}/{y}.png',
                  'https://c.tile.openstreetmap.org/{z}/{x}/{y}.png',
                ],
                tileSize: 256,
                attribution: '© OpenStreetMap contributors | PlanGram Spatial',
              },
            },
            layers: [
              {
                id: 'osm-tiles-layer',
                type: 'raster',
                source: 'osm-tiles',
                minzoom: 0,
                maxzoom: 19,
                paint: {
                  'raster-opacity': 1.0,
                },
              },
            ],
          },
          center: bounds.center,
          zoom: 14.5,
          minZoom: 11,
          maxZoom: 19,
        });

        newMap.addControl(new maplibregl.NavigationControl({ showCompass: true }), 'top-right');
        newMap.addControl(new maplibregl.ScaleControl({ unit: 'metric' }), 'bottom-left');

        // Click handler reads from refs so it always has current values
        newMap.on('click', (e) => {
          if (isPlacingProposedRef.current && onUpdateProposedLocationRef.current) {
            onUpdateProposedLocationRef.current([e.lngLat.lng, e.lngLat.lat]);
          }
        });

        newMap.on('load', async () => {
          if (isCancelled) {
            newMap.remove();
            return;
          }

          map.current = newMap;
          await loadVillageLayersForMap(newMap, village.id);
          rebuildCoverageBuffers(newMap);
          rebuildUnderservedClusters(newMap);

          newMap.fitBounds(
            [[bounds.west, bounds.south], [bounds.east, bounds.north]],
            { padding: 70, duration: 600 }
          );

          setMapReady(true);
          setLoading(false);
        });

        newMap.on('error', (e) => {
          console.error('Map error:', e);
        });

      } catch (err) {
        console.error('Error initializing map:', err);
        if (!isCancelled) {
          setError('Failed to initialize map');
          setLoading(false);
        }
      }
    };

    initMap();

    return () => {
      isCancelled = true;
      candidateMarkersRef.current.forEach((m) => m.remove());
      candidateMarkersRef.current = [];
      if (proposedMarkerRef.current) { proposedMarkerRef.current.remove(); proposedMarkerRef.current = null; }
      if (popupRef.current) { popupRef.current.remove(); popupRef.current = null; }
      if (map.current) { map.current.remove(); map.current = null; }
      setMapReady(false);
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Mount once only

  // =====================================================================
  // 2. VILLAGE CHANGE: swap layers on the existing map (no re-create)
  // =====================================================================
  const currentVillageIdRef = useRef(village.id);
  useEffect(() => {
    if (!map.current || !mapReady) return;
    if (village.id === currentVillageIdRef.current) return; // skip initial
    currentVillageIdRef.current = village.id;

    const switchVillage = async () => {
      try {
        setLoading(true);
        const { bounds } = await villageApi.getVillageBounds(village.id);
        boundsRef.current = bounds;

        removeCustomLayers(map.current!);
        existingFacilitiesDataRef.current = null;

        await loadVillageLayersForMap(map.current!, village.id);
        rebuildCoverageBuffers(map.current!);
        rebuildUnderservedClusters(map.current!);

        map.current!.fitBounds(
          [[bounds.west, bounds.south], [bounds.east, bounds.north]],
          { padding: 70, duration: 800 }
        );

        setLoading(false);
      } catch (err) {
        console.error('Error switching village:', err);
        setLoading(false);
      }
    };

    switchVillage();
  }, [village.id, mapReady, removeCustomLayers]);

  // =====================================================================
  // 3. LAYER VISIBILITY TOGGLING (runs whenever layerVisibility changes)
  // =====================================================================
  useEffect(() => {
    if (!map.current || !mapReady) return;
    const m = map.current;

    // Boundary
    safeSetVisibility(m, 'boundary-fill', !!layerVisibility.boundary);
    safeSetVisibility(m, 'boundary-casing', !!layerVisibility.boundary);
    safeSetVisibility(m, 'boundary-line', !!layerVisibility.boundary);

    // Buildings
    safeSetVisibility(m, 'buildings', !!layerVisibility.buildings);
    safeSetVisibility(m, 'buildings-outline', !!layerVisibility.buildings);

    // Facilities
    safeSetVisibility(m, 'facilities', !!layerVisibility.facilities);
    safeSetVisibility(m, 'facilities-glow', !!layerVisibility.facilities);
    safeSetVisibility(m, 'facilities-labels', !!layerVisibility.facilities);

    // Coverage buffers
    safeSetVisibility(m, 'coverage-buffers-fill', !!layerVisibility.coverage);
    safeSetVisibility(m, 'coverage-buffers-line', !!layerVisibility.coverage);

    // Underserved
    safeSetVisibility(m, 'underserved-clusters-fill', !!layerVisibility.underserved);
    safeSetVisibility(m, 'underserved-clusters-line', !!layerVisibility.underserved);

    // Parcels
    safeSetVisibility(m, 'parcels', !!layerVisibility.parcels);

    // Water bodies
    safeSetVisibility(m, 'water_bodies', !!layerVisibility.water_bodies);
  }, [layerVisibility, mapReady, safeSetVisibility]);

  // =====================================================================
  // 4. COVERAGE BUFFERS: rebuild when threshold/proposedLocation changes
  // =====================================================================
  useEffect(() => {
    if (!map.current || !mapReady) return;
    rebuildCoverageBuffers(map.current);
  }, [threshold, proposedLocation, mapReady]);

  // =====================================================================
  // 5. UNDERSERVED CLUSTERS: rebuild when metrics change
  // =====================================================================
  useEffect(() => {
    if (!map.current || !mapReady) return;
    rebuildUnderservedClusters(map.current);
  }, [metrics, mapReady]);

  // =====================================================================
  // 6. CANDIDATE MARKERS
  // =====================================================================
  useEffect(() => {
    candidateMarkersRef.current.forEach((m) => m.remove());
    candidateMarkersRef.current = [];

    if (!map.current || !mapReady || layerVisibility.candidates === false || candidates.length === 0) return;

    candidates.forEach((cand, idx) => {
      const rank = cand.rank || idx + 1;
      const el = document.createElement('div');
      el.className =
        'w-8 h-8 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white font-extrabold text-xs flex items-center justify-center border-2 border-white shadow-2xl cursor-pointer transform hover:scale-125 transition-transform z-20';
      el.innerHTML = `${rank}`;
      el.title = `Candidate #${rank} — Click to place facility here`;

      const popup = new maplibregl.Popup({ offset: 12 }).setHTML(
        `<div class="text-xs font-sans p-1">
          <div class="font-bold text-indigo-900 text-sm">Recommended Site #${rank}</div>
          <div class="text-slate-600 mt-1">Suitability: <strong>${Math.round(cand.combined_score)}%</strong></div>
          <div class="text-emerald-700 font-semibold mt-0.5">+${cand.households_gained || 160} households gained</div>
          <div class="text-[11px] text-blue-600 mt-2 font-bold bg-blue-50 p-1 rounded text-center">Click to place facility</div>
        </div>`
      );

      const marker = new maplibregl.Marker({ element: el })
        .setLngLat(cand.location)
        .setPopup(popup)
        .addTo(map.current!);

      el.addEventListener('click', () => {
        if (onSelectCandidate) onSelectCandidate(cand);
      });

      candidateMarkersRef.current.push(marker);
    });
  }, [candidates, layerVisibility.candidates, onSelectCandidate, mapReady]);

  // =====================================================================
  // 7. PROPOSED FACILITY MARKER (draggable)
  // =====================================================================
  useEffect(() => {
    if (proposedMarkerRef.current) {
      proposedMarkerRef.current.remove();
      proposedMarkerRef.current = null;
    }

    if (!map.current || !mapReady || !proposedLocation || layerVisibility.proposed === false) return;

    const el = document.createElement('div');
    el.className = 'relative flex items-center justify-center cursor-move z-30';
    el.innerHTML = `
      <div class="absolute w-10 h-10 rounded-full bg-blue-500 animate-pulse-ring"></div>
      <div class="w-9 h-9 rounded-full bg-blue-600 border-2 border-white shadow-2xl flex items-center justify-center text-white text-base font-bold z-10">
        📍
      </div>
    `;

    const popup = new maplibregl.Popup({ offset: 18 }).setHTML(
      `<div class="text-xs font-sans p-1">
        <div class="font-bold text-blue-900 text-sm">Proposed Water Facility</div>
        <div class="text-slate-600 text-[11px] mt-1">Drag to reposition & re-simulate coverage</div>
      </div>`
    );

    const marker = new maplibregl.Marker({ element: el, draggable: true })
      .setLngLat(proposedLocation)
      .setPopup(popup)
      .addTo(map.current!);

    marker.on('dragend', () => {
      const lngLat = marker.getLngLat();
      if (onUpdateProposedLocationRef.current) {
        onUpdateProposedLocationRef.current([lngLat.lng, lngLat.lat]);
      }
    });

    proposedMarkerRef.current = marker;
  }, [proposedLocation, layerVisibility.proposed, mapReady]);

  // =====================================================================
  // 8. RESIZE ON PANEL COLLAPSE/EXPAND
  // =====================================================================
  useEffect(() => {
    if (map.current) {
      setTimeout(() => { map.current?.resize(); }, 150);
    }
  }, [isLeftSidebarOpen, isRightPanelOpen]);

  // =====================================================================
  // HELPER: Load GIS layers for a given village onto a map instance
  // =====================================================================
  const loadVillageLayersForMap = async (mapInstance: maplibregl.Map, villageId: string) => {
    const layers = ['boundary', 'parcels', 'water_bodies', 'buildings', 'facilities'];
    const vis = layerVisibilityRef.current;

    for (const layerName of layers) {
      try {
        const geojson = await villageApi.getVillageLayer(villageId, layerName);

        if (layerName === 'facilities') {
          existingFacilitiesDataRef.current = geojson;
        }

        if (!mapInstance.getSource(layerName)) {
          mapInstance.addSource(layerName, { type: 'geojson', data: geojson });
        }

        if (layerName === 'boundary') {
          mapInstance.addLayer({
            id: 'boundary-fill', type: 'fill', source: 'boundary',
            layout: { visibility: vis.boundary ? 'visible' : 'none' },
            paint: { 'fill-color': '#2563eb', 'fill-opacity': 0.12 },
          });
          mapInstance.addLayer({
            id: 'boundary-casing', type: 'line', source: 'boundary',
            layout: { visibility: vis.boundary ? 'visible' : 'none' },
            paint: { 'line-color': '#ffffff', 'line-width': 6, 'line-opacity': 0.9 },
          });
          mapInstance.addLayer({
            id: 'boundary-line', type: 'line', source: 'boundary',
            layout: { visibility: vis.boundary ? 'visible' : 'none' },
            paint: { 'line-color': '#1d4ed8', 'line-width': 3.5, 'line-dasharray': [4, 2] },
          });
        } else if (layerName === 'parcels') {
          mapInstance.addLayer({
            id: 'parcels', type: 'line', source: 'parcels',
            layout: { visibility: vis.parcels ? 'visible' : 'none' },
            paint: { 'line-color': '#64748b', 'line-width': 1, 'line-dasharray': [3, 3] },
          });
        } else if (layerName === 'water_bodies') {
          mapInstance.addLayer({
            id: 'water_bodies', type: 'fill', source: 'water_bodies',
            layout: { visibility: vis.water_bodies ? 'visible' : 'none' },
            paint: { 'fill-color': '#0284c7', 'fill-opacity': 0.5 },
          });
        } else if (layerName === 'buildings') {
          mapInstance.addLayer({
            id: 'buildings', type: 'fill', source: 'buildings',
            layout: { visibility: vis.buildings ? 'visible' : 'none' },
            paint: { 'fill-color': '#334155', 'fill-opacity': 0.85 },
          });
          mapInstance.addLayer({
            id: 'buildings-outline', type: 'line', source: 'buildings',
            layout: { visibility: vis.buildings ? 'visible' : 'none' },
            paint: { 'line-color': '#0f172a', 'line-width': 1 },
          });

          // Building hover popup
          const popup = new maplibregl.Popup({ closeButton: false, closeOnClick: false, className: 'building-tooltip' });
          popupRef.current = popup;

          mapInstance.on('mouseenter', 'buildings', (e) => {
            mapInstance.getCanvas().style.cursor = 'pointer';
            if (e.features?.[0]) {
              const props = e.features[0].properties || {};
              popup.setLngLat(e.lngLat).setHTML(
                `<div class="text-xs font-sans p-1">
                  <div class="font-bold text-slate-900">${props.building_id || 'Building'}</div>
                  <div class="text-slate-600 mt-0.5">${props.households || 1} household(s) • ~${props.population || 4} people</div>
                </div>`
              ).addTo(mapInstance);
            }
          });
          mapInstance.on('mouseleave', 'buildings', () => {
            mapInstance.getCanvas().style.cursor = '';
            popup.remove();
          });
        } else if (layerName === 'facilities') {
          mapInstance.addLayer({
            id: 'facilities-glow', type: 'circle', source: 'facilities',
            layout: { visibility: vis.facilities ? 'visible' : 'none' },
            paint: { 'circle-radius': 14, 'circle-color': '#10b981', 'circle-opacity': 0.45 },
          });
          mapInstance.addLayer({
            id: 'facilities', type: 'circle', source: 'facilities',
            layout: { visibility: vis.facilities ? 'visible' : 'none' },
            paint: { 'circle-radius': 8, 'circle-color': '#059669', 'circle-stroke-width': 3, 'circle-stroke-color': '#ffffff' },
          });
          mapInstance.addLayer({
            id: 'facilities-labels', type: 'symbol', source: 'facilities',
            layout: {
              'text-field': ['get', 'name'], 'text-size': 12, 'text-offset': [0, 1.5],
              'text-anchor': 'top', 'text-font': ['Open Sans Bold', 'Arial Unicode MS Bold'],
              visibility: vis.facilities ? 'visible' : 'none',
            },
            paint: { 'text-color': '#064e3b', 'text-halo-color': '#ffffff', 'text-halo-width': 3 },
          });
        }
      } catch (layerErr) {
        console.warn(`Layer ${layerName} skipped:`, layerErr);
      }
    }
  };

  // =====================================================================
  // HELPER: Rebuild coverage buffer polygons
  // =====================================================================
  const rebuildCoverageBuffers = (mapInstance: maplibregl.Map) => {
    const features: GeoJSON.Feature<GeoJSON.Polygon>[] = [];
    const currentThreshold = thresholdRef.current;
    const currentProposed = proposedLocationRef.current;
    const vis = layerVisibilityRef.current;

    if (existingFacilitiesDataRef.current?.features) {
      for (const f of existingFacilitiesDataRef.current.features) {
        if (f.geometry.type === 'Point') {
          const coords = (f.geometry as GeoJSON.Point).coordinates as [number, number];
          features.push({
            type: 'Feature', properties: { type: 'existing' },
            geometry: { type: 'Polygon', coordinates: [createGeoJSONCircle(coords, currentThreshold)] },
          });
        }
      }
    }

    if (currentProposed) {
      features.push({
        type: 'Feature', properties: { type: 'proposed' },
        geometry: { type: 'Polygon', coordinates: [createGeoJSONCircle(currentProposed, currentThreshold)] },
      });
    }

    const geojson: GeoJSON.FeatureCollection = { type: 'FeatureCollection', features };

    if (mapInstance.getSource('coverage-buffers')) {
      (mapInstance.getSource('coverage-buffers') as maplibregl.GeoJSONSource).setData(geojson);
    } else {
      mapInstance.addSource('coverage-buffers', { type: 'geojson', data: geojson });
      mapInstance.addLayer({
        id: 'coverage-buffers-fill', type: 'fill', source: 'coverage-buffers',
        layout: { visibility: vis.coverage ? 'visible' : 'none' },
        paint: {
          'fill-color': ['case', ['==', ['get', 'type'], 'proposed'], '#2563eb', '#10b981'],
          'fill-opacity': 0.28,
        },
      });
      mapInstance.addLayer({
        id: 'coverage-buffers-line', type: 'line', source: 'coverage-buffers',
        layout: { visibility: vis.coverage ? 'visible' : 'none' },
        paint: {
          'line-color': ['case', ['==', ['get', 'type'], 'proposed'], '#1d4ed8', '#047857'],
          'line-width': 2.5, 'line-dasharray': [4, 2],
        },
      });
    }
  };

  // =====================================================================
  // HELPER: Rebuild underserved cluster polygons
  // =====================================================================
  const rebuildUnderservedClusters = (mapInstance: maplibregl.Map) => {
    const features: GeoJSON.Feature<GeoJSON.Polygon>[] = [];
    const currentMetrics = metricsRef.current;
    const vis = layerVisibilityRef.current;

    if (currentMetrics?.underserved_clusters) {
      for (const cluster of currentMetrics.underserved_clusters) {
        if (cluster.center) {
          features.push({
            type: 'Feature',
            properties: { cluster_id: cluster.cluster_id, households: cluster.households, population: cluster.population },
            geometry: { type: 'Polygon', coordinates: [createGeoJSONCircle(cluster.center, 220)] },
          });
        }
      }
    }

    const geojson: GeoJSON.FeatureCollection = { type: 'FeatureCollection', features };

    if (mapInstance.getSource('underserved-clusters')) {
      (mapInstance.getSource('underserved-clusters') as maplibregl.GeoJSONSource).setData(geojson);
    } else {
      mapInstance.addSource('underserved-clusters', { type: 'geojson', data: geojson });
      mapInstance.addLayer({
        id: 'underserved-clusters-fill', type: 'fill', source: 'underserved-clusters',
        layout: { visibility: vis.underserved ? 'visible' : 'none' },
        paint: { 'fill-color': '#f59e0b', 'fill-opacity': 0.28 },
      });
      mapInstance.addLayer({
        id: 'underserved-clusters-line', type: 'line', source: 'underserved-clusters',
        layout: { visibility: vis.underserved ? 'visible' : 'none' },
        paint: { 'line-color': '#b45309', 'line-width': 2.5, 'line-dasharray': [2, 2] },
      });
    }
  };

  // =====================================================================
  // Fit bounds helper
  // =====================================================================
  const handleFitBounds = async () => {
    if (!map.current) return;
    try {
      const { bounds } = await villageApi.getVillageBounds(village.id);
      boundsRef.current = bounds;
      map.current.fitBounds(
        [[bounds.west, bounds.south], [bounds.east, bounds.north]],
        { padding: 70, duration: 800 }
      );
    } catch (err) {
      console.warn('Fit bounds error:', err);
    }
  };

  // =====================================================================
  // RENDER
  // =====================================================================
  return (
    <div className="relative w-full h-full bg-slate-950 overflow-hidden">
      <div ref={mapContainer} className="w-full h-full" />

      {/* Floating Placement Mode Indicator */}
      {isPlacingProposed && (
        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-20 bg-amber-500 text-slate-950 font-extrabold px-5 py-2.5 rounded-xl shadow-2xl flex items-center gap-2.5 text-xs animate-bounce border-2 border-slate-950">
          <span className="text-base">📍</span>
          <span>Click anywhere on the map to place the proposed water facility</span>
        </div>
      )}

      {/* Floating Map Controls Top Left */}
      <div className="absolute top-4 left-4 z-10 flex items-center gap-2">
        <button
          onClick={handleFitBounds}
          className="px-3.5 py-2 rounded-xl bg-slate-900/95 hover:bg-slate-800 text-white border border-slate-700/90 text-xs font-bold shadow-xl backdrop-blur-md transition-all flex items-center gap-2 hover:scale-105 active:scale-95"
          title="Center entire village in view"
        >
          <span>🎯</span>
          <span>Center {village.name}</span>
        </button>

        <div className="px-3.5 py-2 rounded-xl bg-slate-900/95 text-slate-200 border border-slate-700/90 text-xs font-semibold shadow-xl backdrop-blur-md flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>Radius: <strong className="text-white font-mono">{threshold}m</strong></span>
        </div>
      </div>

      {/* Map Legend Bottom Right */}
      <div className="absolute bottom-6 right-4 z-10 bg-slate-900/95 border border-slate-700/90 rounded-xl p-3 shadow-2xl backdrop-blur-md text-[11px] space-y-1.5 text-slate-300">
        <div className="font-bold text-white text-xs mb-1 border-b border-slate-800 pb-1 flex items-center justify-between gap-4">
          <span>Map Legend</span>
          <span className="text-[10px] text-slate-400 font-mono">EPSG:4326</span>
        </div>
        <div className="flex items-center gap-2 font-medium">
          <span className="w-3.5 h-3.5 rounded-full bg-emerald-500 border-2 border-white shadow-sm"></span>
          <span className="text-slate-100">Existing Water Facility</span>
        </div>
        {proposedLocation && (
          <div className="flex items-center gap-2 font-medium">
            <span className="w-3.5 h-3.5 rounded-full bg-blue-600 border-2 border-white shadow-sm animate-pulse"></span>
            <span className="text-blue-300 font-bold">Proposed Facility</span>
          </div>
        )}
        {candidates.length > 0 && (
          <div className="flex items-center gap-2 font-medium">
            <span className="w-3.5 h-3.5 rounded-full bg-indigo-600 text-white text-[8px] font-bold flex items-center justify-center">1</span>
            <span className="text-indigo-300">Candidate Site</span>
          </div>
        )}
        <div className="flex items-center gap-2">
          <span className="w-4 h-2.5 rounded bg-emerald-500/50 border border-emerald-500"></span>
          <span>{threshold}m Coverage Buffer</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-4 h-2.5 rounded bg-amber-500/50 border border-amber-500"></span>
          <span>Underserved Zone</span>
        </div>
      </div>

      {/* Loading Overlay */}
      {loading && (
        <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm z-30 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-3 border-blue-500 border-t-transparent mx-auto mb-3"></div>
            <p className="text-sm font-bold text-white">Centering {village.name}...</p>
            <p className="text-xs text-slate-400 mt-1">Rendering GIS boundaries & facilities</p>
          </div>
        </div>
      )}

      {/* Error Overlay */}
      {error && (
        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-30 bg-red-950/90 border border-red-500/50 rounded-xl p-4 shadow-2xl text-red-200 text-xs flex items-center gap-3">
          <span className="text-lg">⚠️</span>
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}
