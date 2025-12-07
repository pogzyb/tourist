import logging

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, field_validator

from tourist.app.base import BaseResponse, BaseRequest
from tourist.service import get_page, get_serp_results

tour = APIRouter(prefix="/tour", redirect_slashes=True, tags=["Tour"])
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Page(BaseModel):
    contents: str
    url: str


class TouristSerpRequest(BaseRequest):
    search_query: str
    max_results: int

    @field_validator("max_results")
    @classmethod
    def max_results_reasonable(cls, v: int) -> int:
        if v > 10 and v < 1:
            raise ValueError("max_results must be >= 1 and <= 10")
        return v


class TouristSerpResponse(BaseResponse):
    pages: list[Page]


class TouristViewRequest(BaseRequest):
    url: str


class TouristViewResponse(BaseResponse, Page): ...


@tour.post("/serp", response_model=TouristSerpResponse)
def do_serp(tourist_serp_request: TouristSerpRequest):
    if serp_results := get_serp_results(**tourist_serp_request.model_dump()):
        pages = [
            Page(url=r["current_url"], contents=r["contents"]) for r in serp_results
        ]
        serp_response = TouristSerpResponse(pages=pages)
        return serp_response
    else:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="something went wrong",
        )


@tour.post("/view", response_model=TouristViewResponse)
def view_page(tourist_view_request: TouristViewRequest):
    if page := get_page(**tourist_view_request.model_dump()):
        return TouristViewResponse(url=r["current_url"], contents=r["contents"])
    else:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="something went wrong",
        )
