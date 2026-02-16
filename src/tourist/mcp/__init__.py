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

        if authorization := headers.get("authorization"):
            # check bearer token
            if authorization.lstrip("Bearer ") == os.getenv("X_API_KEY"):
                result = await call_next(context)
                return result
            else:
                raise ToolError(
                    "Access denied. Please check your Authorization header."
                )
        else:
            raise ToolError("Access denied. Please include an Authorization header.")


async def create_server() -> FastMCP:
    mcp = FastMCP(
        "Tourist🤳", host="0.0.0.0", port=8000, version=__version__, stateless_http=True
    )

    @mcp.custom_route("/info/health", methods=["GET"])
    async def health_check(request: Request) -> PlainTextResponse:
        return PlainTextResponse("OK")

    @mcp.tool(
        name="web_search",
        description="Search the web for information related to the given query. "
        "Useful when you need more detailed information about a given topic or subject.",
        tags={"SERP", "web-search"},
        meta={"version": __version__, "author": "tourist"},
    )
    async def web_search(query: str) -> list[Page]:
        if serp_results := await get_serp_results(
            search_query=query, search_engine="google", max_results=5
        ):
            pages = [
                Page(url=r["current_url"], contents=r["contents"]) for r in serp_results
            ]
            return pages
        else:
            raise ToolError("Something went wrong in this Tool Call.")

    mcp.add_middleware(AuthMiddleware())

    return mcp
