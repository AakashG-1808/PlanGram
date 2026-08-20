"""
Generate Deterministic Synthetic Village Data for PlanGram Prototype

This script creates realistic representative GIS data for two villages:
- Village 01 (Chikkahullur): Clustered settlements
- Village 02 (Bandapalya): Dispersed settlements

All data is SYNTHETIC and for prototype demonstration only.
"""

import json
import csv
import random
import math
from pathlib import Path
from typing import List, Tuple, Dict
import numpy as np

# Fixed random seed for reproducibility
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


def create_polygon_coords(center: Tuple[float, float], radius: float, num_points: int = 6) -> List[List[float]]:
    """Create a polygon around a center point"""
    coords = []
    for i in range(num_points):
        angle = (2 * math.pi * i) / num_points + random.uniform(-0.2, 0.2)
        r = radius * random.uniform(0.8, 1.2)
        x = center[0] + r * math.cos(angle)
        y = center[1] + r * math.sin(angle)
        coords.append([x, y])
    coords.append(coords[0])  # Close the polygon
    return coords


def create_rectangle_coords(center: Tuple[float, float], width: float, height: float, rotation: float = 0) -> List[List[float]]:
    """Create a rectangle (for buildings)"""
    hw, hh = width / 2, height / 2
    corners = [
        [-hw, -hh], [hw, -hh], [hw, hh], [-hw, hh], [-hw, -hh]
    ]
    
    # Rotate
    cos_r, sin_r = math.cos(rotation), math.sin(rotation)
    rotated = []
    for x, y in corners:
        rx = x * cos_r - y * sin_r
        ry = x * sin_r + y * cos_r
        rotated.append([center[0] + rx, center[1] + ry])
    
    return rotated


def generate_village_boundary(center: Tuple[float, float], radius_km: float) -> Dict:
    """Generate village boundary"""
    # Convert km to approximate degrees (rough approximation for Karnataka)
    radius_deg = radius_km / 111.0
    coords = create_polygon_coords(center, radius_deg, num_points=12)
    
    return {
        "type": "Feature",
        "properties": {
            "name": "Village Boundary"
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [coords]
        }
    }


def point_in_polygon(point: Tuple[float, float], polygon: List[List[float]]) -> bool:
    """Check if point is inside polygon (ray casting algorithm)"""
    x, y = point
    n = len(polygon) - 1
    inside = False
    
    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    
    return inside


def generate_road_network(center: Tuple[float, float], boundary_coords: List[List[float]], num_roads: int, pattern: str) -> List[Dict]:
    """Generate road network"""
    roads = []
    radius_deg = 0.02
    
    if pattern == "clustered":
        # Radial + ring pattern
        # Main roads from center
        for i in range(4):
            angle = (2 * math.pi * i) / 4 + random.uniform(-0.3, 0.3)
            end_x = center[0] + radius_deg * math.cos(angle)
            end_y = center[1] + radius_deg * math.sin(angle)
            
            roads.append({
                "type": "Feature",
                "properties": {
                    "road_id": f"road_{len(roads)+1:03d}",
                    "road_type": "main",
                    "surface": "paved",
                    "length_m": int(radius_deg * 111000)
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [center[0], center[1]],
                        [end_x, end_y]
                    ]
                }
            })
        
        # Local connecting roads
        for _ in range(num_roads - 4):
            angle1 = random.uniform(0, 2 * math.pi)
            angle2 = angle1 + random.uniform(0.5, 1.5)
            r = radius_deg * random.uniform(0.3, 0.8)
            
            x1 = center[0] + r * math.cos(angle1)
            y1 = center[1] + r * math.sin(angle1)
            x2 = center[0] + r * math.cos(angle2)
            y2 = center[1] + r * math.sin(angle2)
            
            length = math.sqrt((x2-x1)**2 + (y2-y1)**2) * 111000
            
            roads.append({
                "type": "Feature",
                "properties": {
                    "road_id": f"road_{len(roads)+1:03d}",
                    "road_type": "local",
                    "surface": random.choice(["paved", "unpaved", "unpaved"]),
                    "length_m": int(length)
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[x1, y1], [x2, y2]]
                }
            })
    
    else:  # dispersed
        # More irregular network
        nodes = []
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            r = radius_deg * random.uniform(0.2, 0.9)
            x = center[0] + r * math.cos(angle)
            y = center[1] + r * math.sin(angle)
            if point_in_polygon((x, y), boundary_coords):
                nodes.append((x, y))
        
        # Connect some nodes
        for i in range(min(num_roads, len(nodes) - 1)):
            if i < len(nodes) - 1:
                x1, y1 = nodes[i]
                x2, y2 = nodes[i + 1]
                length = math.sqrt((x2-x1)**2 + (y2-y1)**2) * 111000
                
                roads.append({
                    "type": "Feature",
                    "properties": {
                        "road_id": f"road_{len(roads)+1:03d}",
                        "road_type": random.choice(["main", "local", "local", "path"]),
                        "surface": random.choice(["paved", "unpaved", "unpaved", "unpaved"]),
                        "length_m": int(length)
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [[x1, y1], [x2, y2]]
                    }
                })
    
    return roads


