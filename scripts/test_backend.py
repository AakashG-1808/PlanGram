"""
Test Backend Connectivity and Phase 1 Setup

This script tests:
1. Backend server is running
2. API endpoints respond correctly
3. Village registry is accessible
4. Generated data files exist
"""

import requests
import json
from pathlib import Path
import sys

BASE_URL = "http://localhost:8000"
DATA_DIR = Path("data")


def test_color(passed: bool) -> str:
    """Return color code for test result"""
    return "✅" if passed else "❌"


def test_backend_health():
    """Test backend health endpoint"""
    print("\n1. Testing Backend Health...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   {test_color(True)} Backend is healthy")
            print(f"      Status: {data.get('status')}")
            print(f"      Data Mode: {data.get('data_mode')}")
            print(f"      AI Provider: {data.get('ai_provider')}")
            return True
        else:
            print(f"   {test_color(False)} Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"   {test_color(False)} Cannot connect to backend at {BASE_URL}")
        print(f"      Make sure backend is running: cd backend && uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return False


def test_config_endpoint():
    """Test config endpoint"""
    print("\n2. Testing Config Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/config", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   {test_color(True)} Config endpoint working")
            print(f"      Data Mode: {data.get('data_mode')}")
            print(f"      Distance Threshold: {data.get('distance_threshold_meters')}m")
            print(f"      Supported Infrastructure: {', '.join(data.get('supported_infrastructure_types', []))}")
            return True
        else:
            print(f"   {test_color(False)} Config returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return False


def test_village_registry():
    """Test village registry file"""
    print("\n3. Testing Village Registry...")
    registry_path = DATA_DIR / "village_registry.json"
    
    if not registry_path.exists():
        print(f"   {test_color(False)} Village registry not found at {registry_path}")
        return False
    
    try:
        with open(registry_path) as f:
            villages = json.load(f)
        
        print(f"   {test_color(True)} Village registry loaded")
        print(f"      Villages: {len(villages)}")
        
        for village in villages:
            print(f"      - {village['name']} ({village['id']})")
            print(f"        Taluk: {village['taluk']}, District: {village['district']}")
            print(f"        Population: {village.get('estimated_population', 'N/A')}")
        
        return len(villages) == 2
    except Exception as e:
        print(f"   {test_color(False)} Error reading registry: {e}")
        return False


def test_village_data_files():
    """Test that generated village data files exist"""
    print("\n4. Testing Village Data Files...")
    
    required_files = [
        "boundary.geojson",
        "buildings.geojson",
        "parcels.geojson",
        "roads.geojson",
        "water_bodies.geojson",
        "facilities.geojson",
        "households.csv"
    ]
    
    villages = ["village_01", "village_02"]
    all_passed = True
    
    for village_id in villages:
        print(f"\n   Testing {village_id}:")
        village_dir = DATA_DIR / "villages" / village_id
        
        if not village_dir.exists():
            print(f"      {test_color(False)} Village directory not found")
            all_passed = False
            continue
        
        village_passed = True
        for filename in required_files:
            filepath = village_dir / filename
            exists = filepath.exists()
            
            if exists:
                # Check file size
                size = filepath.stat().st_size
                print(f"      {test_color(True)} {filename} ({size} bytes)")
            else:
                print(f"      {test_color(False)} {filename} missing")
                village_passed = False
        
        if village_passed:
            # Try to load and count features
            try:
                with open(village_dir / "buildings.geojson") as f:
                    buildings = json.load(f)
                    print(f"      📊 {len(buildings['features'])} buildings")
                
                with open(village_dir / "facilities.geojson") as f:
                    facilities = json.load(f)
                    print(f"      📊 {len(facilities['features'])} facilities")
                
                import csv
                with open(village_dir / "households.csv") as f:
                    households = list(csv.DictReader(f))
                    total_pop = sum(int(h['estimated_population']) for h in households)
                    print(f"      📊 {len(households)} households, {total_pop} population")
            except Exception as e:
                print(f"      ⚠️  Could not parse data files: {e}")
        
        all_passed = all_passed and village_passed
    
    return all_passed


def test_source_metadata():
    """Test source metadata file"""
    print("\n5. Testing Source Metadata...")
    metadata_path = DATA_DIR / "source_metadata.json"
    
    if not metadata_path.exists():
        print(f"   {test_color(False)} Source metadata not found")
        return False
    
    try:
        with open(metadata_path) as f:
            metadata = json.load(f)
        
        print(f"   {test_color(True)} Source metadata loaded")
        print(f"      Version: {metadata.get('metadata_version')}")
        print(f"      Source Types: {len(metadata.get('source_types', {}))}")
        print(f"      Datasets: {len(metadata.get('datasets', {}))}")
        
        # Check source types
        source_types = metadata.get('source_types', {})
        required_types = ['REAL_OFFICIAL', 'OPEN_PUBLIC', 'ESTIMATED', 'SYNTHETIC']
        for st in required_types:
            exists = st in source_types
            print(f"      {test_color(exists)} {st}")
        
        return True
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return False


def test_cost_config():
    """Test cost configuration file"""
    print("\n6. Testing Cost Configuration...")
    cost_path = DATA_DIR / "cost_config.json"
    
    if not cost_path.exists():
        print(f"   {test_color(False)} Cost config not found")
        return False
    
    try:
        with open(cost_path) as f:
            config = json.load(f)
        
        print(f"   {test_color(True)} Cost config loaded")
        print(f"      Currency: {config.get('currency')}")
        
        infra_costs = config.get('infrastructure_costs', {})
        print(f"      Infrastructure types: {len(infra_costs)}")
        
        for infra_type, details in infra_costs.items():
            print(f"      - {infra_type}: ₹{details.get('base_cost', 0):,}")
        
        return True
    except Exception as e:
        print(f"   {test_color(False)} Error: {e}")
        return False


def main():
    """Run all tests"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║   PlanGram Phase 1 Validation                               ║
║   Testing Backend Setup and Data Generation                 ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    results = []
    
    # Run tests
    results.append(("Backend Health", test_backend_health()))
    results.append(("Config Endpoint", test_config_endpoint()))
    results.append(("Village Registry", test_village_registry()))
    results.append(("Village Data Files", test_village_data_files()))
    results.append(("Source Metadata", test_source_metadata()))
    results.append(("Cost Configuration", test_cost_config()))
    
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
        print("\n✅ Phase 1 setup is complete and validated!")
        print("\nNext Steps:")
        print("1. Check README.md for architecture overview")
        print("2. Review docs/ for detailed documentation")
        print("3. Ready to start Phase 2 (Village + Map)")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review errors above.")
        if not results[0][1]:  # Backend health failed
            print("\n💡 Tip: Make sure backend is running:")
            print("   cd backend")
            print("   python -m venv venv")
            print("   venv\\Scripts\\activate  # Windows")
            print("   pip install -r requirements.txt")
            print("   python -m app.main")
        return 1


if __name__ == "__main__":
    sys.exit(main())
