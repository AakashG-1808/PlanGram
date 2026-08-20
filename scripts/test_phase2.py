"""
Test Phase 2 - Village + Map Implementation

This script tests:
1. Village list API
2. Village details API
3. Village layers API
4. Village bounds API
5. Layer data retrieval
"""

import requests
import sys

BASE_URL = "http://localhost:8000"


def test_color(passed: bool) -> str:
    """Return color code for test result"""
    return "✅" if passed else "❌"


def test_villages_list():
    """Test villages list endpoint"""
    print("\n1. Testing Villages List API...")
    try:
        response = requests.get(f"{BASE_URL}/api/villages", timeout=5)
        if response.status_code == 200:
            data = response.json()
            villages = data.get('villages', [])
            print(f"   {test_color(True)} Found {len(villages)} villages")
            for village in villages:
                print(f"      - {village['name']} ({village['id']})")
            return len(villages) >= 2
        else:
            print(f"   {test_color(False)} API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return False


def test_village_details():
    """Test village details endpoint"""
    print("\n2. Testing Village Details API...")
    try:
        response = requests.get(f"{BASE_URL}/api/villages/village_01", timeout=5)
        if response.status_code == 200:
            data = response.json()
            village = data.get('village', {})
            print(f"   {test_color(True)} Village details loaded")
            print(f"      Name: {village.get('name')}")
            print(f"      Population: {village.get('estimated_population')}")
            print(f"      Area: {village.get('area_sq_km')} km²")
            return True
        else:
            print(f"   {test_color(False)} API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return False


def test_village_layers():
    """Test village layers endpoint"""
    print("\n3. Testing Village Layers API...")
    try:
        response = requests.get(f"{BASE_URL}/api/villages/village_01/layers", timeout=5)
        if response.status_code == 200:
            data = response.json()
            layers = data.get('layers', {})
            print(f"   {test_color(True)} Village layers loaded")
            
            available_count = 0
            for layer_name, layer_info in layers.items():
                if layer_info.get('available'):
                    available_count += 1
                    feature_count = layer_info.get('feature_count', 0)
                    print(f"      ✓ {layer_name}: {feature_count} features")
                else:
                    print(f"      ✗ {layer_name}: not available")
            
            return available_count >= 4  # At least 4 layers should be available
        else:
            print(f"   {test_color(False)} API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return False


def test_village_bounds():
    """Test village bounds endpoint"""
    print("\n4. Testing Village Bounds API...")
    try:
        response = requests.get(f"{BASE_URL}/api/villages/village_01/bounds", timeout=5)
        if response.status_code == 200:
            data = response.json()
            bounds = data.get('bounds', {})
            center = bounds.get('center', [])
            print(f"   {test_color(True)} Village bounds calculated")
            print(f"      Center: [{center[0]:.6f}, {center[1]:.6f}]")
            print(f"      West: {bounds.get('west'):.6f}, East: {bounds.get('east'):.6f}")
            print(f"      South: {bounds.get('south'):.6f}, North: {bounds.get('north'):.6f}")
            return True
        else:
            print(f"   {test_color(False)} API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return False


def test_layer_data():
    """Test layer data retrieval"""
    print("\n5. Testing Layer Data Retrieval...")
    layers_to_test = ['boundary', 'buildings', 'facilities']
    all_passed = True
    
    for layer in layers_to_test:
        try:
            response = requests.get(
                f"{BASE_URL}/api/villages/village_01/layers/{layer}",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                feature_count = len(data.get('features', []))
                print(f"   {test_color(True)} {layer}: {feature_count} features loaded")
            else:
                print(f"   {test_color(False)} {layer}: status {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"   {test_color(False)} {layer}: {e}")
            all_passed = False
    
    return all_passed


def test_both_villages():
    """Test that both villages work"""
    print("\n6. Testing Multiple Villages...")
    villages = ['village_01', 'village_02']
    all_passed = True
    
    for village_id in villages:
        try:
            response = requests.get(
                f"{BASE_URL}/api/villages/{village_id}",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                village = data.get('village', {})
                print(f"   {test_color(True)} {village.get('name')}: accessible")
            else:
                print(f"   {test_color(False)} {village_id}: status {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"   {test_color(False)} {village_id}: {e}")
            all_passed = False
    
    return all_passed


def main():
    """Run all Phase 2 tests"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║   PlanGram Phase 2 Validation                               ║
║   Testing Village + Map Implementation                      ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    results = []
    
    # Run tests
    results.append(("Villages List API", test_villages_list()))
    results.append(("Village Details API", test_village_details()))
    results.append(("Village Layers API", test_village_layers()))
    results.append(("Village Bounds API", test_village_bounds()))
    results.append(("Layer Data Retrieval", test_layer_data()))
    results.append(("Multiple Villages", test_both_villages()))
    
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
        print("\n✅ Phase 2 backend is complete and validated!")
        print("\nNext Steps:")
        print("1. Start frontend: cd frontend && npm run dev")
        print("2. Open browser: http://localhost:5173")
        print("3. Test village selector and interactive map")
        print("4. Toggle layers and verify map updates")
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
