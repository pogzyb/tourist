from fastapi import APIRouter, HTTPException

from tourist.app.base import BaseResponse, BaseRequest
from tourist.core import get_page, get_page_with_actions

tour = APIRouter(prefix="/tour", redirect_slashes=True, tags=["Tour"])


class TourRequest(BaseRequest):
    target_url: str | None = None
    warmup_url: str | None = None
    cookies: list | None = None
    include_b64_png: bool | None = False


class TourActionsRequest(BaseRequest):
    actions: str | None = None


class TourResponse(BaseResponse):
    current_url: str | None = None
    cookies: list | None = None
    source_html: str
    b64_png: str | None = None


class TouristActionsResponse(BaseResponse): ...


@tour.post("/page", response_model=TourResponse)
def view_page(tourist_request: TourRequest):
    page = get_page(**tourist_request.dict())
    return page or HTTPException(status_code=400, detail="something went wrong")


@tour.post("/actions")
def do_actions(tourist_actions_request: TourActionsRequest):
    page = get_page_with_actions(**tourist_actions_request.dict())
    return page or HTTPException(status_code=400, detail="something went wrong")
