"""
Budget Optimization Service

Solves multi-facility placement optimization problem:
- Maximize coverage within budget constraint
- Integer linear programming (ILP) formulation
- Considers facility costs and coverage overlap
- Generates multiple feasible plans

Uses greedy algorithm (OR-Tools alternative for prototype phase)
"""

from typing import List, Dict, Any, Tuple, Set
import math


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points using Haversine formula."""
    R = 6371000  # Earth radius in meters
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


def calculate_building_coverage(
    buildings: List[Dict],
    facilities: List[Dict],
    threshold_meters: float
) -> Tuple[Set[str], Dict[str, List[str]]]:
    """
    Calculate which buildings are covered by which facilities.
    
    Returns:
        - Set of covered building IDs
        - Dict mapping building_id to list of covering facility_ids
    """
    covered = set()
    coverage_map = {}
    
    for building in buildings:
        building_id = building["properties"].get("building_id")
        from shapely.geometry import shape
        building_geom = shape(building["geometry"])
        building_center = building_geom.centroid
        
        covering_facilities = []
        
        for facility in facilities:
            facility_id = facility.get("facility_id", facility["properties"].get("facility_id"))
            facility_geom = shape(facility["geometry"])
            facility_center = facility_geom.centroid
            
            distance = haversine_distance(
                building_center.y, building_center.x,
                facility_center.y, facility_center.x
            )
            
            if distance <= threshold_meters:
                covering_facilities.append(facility_id)
        
        if covering_facilities:
            covered.add(building_id)
            coverage_map[building_id] = covering_facilities
    
    return covered, coverage_map


def greedy_optimization(
    candidates: List[Dict],
    buildings: List[Dict],
    existing_facilities: List[Dict],
    budget: float,
    facility_cost: float,
    threshold_meters: float,
    max_facilities: int = None
) -> Dict[str, Any]:
    """
    Greedy algorithm for budget-constrained facility placement.
    
    At each iteration, select the candidate that provides maximum marginal coverage improvement.
    
    Args:
        candidates: Ranked candidate locations
        buildings: Building features
        existing_facilities: Existing facility features
        budget: Total budget available
        facility_cost: Cost per facility
        threshold_meters: Coverage threshold
        max_facilities: Optional limit on number of facilities
    
    Returns:
        Optimization solution with selected facilities
    """
    from shapely.geometry import Point
    
    # Calculate how many facilities we can afford
    max_affordable = int(budget / facility_cost)
    if max_facilities:
        max_affordable = min(max_affordable, max_facilities)
    
    if max_affordable == 0:
        return {
            "status": "insufficient_budget",
            "message": f"Budget ₹{budget:,.0f} insufficient for even one facility (cost: ₹{facility_cost:,.0f})",
            "selected_facilities": [],
            "total_cost": 0,
            "coverage_improvement": 0
        }
    
    # Initialize with existing facilities
    selected_facilities = []
    current_facilities = list(existing_facilities)
    
    # Track covered buildings
    covered_buildings, _ = calculate_building_coverage(buildings, current_facilities, threshold_meters)
    initial_coverage = len(covered_buildings)
    
    # Greedy selection
    for iteration in range(max_affordable):
        best_candidate = None
        best_marginal_gain = 0
        best_new_covered = set()
        
        # Try each remaining candidate
        for candidate in candidates:
            # Skip if already selected
            if any(c["location"] == candidate["location"] for c in selected_facilities):
                continue
            
            # Skip if invalid
            if not candidate.get("is_valid", True):
                continue
            
            # Create temporary facility at candidate location
            temp_facility = {
                "facility_id": f"candidate_{iteration}",
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": candidate["location"]
                },
                "properties": {
                    "facility_id": f"candidate_{iteration}"
                }
            }
            
            # Calculate coverage with this candidate added
            test_facilities = current_facilities + [temp_facility]
            new_covered, _ = calculate_building_coverage(buildings, test_facilities, threshold_meters)
            
            # Calculate marginal gain
            marginal_gain = len(new_covered) - len(covered_buildings)
            
            if marginal_gain > best_marginal_gain:
                best_marginal_gain = marginal_gain
                best_candidate = candidate
                best_new_covered = new_covered
        
        # If no improvement possible, stop
        if best_marginal_gain == 0 or best_candidate is None:
            break
        
        # Add best candidate to selection
        selected_facilities.append({
            "facility_id": f"facility_{iteration + 1}",
            "location": best_candidate["location"],
            "buildings_gained": best_marginal_gain,
            "cost": facility_cost,
            "suitability_score": best_candidate.get("suitability_score", 0),
            "coverage_score": best_candidate.get("coverage_score", 0)
        })
        
        # Update current state
        current_facilities.append({
            "facility_id": f"facility_{iteration + 1}",
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": best_candidate["location"]
            },
            "properties": {
                "facility_id": f"facility_{iteration + 1}"
            }
        })
        covered_buildings = best_new_covered
    
    # Calculate final metrics
    final_coverage = len(covered_buildings)
    total_cost = len(selected_facilities) * facility_cost
    coverage_improvement = ((final_coverage - initial_coverage) / len(buildings) * 100) if buildings else 0
    
    return {
        "status": "optimal" if len(selected_facilities) == max_affordable else "converged",
        "message": f"Selected {len(selected_facilities)} facilities within budget",
        "selected_facilities": selected_facilities,
        "num_facilities": len(selected_facilities),
        "total_cost": total_cost,
        "remaining_budget": budget - total_cost,
        "coverage_before": initial_coverage,
        "coverage_after": final_coverage,
        "buildings_gained": final_coverage - initial_coverage,
        "coverage_improvement_pct": round(coverage_improvement, 2),
        "cost_per_building": round(total_cost / (final_coverage - initial_coverage), 2) if (final_coverage > initial_coverage) else 0,
        "budget_utilization_pct": round(total_cost / budget * 100, 2)
    }


def generate_budget_scenarios(
    candidates: List[Dict],
    buildings: List[Dict],
    existing_facilities: List[Dict],
    base_budget: float,
    facility_cost: float,
    threshold_meters: float,
    scenario_count: int = 3
) -> List[Dict[str, Any]]:
    """
    Generate multiple budget scenarios (conservative, moderate, aggressive).
    
    Args:
        candidates: Ranked candidate locations
        buildings: Building features
        existing_facilities: Existing facilities
        base_budget: User-specified budget
        facility_cost: Cost per facility
        threshold_meters: Coverage threshold
        scenario_count: Number of scenarios to generate (default: 3)
    
    Returns:
        List of optimization results for different budget levels
    """
    scenarios = []
    
    # Define budget multipliers for scenarios
    if scenario_count == 3:
        multipliers = [0.7, 1.0, 1.3]  # Conservative, Moderate, Aggressive
        labels = ["Conservative", "Moderate", "Aggressive"]
    elif scenario_count == 5:
        multipliers = [0.5, 0.75, 1.0, 1.25, 1.5]
        labels = ["Minimal", "Conservative", "Moderate", "Aggressive", "Maximal"]
    else:
        multipliers = [1.0]
        labels = ["Standard"]
    
    for i, (multiplier, label) in enumerate(zip(multipliers, labels)):
        scenario_budget = base_budget * multiplier
        
        result = greedy_optimization(
            candidates,
            buildings,
            existing_facilities,
            scenario_budget,
            facility_cost,
            threshold_meters
        )
        
        result["scenario_id"] = f"scenario_{i+1}"
        result["scenario_name"] = label
        result["budget"] = scenario_budget
        
        scenarios.append(result)
    
    return scenarios


def compare_scenarios(scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compare multiple budget scenarios and identify best options.
    
    Returns:
        Comparison summary with recommendations
    """
    if not scenarios:
        return {"error": "No scenarios to compare"}
    
    # Find best by different criteria
    best_coverage = max(scenarios, key=lambda s: s["coverage_after"])
    best_efficiency = min(
        [s for s in scenarios if s["buildings_gained"] > 0],
        key=lambda s: s["cost_per_building"],
        default=scenarios[0]
    )
    best_utilization = max(scenarios, key=lambda s: s["budget_utilization_pct"])
    
    return {
        "num_scenarios": len(scenarios),
        "scenarios": scenarios,
        "recommendations": {
            "best_coverage": {
                "scenario_id": best_coverage["scenario_id"],
                "scenario_name": best_coverage["scenario_name"],
                "coverage_after": best_coverage["coverage_after"],
                "buildings_gained": best_coverage["buildings_gained"]
            },
            "best_efficiency": {
                "scenario_id": best_efficiency["scenario_id"],
                "scenario_name": best_efficiency["scenario_name"],
                "cost_per_building": best_efficiency["cost_per_building"],
                "buildings_gained": best_efficiency["buildings_gained"]
            },
            "best_utilization": {
                "scenario_id": best_utilization["scenario_id"],
                "scenario_name": best_utilization["scenario_name"],
                "budget_utilization_pct": best_utilization["budget_utilization_pct"],
                "remaining_budget": best_utilization["remaining_budget"]
            }
        },
        "summary": {
            "budget_range": f"₹{min(s['budget'] for s in scenarios):,.0f} - ₹{max(s['budget'] for s in scenarios):,.0f}",
            "facilities_range": f"{min(s['num_facilities'] for s in scenarios)} - {max(s['num_facilities'] for s in scenarios)}",
            "coverage_range": f"{min(s['coverage_improvement_pct'] for s in scenarios):.1f}% - {max(s['coverage_improvement_pct'] for s in scenarios):.1f}%",
            "cost_efficiency_range": f"₹{min(s['cost_per_building'] for s in scenarios if s['cost_per_building'] > 0):,.0f} - ₹{max(s['cost_per_building'] for s in scenarios if s['cost_per_building'] > 0):,.0f} per building"
        }
    }


