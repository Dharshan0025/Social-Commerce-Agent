import requests
import json

# Replace with your current ngrok URL
ngrok_url = input("Enter your current ngrok URL (e.g., https://abc123.ngrok-free.app): ").strip()

print(f"\n🔍 Testing {ngrok_url}")

# Test 1: Health check
print("\n1. Testing health endpoint...")
try:
    health = requests.get(f"{ngrok_url}/health", timeout=10)
    print(f"   ✅ Health: {health.status_code} - {health.json()}")
except Exception as e:
    print(f"   ❌ Health failed: {e}")
    exit()

# Test 2: Webhook verification (GET request)
print("\n2. Testing webhook verification...")
try:
    verify = requests.get(
        f"{ngrok_url}/webhook/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.challenge": "12345",
            "hub.verify_token": "mytoken"
        },
        timeout=10
    )
    print(f"   ✅ Verification: {verify.status_code} - Response: {verify.text}")
except Exception as e:
    print(f"   ❌ Verification failed: {e}")

# Test 3: Webhook message (POST request)
print("\n3. Testing webhook message...")
test_payload = {
    "entry": [{
        "changes": [{
            "value": {
                "messages": [{
                    "from": "919876543210",
                    "id": "test_msg_001",
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

try:
    webhook = requests.post(
        f"{ngrok_url}/webhook/whatsapp",
        json=test_payload,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    print(f"   ✅ Webhook: {webhook.status_code}")
    print(f"   📝 Response: {webhook.json()}")
except Exception as e:
    print(f"   ❌ Webhook failed: {e}")

print("\n🎯 If all tests pass, your webhook should work with WhatsApp!")
print("📋 Make sure your WhatsApp webhook settings are:")
print(f"   Callback URL: {ngrok_url}/webhook/whatsapp")
print("   Verify Token: mytoken")