def generate_buildings(center: Tuple[float, float], boundary_coords: List[List[float]], 
                       num_buildings: int, pattern: str, roads: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """Generate buildings and households"""
    buildings = []
    households = []
    
    # Extract road points for proximity
    road_points = []
    for road in roads:
        coords = road["geometry"]["coordinates"]
        road_points.extend(coords)
    
    if pattern == "clustered":
        # Generate clusters
        num_clusters = 3
        clusters = []
        for _ in range(num_clusters):
            angle = random.uniform(0, 2 * math.pi)
            r = random.uniform(0.003, 0.015)
            cluster_center = (
                center[0] + r * math.cos(angle),
                center[1] + r * math.sin(angle)
            )
            clusters.append(cluster_center)
        
        buildings_per_cluster = num_buildings // num_clusters
        
        for cluster_idx, cluster_center in enumerate(clusters):
            for i in range(buildings_per_cluster):
                # Place near cluster center
                angle = random.uniform(0, 2 * math.pi)
                r = random.uniform(0.0005, 0.003)
                bldg_center = (
                    cluster_center[0] + r * math.cos(angle),
                    cluster_center[1] + r * math.sin(angle)
                )
                
                if not point_in_polygon(bldg_center, boundary_coords):
                    continue
                
                # Building footprint
                width = random.uniform(0.00008, 0.00015)  # ~9-17m
                height = random.uniform(0.00006, 0.00012)  # ~7-13m
                rotation = random.uniform(0, 2 * math.pi)
                coords = create_rectangle_coords(bldg_center, width, height, rotation)
                
                building_type = random.choice(["residential"] * 85 + ["commercial"] * 10 + ["public"] * 5)
                households_count = 1 if building_type == "residential" else 0
                population = random.randint(3, 5) if households_count > 0 else 0
                
                building_id = f"bldg_{len(buildings)+1:04d}"
                
                buildings.append({
                    "type": "Feature",
                    "properties": {
                        "building_id": building_id,
                        "building_type": building_type,
                        "estimated_households": households_count,
                        "estimated_population": population,
                        "area_sq_m": round(width * height * 111000 * 111000, 1)
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [coords]
                    }
                })
                
                if households_count > 0:
                    households.append({
                        "household_id": f"hh_{len(households)+1:04d}",
                        "building_id": building_id,
                        "estimated_population": population,
                        "estimated": True
                    })
    
    else:  # dispersed
        for i in range(num_buildings):
            # More spread out
            angle = random.uniform(0, 2 * math.pi)
            r = random.uniform(0.002, 0.018)
            bldg_center = (
                center[0] + r * math.cos(angle),
                center[1] + r * math.sin(angle)
            )
            
            if not point_in_polygon(bldg_center, boundary_coords):
                continue
            
            width = random.uniform(0.00007, 0.00013)
            height = random.uniform(0.00006, 0.00011)
            rotation = random.uniform(0, 2 * math.pi)
            coords = create_rectangle_coords(bldg_center, width, height, rotation)
            
            building_type = random.choice(["residential"] * 90 + ["commercial"] * 5 + ["agricultural"] * 5)
            households_count = 1 if building_type == "residential" else 0
            population = random.randint(3, 5) if households_count > 0 else 0
            
            building_id = f"bldg_{len(buildings)+1:04d}"
            
            buildings.append({
                "type": "Feature",
                "properties": {
                    "building_id": building_id,
                    "building_type": building_type,
                    "estimated_households": households_count,
                    "estimated_population": population,
                    "area_sq_m": round(width * height * 111000 * 111000, 1)
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coords]
                }
            })
            
            if households_count > 0:
                households.append({
                    "household_id": f"hh_{len(households)+1:04d}",
                    "building_id": building_id,
                    "estimated_population": population,
                    "estimated": True
                })
    
    return buildings, households


