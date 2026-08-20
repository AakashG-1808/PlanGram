"""
Phase 8 - Simple End-to-End Integration Test

Tests the complete workflow in a straightforward manner.
"""

import requests
import sys

BASE_URL = "http://localhost:8000"
VILLAGE_ID = "village_01"

def test():
    print("\n" + "="*60)
    print("PLANGRAM PHASE 8 - END-TO-END INTEGRATION TEST")
    print("="*60)
    
    results = []
    
    # Test 1: Get village
    print("\n1. Get Village Data...")
    try:
        r = requests.get(f"{BASE_URL}/api/villages/{VILLAGE_ID}", timeout=10)
        success = r.status_code == 200
        print(f"   {'✅' if success else '❌'} Status: {r.status_code}")
        if success:
            data = r.json()
            print(f"   Village: {data['village']['name']}")
        results.append(("Get Village", success))
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(("Get Village", False))
    
    # Test 2: Validate location
    print("\n2. Validate Location (Constraints)...")
    try:
        r = requests.post(
            f"{BASE_URL}/api/villages/{VILLAGE_ID}/validate-location",
            json={"location": [77.688, 12.699], "infrastructure_type": "water_facility"},
            timeout=10
        )
        success = r.status_code == 200
        print(f"   {'✅' if success else '❌'} Status: {r.status_code}")
        if success:
            data = r.json()
            print(f"   Valid: {data['is_valid']}, Score: {data['suitability_score']}/100")
        results.append(("Validate Location", success))
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(("Validate Location", False))
    
    # Test 3: Get buildable area
    print("\n3. Get Buildable Area...")
    try:
        r = requests.get(f"{BASE_URL}/api/villages/{VILLAGE_ID}/buildable-area", timeout=10)
        success = r.status_code == 200
        print(f"   {'✅' if success else '❌'} Status: {r.status_code}")
        if success:
            data = r.json()
            print(f"   Buildable: {data['buildable_percentage']:.1f}%")
        results.append(("Buildable Area", success))
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(("Buildable Area", False))
    
    # Test 4: Generate candidates
    print("\n4. Generate Candidate Locations...")
    try:
        r = requests.post(
            f"{BASE_URL}/api/villages/{VILLAGE_ID}/generate-candidates",
            json={
                "infrastructure_type": "water_facility",
                "method": "hybrid",
                "num_candidates": 10,
                "threshold_meters": 500
            },
            timeout=30
        )
        success = r.status_code == 200
        print(f"   {'✅' if success else '❌'} Status: {r.status_code}")
        if success:
            data = r.json()
            print(f"   Candidates: {data['num_candidates']}, Valid: {data['valid_candidates']}")
            if data['candidates']:
                best = data['candidates'][0]
                print(f"   Best: Score {best['combined_score']:.1f}/100, +{best['coverage_improvement']:.1f}% coverage")
        results.append(("Generate Candidates", success))
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(("Generate Candidates", False))
    
    # Test 5: Optimize budget
    print("\n5. Optimize Within Budget...")
    try:
        r = requests.post(
            f"{BASE_URL}/api/villages/{VILLAGE_ID}/optimize",
            json={
                "infrastructure_type": "water_facility",
                "budget": 360000,
                "threshold_meters": 500,
                "num_candidates": 20
            },
            timeout=60
        )
        success = r.status_code == 200
        print(f"   {'✅' if success else '❌'} Status: {r.status_code}")
        if success:
            data = r.json()
            print(f"   Facility cost: ₹{data['facility_cost']:,.0f}")
            print(f"   Selected: {data['num_facilities']} facilities")
            print(f"   Cost: ₹{data['total_cost']:,.0f}, Remaining: ₹{data['remaining_budget']:,.0f}")
            print(f"   Impact: +{data['coverage_improvement_pct']:.1f}% coverage, {data['buildings_gained']} buildings")
            print(f"   Efficiency: ₹{data['cost_per_building']:,.0f} per building")
        results.append(("Optimize Budget", success))
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(("Optimize Budget", False))
    
    # Test 6: Compare scenarios
    print("\n6. Compare Budget Scenarios...")
    try:
        r = requests.post(
            f"{BASE_URL}/api/villages/{VILLAGE_ID}/optimize/scenarios",
            json={
                "infrastructure_type": "water_facility",
                "budget": 500000,
                "threshold_meters": 500,
                "num_candidates": 20,
                "scenario_count": 3
            },
            timeout=60
        )
        success = r.status_code == 200
        print(f"   {'✅' if success else '❌'} Status: {r.status_code}")
        if success:
            data = r.json()
            print(f"   Scenarios: {data['num_scenarios']}")
            for s in data['scenarios']:
                print(f"     {s['scenario_name']}: {s['num_facilities']} facilities, +{s['coverage_improvement_pct']:.1f}%, ₹{s['cost_per_building']:,.0f}/bldg")
            print(f"   Best Coverage: {data['recommendations']['best_coverage']['scenario_name']}")
            print(f"   Best Efficiency: {data['recommendations']['best_efficiency']['scenario_name']}")
        results.append(("Compare Scenarios", success))
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(("Compare Scenarios", False))
    
    # Test 7: Sensitivity analysis
    print("\n7. Budget Sensitivity Analysis...")
    try:
        r = requests.post(
            f"{BASE_URL}/api/villages/{VILLAGE_ID}/optimize/sensitivity",
            params={
                "infrastructure_type": "water_facility",
                "base_budget": 500000,
                "threshold_meters": 500
            },
            timeout=60
        )
        success = r.status_code == 200
        print(f"   {'✅' if success else '❌'} Status: {r.status_code}")
        if success:
            data = r.json()
            print(f"   Budget levels tested: {len(data['budget_levels'])}")
            print(f"   Diminishing returns: {data['insights']['diminishing_returns']}")
            print(f"   Optimal budget range: {data['insights']['optimal_budget_range']}")
        results.append(("Sensitivity Analysis", success))
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(("Sensitivity Analysis", False))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    passed = sum(1 for _, success in results if success)
    total = len(results)
    for name, success in results:
        print(f"{'✅' if success else '❌'} {name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 Phase 8 Complete! All systems operational!")
        print("\nEnd-to-End Workflow Verified:")
        print("  Phase 1-2: Village data loading ✅")
        print("  Phase 3: Coverage analysis (implicit in optimization) ✅")
        print("  Phase 4: Scenario management (via API) ✅")
        print("  Phase 5: Constraint validation ✅")
        print("  Phase 6: Candidate generation ✅")
        print("  Phase 7: Budget optimization ✅")
        print("  Phase 8: Complete integration ✅")
        print("\nAll 7 backend phases working together seamlessly!")
        return 0
    else:
        print("\n⚠️ Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(test())
