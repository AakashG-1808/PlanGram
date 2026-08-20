import axios from 'axios';
import type { Village, VillageLayers, VillageBounds } from '../types/village';
import type { VillageMetrics, InfrastructureAnalysis } from '../types/analysis';
import type { Scenario, ScenarioSimulation, ScenarioComparison } from '../types/scenario';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const villageApi = {
  // Get all villages
  getVillages: async () => {
    const response = await api.get<{ villages: Village[]; count: number }>('/villages');
    return response.data;
  },

  // Get specific village
  getVillage: async (villageId: string) => {
    const response = await api.get<{ village: Village; data_available: boolean }>(
      `/villages/${villageId}`
    );
    return response.data;
  },

  // Get village layers info
  getVillageLayers: async (villageId: string) => {
    const response = await api.get<{ village_id: string; layers: VillageLayers }>(
      `/villages/${villageId}/layers`
    );
    return response.data;
  },

  // Get specific layer data
  getVillageLayer: async (villageId: string, layerName: string) => {
    const response = await api.get<GeoJSON.FeatureCollection>(
      `/villages/${villageId}/layers/${layerName}`
    );
    return response.data;
  },

  // Get village bounds
  getVillageBounds: async (villageId: string) => {
    const response = await api.get<{ village_id: string; bounds: VillageBounds }>(
      `/villages/${villageId}/bounds`
    );
    return response.data;
  },
};

export const analysisApi = {
  // Get village metrics with coverage analysis
  getVillageMetrics: async (villageId: string, threshold?: number) => {
    const params = threshold ? { threshold } : {};
    const response = await api.get<VillageMetrics>(
      `/villages/${villageId}/metrics`,
      { params }
    );
    return response.data;
  },

  // Get infrastructure-specific analysis
  getInfrastructureAnalysis: async (
    villageId: string,
    infrastructureType: string,
    threshold?: number
  ) => {
    const params = threshold ? { threshold } : {};
    const response = await api.get<InfrastructureAnalysis>(
      `/villages/${villageId}/analysis/${infrastructureType}`,
      { params }
    );
    return response.data;
  },

  // Get building distances for heatmap
  getBuildingDistances: async (villageId: string, infrastructureType: string) => {
    const response = await api.get<{
      village_id: string;
      infrastructure_type: string;
      building_distances: Record<string, number>;
      count: number;
    }>(`/villages/${villageId}/building-distances`, {
      params: { infrastructure_type: infrastructureType },
    });
    return response.data;
  },
};

export const scenarioApi = {
  // Create new scenario
  createScenario: async (name: string, villageId: string, description?: string) => {
    const response = await api.post<Scenario>('/scenarios', {
      name,
      village_id: villageId,
      description,
    });
    return response.data;
  },

  // Get all scenarios
  getScenarios: async (villageId?: string) => {
    const params = villageId ? { village_id: villageId } : {};
    const response = await api.get<Scenario[]>('/scenarios', { params });
    return response.data;
  },

  // Get specific scenario
  getScenario: async (scenarioId: string) => {
    const response = await api.get<Scenario>(`/scenarios/${scenarioId}`);
    return response.data;
  },

  // Add project to scenario
  addProject: async (
    scenarioId: string,
    infrastructureType: string,
    location: [number, number],
    name?: string
  ) => {
    const response = await api.post<Scenario>(
      `/scenarios/${scenarioId}/projects`,
      {
        infrastructure_type: infrastructureType,
        location,
        name,
      }
    );
    return response.data;
  },

  // Update project location
  updateProject: async (
    scenarioId: string,
    projectId: string,
    location: [number, number]
  ) => {
    const response = await api.put<Scenario>(
      `/scenarios/${scenarioId}/projects/${projectId}`,
      location
    );
    return response.data;
  },

  // Delete project
  deleteProject: async (scenarioId: string, projectId: string) => {
    const response = await api.delete<Scenario>(
      `/scenarios/${scenarioId}/projects/${projectId}`
    );
    return response.data;
  },

  // Delete scenario
  deleteScenario: async (scenarioId: string) => {
    const response = await api.delete(`/scenarios/${scenarioId}`);
    return response.data;
  },

  // Simulate scenario
  simulateScenario: async (scenarioId: string, threshold?: number) => {
    const params = threshold ? { threshold } : {};
    const response = await api.post<ScenarioSimulation>(
      `/scenarios/${scenarioId}/simulate`,
      null,
      { params }
    );
    return response.data;
  },

  // Compare scenarios
  compareScenarios: async (scenarioIds: string[], threshold?: number) => {
    const params = threshold ? { threshold } : {};
    const response = await api.post<ScenarioComparison>(
      '/scenarios/compare',
      scenarioIds,
      { params }
    );
    return response.data;
  },
};

export default api;

