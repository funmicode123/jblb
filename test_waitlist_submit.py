import requests
import json

# Test the waitlist submit endpoint
test_data = {
    "username": "testuser",
    "email": "test@example.com"
}

url = "http://127.0.0.1:8000/api/waitlist/submit/"

try:
    response = requests.post(
        url,
        json=test_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
except Exception as e:
    print(f"Error: {str(e)}")