import requests

def test_api():
    base_url = "http://127.0.0.1:8000"
    
    print("Testing API endpoints...")
    
    # Test 1: Get all features
    print("\nTest 1: Getting all features")
    response = requests.get(f"{base_url}/features")
    if response.status_code == 200:
        features = response.json()
        print(f"Success! Found {len(features)} features")
        if len(features) > 0:
            print(f"Sample feature: {features[0]['name']}")
    else:
        print(f"Error: {response.status_code}")
    
    # Test 2: Get first feature
    print("\nTest 2: Getting feature with ID 1")
    response = requests.get(f"{base_url}/feature/1")
    if response.status_code == 200:
        feature = response.json()
        print(f"Success! Feature name: {feature['name']}")
    else:
        print(f"Error: {response.status_code}")
    
    # Test 3: Check API documentation
    print("\nTest 3: Checking API documentation")
    response = requests.get(f"{base_url}/openapi.json")
    if response.status_code == 200:
        print("Success! API documentation is available")
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    test_api()
