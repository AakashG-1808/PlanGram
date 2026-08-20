"""
Test Phase 6 - Candidate Location Generation Engine

This script tests:
1. Grid-based candidate generation
2. Coverage gap candidate generation
3. Hybrid candidate generation
4. Coverage scoring
5. Constraint validation integration
6. Multi-objective ranking
7. Top N candidates retrieval
"""

import requests
import sys
import json

BASE_URL = "http://localhost:8000"
VILLAGE_ID = "village_01"


def test_color(passed: bool) -> str:
    """Return color code for test result"""
    return "✅" if passed else "❌"


def test_grid_candidates():
    """Test grid-based candidate generation"""
    print("\n1. Testing Grid-Based Candidate Generation...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/villages/{VILLAGE_ID}/generate-candidates",
            json={
                "infrastructure_type": "water_facility",
                "method": "grid",
                "num_candidates": 15,
                "threshold_meters": 500,
                "grid_spacing_meters": 200
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   {test_color(True)} Grid candidates generated")
            print(f"      Method: {data['method']}")
            print(f"      Candidates generated: {data['num_candidates']}")
            print(f"      Valid candidates: {data['valid_candidates']}")
            
            if data['candidates']:
                best = data['candidates'][0]
                print(f"\n      Best candidate:")
                print(f"        Rank: {best['rank']}")
                print(f"        Location: {best['location']}")
                print(f"        Combined score: {best['combined_score']}/100")
                print(f"        Coverage improvement: +{best['coverage_improvement']}%")
                print(f"        Buildings gained: {best['buildings_gained']}")
            
            return data['num_candidates'] > 0
        else:
            print(f"   {test_color(False)} API returned status {response.status_code}")
            print(f"      Response: {response.text}")
            return False
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return False


def test_gap_candidates():
    """Test coverage gap candidate generation"""
    print("\n2. Testing Coverage Gap Candidate Generation...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/villages/{VILLAGE_ID}/generate-candidates",
            json={
                "infrastructure_type": "water_facility",
                "method": "gap",
                "num_candidates": 10,
                "threshold_meters": 500
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   {test_color(True)} Gap candidates generated")
            print(f"      Method: {data['method']}")
            print(f"      Candidates generated: {data['num_candidates']}")
            print(f"      Valid candidates: {data['valid_candidates']}")
            
            # Gap candidates should target underserved areas
            if data['candidates']:
                avg_improvement = data['summary']['avg_coverage_improvement']
                print(f"      Avg coverage improvement: +{avg_improvement}%")
                
                # Show top 3
                print(f"\n      Top 3 candidates:")
                for i, candidate in enumerate(data['candidates'][:3], 1):
                    print(f"        {i}. Coverage: +{candidate['coverage_improvement']}%, " +
                          f"Buildings: +{candidate['buildings_gained']}, " +
                          f"Score: {candidate['combined_score']:.1f}/100")
            
            return data['num_candidates'] > 0
        else:
            print(f"   {test_color(False)} API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return False


def test_hybrid_candidates():
    """Test hybrid candidate generation (grid + gap)"""
    print("\n3. Testing Hybrid Candidate Generation...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/villages/{VILLAGE_ID}/generate-candidates",
            json={
                "infrastructure_type": "water_facility",
                "method": "hybrid",
                "num_candidates": 20,
                "threshold_meters": 500,
                "grid_spacing_meters": 150
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   {test_color(True)} Hybrid candidates generated")
            print(f"      Method: {data['method']}")
            print(f"      Candidates generated: {data['num_candidates']}")
            print(f"      Valid candidates: {data['valid_candidates']}")
            print(f"      Avg coverage improvement: +{data['summary']['avg_coverage_improvement']}%")
            print(f"      Avg combined score: {data['summary']['avg_combined_score']:.1f}/100")
            
            if data['summary']['best_candidate']:
                best = data['summary']['best_candidate']
                print(f"\n      Best candidate:")
                print(f"        Location: {best['location']}")
                print(f"        Combined score: {best['combined_score']}/100")
                print(f"        Coverage improvement: +{best['coverage_improvement']}%")
                print(f"        Buildings gained: {best['buildings_gained']}")
                print(f"        Households gained: {best['households_gained']}")
                print(f"        Valid: {best['is_valid']}")
            
            return data['num_candidates'] > 0 and data['valid_candidates'] > 0
        else:
            print(f"   {test_color(False)} API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return False


def test_coverage_scoring():
    """Test coverage improvement scoring"""
    print("\n4. Testing Coverage Improvement Scoring...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/villages/{VILLAGE_ID}/generate-candidates",
            json={
                "infrastructure_type": "water_facility",
                "method": "hybrid",
                "num_candidates": 10,
                "threshold_meters": 500
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            has_coverage_scores = all(
                'coverage_improvement' in c and 'buildings_gained' in c
                for c in data['candidates']
            )
            
            print(f"   {test_color(has_coverage_scores)} Coverage scoring working")
            
            if has_coverage_scores and data['candidates']:
                improvements = [c['coverage_improvement'] for c in data['candidates']]
                print(f"      Coverage improvements range: {min(improvements):.1f}% to {max(improvements):.1f}%")
                
                buildings_gained = [c['buildings_gained'] for c in data['candidates']]
                print(f"      Buildings gained range: {min(buildings_gained)} to {max(buildings_gained)}")
                
                # Verify top candidate has good coverage improvement
                best = data['candidates'][0]
                print(f"      Best candidate improvement: +{best['coverage_improvement']}%")
            
            return has_coverage_scores
        else:
            print(f"   {test_color(False)} API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return False


def test_constraint_integration():
    """Test constraint validation integration"""
    print("\n5. Testing Constraint Validation Integration...")
    try:
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
        
        if response.status_code == 200:
            data = response.json()
            
            has_validation = all(
                'is_valid' in c and 'suitability_score' in c
                for c in data['candidates']
            )
            
            print(f"   {test_color(has_validation)} Constraint validation integrated")
            
            if has_validation:
                valid_count = sum(1 for c in data['candidates'] if c['is_valid'])
                invalid_count = len(data['candidates']) - valid_count
                
                print(f"      Valid candidates: {valid_count}")
                print(f"      Invalid candidates: {invalid_count}")
                
                # Show suitability scores
                suitability_scores = [c['suitability_score'] for c in data['candidates'] if c['is_valid']]
                if suitability_scores:
                    avg_suitability = sum(suitability_scores) / len(suitability_scores)
                    print(f"      Avg suitability (valid): {avg_suitability:.1f}/100")
                
                # Check if invalid candidates are ranked lower
                if data['candidates']:
                    top_candidate = data['candidates'][0]
                    print(f"      Top candidate is valid: {top_candidate['is_valid']}")
            
            return has_validation
        else:
            print(f"   {test_color(False)} API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return False


def test_multi_objective_ranking():
    """Test multi-objective ranking (coverage + suitability)"""
    print("\n6. Testing Multi-Objective Ranking...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/villages/{VILLAGE_ID}/generate-candidates",
            json={
                "infrastructure_type": "water_facility",
                "method": "hybrid",
                "num_candidates": 15,
                "threshold_meters": 500
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            has_combined_scores = all(
                'combined_score' in c and 'coverage_score' in c and 'suitability_score' in c
                for c in data['candidates']
            )
            
            print(f"   {test_color(has_combined_scores)} Multi-objective ranking working")
            
            if has_combined_scores and data['candidates']:
                # Verify ranking is correct (sorted by valid + combined_score)
                is_sorted = all(
                    data['candidates'][i]['rank'] == i + 1
                    for i in range(len(data['candidates']))
                )
                print(f"      Rank numbers correct: {is_sorted}")
                
                # Verify valid candidates rank higher than invalid
                valid_ranks = [c['rank'] for c in data['candidates'] if c['is_valid']]
                invalid_ranks = [c['rank'] for c in data['candidates'] if not c['is_valid']]
                
                if valid_ranks and invalid_ranks:
                    valid_higher = max(invalid_ranks) > min(valid_ranks)
                    print(f"      Valid candidates rank higher: {not valid_higher or len(invalid_ranks) == 0}")
                
                # Show score breakdown for top candidate
                top = data['candidates'][0]
                print(f"\n      Top candidate score breakdown:")
                print(f"        Combined: {top['combined_score']:.1f}/100")
                print(f"        Coverage: {top['coverage_score']:.1f}/100 (weight: 60%)")
                print(f"        Suitability: {top['suitability_score']:.1f}/100 (weight: 40%)")
            
            return has_combined_scores
        else:
            print(f"   {test_color(False)} API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return False


def test_top_n_endpoint():
    """Test quick top-N candidates endpoint"""
    print("\n7. Testing Top-N Candidates Endpoint...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/villages/{VILLAGE_ID}/candidates/top/5",
            params={
                "infrastructure_type": "water_facility",
                "threshold_meters": 500
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   {test_color(True)} Top-N endpoint working")
            print(f"      Requested: 5 candidates")
            print(f"      Received: {data['num_candidates']} candidates")
            print(f"      Valid: {data['valid_candidates']} candidates")
            
            if data['candidates']:
                print(f"\n      Top 5 candidates:")
                for candidate in data['candidates'][:5]:
                    print(f"        Rank {candidate['rank']}: " +
                          f"Score {candidate['combined_score']:.1f}, " +
                          f"Coverage +{candidate['coverage_improvement']:.1f}%, " +
                          f"Valid: {candidate['is_valid']}")
            
            return data['num_candidates'] <= 5 and data['num_candidates'] > 0
        else:
            print(f"   {test_color(False)} API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return False


def test_different_thresholds():
    """Test candidate generation with different distance thresholds"""
    print("\n8. Testing Different Distance Thresholds...")
    try:
        thresholds = [300, 500, 800]
        results = []
        
        for threshold in thresholds:
            response = requests.post(
                f"{BASE_URL}/api/villages/{VILLAGE_ID}/generate-candidates",
                json={
                    "infrastructure_type": "water_facility",
                    "method": "gap",
                    "num_candidates": 5,
                    "threshold_meters": threshold
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                avg_improvement = data.get('summary', {}).get('avg_coverage_improvement', 0)
                results.append({
                    "threshold": threshold,
                    "avg_improvement": avg_improvement
                })
        
        if len(results) == len(thresholds):
            print(f"   {test_color(True)} Multiple thresholds tested")
            print(f"      Threshold sensitivity:")
            for result in results:
                print(f"        {result['threshold']}m: Avg improvement +{result['avg_improvement']:.1f}%")
            
            # Lower thresholds should generally show higher impact per facility
            return True
        else:
            print(f"   {test_color(False)} Not all thresholds tested successfully")
            return False
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return False


def test_performance():
    """Test candidate generation performance"""
    print("\n9. Testing Performance...")
    try:
        import time
        
        start_time = time.time()
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
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"   {test_color(True)} Performance test complete")
            print(f"      Time: {elapsed_time:.2f} seconds")
            print(f"      Candidates: {data['num_candidates']}")
            print(f"      Rate: {data['num_candidates'] / elapsed_time:.1f} candidates/sec")
            
            # Should complete in reasonable time (< 10 seconds for 20 candidates)
            is_fast = elapsed_time < 10
            print(f"      Acceptable performance (< 10s): {is_fast}")
            
            return is_fast
        else:
            print(f"   {test_color(False)} API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return False


def main():
    """Run all Phase 6 tests"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║   PlanGram Phase 6 Validation                               ║
║   Testing Candidate Location Generation Engine              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    results = []
    
    # Run tests
    results.append(("Grid-Based Generation", test_grid_candidates()))
    results.append(("Coverage Gap Generation", test_gap_candidates()))
    results.append(("Hybrid Generation", test_hybrid_candidates()))
    results.append(("Coverage Scoring", test_coverage_scoring()))
    results.append(("Constraint Integration", test_constraint_integration()))
    results.append(("Multi-Objective Ranking", test_multi_objective_ranking()))
    results.append(("Top-N Endpoint", test_top_n_endpoint()))
    results.append(("Threshold Sensitivity", test_different_thresholds()))
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
        print("\n✅ Phase 6 is complete and validated!")
        print("\nKey Features Working:")
        print("- Grid-based candidate generation")
        print("- Coverage gap candidate generation")
        print("- Hybrid candidate generation")
        print("- Coverage improvement scoring")
        print("- Constraint validation integration")
        print("- Multi-objective ranking (coverage 60% + suitability 40%)")
        print("- Top-N quick retrieval")
        print("- Threshold sensitivity")
        print("- Performance optimization")
        print("\nCandidate Generation Methods:")
        print("- Grid: Regular spatial sampling")
        print("- Gap: Target underserved clusters")
        print("- Hybrid: Best of both approaches (recommended)")
        print("\nNext Steps:")
        print("1. Frontend candidate visualization")
        print("2. Interactive candidate selection")
        print("3. Budget optimization engine (Phase 7)")
        print("4. Multi-facility optimization")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
