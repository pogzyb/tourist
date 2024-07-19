from fastapi import FastAPI

from .routers import info, tour


def create_app():
    app = FastAPI(
        title="tourist",
        description="Serverless framework for web scraping.",
        version="0.1.0a1",
    )
    app.include_router(info)
    app.include_router(tour, prefix="/v1")

    return app
