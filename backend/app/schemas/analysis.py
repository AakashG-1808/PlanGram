"""
Pydantic schemas for analysis endpoints
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class CoverageMetrics(BaseModel):
    """Coverage analysis metrics"""
    total_buildings: int
    total_households: int
    total_population: int
    served_households: int
    served_population: int
    underserved_households: int
    underserved_population: int
    coverage_percentage: float
    average_distance: float
    median_distance: float
    max_distance: float
    threshold_meters: float
    distance_method: str
    underserved_buildings: List[Dict[str, Any]] = []


class UnderservedCluster(BaseModel):
    """Underserved area cluster"""
    cluster_id: str
    building_count: int
    households: int
    population: int
    center: List[float]
    avg_distance_to_facility: float
    priority_score: float


class VillageMetrics(BaseModel):
    """Complete village metrics"""
    village_id: str
    village_name: str
    
    # Basic stats
    total_households: int
    total_population: int
    total_buildings: int
    area_sq_km: float
    
    # Infrastructure
    water_facilities: int
    other_facilities: int
    
    # Coverage metrics
    water_coverage: Optional[CoverageMetrics] = None
    
    # Underserved areas
    underserved_clusters: List[UnderservedCluster] = []
    
    # Priority assessment
    priority_level: str = "medium"  # low, medium, high
    priority_factors: List[str] = []


class InfrastructureAnalysis(BaseModel):
    """Analysis for specific infrastructure type"""
    infrastructure_type: str
    facility_count: int
    coverage: CoverageMetrics
    underserved_clusters: List[UnderservedCluster]
    recommendations: List[str] = []
