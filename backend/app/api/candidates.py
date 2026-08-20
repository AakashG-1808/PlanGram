"""
Candidate Location Generation API Routes
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
import json
from pathlib import Path
from pydantic import BaseModel

from app.services.gis.candidates import (
    generate_grid_candidates,
    generate_coverage_gap_candidates,
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


class CandidateGenerationRequest(BaseModel):
    """Request for candidate generation"""
    infrastructure_type: str = "water_facility"
    method: str = "hybrid"  # "grid", "gap", "hybrid"
    num_candidates: int = 20
    threshold_meters: float = 500.0
    grid_spacing_meters: Optional[float] = 150.0


@router.post("/villages/{village_id}/generate-candidates")
async def generate_candidates(
    village_id: str,
    request: CandidateGenerationRequest
):
    """
    Generate candidate locations for infrastructure placement.
    
    Methods:
    - "grid": Regular grid sampling
    - "gap": Target coverage gaps (underserved areas)
    - "hybrid": Combination of grid and gap (recommended)
    
    Returns ranked list of candidates with:
    - Location coordinates
    - Coverage improvement score
    - Constraint suitability score
    - Combined ranking score
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
        
        # Generate candidates based on method
        if request.method == "grid":
            candidates = generate_grid_candidates(
                boundary,
                grid_spacing_meters=request.grid_spacing_meters or 150.0,
                random_offset=True
            )
            # Limit to requested number
            if len(candidates) > request.num_candidates:
                import random
                random.shuffle(candidates)
                candidates = candidates[:request.num_candidates]
        
        elif request.method == "gap":
            candidates = generate_coverage_gap_candidates(
                buildings,
                existing_facilities,
                threshold_meters=request.threshold_meters,
                num_candidates=request.num_candidates
            )
        
        else:  # hybrid (default)
            candidates = generate_hybrid_candidates(
                boundary,
                buildings,
                existing_facilities,
                threshold_meters=request.threshold_meters,
                num_grid=max(10, request.num_candidates // 2),
                num_gap=max(10, request.num_candidates // 2),
                grid_spacing_meters=request.grid_spacing_meters or 150.0
            )
            # Limit to requested number
            candidates = candidates[:request.num_candidates]
        
        if not candidates:
            return {
                "village_id": village_id,
                "infrastructure_type": request.infrastructure_type,
                "method": request.method,
                "num_candidates": 0,
                "candidates": [],
                "message": "No valid candidates found"
            }
        
        # Score each candidate for coverage improvement
        coverage_scores = []
        for candidate in candidates:
            coverage_score = score_candidate_coverage(
                candidate,
                buildings,
                existing_facilities,
                threshold_meters=request.threshold_meters
            )
            coverage_scores.append(coverage_score)
        
        # Validate each candidate against constraints
        validation_results = []
        for candidate in candidates:
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
        
        # Rank candidates using multi-objective scoring
        ranked_candidates = rank_candidates(
            candidates,
            validation_results,
            coverage_scores,
            weights={"coverage": 0.6, "suitability": 0.4}
        )
        
        # Add rank numbers
        for i, candidate in enumerate(ranked_candidates, 1):
            candidate["rank"] = i
        
        return {
            "village_id": village_id,
            "infrastructure_type": request.infrastructure_type,
            "method": request.method,
            "threshold_meters": request.threshold_meters,
            "num_candidates": len(ranked_candidates),
            "valid_candidates": sum(1 for c in ranked_candidates if c["is_valid"]),
            "candidates": ranked_candidates,
            "summary": {
                "best_candidate": ranked_candidates[0] if ranked_candidates else None,
                "avg_coverage_improvement": round(
                    sum(c["coverage_improvement"] for c in ranked_candidates) / len(ranked_candidates), 2
                ) if ranked_candidates else 0,
                "avg_combined_score": round(
                    sum(c["combined_score"] for c in ranked_candidates) / len(ranked_candidates), 2
                ) if ranked_candidates else 0
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/villages/{village_id}/candidates/top/{n}")
async def get_top_candidates(
    village_id: str,
    n: int,
    infrastructure_type: str = Query("water_facility", description="Infrastructure type"),
    threshold_meters: float = Query(500.0, description="Coverage threshold in meters")
):
    """
    Quick endpoint to get top N candidate locations.
    
    Uses hybrid method with sensible defaults.
    """
    request = CandidateGenerationRequest(
        infrastructure_type=infrastructure_type,
        method="hybrid",
        num_candidates=min(n * 2, 50),  # Generate more, return top N
        threshold_meters=threshold_meters,
        grid_spacing_meters=150.0
    )
    
    result = await generate_candidates(village_id, request)
    
    # Return only top N
    if result["candidates"]:
        result["candidates"] = result["candidates"][:n]
        result["num_candidates"] = len(result["candidates"])
    
    return result
