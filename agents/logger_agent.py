import logging
from typing import Dict, Any, List
from datetime import datetime
from utils.google_sheets import sheets_connector

logger = logging.getLogger(__name__)

class LoggerAgent:
    """Logger Agent responsible for logging customer interactions and orders to Google Sheets."""
    
    def __init__(self):
        self.system_prompt = """You are the Logger Agent. Input: structured data (customer metadata, chosen match, action, payment link, status). Append a row to the Leads/Orders sheet with fields: Timestamp, Customer Name, Phone, Address (if provided), Vendor Code, Product, Size, Qty, Price, Action, Payment Status, Order Status, Payment ID.

Return JSON: {"ok":true, "row_id": <index>} or {"ok":false,"error":"..."}."""
    
    async def log_customer_interaction(
        self,
        customer_data: Dict[str, Any],
        extracted_info: Dict[str, Any],
        inventory_result: Dict[str, Any],
        response_sent: str,
        interaction_type: str = "enquiry"
    ) -> Dict[str, Any]:
        """Log customer interaction to Google Sheets."""
        try:
            # Prepare log data
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Extract customer information
            customer_phone = customer_data.get("customer_phone", "")
            customer_name = customer_data.get("name", "")
            customer_address = customer_data.get("address", "")
            
            # Extract product information
            vendor_code = extracted_info.get("vendor_code", "")
            product_name = extracted_info.get("product_name", "")
            size = extracted_info.get("size", "")
            qty = extracted_info.get("qty", 1)
            action = extracted_info.get("action", "unknown")
            
            # Extract inventory information
            chosen = inventory_result.get("chosen")
            price = ""
            payment_link = ""
            
            if chosen:
                product_name = chosen.get("description", product_name)
                vendor_code = chosen.get("vendor_code", vendor_code)
                price = chosen.get("sale_price", "")
                payment_link = chosen.get("payment_link", "")
            
            # Determine order status
            order_status = ""
            if action == "buy":
                if chosen:
                    order_status = "pending"
                else:
                    order_status = "product_not_found"
            
            # Prepare row data for Google Sheets
            row_data = {
                "timestamp": timestamp,
                "customer_name": customer_name,
                "customer_phone": customer_phone,
                "customer_address": customer_address,
                "vendor_code": vendor_code,
                "product": product_name,
                "size": size,
                "qty": qty,
                "price": price,
                "action": action,
                "payment_status": "",
                "order_status": order_status,
                "payment_id": "",
                "payment_link": payment_link
            }
            
            # Log to Google Sheets
            success = sheets_connector.log_enquiry(row_data)
            
            if success:
                logger.info(f"Successfully logged interaction for customer: {customer_phone}")
                return {"ok": True, "row_id": "auto_generated"}
            else:
                logger.error(f"Failed to log interaction for customer: {customer_phone}")
                return {"ok": False, "error": "Failed to write to Google Sheets"}
            
        except Exception as e:
            logger.error(f"Error logging customer interaction: {str(e)}")
            return {"ok": False, "error": str(e)}
    
    async def log_order_update(
        self,
        customer_phone: str,
        order_status: str,
        payment_id: str = "",
        additional_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Log order status update."""
        try:
            success = sheets_connector.update_order_status(customer_phone, order_status, payment_id)
            
            if success:
                logger.info(f"Updated order status for {customer_phone}: {order_status}")
                return {"ok": True, "row_id": "updated"}
            else:
                logger.error(f"Failed to update order status for {customer_phone}")
                return {"ok": False, "error": "Failed to update Google Sheets"}
            
        except Exception as e:
            logger.error(f"Error logging order update: {str(e)}")
            return {"ok": False, "error": str(e)}
    
    async def log_payment_event(
        self,
        payment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Log payment webhook event."""
        try:
            # Extract payment information
            customer_phone = payment_data.get("customer_phone", "")
            payment_status = payment_data.get("status", "")
            payment_id = payment_data.get("payment_id", "")
            amount = payment_data.get("amount", "")
            
            # Update order status based on payment
            if payment_status == "success":
                order_status = "paid"
            elif payment_status == "failed":
                order_status = "payment_failed"
            else:
                order_status = "payment_pending"
            
            # Update in sheets
            result = await self.log_order_update(customer_phone, order_status, payment_id)
            
            logger.info(f"Logged payment event - Customer: {customer_phone}, Status: {payment_status}, ID: {payment_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error logging payment event: {str(e)}")
            return {"ok": False, "error": str(e)}
    
    async def get_customer_history(self, customer_phone: str) -> List[Dict[str, Any]]:
        """Get customer interaction history (if needed for context)."""
        try:
            # This would require additional Google Sheets functionality
            # For now, return empty list
            logger.info(f"Customer history requested for: {customer_phone}")
            return []
            
        except Exception as e:
            logger.error(f"Error getting customer history: {str(e)}")
            return []
