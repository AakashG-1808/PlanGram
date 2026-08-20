"""
Candidate Location Generation Service

Generates and ranks candidate locations for infrastructure placement using:
- Grid-based sampling of buildable areas
- Coverage gap targeting
- Constraint-aware filtering
- Multi-objective scoring (coverage improvement + suitability)
"""

from typing import List, Dict, Any, Tuple
from shapely.geometry import Point, shape, box
from shapely.ops import unary_union
import random
import math


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two points using Haversine formula.
    
    Returns distance in meters.
    """
    R = 6371000  # Earth radius in meters
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


def generate_grid_candidates(
    boundary: List[Dict],
    grid_spacing_meters: float = 100.0,
    random_offset: bool = False
) -> List[List[float]]:
    """
    Generate candidate locations on a regular grid within village boundary.
    
    Args:
        boundary: Village boundary features
        grid_spacing_meters: Spacing between grid points in meters
        random_offset: Add small random offset to avoid perfect grid
    
    Returns:
        List of [lon, lat] candidate locations
    """
    if not boundary:
        return []
    
    # Get boundary geometry
    boundary_geom = shape(boundary[0]["geometry"])
    bounds = boundary_geom.bounds  # (minx, miny, maxx, maxy)
    
    # Convert grid spacing from meters to degrees (approximate)
    grid_spacing_deg = grid_spacing_meters / 111000
    
    candidates = []
    
    # Generate grid points
    lon = bounds[0]
    while lon <= bounds[2]:
        lat = bounds[1]
        while lat <= bounds[3]:
            # Add random offset if requested
            if random_offset:
                offset_lon = (random.random() - 0.5) * grid_spacing_deg * 0.3
                offset_lat = (random.random() - 0.5) * grid_spacing_deg * 0.3
                test_point = Point(lon + offset_lon, lat + offset_lat)
            else:
                test_point = Point(lon, lat)
            
            # Check if point is inside boundary
            if boundary_geom.contains(test_point):
                candidates.append([test_point.x, test_point.y])
            
            lat += grid_spacing_deg
        lon += grid_spacing_deg
    
    return candidates


def generate_coverage_gap_candidates(
    buildings: List[Dict],
    existing_facilities: List[Dict],
    threshold_meters: float = 500.0,
    num_candidates: int = 20
) -> List[List[float]]:
    """
    Generate candidate locations targeting coverage gaps (underserved buildings).
    
    Args:
        buildings: Building features with locations
        existing_facilities: Existing facility features
        threshold_meters: Coverage distance threshold
        num_candidates: Maximum number of candidates to generate
    
    Returns:
        List of [lon, lat] candidate locations near underserved clusters
    """
    if not buildings:
        return []
    
    # Identify underserved buildings
    underserved = []
    
    for building in buildings:
        building_geom = shape(building["geometry"])
        building_center = building_geom.centroid
        
        # Check if building is served by any existing facility
        is_served = False
        for facility in existing_facilities:
            facility_geom = shape(facility["geometry"])
            facility_center = facility_geom.centroid
            
            distance = haversine_distance(
                building_center.y, building_center.x,
                facility_center.y, facility_center.x
            )
            
            if distance <= threshold_meters:
                is_served = True
                break
        
        if not is_served:
            underserved.append({
                "location": [building_center.x, building_center.y],
                "households": building["properties"].get("households", 1)
            })
    
    if not underserved:
        return []
    
    # Cluster underserved buildings using simple spatial clustering
    clusters = _cluster_locations(
        [b["location"] for b in underserved],
        max_clusters=min(num_candidates, len(underserved)),
        cluster_distance_meters=threshold_meters * 0.5
    )
    
    # Return cluster centroids as candidates
    return clusters[:num_candidates]


def _cluster_locations(
    locations: List[List[float]],
    max_clusters: int,
    cluster_distance_meters: float
) -> List[List[float]]:
    """
    Simple spatial clustering using greedy approach.
    
    Returns cluster centroids.
    """
    if not locations:
        return []
    
    if len(locations) <= max_clusters:
        return locations
    
    # Start with first location as first cluster
    clusters = [[locations[0]]]
    
    for location in locations[1:]:
        # Find nearest cluster
        min_distance = float('inf')
        nearest_cluster_idx = 0
        
        for i, cluster in enumerate(clusters):
            # Calculate distance to cluster centroid
            centroid = _calculate_centroid(cluster)
            distance = haversine_distance(
                location[1], location[0],
                centroid[1], centroid[0]
            )
            
            if distance < min_distance:
                min_distance = distance
                nearest_cluster_idx = i
        
        # Add to nearest cluster if within threshold, else create new cluster
        if min_distance <= cluster_distance_meters or len(clusters) >= max_clusters:
            clusters[nearest_cluster_idx].append(location)
        else:
            clusters.append([location])
    
    # Return cluster centroids
    return [_calculate_centroid(cluster) for cluster in clusters]


def _calculate_centroid(locations: List[List[float]]) -> List[float]:
    """Calculate centroid of a list of [lon, lat] locations."""
    if not locations:
        return [0, 0]
    
    avg_lon = sum(loc[0] for loc in locations) / len(locations)
    avg_lat = sum(loc[1] for loc in locations) / len(locations)
    
    return [avg_lon, avg_lat]


def generate_hybrid_candidates(
    boundary: List[Dict],
    buildings: List[Dict],
    existing_facilities: List[Dict],
    threshold_meters: float = 500.0,
    num_grid: int = 30,
    num_gap: int = 20,
    grid_spacing_meters: float = 150.0
) -> List[List[float]]:
    """
    Generate candidates using hybrid approach:
    - Grid-based sampling for broad coverage
    - Gap-based targeting for underserved areas
    
    Args:
        boundary: Village boundary features
        buildings: Building features
        existing_facilities: Existing facility features
        threshold_meters: Coverage distance threshold
        num_grid: Number of grid candidates to keep
        num_gap: Number of gap candidates to generate
        grid_spacing_meters: Grid spacing in meters
    
    Returns:
        Combined list of candidate locations
    """
    # Generate grid candidates
    grid_candidates = generate_grid_candidates(
        boundary,
        grid_spacing_meters=grid_spacing_meters,
        random_offset=True
    )
    
    # Sample grid candidates if too many
    if len(grid_candidates) > num_grid:
        random.shuffle(grid_candidates)
        grid_candidates = grid_candidates[:num_grid]
    
    # Generate gap-targeted candidates
    gap_candidates = generate_coverage_gap_candidates(
        buildings,
        existing_facilities,
        threshold_meters=threshold_meters,
        num_candidates=num_gap
    )
    
    # Combine and deduplicate
    all_candidates = grid_candidates + gap_candidates
    
    # Remove duplicates (locations within 50m of each other)
    unique_candidates = _deduplicate_locations(all_candidates, min_distance_meters=50)
    
    return unique_candidates


def _deduplicate_locations(
    locations: List[List[float]],
    min_distance_meters: float = 50
) -> List[List[float]]:
    """Remove duplicate locations that are too close to each other."""
    if not locations:
        return []
    
    unique = [locations[0]]
    
    for location in locations[1:]:
        is_duplicate = False
        for existing in unique:
            distance = haversine_distance(
                location[1], location[0],
                existing[1], existing[0]
            )
            if distance < min_distance_meters:
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique.append(location)
    
    return unique


def score_candidate_coverage(
    candidate_location: List[float],
    buildings: List[Dict],
    existing_facilities: List[Dict],
    threshold_meters: float = 500.0
) -> Dict[str, Any]:
    """
    Score a candidate location based on coverage improvement.
    
    Returns:
        Dictionary with coverage metrics
    """
    # Calculate current coverage (without candidate)
    served_before = set()
    for building in buildings:
        building_geom = shape(building["geometry"])
        building_center = building_geom.centroid
        building_id = building["properties"].get("building_id")
        
        for facility in existing_facilities:
            facility_geom = shape(facility["geometry"])
            facility_center = facility_geom.centroid
            
            distance = haversine_distance(
                building_center.y, building_center.x,
                facility_center.y, facility_center.x
            )
            
            if distance <= threshold_meters:
                served_before.add(building_id)
                break
    
    # Calculate coverage with candidate
    served_after = set(served_before)
    candidate_point = Point(candidate_location[0], candidate_location[1])
    
    newly_served_buildings = []
    for building in buildings:
        building_geom = shape(building["geometry"])
        building_center = building_geom.centroid
        building_id = building["properties"].get("building_id")
        
        if building_id not in served_before:
            distance = haversine_distance(
                building_center.y, building_center.x,
                candidate_point.y, candidate_point.x
            )
            
            if distance <= threshold_meters:
                served_after.add(building_id)
                newly_served_buildings.append({
                    "building_id": building_id,
                    "distance": round(distance, 1),
                    "households": building["properties"].get("households", 1)
                })
    
    # Calculate improvement metrics
    buildings_gained = len(served_after) - len(served_before)
    households_gained = sum(b["households"] for b in newly_served_buildings)
    coverage_before = len(served_before) / len(buildings) * 100 if buildings else 0
    coverage_after = len(served_after) / len(buildings) * 100 if buildings else 0
    coverage_improvement = coverage_after - coverage_before
    
    return {
        "coverage_improvement": round(coverage_improvement, 2),
        "buildings_gained": buildings_gained,
        "households_gained": households_gained,
        "coverage_before": round(coverage_before, 1),
        "coverage_after": round(coverage_after, 1),
        "newly_served_count": len(newly_served_buildings)
    }


def rank_candidates(
    candidates: List[List[float]],
    validation_results: List[Dict],
    coverage_scores: List[Dict],
    weights: Dict[str, float] = None
) -> List[Dict[str, Any]]:
    """
    Rank candidates using multi-objective scoring.
    
    Args:
        candidates: List of candidate locations
        validation_results: Constraint validation results for each candidate
        coverage_scores: Coverage improvement scores for each candidate
        weights: Scoring weights (default: coverage=0.6, suitability=0.4)
    
    Returns:
        Ranked list of candidates with combined scores
    """
    if weights is None:
        weights = {
            "coverage": 0.6,
            "suitability": 0.4
        }
    
    ranked = []
    
    for i, location in enumerate(candidates):
        validation = validation_results[i] if i < len(validation_results) else {}
        coverage = coverage_scores[i] if i < len(coverage_scores) else {}
        
        # Normalize coverage improvement to 0-100 scale
        # Assume 20% coverage improvement = score 100
        coverage_score = min(coverage.get("coverage_improvement", 0) / 20 * 100, 100)
        
        # Get suitability score from validation
        suitability_score = validation.get("suitability_score", 0) if validation.get("is_valid", False) else 0
        
        # Calculate combined score
        combined_score = (
            weights["coverage"] * coverage_score +
            weights["suitability"] * suitability_score
        )
        
        ranked.append({
            "location": location,
            "combined_score": round(combined_score, 2),
            "coverage_score": round(coverage_score, 2),
            "suitability_score": round(suitability_score, 2),
            "coverage_improvement": coverage.get("coverage_improvement", 0),
            "buildings_gained": coverage.get("buildings_gained", 0),
            "households_gained": coverage.get("households_gained", 0),
            "is_valid": validation.get("is_valid", False),
            "violations": validation.get("violations", []),
            "warnings": validation.get("warnings", [])
        })
    
    # Sort by combined score (descending)
    ranked.sort(key=lambda x: (x["is_valid"], x["combined_score"]), reverse=True)
    
    return ranked
