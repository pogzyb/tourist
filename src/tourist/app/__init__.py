import os

from fastapi import FastAPI

from .routers import info, tour


def create_app():
    app = FastAPI(
        title="Tourist🤳",
        description="An open-source, low-cost, serverless application for web scraping.",
        version=os.getenv("TOURIST_VERSION"),
    )
    app.include_router(info)
    app.include_router(tour, prefix="/v1")

    return app
