"""
Test Phase 4 - Scenario Builder Implementation

This script tests:
1. Create scenario
2. Add project to scenario
3. Move project location
4. Delete project
5. Simulate scenario (before/after metrics)
6. Compare scenarios
7. Delete scenario
"""

import requests
import sys
import json

BASE_URL = "http://localhost:8000"


def test_color(passed: bool) -> str:
    """Return color code for test result"""
    return "✅" if passed else "❌"


def test_create_scenario():
    """Test creating a new scenario"""
    print("\n1. Testing Scenario Creation...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/scenarios",
            json={
                "name": "Test Water Improvement",
                "village_id": "village_01",
                "description": "Testing scenario creation"
            },
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   {test_color(True)} Scenario created successfully")
            print(f"      ID: {data['scenario_id']}")
            print(f"      Name: {data['name']}")
            print(f"      Projects: {len(data['projects'])}")
            print(f"      Total cost: ₹{data['total_cost']:,.0f}")
            return data['scenario_id']
        else:
            print(f"   {test_color(False)} API returned status {response.status_code}")
            print(f"      Response: {response.text}")
            return None
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return None


def test_add_project(scenario_id: str):
    """Test adding a project to scenario"""
    print("\n2. Testing Add Project...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/scenarios/{scenario_id}/projects",
            json={
                "infrastructure_type": "water_facility",
                "location": [77.686, 12.698],
                "name": "New Water Point - Northwest"
            },
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   {test_color(True)} Project added successfully")
            print(f"      Projects in scenario: {len(data['projects'])}")
            print(f"      Total cost: ₹{data['total_cost']:,.0f}")
            
            if data['projects']:
                project = data['projects'][0]
                print(f"      Project ID: {project['project_id']}")
                print(f"      Type: {project['infrastructure_type']}")
                print(f"      Cost: ₹{project['cost']:,.0f}")
                return project['project_id']
            return None
        else:
            print(f"   {test_color(False)} API returned status {response.status_code}")
            return None
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return None


def test_move_project(scenario_id: str, project_id: str):
    """Test moving a project location"""
    print("\n3. Testing Move Project...")
    try:
        new_location = [77.688, 12.699]
        response = requests.put(
            f"{BASE_URL}/api/scenarios/{scenario_id}/projects/{project_id}",
            json=new_location,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            project = next((p for p in data['projects'] if p['project_id'] == project_id), None)
            if project:
                print(f"   {test_color(True)} Project location updated")
                print(f"      New location: {project['location']}")
                return True
            else:
                print(f"   {test_color(False)} Project not found in response")
                return False
        else:
            print(f"   {test_color(False)} API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return False


def test_simulate_scenario(scenario_id: str):
    """Test scenario simulation"""
    print("\n4. Testing Scenario Simulation...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/scenarios/{scenario_id}/simulate",
            params={"threshold": 500},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   {test_color(True)} Simulation completed successfully")
            
            before = data['before_coverage']
            after = data['after_coverage']
            improvement = data['improvement']
            
            print(f"\n      BEFORE:")
            print(f"        Coverage: {before['coverage_percentage']:.1f}%")
            print(f"        Served: {before['served_households']} households")
            
            print(f"\n      AFTER:")
            print(f"        Coverage: {after['coverage_percentage']:.1f}%")
            print(f"        Served: {after['served_households']} households")
            
            print(f"\n      IMPROVEMENT:")
            print(f"        Coverage gain: +{improvement['coverage_change']:.1f}%")
            print(f"        Households gained: +{improvement['households_gained']}")
            print(f"        Population gained: +{improvement['population_gained']}")
            
            print(f"\n      COST: ₹{data['total_cost']:,.0f}")
            
            return improvement['households_gained'] > 0
        else:
            print(f"   {test_color(False)} API returned status {response.status_code}")
            print(f"      Response: {response.text}")
            return False
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return False


def test_multiple_projects(scenario_id: str):
    """Test adding multiple projects"""
    print("\n5. Testing Multiple Projects...")
    try:
        locations = [
            [77.690, 12.700],
            [77.685, 12.696]
        ]
        
        for i, location in enumerate(locations, 2):
            response = requests.post(
                f"{BASE_URL}/api/scenarios/{scenario_id}/projects",
                json={
                    "infrastructure_type": "water_facility",
                    "location": location,
                    "name": f"Water Point #{i}"
                },
                timeout=10
            )
            if response.status_code != 200:
                print(f"   {test_color(False)} Failed to add project {i}")
                return False
        
        # Get scenario to verify
        response = requests.get(f"{BASE_URL}/api/scenarios/{scenario_id}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   {test_color(True)} Multiple projects added")
            print(f"      Total projects: {len(data['projects'])}")
            print(f"      Total cost: ₹{data['total_cost']:,.0f}")
            return len(data['projects']) == 3
        
        return False
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return False


def test_compare_scenarios():
    """Test comparing multiple scenarios"""
    print("\n6. Testing Scenario Comparison...")
    try:
        # Create two scenarios with different configurations
        scenarios = []
        
        # Scenario 1: Single facility
        resp1 = requests.post(
            f"{BASE_URL}/api/scenarios",
            json={
                "name": "Scenario A - Single Facility",
                "village_id": "village_01",
                "description": "One water facility"
            }
        )
        if resp1.status_code == 200:
            scen1 = resp1.json()
            scenarios.append(scen1['scenario_id'])
            
            # Add one project
            requests.post(
                f"{BASE_URL}/api/scenarios/{scen1['scenario_id']}/projects",
                json={
                    "infrastructure_type": "water_facility",
                    "location": [77.686, 12.698]
                }
            )
        
        # Scenario 2: Two facilities
        resp2 = requests.post(
            f"{BASE_URL}/api/scenarios",
            json={
                "name": "Scenario B - Two Facilities",
                "village_id": "village_01",
                "description": "Two water facilities"
            }
        )
        if resp2.status_code == 200:
            scen2 = resp2.json()
            scenarios.append(scen2['scenario_id'])
            
            # Add two projects
            for loc in [[77.686, 12.698], [77.690, 12.700]]:
                requests.post(
                    f"{BASE_URL}/api/scenarios/{scen2['scenario_id']}/projects",
                    json={
                        "infrastructure_type": "water_facility",
                        "location": loc
                    }
                )
        
        if len(scenarios) < 2:
            print(f"   {test_color(False)} Failed to create comparison scenarios")
            return False
        
        # Compare scenarios
        response = requests.post(
            f"{BASE_URL}/api/scenarios/compare",
            json=scenarios,
            params={"threshold": 500},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   {test_color(True)} Scenarios compared successfully")
            print(f"      Scenarios compared: {len(data['scenarios'])}")
            print(f"      Best coverage: {data['best_coverage_id'][:8]}...")
            print(f"      Best cost efficiency: {data['best_cost_efficiency_id'][:8]}...")
            
            for sim in data['scenarios']:
                print(f"\n      Scenario {sim['scenario_id'][:8]}:")
                print(f"        Projects: {sim['num_projects']}")
                print(f"        Coverage: {sim['after_coverage']['coverage_percentage']:.1f}%")
                print(f"        Cost: ₹{sim['total_cost']:,.0f}")
            
            return True
        else:
            print(f"   {test_color(False)} Comparison failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return False


def test_delete_project(scenario_id: str, project_id: str):
    """Test deleting a project"""
    print("\n7. Testing Delete Project...")
    try:
        response = requests.delete(
            f"{BASE_URL}/api/scenarios/{scenario_id}/projects/{project_id}",
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   {test_color(True)} Project deleted successfully")
            print(f"      Remaining projects: {len(data['projects'])}")
            print(f"      Updated cost: ₹{data['total_cost']:,.0f}")
            return True
        else:
            print(f"   {test_color(False)} API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return False


def cleanup_scenarios():
    """Clean up test scenarios"""
    try:
        response = requests.get(f"{BASE_URL}/api/scenarios", timeout=10)
        if response.status_code == 200:
            scenarios = response.json()
            for scenario in scenarios:
                requests.delete(f"{BASE_URL}/api/scenarios/{scenario['scenario_id']}")
    except:
        pass


def main():
    """Run all Phase 4 tests"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║   PlanGram Phase 4 Validation                               ║
║   Testing Scenario Builder Implementation                   ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Clean up any existing test scenarios
    cleanup_scenarios()
    
    results = []
    scenario_id = None
    project_id = None
    
    # Run tests
    scenario_id = test_create_scenario()
    results.append(("Scenario Creation", scenario_id is not None))
    
    if scenario_id:
        project_id = test_add_project(scenario_id)
        results.append(("Add Project", project_id is not None))
        
        if project_id:
            move_result = test_move_project(scenario_id, project_id)
            results.append(("Move Project", move_result))
        else:
            results.append(("Move Project", False))
        
        sim_result = test_simulate_scenario(scenario_id)
        results.append(("Scenario Simulation", sim_result))
        
        multi_result = test_multiple_projects(scenario_id)
        results.append(("Multiple Projects", multi_result))
        
        if project_id:
            delete_result = test_delete_project(scenario_id, project_id)
            results.append(("Delete Project", delete_result))
        else:
            results.append(("Delete Project", False))
    else:
        results.append(("Add Project", False))
        results.append(("Move Project", False))
        results.append(("Scenario Simulation", False))
        results.append(("Multiple Projects", False))
        results.append(("Delete Project", False))
    
    compare_result = test_compare_scenarios()
    results.append(("Scenario Comparison", compare_result))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        print(f"{test_color(result)} {test_name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    # Cleanup
    cleanup_scenarios()
    
    if passed == total:
        print("\n✅ Phase 4 is complete and validated!")
        print("\nKey Features Working:")
        print("- Create scenarios")
        print("- Add/move/delete projects")
        print("- Live simulation with before/after metrics")
        print("- Cost tracking")
        print("- Scenario comparison")
        print("\nNext Steps:")
        print("1. Frontend scenario builder UI")
        print("2. Interactive map placement")
        print("3. Visual before/after comparison")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
