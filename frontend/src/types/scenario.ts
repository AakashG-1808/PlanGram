export interface ScenarioProject {
  project_id: string;
  infrastructure_type: string;
  location: [number, number];
  name: string;
  cost: number;
  status: string;
}

export interface Scenario {
  scenario_id: string;
  name: string;
  description: string;
  village_id: string;
  projects: ScenarioProject[];
  total_cost: number;
  created_at: string;
  updated_at: string;
}

export interface ScenarioSimulation {
  scenario_id: string;
  village_id: string;
  threshold_meters: number;
  before_coverage: {
    coverage_percentage: number;
    served_households: number;
    served_population: number;
    underserved_households: number;
    underserved_population: number;
    average_distance: number;
  };
  after_coverage: {
    coverage_percentage: number;
    served_households: number;
    served_population: number;
    underserved_households: number;
    underserved_population: number;
    average_distance: number;
  };
  improvement: {
    coverage_change: number;
    households_gained: number;
    population_gained: number;
    avg_distance_change: number;
  };
  total_cost: number;
  num_projects: number;
}

export interface ScenarioComparison {
  scenarios: ScenarioSimulation[];
  best_coverage_id: string;
  best_cost_efficiency_id: string;
  threshold_meters: number;
}
