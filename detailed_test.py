import requests
import json

# Test the exact same request that would fail in Postman
test_cases = [
    {
        "name": "Original failing request",
        "data": {
            "clerk_user_id": "user_clerk_id_from_frontend",
            "email": "user2@example.com", 
            "username": "username2",
            "provider": "google",
            "referral_code": "ABC123XYZ"
        }
    },
    {
        "name": "With empty referral code",
        "data": {
            "clerk_user_id": "user_clerk_id_from_frontend_new",
            "email": "user5@example.com",
            "username": "username5", 
            "provider": "google",
            "referral_code": ""
        }
    }
]

url = "http://127.0.0.1:8000/api/waitlist/clerk-auth/"

for test_case in test_cases:
    print(f"\n=== Testing: {test_case['name']} ===")
    print(f"Request data: {json.dumps(test_case['data'], indent=2)}")
    
    try:
        response = requests.post(
            url,
            json=test_case['data'],
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200 or response.status_code == 201:
            print("✅ SUCCESS")
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
        else:
            print("❌ FAILED")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {str(e)}")