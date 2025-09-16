import logging
import json
from typing import Dict, Any, Optional
from utils.groq_client import groq_client
from utils.huggingface_media import media_processor
from config import settings

logger = logging.getLogger(__name__)

class ProductExtractorAgent:
    """Input Agent responsible for extracting product information from customer messages."""
    
    def __init__(self):
        self.system_prompt = """You are the Input Agent. Purpose: from a single incoming customer message (text OR an image caption OR transcribed audio) produce a strict JSON object with these fields: vendor_code, product_name, brand, type, style, color, size, qty, action, language, confidence. 

Rules:
- If the user explicitly provides vendor_code, set vendor_code and leave other fields blank if unknown.
- action must be one of: check_price, check_availability, buy, delivery_info, unknown.
- language: detect language or mixed-language (e.g., 'ta-en' for Tanglish).
- confidence: a numeric 0–1 confidence in extraction.
- Output ONLY JSON — no additional text.

Example output:
{"vendor_code":"V001","product_name":"Polo Shirt","brand":"Zara","type":"Shirt","color":"Blue","size":"L","qty":1,"action":"buy","language":"ta-en","confidence":0.93}

If uncertain, include partial fields and confidence < 0.8."""

    async def extract_product_info(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract product information from customer message."""
        try:
            message_text = ""
            message_type = message_data.get("type", "text")
            
            if message_type == "text":
                message_text = message_data.get("text", "")
            
            elif message_type == "image":
                # Process image if available
                image_data = message_data.get("image_data")
                if image_data:
                    caption = await media_processor.process_image(image_data)
                    if caption:
                        message_text = f"Image shows: {caption}"
                    else:
                        message_text = "Image received but could not process"
                else:
                    message_text = "Image received but no data available"
            
            elif message_type == "audio":
                # Process audio if available
                audio_data = message_data.get("audio_data")
                if audio_data:
                    transcription = await media_processor.process_audio(audio_data)
                    if transcription:
                        message_text = transcription
                    else:
                        message_text = "Audio received but could not transcribe"
                else:
                    message_text = "Audio received but no data available"
            
            if not message_text:
                return {
                    "vendor_code": "",
                    "product_name": "",
                    "brand": "",
                    "type": "",
                    "style": "",
                    "color": "",
                    "size": "",
                    "qty": 1,
                    "action": "unknown",
                    "language": "unknown",
                    "confidence": 0.0
                }
            
            # Generate extraction using Groq
            prompt = f"Extract product information from this customer message: '{message_text}'"
            
            response = await groq_client.generate_structured_completion(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.3
            )
            
            # Parse JSON response
            try:
                extracted_info = json.loads(response.strip())
                logger.info(f"Extracted product info: {extracted_info}")
                return extracted_info
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON response: {response}")
                # Return default structure
                return {
                    "vendor_code": "",
                    "product_name": message_text[:50],
                    "brand": "",
                    "type": "",
                    "style": "",
                    "color": "",
                    "size": "",
                    "qty": 1,
                    "action": "unknown",
                    "language": "unknown",
                    "confidence": 0.3
                }
                
        except Exception as e:
            logger.error(f"Error in product extraction: {str(e)}")
            return {
                "vendor_code": "",
                "product_name": "",
                "brand": "",
                "type": "",
                "style": "",
                "color": "",
                "size": "",
                "qty": 1,
                "action": "unknown",
                "language": "unknown",
                "confidence": 0.0
            }