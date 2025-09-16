import logging
from typing import Dict, Any, List
from utils.groq_client import groq_client

logger = logging.getLogger(__name__)

class ResponseGeneratorAgent:
    """Sales Response Agent responsible for generating WhatsApp-friendly responses."""
    
    def __init__(self):
        self.system_prompt = """You are the Sales Response Agent for WhatsApp. Input: JSON containing match result and the original input JSON. Your job: craft a WhatsApp-friendly short reply in the same language/style as the user (if language indicates 'ta-en' produce Tanglish). 

Rules:
- If exact match: produce reply in this format:
✅ Product: [Type] - [Brand]
🎨 Color: [Color] | Sizes: [Sizes comma-separated]
💰 Price: ₹[sale_price]
📦 Stock: [qty_on_hand] pieces
🔗 Order: [payment_link]

- If partial match: list up to 3 candidates with vendor_codes and short prompt: "Which one you mean? Reply with vendor code like V001".

- If not found: ask a clarifying question: "Can you share vendor code or a clearer picture?"

- If action=buy and address/name not yet collected: ask for Name and Delivery Address in short form.

Return ONLY the reply string as {"reply":"..."}."""

    async def generate_response(
        self, 
        extracted_info: Dict[str, Any], 
        inventory_result: Dict[str, Any],
        customer_context: Dict[str, Any] = None
    ) -> str:
        """Generate customer response based on extraction and inventory results."""
        try:
            language = extracted_info.get("language", "en")
            action = extracted_info.get("action", "unknown")
            status = inventory_result.get("status", "not_found")
            matches = inventory_result.get("matches", [])
            chosen = inventory_result.get("chosen")
            
            # Check if we need to collect address for buy action
            if action == "buy" and chosen and customer_context:
                if not customer_context.get("name") or not customer_context.get("address"):
                    return await self._generate_address_request(language, chosen)
            
            # Build context for response generation
            context = {
                "language": language,
                "action": action,
                "status": status,
                "matches": matches,
                "chosen": chosen,
                "extracted_info": extracted_info
            }
            
            if status == "exact_match" and chosen:
                return await self._generate_exact_match_response(context)
            elif status == "partial_match" and matches:
                return await self._generate_partial_match_response(context)
            else:
                return await self._generate_not_found_response(context)
                
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "Thank you for your message! We're processing your request and will get back to you shortly. 😊"
    
    async def _generate_exact_match_response(self, context: Dict[str, Any]) -> str:
        """Generate response for exact match."""
        try:
            chosen = context["chosen"]
            language = context["language"]
            
            # Format the exact match response
            product_type = chosen.get("type", "Product")
            brand = chosen.get("brand", "")
            color = chosen.get("color", "")
            sizes = ", ".join(chosen.get("sizes_available", []))
            price = chosen.get("sale_price", "")
            stock = chosen.get("qty_on_hand", 0)
            payment_link = chosen.get("payment_link", "")
            
            if language in ["ta-en", "tanglish"]:
                response = f"✅ Product: {product_type} - {brand}\n"
                response += f"🎨 Color: {color} | Sizes: {sizes}\n"
                response += f"💰 Price: ₹{price}\n"
                response += f"📦 Stock: {stock} pieces\n"
                if payment_link:
                    response += f"🔗 Order: {payment_link}"
                else:
                    response += "Ready to order ah? Send your name and address!"
            else:
                response = f"✅ Product: {product_type} - {brand}\n"
                response += f"🎨 Color: {color} | Sizes: {sizes}\n"
                response += f"💰 Price: ₹{price}\n"
                response += f"📦 Stock: {stock} pieces\n"
                if payment_link:
                    response += f"🔗 Order: {payment_link}"
                else:
                    response += "Ready to order? Send your name and address!"
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating exact match response: {str(e)}")
            return "Great! We found your product. Please contact us for more details."
    
    async def _generate_partial_match_response(self, context: Dict[str, Any]) -> str:
        """Generate response for partial matches."""
        try:
            matches = context["matches"]
            language = context["language"]
            
            if language in ["ta-en", "tanglish"]:
                response = "Found some options da! Which one you mean?\n\n"
            else:
                response = "Found some options! Which one you mean?\n\n"
            
            for i, match in enumerate(matches[:3], 1):
                vendor_code = match.get("vendor_code", "")
                description = match.get("description", "")
                price = match.get("sale_price", "")
                response += f"{i}. {vendor_code} - {description} - ₹{price}\n"
            
            if language in ["ta-en", "tanglish"]:
                response += "\nReply with vendor code like V001 da!"
            else:
                response += "\nReply with vendor code like V001!"
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating partial match response: {str(e)}")
            return "Found some similar products. Can you be more specific?"
    
    async def _generate_not_found_response(self, context: Dict[str, Any]) -> str:
        """Generate response when no matches found."""
        try:
            language = context["language"]
            
            if language in ["ta-en", "tanglish"]:
                return "Sorry da, couldn't find that product. Can you share vendor code or a clearer picture?"
            else:
                return "Can you share vendor code or a clearer picture?"
                
        except Exception as e:
            logger.error(f"Error generating not found response: {str(e)}")
            return "Sorry, couldn't find that product. Can you provide more details?"
    
    async def _generate_address_request(self, language: str, product: Dict[str, Any]) -> str:
        """Generate address collection request."""
        try:
            product_name = product.get("description", "product")
            
            if language in ["ta-en", "tanglish"]:
                return f"Super! {product_name} ready da! Send your Name and Delivery Address to confirm order."
            else:
                return f"Great! {product_name} is ready! Send your Name and Delivery Address to confirm order."
                
        except Exception as e:
            logger.error(f"Error generating address request: {str(e)}")
            return "Please share your Name and Delivery Address to complete the order."