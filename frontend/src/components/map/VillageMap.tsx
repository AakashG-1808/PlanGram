import { useEffect, useRef, useState, useCallback } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { villageApi } from '../../services/api';
import type { Village, LayerVisibility, ProposedFacility } from '../../types/village';
import type { Candidate } from '../../types/optimization';
import type { VillageMetrics } from '../../types/analysis';
import type { PlanningObjective } from '../planning/PlanningSidebar';

/** Icon and color config for each facility type */
const FACILITY_TYPE_CONFIG: Record<string, { icon: string; color: string; bgColor: string; label: string }> = {
  water:       { icon: '💧', color: '#0ea5e9', bgColor: '#0c4a6e', label: 'Water Point' },
  education:   { icon: '🎓', color: '#a855f7', bgColor: '#581c87', label: 'Education' },
  health:      { icon: '🏥', color: '#ef4444', bgColor: '#7f1d1d', label: 'Healthcare' },
  healthcare:  { icon: '🏥', color: '#ef4444', bgColor: '#7f1d1d', label: 'Healthcare' },
  sanitation:  { icon: '🚽', color: '#f59e0b', bgColor: '#78350f', label: 'Sanitation' },
  waste:       { icon: '♻️', color: '#22c55e', bgColor: '#14532d', label: 'Waste Mgmt' },
  connectivity:{ icon: '🛣️', color: '#f97316', bgColor: '#7c2d12', label: 'Connectivity' },
  bus_stop:    { icon: '🚏', color: '#f97316', bgColor: '#7c2d12', label: 'Bus Stop' },
  public_toilet:{ icon: '🚻', color: '#eab308', bgColor: '#713f12', label: 'Public Toilet' },
};

/** Get the icon for the active planning objective (used for proposed marker) */
const OBJECTIVE_ICON: Record<PlanningObjective, string> = {
  water: '💧',
  healthcare: '🏥',
  education: '🎓',
  sanitation: '🚽',
  waste: '♻️',
  connectivity: '🛣️',
};

const DEFAULT_FACILITY_CONFIG = { icon: '📍', color: '#10b981', bgColor: '#064e3b', label: 'Facility' };

interface VillageMapProps {
  village: Village;
  layerVisibility: LayerVisibility;
  threshold: number;
  candidates: Candidate[];
  onSelectCandidate?: (candidate: Candidate) => void;
  onDismissCandidate?: (candidate: Candidate) => void;
  proposedFacilities?: ProposedFacility[];
  onAddProposedFacility?: (loc: [number, number]) => void;
  onUpdateProposedFacilityLocation?: (id: string, loc: [number, number]) => void;
  onDeleteProposedFacility?: (id: string) => void;
  isPlacingProposed?: boolean;
  activeObjective?: PlanningObjective;
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
  onDismissCandidate,
  proposedFacilities = [],
  onAddProposedFacility,
  onUpdateProposedFacilityLocation,
  onDeleteProposedFacility,
  isPlacingProposed,
  activeObjective = 'water',
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
  const proposedMarkersRef = useRef<maplibregl.Marker[]>([]);
  const facilityMarkersRef = useRef<maplibregl.Marker[]>([]);
  const existingFacilitiesDataRef = useRef<GeoJSON.FeatureCollection | null>(null);
  const boundsRef = useRef<{ west: number; south: number; east: number; north: number; center: [number, number] } | null>(null);
  const popupRef = useRef<maplibregl.Popup | null>(null);

  // *** CRITICAL: Refs to keep callback-accessed props always current ***
  const isPlacingProposedRef = useRef(isPlacingProposed);
  const onAddProposedFacilityRef = useRef(onAddProposedFacility);
  const onUpdateProposedFacilityLocationRef = useRef(onUpdateProposedFacilityLocation);
  const onDeleteProposedFacilityRef = useRef(onDeleteProposedFacility);
  const layerVisibilityRef = useRef(layerVisibility);
  const thresholdRef = useRef(threshold);
  const proposedFacilitiesRef = useRef(proposedFacilities);
  const metricsRef = useRef(metrics);
  const activeObjectiveRef = useRef(activeObjective);

