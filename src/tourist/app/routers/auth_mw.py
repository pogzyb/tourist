import logging
import os

from fastapi import HTTPException, Request, status

logger = logging.getLogger("uvicorn.error")


async def check_secret_key(request: Request) -> None:
    x_api_key = request.headers.get("x-api-key") or request.headers.get("X-API-KEY")
    if x_api_key is None:
        logger.info("X-API-KEY header is missing.")
        raise HTTPException(
            detail="access denied.", status_code=status.HTTP_403_FORBIDDEN
        )
    elif x_api_key != os.getenv("X_API_KEY"):
        logger.info("X-API-KEY is incorrect.")
        raise HTTPException(
            detail="access denied.", status_code=status.HTTP_403_FORBIDDEN
        )
