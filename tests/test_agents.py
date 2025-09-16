#!/usr/bin/env python3
"""Test individual agents without server"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agents.product_extractor import ProductExtractorAgent
from agents.inventory_matcher import InventoryMatcherAgent
from agents.response_generator import ResponseGeneratorAgent

async def test_agents():
    print("🧪 Testing Social Commerce AI Agents\n")
    
    # Test message
    message_data = {
        "customer_phone": "919876543210",
        "message": "V001 buy pannanum",
        "type": "text"
    }
    
    # Test Input Agent
    print("1️⃣ Testing Input Agent...")
    extractor = ProductExtractorAgent()
    extracted = await extractor.extract_product_info(message_data)
    print(f"Extracted: {extracted}\n")
    
    # Test Inventory Agent
    print("2️⃣ Testing Inventory Agent...")
    matcher = InventoryMatcherAgent()
    inventory_result = await matcher.match_inventory(extracted)
    print(f"Inventory Result: {inventory_result}\n")
    
    # Test Response Agent
    print("3️⃣ Testing Response Agent...")
    responder = ResponseGeneratorAgent()
    response = await responder.generate_response(extracted, inventory_result, {})
    print(f"Response: {response}\n")
    
    print("✅ Agent testing complete!")

if __name__ == "__main__":
    asyncio.run(test_agents())
