"""
Scenario API Routes
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
import json
import uuid
from pathlib import Path
from datetime import datetime
from app.schemas.scenario import (
    Scenario,
    ScenarioCreate,
    ScenarioProject,
    ScenarioProjectCreate,
    ScenarioSimulation,
    ScenarioComparison
)
from app.services.gis.coverage import calculate_facility_coverage
from pydantic import BaseModel

router = APIRouter()

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
VILLAGES_DIR = DATA_DIR / "villages"
SCENARIOS_DIR = DATA_DIR / "scenarios"

# Ensure scenarios directory exists
SCENARIOS_DIR.mkdir(parents=True, exist_ok=True)


def load_geojson(filepath: Path):
    """Load GeoJSON file"""
    if not filepath.exists():
        return {"type": "FeatureCollection", "features": []}
    
    with open(filepath) as f:
        return json.load(f)


def load_cost_config():
    """Load cost configuration"""
    cost_path = DATA_DIR / "cost_config.json"
    if not cost_path.exists():
        return {}
    
    with open(cost_path) as f:
        return json.load(f)


def save_scenario(scenario: dict):
    """Save scenario to file"""
    scenario_path = SCENARIOS_DIR / f"{scenario['scenario_id']}.json"
    with open(scenario_path, 'w') as f:
        json.dump(scenario, f, indent=2)


def load_scenario(scenario_id: str):
    """Load scenario from file"""
    scenario_path = SCENARIOS_DIR / f"{scenario_id}.json"
    if not scenario_path.exists():
        raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")
    
    with open(scenario_path) as f:
        return json.load(f)


def list_scenarios(village_id: Optional[str] = None):
    """List all scenarios, optionally filtered by village"""
    scenarios = []
    
    for scenario_file in SCENARIOS_DIR.glob("*.json"):
        try:
            with open(scenario_file) as f:
                scenario = json.load(f)
                if village_id is None or scenario.get('village_id') == village_id:
                    scenarios.append(scenario)
        except Exception as e:
            print(f"Error loading scenario {scenario_file}: {e}")
            continue
    
    # Sort by created_at descending
    scenarios.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return scenarios


@router.post("/scenarios", response_model=Scenario)
async def create_scenario(scenario_data: ScenarioCreate):
    """
    Create a new scenario for infrastructure planning.
    """
    try:
        scenario_id = str(uuid.uuid4())
        
        scenario = {
            "scenario_id": scenario_id,
            "name": scenario_data.name,
            "description": scenario_data.description or "",
            "village_id": scenario_data.village_id,
            "projects": [],
            "total_cost": 0.0,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z"
        }
        
        save_scenario(scenario)
        
        return Scenario(**scenario)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scenarios", response_model=List[Scenario])
async def get_scenarios(village_id: Optional[str] = None):
    """
    Get all scenarios, optionally filtered by village.
    """
    try:
        scenarios = list_scenarios(village_id)
        return [Scenario(**s) for s in scenarios]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scenarios/{scenario_id}", response_model=Scenario)
async def get_scenario(scenario_id: str):
    """
    Get a specific scenario by ID.
    """
    try:
        scenario = load_scenario(scenario_id)
        return Scenario(**scenario)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scenarios/{scenario_id}/projects", response_model=Scenario)
async def add_project(scenario_id: str, project_data: ScenarioProjectCreate):
    """
    Add a proposed infrastructure project to a scenario.
    """
    try:
        # Load scenario
        scenario = load_scenario(scenario_id)
        
        # Load cost config
        costs = load_cost_config()
        infrastructure_costs = costs.get("infrastructure_costs", {})
        
        # Get cost for this infrastructure type
        infra_type = project_data.infrastructure_type
        base_cost = infrastructure_costs.get(infra_type, {}).get("base_cost", 0)
        
        # Create project
        project_id = str(uuid.uuid4())
        project = {
            "project_id": project_id,
            "infrastructure_type": infra_type,
            "location": project_data.location,
            "name": project_data.name or f"{infra_type.replace('_', ' ').title()} #{len(scenario['projects']) + 1}",
            "cost": base_cost,
            "status": "proposed"
        }
        
        # Add to scenario
        scenario["projects"].append(project)
        scenario["total_cost"] = sum(p["cost"] for p in scenario["projects"])
        scenario["updated_at"] = datetime.utcnow().isoformat() + "Z"
        
        save_scenario(scenario)
        
        return Scenario(**scenario)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/scenarios/{scenario_id}/projects/{project_id}", response_model=Scenario)
async def update_project(scenario_id: str, project_id: str, location: List[float]):
    """
    Update a project's location (for moving on map).
    """
    try:
        scenario = load_scenario(scenario_id)
        
        # Find and update project
        project_found = False
        for project in scenario["projects"]:
            if project["project_id"] == project_id:
                project["location"] = location
                project_found = True
                break
        
        if not project_found:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
        
        scenario["updated_at"] = datetime.utcnow().isoformat() + "Z"
        save_scenario(scenario)
        
        return Scenario(**scenario)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/scenarios/{scenario_id}/projects/{project_id}", response_model=Scenario)
async def delete_project(scenario_id: str, project_id: str):
    """
    Remove a project from a scenario.
    """
    try:
        scenario = load_scenario(scenario_id)
        
        # Remove project
        original_count = len(scenario["projects"])
        scenario["projects"] = [p for p in scenario["projects"] if p["project_id"] != project_id]
        
        if len(scenario["projects"]) == original_count:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
        
        # Recalculate total cost
        scenario["total_cost"] = sum(p["cost"] for p in scenario["projects"])
        scenario["updated_at"] = datetime.utcnow().isoformat() + "Z"
        
        save_scenario(scenario)
        
        return Scenario(**scenario)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/scenarios/{scenario_id}")
async def delete_scenario(scenario_id: str):
    """
    Delete a scenario.
    """
    try:
        scenario_path = SCENARIOS_DIR / f"{scenario_id}.json"
        if not scenario_path.exists():
            raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")
        
        scenario_path.unlink()
        
        return {"message": "Scenario deleted successfully", "scenario_id": scenario_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scenarios/{scenario_id}/simulate", response_model=ScenarioSimulation)
async def simulate_scenario(scenario_id: str, threshold: Optional[float] = 500.0):
    """
    Simulate the impact of a scenario's proposed infrastructure.
    Returns before/after coverage metrics.
    """
    try:
        # Load scenario
        scenario = load_scenario(scenario_id)
        village_id = scenario["village_id"]
        
        # Load village data
        village_dir = VILLAGES_DIR / village_id
        buildings_data = load_geojson(village_dir / "buildings.geojson")
        facilities_data = load_geojson(village_dir / "facilities.geojson")
        
        buildings = buildings_data.get("features", [])
        existing_facilities = facilities_data.get("features", [])
        
        # Map infra types
        def normalize_infra_type(itype: str) -> str:
            t = itype.lower().replace("_facility", "")
            if "health" in t or "wellness" in t or "subcenter" in t:
                return "health"
            if "school" in t or "education" in t or "anganwadi" in t:
                return "education"
            if "toilet" in t or "sanitation" in t or "stp" in t:
                return "sanitation"
            if "waste" in t or "recycl" in t:
                return "waste"
            if "bus" in t or "transit" in t or "road" in t or "connect" in t:
                return "connectivity"
            return "water"

        # Determine target sectors from projects
        project_sectors = set(normalize_infra_type(p["infrastructure_type"]) for p in scenario["projects"])
        if not project_sectors:
            project_sectors = {"water"}

        # Filter existing facilities matching target sectors
        existing_matched = [
            f for f in existing_facilities
            if normalize_infra_type(f["properties"].get("facility_type", "")) in project_sectors
        ]
        
        # Calculate BEFORE metrics (existing facilities matching sector)
        before_metrics = calculate_facility_coverage(buildings, existing_matched, threshold)
        
        # Create proposed facilities from scenario projects
        proposed_facilities = []
        for project in scenario["projects"]:
            norm_sec = normalize_infra_type(project["infrastructure_type"])
            proposed_facilities.append({
                "type": "Feature",
                "properties": {
                    "facility_id": project["project_id"],
                    "facility_type": norm_sec,
                    "name": project["name"],
                    "status": "proposed"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": project["location"]
                }
            })
        
        # Calculate AFTER metrics (existing + proposed)
        all_facilities = existing_matched + proposed_facilities
        after_metrics = calculate_facility_coverage(buildings, all_facilities, threshold)
        
        # Calculate improvements
        improvement = {
            "coverage_change": round(after_metrics["coverage_percentage"] - before_metrics["coverage_percentage"], 1),
            "households_gained": after_metrics["served_households"] - before_metrics["served_households"],
            "population_gained": after_metrics["served_population"] - before_metrics["served_population"],
            "avg_distance_change": round(after_metrics["average_distance"] - before_metrics["average_distance"], 1)
        }
        
        return ScenarioSimulation(
            scenario_id=scenario_id,
            village_id=village_id,
            threshold_meters=threshold,
            before_coverage=before_metrics,
            after_coverage=after_metrics,
            improvement=improvement,
            total_cost=scenario["total_cost"],
            num_projects=len(scenario["projects"])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scenarios/compare", response_model=ScenarioComparison)
async def compare_scenarios(scenario_ids: List[str], threshold: Optional[float] = 500.0):
    """
    Compare multiple scenarios side-by-side.
    """
    try:
        simulations = []
        
        for scenario_id in scenario_ids:
            try:
                # Simulate each scenario
                sim = await simulate_scenario(scenario_id, threshold)
                simulations.append(sim)
            except HTTPException as e:
                # Skip scenarios that can't be loaded
                print(f"Warning: Could not simulate scenario {scenario_id}: {e.detail}")
                continue
        
        if not simulations:
            raise HTTPException(status_code=404, detail="No valid scenarios found")
        
        # Find best by different criteria
        best_coverage = max(simulations, key=lambda s: s.after_coverage["coverage_percentage"])
        best_cost_efficiency = min(simulations, key=lambda s: 
            s.total_cost / max(s.improvement["households_gained"], 1))
        
        return ScenarioComparison(
            scenarios=simulations,
            best_coverage_id=best_coverage.scenario_id,
            best_cost_efficiency_id=best_cost_efficiency.scenario_id,
            threshold_meters=threshold
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
