import os
from fastapi import Header, HTTPException

async def verify_api_key(authorization: str = Header(default=os.getenv("API_KEY"))):
    api_key = os.getenv("API_KEY")
    if not api_key or authorization != f"Bearer {api_key}":
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    return True