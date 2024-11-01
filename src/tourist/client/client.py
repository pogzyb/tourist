import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum
from urllib.parse import quote_plus

from httpx import AsyncClient, Client, HTTPError

from tourist.common import DEFAULT_USER_AGENT, DEFAULT_TIMEOUT, DEFAULT_WINDOW_SIZE
from tourist.client.parse_utils import get_text, get_links_from_serp

logger = logging.getLogger("tourist.client")
logger.addHandler(logging.NullHandler())

DEFAULT_MAX_RESULTS = 3
DEFAULT_CONCURRENCY = 2  # should be <= 2 when running locally
ENDPOINT_ACTIONS = "/tour/actions"
ENDPOINT_VIEW = "/tour/view"


class EngineEnum(str, Enum):
    GOOGLE = "google"


class Singleton(type):
    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls.instance = None

    def __call__(cls, *args, **kw):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)
        return cls.instance


class TouristScraper:
    __metaclass__ = Singleton

    def __init__(
        self,
        base_url: str,
        secret: str,
        concurrency: int = DEFAULT_CONCURRENCY,
        version_prefix: str = "/v1",
    ) -> None:
        self.base_url = base_url
        self.secret = secret
        self.concurrency = concurrency
        self.version_prefix = version_prefix

    def get_actions_uri(self):
        uri = self.version_prefix + ENDPOINT_ACTIONS
        return uri

    def get_view_uri(self):
        uri = self.version_prefix + ENDPOINT_VIEW
        return uri

    async def apost(self, uri: str, body: dict = None, **httpx_kws):
        timeout = httpx_kws.pop("timeout", 30.0)
        headers = httpx_kws.pop("headers", {})
        headers["X-SECRET"] = self.secret
        async with AsyncClient(
            base_url=self.base_url, headers=headers, timeout=timeout, **httpx_kws
        ) as client:
            try:
                response = await client.post(uri, json=body)
                response.raise_for_status()
                return response.json()
            except HTTPError as e:
                return {"error": True, "detail": f"There was an HTTPError: {e}"}

    def post(self, uri: str, body: dict = None, **httpx_kws):
        timeout = httpx_kws.pop("timeout", 30.0)
        headers = httpx_kws.pop("headers", {})
        headers["X-SECRET"] = self.secret
        with Client(
            base_url=self.base_url, headers=headers, timeout=timeout, **httpx_kws
        ) as client:
            try:
                response = client.post(uri, json=body)
                response.raise_for_status()
                return response.json()
            except HTTPError as e:
                return {"error": True, "detail": f"There was an HTTPError: {e}"}

    async def aget_page(
        self,
        target_url: str,
        warmup_url: str = None,
        cookies: list[dict[str, str]] = [],
        screenshot: bool = False,
        timeout: float = DEFAULT_TIMEOUT,
        user_agent: str = DEFAULT_USER_AGENT,
        window_size: tuple[int, int] = DEFAULT_WINDOW_SIZE,
        **httpx_kws,
    ) -> dict:
        payload = {
            "target_url": target_url,
            "warmup_url": warmup_url,
            "cookies": cookies,
            "screenshot": screenshot,
            "user_agent": user_agent,
            "timeout": timeout,
            "window_size": window_size,
        }
        return await self.aio_post(self.get_view_uri(), payload, **httpx_kws)

    def get_page(
        self,
        target_url: str,
        warmup_url: str = None,
        cookies: list[dict[str, str]] = [],
        screenshot: bool = False,
        timeout: float = DEFAULT_TIMEOUT,
        user_agent: str = DEFAULT_USER_AGENT,
        window_size: tuple[int, int] = DEFAULT_WINDOW_SIZE,
        **httpx_kws,
    ) -> dict:
        payload = {
            "target_url": target_url,
            "warmup_url": warmup_url,
            "cookies": cookies,
            "screenshot": screenshot,
            "user_agent": user_agent,
            "timeout": timeout,
            "window_size": window_size,
        }
        return self.post(self.get_view_uri(), payload, **httpx_kws)

    async def ado_actions(
        self,
        actions: str,
        timeout: float = DEFAULT_TIMEOUT,
        user_agent: str = DEFAULT_USER_AGENT,
        window_size: tuple[int, int] = DEFAULT_WINDOW_SIZE,
        **httpx_kws,
    ) -> dict:
        payload = {
            "actions": actions,
            "user_agent": user_agent,
            "timeout": timeout,
            "window_size": window_size,
        }
        return await self.apost(self.get_actions_uri(), payload, **httpx_kws)

    def do_actions(
        self,
        actions: str,
        timeout: float = DEFAULT_TIMEOUT,
        user_agent: str = DEFAULT_USER_AGENT,
        window_size: tuple[int, int] = DEFAULT_WINDOW_SIZE,
        **httpx_kws,
    ) -> dict:
        payload = {
            "actions": actions,
            "user_agent": user_agent,
            "timeout": timeout,
            "window_size": window_size,
        }
        return self.post(self.get_actions_uri(), payload, **httpx_kws)

    # TODO/Contribution: open to re-works of this function + error checking.
    def get_serp(
        self,
        query: str,
        max_results: int = DEFAULT_MAX_RESULTS,
        exclude_hosts: list[str] = [],
        engine: EngineEnum = EngineEnum.GOOGLE,
        **httpx_kws,
    ) -> list[dict]:
        assert engine == EngineEnum.GOOGLE, f"{engine} is not yet supported."
        page = self.get_page(
            f"https://google.com/search?q={quote_plus(query)}", **httpx_kws
        )
        pages = []
        if source_html := page.get("source_html"):
            links = get_links_from_serp(source_html, engine.value, exclude_hosts)
            logger.debug(f"Found {len(links)} relevant links on SERP")
            # retrieve links in separate threads
            with ThreadPoolExecutor(max_workers=self.concurrency) as pool:
                futures = {
                    pool.submit(self.get_page, link, **httpx_kws): link
                    for link in links
                }
                for f in as_completed(futures):
                    try:
                        page = f.result()
                        if not page.get("error"):
                            page_data = {
                                "url": futures[f],
                                "content": get_text(page["source_html"]),
                            }
                            pages.append(page_data)
                            # once we have enough results, break
                            if len(pages) >= max_results:
                                break
                    except:
                        ...
                # shutdown the threadpool and cancel pending work
                pool.shutdown(wait=False, cancel_futures=True)
        # return serp content
        logger.debug(f"Extracted {len(pages)} of information from SERP")
        return pages

    # TODO/Contribution: open to re-works of this function + error checking.
    async def aget_serp(
        self,
        query: str,
        max_results: int = DEFAULT_MAX_RESULTS,
        exclude_hosts: list[str] = [],
        engine: EngineEnum = EngineEnum.GOOGLE,
        **httpx_kws,
    ) -> list[dict]:
        assert engine == EngineEnum.GOOGLE, f"{engine} is not yet supported."
        page = await self.aget_page(
            f"https://www.google.com/search?q={quote_plus(query)}", **httpx_kws
        )
        pages = []
        if source_html := page.get("source_html"):
            links = get_links_from_serp(source_html, engine.value, exclude_hosts)
            logger.debug(f"Found {len(links)} relevant links on SERP")
            tasks = {
                asyncio.create_task(self.aget_page(link, **httpx_kws)): link
                for link in links
            }
            for task in asyncio.as_completed(tasks):
                try:
                    page = await task
                    if not page.get("error"):
                        page_data = {
                            "url": tasks[task],
                            "content": get_text(page["source_html"]),
                        }
                        pages.append(page_data)
                        if len(pages) >= max_results:
                            break
                except:
                    ...
            # clean up coroutines
            tasks = [task.cancel() for task in tasks]
        # return serp content
        logger.debug(f"Extracted {len(pages)} pages of information from SERP")
        return pages