def sensitivity_analysis(
    candidates: List[Dict],
    buildings: List[Dict],
    existing_facilities: List[Dict],
    base_budget: float,
    facility_cost: float,
    threshold_meters: float
) -> Dict[str, Any]:
    """
    Perform sensitivity analysis on budget variations.
    
    Shows how coverage changes with budget.
    """
    # Test budget levels from 50% to 200% of base
    budget_levels = [base_budget * m for m in [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]]
    
    results = []
    for budget_level in budget_levels:
        result = greedy_optimization(
            candidates,
            buildings,
            existing_facilities,
            budget_level,
            facility_cost,
            threshold_meters
        )
        
        results.append({
            "budget": budget_level,
            "num_facilities": result["num_facilities"],
            "coverage_after": result["coverage_after"],
            "coverage_improvement_pct": result["coverage_improvement_pct"],
            "cost_per_building": result["cost_per_building"]
        })
    
    return {
        "base_budget": base_budget,
        "facility_cost": facility_cost,
        "budget_levels": results,
        "insights": {
            "diminishing_returns": _check_diminishing_returns(results),
            "optimal_budget_range": _find_optimal_budget_range(results, base_budget)
        }
    }


def _check_diminishing_returns(results: List[Dict]) -> bool:
    """Check if there are diminishing returns with increased budget."""
    if len(results) < 3:
        return False
    
    # Check if marginal gain per facility is decreasing
    marginal_gains = []
    for i in range(1, len(results)):
        if results[i]["num_facilities"] > results[i-1]["num_facilities"]:
            marginal_gain = (results[i]["coverage_after"] - results[i-1]["coverage_after"])
            marginal_gains.append(marginal_gain)
    
    # Diminishing returns if later gains are less than earlier gains
    if len(marginal_gains) >= 2:
        return marginal_gains[-1] < marginal_gains[0] * 0.7
    
    return False


def _find_optimal_budget_range(results: List[Dict], base_budget: float) -> str:
    """Identify optimal budget range based on cost efficiency."""
    if not results:
        return "Insufficient data"
    
    # Find the "elbow" point where efficiency starts dropping significantly
    best_efficiency = min(r["cost_per_building"] for r in results if r["cost_per_building"] > 0)
    
    optimal_results = [
        r for r in results
        if r["cost_per_building"] > 0 and r["cost_per_building"] <= best_efficiency * 1.3
    ]
    
    if optimal_results:
        min_budget = min(r["budget"] for r in optimal_results)
        max_budget = max(r["budget"] for r in optimal_results)
        return f"₹{min_budget:,.0f} - ₹{max_budget:,.0f}"
    
    return f"Around ₹{base_budget:,.0f}"
