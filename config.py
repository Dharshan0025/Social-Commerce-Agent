import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Groq Configuration
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = "llama-3.3-70b-versatile"
    
    # Google Sheets Configuration
    google_sheets_credentials_file: str = os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE", "")
    inventory_sheet_id: str = os.getenv("INVENTORY_SHEET_ID", "")
    inventory_sheet_name: str = os.getenv("INVENTORY_SHEET_NAME", "Inventory")
    leads_sheet_name: str = os.getenv("LEADS_SHEET_NAME", "Leads_Orders")
    
    # WhatsApp Configuration
    whatsapp_verify_token: str = os.getenv("WHATSAPP_VERIFY_TOKEN", "")
    whatsapp_access_token: str = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
    whatsapp_phone_number_id: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    
    # Payment Gateway Configuration
    payment_secret: str = os.getenv("PAYMENT_SECRET", "")
    
    # HuggingFace Configuration
    huggingface_api_token: Optional[str] = os.getenv("HUGGINGFACE_API_TOKEN")
    
    # Sentry Configuration
    sentry_dsn: Optional[str] = os.getenv("SENTRY_DSN")
    
    # Server Configuration
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # Logging Configuration
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

# Validate required settings
def validate_settings():
    required_settings = [
        ("GROQ_API_KEY", settings.groq_api_key),
        ("GOOGLE_SHEETS_CREDENTIALS_FILE", settings.google_sheets_credentials_file),
        ("INVENTORY_SHEET_ID", settings.inventory_sheet_id),
        ("WHATSAPP_VERIFY_TOKEN", settings.whatsapp_verify_token),
    ]
    
    missing_settings = [name for name, value in required_settings if not value]
    
    if missing_settings:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_settings)}")
    
    return True