// Constraints API
export const constraintsApi = {
  // Validate single location
  validateLocation: async (
    villageId: string,
    location: [number, number],
    infrastructureType: string = 'water_facility'
  ) => {
    const response = await api.post(
      `/villages/${villageId}/validate-location`,
      {
        location,
        infrastructure_type: infrastructureType,
      }
    );
    return response.data;
  },

  // Validate multiple locations
  validateLocations: async (
    villageId: string,
    locations: [number, number][],
    infrastructureType: string = 'water_facility'
  ) => {
    const response = await api.post(
      `/villages/${villageId}/validate-locations`,
      {
        locations,
        infrastructure_type: infrastructureType,
      }
    );
    return response.data;
  },

  // Get buildable area statistics
  getBuildableArea: async (villageId: string) => {
    const response = await api.get(`/villages/${villageId}/buildable-area`);
    return response.data;
  },
};

// Candidates API
export const candidatesApi = {
  // Generate candidate locations
  generate: async (
    villageId: string,
    options: {
      infrastructure_type?: string;
      method?: 'grid' | 'gap' | 'hybrid';
      num_candidates?: number;
      threshold_meters?: number;
      grid_spacing_meters?: number;
    }
  ) => {
    const response = await api.post(
      `/villages/${villageId}/generate-candidates`,
      {
        infrastructure_type: options.infrastructure_type || 'water_facility',
        method: options.method || 'hybrid',
        num_candidates: options.num_candidates || 20,
        threshold_meters: options.threshold_meters || 500,
        grid_spacing_meters: options.grid_spacing_meters || 150,
      }
    );
    return response.data;
  },

  // Get top N candidates
  getTopN: async (
    villageId: string,
    n: number,
    options: {
      infrastructure_type?: string;
      threshold_meters?: number;
    } = {}
  ) => {
    const response = await api.get(
      `/villages/${villageId}/candidates/top/${n}`,
      {
        params: {
          infrastructure_type: options.infrastructure_type || 'water_facility',
          threshold_meters: options.threshold_meters || 500,
        },
      }
    );
    return response.data;
  },
};

// Optimization API
export const optimizationApi = {
  // Optimize for single budget
  optimize: async (
    villageId: string,
    options: {
      infrastructure_type?: string;
      budget: number;
      threshold_meters?: number;
      num_candidates?: number;
    }
  ) => {
    const response = await api.post(`/villages/${villageId}/optimize`, {
      infrastructure_type: options.infrastructure_type || 'water_facility',
      budget: options.budget,
      threshold_meters: options.threshold_meters || 500,
      num_candidates: options.num_candidates || 30,
    });
    return response.data;
  },

  // Generate budget scenarios
  scenarios: async (
    villageId: string,
    options: {
      infrastructure_type?: string;
      budget: number;
      threshold_meters?: number;
      num_candidates?: number;
      scenario_count?: number;
    }
  ) => {
    const response = await api.post(`/villages/${villageId}/optimize/scenarios`, {
      infrastructure_type: options.infrastructure_type || 'water_facility',
      budget: options.budget,
      threshold_meters: options.threshold_meters || 500,
      num_candidates: options.num_candidates || 30,
      scenario_count: options.scenario_count || 3,
    });
    return response.data;
  },

  // Sensitivity analysis
  sensitivity: async (
    villageId: string,
    options: {
      infrastructure_type?: string;
      base_budget: number;
      threshold_meters?: number;
    }
  ) => {
    const response = await api.post(
      `/villages/${villageId}/optimize/sensitivity`,
      null,
      {
        params: {
          infrastructure_type: options.infrastructure_type || 'water_facility',
          base_budget: options.base_budget,
          threshold_meters: options.threshold_meters || 500,
        },
      }
    );
    return response.data;
  },
};

// AI API
import type {
  QueryRequest,
  QueryResponse,
  ExplainRequest,
  ExplainResponse,
  InsightsRequest,
  InsightsResponse,
  AIHealthResponse,
} from '../types/ai';

export const aiApi = {
  // Parse natural language query
  query: async (request: QueryRequest): Promise<QueryResponse> => {
    const response = await api.post<QueryResponse>('/ai/query', request);
    return response.data;
  },

  // Explain recommendation
  explain: async (request: ExplainRequest): Promise<ExplainResponse> => {
    const response = await api.post<ExplainResponse>('/ai/explain', request);
    return response.data;
  },

  // Generate insights
  generateInsights: async (request: InsightsRequest): Promise<InsightsResponse> => {
    const response = await api.post<InsightsResponse>('/ai/insights', request);
    return response.data;
  },

  // Check AI health
  healthCheck: async (): Promise<AIHealthResponse> => {
    const response = await api.get<AIHealthResponse>('/ai/health');
    return response.data;
  },
};
