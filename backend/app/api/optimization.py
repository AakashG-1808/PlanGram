"""
Budget Optimization API Routes
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
import json
from pathlib import Path
from pydantic import BaseModel

from app.services.optimization.budget_optimizer import (
    greedy_optimization,
    generate_budget_scenarios,
    compare_scenarios,
    sensitivity_analysis
)
from app.services.gis.candidates import (
    generate_hybrid_candidates,
    score_candidate_coverage,
    rank_candidates
)
from app.services.gis.constraints import validate_location_constraints

router = APIRouter()

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
VILLAGES_DIR = DATA_DIR / "villages"


def load_geojson(filepath: Path):
    """Load GeoJSON file"""
    if not filepath.exists():
        return {"type": "FeatureCollection", "features": []}
    
    with open(filepath) as f:
        return json.load(f)


def load_cost_config():
    """Load cost configuration"""
    cost_file = DATA_DIR / "cost_config.json"
    if cost_file.exists():
        with open(cost_file) as f:
            return json.load(f)
    return {}


class OptimizationRequest(BaseModel):
    """Request for budget optimization"""
    infrastructure_type: str = "water_facility"
    budget: float  # Total budget in rupees
    threshold_meters: float = 500.0
    num_candidates: int = 30  # Generate more candidates for better optimization
    scenario_count: int = 3  # Number of budget scenarios


@router.post("/villages/{village_id}/optimize")
async def optimize_budget(
    village_id: str,
    request: OptimizationRequest
):
    """
    Optimize infrastructure placement within budget constraint.
    
    Uses greedy algorithm to:
    1. Generate candidate locations
    2. Iteratively select facilities that maximize marginal coverage
    3. Stop when budget exhausted or no more improvement
    
    Returns:
        - Selected facility locations
        - Total cost and remaining budget
        - Coverage improvement metrics
        - Cost efficiency metrics
    """
    try:
        village_dir = VILLAGES_DIR / village_id
        
        # Load GIS data
        boundary_data = load_geojson(village_dir / "boundary.geojson")
        buildings_data = load_geojson(village_dir / "buildings.geojson")
        facilities_data = load_geojson(village_dir / "facilities.geojson")
        parcels_data = load_geojson(village_dir / "parcels.geojson")
        water_bodies_data = load_geojson(village_dir / "water_bodies.geojson")
        roads_data = load_geojson(village_dir / "roads.geojson")
        
        boundary = boundary_data.get("features", [])
        buildings = buildings_data.get("features", [])
        all_facilities = facilities_data.get("features", [])
        parcels = parcels_data.get("features", [])
        water_bodies = water_bodies_data.get("features", [])
        roads = roads_data.get("features", [])
        
        # Filter facilities by type
        facility_type = request.infrastructure_type.replace("_facility", "")
        existing_facilities = [
            f for f in all_facilities
            if f["properties"].get("facility_type") == facility_type
        ]
        
        # Get facility cost from config
        cost_config = load_cost_config()
        facility_cost = cost_config.get("infrastructure_costs", {}).get(
            request.infrastructure_type, {}
        ).get("base_cost", 180000)  # Default: ₹1,80,000
        
        # Generate candidates
        from app.services.gis.candidates import generate_hybrid_candidates
        candidates_locations = generate_hybrid_candidates(
            boundary,
            buildings,
            existing_facilities,
            threshold_meters=request.threshold_meters,
            num_grid=request.num_candidates // 2,
            num_gap=request.num_candidates // 2,
            grid_spacing_meters=150.0
        )
        
        if not candidates_locations:
            return {
                "village_id": village_id,
                "status": "no_candidates",
                "message": "No valid candidate locations found",
                "selected_facilities": [],
                "total_cost": 0
            }
        
        # Score and validate candidates
        coverage_scores = []
        for candidate in candidates_locations:
            coverage_score = score_candidate_coverage(
                candidate,
                buildings,
                existing_facilities,
                threshold_meters=request.threshold_meters
            )
            coverage_scores.append(coverage_score)
        
        validation_results = []
        for candidate in candidates_locations:
            validation = validate_location_constraints(
                candidate,
                boundary,
                parcels,
                water_bodies,
                roads,
                existing_facilities,
                request.infrastructure_type
            )
            validation_results.append(validation)
        
        # Rank candidates
        ranked_candidates = rank_candidates(
            candidates_locations,
            validation_results,
            coverage_scores,
            weights={"coverage": 0.6, "suitability": 0.4}
        )
        
        # Run optimization
        result = greedy_optimization(
            ranked_candidates,
            buildings,
            existing_facilities,
            request.budget,
            facility_cost,
            request.threshold_meters
        )
        
        result["village_id"] = village_id
        result["infrastructure_type"] = request.infrastructure_type
        result["facility_cost"] = facility_cost
        result["threshold_meters"] = request.threshold_meters
        result["num_candidates_evaluated"] = len(ranked_candidates)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/villages/{village_id}/optimize/scenarios")
async def optimize_scenarios(
    village_id: str,
    request: OptimizationRequest
):
    """
    Generate multiple budget scenarios (conservative, moderate, aggressive).
    
    Helps planners understand budget-coverage tradeoffs.
    
    Returns:
        - Multiple optimization results for different budgets
        - Comparison and recommendations
        - Sensitivity insights
    """
    try:
        village_dir = VILLAGES_DIR / village_id
        
        # Load GIS data (same as optimize_budget)
        boundary_data = load_geojson(village_dir / "boundary.geojson")
        buildings_data = load_geojson(village_dir / "buildings.geojson")
        facilities_data = load_geojson(village_dir / "facilities.geojson")
        parcels_data = load_geojson(village_dir / "parcels.geojson")
        water_bodies_data = load_geojson(village_dir / "water_bodies.geojson")
        roads_data = load_geojson(village_dir / "roads.geojson")
        
        boundary = boundary_data.get("features", [])
        buildings = buildings_data.get("features", [])
        all_facilities = facilities_data.get("features", [])
        parcels = parcels_data.get("features", [])
        water_bodies = water_bodies_data.get("features", [])
        roads = roads_data.get("features", [])
        
        facility_type = request.infrastructure_type.replace("_facility", "")
        existing_facilities = [
            f for f in all_facilities
            if f["properties"].get("facility_type") == facility_type
        ]
        
        # Get facility cost
        cost_config = load_cost_config()
        facility_cost = cost_config.get("infrastructure_costs", {}).get(
            request.infrastructure_type, {}
        ).get("base_cost", 180000)
        
        # Generate and rank candidates
        candidates_locations = generate_hybrid_candidates(
            boundary,
            buildings,
            existing_facilities,
            threshold_meters=request.threshold_meters,
            num_grid=request.num_candidates // 2,
            num_gap=request.num_candidates // 2,
            grid_spacing_meters=150.0
        )
        
        if not candidates_locations:
            return {
                "village_id": village_id,
                "status": "no_candidates",
                "message": "No valid candidate locations found"
            }
        
        # Score and validate
        coverage_scores = []
        for candidate in candidates_locations:
            coverage_score = score_candidate_coverage(
                candidate,
                buildings,
                existing_facilities,
                threshold_meters=request.threshold_meters
            )
            coverage_scores.append(coverage_score)
        
        validation_results = []
        for candidate in candidates_locations:
            validation = validate_location_constraints(
                candidate,
                boundary,
                parcels,
                water_bodies,
                roads,
                existing_facilities,
                request.infrastructure_type
            )
            validation_results.append(validation)
        
        ranked_candidates = rank_candidates(
            candidates_locations,
            validation_results,
            coverage_scores,
            weights={"coverage": 0.6, "suitability": 0.4}
        )
        
        # Generate budget scenarios
        scenarios = generate_budget_scenarios(
            ranked_candidates,
            buildings,
            existing_facilities,
            request.budget,
            facility_cost,
            request.threshold_meters,
            scenario_count=request.scenario_count
        )
        
        # Compare scenarios
        comparison = compare_scenarios(scenarios)
        
        comparison["village_id"] = village_id
        comparison["infrastructure_type"] = request.infrastructure_type
        comparison["base_budget"] = request.budget
        comparison["facility_cost"] = facility_cost
        
        return comparison
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/villages/{village_id}/optimize/sensitivity")
async def analyze_sensitivity(
    village_id: str,
    infrastructure_type: str = Query("water_facility"),
    base_budget: float = Query(..., description="Base budget for sensitivity analysis"),
    threshold_meters: float = Query(500.0)
):
    """
    Perform budget sensitivity analysis.
    
    Shows how coverage changes with budget variations (50% to 200% of base).
    Identifies optimal budget range and diminishing returns.
    """
    try:
        village_dir = VILLAGES_DIR / village_id
        
        # Load GIS data
        boundary_data = load_geojson(village_dir / "boundary.geojson")
        buildings_data = load_geojson(village_dir / "buildings.geojson")
        facilities_data = load_geojson(village_dir / "facilities.geojson")
        parcels_data = load_geojson(village_dir / "parcels.geojson")
        water_bodies_data = load_geojson(village_dir / "water_bodies.geojson")
        roads_data = load_geojson(village_dir / "roads.geojson")
        
        boundary = boundary_data.get("features", [])
        buildings = buildings_data.get("features", [])
        all_facilities = facilities_data.get("features", [])
        parcels = parcels_data.get("features", [])
        water_bodies = water_bodies_data.get("features", [])
        roads = roads_data.get("features", [])
        
        facility_type = infrastructure_type.replace("_facility", "")
        existing_facilities = [
            f for f in all_facilities
            if f["properties"].get("facility_type") == facility_type
        ]
        
        # Get facility cost
        cost_config = load_cost_config()
        facility_cost = cost_config.get("infrastructure_costs", {}).get(
            infrastructure_type, {}
        ).get("base_cost", 180000)
        
        # Generate candidates
        candidates_locations = generate_hybrid_candidates(
            boundary,
            buildings,
            existing_facilities,
            threshold_meters=threshold_meters,
            num_grid=15,
            num_gap=15,
            grid_spacing_meters=150.0
        )
        
        if not candidates_locations:
            return {
                "village_id": village_id,
                "status": "no_candidates",
                "message": "No valid candidate locations found"
            }
        
        # Score and validate
        coverage_scores = []
        for candidate in candidates_locations:
            coverage_score = score_candidate_coverage(
                candidate,
                buildings,
                existing_facilities,
                threshold_meters=threshold_meters
            )
            coverage_scores.append(coverage_score)
        
        validation_results = []
        for candidate in candidates_locations:
            validation = validate_location_constraints(
                candidate,
                boundary,
                parcels,
                water_bodies,
                roads,
                existing_facilities,
                infrastructure_type
            )
            validation_results.append(validation)
        
        ranked_candidates = rank_candidates(
            candidates_locations,
            validation_results,
            coverage_scores,
            weights={"coverage": 0.6, "suitability": 0.4}
        )
        
        # Perform sensitivity analysis
        analysis = sensitivity_analysis(
            ranked_candidates,
            buildings,
            existing_facilities,
            base_budget,
            facility_cost,
            threshold_meters
        )
        
        analysis["village_id"] = village_id
        analysis["infrastructure_type"] = infrastructure_type
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
