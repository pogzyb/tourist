import logging

from fastapi import APIRouter, HTTPException

from tourist.app.base import BaseResponse, BaseRequest
from tourist.core import get_page, get_page_with_actions

tour = APIRouter(prefix="/tour", redirect_slashes=True, tags=["Tour"])
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TouristViewRequest(BaseRequest):
    target_url: str
    warmup_url: str | None = None
    cookies: list | None = None
    screenshot: bool | None = False


class TouristActionsRequest(BaseRequest):
    actions: str


class TouristViewResponse(BaseResponse):
    current_url: str | None = None
    cookies: list | None = None
    source_html: str
    b64_screenshot: str | None = None


class TouristActionsResponse(BaseResponse): ...


@tour.post("/view", response_model=TouristViewResponse)
def view_page(tourist_view_request: TouristViewRequest):
    page = get_page(**tourist_view_request.model_dump())
    if not page:
        raise HTTPException(status_code=400, detail="something went wrong")
    else:
        return page


@tour.post("/actions")
def do_actions(tourist_actions_request: TouristActionsRequest):
    page = get_page_with_actions(**tourist_actions_request.model_dump())
    if not page:
        raise HTTPException(status_code=400, detail="something went wrong")
    else:
        return page
