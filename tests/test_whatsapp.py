import requests
import json

# Test WhatsApp message simulation
test_payload = {
    "entry": [{
        "changes": [{
            "value": {
                "messages": [{
                    "from": "919876543210",
                    "id": "msg_001", 
                    "timestamp": "1694876543",
                    "type": "text",
                    "text": {"body": "V001 buy pannanum"}
                }],
                "contacts": [{
                    "profile": {"name": "Test Customer"}
                }]
            }
        }]
    }]
}

# Send to test endpoint
response = requests.post(
    "http://localhost:8000/test/message",
    json=test_payload
)

print("Response:", response.json())
