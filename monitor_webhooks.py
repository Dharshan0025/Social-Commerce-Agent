#!/usr/bin/env python3
"""
Monitor incoming WhatsApp webhooks in real-time
"""
import time
import requests
import json
from datetime import datetime

def monitor_ngrok_requests():
    """Monitor ngrok requests in real-time."""
    print("🔍 Monitoring WhatsApp Webhooks")
    print("=" * 40)
    print("Waiting for WhatsApp messages...")
    print("Send a message to your WhatsApp Business number to test")
    print("Press Ctrl+C to stop monitoring")
    print()
    
    last_request_time = time.time()
    
    try:
        while True:
            try:
                # Get ngrok tunnel requests
                response = requests.get("http://localhost:4040/api/requests/http", timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    requests_data = data.get('requests', [])
                    
                    for req in requests_data:
                        req_time = req.get('started_at', '')
                        req_timestamp = datetime.fromisoformat(req_time.replace('Z', '+00:00')).timestamp()
                        
                        if req_timestamp > last_request_time:
                            method = req.get('request', {}).get('method', 'Unknown')
                            uri = req.get('request', {}).get('uri', 'Unknown')
                            status = req.get('response', {}).get('status', 'Unknown')
                            
                            print(f"📨 {datetime.now().strftime('%H:%M:%S')} - {method} {uri} → {status}")
                            
                            # If it's a WhatsApp webhook
                            if '/webhook/whatsapp' in uri and method == 'POST':
                                print("🎉 WhatsApp webhook received!")
                                
                                # Try to get request body
                                req_body = req.get('request', {}).get('body', '')
                                if req_body:
                                    try:
                                        webhook_data = json.loads(req_body)
                                        messages = webhook_data.get('entry', [{}])[0].get('changes', [{}])[0].get('value', {}).get('messages', [])
                                        
                                        if messages:
                                            msg = messages[0]
                                            from_number = msg.get('from', 'Unknown')
                                            message_text = msg.get('text', {}).get('body', 'No text')
                                            print(f"📱 From: {from_number}")
                                            print(f"💬 Message: {message_text}")
                                    except:
                                        print("📄 Webhook data received (couldn't parse)")
                                
                                print("-" * 40)
                            
                            last_request_time = req_timestamp
                
                time.sleep(2)  # Check every 2 seconds
                
            except requests.exceptions.RequestException:
                print("⚠️  ngrok not accessible - make sure ngrok is running")
                time.sleep(5)
                
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped")

if __name__ == "__main__":
    monitor_ngrok_requests()
