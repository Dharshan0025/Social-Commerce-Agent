import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from api import app

class TestAPI:
    """Test cases for FastAPI endpoints."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Social Commerce AI Agent"
    
    def test_whatsapp_webhook_verification(self, client):
        """Test WhatsApp webhook verification."""
        params = {
            "hub.mode": "subscribe",
            "hub.challenge": "12345",
            "hub.verify_token": "test_verify_token"
        }
        
        with patch('config.settings.whatsapp_verify_token', "test_verify_token"):
            response = client.get("/webhook/whatsapp", params=params)
            assert response.status_code == 200
            assert response.text == "12345"
    
    def test_whatsapp_webhook_verification_failed(self, client):
        """Test WhatsApp webhook verification failure."""
        params = {
            "hub.mode": "subscribe",
            "hub.challenge": "12345",
            "hub.verify_token": "wrong_token"
        }
        
        with patch('config.settings.whatsapp_verify_token', "correct_token"):
            response = client.get("/webhook/whatsapp", params=params)
            assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_whatsapp_webhook_message_processing(self, client):
        """Test WhatsApp message processing."""
        payload = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "from": "919876543210",
                            "id": "wamid.test123",
                            "timestamp": "1694876543",
                            "type": "text",
                            "text": {
                                "body": "I want a blue shirt"
                            }
                        }]
                    }
                }]
            }]
        }
        
        with patch('agents.coordinator.CoordinatorAgent.process_whatsapp_message') as mock_process:
            mock_process.return_value = {
                "status": "processed",
                "customer_phone": "919876543210",
                "response_sent": "Great choice! We have blue shirts available."
            }
            
            response = client.post("/webhook/whatsapp", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
    
    def test_whatsapp_webhook_invalid_json(self, client):
        """Test WhatsApp webhook with invalid JSON."""
        response = client.post(
            "/webhook/whatsapp",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_payment_webhook_processing(self, client):
        """Test payment webhook processing."""
        payload = {
            "status": "success",
            "payment_id": "pay_test123",
            "customer_phone": "919876543210",
            "amount": "599.00"
        }
        
        with patch('agents.coordinator.CoordinatorAgent.process_payment_webhook') as mock_process:
            mock_process.return_value = {
                "status": "processed",
                "payment_id": "pay_test123",
                "response_sent": "Payment successful!"
            }
            
            response = client.post("/webhook/payment", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
    
    def test_test_endpoint_in_debug_mode(self, client):
        """Test the test endpoint when debug is enabled."""
        payload = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "from": "919876543210",
                            "type": "text",
                            "text": {"body": "test message"}
                        }]
                    }
                }]
            }]
        }
        
        with patch('config.settings.debug', True):
            with patch('agents.coordinator.CoordinatorAgent.process_whatsapp_message') as mock_process:
                mock_process.return_value = {"status": "processed"}
                
                response = client.post("/test/message", json=payload)
                assert response.status_code == 200
    
    def test_test_endpoint_in_production_mode(self, client):
        """Test the test endpoint when debug is disabled."""
        with patch('config.settings.debug', False):
            response = client.post("/test/message", json={})
            assert response.status_code == 404
