#!/usr/bin/env python3
"""
Test script to simulate WhatsApp webhook messages and test the complete flow
"""
import asyncio
import httpx
import json
from datetime import datetime

# Sample WhatsApp webhook payload
SAMPLE_WHATSAPP_MESSAGE = {
    "object": "whatsapp_business_account",
    "entry": [
        {
            "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
            "changes": [
                {
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "15550559999",
                            "phone_number_id": "123456789012345"
                        },
                        "contacts": [
                            {
                                "profile": {
                                    "name": "Test Customer"
                                },
                                "wa_id": "919876543210"
                            }
                        ],
                        "messages": [
                            {
                                "from": "919876543210",
                                "id": "wamid.test123",
                                "timestamp": str(int(datetime.now().timestamp())),
                                "text": {
                                    "body": "Hi, I want to buy iPhone 15 Pro"
                                },
                                "type": "text"
                            }
                        ]
                    },
                    "field": "messages"
                }
            ]
        }
    ]
}

SAMPLE_TAMIL_MESSAGE = {
    "object": "whatsapp_business_account",
    "entry": [
        {
            "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
            "changes": [
                {
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "15550559999",
                            "phone_number_id": "123456789012345"
                        },
                        "contacts": [
                            {
                                "profile": {
                                    "name": "Tamil Customer"
                                },
                                "wa_id": "919876543211"
                            }
                        ],
                        "messages": [
                            {
                                "from": "919876543211",
                                "id": "wamid.test124",
                                "timestamp": str(int(datetime.now().timestamp())),
                                "text": {
                                    "body": "Anna, iPhone 15 Pro venum da"
                                },
                                "type": "text"
                            }
                        ]
                    },
                    "field": "messages"
                }
            ]
        }
    ]
}

async def test_whatsapp_webhook(message_payload, test_name):
    """Test WhatsApp webhook endpoint with sample message."""
    try:
        print(f"\n=== Testing {test_name} ===")
        
        url = "http://localhost:8000/webhook/whatsapp"
        headers = {"Content-Type": "application/json"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=message_payload, headers=headers)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Test passed: {test_name}")
                print(f"Processing Status: {result.get('status')}")
                if result.get('response_sent'):
                    print(f"Response Generated: {result.get('response_sent')[:100]}...")
                return True
            else:
                print(f"❌ Test failed: {test_name}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing {test_name}: {str(e)}")
        return False

async def test_payment_webhook():
    """Test payment webhook endpoint."""
    try:
        print(f"\n=== Testing Payment Webhook ===")
        
        payment_payload = {
            "status": "success",
            "payment_id": "pay_test123",
            "customer_phone": "919876543210",
            "amount": "79900",
            "currency": "INR",
            "timestamp": str(int(datetime.now().timestamp()))
        }
        
        url = "http://localhost:8000/webhook/payment"
        headers = {"Content-Type": "application/json"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payment_payload, headers=headers)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Payment webhook test passed")
                print(f"Processing Status: {result.get('status')}")
                return True
            else:
                print(f"❌ Payment webhook test failed")
                return False
                
    except Exception as e:
        print(f"❌ Error testing payment webhook: {str(e)}")
        return False

async def test_health_endpoint():
    """Test health endpoint."""
    try:
        print(f"\n=== Testing Health Endpoint ===")
        
        url = "http://localhost:8000/health"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                print(f"✅ Health endpoint test passed")
                return True
            else:
                print(f"❌ Health endpoint test failed")
                return False
                
    except Exception as e:
        print(f"❌ Error testing health endpoint: {str(e)}")
        return False

async def main():
    """Run all webhook tests."""
    print("🚀 Starting WhatsApp Social Commerce Agent Tests")
    print("=" * 50)
    
    # Test health endpoint first
    health_ok = await test_health_endpoint()
    
    if not health_ok:
        print("❌ Server not responding. Make sure the server is running on localhost:8000")
        return
    
    # Test WhatsApp webhook with English message
    english_test = await test_whatsapp_webhook(SAMPLE_WHATSAPP_MESSAGE, "English Product Query")
    
    # Wait a bit between tests
    await asyncio.sleep(2)
    
    # Test WhatsApp webhook with Tamil message
    tamil_test = await test_whatsapp_webhook(SAMPLE_TAMIL_MESSAGE, "Tamil Product Query")
    
    # Wait a bit between tests
    await asyncio.sleep(2)
    
    # Test payment webhook
    payment_test = await test_payment_webhook()
    
    # Summary
    print(f"\n{'='*50}")
    print("🏁 Test Summary:")
    print(f"Health Endpoint: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"English Message: {'✅ PASS' if english_test else '❌ FAIL'}")
    print(f"Tamil Message: {'✅ PASS' if tamil_test else '❌ FAIL'}")
    print(f"Payment Webhook: {'✅ PASS' if payment_test else '❌ FAIL'}")
    
    if all([health_ok, english_test, tamil_test, payment_test]):
        print("\n🎉 All tests passed! Your WhatsApp Social Commerce Agent is working!")
        print("\n📱 Next Steps:")
        print("1. Install ngrok: https://ngrok.com/download")
        print("2. Run: ngrok http 8000")
        print("3. Copy the ngrok URL and configure it in Meta Business Manager")
        print("4. Test with real WhatsApp messages!")
    else:
        print("\n❌ Some tests failed. Check the logs above for details.")

if __name__ == "__main__":
    asyncio.run(main())
