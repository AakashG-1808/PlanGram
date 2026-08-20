export interface Village {
  id: string;
  name: string;
  taluk: string;
  district: string;
  state: string;
  data_mode: 'prototype' | 'uploaded' | 'official';
  area_sq_km: number;
  estimated_population: number;
  estimated_households: number;
  description: string;
  priority_infrastructure: string[];
  created_at: string;
}

export interface VillageLayer {
  available: boolean;
  feature_count?: number;
  geometry_type?: string;
}

export interface VillageLayers {
  boundary: VillageLayer;
  buildings: VillageLayer;
  parcels: VillageLayer;
  roads: VillageLayer;
  water_bodies: VillageLayer;
  facilities: VillageLayer;
}

export interface VillageBounds {
  west: number;
  south: number;
  east: number;
  north: number;
  center: [number, number];
}

export interface LayerVisibility {
  boundary: boolean;
  buildings: boolean;
  parcels: boolean;
  roads: boolean;
  water_bodies: boolean;
  facilities: boolean;
}
