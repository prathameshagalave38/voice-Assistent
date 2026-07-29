from fastapi import Header, HTTPException, status
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)

async def verify_api_key(x_api_key: str = Header(..., description="API Key for Authentication")):
    if x_api_key != settings.api_key:
        logger.warning("Unauthorized access attempt with invalid API Key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    return x_api_key
