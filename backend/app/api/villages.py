"""
Village API Routes
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import json
from pathlib import Path
import os

router = APIRouter()

# Get the project root directory (2 levels up from this file)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
VILLAGES_DIR = DATA_DIR / "villages"


def load_village_registry() -> List[Dict[str, Any]]:
    """Load village registry"""
    registry_path = DATA_DIR / "village_registry.json"
    
    if not registry_path.exists():
        raise HTTPException(status_code=500, detail="Village registry not found")
    
    with open(registry_path) as f:
        return json.load(f)


def load_geojson(filepath: Path) -> Dict[str, Any]:
    """Load GeoJSON file"""
    if not filepath.exists():
        return {
            "type": "FeatureCollection",
            "features": []
        }
    
    with open(filepath) as f:
        return json.load(f)


@router.get("/villages")
async def get_villages():
    """Get list of all villages"""
    try:
        villages = load_village_registry()
        return {
            "villages": villages,
            "count": len(villages)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/villages/{village_id}")
async def get_village(village_id: str):
    """Get detailed information about a specific village"""
    try:
        # Load registry to get village metadata
        villages = load_village_registry()
        village = next((v for v in villages if v["id"] == village_id), None)
        
        if not village:
            raise HTTPException(status_code=404, detail=f"Village {village_id} not found")
        
        return {
            "village": village,
            "data_available": True
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/villages/{village_id}/layers")
async def get_village_layers(village_id: str):
    """Get available layers for a village"""
    try:
        village_dir = VILLAGES_DIR / village_id
        
        if not village_dir.exists():
            raise HTTPException(status_code=404, detail=f"Village data directory not found: {village_id}")
        
        # Check which layers exist
        layers = {}
        layer_files = {
            "boundary": "boundary.geojson",
            "buildings": "buildings.geojson",
            "parcels": "parcels.geojson",
            "roads": "roads.geojson",
            "water_bodies": "water_bodies.geojson",
            "facilities": "facilities.geojson"
        }
        
        for layer_name, filename in layer_files.items():
            filepath = village_dir / filename
            if filepath.exists():
                # Get feature count
                data = load_geojson(filepath)
                layers[layer_name] = {
                    "available": True,
                    "feature_count": len(data.get("features", [])),
                    "geometry_type": data.get("features", [{}])[0].get("geometry", {}).get("type") if data.get("features") else None
                }
            else:
                layers[layer_name] = {
                    "available": False
                }
        
        return {
            "village_id": village_id,
            "layers": layers
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/villages/{village_id}/layers/{layer_name}")
async def get_village_layer(village_id: str, layer_name: str):
    """Get GeoJSON data for a specific layer"""
    try:
        village_dir = VILLAGES_DIR / village_id
        
        if not village_dir.exists():
            raise HTTPException(status_code=404, detail=f"Village {village_id} not found")
        
        # Map layer names to files
        layer_files = {
            "boundary": "boundary.geojson",
            "buildings": "buildings.geojson",
            "parcels": "parcels.geojson",
            "roads": "roads.geojson",
            "water_bodies": "water_bodies.geojson",
            "facilities": "facilities.geojson"
        }
        
        if layer_name not in layer_files:
            raise HTTPException(status_code=400, detail=f"Invalid layer name: {layer_name}")
        
        filepath = village_dir / layer_files[layer_name]
        
        if not filepath.exists():
            raise HTTPException(status_code=404, detail=f"Layer {layer_name} not found for village {village_id}")
        
        geojson_data = load_geojson(filepath)
        
        return geojson_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/villages/{village_id}/bounds")
async def get_village_bounds(village_id: str):
    """Get geographic bounds of a village"""
    try:
        village_dir = VILLAGES_DIR / village_id
        boundary_file = village_dir / "boundary.geojson"
        
        if not boundary_file.exists():
            raise HTTPException(status_code=404, detail=f"Boundary not found for village {village_id}")
        
        boundary_data = load_geojson(boundary_file)
        
        if not boundary_data.get("features"):
            raise HTTPException(status_code=404, detail="No boundary features found")
        
        # Calculate bounds from boundary coordinates
        coords = boundary_data["features"][0]["geometry"]["coordinates"][0]
        lons = [c[0] for c in coords]
        lats = [c[1] for c in coords]
        
        bounds = {
            "west": min(lons),
            "south": min(lats),
            "east": max(lons),
            "north": max(lats),
            "center": [
                (min(lons) + max(lons)) / 2,
                (min(lats) + max(lats)) / 2
            ]
        }
        
        return {
            "village_id": village_id,
            "bounds": bounds
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
