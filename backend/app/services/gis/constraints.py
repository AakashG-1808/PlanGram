"""
Constraint Validation Service

Validates proposed infrastructure locations against spatial constraints:
- Village boundary
- Parcel conflicts (private/restricted land)
- Water body conflicts
- Road accessibility
- Exclusion zones
"""

from typing import List, Dict, Any, Tuple
from shapely.geometry import Point, shape
from shapely.ops import nearest_points
import math


def point_in_polygon(point: Point, polygon_geom: Dict) -> bool:
    """Check if point is inside polygon"""
    try:
        polygon = shape(polygon_geom)
        return polygon.contains(point)
    except Exception as e:
        print(f"Error checking point in polygon: {e}")
        return False


def distance_to_nearest(point: Point, features: List[Dict]) -> float:
    """Calculate distance to nearest feature in meters"""
    if not features:
        return float('inf')
    
    min_distance = float('inf')
    
    for feature in features:
        try:
            geom = shape(feature["geometry"])
            distance = point.distance(geom)
            # Convert degrees to meters (approximate)
            distance_meters = distance * 111000
            if distance_meters < min_distance:
                min_distance = distance_meters
        except Exception as e:
            print(f"Error calculating distance: {e}")
            continue
    
    return min_distance


def validate_location_constraints(
    location: List[float],
    boundary: List[Dict],
    parcels: List[Dict],
    water_bodies: List[Dict],
    roads: List[Dict],
    existing_facilities: List[Dict],
    infrastructure_type: str = "water_facility"
) -> Dict[str, Any]:
    """
    Validate a proposed location against all constraints.
    
    Args:
        location: [lon, lat] coordinates
        boundary: Village boundary features
        parcels: Parcel features
        water_bodies: Water body features
        roads: Road features
        existing_facilities: Existing facility features
        infrastructure_type: Type of infrastructure being proposed
    
    Returns:
        Validation result with is_valid flag and constraint details
    """
    point = Point(location[0], location[1])
    
    constraints = {
        "is_valid": True,
        "violations": [],
        "warnings": [],
        "scores": {},
        "details": {}
    }
    
    # 1. Check village boundary
    if boundary:
        boundary_feature = boundary[0] if boundary else None
        if boundary_feature:
            inside_boundary = point_in_polygon(point, boundary_feature["geometry"])
            constraints["details"]["inside_boundary"] = inside_boundary
            
            if not inside_boundary:
                constraints["is_valid"] = False
                constraints["violations"].append({
                    "type": "boundary_violation",
                    "severity": "critical",
                    "message": "Location is outside village boundary"
                })
            else:
                constraints["scores"]["boundary"] = 100
    
    # 2. Check parcel conflicts
    parcel_conflicts = []
    for parcel in parcels:
        if point_in_polygon(point, parcel["geometry"]):
            parcel_type = parcel["properties"].get("parcel_type", "unknown")
            owner_type = parcel["properties"].get("owner_type", "unknown")
            restricted = parcel["properties"].get("restricted", False)
            
            # Critical: Private or restricted parcels
            if owner_type == "private" or restricted:
                constraints["is_valid"] = False
                constraints["violations"].append({
                    "type": "parcel_conflict",
                    "severity": "critical",
                    "message": f"Location conflicts with {owner_type} {parcel_type} parcel",
                    "parcel_id": parcel["properties"].get("parcel_id")
                })
                parcel_conflicts.append(parcel)
            
            # Warning: Agricultural or commercial parcels
            elif parcel_type in ["agricultural", "commercial"]:
                constraints["warnings"].append({
                    "type": "parcel_warning",
                    "severity": "warning",
                    "message": f"Location on {parcel_type} land - may require negotiation",
                    "parcel_id": parcel["properties"].get("parcel_id")
                })
            
            # OK: Public or government parcels
            elif owner_type in ["government", "public", "common"]:
                constraints["scores"]["parcel"] = 100
    
    constraints["details"]["parcel_conflicts"] = len(parcel_conflicts)
    
    # 3. Check water body conflicts
    water_conflicts = []
    min_water_distance = distance_to_nearest(point, water_bodies)
    # Handle infinity (no water bodies)
    if min_water_distance == float('inf'):
        constraints["details"]["distance_to_water"] = None
        constraints["scores"]["water_buffer"] = 100
    else:
        constraints["details"]["distance_to_water"] = round(min_water_distance, 1)
    
    # Critical: Too close to water (< 10m)
    if min_water_distance != float('inf') and min_water_distance < 10:
        constraints["is_valid"] = False
        constraints["violations"].append({
            "type": "water_body_conflict",
            "severity": "critical",
            "message": f"Too close to water body ({min_water_distance:.1f}m < 10m minimum)",
            "distance": round(min_water_distance, 1)
        })
    # Warning: Close to water (10-30m)
    elif min_water_distance != float('inf') and min_water_distance < 30:
        constraints["warnings"].append({
            "type": "water_proximity",
            "severity": "warning",
            "message": f"Close to water body ({min_water_distance:.1f}m). Verify flood risk.",
            "distance": round(min_water_distance, 1)
        })
        constraints["scores"]["water_buffer"] = 50
    else:
        if min_water_distance != float('inf'):
            constraints["scores"]["water_buffer"] = 100
    
    # 4. Check road accessibility
    min_road_distance = distance_to_nearest(point, roads)
    # Handle infinity (no roads)
    if min_road_distance == float('inf'):
        constraints["details"]["distance_to_road"] = None
        constraints["scores"]["road_access"] = 30  # Poor access if no roads
        constraints["warnings"].append({
            "type": "road_access",
            "severity": "warning",
            "message": "No roads found nearby. Access may be very challenging.",
            "distance": None
        })
    else:
        constraints["details"]["distance_to_road"] = round(min_road_distance, 1)
    
    # Scoring: Closer to roads is better (only if roads exist)
    if min_road_distance != float('inf'):
        if min_road_distance < 50:
            constraints["scores"]["road_access"] = 100
        elif min_road_distance < 100:
            constraints["scores"]["road_access"] = 80
            constraints["warnings"].append({
                "type": "road_access",
                "severity": "info",
                "message": f"Moderate distance to road ({min_road_distance:.1f}m)",
                "distance": round(min_road_distance, 1)
            })
        elif min_road_distance < 200:
            constraints["scores"]["road_access"] = 60
            constraints["warnings"].append({
                "type": "road_access",
                "severity": "warning",
                "message": f"Far from road ({min_road_distance:.1f}m). Access may be challenging.",
                "distance": round(min_road_distance, 1)
            })
        else:
            constraints["scores"]["road_access"] = 30
            constraints["warnings"].append({
                "type": "road_access",
                "severity": "warning",
                "message": f"Very far from road ({min_road_distance:.1f}m). Poor accessibility.",
                "distance": round(min_road_distance, 1)
            })
    
    # 5. Check proximity to existing facilities
    if existing_facilities:
        min_facility_distance = distance_to_nearest(point, existing_facilities)
        # Handle infinity (no existing facilities)
        if min_facility_distance == float('inf'):
            constraints["details"]["distance_to_existing"] = None
            constraints["scores"]["spacing"] = 100  # No existing facilities, so spacing is fine
        else:
            constraints["details"]["distance_to_existing"] = round(min_facility_distance, 1)
            
            # Warning: Too close to existing facility (< 200m)
            if min_facility_distance < 200:
                constraints["warnings"].append({
                    "type": "facility_proximity",
                    "severity": "warning",
                    "message": f"Close to existing facility ({min_facility_distance:.1f}m). May have overlap.",
                    "distance": round(min_facility_distance, 1)
                })
                constraints["scores"]["spacing"] = 50
            # Good: Well-spaced (200-500m)
            elif min_facility_distance < 500:
                constraints["scores"]["spacing"] = 100
            # OK: Far from existing (> 500m)
            else:
                constraints["scores"]["spacing"] = 90
    
    # Calculate overall suitability score (0-100)
    if constraints["scores"]:
        avg_score = sum(constraints["scores"].values()) / len(constraints["scores"])
        constraints["suitability_score"] = round(avg_score, 1)
    else:
        constraints["suitability_score"] = 0 if not constraints["is_valid"] else 50
    
    # Generate summary message
    if constraints["is_valid"]:
        if constraints["suitability_score"] >= 80:
            constraints["summary"] = "✓ Suitable location with good accessibility"
        elif constraints["suitability_score"] >= 60:
            constraints["summary"] = "⚠ Acceptable location with minor concerns"
        else:
            constraints["summary"] = "⚠ Marginal location - consider alternatives"
    else:
        constraints["summary"] = "✗ Invalid location - critical constraints violated"
    
    return constraints


