import os

from pydantic import BaseModel, field_validator

from tourist.common import DEFAULT_TIMEOUT


class BaseRequest(BaseModel):
    timeout: float | None = DEFAULT_TIMEOUT

    @field_validator("timeout")
    @classmethod
    def timeout_less_than_30(cls, v: float) -> float:
        if v > 900.0:
            raise ValueError("timeout must be <= 900")
        return v


class BaseResponse(BaseModel):
    version: str | None = os.getenv("TOURIST_VERSION")
