#!/usr/bin/env python3
"""
Test script for Grocery Demand Forecasting API
Run after starting the FastAPI server with: uvicorn main:app --reload
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000"
HEALTH_CHECK_URL = f"{API_URL}/"
PREDICT_URL = f"{API_URL}/predict"

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

# Test data
test_cases = [
    {
        "name": "Test Case 1: Regular Day",
        "data": {
            "store_id_enc": 1.0,
            "item_id_enc": 5.0,
            "price": 100.0,
            "base_price": 120.0,
            "promotion": 1.0,
            "discount_pct": 15.0,
            "month": 5.0,
            "day_of_week": 2.0,
            "festival_flag": 0.0,
            "weekend": 0.0,
            "lag_1": 45.0,
            "lag_7": 50.0,
            "lag_14": 52.0,
            "rolling_mean_7": 48.0,
            "rolling_std_7": 3.0,
        }
    },
    {
        "name": "Test Case 2: Festival Day",
        "data": {
            "store_id_enc": 2.0,
            "item_id_enc": 10.0,
            "price": 80.0,
            "base_price": 100.0,
            "promotion": 2.0,
            "discount_pct": 20.0,
            "month": 10.0,
            "day_of_week": 6.0,
            "festival_flag": 1.0,
            "weekend": 1.0,
            "lag_1": 60.0,
            "lag_7": 65.0,
            "lag_14": 70.0,
            "rolling_mean_7": 65.0,
            "rolling_std_7": 5.0,
        }
    },
    {
        "name": "Test Case 3: High Promotion",
        "data": {
            "store_id_enc": 3.0,
            "item_id_enc": 8.0,
            "price": 50.0,
            "base_price": 80.0,
            "promotion": 3.0,
            "discount_pct": 37.5,
            "month": 12.0,
            "day_of_week": 1.0,
            "festival_flag": 1.0,
            "weekend": 0.0,
            "lag_1": 40.0,
            "lag_7": 42.0,
            "lag_14": 45.0,
            "rolling_mean_7": 42.0,
            "rolling_std_7": 2.0,
        }
    },
    {
        "name": "Test Case 4: Low Demand",
        "data": {
            "store_id_enc": 4.0,
            "item_id_enc": 15.0,
            "price": 150.0,
            "base_price": 150.0,
            "promotion": 0.0,
            "discount_pct": 0.0,
            "month": 2.0,
            "day_of_week": 3.0,
            "festival_flag": 0.0,
            "weekend": 0.0,
            "lag_1": 10.0,
            "lag_7": 12.0,
            "lag_14": 15.0,
            "rolling_mean_7": 12.0,
            "rolling_std_7": 2.0,
        }
    }
]


def print_header(text):
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}{text.center(60)}{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")


def print_success(text):
    print(f"{GREEN}✓ {text}{RESET}")


def print_error(text):
    print(f"{RED}✗ {text}{RESET}")


def print_warning(text):
    print(f"{YELLOW}⚠ {text}{RESET}")


def print_info(text):
    print(f"{BLUE}ℹ {text}{RESET}")


def test_health_check():
    """Test if API is running"""
    print_header("Health Check")
    
    try:
        response = requests.get(HEALTH_CHECK_URL, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"API is running: {data.get('message', 'OK')}")
            return True
        else:
            print_error(f"API returned status code {response.status_code}")
            return False
    
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to API. Make sure it's running on http://localhost:8000")
        print_info("Start the API with: uvicorn main:app --reload")
        return False
    
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        return False


def test_prediction(test_case):
    """Test prediction endpoint"""
    name = test_case["name"]
    data = test_case["data"]
    
    print(f"\n{YELLOW}{name}{RESET}")
    print(f"Input data: {json.dumps(data, indent=2)}")
    
    try:
        start_time = time.time()
        response = requests.post(PREDICT_URL, json=data, timeout=10)
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            if "error" in result:
                print_error(f"API Error: {result['error']}")
                return False
            
            predicted_demand = result.get("predicted_demand")
            store_id = result.get("store_id")
            item_id = result.get("item_id")
            status = result.get("status")
            
            print_success(f"Prediction successful (took {elapsed_time:.2f}s)")
            print(f"  Store ID: {store_id}")
            print(f"  Item ID: {item_id}")
            print(f"  Predicted Demand: {predicted_demand:.2f} units")
            print(f"  Status: {status}")
            
            return True
        
        else:
            print_error(f"API returned status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    except requests.exceptions.Timeout:
        print_error("Request timed out. API might be slow or overloaded.")
        return False
    
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        return False


def test_all():
    """Run all tests"""
    print_header("🧪 Grocery Demand Forecasting API - Test Suite")
    
    print_info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test health check
    if not test_health_check():
        print_error("API is not running. Exiting tests.")
        return
    
    time.sleep(1)
    
    # Run prediction tests
    print_header("Prediction Tests")
    
    results = []
    for i, test_case in enumerate(test_cases, 1):
        success = test_prediction(test_case)
        results.append(success)
        time.sleep(0.5)  # Small delay between requests
    
    # Summary
    print_header("📊 Test Summary")
    
    total = len(results)
    passed = sum(results)
    failed = total - passed
    
    print(f"Total Tests: {total}")
    print_success(f"Passed: {passed}")
    if failed > 0:
        print_error(f"Failed: {failed}")
    
    success_rate = (passed / total * 100) if total > 0 else 0
    
    if success_rate == 100:
        print(f"\n{GREEN}{'🎉 All tests passed! API is working correctly.' * 1}{RESET}")
    elif success_rate >= 75:
        print_warning(f"Success rate: {success_rate:.1f}% - Most tests passed, check failures above")
    else:
        print_error(f"Success rate: {success_rate:.1f}% - Multiple failures detected")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


if __name__ == "__main__":
    try:
        test_all()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Tests interrupted by user{RESET}")
    except Exception as e:
        print_error(f"Fatal error: {str(e)}")