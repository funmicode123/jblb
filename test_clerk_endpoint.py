import requests
import json

# Test data with valid clerk_user_id and empty referral code
test_data = {
    "clerk_user_id": "user_clerk_id_from_frontend_email_test",
    "email": "emailtest@example.com",
    "username": "emailtestuser",
    "first_name": "Email",
    "last_name": "Tester",
    "provider": "google",
    "referral_code": ""
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
    response_json = response.json()
    print(f"Response: {json.dumps(response_json, indent=2)}")
    
    # Check if email was sent
    if response.status_code == 201 and response_json.get('email_sent'):
        print("\n✅ Email notification sent successfully!")
    else:
        print("\n⚠️  Email notification may not have been sent")
        
except Exception as e:
    print(f"Error: {str(e)}")