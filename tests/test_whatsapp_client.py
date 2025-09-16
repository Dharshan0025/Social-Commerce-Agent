import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.whatsapp_client import whatsapp_client
from config import settings

def test_whatsapp_credentials_configured():
    """Test if WhatsApp credentials are properly configured."""
    print(f"WhatsApp Access Token: {'✓ Configured' if settings.whatsapp_access_token else '✗ Missing'}")
    print(f"WhatsApp Phone Number ID: {'✓ Configured' if settings.whatsapp_phone_number_id else '✗ Missing'}")
    print(f"WhatsApp Verify Token: {'✓ Configured' if settings.whatsapp_verify_token else '✗ Missing'}")
    
    # Check if essential credentials are present
    assert settings.whatsapp_access_token, "WHATSAPP_ACCESS_TOKEN is required"
    assert settings.whatsapp_verify_token, "WHATSAPP_VERIFY_TOKEN is required"
    
    # Phone number ID is required for sending messages
    if settings.whatsapp_phone_number_id == "your_phone_number_id_here":
        print("⚠️  Warning: WHATSAPP_PHONE_NUMBER_ID needs to be configured with actual phone number ID")

async def test_send_text_message_missing_credentials():
    """Test sending message with missing credentials."""
    # Temporarily clear credentials
    original_token = whatsapp_client.access_token
    original_phone_id = whatsapp_client.phone_number_id
    
    whatsapp_client.access_token = ""
    whatsapp_client.phone_number_id = ""
    
    result = await whatsapp_client.send_text_message("1234567890", "Test message")
    
    assert result["success"] is False
    assert "credentials not configured" in result["error"]
    
    # Restore credentials
    whatsapp_client.access_token = original_token
    whatsapp_client.phone_number_id = original_phone_id

if __name__ == "__main__":
    # Run basic credential check
    test_whatsapp_credentials_configured()
    
    # Run async tests
    async def run_async_tests():
        await test_send_text_message_missing_credentials()
        print("✓ Missing credentials test passed")
    
    asyncio.run(run_async_tests())
    print("✓ WhatsApp client tests completed")
