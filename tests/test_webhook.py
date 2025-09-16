import requests
import json

# Test if your webhook endpoint is working
test_payload = {
    "entry": [{
        "changes": [{
            "value": {
                "messages": [{
                    "from": "919876543210",
                    "id": "msg_test_001",
                    "timestamp": "1694876543",
                    "type": "text",
                    "text": {"body": "V001 buy pannanum"}
                }],
                "contacts": [{
                    "profile": {"name": "Test Customer"},
                    "wa_id": "919876543210"
                }]
            }
        }]
    }]
}

# Test via local URL first
local_url = "http://localhost:8000"

print("Testing webhook endpoint...")
try:
    response = requests.post(
        f"{local_url}/webhook/whatsapp",
        json=test_payload,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Also test health endpoint
try:
    health_response = requests.get(f"{local_url}/health", timeout=10)
    print(f"Health Check: {health_response.status_code} - {health_response.json()}")
except Exception as e:
    print(f"Health check error: {e}")
