#!/usr/bin/env python3
"""
Comprehensive debug script to test WhatsApp API integration
"""
import asyncio
import httpx
import json
from config import settings
from utils.whatsapp_client import whatsapp_client

async def test_whatsapp_api_directly():
    """Test WhatsApp API directly with real credentials."""
    print("=== Testing WhatsApp Business API Directly ===")
    
    # Check credentials
    print(f"Access Token: {'✓' if settings.whatsapp_access_token else '✗'}")
    print(f"Phone Number ID: {'✓' if settings.whatsapp_phone_number_id else '✗'}")
    print(f"Phone Number ID Value: {settings.whatsapp_phone_number_id}")
    
    if not settings.whatsapp_access_token or not settings.whatsapp_phone_number_id:
        print("❌ Missing credentials - cannot test API")
        return False
    
    if settings.whatsapp_phone_number_id == "your_phone_number_id_here":
        print("❌ Phone Number ID not configured properly")
        return False
    
    # Test API endpoint directly
    try:
        url = f"https://graph.facebook.com/v18.0/{settings.whatsapp_phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {settings.whatsapp_access_token}",
            "Content-Type": "application/json"
        }
        
        # Use a test phone number (your own number)
        test_payload = {
            "messaging_product": "whatsapp",
            "to": "919876543210",  # Replace with your actual WhatsApp number
            "type": "text",
            "text": {
                "body": "🤖 Test message from Social Commerce AI Agent - API working!"
            }
        }
        
        print(f"Testing API endpoint: {url}")
        print(f"Payload: {json.dumps(test_payload, indent=2)}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=test_payload)
            
            print(f"Response Status: {response.status_code}")
            print(f"Response Body: {response.text}")
            
            if response.status_code == 200:
                print("✅ WhatsApp API working - message sent successfully!")
                return True
            else:
                print(f"❌ WhatsApp API error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error details: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"Raw error: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Exception testing WhatsApp API: {str(e)}")
        return False

async def test_whatsapp_client():
    """Test our WhatsApp client wrapper."""
    print("\n=== Testing WhatsApp Client Wrapper ===")
    
    try:
        result = await whatsapp_client.send_text_message(
            "919876543210",  # Replace with your actual WhatsApp number
            "🤖 Test message from WhatsApp Client - wrapper working!"
        )
        
        print(f"Client result: {json.dumps(result, indent=2)}")
        
        if result.get("success"):
            print("✅ WhatsApp Client working!")
            return True
        else:
            print(f"❌ WhatsApp Client failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Exception testing WhatsApp Client: {str(e)}")
        return False

async def test_coordinator_flow():
    """Test the coordinator message processing flow."""
    print("\n=== Testing Coordinator Flow ===")
    
    try:
        from agents.coordinator import CoordinatorAgent
        
        coordinator = CoordinatorAgent()
        await coordinator.initialize()
        
        # Test webhook payload
        test_payload = {
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
                                    "phone_number_id": settings.whatsapp_phone_number_id
                                },
                                "contacts": [
                                    {
                                        "profile": {
                                            "name": "Debug Test"
                                        },
                                        "wa_id": "919876543210"  # Replace with your number
                                    }
                                ],
                                "messages": [
                                    {
                                        "from": "919876543210",  # Replace with your number
                                        "id": "wamid.debug123",
                                        "timestamp": "1234567890",
                                        "text": {
                                            "body": "Debug test - send me iPhone 15 Pro price"
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
        
        print("Processing test message through coordinator...")
        result = await coordinator.process_whatsapp_message(test_payload)
        
        print(f"Coordinator result: {json.dumps(result, indent=2)}")
        
        if result.get("status") == "processed":
            print("✅ Coordinator processing working!")
            return True
        else:
            print(f"❌ Coordinator failed: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Exception testing Coordinator: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def check_server_running():
    """Check if the server is running and accessible."""
    print("\n=== Checking Server Status ===")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health", timeout=5.0)
            
            if response.status_code == 200:
                print("✅ Server is running and accessible")
                print(f"Health response: {response.json()}")
                return True
            else:
                print(f"❌ Server responding with error: {response.status_code}")
                return False
                
    except httpx.ConnectError:
        print("❌ Server not running or not accessible on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {str(e)}")
        return False

async def main():
    """Run all debug tests."""
    print("🔍 WhatsApp Social Commerce Agent - Debug Analysis")
    print("=" * 60)
    
    # Test 1: Check server
    server_ok = await check_server_running()
    
    # Test 2: Test WhatsApp API directly
    api_ok = await test_whatsapp_api_directly()
    
    # Test 3: Test WhatsApp client wrapper
    client_ok = await test_whatsapp_client()
    
    # Test 4: Test coordinator flow
    coordinator_ok = await test_coordinator_flow()
    
    # Summary
    print(f"\n{'='*60}")
    print("🏁 Debug Summary:")
    print(f"Server Running: {'✅' if server_ok else '❌'}")
    print(f"WhatsApp API: {'✅' if api_ok else '❌'}")
    print(f"Client Wrapper: {'✅' if client_ok else '❌'}")
    print(f"Coordinator Flow: {'✅' if coordinator_ok else '❌'}")
    
    if not api_ok:
        print(f"\n🔧 WhatsApp API Issues:")
        print("1. Check if your access token is valid and not expired")
        print("2. Verify the phone number ID is correct")
        print("3. Ensure your WhatsApp Business account is approved")
        print("4. Check if you have the necessary permissions")
        print("5. Try sending a message manually from Meta Business Manager")
    
    if not server_ok:
        print(f"\n🔧 Server Issues:")
        print("1. Start the server with: python main.py")
        print("2. Check if port 8000 is available")
        print("3. Check for any startup errors in logs")
    
    if api_ok and server_ok and not coordinator_ok:
        print(f"\n🔧 Coordinator Issues:")
        print("1. Check agent initialization")
        print("2. Verify Google Sheets connectivity")
        print("3. Check Groq API connectivity")

if __name__ == "__main__":
    asyncio.run(main())
