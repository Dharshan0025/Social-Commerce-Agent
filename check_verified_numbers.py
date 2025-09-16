#!/usr/bin/env python3
"""
Check what phone numbers are actually verified in your WhatsApp Business account
"""
import asyncio
import httpx
import json
from config import settings

async def get_verified_numbers():
    """Get the list of verified phone numbers from WhatsApp Business API."""
    try:
        # Try different API endpoints to get phone numbers
        endpoints = [
            f"https://graph.facebook.com/v18.0/{settings.whatsapp_phone_number_id}",
            f"https://graph.facebook.com/v18.0/me/phone_numbers",
            f"https://graph.facebook.com/v18.0/{settings.whatsapp_phone_number_id}/phone_numbers"
        ]
        
        headers = {
            "Authorization": f"Bearer {settings.whatsapp_access_token}"
        }
        
        async with httpx.AsyncClient() as client:
            for endpoint in endpoints:
                print(f"Trying endpoint: {endpoint}")
                try:
                    response = await client.get(endpoint, headers=headers)
                    print(f"Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"Response: {json.dumps(data, indent=2)}")
                    else:
                        print(f"Error: {response.text}")
                    
                    print("-" * 50)
                except Exception as e:
                    print(f"Exception: {str(e)}")
                    print("-" * 50)
                    
    except Exception as e:
        print(f"Error: {str(e)}")

async def test_specific_formats():
    """Test different phone number formats."""
    print("Testing different formats for your numbers:")
    
    # Your numbers in different formats
    formats_to_test = [
        # Without country code
        "9514102589",
        "9840604033",
        # With +91
        "+919514102589", 
        "+919840604033",
        # With 91
        "919514102589",
        "919840604033",
        # With 0091
        "00919514102589",
        "00919840604033"
    ]
    
    headers = {
        "Authorization": f"Bearer {settings.whatsapp_access_token}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        for number in formats_to_test:
            print(f"Testing format: {number}")
            
            payload = {
                "messaging_product": "whatsapp",
                "to": number,
                "type": "text",
                "text": {
                    "body": f"Test format: {number}"
                }
            }
            
            try:
                url = f"https://graph.facebook.com/v18.0/{settings.whatsapp_phone_number_id}/messages"
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    print(f"✅ SUCCESS with format: {number}")
                    result = response.json()
                    print(f"Message ID: {result.get('messages', [{}])[0].get('id')}")
                    break  # Stop on first success
                else:
                    error = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"error": response.text}
                    print(f"❌ Failed: {error.get('error', {}).get('message', 'Unknown error')}")
                    
            except Exception as e:
                print(f"❌ Exception: {str(e)}")
            
            print("-" * 30)
            await asyncio.sleep(1)

async def main():
    print("🔍 Checking WhatsApp Business Account Configuration")
    print("=" * 60)
    
    print("1. Getting account info...")
    await get_verified_numbers()
    
    print("\n2. Testing phone number formats...")
    await test_specific_formats()

if __name__ == "__main__":
    asyncio.run(main())
