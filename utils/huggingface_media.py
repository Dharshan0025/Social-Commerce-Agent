import logging
import requests
from typing import Optional, Dict, Any
import base64
from io import BytesIO
try:
    from PIL import Image
except ImportError:
    Image = None
from config import settings

logger = logging.getLogger(__name__)

class HuggingFaceMediaProcessor:
    """Processor for handling media files using HuggingFace Inference API."""
    
    def __init__(self):
        self.api_token = settings.huggingface_api_token
        self.headers = {"Authorization": f"Bearer {self.api_token}"} if self.api_token else {}
        
        # Model endpoints
        self.image_caption_model = "Salesforce/blip-image-captioning-large"
        self.speech_to_text_model = "openai/whisper-large-v3"
    
    async def process_image(self, image_data: bytes) -> Optional[str]:
        """Process image and return caption/description."""
        if not self.api_token:
            logger.warning("HuggingFace API token not configured, skipping image processing")
            return None
        
        try:
            if Image is None:
                logger.warning("PIL not available, skipping image processing")
                return None
                
            # Validate and resize image if needed
            image = Image.open(BytesIO(image_data))
            
            # Resize if too large (max 1024x1024)
            if image.width > 1024 or image.height > 1024:
                image.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
            
            # Convert to bytes
            img_buffer = BytesIO()
            image.save(img_buffer, format='JPEG', quality=85)
            processed_image_data = img_buffer.getvalue()
            
            # Make API request
            api_url = f"https://api-inference.huggingface.co/models/{self.image_caption_model}"
            
            response = requests.post(
                api_url,
                headers=self.headers,
                data=processed_image_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    caption = result[0].get("generated_text", "")
                    logger.info(f"Generated image caption: {caption}")
                    return caption
                else:
                    logger.warning("Unexpected response format from image captioning API")
                    return None
            else:
                logger.error(f"Image captioning API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return None
    
    async def process_audio(self, audio_data: bytes, content_type: str = "audio/ogg") -> Optional[str]:
        """Process audio and return transcribed text."""
        if not self.api_token:
            logger.warning("HuggingFace API token not configured, skipping audio processing")
            return None
        
        try:
            # Make API request
            api_url = f"https://api-inference.huggingface.co/models/{self.speech_to_text_model}"
            
            response = requests.post(
                api_url,
                headers=self.headers,
                data=audio_data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                transcription = result.get("text", "")
                logger.info(f"Generated audio transcription: {transcription}")
                return transcription
            else:
                logger.error(f"Speech-to-text API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}")
            return None
    
    async def download_media_from_whatsapp(self, media_id: str, access_token: str) -> Optional[bytes]:
        """Download media file from WhatsApp API."""
        try:
            # Get media URL
            url = f"https://graph.facebook.com/v18.0/{media_id}"
            headers = {"Authorization": f"Bearer {access_token}"}
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                media_info = response.json()
                media_url = media_info.get("url")
                
                if media_url:
                    # Download the actual media file
                    media_response = requests.get(media_url, headers=headers, timeout=60)
                    
                    if media_response.status_code == 200:
                        return media_response.content
                    else:
                        logger.error(f"Failed to download media: {media_response.status_code}")
                        return None
                else:
                    logger.error("No media URL found in response")
                    return None
            else:
                logger.error(f"Failed to get media info: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error downloading media from WhatsApp: {str(e)}")
            return None

# Global instance
media_processor = HuggingFaceMediaProcessor()
