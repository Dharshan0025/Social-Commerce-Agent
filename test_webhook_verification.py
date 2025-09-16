#!/usr/bin/env python3
"""
Test webhook verification through ngrok
"""
import requests

def test_ngrok_webhook_verification():
    """Test webhook verification through ngrok tunnel."""
    print("🔍 Testing Webhook Verification Through ngrok")
    print("=" * 50)
    
    # Get ngrok tunnel URL
    try:
        response = requests.get("http://localhost:4040/api/tunnels")
        if response.status_code == 200:
            data = response.json()
            tunnels = data.get('tunnels', [])
            
            for tunnel in tunnels:
                if tunnel.get('proto') == 'https':
                    public_url = tunnel.get('public_url')
                    print(f"Testing: {public_url}")
                    
                    # Test webhook verification
                    verify_url = f"{public_url}/webhook/whatsapp?hub.mode=subscribe&hub.challenge=VERIFICATION_TEST&hub.verify_token=mytoken"
                    
                    try:
                        verify_response = requests.get(verify_url, timeout=10)
                        print(f"Status: {verify_response.status_code}")
                        print(f"Response: {verify_response.text}")
                        
                        if verify_response.status_code == 200 and verify_response.text == "VERIFICATION_TEST":
                            print("✅ Webhook verification through ngrok: SUCCESS")
                            print(f"📝 Use this URL in Meta Business Manager:")
                            print(f"   Callback URL: {public_url}/webhook/whatsapp")
                            print(f"   Verify Token: mytoken")
                            return True
                        else:
                            print("❌ Webhook verification failed")
                            return False
                            
                    except Exception as e:
                        print(f"❌ Error testing webhook: {e}")
                        return False
            
            print("❌ No HTTPS tunnel found")
            return False
        else:
            print("❌ Cannot access ngrok API")
            return False
    except Exception as e:
        print(f"❌ ngrok not running: {e}")
        return False

if __name__ == "__main__":
    test_ngrok_webhook_verification()
