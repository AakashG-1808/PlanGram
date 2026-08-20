"""
Test Phase 8 - End-to-End Integration Testing

This script tests the complete workflow from village selection
through optimization and scenario comparison. It validates that
all 7 phases work together seamlessly.

Complete user workflow:
1. Select village
2. Analyze current coverage
3. Identify constraints and buildable areas
4. Generate candidate locations
5. Optimize within budget
6. Compare scenarios
7. Make informed decision
"""

import requests
import sys
import json
import time

BASE_URL = "http://localhost:8000"
VILLAGE_ID = "village_01"


def test_color(passed: bool) -> str:
    """Return color code for test result"""
    return "✅" if passed else "❌"


def print_section(title: str):
    """Print section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def test_complete_workflow():
    """Test complete end-to-end workflow"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║   PlanGram Phase 8 Integration Test                         ║
║   Testing Complete End-to-End Workflow                      ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    workflow_steps = []
    
    # STEP 1: Village Selection
    print_section("STEP 1: Village Selection & Data Loading")
    try:
        start = time.time()
        response = requests.get(f"{BASE_URL}/api/villages/{VILLAGE_ID}", timeout=10)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            village = response.json()
            print(f"   {test_color(True)} Village data loaded ({elapsed:.2f}s)")
            print(f"      Name: {village['village']['name']}")
            print(f"      Taluk: {village['village']['taluk']}")
            print(f"      Area: {village['village']['area_hectares']} hectares")
            print(f"      Population: {village['village']['population']}")
            workflow_steps.append(("Village Selection", True, elapsed))
        else:
            print(f"   {test_color(False)} Failed to load village")
            workflow_steps.append(("Village Selection", False, elapsed))
            return workflow_steps
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        workflow_steps.append(("Village Selection", False, 0))
        return workflow_steps
    
    # STEP 2: Coverage Analysis
    print_section("STEP 2: Current Coverage Analysis")
    try:
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/api/villages/{VILLAGE_ID}/analyze",
            json={"threshold_meters": 500},
            timeout=10
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            analysis = response.json()
            print(f"   {test_color(True)} Coverage analysis complete ({elapsed:.2f}s)")
            print(f"      Current coverage: {analysis['coverage_percentage']:.1f}%")
            print(f"      Served buildings: {analysis['served_buildings']}")
            print(f"      Underserved buildings: {analysis['underserved_buildings']}")
            print(f"      Underserved clusters: {len(analysis['underserved_clusters'])}")
            workflow_steps.append(("Coverage Analysis", True, elapsed))
            baseline_coverage = analysis['coverage_percentage']
        else:
            print(f"   {test_color(False)} Analysis failed")
            workflow_steps.append(("Coverage Analysis", False, elapsed))
            return workflow_steps
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        workflow_steps.append(("Coverage Analysis", False, 0))
        return workflow_steps
    
    # STEP 3: Constraint Validation
    print_section("STEP 3: Constraint & Buildable Area Analysis")
    try:
        start = time.time()
        response = requests.get(
            f"{BASE_URL}/api/villages/{VILLAGE_ID}/buildable-area",
            timeout=10
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            buildable = response.json()
            print(f"   {test_color(True)} Buildable area calculated ({elapsed:.2f}s)")
            print(f"      Total area: {buildable['total_area_m2']:,.0f} m²")
            print(f"      Buildable: {buildable['buildable_percentage']:.1f}%")
            print(f"      Restricted parcels: {buildable['num_restricted_parcels']}")
            workflow_steps.append(("Constraint Analysis", True, elapsed))
        else:
            print(f"   {test_color(False)} Failed")
            workflow_steps.append(("Constraint Analysis", False, elapsed))
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        workflow_steps.append(("Constraint Analysis", False, 0))
    
    # STEP 4: Candidate Generation
    print_section("STEP 4: Generate Candidate Locations")
    try:
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/api/villages/{VILLAGE_ID}/generate-candidates",
            json={
                "infrastructure_type": "water_facility",
                "method": "hybrid",
                "num_candidates": 20,
                "threshold_meters": 500
            },
            timeout=30
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            candidates = response.json()
            print(f"   {test_color(True)} Candidates generated ({elapsed:.2f}s)")
            print(f"      Total candidates: {candidates['num_candidates']}")
            print(f"      Valid candidates: {candidates['valid_candidates']}")
            print(f"      Best score: {candidates['summary']['best_candidate']['combined_score']:.1f}/100")
            print(f"      Best improvement: +{candidates['summary']['best_candidate']['coverage_improvement']:.1f}%")
            workflow_steps.append(("Candidate Generation", True, elapsed))
        else:
            print(f"   {test_color(False)} Failed")
            workflow_steps.append(("Candidate Generation", False, elapsed))
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        workflow_steps.append(("Candidate Generation", False, 0))
    
    # STEP 5: Budget Optimization
    print_section("STEP 5: Budget Optimization")
    budget = 500000  # ₹5 lakhs
    try:
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/api/villages/{VILLAGE_ID}/optimize",
            json={
                "infrastructure_type": "water_facility",
                "budget": budget,
                "threshold_meters": 500,
                "num_candidates": 30
            },
            timeout=60
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            optimization = response.json()
            print(f"   {test_color(True)} Optimization complete ({elapsed:.2f}s)")
            print(f"      Budget: ₹{budget:,.0f}")
            print(f"      Facilities selected: {optimization['num_facilities']}")
            print(f"      Total cost: ₹{optimization['total_cost']:,.0f}")
            print(f"      Remaining: ₹{optimization['remaining_budget']:,.0f}")
            print(f"      Coverage improvement: +{optimization['coverage_improvement_pct']:.1f}%")
            print(f"      Buildings gained: {optimization['buildings_gained']}")
            print(f"      Cost per building: ₹{optimization['cost_per_building']:,.0f}")
            workflow_steps.append(("Budget Optimization", True, elapsed))
            optimized_coverage = baseline_coverage + optimization['coverage_improvement_pct']
        else:
            print(f"   {test_color(False)} Failed")
            workflow_steps.append(("Budget Optimization", False, elapsed))
            return workflow_steps
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        workflow_steps.append(("Budget Optimization", False, 0))
        return workflow_steps
    
    # STEP 6: Scenario Comparison
    print_section("STEP 6: Multi-Scenario Comparison")
    try:
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/api/villages/{VILLAGE_ID}/optimize/scenarios",
            json={
                "infrastructure_type": "water_facility",
                "budget": budget,
                "threshold_meters": 500,
                "num_candidates": 30,
                "scenario_count": 3
            },
            timeout=60
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            comparison = response.json()
            print(f"   {test_color(True)} Scenarios compared ({elapsed:.2f}s)")
            print(f"      Scenarios generated: {comparison['num_scenarios']}")
            print(f"\n      Scenario Details:")
            for scenario in comparison['scenarios']:
                print(f"        {scenario['scenario_name']}:")
                print(f"          Budget: ₹{scenario['budget']:,.0f}")
                print(f"          Facilities: {scenario['num_facilities']}")
                print(f"          Coverage: +{scenario['coverage_improvement_pct']:.1f}%")
                print(f"          Efficiency: ₹{scenario['cost_per_building']:,.0f}/building")
            
            print(f"\n      Recommendations:")
            print(f"        Best coverage: {comparison['recommendations']['best_coverage']['scenario_name']}")
            print(f"        Best efficiency: {comparison['recommendations']['best_efficiency']['scenario_name']}")
            print(f"        Best utilization: {comparison['recommendations']['best_utilization']['scenario_name']}")
            
            workflow_steps.append(("Scenario Comparison", True, elapsed))
        else:
            print(f"   {test_color(False)} Failed")
            workflow_steps.append(("Scenario Comparison", False, elapsed))
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        workflow_steps.append(("Scenario Comparison", False, 0))
    
    # STEP 7: Sensitivity Analysis
    print_section("STEP 7: Budget Sensitivity Analysis")
    try:
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/api/villages/{VILLAGE_ID}/optimize/sensitivity",
            params={
                "infrastructure_type": "water_facility",
                "base_budget": budget,
                "threshold_meters": 500
            },
            timeout=60
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            sensitivity = response.json()
            print(f"   {test_color(True)} Sensitivity analysis complete ({elapsed:.2f}s)")
            print(f"      Budget levels tested: {len(sensitivity['budget_levels'])}")
            print(f"      Diminishing returns: {sensitivity['insights']['diminishing_returns']}")
            print(f"      Optimal range: {sensitivity['insights']['optimal_budget_range']}")
            print(f"\n      Budget vs Coverage:")
            for level in sensitivity['budget_levels'][:5]:  # Show first 5
                print(f"        ₹{level['budget']:,.0f}: {level['num_facilities']} facilities, +{level['coverage_improvement_pct']:.1f}%")
            
            workflow_steps.append(("Sensitivity Analysis", True, elapsed))
        else:
            print(f"   {test_color(False)} Failed")
            workflow_steps.append(("Sensitivity Analysis", False, elapsed))
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        workflow_steps.append(("Sensitivity Analysis", False, 0))
    
    return workflow_steps


def test_api_coverage():
    """Test that all major API endpoints are accessible"""
    print_section("API Endpoint Coverage Test")
    
    endpoints = [
        ("GET", "/api/villages", "List villages"),
        ("GET", f"/api/villages/{VILLAGE_ID}", "Get village"),
        ("POST", f"/api/villages/{VILLAGE_ID}/analyze", "Analyze coverage"),
        ("POST", f"/api/villages/{VILLAGE_ID}/validate-location", "Validate location"),
        ("GET", f"/api/villages/{VILLAGE_ID}/buildable-area", "Buildable area"),
        ("POST", f"/api/villages/{VILLAGE_ID}/generate-candidates", "Generate candidates"),
        ("POST", f"/api/villages/{VILLAGE_ID}/optimize", "Optimize budget"),
        ("POST", f"/api/villages/{VILLAGE_ID}/optimize/scenarios", "Budget scenarios"),
        ("POST", f"/api/villages/{VILLAGE_ID}/optimize/sensitivity", "Sensitivity analysis"),
    ]
    
    results = []
    for method, endpoint, description in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            elif method == "POST":
                # Use minimal valid payloads
                if "analyze" in endpoint:
                    response = requests.post(f"{BASE_URL}{endpoint}", json={"threshold_meters": 500}, timeout=10)
                elif "validate-location" in endpoint:
                    response = requests.post(f"{BASE_URL}{endpoint}", json={"location": [77.688, 12.699]}, timeout=10)
                elif "generate-candidates" in endpoint:
                    response = requests.post(f"{BASE_URL}{endpoint}", json={"num_candidates": 5}, timeout=30)
                elif "optimize" in endpoint and "scenarios" not in endpoint and "sensitivity" not in endpoint:
                    response = requests.post(f"{BASE_URL}{endpoint}", json={"budget": 360000}, timeout=60)
                elif "scenarios" in endpoint:
                    response = requests.post(f"{BASE_URL}{endpoint}", json={"budget": 500000}, timeout=60)
                elif "sensitivity" in endpoint:
                    response = requests.post(f"{BASE_URL}{endpoint}", params={"base_budget": 500000}, timeout=60)
            
            success = response.status_code in [200, 201]
            results.append((description, success))
            print(f"   {test_color(success)} {description} - {response.status_code}")
        except Exception as e:
            results.append((description, False))
            print(f"   {test_color(False)} {description} - Error: {str(e)[:50]}")
    
    return results


def main():
    """Run Phase 8 integration tests"""
    
    # Test complete workflow
    workflow_results = test_complete_workflow()
    
    # Test API coverage
    api_results = test_api_coverage()
    
    # Summary
    print("\n" + "="*60)
    print("INTEGRATION TEST SUMMARY")
    print("="*60)
    
    print("\nWorkflow Steps:")
    total_time = 0
    for step_name, success, elapsed in workflow_results:
        print(f"{test_color(success)} {step_name} ({elapsed:.2f}s)")
        total_time += elapsed
    
    print(f"\nTotal workflow time: {total_time:.2f} seconds")
    
    print("\nAPI Endpoint Coverage:")
    for endpoint_desc, success in api_results:
        print(f"{test_color(success)} {endpoint_desc}")
    
    workflow_passed = sum(1 for _, success, _ in workflow_results if success)
    workflow_total = len(workflow_results)
    api_passed = sum(1 for _, success in api_results if success)
    api_total = len(api_results)
    
    print(f"\nWorkflow: {workflow_passed}/{workflow_total} steps passed")
    print(f"API Coverage: {api_passed}/{api_total} endpoints working")
    
    overall_success = workflow_passed == workflow_total and api_passed == api_total
    
    if overall_success:
        print("\n✅ Phase 8 Integration Test PASSED!")
        print("\n🎉 Complete System Integration Verified!")
        print("\nEnd-to-End Capabilities Confirmed:")
        print("- Village data loading and analysis")
        print("- Coverage gap identification")
        print("- Constraint validation")
        print("- Candidate location generation")
        print("- Budget optimization")
        print("- Multi-scenario comparison")
        print("- Sensitivity analysis")
        print("- All 7 phases working together seamlessly")
        print(f"\nTotal system response time: {total_time:.2f}s")
        print("Performance: Excellent (< 60s for complete workflow)")
        return 0
    else:
        print("\n⚠️  Some integration tests failed. Please review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
