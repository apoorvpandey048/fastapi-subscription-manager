# Test Script for FastAPI Subscription Manager
# Run this script to verify all endpoints are working

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8080"

def print_response(title, response):
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def test_api():
    print("\n🚀 Starting API Tests...\n")
    
    # Test 1: Create a subscription
    print("\n📝 TEST 1: Create Subscription")
    start_date = datetime.now()
    end_date = start_date + timedelta(days=30)
    
    create_data = {
        "user_email": "test@example.com",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }
    
    response = requests.post(f"{BASE_URL}/subscriptions/", json=create_data)
    print_response("Create Subscription", response)
    
    if response.status_code == 201:
        subscription_id = response.json()["id"]
        print(f"\n✅ Subscription created with ID: {subscription_id}")
        
        # Test 2: Get subscription
        print("\n📖 TEST 2: Get Subscription")
        response = requests.get(f"{BASE_URL}/subscriptions/{subscription_id}")
        print_response("Get Subscription", response)
        
        # Test 3: Renew subscription
        print("\n🔄 TEST 3: Renew Subscription")
        new_end_date = end_date + timedelta(days=30)
        renew_data = {
            "end_date": new_end_date.isoformat()
        }
        response = requests.put(f"{BASE_URL}/subscriptions/{subscription_id}/renew", json=renew_data)
        print_response("Renew Subscription", response)
        
        # Test 4: Get subscription again to verify renewal
        print("\n📖 TEST 4: Verify Renewal")
        response = requests.get(f"{BASE_URL}/subscriptions/{subscription_id}")
        print_response("Get Updated Subscription", response)
        
        # Test 5: Delete subscription
        print("\n🗑️  TEST 5: Delete Subscription")
        response = requests.delete(f"{BASE_URL}/subscriptions/{subscription_id}")
        print_response("Delete Subscription", response)
        
        # Test 6: Verify deletion
        print("\n🔍 TEST 6: Verify Deletion (Should return 404)")
        response = requests.get(f"{BASE_URL}/subscriptions/{subscription_id}")
        print_response("Get Deleted Subscription", response)
        
    else:
        print("\n❌ Failed to create subscription. Cannot proceed with other tests.")
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        # Test if server is running
        response = requests.get(f"{BASE_URL}/docs")
        print("✅ Server is running!")
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to server. Make sure the server is running at http://127.0.0.1:8080")
    except Exception as e:
        print(f"❌ Error: {e}")
