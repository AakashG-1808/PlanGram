"""
Analysis API Routes
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import json
from pathlib import Path
from app.services.gis.coverage import (
    calculate_facility_coverage,
    calculate_building_distances,
    identify_underserved_areas
)
from app.schemas.analysis import (
    CoverageMetrics,
    VillageMetrics,
    InfrastructureAnalysis,
    UnderservedCluster
)

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


def load_village_registry():
    """Load village registry"""
    registry_path = DATA_DIR / "village_registry.json"
    if not registry_path.exists():
        raise HTTPException(status_code=500, detail="Village registry not found")
    
    with open(registry_path) as f:
        return json.load(f)


@router.get("/villages/{village_id}/metrics", response_model=VillageMetrics)
async def get_village_metrics(
    village_id: str,
    threshold: Optional[float] = Query(500.0, description="Distance threshold in meters")
):
    """
    Get comprehensive metrics for a village including coverage analysis.
    """
    try:
        # Load village metadata
        villages = load_village_registry()
        village = next((v for v in villages if v["id"] == village_id), None)
        
        if not village:
            raise HTTPException(status_code=404, detail=f"Village {village_id} not found")
        
        village_dir = VILLAGES_DIR / village_id
        
        # Load data layers
        buildings_data = load_geojson(village_dir / "buildings.geojson")
        facilities_data = load_geojson(village_dir / "facilities.geojson")
        
        buildings = buildings_data.get("features", [])
        facilities = facilities_data.get("features", [])
        
        # Separate water facilities
        water_facilities = [
            f for f in facilities
            if f["properties"].get("facility_type") == "water"
        ]
        other_facilities = [
            f for f in facilities
            if f["properties"].get("facility_type") != "water"
        ]
        
        # Calculate coverage for water facilities
        water_coverage = None
        underserved_clusters = []
        
        if water_facilities and buildings:
            coverage_data = calculate_facility_coverage(
                buildings,
                water_facilities,
                threshold
            )
            water_coverage = CoverageMetrics(**coverage_data)
            
            # Identify underserved clusters
            clusters_data = identify_underserved_areas(
                buildings,
                water_facilities,
                threshold
            )
            underserved_clusters = [UnderservedCluster(**c) for c in clusters_data]
        
        # Calculate basic stats
        total_households = sum(
            b["properties"].get("estimated_households", 0)
            for b in buildings
        )
        total_population = sum(
            b["properties"].get("estimated_population", 0)
            for b in buildings
        )
        
        # Determine priority level
        priority_level = "medium"
        priority_factors = []
        
        if water_coverage:
            if water_coverage.coverage_percentage < 50:
                priority_level = "high"
                priority_factors.append("Low water coverage (<50%)")
            elif water_coverage.coverage_percentage < 70:
                priority_level = "medium"
                priority_factors.append("Moderate water coverage (50-70%)")
            
            if water_coverage.underserved_households > 100:
                priority_factors.append(f"{water_coverage.underserved_households} households underserved")
            
            if len(underserved_clusters) > 0:
                priority_factors.append(f"{len(underserved_clusters)} underserved clusters identified")
        
        return VillageMetrics(
            village_id=village_id,
            village_name=village["name"],
            total_households=total_households,
            total_population=total_population,
            total_buildings=len(buildings),
            area_sq_km=village["area_sq_km"],
            water_facilities=len(water_facilities),
            other_facilities=len(other_facilities),
            water_coverage=water_coverage,
            underserved_clusters=underserved_clusters,
            priority_level=priority_level,
            priority_factors=priority_factors
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/villages/{village_id}/analysis/{infrastructure_type}", response_model=InfrastructureAnalysis)
async def analyze_infrastructure(
    village_id: str,
    infrastructure_type: str,
    threshold: Optional[float] = Query(500.0, description="Distance threshold in meters")
):
    """
    Analyze coverage for specific infrastructure type.
    """
    try:
        village_dir = VILLAGES_DIR / village_id
        
        # Normalize infrastructure type
        norm_type = infrastructure_type.lower().replace("_facility", "")
        if norm_type == "healthcare":
            norm_type = "health"
        
        # Load data
        buildings_data = load_geojson(village_dir / "buildings.geojson")
        facilities_data = load_geojson(village_dir / "facilities.geojson")
        
        buildings = buildings_data.get("features", [])
        facilities = facilities_data.get("features", [])
        
        # Filter facilities by type
        typed_facilities = [
            f for f in facilities
            if f["properties"].get("facility_type") in [norm_type, infrastructure_type]
        ]
        
        total_households = sum(
            b["properties"].get("estimated_households", 1)
            for b in buildings
        )
        total_population = sum(
            b["properties"].get("estimated_population", 4)
            for b in buildings
        )
        
        if not typed_facilities:
            return InfrastructureAnalysis(
                infrastructure_type=infrastructure_type,
                facility_count=0,
                coverage=CoverageMetrics(
                    total_buildings=len(buildings),
                    total_households=total_households,
                    total_population=total_population,
                    served_households=0,
                    served_population=0,
                    underserved_households=total_households,
                    underserved_population=total_population,
                    coverage_percentage=0.0,
                    average_distance=750.0,
                    median_distance=700.0,
                    max_distance=1200.0,
                    threshold_meters=threshold,
                    distance_method="euclidean"
                ),
                underserved_clusters=[],
                recommendations=[
                    f"No {infrastructure_type.replace('_', ' ')} facilities currently exist in this village",
                    f"All {total_households} households (~{total_population} residents) currently lack nearby access",
                    "Establish initial facilities near central residential clusters"
                ]
            )
        
        # Calculate coverage
        coverage_data = calculate_facility_coverage(
            buildings,
            typed_facilities,
            threshold
        )
        coverage = CoverageMetrics(**coverage_data)
        
        # Identify underserved areas
        clusters_data = identify_underserved_areas(
            buildings,
            typed_facilities,
            threshold
        )
        underserved_clusters = [UnderservedCluster(**c) for c in clusters_data]
        
        # Generate recommendations
        recommendations = []
        if coverage.coverage_percentage < 60:
            recommendations.append(
                f"Coverage is below 60% ({coverage.coverage_percentage:.1f}%). "
                "Additional facilities needed."
            )
        if len(underserved_clusters) > 0:
            top_cluster = underserved_clusters[0]
            recommendations.append(
                f"Prioritize {top_cluster.cluster_id} serving {top_cluster.households} "
                f"households ({top_cluster.population} people)"
            )
        if coverage.average_distance > threshold:
            recommendations.append(
                f"Average distance ({coverage.average_distance:.0f}m) exceeds "
                f"threshold ({threshold:.0f}m). Consider strategic placement."
            )
        
        if not recommendations:
            recommendations.append(
                f"Coverage is adequate ({coverage.coverage_percentage:.1f}%). "
                "Monitor for population growth."
            )
        
        return InfrastructureAnalysis(
            infrastructure_type=infrastructure_type,
            facility_count=len(typed_facilities),
            coverage=coverage,
            underserved_clusters=underserved_clusters,
            recommendations=recommendations
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/villages/{village_id}/building-distances")
async def get_building_distances(
    village_id: str,
    infrastructure_type: str = Query("water", description="Infrastructure type to measure distance to")
):
    """
    Get distance from each building to nearest facility.
    Returns a heatmap-ready dataset.
    """
    try:
        village_dir = VILLAGES_DIR / village_id
        
        # Load data
        buildings_data = load_geojson(village_dir / "buildings.geojson")
        facilities_data = load_geojson(village_dir / "facilities.geojson")
        
        buildings = buildings_data.get("features", [])
        facilities = facilities_data.get("features", [])
        
        # Filter facilities by type
        typed_facilities = [
            f for f in facilities
            if f["properties"].get("facility_type") == infrastructure_type
        ]
        
        if not typed_facilities:
            return {
                "village_id": village_id,
                "infrastructure_type": infrastructure_type,
                "building_distances": {},
                "message": f"No {infrastructure_type} facilities found"
            }
        
        # Calculate distances
        distances = calculate_building_distances(buildings, typed_facilities)
        
        return {
            "village_id": village_id,
            "infrastructure_type": infrastructure_type,
            "building_distances": distances,
            "count": len(distances)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
