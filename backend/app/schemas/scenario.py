"""
Pydantic schemas for scenario endpoints
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class ScenarioProjectCreate(BaseModel):
    """Create a new project within a scenario"""
    infrastructure_type: str
    location: List[float]  # [lon, lat]
    name: Optional[str] = None


class ScenarioProject(BaseModel):
    """Infrastructure project within a scenario"""
    project_id: str
    infrastructure_type: str
    location: List[float]
    name: str
    cost: float
    status: str = "proposed"


class ScenarioCreate(BaseModel):
    """Create a new scenario"""
    name: str
    village_id: str
    description: Optional[str] = None


class Scenario(BaseModel):
    """Complete scenario with projects"""
    scenario_id: str
    name: str
    description: str
    village_id: str
    projects: List[ScenarioProject] = []
    total_cost: float = 0.0
    created_at: str
    updated_at: str


class ScenarioSimulation(BaseModel):
    """Simulation results for a scenario"""
    scenario_id: str
    village_id: str
    threshold_meters: float
    before_coverage: Dict[str, Any]
    after_coverage: Dict[str, Any]
    improvement: Dict[str, float]
    total_cost: float
    num_projects: int


class ScenarioComparison(BaseModel):
    """Comparison of multiple scenarios"""
    scenarios: List[ScenarioSimulation]
    best_coverage_id: str
    best_cost_efficiency_id: str
    threshold_meters: float
