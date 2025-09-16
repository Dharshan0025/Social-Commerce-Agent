import logging
from typing import Dict, Any, Optional
import json
from datetime import datetime

from agents.product_extractor import ProductExtractorAgent
from agents.inventory_matcher import InventoryMatcherAgent
from agents.response_generator import ResponseGeneratorAgent
from agents.logger_agent import LoggerAgent
from utils.huggingface_media import media_processor
from utils.whatsapp_client import whatsapp_client
from config import settings

logger = logging.getLogger(__name__)

class CoordinatorAgent:
    """Coordinator Agent that orchestrates all agents in the pipeline."""
    
    def __init__(self):
        self.system_prompt = """You are the Coordinator. Orchestrate agents in order: Input Agent → Inventory Agent → Response Agent → Logger Agent. Handle low-confidence extractor outputs by asking for clarification. If payment confirmation webhook arrives, update order status and notify the customer. Always route only JSON between agents."""
        
        self.product_extractor = ProductExtractorAgent()
        self.inventory_matcher = InventoryMatcherAgent()
        self.response_generator = ResponseGeneratorAgent()
        self.logger_agent = LoggerAgent()
        
        # State management for multi-step conversations
        self.conversation_state = {}
    
    async def initialize(self):
        """Initialize the coordinator and all agents."""
        try:
            logger.info("Initializing Social Commerce AI Agent Coordinator")
            # Any initialization logic here
            return True
        except Exception as e:
            logger.error(f"Failed to initialize coordinator: {str(e)}")
            raise
    
    async def process_whatsapp_message(self, webhook_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming WhatsApp message through the agent pipeline."""
        try:
            # Extract message data from WhatsApp webhook
            message_data = await self._extract_whatsapp_message(webhook_payload)
            
            if not message_data:
                logger.warning("No valid message data found in webhook payload")
                return {"status": "ignored", "reason": "No valid message data"}
            
            customer_phone = message_data.get("customer_phone", "")
            
            # Check conversation state for multi-step flows
            conversation_context = self.conversation_state.get(customer_phone, {})
            
            # Handle address collection flow
            if conversation_context.get("awaiting_address"):
                return await self._handle_address_collection(message_data, conversation_context)
            
            # Step 1: Input Agent - Extract product information
            logger.info("Step 1: Input Agent - Extracting product information")
            extracted_info = await self.product_extractor.extract_product_info(message_data)
            
            # Check confidence level
            confidence = extracted_info.get("confidence", 0.0)
            if confidence < 0.8:
                logger.info(f"Low confidence extraction ({confidence}), asking for clarification")
                clarification_response = await self._generate_clarification_request(extracted_info)
                await self._send_whatsapp_message(customer_phone, clarification_response)
                return {
                    "status": "clarification_requested",
                    "customer_phone": customer_phone,
                    "extracted_info": extracted_info,
                    "response_sent": clarification_response
                }
            
            # Step 2: Inventory Agent - Match with inventory
            logger.info("Step 2: Inventory Agent - Matching with inventory")
            inventory_result = await self.inventory_matcher.match_inventory(extracted_info)
            
            # Step 3: Response Agent - Generate response
            logger.info("Step 3: Response Agent - Generating customer response")
            response_text = await self.response_generator.generate_response(
                extracted_info, inventory_result, conversation_context
            )
            
            # Step 4: Handle purchase flow if needed
            if extracted_info.get("action") == "buy" and inventory_result.get("chosen"):
                response_text = await self._handle_purchase_flow(
                    message_data, extracted_info, inventory_result, response_text
                )
            
            # Step 5: Send response
            await self._send_whatsapp_message(customer_phone, response_text)
            
            # Step 6: Logger Agent - Log interaction
            logger.info("Step 4: Logger Agent - Logging interaction")
            log_result = await self.logger_agent.log_customer_interaction(
                customer_data=message_data,
                extracted_info=extracted_info,
                inventory_result=inventory_result,
                response_sent=response_text
            )
            
            return {
                "status": "processed",
                "customer_phone": customer_phone,
                "extracted_info": extracted_info,
                "inventory_result": inventory_result,
                "response_sent": response_text,
                "log_result": log_result
            }
            
        except Exception as e:
            logger.error(f"Error processing WhatsApp message: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def process_payment_webhook(self, payment_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment webhook events."""
        try:
            logger.info("Processing payment webhook")
            
            # Extract payment information
            payment_status = payment_payload.get("status", "")
            customer_phone = payment_payload.get("customer_phone", "")
            payment_id = payment_payload.get("payment_id", "")
            amount = payment_payload.get("amount", "")
            
            # Log payment event
            log_result = await self.logger_agent.log_payment_event(payment_payload)
            
            # Generate appropriate response based on payment status
            if payment_status == "success":
                response = await self._handle_successful_payment(payment_payload)
            elif payment_status == "failed":
                response = await self._handle_failed_payment(payment_payload)
            else:
                response = await self._handle_pending_payment(payment_payload)
            
            # Send notification to customer
            if customer_phone and response:
                await self._send_whatsapp_message(customer_phone, response)
            
            return {
                "status": "processed",
                "payment_id": payment_id,
                "customer_phone": customer_phone,
                "response_sent": response,
                "log_result": log_result
            }
            
        except Exception as e:
            logger.error(f"Error processing payment webhook: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _extract_whatsapp_message(self, webhook_payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract message data from WhatsApp webhook payload."""
        try:
            # Navigate WhatsApp webhook structure
            entry = webhook_payload.get("entry", [])
            if not entry:
                return None
            
            changes = entry[0].get("changes", [])
            if not changes:
                return None
            
            value = changes[0].get("value", {})
            messages = value.get("messages", [])
            
            if not messages:
                return None
            
            message = messages[0]
            
            # Extract basic info
            customer_phone = message.get("from", "")
            message_id = message.get("id", "")
            timestamp = message.get("timestamp", "")
            
            # Extract message content based on type
            message_type = message.get("type", "text")
            message_data = {
                "customer_phone": customer_phone,
                "message_id": message_id,
                "timestamp": timestamp,
                "type": message_type
            }
            
            if message_type == "text":
                message_data["text"] = message.get("text", {}).get("body", "")
                message_data["message"] = message_data["text"]
            
            elif message_type == "image":
                image_info = message.get("image", {})
                media_id = image_info.get("id", "")
                caption = image_info.get("caption", "")
                
                # Download image data if media_id is available
                if media_id and settings.whatsapp_access_token:
                    image_data = await media_processor.download_media_from_whatsapp(
                        media_id, settings.whatsapp_access_token
                    )
                    message_data["image_data"] = image_data
                
                message_data["caption"] = caption
                message_data["message"] = caption or "Image received"
            
            elif message_type == "audio":
                audio_info = message.get("audio", {})
                media_id = audio_info.get("id", "")
                
                # Download audio data if media_id is available
                if media_id and settings.whatsapp_access_token:
                    audio_data = await media_processor.download_media_from_whatsapp(
                        media_id, settings.whatsapp_access_token
                    )
                    message_data["audio_data"] = audio_data
                
                message_data["message"] = "Audio message received"
            
            # Try to get contact info
            contacts = value.get("contacts", [])
            if contacts:
                contact = contacts[0]
                profile = contact.get("profile", {})
                message_data["name"] = profile.get("name", "")
            
            return message_data
            
        except Exception as e:
            logger.error(f"Error extracting WhatsApp message: {str(e)}")
            return None
    
    async def _generate_clarification_request(self, extracted_info: Dict[str, Any]) -> str:
        """Generate clarification request for low confidence extractions."""
        try:
            language = extracted_info.get("language", "en")
            
            if language in ["ta-en", "tanglish"]:
                return "Sorry da, didn't understand properly. Can you share vendor code or send a clear picture?"
            else:
                return "Can you share vendor code or send a clear picture?"
                
        except Exception as e:
            logger.error(f"Error generating clarification request: {str(e)}")
            return "Can you provide more details about the product you're looking for?"
    
    async def _handle_purchase_flow(
        self, 
        message_data: Dict[str, Any], 
        extracted_info: Dict[str, Any], 
        inventory_result: Dict[str, Any],
        current_response: str
    ) -> str:
        """Handle purchase flow - ask for address if needed."""
        try:
            customer_phone = message_data.get("customer_phone", "")
            chosen = inventory_result.get("chosen")
            
            if not chosen:
                return current_response
            
            language = extracted_info.get("language", "en")
            
            # Set conversation state to await address
            self.conversation_state[customer_phone] = {
                "awaiting_address": True,
                "product": chosen,
                "language": language,
                "timestamp": datetime.now().isoformat()
            }
            
            # Generate address request
            address_request = await self.response_generator._generate_address_request(
                language, chosen
            )
            
            return f"{current_response}\n\n{address_request}"
            
        except Exception as e:
            logger.error(f"Error in purchase flow: {str(e)}")
            return current_response
    
    async def _handle_address_collection(
        self, 
        message_data: Dict[str, Any], 
        conversation_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle address collection step."""
        try:
            customer_phone = message_data.get("customer_phone", "")
            address = message_data.get("message", "")
            product = conversation_context.get("product", {})
            language = conversation_context.get("language", "english")
            
            # Clear conversation state
            if customer_phone in self.conversation_state:
                del self.conversation_state[customer_phone]
            
            # Generate order confirmation
            if language in ["ta-en", "tanglish"]:
                order_confirmation = f"Super! Order confirmed da! {product.get('description', 'Product')} will be delivered to: {address}"
            else:
                order_confirmation = f"Order confirmed! {product.get('description', 'Product')} will be delivered to: {address}"
            
            # Send confirmation
            await self._send_whatsapp_message(customer_phone, order_confirmation)
            
            # Log order
            await self.logger_agent.log_order_update(customer_phone, "confirmed")
            
            return {
                "status": "order_confirmed",
                "customer_phone": customer_phone,
                "address": address,
                "product": product,
                "response_sent": order_confirmation
            }
            
        except Exception as e:
            logger.error(f"Error handling address collection: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _handle_successful_payment(self, payment_payload: Dict[str, Any]) -> str:
        """Handle successful payment notification."""
        try:
            # Generate success message (could be multilingual based on customer data)
            return "🎉 Payment successful! Your order is confirmed and will be processed shortly. Thank you for shopping with us!"
            
        except Exception as e:
            logger.error(f"Error handling successful payment: {str(e)}")
            return "Payment received! Thank you for your order."
    
    async def _handle_failed_payment(self, payment_payload: Dict[str, Any]) -> str:
        """Handle failed payment notification."""
        try:
            return "❌ Payment failed. Please try again or contact support. Your order is still pending."
            
        except Exception as e:
            logger.error(f"Error handling failed payment: {str(e)}")
            return "Payment failed. Please try again."
    
    async def _handle_pending_payment(self, payment_payload: Dict[str, Any]) -> str:
        """Handle pending payment notification."""
        try:
            return "⏳ Payment is being processed. We'll notify you once it's confirmed."
            
        except Exception as e:
            logger.error(f"Error handling pending payment: {str(e)}")
            return "Payment is being processed."
    
    async def _send_whatsapp_message(self, customer_phone: str, message: str) -> bool:
        """Send message via WhatsApp Business API."""
        try:
            logger.info(f"Sending WhatsApp message to {customer_phone}: {message}")
            
            # Use the WhatsApp client to send the message
            result = await whatsapp_client.send_text_message(customer_phone, message)
            
            if result.get("success"):
                logger.info(f"WhatsApp message sent successfully. Message ID: {result.get('message_id')}")
                return True
            else:
                logger.error(f"Failed to send WhatsApp message: {result.get('error')}")
                return False
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {str(e)}")
            return False
