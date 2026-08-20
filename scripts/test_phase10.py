"""
Test Phase 10: AI Integration
Tests natural language queries, explanations, and insights generation
"""

import requests
import json
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://localhost:8000/api"

def print_section(title):
    """Print section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)

def print_result(test_name, passed, details=""):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"\n{status}: {test_name}")
    if details:
        print(f"  {details}")

def test_ai_health():
    """Test AI service health check"""
    print_section("Test 1: AI Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/ai/health")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert 'ai_enabled' in data
        assert 'provider' in data
        assert 'features' in data
        
        print_result(
            "AI Health Check",
            True,
            f"Provider: {data['provider']}, Enabled: {data['ai_enabled']}, " +
            f"Fallback: {data['fallback_mode']}"
        )
        return data
        
    except Exception as e:
        print_result("AI Health Check", False, str(e))
        return None

def test_intent_parsing():
    """Test natural language query parsing"""
    print_section("Test 2: Intent Parsing")
    
    queries = [
        {
            'query': 'Find best water facility location in village_01 with budget 200000',
            'expected_action': 'optimize',
            'expected_params': {'village_id': 'village_01', 'infrastructure_type': 'water', 'budget': 200000}
        },
        {
            'query': 'Analyze coverage in village_02',
            'expected_action': 'analyze',
            'expected_params': {'village_id': 'village_02'}
        },
        {
            'query': 'Generate 20 candidates for water using hybrid method in village_01',
            'expected_action': 'generate_candidates',
            'expected_params': {'village_id': 'village_01', 'infrastructure_type': 'water', 'method': 'hybrid'}
        },
    ]
    
    passed_count = 0
    
    for test_query in queries:
        try:
            response = requests.post(
                f"{BASE_URL}/ai/query",
                json={'query': test_query['query']}
            )
            assert response.status_code == 200
            
            data = response.json()
            intent = data.get('intent', {})
            
            # Check action
            action_match = intent.get('action') == test_query['expected_action']
            
            # Check parameters
            param_match = True
            for key, expected_value in test_query['expected_params'].items():
                if intent.get(key) != expected_value:
                    param_match = False
                    break
            
            passed = action_match and param_match
            
            print_result(
                f"Query: '{test_query['query'][:50]}...'",
                passed,
                f"Action: {intent.get('action')}, Params: {list(test_query['expected_params'].keys())}"
            )
            
            if passed:
                passed_count += 1
                
        except Exception as e:
            print_result(f"Query parsing", False, str(e))
    
    return passed_count == len(queries)

def test_explanation_generation():
    """Test recommendation explanation generation"""
    print_section("Test 3: Explanation Generation")
    
    # Sample location and context
    request_data = {
        'location': {
            'lat': 12.699,
            'lng': 77.688,
            'score': 97.5
        },
        'context': {
            'village_id': 'village_01',
            'buildings_served': 92,
            'coverage_improvement': 35.5,
            'current_coverage': 59.3,
            'cost': 180000,
            'cost_per_building': 1957,
            'constraints': {
                'boundary': 'valid',
                'land_type': 'public',
                'water_distance': 45,
                'road_distance': 50
            }
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/ai/explain",
            json=request_data
        )
        assert response.status_code == 200
        
        data = response.json()
        
        # Check required fields
        assert 'summary' in data
        assert 'full_explanation' in data
        assert 'factors' in data
        assert 'warnings' in data
        
        # Check summary is meaningful
        assert len(data['summary']) > 50
        
        # Check factors are present
        assert len(data['factors']) > 0
        
        # Check factors have required structure
        for factor in data['factors']:
            assert 'name' in factor
            assert 'score' in factor
            assert 'weight' in factor
            assert 'description' in factor
        
        print_result(
            "Explanation Generation",
            True,
            f"Summary length: {len(data['summary'])} chars, " +
            f"Factors: {len(data['factors'])}, Warnings: {len(data['warnings'])}"
        )
        
        # Print sample of explanation
        print("\n  Sample explanation:")
        print(f"  {data['summary'][:150]}...")
        
        return True
        
    except Exception as e:
        print_result("Explanation Generation", False, str(e))
        return False

def test_insights_generation():
    """Test insights generation from analysis"""
    print_section("Test 4: Insights Generation")
    
    # Sample analysis results
    request_data = {
        'village_id': 'village_01',
        'analysis_results': {
            'coverage_percent': 59.3,
            'total_buildings': 259,
            'served_buildings': 154,
            'clusters': [
                {'building_count': 78, 'priority': 'HIGH'},
                {'building_count': 32, 'priority': 'MEDIUM'},
                {'building_count': 15, 'priority': 'MEDIUM'}
            ],
            'high_priority_count': 1,
            'medium_priority_count': 2
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/ai/insights",
            json=request_data
        )
        assert response.status_code == 200
        
        data = response.json()
        insights = data.get('insights', [])
        
        # Check insights were generated
        assert len(insights) > 0, "No insights generated"
        
        # Check each insight has required fields
        for insight in insights:
            assert 'type' in insight
            assert 'title' in insight
            assert 'description' in insight
            assert 'action' in insight
            assert 'impact' in insight
            
            # Check type is valid
            assert insight['type'] in ['critical', 'opportunity', 'warning']
        
        # Count by type
        critical = len([i for i in insights if i['type'] == 'critical'])
        opportunities = len([i for i in insights if i['type'] == 'opportunity'])
        warnings = len([i for i in insights if i['type'] == 'warning'])
        
        print_result(
            "Insights Generation",
            True,
            f"Generated {len(insights)} insights: " +
            f"{critical} critical, {opportunities} opportunities, {warnings} warnings"
        )
        
        # Print first insight
        if insights:
            print(f"\n  Sample insight ({insights[0]['type']}):")
            print(f"  Title: {insights[0]['title']}")
            print(f"  Action: {insights[0]['action']}")
        
        return True
        
    except Exception as e:
        print_result("Insights Generation", False, str(e))
        return False

def test_error_handling():
    """Test error handling for invalid inputs"""
    print_section("Test 5: Error Handling")
    
    tests = [
        {
            'name': 'Empty query',
            'endpoint': '/ai/query',
            'data': {'query': ''},
            'expect_error': True
        },
        {
            'name': 'Missing location in explain',
            'endpoint': '/ai/explain',
            'data': {'context': {}},
            'expect_error': True
        },
        {
            'name': 'Invalid village_id in insights',
            'endpoint': '/ai/insights',
            'data': {'village_id': '', 'analysis_results': {}},
            'expect_error': True
        }
    ]
    
    passed_count = 0
    
    for test in tests:
        try:
            response = requests.post(
                f"{BASE_URL}{test['endpoint']}",
                json=test['data']
            )
            
            # Should get error response
            error_occurred = response.status_code >= 400
            
            passed = error_occurred == test['expect_error']
            
            print_result(
                test['name'],
                passed,
                f"Status: {response.status_code}"
            )
            
            if passed:
                passed_count += 1
                
        except Exception as e:
            print_result(test['name'], False, str(e))
    
    return passed_count == len(tests)

def test_integration_workflow():
    """Test complete AI workflow"""
    print_section("Test 6: Integration Workflow")
    
    try:
        # Step 1: Parse query
        print("\n  Step 1: Parse natural language query")
        query_response = requests.post(
            f"{BASE_URL}/ai/query",
            json={'query': 'optimize water for village_01 with budget 300000'}
        )
        assert query_response.status_code == 200
        intent = query_response.json().get('intent', {})
        assert intent['action'] == 'optimize'
        print("  ✓ Query parsed successfully")
        
        # Step 2: Get analysis data (simulated)
        print("\n  Step 2: Simulate analysis results")
        analysis_results = {
            'coverage_percent': 59.3,
            'total_buildings': 259,
            'served_buildings': 154,
            'clusters': [{'building_count': 78, 'priority': 'HIGH'}],
            'high_priority_count': 1
        }
        
        # Step 3: Generate insights
        print("\n  Step 3: Generate insights from analysis")
        insights_response = requests.post(
            f"{BASE_URL}/ai/insights",
            json={
                'village_id': 'village_01',
                'analysis_results': analysis_results
            }
        )
        assert insights_response.status_code == 200
        insights = insights_response.json().get('insights', [])
        assert len(insights) > 0
        print(f"  ✓ Generated {len(insights)} insights")
        
        # Step 4: Explain recommendation
        print("\n  Step 4: Explain recommendation")
        explain_response = requests.post(
            f"{BASE_URL}/ai/explain",
            json={
                'location': {'lat': 12.699, 'lng': 77.688, 'score': 95.0},
                'context': {
                    'village_id': 'village_01',
                    'buildings_served': 85,
                    'coverage_improvement': 32.8,
                    'current_coverage': 59.3,
                    'cost': 180000,
                    'cost_per_building': 2118,
                    'constraints': {
                        'boundary': 'valid',
                        'land_type': 'public',
                        'water_distance': 55,
                        'road_distance': 45
                    }
                }
            }
        )
        assert explain_response.status_code == 200
        explanation = explain_response.json()
        assert 'summary' in explanation
        print(f"  ✓ Explanation generated ({len(explanation['summary'])} chars)")
        
        print_result("Integration Workflow", True, "All steps completed successfully")
        return True
        
    except Exception as e:
        print_result("Integration Workflow", False, str(e))
        return False

def main():
    """Run all Phase 10 tests"""
    print("\n" + "="*70)
    print("  PHASE 10: AI INTEGRATION - TEST SUITE")
    print("="*70)
    
    results = {}
    
    # Test 1: AI Health
    ai_health = test_ai_health()
    results['health'] = ai_health is not None
    
    # Test 2: Intent Parsing
    results['intent_parsing'] = test_intent_parsing()
    
    # Test 3: Explanation Generation
    results['explanation'] = test_explanation_generation()
    
    # Test 4: Insights Generation
    results['insights'] = test_insights_generation()
    
    # Test 5: Error Handling
    results['error_handling'] = test_error_handling()
    
    # Test 6: Integration Workflow
    results['integration'] = test_integration_workflow()
    
    # Summary
    print_section("TEST SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n{'='*70}")
    print(f"  RESULTS: {passed}/{total} tests passed")
    
    if ai_health and not ai_health['api_key_configured']:
        print("\n  ⚠️  NOTE: AI provider API key not configured")
        print("  Tests ran with regex fallback mode")
        print("  Configure GEMINI_API_KEY in .env for full AI features")
    
    print('='*70)
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        sys.exit(1)
