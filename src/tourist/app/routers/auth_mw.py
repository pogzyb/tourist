import logging
import os

from fastapi import HTTPException, Request, status

logger = logging.getLogger("uvicorn.error")


async def check_secret_key(request: Request) -> bool:
    x_api_key = request.headers.get("x-api-key")
    if x_api_key != os.getenv("X_API_KEY"):
        logger.info("X-API-KEY is incorrect or missing.")
        raise HTTPException(
            detail="access denied.", status_code=status.HTTP_403_FORBIDDEN
        )