def generate_parcels(buildings: List[Dict], boundary_coords: List[List[float]]) -> List[Dict]:
    """Generate parcels around buildings"""
    parcels = []
    
    for i, building in enumerate(buildings):
        # Create parcel slightly larger than building
        bldg_coords = building["geometry"]["coordinates"][0]
        center_x = sum(c[0] for c in bldg_coords) / len(bldg_coords)
        center_y = sum(c[1] for c in bldg_coords) / len(bldg_coords)
        
        # Parcel radius slightly larger
        radius = random.uniform(0.0001, 0.00015)
        parcel_coords = create_polygon_coords((center_x, center_y), radius, num_points=5)
        
        parcel_type = building["properties"]["building_type"]
        if parcel_type == "commercial":
            parcel_type = "commercial"
        elif parcel_type == "public":
            parcel_type = "public"
        else:
            parcel_type = random.choice(["residential"] * 70 + ["agricultural"] * 30)
        
        # Calculate area
        area = abs(sum(parcel_coords[i][0] * parcel_coords[i+1][1] - 
                      parcel_coords[i+1][0] * parcel_coords[i][1] 
                      for i in range(len(parcel_coords)-1))) * 0.5
        area_sq_m = area * 111000 * 111000
        
        parcels.append({
            "type": "Feature",
            "properties": {
                "parcel_id": f"parc_{i+1:04d}",
                "parcel_type": parcel_type,
                "owner_type": random.choice(["private"] * 80 + ["government"] * 15 + ["common"] * 5),
                "area_sq_m": round(area_sq_m, 1),
                "restricted": random.random() < 0.05
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [parcel_coords]
            }
        })
    
    return parcels


def generate_water_bodies(center: Tuple[float, float], boundary_coords: List[List[float]], num_bodies: int) -> List[Dict]:
    """Generate water bodies"""
    water_bodies = []
    
    for i in range(num_bodies):
        angle = random.uniform(0, 2 * math.pi)
        r = random.uniform(0.005, 0.015)
        wb_center = (
            center[0] + r * math.cos(angle),
            center[1] + r * math.sin(angle)
        )
        
        if not point_in_polygon(wb_center, boundary_coords):
            continue
        
        radius = random.uniform(0.0008, 0.002)
        coords = create_polygon_coords(wb_center, radius, num_points=8)
        
        area = abs(sum(coords[i][0] * coords[i+1][1] - coords[i+1][0] * coords[i][1] 
                      for i in range(len(coords)-1))) * 0.5
        area_sq_m = area * 111000 * 111000
        
        water_bodies.append({
            "type": "Feature",
            "properties": {
                "waterbody_id": f"wb_{i+1:03d}",
                "waterbody_type": random.choice(["tank", "pond", "pond"]),
                "seasonal": random.choice([True, False]),
                "area_sq_m": round(area_sq_m, 1)
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [coords]
            }
        })
    
    return water_bodies


def generate_facilities(center: Tuple[float, float], boundary_coords: List[List[float]], 
                       pattern: str, num_water: int) -> List[Dict]:
    """Generate existing facilities"""
    facilities = []
    
    # Water facilities
    for i in range(num_water):
        if pattern == "clustered":
            angle = random.uniform(0, 2 * math.pi)
            r = random.uniform(0.003, 0.008)
        else:
            angle = random.uniform(0, 2 * math.pi)
            r = random.uniform(0.005, 0.012)
        
        fac_x = center[0] + r * math.cos(angle)
        fac_y = center[1] + r * math.sin(angle)
        
        if not point_in_polygon((fac_x, fac_y), boundary_coords):
            continue
        
        facilities.append({
            "type": "Feature",
            "properties": {
                "facility_id": f"fac_water_{i+1:03d}",
                "facility_type": "water",
                "name": f"Water Point {i+1}",
                "status": "existing",
                "capacity": random.randint(100, 180),
                "year_established": random.randint(2010, 2022)
            },
            "geometry": {
                "type": "Point",
                "coordinates": [fac_x, fac_y]
            }
        })
    
    # School
    school_angle = random.uniform(0, 2 * math.pi)
    school_r = random.uniform(0.002, 0.006)
    facilities.append({
        "type": "Feature",
        "properties": {
            "facility_id": "fac_school_001",
            "facility_type": "education",
            "name": "Primary School",
            "status": "existing",
            "capacity": 200,
            "year_established": 2005
        },
        "geometry": {
            "type": "Point",
            "coordinates": [center[0] + school_r * math.cos(school_angle), 
                          center[1] + school_r * math.sin(school_angle)]
        }
    })
    
    return facilities


