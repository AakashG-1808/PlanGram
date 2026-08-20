"""
Constraint Validation API Routes
"""

from fastapi import APIRouter, HTTPException, Body
from typing import List, Dict, Any
import json
from pathlib import Path
from app.services.gis.constraints import (
    validate_location_constraints,
    validate_multiple_locations,
    get_buildable_area
)
from pydantic import BaseModel

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


class LocationValidation(BaseModel):
    """Request for location validation"""
    location: List[float]
    infrastructure_type: str = "water_facility"


class MultiLocationValidation(BaseModel):
    """Request for multiple location validation"""
    locations: List[List[float]]
    infrastructure_type: str = "water_facility"


@router.post("/villages/{village_id}/validate-location")
async def validate_location(
    village_id: str,
    validation_request: LocationValidation
):
    """
    Validate a proposed infrastructure location against constraints.
    
    Returns validation result with:
    - is_valid: Whether location passes all critical constraints
    - violations: List of critical constraint violations
    - warnings: List of non-critical issues
    - suitability_score: Overall score (0-100)
    - summary: Human-readable summary
    """
    try:
        village_dir = VILLAGES_DIR / village_id
        
        # Load GIS data
        boundary_data = load_geojson(village_dir / "boundary.geojson")
        parcels_data = load_geojson(village_dir / "parcels.geojson")
        water_bodies_data = load_geojson(village_dir / "water_bodies.geojson")
        roads_data = load_geojson(village_dir / "roads.geojson")
        facilities_data = load_geojson(village_dir / "facilities.geojson")
        
        boundary = boundary_data.get("features", [])
        parcels = parcels_data.get("features", [])
        water_bodies = water_bodies_data.get("features", [])
        roads = roads_data.get("features", [])
        facilities = facilities_data.get("features", [])
        
        # Filter facilities by type
        typed_facilities = [
            f for f in facilities
            if f["properties"].get("facility_type") == validation_request.infrastructure_type.replace("_facility", "")
        ]
        
        # Validate location
        result = validate_location_constraints(
            validation_request.location,
            boundary,
            parcels,
            water_bodies,
            roads,
            typed_facilities,
            validation_request.infrastructure_type
        )
        
        result["village_id"] = village_id
        result["location"] = validation_request.location
        result["infrastructure_type"] = validation_request.infrastructure_type
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/villages/{village_id}/validate-locations")
async def validate_locations(
    village_id: str,
    validation_request: MultiLocationValidation
):
    """
    Validate multiple proposed locations and rank by suitability.
    
    Returns list of validation results sorted by suitability score.
    """
    try:
        village_dir = VILLAGES_DIR / village_id
        
        # Load GIS data
        boundary_data = load_geojson(village_dir / "boundary.geojson")
        parcels_data = load_geojson(village_dir / "parcels.geojson")
        water_bodies_data = load_geojson(village_dir / "water_bodies.geojson")
        roads_data = load_geojson(village_dir / "roads.geojson")
        facilities_data = load_geojson(village_dir / "facilities.geojson")
        
        boundary = boundary_data.get("features", [])
        parcels = parcels_data.get("features", [])
        water_bodies = water_bodies_data.get("features", [])
        roads = roads_data.get("features", [])
        facilities = facilities_data.get("features", [])
        
        # Filter facilities by type
        typed_facilities = [
            f for f in facilities
            if f["properties"].get("facility_type") == validation_request.infrastructure_type.replace("_facility", "")
        ]
        
        # Validate all locations
        results = validate_multiple_locations(
            validation_request.locations,
            boundary,
            parcels,
            water_bodies,
            roads,
            typed_facilities,
            validation_request.infrastructure_type
        )
        
        return {
            "village_id": village_id,
            "infrastructure_type": validation_request.infrastructure_type,
            "total_locations": len(results),
            "valid_locations": sum(1 for r in results if r["is_valid"]),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/villages/{village_id}/buildable-area")
async def get_village_buildable_area(village_id: str):
    """
    Get buildable area statistics for a village.
    
    Returns:
    - Total village area
    - Restricted area (private parcels, water bodies)
    - Buildable area
    - Percentage buildable
    """
    try:
        village_dir = VILLAGES_DIR / village_id
        
        # Load GIS data
        boundary_data = load_geojson(village_dir / "boundary.geojson")
        parcels_data = load_geojson(village_dir / "parcels.geojson")
        water_bodies_data = load_geojson(village_dir / "water_bodies.geojson")
        
        boundary = boundary_data.get("features", [])
        parcels = parcels_data.get("features", [])
        water_bodies = water_bodies_data.get("features", [])
        
        # Calculate buildable area
        result = get_buildable_area(boundary, parcels, water_bodies)
        result["village_id"] = village_id
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
