"""
Coverage Analysis Service

Calculates household and population coverage for infrastructure facilities.
"""

from typing import List, Dict, Any, Tuple
from shapely.geometry import Point, shape
from shapely.ops import nearest_points
import math


def calculate_euclidean_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """
    Calculate Euclidean (straight-line) distance between two points in meters.
    Uses Haversine formula for lat/lon coordinates.
    
    Args:
        point1: (lon, lat) tuple
        point2: (lon, lat) tuple
    
    Returns:
        Distance in meters
    """
    lon1, lat1 = point1
    lon2, lat2 = point2
    
    # Earth radius in meters
    R = 6371000
    
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    # Haversine formula
    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance


def get_building_center(building_geom: Dict) -> Tuple[float, float]:
    """Get center point of building geometry"""
    geom = shape(building_geom)
    centroid = geom.centroid
    return (centroid.x, centroid.y)


def calculate_facility_coverage(
    buildings: List[Dict],
    facilities: List[Dict],
    threshold_meters: float = 500.0
) -> Dict[str, Any]:
    """
    Calculate household and population coverage for facilities.
    
    Args:
        buildings: List of building features (GeoJSON format)
        facilities: List of facility features (GeoJSON format)
        threshold_meters: Distance threshold for "served" status
    
    Returns:
        Coverage statistics including served/underserved counts
    """
    if not buildings:
        return {
            "total_buildings": 0,
            "total_households": 0,
            "total_population": 0,
            "served_households": 0,
            "served_population": 0,
            "underserved_households": 0,
            "underserved_population": 0,
            "coverage_percentage": 0.0,
            "average_distance": 0.0,
            "threshold_meters": threshold_meters,
            "distance_method": "euclidean"
        }
    
    if not facilities:
        total_hh = sum(b.get("properties", {}).get("estimated_households", 1) for b in buildings)
        total_pop = sum(b.get("properties", {}).get("estimated_population", 4) for b in buildings)
        return {
            "total_buildings": len(buildings),
            "total_households": total_hh,
            "total_population": total_pop,
            "served_households": 0,
            "served_population": 0,
            "underserved_households": total_hh,
            "underserved_population": total_pop,
            "coverage_percentage": 0.0,
            "average_distance": 850.0,
            "threshold_meters": threshold_meters,
            "distance_method": "euclidean"
        }
    
    # Extract facility locations
    facility_points = []
    for facility in facilities:
        coords = facility["geometry"]["coordinates"]
        facility_points.append(coords)
    
    # Calculate coverage for each building
    total_households = 0
    total_population = 0
    served_households = 0
    served_population = 0
    distances = []
    
    underserved_buildings = []
    
    for building in buildings:
        properties = building["properties"]
        households = properties.get("estimated_households", 0)
        population = properties.get("estimated_population", 0)
        
        total_households += households
        total_population += population
        
        # Get building center
        building_center = get_building_center(building["geometry"])
        
        # Find nearest facility and distance
        min_distance = float('inf')
        for facility_point in facility_points:
            distance = calculate_euclidean_distance(building_center, facility_point)
            if distance < min_distance:
                min_distance = distance
        
        distances.append(min_distance)
        
        # Check if served
        if min_distance <= threshold_meters:
            served_households += households
            served_population += population
        else:
            underserved_buildings.append({
                "building_id": properties.get("building_id"),
                "households": households,
                "population": population,
                "distance": round(min_distance, 1),
                "center": building_center
            })
    
    underserved_households = total_households - served_households
    underserved_population = total_population - served_population
    
    coverage_percentage = (served_households / total_households * 100) if total_households > 0 else 0
    average_distance = sum(distances) / len(distances) if distances else 0
    
    return {
        "total_buildings": len(buildings),
        "total_households": total_households,
        "total_population": total_population,
        "served_households": served_households,
        "served_population": served_population,
        "underserved_households": underserved_households,
        "underserved_population": underserved_population,
        "coverage_percentage": round(coverage_percentage, 2),
        "average_distance": round(average_distance, 1),
        "median_distance": round(sorted(distances)[len(distances)//2], 1) if distances else 0,
        "max_distance": round(max(distances), 1) if distances else 0,
        "threshold_meters": threshold_meters,
        "distance_method": "euclidean",
        "underserved_buildings": underserved_buildings[:50]  # Limit to 50 for response size
    }


def calculate_building_distances(
    buildings: List[Dict],
    facilities: List[Dict]
) -> Dict[str, List[float]]:
    """
    Calculate distance from each building to nearest facility.
    
    Returns:
        Dictionary mapping building_id to distance in meters
    """
    if not facilities:
        return {}
    
    # Extract facility locations
    facility_points = []
    for facility in facilities:
        coords = facility["geometry"]["coordinates"]
        facility_points.append(coords)
    
    building_distances = {}
    
    for building in buildings:
        building_id = building["properties"].get("building_id")
        building_center = get_building_center(building["geometry"])
        
        # Find nearest facility
        min_distance = float('inf')
        for facility_point in facility_points:
            distance = calculate_euclidean_distance(building_center, facility_point)
            if distance < min_distance:
                min_distance = distance
        
        building_distances[building_id] = round(min_distance, 1)
    
    return building_distances


def identify_underserved_areas(
    buildings: List[Dict],
    facilities: List[Dict],
    threshold_meters: float = 500.0,
    min_cluster_size: int = 3
) -> List[Dict[str, Any]]:
    """
    Identify clusters of underserved buildings.
    
    Args:
        buildings: List of building features
        facilities: List of facility features
        threshold_meters: Distance threshold for "served" status
        min_cluster_size: Minimum buildings to form a cluster
    
    Returns:
        List of underserved area clusters
    """
    if not buildings or not facilities:
        return []
    
    # Extract facility locations
    facility_points = []
    for facility in facilities:
        coords = facility["geometry"]["coordinates"]
        facility_points.append(coords)
    
    # Find underserved buildings
    underserved = []
    for building in buildings:
        building_center = get_building_center(building["geometry"])
        
        # Find nearest facility distance
        min_distance = float('inf')
        for facility_point in facility_points:
            distance = calculate_euclidean_distance(building_center, facility_point)
            if distance < min_distance:
                min_distance = distance
        
        if min_distance > threshold_meters:
            underserved.append({
                "building": building,
                "center": building_center,
                "distance": min_distance
            })
    
    if len(underserved) < min_cluster_size:
        return []
    
    # Simple clustering: group nearby underserved buildings
    # For Phase 3, use a basic distance-based approach
    clusters = []
    cluster_threshold = 200  # meters - buildings within 200m are in same cluster
    
    processed = set()
    
    for i, item in enumerate(underserved):
        if i in processed:
            continue
        
        # Start new cluster
        cluster = [item]
        processed.add(i)
        
        # Find nearby underserved buildings
        for j, other in enumerate(underserved):
            if j in processed:
                continue
            
            distance = calculate_euclidean_distance(item["center"], other["center"])
            if distance <= cluster_threshold:
                cluster.append(other)
                processed.add(j)
        
        if len(cluster) >= min_cluster_size:
            # Calculate cluster stats
            cluster_households = sum(
                b["building"]["properties"].get("estimated_households", 0)
                for b in cluster
            )
            cluster_population = sum(
                b["building"]["properties"].get("estimated_population", 0)
                for b in cluster
            )
            
            # Calculate cluster center
            lons = [b["center"][0] for b in cluster]
            lats = [b["center"][1] for b in cluster]
            cluster_center = [
                sum(lons) / len(lons),
                sum(lats) / len(lats)
            ]
            
            clusters.append({
                "cluster_id": f"cluster_{len(clusters) + 1}",
                "building_count": len(cluster),
                "households": cluster_households,
                "population": cluster_population,
                "center": cluster_center,
                "avg_distance_to_facility": round(
                    sum(b["distance"] for b in cluster) / len(cluster), 1
                ),
                "priority_score": cluster_households * 2 + cluster_population  # Simple priority
            })
    
    # Sort by priority (descending)
    clusters.sort(key=lambda x: x["priority_score"], reverse=True)
    
    return clusters
