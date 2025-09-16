#!/usr/bin/env python3
"""
Main entry point for the Social Commerce AI Agent.
This script starts the FastAPI server with proper configuration.
"""

import logging
import uvicorn
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import settings, validate_settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('social_commerce_agent.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main function to start the server."""
    try:
        # Validate required settings
        validate_settings()
        logger.info("Configuration validated successfully")
        
        # Import the FastAPI app
        from api import app
        
        # Start the server
        logger.info(f"Starting Social Commerce AI Agent on {settings.host}:{settings.port}")
        uvicorn.run(
            "api:app",
            host=settings.host,
            port=settings.port,
            reload=settings.debug,
            log_level=settings.log_level.lower()
        )
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()