def save_geojson(features: List[Dict], filepath: Path):
    """Save features as GeoJSON"""
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(geojson, f, indent=2)
    print(f"✓ Created {filepath}")


def save_households_csv(households: List[Dict], filepath: Path):
    """Save households as CSV"""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["household_id", "building_id", "estimated_population", "estimated"])
        writer.writeheader()
        writer.writerows(households)
    print(f"✓ Created {filepath}")


def generate_village(village_id: str, village_name: str, center: Tuple[float, float], 
                     config: Dict):
    """Generate all data for a village"""
    print(f"\n{'='*60}")
    print(f"Generating {village_name} ({village_id})")
    print(f"{'='*60}")
    
    base_path = Path(f"data/villages/{village_id}")
    
    # 1. Boundary
    boundary = generate_village_boundary(center, config["radius_km"])
    boundary_coords = boundary["geometry"]["coordinates"][0]
    save_geojson([boundary], base_path / "boundary.geojson")
    
    # 2. Roads
    roads = generate_road_network(center, boundary_coords, config["num_roads"], config["pattern"])
    save_geojson(roads, base_path / "roads.geojson")
    
    # 3. Buildings & Households
    buildings, households = generate_buildings(center, boundary_coords, config["num_buildings"], 
                                              config["pattern"], roads)
    save_geojson(buildings, base_path / "buildings.geojson")
    save_households_csv(households, base_path / "households.csv")
    
    # 4. Parcels
    parcels = generate_parcels(buildings, boundary_coords)
    save_geojson(parcels, base_path / "parcels.geojson")
    
    # 5. Water bodies
    water_bodies = generate_water_bodies(center, boundary_coords, config["num_water_bodies"])
    save_geojson(water_bodies, base_path / "water_bodies.geojson")
    
    # 6. Facilities
    facilities = generate_facilities(center, boundary_coords, config["pattern"], config["num_water_facilities"])
    save_geojson(facilities, base_path / "facilities.geojson")
    
    # Summary
    total_population = sum(h["estimated_population"] for h in households)
    print(f"\n📊 Summary:")
    print(f"   Buildings: {len(buildings)}")
    print(f"   Households: {len(households)}")
    print(f"   Population: {total_population}")
    print(f"   Parcels: {len(parcels)}")
    print(f"   Roads: {len(roads)}")
    print(f"   Water Bodies: {len(water_bodies)}")
    print(f"   Facilities: {len(facilities)}")


def main():
    """Main generation function"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║   PlanGram Synthetic Village Data Generator                 ║
║   Deterministic Representative Data for Prototype           ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Village 01: Chikkahullur (Clustered)
    # Approximate location in Anekal Taluk
    village_01_config = {
        "radius_km": 1.2,
        "num_buildings": 720,
        "num_roads": 68,
        "num_water_bodies": 3,
        "num_water_facilities": 4,
        "pattern": "clustered"
    }
    generate_village("village_01", "Chikkahullur", (77.695, 12.695), village_01_config)
    
    # Village 02: Bandapalya (Dispersed)
    village_02_config = {
        "radius_km": 1.1,
        "num_buildings": 580,
        "num_roads": 52,
        "num_water_bodies": 2,
        "num_water_facilities": 3,
        "pattern": "dispersed"
    }
    generate_village("village_02", "Bandapalya", (77.715, 12.682), village_02_config)
    
    print(f"\n{'='*60}")
    print("✅ Village data generation complete!")
    print("="*60)
    print("\nIMPORTANT:")
    print("- All data is SYNTHETIC for prototype demonstration")
    print("- This is NOT official SVAMITVA or government data")
    print("- Data is deterministic (same output each run)")
    print("- Use data/source_metadata.json to track data sources")


if __name__ == "__main__":
    main()
