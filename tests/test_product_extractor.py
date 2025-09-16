import pytest
import json
from unittest.mock import AsyncMock, patch
from agents.product_extractor import ProductExtractorAgent

class TestProductExtractorAgent:
    """Test cases for ProductExtractorAgent."""
    
    @pytest.fixture
    def agent(self):
        return ProductExtractorAgent()
    
    @pytest.mark.asyncio
    async def test_extract_text_message_english(self, agent):
        """Test extraction from English text message."""
        message_data = {
            "type": "text",
            "text": "I want a blue shirt in medium size"
        }
        
        with patch('utils.groq_client.groq_client.generate_structured_completion') as mock_groq:
            mock_groq.return_value = json.dumps({
                "vendor_code": "",
                "product_name": "shirt",
                "brand": "",
                "type": "shirt",
                "style": "",
                "color": "blue",
                "size": "medium",
                "quantity": 1,
                "action": "browse",
                "language_detected": "english",
                "confidence": "high"
            })
            
            result = await agent.extract_product_info(message_data)
            
            assert result["product_name"] == "shirt"
            assert result["color"] == "blue"
            assert result["size"] == "medium"
            assert result["language_detected"] == "english"
    
    @pytest.mark.asyncio
    async def test_extract_text_message_tamil(self, agent):
        """Test extraction from Tamil text message."""
        message_data = {
            "type": "text",
            "text": "நீல நிற சட்டை வேணும் medium size"
        }
        
        with patch('utils.groq_client.groq_client.generate_structured_completion') as mock_groq:
            mock_groq.return_value = json.dumps({
                "vendor_code": "",
                "product_name": "shirt",
                "brand": "",
                "type": "shirt",
                "style": "",
                "color": "blue",
                "size": "medium",
                "quantity": 1,
                "action": "browse",
                "language_detected": "tamil",
                "confidence": "high"
            })
            
            result = await agent.extract_product_info(message_data)
            
            assert result["language_detected"] == "tamil"
            assert result["product_name"] == "shirt"
    
    @pytest.mark.asyncio
    async def test_extract_vendor_code(self, agent):
        """Test extraction with vendor code."""
        message_data = {
            "type": "text",
            "text": "VS001 product buy pannanum"
        }
        
        with patch('utils.groq_client.groq_client.generate_structured_completion') as mock_groq:
            mock_groq.return_value = json.dumps({
                "vendor_code": "VS001",
                "product_name": "",
                "brand": "",
                "type": "",
                "style": "",
                "color": "",
                "size": "",
                "quantity": 1,
                "action": "buy",
                "language_detected": "thanglish",
                "confidence": "high"
            })
            
            result = await agent.extract_product_info(message_data)
            
            assert result["vendor_code"] == "VS001"
            assert result["action"] == "buy"
    
    @pytest.mark.asyncio
    async def test_extract_image_message(self, agent):
        """Test extraction from image message."""
        message_data = {
            "type": "image",
            "image_data": b"fake_image_data"
        }
        
        with patch('utils.huggingface_media.media_processor.process_image') as mock_image:
            mock_image.return_value = "A blue shirt on display"
            
            with patch('utils.groq_client.groq_client.generate_structured_completion') as mock_groq:
                mock_groq.return_value = json.dumps({
                    "vendor_code": "",
                    "product_name": "shirt",
                    "brand": "",
                    "type": "shirt",
                    "style": "",
                    "color": "blue",
                    "size": "",
                    "quantity": 1,
                    "action": "browse",
                    "language_detected": "english",
                    "confidence": "medium"
                })
                
                result = await agent.extract_product_info(message_data)
                
                assert result["product_name"] == "shirt"
                assert result["color"] == "blue"
    
    @pytest.mark.asyncio
    async def test_extract_audio_message(self, agent):
        """Test extraction from audio message."""
        message_data = {
            "type": "audio",
            "audio_data": b"fake_audio_data"
        }
        
        with patch('utils.huggingface_media.media_processor.process_audio') as mock_audio:
            mock_audio.return_value = "I want to buy a red saree"
            
            with patch('utils.groq_client.groq_client.generate_structured_completion') as mock_groq:
                mock_groq.return_value = json.dumps({
                    "vendor_code": "",
                    "product_name": "saree",
                    "brand": "",
                    "type": "saree",
                    "style": "",
                    "color": "red",
                    "size": "",
                    "quantity": 1,
                    "action": "buy",
                    "language_detected": "english",
                    "confidence": "high"
                })
                
                result = await agent.extract_product_info(message_data)
                
                assert result["product_name"] == "saree"
                assert result["color"] == "red"
                assert result["action"] == "buy"
    
    @pytest.mark.asyncio
    async def test_extract_empty_message(self, agent):
        """Test extraction from empty message."""
        message_data = {
            "type": "text",
            "text": ""
        }
        
        result = await agent.extract_product_info(message_data)
        
        assert result["confidence"] == "low"
        assert result["action"] == "inquiry"
    
    @pytest.mark.asyncio
    async def test_extract_json_parse_error(self, agent):
        """Test handling of JSON parse errors."""
        message_data = {
            "type": "text",
            "text": "blue shirt"
        }
        
        with patch('utils.groq_client.groq_client.generate_structured_completion') as mock_groq:
            mock_groq.return_value = "Invalid JSON response"
            
            result = await agent.extract_product_info(message_data)
            
            assert result["confidence"] == "low"
            assert "blue shirt" in result["product_name"]
