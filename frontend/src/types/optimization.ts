/**
 * Optimization-related TypeScript types
 */

export interface OptimizationRequest {
  infrastructure_type: string;
  budget: number;
  threshold_meters: number;
  num_candidates?: number;
  scenario_count?: number;
}

export interface SelectedFacility {
  facility_id: string;
  location: [number, number];
  buildings_gained: number;
  cost: number;
  suitability_score: number;
  coverage_score: number;
}

export interface OptimizationResult {
  village_id: string;
  infrastructure_type: string;
  status: string;
  message: string;
  num_facilities: number;
  selected_facilities: SelectedFacility[];
  total_cost: number;
  remaining_budget: number;
  coverage_before: number;
  coverage_after: number;
  buildings_gained: number;
  coverage_improvement_pct: number;
  cost_per_building: number;
  budget_utilization_pct: number;
  facility_cost: number;
  threshold_meters: number;
  num_candidates_evaluated: number;
}

export interface BudgetScenario {
  scenario_id: string;
  scenario_name: string;
  budget: number;
  status: string;
  num_facilities: number;
  selected_facilities: SelectedFacility[];
  total_cost: number;
  remaining_budget: number;
  coverage_improvement_pct: number;
  cost_per_building: number;
  budget_utilization_pct: number;
  buildings_gained: number;
  coverage_after: number;
}

export interface ScenarioRecommendations {
  best_coverage: {
    scenario_id: string;
    scenario_name: string;
    coverage_after: number;
    buildings_gained: number;
  };
  best_efficiency: {
    scenario_id: string;
    scenario_name: string;
    cost_per_building: number;
    buildings_gained: number;
  };
  best_utilization: {
    scenario_id: string;
    scenario_name: string;
    budget_utilization_pct: number;
    remaining_budget: number;
  };
}

export interface ScenarioComparison {
  village_id: string;
  infrastructure_type: string;
  base_budget: number;
  facility_cost: number;
  num_scenarios: number;
  scenarios: BudgetScenario[];
  recommendations: ScenarioRecommendations;
  summary: {
    budget_range: string;
    facilities_range: string;
    coverage_range: string;
    cost_efficiency_range: string;
  };
}

export interface SensitivityBudgetLevel {
  budget: number;
  num_facilities: number;
  coverage_after: number;
  coverage_improvement_pct: number;
  cost_per_building: number;
}

export interface SensitivityAnalysis {
  village_id: string;
  infrastructure_type: string;
  base_budget: number;
  facility_cost: number;
  budget_levels: SensitivityBudgetLevel[];
  insights: {
    diminishing_returns: boolean;
    optimal_budget_range: string;
  };
}

export interface Candidate {
  rank: number;
  location: [number, number];
  combined_score: number;
  coverage_score: number;
  suitability_score: number;
  coverage_improvement: number;
  buildings_gained: number;
  households_gained: number;
  is_valid: boolean;
  violations: any[];
  warnings: any[];
}

export interface CandidateGenerationResult {
  village_id: string;
  infrastructure_type: string;
  method: string;
  threshold_meters: number;
  num_candidates: number;
  valid_candidates: number;
  candidates: Candidate[];
  summary: {
    best_candidate: Candidate | null;
    avg_coverage_improvement: number;
    avg_combined_score: number;
  };
}
