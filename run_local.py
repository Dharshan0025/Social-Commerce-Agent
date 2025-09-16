#!/usr/bin/env python3
"""
Local development runner with sample test commands.
This script provides easy commands to test the Social Commerce AI Agent locally.
"""

import asyncio
import json
import requests
import sys
from typing import Dict, Any

# Base URL for local testing
BASE_URL = "http://localhost:8000"

def load_sample_payloads() -> Dict[str, Any]:
    """Load sample payloads from JSON file."""
    try:
        with open("sample_payloads.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ sample_payloads.json not found. Please ensure it exists in the project root.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("❌ Invalid JSON in sample_payloads.json")
        sys.exit(1)

def test_health_check():
    """Test the health check endpoint."""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        print("   Make sure the server is running with: python main.py")

def test_whatsapp_message(payload_name: str):
    """Test WhatsApp message processing."""
    payloads = load_sample_payloads()
    
    if payload_name not in payloads:
        print(f"❌ Payload '{payload_name}' not found in sample_payloads.json")
        return
    
    payload = payloads[payload_name]
    print(f"🔍 Testing WhatsApp message: {payload_name}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/test/message",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Message processed successfully")
            result = response.json()
            print(f"   Status: {result.get('status')}")
            if 'result' in result:
                print(f"   Customer: {result['result'].get('customer_phone')}")
                print(f"   Response: {result['result'].get('response_sent')}")
        else:
            print(f"❌ Message processing failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

def test_payment_webhook(payload_name: str):
    """Test payment webhook processing."""
    payloads = load_sample_payloads()
    
    if payload_name not in payloads:
        print(f"❌ Payload '{payload_name}' not found in sample_payloads.json")
        return
    
    payload = payloads[payload_name]
    print(f"🔍 Testing payment webhook: {payload_name}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/webhook/payment",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Payment webhook processed successfully")
            result = response.json()
            print(f"   Status: {result.get('status')}")
            if 'result' in result:
                print(f"   Payment ID: {result['result'].get('payment_id')}")
                print(f"   Response: {result['result'].get('response_sent')}")
        else:
            print(f"❌ Payment webhook failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

def run_all_tests():
    """Run all available tests."""
    print("🚀 Running all tests...\n")
    
    # Test health check
    test_health_check()
    print()
    
    # Test WhatsApp messages
    whatsapp_tests = [
        "whatsapp_text_message",
        "whatsapp_vendor_code_message", 
        "whatsapp_tamil_message",
        "whatsapp_image_message",
        "whatsapp_audio_message"
    ]
    
    for test in whatsapp_tests:
        test_whatsapp_message(test)
        print()
    
    # Test payment webhooks
    payment_tests = [
        "payment_success_webhook",
        "payment_failed_webhook"
    ]
    
    for test in payment_tests:
        test_payment_webhook(test)
        print()

def show_help():
    """Show help information."""
    print("""
🤖 Social Commerce AI Agent - Local Test Runner

Usage: python run_local.py [command] [options]

Commands:
  health                    - Test health check endpoint
  test <payload_name>       - Test specific WhatsApp message
  payment <payload_name>    - Test payment webhook
  all                       - Run all tests
  help                      - Show this help

Available WhatsApp Test Payloads:
  - whatsapp_text_message          (English text message)
  - whatsapp_vendor_code_message   (Vendor code purchase)
  - whatsapp_tamil_message         (Tamil language message)
  - whatsapp_image_message         (Image with caption)
  - whatsapp_audio_message         (Voice message)
  - address_collection_message     (Address collection flow)

Available Payment Test Payloads:
  - payment_success_webhook        (Successful payment)
  - payment_failed_webhook         (Failed payment)

Examples:
  python run_local.py health
  python run_local.py test whatsapp_text_message
  python run_local.py payment payment_success_webhook
  python run_local.py all

Prerequisites:
  1. Start the server: python main.py
  2. Configure .env file with required API keys
  3. Ensure sample_payloads.json exists
    """)

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "help":
        show_help()
    elif command == "health":
        test_health_check()
    elif command == "test":
        if len(sys.argv) < 3:
            print("❌ Please specify a payload name")
            print("   Usage: python run_local.py test <payload_name>")
            return
        test_whatsapp_message(sys.argv[2])
    elif command == "payment":
        if len(sys.argv) < 3:
            print("❌ Please specify a payload name")
            print("   Usage: python run_local.py payment <payload_name>")
            return
        test_payment_webhook(sys.argv[2])
    elif command == "all":
        run_all_tests()
    else:
        print(f"❌ Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    main()
