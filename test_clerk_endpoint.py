import requests
import json

# Test data with valid clerk_user_id and empty referral code
test_data = {
    "clerk_user_id": "user_clerk_id_from_frontend_3",
    "email": "user4@example.com",
    "username": "username4",
    "provider": "google",
    "referral_code": ""  # Empty referral code
}

# Make the request to your endpoint
url = "http://127.0.0.1:8000/api/waitlist/clerk-auth/"

try:
    response = requests.post(
        url,
        json=test_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
except Exception as e:
    print(f"Error: {str(e)}")