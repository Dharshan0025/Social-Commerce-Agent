#!/usr/bin/env python3
"""
Test the fixed WhatsApp client with proper phone number formatting
"""
import asyncio
from utils.whatsapp_client import whatsapp_client

async def test_fixed_client():
    """Test the updated WhatsApp client."""
    print("🧪 Testing Fixed WhatsApp Client")
    print("=" * 40)
    
    # Test with your verified numbers (without + prefix)
    test_numbers = [
        "919514102589",
        "919840604033"
    ]
    
    for i, number in enumerate(test_numbers, 1):
        print(f"Testing number {i}: {number}")
        
        result = await whatsapp_client.send_text_message(
            number,
            f"🎉 WhatsApp messaging is now WORKING! Test message {i} from Social Commerce AI Agent"
        )
        
        if result.get("success"):
            print(f"✅ SUCCESS! Message sent to {number}")
            print(f"Message ID: {result.get('message_id')}")
        else:
            print(f"❌ Failed: {result.get('error')}")
        
        print("-" * 30)
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(test_fixed_client())
