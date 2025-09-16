import logging
from typing import Dict, Any, List, Optional
from utils.google_sheets import sheets_connector
from utils.groq_client import groq_client

logger = logging.getLogger(__name__)

class InventoryMatcherAgent:
    """Inventory Matcher Agent responsible for matching extracted product info with inventory."""
    
    def __init__(self):
        self.system_prompt = """You are the Inventory Matcher. Input: a JSON from Input Agent. Task: find matching rows in the provided Google Sheets 'Inventory' by this priority:
1) If vendor_code present → exact lookup by Vendor code.
2) Else → fuzzy match by Brand + Type + Color + Size (use simple substring matching).

Return JSON:
- status: exact_match | partial_match | not_found
- matches: array of up to 3 product objects {vendor_code, brand, type, description, color, sizes_available (list), qty_on_hand, sale_price, payment_link}
- chosen: the single best match object or null
- reason: explanation for match

Output ONLY JSON."""

    async def match_inventory(self, extracted_info: Dict[str, Any]) -> Dict[str, Any]:
        """Match extracted product info with inventory."""
        try:
            vendor_code = extracted_info.get("vendor_code", "")
            product_name = extracted_info.get("product_name", "")
            brand = extracted_info.get("brand", "")
            product_type = extracted_info.get("type", "")
            color = extracted_info.get("color", "")
            size = extracted_info.get("size", "")
            
            matches = []
            chosen = None
            status = "not_found"
            reason = ""
            
            # Priority 1: Exact vendor code match
            if vendor_code:
                exact_product = sheets_connector.get_product_by_vendor_code(vendor_code)
                if exact_product:
                    match_obj = {
                        "vendor_code": exact_product.get("Vendor_Code", ""),
                        "brand": exact_product.get("Brand", ""),
                        "type": exact_product.get("Type", ""),
                        "description": exact_product.get("Product_Name", ""),
                        "color": exact_product.get("Color", ""),
                        "sizes_available": [exact_product.get("Size", "")] if exact_product.get("Size") else [],
                        "qty_on_hand": exact_product.get("Qty_On_Hand", 0),
                        "sale_price": exact_product.get("Sale_Price", ""),
                        "payment_link": exact_product.get("Payment_Link", "")
                    }
                    matches.append(match_obj)
                    chosen = match_obj
                    status = "exact_match"
                    reason = f"Exact vendor code match: {vendor_code}"
                    
                    result = {
                        "status": status,
                        "matches": matches,
                        "chosen": chosen,
                        "reason": reason
                    }
                    logger.info(f"Inventory matching result: {result}")
                    return result
            
            # Priority 2: Fuzzy matching by Brand + Type + Color + Size
            search_terms = {
                "product_name": product_name,
                "brand": brand,
                "type": product_type,
                "color": color,
                "size": size
            }
            
            inventory_matches = sheets_connector.search_inventory(search_terms)
            
            if inventory_matches:
                for match in inventory_matches[:3]:  # Top 3 matches
                    match_obj = {
                        "vendor_code": match.get("Vendor_Code", ""),
                        "brand": match.get("Brand", ""),
                        "type": match.get("Type", ""),
                        "description": match.get("Product_Name", ""),
                        "color": match.get("Color", ""),
                        "sizes_available": [match.get("Size", "")] if match.get("Size") else [],
                        "qty_on_hand": match.get("Qty_On_Hand", 0),
                        "sale_price": match.get("Sale_Price", ""),
                        "payment_link": match.get("Payment_Link", "")
                    }
                    matches.append(match_obj)
                
                # Choose the best match (first one with highest score)
                chosen = matches[0] if matches else None
                
                # Determine if it's exact or partial match
                best_score = inventory_matches[0].get("match_score", 0)
                if best_score >= 80:
                    status = "exact_match"
                    reason = f"High confidence match (score: {best_score})"
                else:
                    status = "partial_match"
                    reason = f"Partial match found (score: {best_score})"
            else:
                status = "not_found"
                reason = "No matching products found in inventory"
            
            result = {
                "status": status,
                "matches": matches,
                "chosen": chosen,
                "reason": reason
            }
            
            logger.info(f"Inventory matching result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error in inventory matching: {str(e)}")
            return {
                "status": "not_found",
                "matches": [],
                "chosen": None,
                "reason": f"Error during matching: {str(e)}"
            }