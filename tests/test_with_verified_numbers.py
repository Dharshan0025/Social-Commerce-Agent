#!/usr/bin/env python3
"""
Test WhatsApp messaging with verified phone numbers
"""
import asyncio
import json
from utils.whatsapp_client import whatsapp_client

async def test_verified_numbers():
    """Test with your verified phone numbers."""
    print("🧪 Testing WhatsApp with Verified Numbers")
    print("=" * 50)
    
    # You can replace these with your actual verified numbers
    # Format: country code + number (no + sign)
    test_numbers = [
        "919514102589",  # With India country code +91
        "919840604033",  # With India country code +91
    ]
    
    print("Please update the phone numbers in this script with your verified numbers:")
    print("1. Open test_with_verified_numbers.py")
    print("2. Replace the numbers in test_numbers list")
    print("3. Run the script again")
    print()
    
    for i, number in enumerate(test_numbers, 1):
        print(f"Testing with number {i}: {number}")
        
        try:
            result = await whatsapp_client.send_text_message(
                number,
                f"🤖 Test message {i} from Social Commerce AI Agent - Testing verified number!"
            )
            
            print(f"Result: {json.dumps(result, indent=2)}")
            
            if result.get("success"):
                print(f"✅ Message sent successfully to {number}")
                print(f"Message ID: {result.get('message_id')}")
            else:
                print(f"❌ Failed to send to {number}: {result.get('error')}")
                if "details" in result:
                    print(f"Details: {result['details']}")
            
            print("-" * 30)
            
        except Exception as e:
            print(f"❌ Exception testing {number}: {str(e)}")
        
        # Wait between tests
        await asyncio.sleep(2)

if __name__ == "__main__":
    print("📱 Replace the phone numbers in this script with your verified numbers")
    print("Format: country_code + number (no + sign)")
    print("Example: 919876543210 for India")
    print()
    
    choice = input("Have you updated the phone numbers? (y/n): ").lower().strip()
    if choice in ['y', 'yes']:
        asyncio.run(test_verified_numbers())
    else:
        print("Please update the phone numbers first and run again.")
