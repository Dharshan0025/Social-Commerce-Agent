import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import JSONResponse
import json
import hashlib
import hmac

from config import settings
from agents.coordinator import CoordinatorAgent

# Configure logging
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Social Commerce AI Agent",
    description="WhatsApp-based social commerce automation using CrewAI agents",
    version="1.0.0"
)

# Initialize coordinator agent
coordinator = CoordinatorAgent()

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    logger.info("Starting Social Commerce AI Agent API")
    await coordinator.initialize()

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Social Commerce AI Agent",
        "version": "1.0.0"
    }

@app.get("/webhook/whatsapp")
async def verify_whatsapp_webhook(request: Request):
    """Verify WhatsApp webhook endpoint."""
    try:
        hub_mode = request.query_params.get("hub.mode")
        hub_challenge = request.query_params.get("hub.challenge")
        hub_verify_token = request.query_params.get("hub.verify_token")
        
        logger.info(f"Webhook verification request: mode={hub_mode}, token={hub_verify_token}")
        
        if hub_mode == "subscribe" and hub_verify_token == settings.whatsapp_verify_token:
            logger.info("WhatsApp webhook verified successfully")
            # Meta expects the challenge as plain text, not JSON
            from fastapi.responses import PlainTextResponse
            return PlainTextResponse(content=hub_challenge)
        else:
            logger.warning(f"WhatsApp webhook verification failed: mode={hub_mode}, expected_token={settings.whatsapp_verify_token}")
            raise HTTPException(status_code=403, detail="Verification failed")
    except Exception as e:
        logger.error(f"Error in webhook verification: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Verification error: {str(e)}")

@app.post("/webhook/whatsapp")
async def handle_whatsapp_webhook(request: Request):
    """Handle incoming WhatsApp webhook events."""
    try:
        # Get the raw body for signature verification
        body = await request.body()
        
        # Verify webhook signature (optional but recommended)
        signature = request.headers.get("X-Hub-Signature-256")
        if signature and settings.whatsapp_access_token:
            expected_signature = hmac.new(
                settings.whatsapp_access_token.encode(),
                body,
                hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(f"sha256={expected_signature}", signature):
                logger.warning("Invalid WhatsApp webhook signature")
                raise HTTPException(status_code=403, detail="Invalid signature")
        
        # Parse the JSON payload
        payload = json.loads(body.decode())
        logger.info(f"Received WhatsApp webhook: {json.dumps(payload, indent=2)}")
        
        # Process the webhook payload
        result = await coordinator.process_whatsapp_message(payload)
        
        return JSONResponse(content={"status": "success", "result": result})
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON in WhatsApp webhook payload")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        logger.error(f"Error processing WhatsApp webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/webhook/payment")
async def handle_payment_webhook(request: Request):
    """Handle payment gateway webhook events."""
    try:
        # Get the raw body for signature verification
        body = await request.body()
        
        # Verify payment webhook signature
        signature = request.headers.get("X-Payment-Signature")
        if signature and settings.payment_secret:
            expected_signature = hmac.new(
                settings.payment_secret.encode(),
                body,
                hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(expected_signature, signature):
                logger.warning("Invalid payment webhook signature")
                raise HTTPException(status_code=403, detail="Invalid signature")
        
        # Parse the JSON payload
        payload = json.loads(body.decode())
        logger.info(f"Received payment webhook: {json.dumps(payload, indent=2)}")
        
        # Process the payment webhook
        result = await coordinator.process_payment_webhook(payload)
        
        return JSONResponse(content={"status": "success", "result": result})
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON in payment webhook payload")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        logger.error(f"Error processing payment webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/test/message")
async def test_message_processing(payload: Dict[str, Any]):
    """Test endpoint for message processing (development only)."""
    if not settings.debug:
        raise HTTPException(status_code=404, detail="Not found")
    
    try:
        logger.info(f"Test message processing: {json.dumps(payload, indent=2)}")
        result = await coordinator.process_whatsapp_message(payload)
        return JSONResponse(content={"status": "success", "result": result})
    except Exception as e:
        logger.error(f"Error in test message processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
