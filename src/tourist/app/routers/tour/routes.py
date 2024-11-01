import logging

from fastapi import APIRouter, HTTPException, status

from tourist.app.base import BaseResponse, BaseRequest
from tourist.service import get_page, get_page_with_actions

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


class TouristActionsResponse(BaseResponse):
    # TODO: should this be a json string or should the user be responsible
    #  ensuring the payload is either serializable or already serialized?
    actions_output: dict


@tour.post("/view", response_model=TouristViewResponse)
def view_page(tourist_view_request: TouristViewRequest):
    if page := get_page(**tourist_view_request.model_dump()):
        return page
    else:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="something went wrong",
        )


@tour.post("/actions", response_model=TouristActionsResponse)
def do_actions(tourist_actions_request: TouristActionsRequest):
    if page := get_page_with_actions(**tourist_actions_request.model_dump()):
        return TouristActionsResponse(actions_output=page)
    else:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="something went wrong",
        )
