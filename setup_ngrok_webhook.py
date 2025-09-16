#!/usr/bin/env python3
"""
Script to help set up ngrok and webhook configuration
"""
import subprocess
import sys
import time
import requests
import json

def check_ngrok_installed():
    """Check if ngrok is installed."""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ ngrok is installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ ngrok not found")
            return False
    except FileNotFoundError:
        print("❌ ngrok not installed")
        return False

def check_server_running():
    """Check if the server is running on localhost:8000."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running on localhost:8000")
            return True
        else:
            print(f"❌ Server responding with error: {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        print("❌ Server not running on localhost:8000")
        return False

def get_ngrok_tunnels():
    """Get active ngrok tunnels."""
    try:
        response = requests.get("http://localhost:4040/api/tunnels")
        if response.status_code == 200:
            data = response.json()
            tunnels = data.get('tunnels', [])
            
            for tunnel in tunnels:
                if tunnel.get('proto') == 'https':
                    public_url = tunnel.get('public_url')
                    print(f"🌐 ngrok HTTPS URL: {public_url}")
                    print(f"📝 Webhook URL: {public_url}/webhook/whatsapp")
                    return public_url
            
            print("❌ No HTTPS tunnel found")
            return None
        else:
            print("❌ Cannot access ngrok API")
            return None
    except requests.exceptions.RequestException:
        print("❌ ngrok not running or API not accessible")
        return None

def main():
    """Main setup function."""
    print("🚀 WhatsApp Webhook Setup Helper")
    print("=" * 40)
    
    # Step 1: Check if server is running
    print("\n1. Checking server status...")
    server_ok = check_server_running()
    
    if not server_ok:
        print("\n❌ Please start your server first:")
        print("   python main.py")
        return
    
    # Step 2: Check ngrok installation
    print("\n2. Checking ngrok installation...")
    ngrok_installed = check_ngrok_installed()
    
    if not ngrok_installed:
        print("\n❌ Please install ngrok:")
        print("   1. Download from https://ngrok.com/download")
        print("   2. Extract and add to PATH")
        print("   3. Run: ngrok authtoken YOUR_TOKEN (optional)")
        return
    
    # Step 3: Check if ngrok is running
    print("\n3. Checking ngrok tunnel...")
    public_url = get_ngrok_tunnels()
    
    if not public_url:
        print("\n❌ Please start ngrok tunnel:")
        print("   ngrok http 8000")
        print("\n   Then run this script again")
        return
    
    # Step 4: Instructions for webhook configuration
    print(f"\n4. Configure WhatsApp Webhook:")
    print("   1. Go to https://developers.facebook.com/")
    print("   2. Select your app > WhatsApp > Configuration")
    print(f"   3. Callback URL: {public_url}/webhook/whatsapp")
    print("   4. Verify Token: mytoken")
    print("   5. Subscribe to 'messages' field")
    
    # Step 5: Test webhook
    print(f"\n5. Test webhook verification:")
    webhook_url = f"{public_url}/webhook/whatsapp"
    test_url = f"{webhook_url}?hub.mode=subscribe&hub.challenge=12345&hub.verify_token=mytoken"
    
    try:
        response = requests.get(test_url)
        if response.status_code == 200 and response.text == "12345":
            print("✅ Webhook verification endpoint working!")
        else:
            print(f"❌ Webhook verification failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing webhook: {str(e)}")
    
    print(f"\n🎉 Setup Complete!")
    print(f"📱 Send a WhatsApp message to test the complete flow")
    print(f"🔍 Monitor requests at: http://localhost:4040")

if __name__ == "__main__":
    main()
