#!/usr/bin/env python3
"""
Script to fetch WhatsApp Business Phone Number ID using the access token
"""
import asyncio
import httpx
from config import settings

async def get_phone_number_id():
    """Fetch the WhatsApp Business Phone Number ID using the access token."""
    
    if not settings.whatsapp_access_token:
        print("❌ WhatsApp Access Token not configured in .env file")
        return None
    
    try:
        # First get the WhatsApp Business Account ID
        url = "https://graph.facebook.com/v18.0/me/businesses"
        headers = {
            "Authorization": f"Bearer {settings.whatsapp_access_token}"
        }
        
        print("🔍 Fetching WhatsApp Business Phone Numbers...")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                phone_numbers = data.get("data", [])
                
                if phone_numbers:
                    print(f"✅ Found {len(phone_numbers)} phone number(s):")
                    for i, phone in enumerate(phone_numbers, 1):
                        phone_id = phone.get("id")
                        display_name = phone.get("display_phone_number", "N/A")
                        verified_name = phone.get("verified_name", "N/A")
                        status = phone.get("status", "N/A")
                        
                        print(f"\n📱 Phone Number {i}:")
                        print(f"   ID: {phone_id}")
                        print(f"   Display Number: {display_name}")
                        print(f"   Verified Name: {verified_name}")
                        print(f"   Status: {status}")
                        
                        if i == 1:  # Use the first phone number
                            print(f"\n🎯 Using Phone Number ID: {phone_id}")
                            return phone_id
                else:
                    print("❌ No phone numbers found in your WhatsApp Business account")
                    print("   Make sure you have set up a phone number in Meta Business Manager")
                    return None
            else:
                error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"message": response.text}
                print(f"❌ API Error {response.status_code}: {error_data.get('error', {}).get('message', 'Unknown error')}")
                
                if response.status_code == 401:
                    print("   → Check if your access token is valid and has the necessary permissions")
                elif response.status_code == 403:
                    print("   → Your access token may not have permission to access phone numbers")
                
                return None
                
    except Exception as e:
        print(f"❌ Error fetching phone number ID: {str(e)}")
        return None

async def update_env_file(phone_number_id):
    """Update the .env file with the phone number ID."""
    try:
        env_file_path = ".env"
        
        # Read current .env file
        with open(env_file_path, 'r') as f:
            lines = f.readlines()
        
        # Update the phone number ID line
        updated = False
        for i, line in enumerate(lines):
            if line.startswith("WHATSAPP_PHONE_NUMBER_ID="):
                lines[i] = f"WHATSAPP_PHONE_NUMBER_ID={phone_number_id}\n"
                updated = True
                break
        
        if updated:
            # Write back to .env file
            with open(env_file_path, 'w') as f:
                f.writelines(lines)
            print(f"✅ Updated .env file with Phone Number ID: {phone_number_id}")
            return True
        else:
            print("❌ Could not find WHATSAPP_PHONE_NUMBER_ID line in .env file")
            return False
            
    except Exception as e:
        print(f"❌ Error updating .env file: {str(e)}")
        return False

async def main():
    """Main function to get and update phone number ID."""
    print("=== WhatsApp Phone Number ID Fetcher ===\n")
    
    phone_number_id = await get_phone_number_id()
    
    if phone_number_id:
        print(f"\n📋 Copy this Phone Number ID to your .env file:")
        print(f"WHATSAPP_PHONE_NUMBER_ID={phone_number_id}")
        
        # Ask user if they want to auto-update
        try:
            update_choice = input("\n❓ Do you want to automatically update the .env file? (y/n): ").lower().strip()
            if update_choice in ['y', 'yes']:
                success = await update_env_file(phone_number_id)
                if success:
                    print("\n🎉 Configuration updated! You can now send WhatsApp messages.")
                    print("   Run 'python check_whatsapp_config.py' to verify the configuration.")
        except KeyboardInterrupt:
            print("\n\n👋 Cancelled by user")
    else:
        print("\n❌ Could not retrieve Phone Number ID")
        print("\n🔧 Manual steps:")
        print("1. Go to https://developers.facebook.com/")
        print("2. Select your app")
        print("3. Go to WhatsApp > API Setup")
        print("4. Copy the Phone Number ID")
        print("5. Update WHATSAPP_PHONE_NUMBER_ID in .env file")

if __name__ == "__main__":
    asyncio.run(main())