def validate_multiple_locations(
    locations: List[List[float]],
    boundary: List[Dict],
    parcels: List[Dict],
    water_bodies: List[Dict],
    roads: List[Dict],
    existing_facilities: List[Dict],
    infrastructure_type: str = "water_facility"
) -> List[Dict[str, Any]]:
    """
    Validate multiple proposed locations.
    
    Returns list of validation results, sorted by suitability score.
    """
    results = []
    
    for i, location in enumerate(locations):
        validation = validate_location_constraints(
            location,
            boundary,
            parcels,
            water_bodies,
            roads,
            existing_facilities,
            infrastructure_type
        )
        validation["location"] = location
        validation["location_id"] = f"location_{i+1}"
        results.append(validation)
    
    # Sort by suitability score (descending)
    results.sort(key=lambda x: (x["is_valid"], x["suitability_score"]), reverse=True)
    
    return results


def get_buildable_area(
    boundary: List[Dict],
    parcels: List[Dict],
    water_bodies: List[Dict],
    buffer_distance: float = 30.0
) -> Dict[str, Any]:
    """
    Calculate approximate buildable area within village.
    
    Returns statistics about available land.
    """
    try:
        # Get total village area
        if not boundary:
            return {"error": "No boundary data"}
        
        village_geom = shape(boundary[0]["geometry"])
        total_area_m2 = village_geom.area * (111000 ** 2)  # Convert to m²
        
        # Calculate restricted area
        restricted_area_m2 = 0
        
        # Subtract restricted parcels
        for parcel in parcels:
            if parcel["properties"].get("restricted") or parcel["properties"].get("owner_type") == "private":
                parcel_geom = shape(parcel["geometry"])
                restricted_area_m2 += parcel_geom.area * (111000 ** 2)
        
        # Subtract water bodies with buffer
        for wb in water_bodies:
            wb_geom = shape(wb["geometry"])
            buffered = wb_geom.buffer(buffer_distance / 111000)  # Convert meters to degrees
            restricted_area_m2 += buffered.area * (111000 ** 2)
        
        # Calculate buildable area
        buildable_area_m2 = max(0, total_area_m2 - restricted_area_m2)
        buildable_percentage = (buildable_area_m2 / total_area_m2 * 100) if total_area_m2 > 0 else 0
        
        return {
            "total_area_m2": round(total_area_m2, 0),
            "restricted_area_m2": round(restricted_area_m2, 0),
            "buildable_area_m2": round(buildable_area_m2, 0),
            "buildable_percentage": round(buildable_percentage, 1),
            "num_restricted_parcels": sum(1 for p in parcels if p["properties"].get("restricted") or p["properties"].get("owner_type") == "private"),
            "num_water_bodies": len(water_bodies)
        }
        
    except Exception as e:
        return {"error": str(e)}
