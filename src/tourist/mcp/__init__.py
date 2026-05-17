import os

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.server.dependencies import get_http_headers
from pydantic import BaseModel, Field
from starlette.requests import Request
from starlette.responses import PlainTextResponse

from tourist import __version__
from tourist.service import get_serp_results


class Page(BaseModel):
    contents: str = Field(description="The contents of the page.")
    url: str = Field(description="The URL of the page.")


class AuthMiddleware(Middleware):
    async def on_message(self, context: MiddlewareContext, call_next):
        headers = get_http_headers()
        if secret_key := headers.get("x-api-key") == os.getenv("X_API_KEY"):
            result = await call_next(context)
            return result
        else:
            raise ToolError("Access denied. Please check your X-API-KEY header.")


def create_mcp() -> FastMCP:
    mcp = FastMCP("Tourist🤳", version=__version__)
    mcp.add_middleware(AuthMiddleware())

    # TODO: this is not needed right now, but might be useful in the future.
    # @mcp.custom_route("/health", methods=["GET"])
    # async def health_check(request: Request) -> PlainTextResponse:
    #     return PlainTextResponse("OK")

    @mcp.tool(
        name="web_search",
        title="Web Search",
        description=(
            "Search the web. Useful when you need to source information from the internet about a given topic or subject."
        ),
        tags={"SERP", "web-search"},
        meta={"version": __version__, "author": "tourist"},
    )
    async def web_search(query: str) -> list[Page]:
        if serp_results := await get_serp_results(
            search_query=query, search_engine="brave", max_results=5, exclude_hosts=["youtube.com"]
        ):
            pages = [
                Page(url=r["current_url"], contents=r["contents"]) for r in serp_results
            ]
            return pages
        else:
            raise ToolError("Something went wrong in this Tool Call.")

    return mcp.http_app(transport="http")
