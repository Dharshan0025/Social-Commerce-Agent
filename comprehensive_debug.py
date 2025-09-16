#!/usr/bin/env python3
"""
Comprehensive debug script to identify WhatsApp webhook issues
"""
import asyncio
import httpx
import json
import requests
from datetime import datetime
from config import settings

async def test_webhook_endpoint():
    """Test all webhook endpoints thoroughly."""
    print("🔍 Testing Webhook Endpoints")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health Check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test 2: Webhook verification (GET)
    verify_url = f"{base_url}/webhook/whatsapp?hub.mode=subscribe&hub.challenge=TEST123&hub.verify_token=mytoken"
    try:
        response = requests.get(verify_url)
        print(f"Webhook Verification: {response.status_code} - {response.text}")
        if response.status_code != 200 or response.text != "TEST123":
            print("❌ Webhook verification failed")
            return False
    except Exception as e:
        print(f"❌ Webhook verification error: {e}")
        return False
    
    # Test 3: Webhook POST with minimal payload
    minimal_payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "test_id",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "15551234567",
                                "phone_number_id": settings.whatsapp_phone_number_id
                            },
                            "contacts": [
                                {
                                    "profile": {"name": "Test User"},
                                    "wa_id": "919514102589"
                                }
                            ],
                            "messages": [
                                {
                                    "from": "919514102589",
                                    "id": "test_msg_id",
                                    "timestamp": str(int(datetime.now().timestamp())),
                                    "text": {"body": "test message"},
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
    
    try:
        response = requests.post(
            f"{base_url}/webhook/whatsapp",
            json=minimal_payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Webhook POST: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Webhook POST failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Webhook POST error: {e}")
        return False

def check_ngrok_status():
    """Check ngrok tunnel status and configuration."""
    print("\n🌐 Checking ngrok Configuration")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:4040/api/tunnels")
        if response.status_code == 200:
            data = response.json()
            tunnels = data.get('tunnels', [])
            
            for tunnel in tunnels:
                if tunnel.get('proto') == 'https':
                    public_url = tunnel.get('public_url')
                    config = tunnel.get('config', {})
                    
                    print(f"✅ HTTPS Tunnel: {public_url}")
                    print(f"   Local: {config.get('addr')}")
                    print(f"   Webhook URL: {public_url}/webhook/whatsapp")
                    
                    # Test webhook verification through ngrok
                    verify_url = f"{public_url}/webhook/whatsapp?hub.mode=subscribe&hub.challenge=NGROK_TEST&hub.verify_token=mytoken"
                    try:
                        ngrok_response = requests.get(verify_url, timeout=10)
                        if ngrok_response.status_code == 200 and ngrok_response.text == "NGROK_TEST":
                            print("✅ Webhook verification through ngrok: SUCCESS")
                            return public_url
                        else:
                            print(f"❌ Webhook verification through ngrok failed: {ngrok_response.status_code}")
                    except Exception as e:
                        print(f"❌ ngrok webhook test error: {e}")
                    
                    return public_url
            
            print("❌ No HTTPS tunnel found")
            return None
        else:
            print("❌ Cannot access ngrok API")
            return None
    except Exception as e:
        print(f"❌ ngrok not running: {e}")
        return None

def check_meta_webhook_config(webhook_url):
    """Provide instructions to check Meta webhook configuration."""
    print(f"\n📱 Meta Business Webhook Configuration")
    print("=" * 40)
    print("Please verify these settings in Meta Business Manager:")
    print(f"1. Callback URL: {webhook_url}")
    print("2. Verify Token: mytoken")
    print("3. Webhook Fields: messages (subscribed)")
    print("4. App Status: Live (not in development mode)")
    print("\nTo check:")
    print("1. Go to https://developers.facebook.com/")
    print("2. Your App > WhatsApp > Configuration")
    print("3. Verify webhook settings")
    print("4. Check webhook subscription status")

async def test_coordinator_directly():
    """Test coordinator processing directly."""
    print(f"\n🤖 Testing Coordinator Processing")
    print("=" * 40)
    
    try:
        from agents.coordinator import CoordinatorAgent
        
        coordinator = CoordinatorAgent()
        await coordinator.initialize()
        
        test_payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "test_entry",
                    "changes": [
                        {
                            "value": {
                                "messaging_product": "whatsapp",
                                "metadata": {
                                    "display_phone_number": "15551234567",
                                    "phone_number_id": settings.whatsapp_phone_number_id
                                },
                                "contacts": [
                                    {
                                        "profile": {"name": "Direct Test"},
                                        "wa_id": "919514102589"
                                    }
                                ],
                                "messages": [
                                    {
                                        "from": "919514102589",
                                        "id": "direct_test_msg",
                                        "timestamp": str(int(datetime.now().timestamp())),
                                        "text": {"body": "Direct coordinator test - iPhone price"},
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
        
        result = await coordinator.process_whatsapp_message(test_payload)
        print(f"Coordinator Result: {json.dumps(result, indent=2)}")
        
        if result.get("status") == "processed":
            print("✅ Coordinator processing: SUCCESS")
            return True
        else:
            print(f"❌ Coordinator processing failed: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Coordinator test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_whatsapp_credentials():
    """Check WhatsApp API credentials and permissions."""
    print(f"\n🔑 Checking WhatsApp Credentials")
    print("=" * 40)
    
    print(f"Access Token: {'✅' if settings.whatsapp_access_token else '❌'}")
    print(f"Phone Number ID: {'✅' if settings.whatsapp_phone_number_id else '❌'}")
    print(f"Verify Token: {'✅' if settings.whatsapp_verify_token else '❌'}")
    
    if settings.whatsapp_phone_number_id:
        print(f"Phone Number ID: {settings.whatsapp_phone_number_id}")
    
    # Test API access
    if settings.whatsapp_access_token and settings.whatsapp_phone_number_id:
        try:
            url = f"https://graph.facebook.com/v18.0/{settings.whatsapp_phone_number_id}"
            headers = {"Authorization": f"Bearer {settings.whatsapp_access_token}"}
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Phone Number Status: {data.get('verified_name', 'Unknown')}")
                print(f"   Display Number: {data.get('display_phone_number', 'Unknown')}")
                print(f"   Quality Rating: {data.get('quality_rating', 'Unknown')}")
            else:
                print(f"❌ API Access Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ API Test Error: {e}")

async def main():
    """Run comprehensive debugging."""
    print("🔍 WhatsApp Social Commerce Agent - Comprehensive Debug")
    print("=" * 60)
    
    # Test 1: Webhook endpoints
    webhook_ok = await test_webhook_endpoint()
    
    # Test 2: ngrok configuration
    webhook_url = check_ngrok_status()
    
    # Test 3: WhatsApp credentials
    check_whatsapp_credentials()
    
    # Test 4: Coordinator processing
    coordinator_ok = await test_coordinator_directly()
    
    # Test 5: Meta configuration guidance
    if webhook_url:
        check_meta_webhook_config(webhook_url)
    
    # Summary
    print(f"\n{'='*60}")
    print("🏁 Debug Summary:")
    print(f"Webhook Endpoints: {'✅' if webhook_ok else '❌'}")
    print(f"ngrok Tunnel: {'✅' if webhook_url else '❌'}")
    print(f"Coordinator Processing: {'✅' if coordinator_ok else '❌'}")
    
    if webhook_ok and webhook_url and coordinator_ok:
        print(f"\n🎉 All components working! Issue likely in Meta configuration.")
        print(f"📱 Next steps:")
        print(f"1. Verify webhook URL in Meta: {webhook_url}/webhook/whatsapp")
        print(f"2. Ensure 'messages' field is subscribed")
        print(f"3. Check app is in Live mode (not Development)")
        print(f"4. Send test message and monitor ngrok: http://localhost:4040")
    else:
        print(f"\n❌ Issues found - check the details above")

if __name__ == "__main__":
    asyncio.run(main())
