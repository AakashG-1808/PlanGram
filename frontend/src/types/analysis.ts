export interface CoverageMetrics {
  total_buildings: number;
  total_households: number;
  total_population: number;
  served_households: number;
  served_population: number;
  underserved_households: number;
  underserved_population: number;
  coverage_percentage: number;
  average_distance: number;
  median_distance: number;
  max_distance: number;
  threshold_meters: number;
  distance_method: string;
  underserved_buildings?: UnderservedBuilding[];
}

export interface UnderservedBuilding {
  building_id: string;
  households: number;
  population: number;
  distance: number;
  center: [number, number];
}

export interface UnderservedCluster {
  cluster_id: string;
  building_count: number;
  households: number;
  population: number;
  center: [number, number];
  avg_distance_to_facility: number;
  priority_score: number;
}

export interface VillageMetrics {
  village_id: string;
  village_name: string;
  total_households: number;
  total_population: number;
  total_buildings: number;
  area_sq_km: number;
  water_facilities: number;
  other_facilities: number;
  water_coverage: CoverageMetrics | null;
  underserved_clusters: UnderservedCluster[];
  priority_level: 'low' | 'medium' | 'high';
  priority_factors: string[];
}

export interface InfrastructureAnalysis {
  infrastructure_type: string;
  facility_count: number;
  coverage: CoverageMetrics;
  underserved_clusters: UnderservedCluster[];
  recommendations: string[];
}
