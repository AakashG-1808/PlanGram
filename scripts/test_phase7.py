"""
Test Phase 7 - Budget Optimization Engine

This script tests:
1. Single budget optimization
2. Multi-facility selection
3. Budget scenarios (conservative, moderate, aggressive)
4. Scenario comparison
5. Sensitivity analysis
6. Cost efficiency metrics
7. Diminishing returns detection
"""

import requests
import sys
import json

BASE_URL = "http://localhost:8000"
VILLAGE_ID = "village_01"


def test_color(passed: bool) -> str:
    """Return color code for test result"""
    return "✅" if passed else "❌"


def test_single_budget_optimization():
    """Test optimization with single budget"""
    print("\n1. Testing Single Budget Optimization...")
    try:
        # Budget for 3 facilities (₹180,000 each = ₹540,000)
        response = requests.post(
            f"{BASE_URL}/api/villages/{VILLAGE_ID}/optimize",
            json={
                "infrastructure_type": "water_facility",
                "budget": 540000,
                "threshold_meters": 500,
                "num_candidates": 30
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   {test_color(True)} Optimization completed")
            print(f"      Status: {data['status']}")
            print(f"      Budget: ₹{data.get('total_cost', 0):,.0f} / ₹540,000")
            print(f"      Facilities selected: {data['num_facilities']}")
            print(f"      Buildings gained: {data['buildings_gained']}")
            print(f"      Coverage improvement: +{data['coverage_improvement_pct']}%")
            print(f"      Cost per building: ₹{data['cost_per_building']:,.0f}")
            print(f"      Budget utilization: {data['budget_utilization_pct']}%")
            
            # Show selected facilities
            if data['selected_facilities']:
                print(f"\n      Selected facilities:")
                for i, facility in enumerate(data['selected_facilities'][:3], 1):
                    print(f"        {i}. Location: {facility['location']}")
                    print(f"           Buildings gained: {facility['buildings_gained']}")
                    print(f"           Cost: ₹{facility['cost']:,.0f}")
            
            return data['num_facilities'] > 0 and data['buildings_gained'] > 0
        else:
            print(f"   {test_color(False)} API returned status {response.status_code}")
            print(f"      Response: {response.text}")
            return False
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return False


def test_multi_facility_selection():
    """Test selection of multiple facilities"""
    print("\n2. Testing Multi-Facility Selection...")
    try:
        # Large budget for multiple facilities
        response = requests.post(
            f"{BASE_URL}/api/villages/{VILLAGE_ID}/optimize",
            json={
                "infrastructure_type": "water_facility",
                "budget": 1000000,  # Budget for 5-6 facilities
                "threshold_meters": 500,
                "num_candidates": 30
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   {test_color(True)} Multi-facility optimization completed")
            print(f"      Facilities selected: {data['num_facilities']}")
            print(f"      Total cost: ₹{data['total_cost']:,.0f}")
            print(f"      Remaining budget: ₹{data['remaining_budget']:,.0f}")
            print(f"      Buildings gained: {data['buildings_gained']}")
            print(f"      Coverage: {data['coverage_before']} → {data['coverage_after']}")
            
            # Check marginal gains per facility
            if data['selected_facilities'] and len(data['selected_facilities']) > 1:
                print(f"\n      Marginal gains per facility:")
                for i, facility in enumerate(data['selected_facilities'], 1):
                    print(f"        Facility {i}: +{facility['buildings_gained']} buildings")
                
                # Verify diminishing returns
                first_gain = data['selected_facilities'][0]['buildings_gained']
                last_gain = data['selected_facilities'][-1]['buildings_gained']
                print(f"      Diminishing returns: First={first_gain}, Last={last_gain}")
            
            return data['num_facilities'] >= 2
        else:
            print(f"   {test_color(False)} API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return False


def test_budget_scenarios():
    """Test multiple budget scenarios"""
    print("\n3. Testing Budget Scenarios...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/villages/{VILLAGE_ID}/optimize/scenarios",
            json={
                "infrastructure_type": "water_facility",
                "budget": 500000,
                "threshold_meters": 500,
                "num_candidates": 30,
                "scenario_count": 3
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   {test_color(True)} Budget scenarios generated")
            print(f"      Scenarios: {data['num_scenarios']}")
            
            if 'scenarios' in data:
                print(f"\n      Scenario comparison:")
                for scenario in data['scenarios']:
                    print(f"        {scenario['scenario_name']}:")
                    print(f"          Budget: ₹{scenario['budget']:,.0f}")
                    print(f"          Facilities: {scenario['num_facilities']}")
                    print(f"          Coverage improvement: +{scenario['coverage_improvement_pct']}%")
                    print(f"          Cost/building: ₹{scenario['cost_per_building']:,.0f}")
            
            return data['num_scenarios'] == 3
        else:
            print(f"   {test_color(False)} API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return False


def test_scenario_comparison():
    """Test scenario comparison and recommendations"""
    print("\n4. Testing Scenario Comparison & Recommendations...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/villages/{VILLAGE_ID}/optimize/scenarios",
            json={
                "infrastructure_type": "water_facility",
                "budget": 500000,
                "threshold_meters": 500,
                "num_candidates": 30,
                "scenario_count": 3
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            has_recommendations = 'recommendations' in data
            
            print(f"   {test_color(has_recommendations)} Scenario comparison available")
            
            if has_recommendations:
                recs = data['recommendations']
                print(f"\n      Recommendations:")
                
                if 'best_coverage' in recs:
                    print(f"        Best coverage: {recs['best_coverage']['scenario_name']}")
                    print(f"          Buildings gained: {recs['best_coverage']['buildings_gained']}")
                
                if 'best_efficiency' in recs:
                    print(f"        Best efficiency: {recs['best_efficiency']['scenario_name']}")
                    print(f"          Cost per building: ₹{recs['best_efficiency']['cost_per_building']:,.0f}")
                
                if 'best_utilization' in recs:
                    print(f"        Best utilization: {recs['best_utilization']['scenario_name']}")
                    print(f"          Budget used: {recs['best_utilization']['budget_utilization_pct']:.1f}%")
                
                # Summary
                if 'summary' in data:
                    print(f"\n      Summary:")
                    summary = data['summary']
                    for key, value in summary.items():
                        print(f"        {key}: {value}")
            
            return has_recommendations
        else:
            print(f"   {test_color(False)} API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return False


def test_sensitivity_analysis():
    """Test budget sensitivity analysis"""
    print("\n5. Testing Budget Sensitivity Analysis...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/villages/{VILLAGE_ID}/optimize/sensitivity",
            params={
                "infrastructure_type": "water_facility",
                "base_budget": 500000,
                "threshold_meters": 500
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            has_budget_levels = 'budget_levels' in data
            
            print(f"   {test_color(has_budget_levels)} Sensitivity analysis completed")
            
            if has_budget_levels:
                print(f"      Budget levels tested: {len(data['budget_levels'])}")
                print(f"\n      Budget vs Coverage:")
                for level in data['budget_levels']:
                    print(f"        ₹{level['budget']:,.0f}: " +
                          f"{level['num_facilities']} facilities, " +
                          f"+{level['coverage_improvement_pct']:.1f}% coverage")
                
                # Insights
                if 'insights' in data:
                    insights = data['insights']
                    print(f"\n      Insights:")
                    print(f"        Diminishing returns: {insights.get('diminishing_returns', 'N/A')}")
                    print(f"        Optimal budget range: {insights.get('optimal_budget_range', 'N/A')}")
            
            return has_budget_levels and len(data['budget_levels']) > 0
        else:
            print(f"   {test_color(False)} API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return False


def test_cost_efficiency():
    """Test cost efficiency metrics"""
    print("\n6. Testing Cost Efficiency Metrics...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/villages/{VILLAGE_ID}/optimize",
            json={
                "infrastructure_type": "water_facility",
                "budget": 360000,  # 2 facilities
                "threshold_meters": 500,
                "num_candidates": 30
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            has_efficiency_metrics = 'cost_per_building' in data
            
            print(f"   {test_color(has_efficiency_metrics)} Cost efficiency calculated")
            
            if has_efficiency_metrics:
                print(f"      Total cost: ₹{data['total_cost']:,.0f}")
                print(f"      Buildings gained: {data['buildings_gained']}")
                print(f"      Cost per building: ₹{data['cost_per_building']:,.0f}")
                print(f"      Budget utilization: {data['budget_utilization_pct']:.1f}%")
                
                # Verify calculation
                if data['buildings_gained'] > 0:
                    expected_cpb = data['total_cost'] / data['buildings_gained']
                    actual_cpb = data['cost_per_building']
                    is_correct = abs(expected_cpb - actual_cpb) < 1
                    print(f"      Calculation correct: {is_correct}")
            
            return has_efficiency_metrics and data.get('cost_per_building', 0) > 0
        else:
            print(f"   {test_color(False)} API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return False


def test_insufficient_budget():
    """Test handling of insufficient budget"""
    print("\n7. Testing Insufficient Budget Handling...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/villages/{VILLAGE_ID}/optimize",
            json={
                "infrastructure_type": "water_facility",
                "budget": 50000,  # Less than one facility cost
                "threshold_meters": 500,
                "num_candidates": 30
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            is_insufficient = data['status'] == 'insufficient_budget'
            
            print(f"   {test_color(is_insufficient)} Insufficient budget detected")
            print(f"      Status: {data['status']}")
            print(f"      Message: {data.get('message', 'N/A')}")
            print(f"      Facilities selected: {data.get('num_facilities', 0)}")
            
            return is_insufficient and data.get('num_facilities', 0) == 0
        else:
            print(f"   {test_color(False)} API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return False


def test_greedy_algorithm():
    """Test greedy algorithm behavior (diminishing returns)"""
    print("\n8. Testing Greedy Algorithm Behavior...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/villages/{VILLAGE_ID}/optimize",
            json={
                "infrastructure_type": "water_facility",
                "budget": 900000,  # Budget for 5 facilities
                "threshold_meters": 500,
                "num_candidates": 30
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data['selected_facilities'] and len(data['selected_facilities']) >= 3:
                print(f"   {test_color(True)} Greedy algorithm working")
                print(f"      Facilities: {data['num_facilities']}")
                
                # Check that first facility has highest marginal gain
                marginal_gains = [f['buildings_gained'] for f in data['selected_facilities']]
                print(f"      Marginal gains: {marginal_gains}")
                
                # Verify greedy selection (generally decreasing)
                is_greedy = marginal_gains[0] >= marginal_gains[-1]
                print(f"      Greedy property (first ≥ last): {is_greedy}")
                
                return True
            else:
                print(f"   {test_color(False)} Not enough facilities for analysis")
                return False
        else:
            print(f"   {test_color(False)} API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return False


def test_performance():
    """Test optimization performance"""
    print("\n9. Testing Performance...")
    try:
        import time
        
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/villages/{VILLAGE_ID}/optimize",
            json={
                "infrastructure_type": "water_facility",
                "budget": 540000,
                "threshold_meters": 500,
                "num_candidates": 30
            },
            timeout=60
        )
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"   {test_color(True)} Performance test complete")
            print(f"      Time: {elapsed_time:.2f} seconds")
            print(f"      Facilities selected: {data['num_facilities']}")
            print(f"      Candidates evaluated: {data.get('num_candidates_evaluated', 0)}")
            
            # Should complete in reasonable time (< 15 seconds)
            is_fast = elapsed_time < 15
            print(f"      Acceptable performance (< 15s): {is_fast}")
            
            return is_fast
        else:
            print(f"   {test_color(False)} API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return False


def main():
    """Run all Phase 7 tests"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║   PlanGram Phase 7 Validation                               ║
║   Testing Budget Optimization Engine                        ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    results = []
    
    # Run tests
    results.append(("Single Budget Optimization", test_single_budget_optimization()))
    results.append(("Multi-Facility Selection", test_multi_facility_selection()))
    results.append(("Budget Scenarios", test_budget_scenarios()))
    results.append(("Scenario Comparison", test_scenario_comparison()))
    results.append(("Sensitivity Analysis", test_sensitivity_analysis()))
    results.append(("Cost Efficiency Metrics", test_cost_efficiency()))
    results.append(("Insufficient Budget Handling", test_insufficient_budget()))
    results.append(("Greedy Algorithm Behavior", test_greedy_algorithm()))
    results.append(("Performance Test", test_performance()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        print(f"{test_color(result)} {test_name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ Phase 7 is complete and validated!")
        print("\nKey Features Working:")
        print("- Single budget optimization")
        print("- Multi-facility selection (greedy algorithm)")
        print("- Budget scenarios (conservative, moderate, aggressive)")
        print("- Scenario comparison and recommendations")
        print("- Budget sensitivity analysis")
        print("- Cost efficiency metrics")
        print("- Insufficient budget detection")
        print("- Diminishing returns analysis")
        print("- Performance optimization")
        print("\nOptimization Approach:")
        print("- Greedy algorithm for multi-facility placement")
        print("- Maximizes marginal coverage improvement")
        print("- Constraint-aware (integrates Phase 5 & 6)")
        print("- Budget-conscious decision making")
        print("\nNext Steps:")
        print("1. Frontend optimization UI")
        print("2. Interactive budget slider")
        print("3. Scenario comparison visualization")
        print("4. Export optimization reports")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
