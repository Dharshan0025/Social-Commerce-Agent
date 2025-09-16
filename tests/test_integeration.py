import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from agents.coordinator import CoordinatorAgent

class TestIntegrationFlow:
    """Integration tests for the complete message processing flow."""
    
    @pytest.fixture
    def coordinator(self):
        return CoordinatorAgent()
    
    @pytest.fixture
    def sample_whatsapp_payload(self):
        """Sample WhatsApp webhook payload."""
        return {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "from": "919876543210",
                            "id": "wamid.test123",
                            "timestamp": "1694876543",
                            "type": "text",
                            "text": {
                                "body": "I want a blue shirt in medium size"
                            }
                        }],
                        "contacts": [{
                            "profile": {
                                "name": "John Doe"
                            }
                        }]
                    }
                }]
            }]
        }
    
    @pytest.fixture
    def sample_payment_payload(self):
        """Sample payment webhook payload."""
        return {
            "status": "success",
            "payment_id": "pay_test123",
            "customer_phone": "919876543210",
            "amount": "599.00",
            "currency": "INR"
        }
    
    @pytest.mark.asyncio
    async def test_complete_message_flow_exact_match(self, coordinator, sample_whatsapp_payload):
        """Test complete flow with exact product match."""
        
        # Mock product extraction
        with patch.object(coordinator.product_extractor, 'extract_product_info') as mock_extract:
            mock_extract.return_value = {
                "vendor_code": "VS001",
                "product_name": "shirt",
                "brand": "Brand A",
                "type": "shirt",
                "style": "",
                "color": "blue",
                "size": "medium",
                "quantity": 1,
                "action": "browse",
                "language_detected": "english",
                "confidence": "high"
            }
            
            # Mock inventory matching
            with patch.object(coordinator.inventory_matcher, 'match_inventory') as mock_match:
                mock_match.return_value = {
                    "exact_match": {
                        "found": True,
                        "product": {
                            "Vendor_Code": "VS001",
                            "Product_Name": "Blue Cotton Shirt",
                            "Brand": "Brand A",
                            "Sale_Price": "599",
                            "Qty_On_Hand": 15,
                            "Payment_Link": "https://pay.example.com/VS001"
                        }
                    },
                    "similar_matches": [],
                    "recommendations": ["Perfect match found!"],
                    "stock_status": "in_stock"
                }
                
                # Mock response generation
                with patch.object(coordinator.response_generator, 'generate_response') as mock_response:
                    mock_response.return_value = "Great choice! We have the Blue Cotton Shirt in medium size for ₹599. Ready to order? 🛒"
                    
                    # Mock WhatsApp sending
                    with patch.object(coordinator, '_send_whatsapp_message') as mock_send:
                        mock_send.return_value = True
                        
                        # Mock logging
                        with patch.object(coordinator.logger_agent, 'log_customer_interaction') as mock_log:
                            mock_log.return_value = True
                            
                            result = await coordinator.process_whatsapp_message(sample_whatsapp_payload)
                            
                            assert result["status"] == "processed"
                            assert result["customer_phone"] == "919876543210"
                            assert "Blue Cotton Shirt" in str(result["inventory_result"])
                            assert "₹599" in result["response_sent"]
    
    @pytest.mark.asyncio
    async def test_complete_message_flow_no_match(self, coordinator, sample_whatsapp_payload):
        """Test complete flow with no product match."""
        
        # Modify payload for a product that doesn't exist
        sample_whatsapp_payload["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"] = "I want a purple unicorn"
        
        with patch.object(coordinator.product_extractor, 'extract_product_info') as mock_extract:
            mock_extract.return_value = {
                "vendor_code": "",
                "product_name": "purple unicorn",
                "brand": "",
                "type": "",
                "style": "",
                "color": "purple",
                "size": "",
                "quantity": 1,
                "action": "browse",
                "language_detected": "english",
                "confidence": "medium"
            }
            
            with patch.object(coordinator.inventory_matcher, 'match_inventory') as mock_match:
                mock_match.return_value = {
                    "exact_match": {"found": False, "product": None},
                    "similar_matches": [],
                    "recommendations": ["Sorry, we couldn't find 'purple unicorn' in our inventory."],
                    "stock_status": "unknown"
                }
                
                with patch.object(coordinator.response_generator, 'generate_response') as mock_response:
                    mock_response.return_value = "Sorry, we couldn't find 'purple unicorn' in our inventory. Please check our catalog or try a different search."
                    
                    with patch.object(coordinator, '_send_whatsapp_message') as mock_send:
                        mock_send.return_value = True
                        
                        with patch.object(coordinator.logger_agent, 'log_customer_interaction') as mock_log:
                            mock_log.return_value = True
                            
                            result = await coordinator.process_whatsapp_message(sample_whatsapp_payload)
                            
                            assert result["status"] == "processed"
                            assert not result["inventory_result"]["exact_match"]["found"]
                            assert "couldn't find" in result["response_sent"]
    
    @pytest.mark.asyncio
    async def test_payment_webhook_success(self, coordinator, sample_payment_payload):
        """Test successful payment webhook processing."""
        
        with patch.object(coordinator.logger_agent, 'log_payment_event') as mock_log:
            mock_log.return_value = True
            
            with patch.object(coordinator, '_send_whatsapp_message') as mock_send:
                mock_send.return_value = True
                
                result = await coordinator.process_payment_webhook(sample_payment_payload)
                
                assert result["status"] == "processed"
                assert result["payment_id"] == "pay_test123"
                assert "successful" in result["response_sent"]
    
    @pytest.mark.asyncio
    async def test_purchase_flow_with_address_collection(self, coordinator, sample_whatsapp_payload):
        """Test purchase flow that requires address collection."""
        
        # Modify payload for purchase action
        sample_whatsapp_payload["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"] = "VS001 buy pannanum"
        
        with patch.object(coordinator.product_extractor, 'extract_product_info') as mock_extract:
            mock_extract.return_value = {
                "vendor_code": "VS001",
                "product_name": "shirt",
                "brand": "",
                "type": "shirt",
                "style": "",
                "color": "",
                "size": "",
                "quantity": 1,
                "action": "buy",
                "language_detected": "thanglish",
                "confidence": "high"
            }
            
            with patch.object(coordinator.inventory_matcher, 'match_inventory') as mock_match:
                mock_match.return_value = {
                    "exact_match": {
                        "found": True,
                        "product": {
                            "Vendor_Code": "VS001",
                            "Product_Name": "Blue Cotton Shirt",
                            "Sale_Price": "599",
                            "Qty_On_Hand": 15,
                            "Payment_Link": "https://pay.example.com/VS001"
                        }
                    },
                    "similar_matches": [],
                    "recommendations": ["Perfect match found!"],
                    "stock_status": "in_stock"
                }
                
                with patch.object(coordinator.response_generator, 'generate_response') as mock_response:
                    mock_response.return_value = "Great! Blue Cotton Shirt for ₹599."
                    
                    with patch.object(coordinator.response_generator, 'generate_address_request') as mock_address:
                        mock_address.return_value = "Please share your delivery address to complete the order. 📍"
                        
                        with patch.object(coordinator, '_send_whatsapp_message') as mock_send:
                            mock_send.return_value = True
                            
                            with patch.object(coordinator.logger_agent, 'log_customer_interaction') as mock_log:
                                mock_log.return_value = True
                                
                                result = await coordinator.process_whatsapp_message(sample_whatsapp_payload)
                                
                                assert result["status"] == "processed"
                                assert "address" in result["response_sent"].lower()
                                assert "919876543210" in coordinator.conversation_state
                                assert coordinator.conversation_state["919876543210"]["awaiting_address"] == True
    
    @pytest.mark.asyncio
    async def test_multilingual_response(self, coordinator):
        """Test multilingual response generation."""
        
        # Tamil message payload
        tamil_payload = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "from": "919876543210",
                            "id": "wamid.test123",
                            "timestamp": "1694876543",
                            "type": "text",
                            "text": {
                                "body": "நீல நிற சட்டை வேணும்"
                            }
                        }],
                        "contacts": [{
                            "profile": {
                                "name": "Tamil User"
                            }
                        }]
                    }
                }]
            }]
        }
        
        with patch.object(coordinator.product_extractor, 'extract_product_info') as mock_extract:
            mock_extract.return_value = {
                "vendor_code": "",
                "product_name": "shirt",
                "brand": "",
                "type": "shirt",
                "style": "",
                "color": "blue",
                "size": "",
                "quantity": 1,
                "action": "browse",
                "language_detected": "tamil",
                "confidence": "high"
            }
            
            with patch.object(coordinator.inventory_matcher, 'match_inventory') as mock_match:
                mock_match.return_value = {
                    "exact_match": {"found": False, "product": None},
                    "similar_matches": [{
                        "product": {
                            "Product_Name": "Blue Cotton Shirt",
                            "Sale_Price": "599"
                        },
                        "match_score": 75,
                        "match_reasons": ["Color match"]
                    }],
                    "recommendations": ["Similar blue shirts available"],
                    "stock_status": "in_stock"
                }
                
                with patch.object(coordinator.response_generator, 'generate_response') as mock_response:
                    mock_response.return_value = "நீல நிற சட்டை கிடைக்கிறது! Blue Cotton Shirt ₹599க்கு. வேணுமா?"
                    
                    with patch.object(coordinator, '_send_whatsapp_message') as mock_send:
                        mock_send.return_value = True
                        
                        with patch.object(coordinator.logger_agent, 'log_customer_interaction') as mock_log:
                            mock_log.return_value = True
                            
                            result = await coordinator.process_whatsapp_message(tamil_payload)
                            
                            assert result["status"] == "processed"
                            assert result["extracted_info"]["language_detected"] == "tamil"
