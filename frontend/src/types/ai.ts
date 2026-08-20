/**
 * AI service types for natural language queries and explanations
 */

// Natural Language Query Types

export interface QueryRequest {
  query: string;
  context?: Record<string, any>;
}

export interface Intent {
  action: 'optimize' | 'analyze' | 'validate' | 'generate_candidates' | 'compare_scenarios' | 'error';
  village_id?: string;
  infrastructure_type?: 'water' | 'waste' | 'health' | 'education';
  budget?: number;
  threshold?: number;
  method?: 'grid' | 'gap' | 'hybrid';
  num_candidates?: number;
  lat?: number;
  lng?: number;
  error?: string;
  original_query?: string;
}

export interface QueryResponse {
  query: string;
  intent: Intent;
  results?: Record<string, any>;
  explanation?: string;
  error?: string;
}

// Explanation Types

export interface ExplainRequest {
  location: {
    lat: number;
    lng: number;
    score: number;
  };
  context: {
    village_id: string;
    buildings_served: number;
    coverage_improvement: number;
    current_coverage: number;
    cost: number;
    cost_per_building?: number;
    constraints?: {
      boundary?: string;
      land_type?: string;
      water_distance?: number;
      road_distance?: number;
    };
    alternatives?: Array<{
      score: number;
    }>;
  };
}

export interface ScoringFactor {
  name: string;
  score: number;
  weight: number;
  description: string;
}

export interface ExplainResponse {
  summary: string;
  full_explanation: string;
  factors: ScoringFactor[];
  warnings: string[];
  alternatives?: string;
}

// Insights Types

export interface InsightsRequest {
  village_id: string;
  analysis_results: {
    coverage_percent: number;
    total_buildings: number;
    served_buildings: number;
    clusters?: Array<{
      building_count: number;
      priority: string;
    }>;
    high_priority_count?: number;
    medium_priority_count?: number;
  };
}

export interface Insight {
  type: 'critical' | 'opportunity' | 'warning';
  title: string;
  description: string;
  action: string;
  impact: string;
}

export interface InsightsResponse {
  insights: Insight[];
}

// AI Health Check Types

export interface AIHealthResponse {
  ai_enabled: boolean;
  provider: 'gemini' | 'openai' | 'none';
  api_key_configured: boolean;
  fallback_mode: boolean;
  features: {
    intent_parsing: boolean;
    ai_explanations: boolean;
    ai_insights: boolean;
  };
}
