import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = "http://localhost:5000"
API_KEY = os.getenv('API_KEY', 'your-secret-api-key')

def test_health_check():
    """Test the health check endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health Check - Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_scrape_basic():
    """Test basic scraping functionality"""
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
    }
    
    data = {
        'links': ['https://httpbin.org/html'],
        'raw': False,
        'summarize': False
    }
    
    response = requests.post(f"{BASE_URL}/scrape", headers=headers, json=data)
    print(f"\nBasic Scrape - Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_scrape_raw():
    """Test raw HTML scraping"""
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
    }
    
    data = {
        'links': ['https://httpbin.org/html'],
        'raw': True
    }
    
    response = requests.post(f"{BASE_URL}/scrape", headers=headers, json=data)
    print(f"\nRaw Scrape - Status: {response.status_code}")
    result = response.json()
    if 'results' in result and len(result['results']) > 0:
        print(f"Content length: {len(result['results'][0].get('content', ''))}")
    return response.status_code == 200

def test_scrape_multiple():
    """Test multiple URL scraping"""
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
    }
    
    data = {
        'links': [
            'https://httpbin.org/html',
            'https://httpbin.org/json',
            'https://httpbin.org/status/404'  # This should fail
        ],
        'raw': False
    }
    
    response = requests.post(f"{BASE_URL}/scrape", headers=headers, json=data)
    print(f"\nMultiple URLs - Status: {response.status_code}")
    result = response.json()
    print(f"Total processed: {result.get('total_processed')}")
    print(f"Successful: {result.get('successful')}")
    print(f"Failed: {result.get('failed')}")
    return response.status_code == 200

def test_auth_failure():
    """Test authentication failure"""
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': 'wrong-key'
    }
    
    data = {
        'links': ['https://httpbin.org/html']
    }
    
    response = requests.post(f"{BASE_URL}/scrape", headers=headers, json=data)
    print(f"\nAuth Failure Test - Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 401

if __name__ == "__main__":
    print("Testing Web Scraper API...")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_check),
        ("Basic Scraping", test_scrape_basic),
        ("Raw HTML Scraping", test_scrape_raw),
        ("Multiple URLs", test_scrape_multiple),
        ("Authentication Failure", test_auth_failure)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"✅ {test_name} - PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {str(e)}")
    
    print("=" * 50)
    print(f"Tests completed: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the server logs.")
