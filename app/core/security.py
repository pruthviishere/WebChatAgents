import os
from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from app.config.Settings import settings
from app.utils.logging import logger

API_KEY_NAME = "Authorization"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_api_key(api_key_header: str = Security(api_key_header)):
    """
    Verify the API key from the Authorization header.
    
    Args:
        api_key_header: The API key from the Authorization header
        
    Returns:
        bool: True if the API key is valid
        
    Raises:
        HTTPException: If the API key is missing or invalid
    """
    if not api_key_header:
        logger.warning("API key is missing")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing"
        )
    
    if api_key_header != settings.APP_API_KEY:
        logger.warning("Invalid API key provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return True

def setup_security(app):
    """
    Setup security middleware and dependencies for the FastAPI app.
    
    Args:
        app: The FastAPI application instance
    """
    # Add security middleware if needed
    pass 