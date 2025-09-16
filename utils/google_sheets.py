import logging
from typing import List, Dict, Any, Optional
import gspread
from google.oauth2.service_account import Credentials
from config import settings

logger = logging.getLogger(__name__)

class GoogleSheetsConnector:
    """Connector for Google Sheets operations."""
    
    def __init__(self):
        self.gc = None
        self.inventory_sheet = None
        self.leads_sheet = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Google Sheets client."""
        try:
            # Define the scope
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ]
            
            # Load credentials
            creds = Credentials.from_service_account_file(
                settings.google_sheets_credentials_file,
                scopes=scope
            )
            
            # Initialize client
            self.gc = gspread.authorize(creds)
            
            # Open the spreadsheet
            spreadsheet = self.gc.open_by_key(settings.inventory_sheet_id)
            
            # Get worksheets
            self.inventory_sheet = spreadsheet.worksheet(settings.inventory_sheet_name)
            
            # Try to get leads sheet, create if doesn't exist
            try:
                self.leads_sheet = spreadsheet.worksheet(settings.leads_sheet_name)
            except gspread.WorksheetNotFound:
                self.leads_sheet = spreadsheet.add_worksheet(
                    title=settings.leads_sheet_name,
                    rows=1000,
                    cols=20
                )
                # Add headers for leads sheet
                headers = [
                    "Timestamp", "Customer_Name", "Phone", "Address", "Vendor_Code", 
                    "Product", "Size", "Qty", "Price", "Action", "Payment_Status", 
                    "Order_Status", "Payment_ID", "Payment_Link"
                ]
                self.leads_sheet.append_row(headers)
            
            logger.info("Google Sheets client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets client: {str(e)}")
            raise
    
    def search_inventory(self, search_terms: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search inventory based on product details."""
        try:
            # Get all inventory data
            records = self.inventory_sheet.get_all_records()
            
            if not records:
                return []
            
            # Extract search criteria
            product_name = search_terms.get("product_name", "").lower()
            brand = search_terms.get("brand", "").lower()
            product_type = search_terms.get("type", "").lower()
            color = search_terms.get("color", "").lower()
            size = search_terms.get("size", "").lower()
            vendor_code = search_terms.get("vendor_code", "").lower()
            
            matches = []
            
            for record in records:
                score = 0
                
                # Exact vendor code match gets highest priority
                if vendor_code and vendor_code == str(record.get("Vendor_Code", "")).lower():
                    score += 100
                
                # Product name matching
                record_name = str(record.get("Product_Name", "")).lower()
                if product_name and product_name in record_name:
                    score += 50
                elif product_name:
                    # Partial matching
                    words = product_name.split()
                    for word in words:
                        if word in record_name:
                            score += 10
                
                # Brand matching
                record_brand = str(record.get("Brand", "")).lower()
                if brand and brand in record_brand:
                    score += 30
                
                # Type matching
                record_type = str(record.get("Type", "")).lower()
                if product_type and product_type in record_type:
                    score += 20
                
                # Color matching
                record_color = str(record.get("Color", "")).lower()
                if color and color in record_color:
                    score += 15
                
                # Size matching
                record_size = str(record.get("Size", "")).lower()
                if size and size in record_size:
                    score += 15
                
                if score > 0:
                    record["match_score"] = score
                    matches.append(record)
            
            # Sort by score and return top 3
            matches.sort(key=lambda x: x["match_score"], reverse=True)
            return matches[:3]
            
        except Exception as e:
            logger.error(f"Error searching inventory: {str(e)}")
            return []
    
    def get_product_by_vendor_code(self, vendor_code: str) -> Optional[Dict[str, Any]]:
        """Get exact product match by vendor code."""
        try:
            records = self.inventory_sheet.get_all_records()
            
            for record in records:
                if str(record.get("Vendor_Code", "")).lower() == vendor_code.lower():
                    return record
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting product by vendor code: {str(e)}")
            return None
    
    def log_enquiry(self, enquiry_data: Dict[str, Any]) -> bool:
        """Log customer enquiry to leads sheet."""
        try:
            row_data = [
                enquiry_data.get("timestamp", ""),
                enquiry_data.get("customer_name", ""),
                enquiry_data.get("customer_phone", ""),
                enquiry_data.get("customer_address", ""),
                enquiry_data.get("vendor_code", ""),
                enquiry_data.get("product", ""),
                enquiry_data.get("size", ""),
                enquiry_data.get("qty", ""),
                enquiry_data.get("price", ""),
                enquiry_data.get("action", ""),
                enquiry_data.get("payment_status", ""),
                enquiry_data.get("order_status", ""),
                enquiry_data.get("payment_id", ""),
                enquiry_data.get("payment_link", "")
            ]
            
            self.leads_sheet.append_row(row_data)
            logger.info(f"Logged enquiry for customer: {enquiry_data.get('customer_phone')}")
            return True
            
        except Exception as e:
            logger.error(f"Error logging enquiry: {str(e)}")
            return False
    
    def update_order_status(self, customer_phone: str, order_status: str, payment_id: str = "") -> bool:
        """Update order status for a customer."""
        try:
            # Find the row with matching customer phone
            cell = self.leads_sheet.find(customer_phone)
            if cell:
                # Update the order status column (column 12)
                self.leads_sheet.update_cell(cell.row, 12, order_status)
                # Update payment ID if provided (column 13)
                if payment_id:
                    self.leads_sheet.update_cell(cell.row, 13, payment_id)
                logger.info(f"Updated order status for {customer_phone}: {order_status}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating order status: {str(e)}")
            return False

# Global instance
sheets_connector = GoogleSheetsConnector()
