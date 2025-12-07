from fastapi import APIRouter

info = APIRouter(prefix="/info", redirect_slashes=True, tags=["Info"])


@info.get("/health")
def health():
    # The aws-lambda-web-adapter uses this route to check if the application is ready.
    return "ok"
