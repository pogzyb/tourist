import os

from pydantic import BaseModel, field_validator

from tourist.common import DEFAULT_TIMEOUT, DEFAULT_USER_AGENT, DEFAULT_WINDOW_SIZE


class BaseRequest(BaseModel):
    timeout: float | None = DEFAULT_TIMEOUT
    user_agent: str | None = DEFAULT_USER_AGENT
    window_size: tuple[int, int] = DEFAULT_WINDOW_SIZE

    @field_validator("timeout")
    @classmethod
    def timeout_less_than_30(cls, v: float) -> float:
        if v > 30.0:
            raise ValueError("timeout must be <= 30")
        return v

    @field_validator("window_size")
    @classmethod
    def check_window_size(cls, v: tuple[int, int]) -> tuple[int, int]:
        w, h = v
        mw, mh = DEFAULT_WINDOW_SIZE
        if (w > mw or h > mh) or (w < 100 or h < 200):
            raise ValueError("window_size is irregular")
        return v


class BaseResponse(BaseModel):
    version: str | None = os.getenv("TOURIST_VERSION")
