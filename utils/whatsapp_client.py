import logging
import httpx
from typing import Dict, Any, Optional
from config import settings

logger = logging.getLogger(__name__)

class WhatsAppClient:
    """WhatsApp Business API client for sending messages."""
    
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v18.0"
        self.phone_number_id = settings.whatsapp_phone_number_id
        self.access_token = settings.whatsapp_access_token
        
    def _format_phone_number(self, phone_number: str) -> str:
        """Format phone number for WhatsApp API."""
        # Remove any existing + or 00 prefix
        clean_number = phone_number.lstrip('+').lstrip('00')
        
        # Add + prefix if not present
        if not phone_number.startswith('+'):
            return f"+{clean_number}"
        return phone_number
    
    async def send_text_message(self, to: str, message: str) -> Dict[str, Any]:
        """Send a text message via WhatsApp Business API."""
        try:
            if not self.access_token or not self.phone_number_id:
                logger.error("WhatsApp credentials not configured")
                return {"success": False, "error": "WhatsApp credentials not configured"}
            
            # Format phone number correctly
            formatted_to = self._format_phone_number(to)
            logger.info(f"Sending message to {to} (formatted as {formatted_to})")
            
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "to": formatted_to,
                "type": "text",
                "text": {
                    "body": message
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"WhatsApp message sent successfully to {formatted_to}")
                    return {"success": True, "message_id": result.get("messages", [{}])[0].get("id")}
                else:
                    error_detail = response.text
                    logger.error(f"Failed to send WhatsApp message: {response.status_code} - {error_detail}")
                    return {"success": False, "error": f"API error: {response.status_code}", "details": error_detail}
                    
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def send_template_message(self, to: str, template_name: str, language: str = "en", components: Optional[list] = None) -> Dict[str, Any]:
        """Send a template message via WhatsApp Business API."""
        try:
            if not self.access_token or not self.phone_number_id:
                logger.error("WhatsApp credentials not configured")
                return {"success": False, "error": "WhatsApp credentials not configured"}
            
            # Format phone number correctly
            formatted_to = self._format_phone_number(to)
            logger.info(f"Sending template message to {to} (formatted as {formatted_to})")
            
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "to": formatted_to,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": language
                    }
                }
            }
            
            if components:
                payload["template"]["components"] = components
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"WhatsApp template message sent successfully to {to}")
                    return {"success": True, "message_id": result.get("messages", [{}])[0].get("id")}
                else:
                    error_detail = response.text
                    logger.error(f"Failed to send WhatsApp template message: {response.status_code} - {error_detail}")
                    return {"success": False, "error": f"API error: {response.status_code}", "details": error_detail}
                    
        except Exception as e:
            logger.error(f"Error sending WhatsApp template message: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def download_media(self, media_id: str) -> Optional[bytes]:
        """Download media from WhatsApp."""
        try:
            if not self.access_token:
                logger.error("WhatsApp access token not configured")
                return None
            
            # First get media URL
            url = f"{self.base_url}/{media_id}"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    media_info = response.json()
                    media_url = media_info.get("url")
                    
                    if media_url:
                        # Download the actual media
                        media_response = await client.get(media_url, headers=headers)
                        if media_response.status_code == 200:
                            return media_response.content
                
                logger.error(f"Failed to download media: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error downloading media: {str(e)}")
            return None

# Global instance
whatsapp_client = WhatsAppClient()
