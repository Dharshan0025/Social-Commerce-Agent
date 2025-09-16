#!/usr/bin/env python3
"""
Simple script to check WhatsApp Business API configuration
"""
import os
import sys
from config import settings

def check_whatsapp_config():
    """Check WhatsApp configuration and credentials."""
    print("=== WhatsApp Business API Configuration Check ===\n")
    
    # Check access token
    if settings.whatsapp_access_token:
        token_preview = settings.whatsapp_access_token[:20] + "..." if len(settings.whatsapp_access_token) > 20 else settings.whatsapp_access_token
        print(f"✓ WhatsApp Access Token: Configured ({token_preview})")
    else:
        print("✗ WhatsApp Access Token: Missing")
    
    # Check phone number ID
    if settings.whatsapp_phone_number_id and settings.whatsapp_phone_number_id != "your_phone_number_id_here":
        print(f"✓ WhatsApp Phone Number ID: Configured ({settings.whatsapp_phone_number_id})")
    else:
        print("✗ WhatsApp Phone Number ID: Missing or not configured")
        print("  → Please update WHATSAPP_PHONE_NUMBER_ID in .env file")
    
    # Check verify token
    if settings.whatsapp_verify_token:
        print(f"✓ WhatsApp Verify Token: Configured ({settings.whatsapp_verify_token})")
    else:
        print("✗ WhatsApp Verify Token: Missing")
    
    print("\n=== Configuration Status ===")
    
    # Overall status
    ready_to_send = (
        settings.whatsapp_access_token and 
        settings.whatsapp_phone_number_id and 
        settings.whatsapp_phone_number_id != "your_phone_number_id_here"
    )
    
    if ready_to_send:
        print("🟢 Ready to send WhatsApp messages!")
    else:
        print("🔴 Not ready to send WhatsApp messages")
        print("\nRequired for sending messages:")
        if not settings.whatsapp_access_token:
            print("  - WHATSAPP_ACCESS_TOKEN")
        if not settings.whatsapp_phone_number_id or settings.whatsapp_phone_number_id == "your_phone_number_id_here":
            print("  - WHATSAPP_PHONE_NUMBER_ID (actual phone number ID from Meta)")
    
    print("\n=== Next Steps ===")
    if not ready_to_send:
        print("1. Get your WhatsApp Business API credentials from Meta Business:")
        print("   - Go to https://developers.facebook.com/")
        print("   - Create/select your app")
        print("   - Add WhatsApp Business API product")
        print("   - Get your Phone Number ID from the API setup")
        print("   - Update the .env file with the actual Phone Number ID")
        print("\n2. Test the webhook endpoint with ngrok")
        print("3. Configure webhook subscription in Meta Business")
    else:
        print("1. Start the server: python main.py")
        print("2. Start ngrok: ngrok http 8000")
        print("3. Update webhook URL in Meta Business with ngrok URL")
        print("4. Test by sending a WhatsApp message")

if __name__ == "__main__":
    check_whatsapp_config()
