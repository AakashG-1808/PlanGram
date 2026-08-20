"""
Test Phase 3 - Spatial Analysis Implementation

This script tests:
1. Village metrics API with coverage analysis
2. Infrastructure-specific analysis
3. Building distances calculation
4. Underserved area identification
5. Priority assessment
"""

import requests
import sys

BASE_URL = "http://localhost:8000"


def test_color(passed: bool) -> str:
    """Return color code for test result"""
    return "✅" if passed else "❌"


def test_village_metrics():
    """Test comprehensive village metrics"""
    print("\n1. Testing Village Metrics API...")
    try:
        response = requests.get(f"{BASE_URL}/api/villages/village_01/metrics", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   {test_color(True)} Village metrics calculated successfully")
            
            # Basic stats
            print(f"      Village: {data['village_name']}")
            print(f"      Total households: {data['total_households']}")
            print(f"      Water facilities: {data['water_facilities']}")
            
            # Coverage metrics
            if data.get('water_coverage'):
                coverage = data['water_coverage']
                print(f"      Water coverage: {coverage['coverage_percentage']:.1f}%")
                print(f"      Served households: {coverage['served_households']}")
                print(f"      Underserved households: {coverage['underserved_households']}")
                print(f"      Average distance: {coverage['average_distance']:.0f}m")
                
                # Priority
                print(f"      Priority level: {data['priority_level']}")
                
                # Underserved clusters
                cluster_count = len(data.get('underserved_clusters', []))
                print(f"      Underserved clusters: {cluster_count}")
                
                return (coverage['served_households'] + coverage['underserved_households'] == 
                       data['total_households'])
            else:
                print(f"   {test_color(False)} No water coverage data")
                return False
        else:
            print(f"   {test_color(False)} API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return False


def test_threshold_variation():
    """Test metrics with different thresholds"""
    print("\n2. Testing Threshold Variation...")
    try:
        thresholds = [300, 500, 800]
        results = []
        
        for threshold in thresholds:
            response = requests.get(
                f"{BASE_URL}/api/villages/village_01/metrics",
                params={"threshold": threshold},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                coverage = data['water_coverage']
                results.append({
                    'threshold': threshold,
                    'coverage': coverage['coverage_percentage'],
                    'served': coverage['served_households']
                })
                print(f"   {test_color(True)} {threshold}m: {coverage['coverage_percentage']:.1f}% " +
                      f"({coverage['served_households']} households)")
            else:
                print(f"   {test_color(False)} Failed at threshold {threshold}m")
                return False
        
        # Verify coverage increases with threshold
        coverages = [r['coverage'] for r in results]
        increasing = all(coverages[i] <= coverages[i+1] for i in range(len(coverages)-1))
        
        if increasing:
            print(f"   {test_color(True)} Coverage correctly increases with threshold")
        else:
            print(f"   {test_color(False)} Coverage does not increase monotonically")
        
        return increasing
        
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return False


def test_infrastructure_analysis():
    """Test infrastructure-specific analysis"""
    print("\n3. Testing Infrastructure Analysis...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/villages/village_01/analysis/water",
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   {test_color(True)} Infrastructure analysis completed")
            print(f"      Infrastructure type: {data['infrastructure_type']}")
            print(f"      Facility count: {data['facility_count']}")
            print(f"      Coverage: {data['coverage']['coverage_percentage']:.1f}%")
            print(f"      Recommendations: {len(data['recommendations'])}")
            
            if data['recommendations']:
                print(f"      - {data['recommendations'][0]}")
            
            return data['facility_count'] > 0
        else:
            print(f"   {test_color(False)} API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return False


def test_building_distances():
    """Test building distances calculation"""
    print("\n4. Testing Building Distances...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/villages/village_01/building-distances",
            params={"infrastructure_type": "water"},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            distances = data.get('building_distances', {})
            print(f"   {test_color(True)} Building distances calculated")
            print(f"      Buildings analyzed: {data.get('count', 0)}")
            
            if distances:
                distance_values = list(distances.values())
                print(f"      Min distance: {min(distance_values):.0f}m")
                print(f"      Max distance: {max(distance_values):.0f}m")
                print(f"      Avg distance: {sum(distance_values)/len(distance_values):.0f}m")
            
            return len(distances) > 0
        else:
            print(f"   {test_color(False)} API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return False


def test_both_villages():
    """Test that both villages have analysis"""
    print("\n5. Testing Both Villages...")
    villages = ['village_01', 'village_02']
    all_passed = True
    
    for village_id in villages:
        try:
            response = requests.get(
                f"{BASE_URL}/api/villages/{village_id}/metrics",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                coverage = data.get('water_coverage')
                if coverage:
                    print(f"   {test_color(True)} {data['village_name']}: " +
                          f"{coverage['coverage_percentage']:.1f}% coverage")
                else:
                    print(f"   {test_color(False)} {village_id}: No coverage data")
                    all_passed = False
            else:
                print(f"   {test_color(False)} {village_id}: status {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"   {test_color(False)} {village_id}: {e}")
            all_passed = False
    
    return all_passed


def test_underserved_clusters():
    """Test underserved cluster identification"""
    print("\n6. Testing Underserved Cluster Identification...")
    try:
        response = requests.get(f"{BASE_URL}/api/villages/village_01/metrics", timeout=10)
        if response.status_code == 200:
            data = response.json()
            clusters = data.get('underserved_clusters', [])
            
            print(f"   {test_color(True)} Found {len(clusters)} underserved clusters")
            
            for i, cluster in enumerate(clusters[:3], 1):
                print(f"      Cluster {i}: {cluster['building_count']} buildings, " +
                      f"{cluster['households']} households, " +
                      f"{cluster['avg_distance_to_facility']:.0f}m avg distance")
            
            # Verify clusters are sorted by priority
            if len(clusters) > 1:
                priorities = [c['priority_score'] for c in clusters]
                sorted_correctly = all(priorities[i] >= priorities[i+1] 
                                      for i in range(len(priorities)-1))
                if sorted_correctly:
                    print(f"   {test_color(True)} Clusters correctly sorted by priority")
                else:
                    print(f"   {test_color(False)} Clusters not sorted by priority")
                return sorted_correctly
            
            return True
        else:
            print(f"   {test_color(False)} API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return False


def main():
    """Run all Phase 3 tests"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║   PlanGram Phase 3 Validation                               ║
║   Testing Spatial Analysis Implementation                   ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    results = []
    
    # Run tests
    results.append(("Village Metrics API", test_village_metrics()))
    results.append(("Threshold Variation", test_threshold_variation()))
    results.append(("Infrastructure Analysis", test_infrastructure_analysis()))
    results.append(("Building Distances", test_building_distances()))
    results.append(("Both Villages", test_both_villages()))
    results.append(("Underserved Clusters", test_underserved_clusters()))
    
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
        print("\n✅ Phase 3 is complete and validated!")
        print("\nKey Features Working:")
        print("- Household coverage calculation")
        print("- Population metrics")
        print("- Distance analysis (Euclidean)")
        print("- Underserved area identification")
        print("- Priority assessment")
        print("- Threshold-based analysis")
        print("\nNext Steps:")
        print("1. Frontend shows metrics in UI")
        print("2. Users can adjust threshold slider")
        print("3. Coverage visualization on map")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review errors above.")
        if not results[0][1]:  # First test failed
            print("\n💡 Tip: Make sure backend is running:")
            print("   cd backend")
            print("   python -m app.main")
        return 1


if __name__ == "__main__":
    sys.exit(main())
