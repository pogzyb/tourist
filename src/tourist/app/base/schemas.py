import os

from pydantic import BaseModel, field_validator

from tourist.common import DEFAULT_TIMEOUT, DEFAULT_USER_AGENT, DEFAULT_WINDOW_SIZE


class BaseRequest(BaseModel):
    timeout: float | None = DEFAULT_TIMEOUT

    @field_validator("timeout")
    @classmethod
    def timeout_less_than_30(cls, v: float) -> float:
        if v > 30.0:
            raise ValueError("timeout must be <= 30")
        return v


class BaseResponse(BaseModel):
    version: str | None = os.getenv("TOURIST_VERSION")