  // Keep refs in sync with props on every render
  useEffect(() => { isPlacingProposedRef.current = isPlacingProposed; });
  useEffect(() => { onAddProposedFacilityRef.current = onAddProposedFacility; });
  useEffect(() => { onUpdateProposedFacilityLocationRef.current = onUpdateProposedFacilityLocation; });
  useEffect(() => { onDeleteProposedFacilityRef.current = onDeleteProposedFacility; });
  useEffect(() => { layerVisibilityRef.current = layerVisibility; });
  useEffect(() => { thresholdRef.current = threshold; });
  useEffect(() => { proposedFacilitiesRef.current = proposedFacilities; });
  useEffect(() => { metricsRef.current = metrics; });
  useEffect(() => { activeObjectiveRef.current = activeObjective; });

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
                maxzoom: 19,
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
          if (isPlacingProposedRef.current && onAddProposedFacilityRef.current) {
            onAddProposedFacilityRef.current([e.lngLat.lng, e.lngLat.lat]);
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
      facilityMarkersRef.current.forEach((m) => m.remove());
      facilityMarkersRef.current = [];
      proposedMarkersRef.current.forEach((m) => m.remove());
      proposedMarkersRef.current = [];
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
        // Clear facility HTML markers
        facilityMarkersRef.current.forEach((m) => m.remove());
        facilityMarkersRef.current = [];

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

    // Facilities (HTML markers — toggle display style)
    facilityMarkersRef.current.forEach((marker) => {
      marker.getElement().style.display = layerVisibility.facilities ? '' : 'none';
    });

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
  // 4. COVERAGE BUFFERS: rebuild when threshold/proposedFacilities changes
  // =====================================================================
  useEffect(() => {
    if (!map.current || !mapReady) return;
    rebuildCoverageBuffers(map.current);
  }, [threshold, proposedFacilities, mapReady]);

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

      const popupEl = document.createElement('div');
      popupEl.className = 'text-xs font-sans p-2 min-w-[170px] space-y-2';
      popupEl.innerHTML = `
        <div class="font-bold text-indigo-900 text-sm flex items-center justify-between">
          <span>Recommended Site #${rank}</span>
          <span class="text-[10px] px-1.5 py-0.5 rounded bg-indigo-100 text-indigo-800 font-bold">${Math.round(cand.combined_score)}% fit</span>
        </div>
        <div class="text-slate-600 text-[11px] mt-1">
          <div>Suitability: <strong>${Math.round(cand.suitability_score || cand.combined_score)}%</strong></div>
          <div class="text-emerald-700 font-semibold mt-0.5">+${cand.households_gained || 160} households gained</div>
        </div>
      `;

      const btnRow = document.createElement('div');
      btnRow.className = 'flex items-center gap-1.5 pt-1 border-t border-slate-200 mt-2';

      const placeBtn = document.createElement('button');
      placeBtn.className = 'flex-1 py-1 px-2 rounded-md bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-[11px] text-center transition-colors shadow-sm';
      placeBtn.innerText = '📍 Pin Facility';
      placeBtn.onclick = () => {
        if (onSelectCandidate) onSelectCandidate(cand);
        popup.remove();
      };

      const dismissBtn = document.createElement('button');
      dismissBtn.className = 'py-1 px-2 rounded-md bg-red-50 hover:bg-red-100 text-red-600 border border-red-200 font-bold text-[11px] text-center transition-colors';
      dismissBtn.innerText = '✕ Remove';
      dismissBtn.title = 'Remove this recommended location';
      dismissBtn.onclick = () => {
        if (onDismissCandidate) onDismissCandidate(cand);
        popup.remove();
      };

      btnRow.appendChild(placeBtn);
      btnRow.appendChild(dismissBtn);
      popupEl.appendChild(btnRow);

      const popup = new maplibregl.Popup({ offset: 12 }).setDOMContent(popupEl);

      const marker = new maplibregl.Marker({ element: el })
        .setLngLat(cand.location)
        .setPopup(popup)
        .addTo(map.current!);

      candidateMarkersRef.current.push(marker);
    });
  }, [candidates, layerVisibility.candidates, onSelectCandidate, onDismissCandidate, mapReady]);

  // =====================================================================
  // 7. PROPOSED FACILITY MARKERS (draggable, multi-facility support)
  // =====================================================================
  useEffect(() => {
    proposedMarkersRef.current.forEach((m) => m.remove());
    proposedMarkersRef.current = [];

    if (!map.current || !mapReady || layerVisibility.proposed === false || proposedFacilities.length === 0) return;

    proposedFacilities.forEach((fac) => {
      const objectiveIcon = OBJECTIVE_ICON[fac.objective] || '📍';
      const objectiveLabel = fac.objective.charAt(0).toUpperCase() + fac.objective.slice(1);

      const el = document.createElement('div');
      el.className = 'relative flex items-center justify-center cursor-move z-30 group';
      el.innerHTML = `
        <div class="absolute w-12 h-12 rounded-full bg-blue-500 opacity-40" style="animation: pulse 2s cubic-bezier(0.4,0,0.6,1) infinite;"></div>
        <div style="width:38px;height:38px;border-radius:50%;background:linear-gradient(135deg,#2563eb,#1d4ed8);border:3px solid #fff;box-shadow:0 4px 20px rgba(37,99,235,0.6);display:flex;align-items:center;justify-content:center;position:relative;z-index:10;user-select:none;">
          <span style="font-size:17px;line-height:1;display:inline-flex;align-items:center;justify-content:center;transform:translateY(0.5px);">${objectiveIcon}</span>
        </div>
      `;

      const popupContainer = document.createElement('div');
      popupContainer.className = 'text-xs font-sans p-1 space-y-1.5';
      popupContainer.style.minWidth = '160px';
      popupContainer.innerHTML = `
        <div class="font-bold text-slate-900 text-sm flex items-center gap-1.5">
          <span>${objectiveIcon}</span>
          <span>${fac.name}</span>
        </div>
        <div class="text-slate-600 text-[11px]">Type: <strong>${objectiveLabel}</strong></div>
        <div class="text-slate-500 text-[10px] font-mono">${fac.location[1].toFixed(5)}, ${fac.location[0].toFixed(5)}</div>
        <div class="text-[10px] text-blue-700 font-semibold bg-blue-50 p-1 rounded text-center">
          ✋ Drag to reposition
        </div>
      `;

      const deleteBtn = document.createElement('button');
      deleteBtn.className =
        'w-full py-1 px-2 rounded bg-red-500 hover:bg-red-600 active:bg-red-700 text-white font-bold text-[11px] flex items-center justify-center gap-1.5 transition-colors shadow-sm cursor-pointer';
      deleteBtn.innerHTML = '<span>🗑️</span><span>Delete Facility</span>';
      deleteBtn.onclick = (e) => {
        e.stopPropagation();
        if (onDeleteProposedFacilityRef.current) {
          onDeleteProposedFacilityRef.current(fac.id);
        }
      };
      popupContainer.appendChild(deleteBtn);

      const popup = new maplibregl.Popup({ offset: 18, closeButton: true })
        .setDOMContent(popupContainer);

      const marker = new maplibregl.Marker({ element: el, draggable: true })
        .setLngLat(fac.location)
        .setPopup(popup)
        .addTo(map.current!);

      marker.on('dragend', () => {
        const lngLat = marker.getLngLat();
        if (onUpdateProposedFacilityLocationRef.current) {
          onUpdateProposedFacilityLocationRef.current(fac.id, [lngLat.lng, lngLat.lat]);
        }
      });

      proposedMarkersRef.current.push(marker);
    });
  }, [proposedFacilities, layerVisibility.proposed, mapReady]);

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
            paint: { 'fill-color': '#2563eb', 'fill-opacity': 0.05 },
          });
          mapInstance.addLayer({
            id: 'boundary-casing', type: 'line', source: 'boundary',
            layout: { visibility: vis.boundary ? 'visible' : 'none' },
            paint: { 'line-color': '#ffffff', 'line-width': 5, 'line-opacity': 0.8 },
          });
          mapInstance.addLayer({
            id: 'boundary-line', type: 'line', source: 'boundary',
            layout: { visibility: vis.boundary ? 'visible' : 'none' },
            paint: { 'line-color': '#1d4ed8', 'line-width': 2.5, 'line-dasharray': [4, 2] },
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
          // Create individual HTML markers for each facility with type-specific icons
          buildFacilityMarkers(mapInstance, geojson, vis.facilities !== false);
        }
      } catch (layerErr) {
        console.warn(`Layer ${layerName} skipped:`, layerErr);
      }
    }
  };

  // =====================================================================
  // HELPER: Build facility markers with type-specific icons
  // =====================================================================
  const buildFacilityMarkers = (
    mapInstance: maplibregl.Map,
    geojson: GeoJSON.FeatureCollection,
    visible: boolean
  ) => {
    // Clear existing facility markers
    facilityMarkersRef.current.forEach((m) => m.remove());
    facilityMarkersRef.current = [];

    for (const feature of geojson.features) {
      if (feature.geometry.type !== 'Point') continue;

      const coords = (feature.geometry as GeoJSON.Point).coordinates as [number, number];
      const props = feature.properties || {};
      const facilityType = props.facility_type || 'unknown';
      const config = FACILITY_TYPE_CONFIG[facilityType] || DEFAULT_FACILITY_CONFIG;

      const el = document.createElement('div');
      el.style.cssText = `
        width: 32px; height: 32px; border-radius: 50%;
        background: ${config.bgColor};
        border: 2.5px solid ${config.color};
        box-shadow: 0 2px 8px ${config.color}44, 0 0 0 3px ${config.color}22;
        display: ${visible ? 'flex' : 'none'};
        align-items: center; justify-content: center;
        cursor: pointer; user-select: none;
        transition: box-shadow 0.2s, border-color 0.2s;
      `;
      el.innerHTML = `<span style="display:inline-flex;align-items:center;justify-content:center;font-size:15px;line-height:1;width:100%;height:100%;margin:0;padding:0;transform:translateY(0.5px);">${config.icon}</span>`;
      el.title = `${props.name || config.label} (${config.label})`;

      el.addEventListener('mouseenter', () => {
        el.style.boxShadow = `0 0 12px 4px ${config.color}88, 0 0 0 4px ${config.color}44`;
        el.style.borderColor = '#ffffff';
      });
      el.addEventListener('mouseleave', () => {
        el.style.boxShadow = `0 2px 8px ${config.color}44, 0 0 0 3px ${config.color}22`;
        el.style.borderColor = config.color;
      });

      const popup = new maplibregl.Popup({ offset: 14, closeButton: false }).setHTML(
        `<div class="text-xs font-sans p-1.5" style="min-width: 140px;">
          <div class="font-bold text-sm" style="color: ${config.bgColor};">${config.icon} ${props.name || 'Facility'}</div>
          <div style="color: #475569; margin-top: 4px;">Type: <strong>${config.label}</strong></div>
          ${props.capacity ? `<div style="color: #475569;">Capacity: <strong>${props.capacity}</strong></div>` : ''}
          ${props.year_established ? `<div style="color: #64748b;">Est. ${props.year_established}</div>` : ''}
          ${props.status ? `<div style="color: #059669; font-weight: 600; margin-top: 2px;">● ${props.status.charAt(0).toUpperCase() + props.status.slice(1)}</div>` : ''}
        </div>`
      );

      const marker = new maplibregl.Marker({ element: el })
        .setLngLat(coords)
        .setPopup(popup)
        .addTo(mapInstance);

      facilityMarkersRef.current.push(marker);
    }
  };

  // =====================================================================
  // HELPER: Rebuild coverage buffer polygons (for existing & all proposed)
  // =====================================================================
  const rebuildCoverageBuffers = (mapInstance: maplibregl.Map) => {
    const features: GeoJSON.Feature<GeoJSON.Polygon>[] = [];
    const currentThreshold = thresholdRef.current;
    const currentProposed = proposedFacilitiesRef.current;
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

    if (currentProposed && currentProposed.length > 0) {
      for (const fac of currentProposed) {
        features.push({
          type: 'Feature', properties: { type: 'proposed', objective: fac.objective },
          geometry: { type: 'Polygon', coordinates: [createGeoJSONCircle(fac.location, currentThreshold)] },
        });
      }
    }

    const geojson: GeoJSON.FeatureCollection = { type: 'FeatureCollection', features };

    if (mapInstance.getSource('coverage-buffers')) {
      (mapInstance.getSource('coverage-buffers') as maplibregl.GeoJSONSource).setData(geojson);
    } else {
      mapInstance.addSource('coverage-buffers', { type: 'geojson', data: geojson });
      // Insert fill layer below buildings if buildings layer exists
      const beforeLayer = mapInstance.getLayer('buildings') ? 'buildings' : undefined;
      mapInstance.addLayer(
        {
          id: 'coverage-buffers-fill',
          type: 'fill',
          source: 'coverage-buffers',
          layout: { visibility: vis.coverage ? 'visible' : 'none' },
          paint: {
            'fill-color': ['case', ['==', ['get', 'type'], 'proposed'], '#2563eb', '#10b981'],
            'fill-opacity': [
              'interpolate',
              ['linear'],
              ['zoom'],
              13,
              0.22,
              15.5,
              0.12,
              17.5,
              0.05,
            ],
          },
        },
        beforeLayer
      );
      mapInstance.addLayer(
        {
          id: 'coverage-buffers-line',
          type: 'line',
          source: 'coverage-buffers',
          layout: { visibility: vis.coverage ? 'visible' : 'none' },
          paint: {
            'line-color': ['case', ['==', ['get', 'type'], 'proposed'], '#1d4ed8', '#047857'],
            'line-width': 2,
            'line-dasharray': [4, 2],
            'line-opacity': 0.85,
          },
        },
        beforeLayer
      );
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
      const beforeLayer = mapInstance.getLayer('buildings') ? 'buildings' : undefined;
      mapInstance.addLayer(
        {
          id: 'underserved-clusters-fill',
          type: 'fill',
          source: 'underserved-clusters',
          layout: { visibility: vis.underserved ? 'visible' : 'none' },
          paint: {
            'fill-color': '#f59e0b',
            'fill-opacity': [
              'interpolate',
              ['linear'],
              ['zoom'],
              13,
              0.22,
              15.5,
              0.12,
              17.5,
              0.05,
            ],
          },
        },
        beforeLayer
      );
      mapInstance.addLayer(
        {
          id: 'underserved-clusters-line',
          type: 'line',
          source: 'underserved-clusters',
          layout: { visibility: vis.underserved ? 'visible' : 'none' },
          paint: { 'line-color': '#b45309', 'line-width': 2, 'line-dasharray': [2, 2], 'line-opacity': 0.85 },
        },
        beforeLayer
      );
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
        {/* Dynamic facility type entries from existing data */}
        {(() => {
          const types = new Set<string>();
          existingFacilitiesDataRef.current?.features?.forEach((f) => {
            const t = f.properties?.facility_type;
            if (t) types.add(t);
          });
          return Array.from(types).map((type) => {
            const cfg = FACILITY_TYPE_CONFIG[type] || DEFAULT_FACILITY_CONFIG;
            return (
              <div key={type} className="flex items-center gap-2 font-medium">
                <span
                  className="w-3.5 h-3.5 rounded-full border-2 border-white shadow-sm flex items-center justify-center text-[9px]"
                  style={{ background: cfg.bgColor, borderColor: cfg.color }}
                >
                  {cfg.icon}
                </span>
                <span className="text-slate-100">{cfg.label}</span>
              </div>
            );
          });
        })()}
        {proposedFacilities.length > 0 && (
          <div className="flex items-center gap-2 font-medium">
            <span className="w-3.5 h-3.5 rounded-full bg-blue-600 border border-white shadow-sm flex items-center justify-center text-[9px] animate-pulse">
              📍
            </span>
            <span className="text-blue-300 font-bold">
              Proposed ({proposedFacilities.length} {proposedFacilities.length === 1 ? 'Facility' : 'Facilities'})
            </span>
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
