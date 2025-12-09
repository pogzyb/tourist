import logging
from typing import Literal

from httpx import AsyncClient, Client, HTTPError

from tourist.common import DEFAULT_TIMEOUT, DEFAULT_MAX_RESULTS

logger = logging.getLogger("tourist.client")
logger.addHandler(logging.NullHandler())

ENDPOINT_SERP = "/tour/serp"
ENDPOINT_VIEW = "/tour/view"


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
        self, base_url: str, x_api_key: str, version_prefix: str = "/v1"
    ) -> None:
        self.base_url = base_url
        self.x_api_key = x_api_key
        self.version_prefix = version_prefix

    def _get_serp_uri(self):
        uri = self.version_prefix + ENDPOINT_SERP
        return uri

    def _get_view_uri(self):
        uri = self.version_prefix + ENDPOINT_VIEW
        return uri

    async def _apost(self, uri: str, body: dict = None, **httpx_kws):
        timeout = httpx_kws.pop("timeout", 30.0)
        headers = httpx_kws.pop("headers", {})
        headers["X-API-KEY"] = self.x_api_key
        async with AsyncClient(
            base_url=self.base_url, headers=headers, timeout=timeout, **httpx_kws
        ) as client:
            try:
                response = await client.post(uri, json=body)
                response.raise_for_status()
                return response.json()
            except HTTPError as e:
                return {"error": True, "detail": f"There was an HTTPError: {e}"}

    def _post(self, uri: str, body: dict = None, **httpx_kws):
        timeout = httpx_kws.pop("timeout", 30.0)
        headers = httpx_kws.pop("headers", {})
        headers["X-API-KEY"] = self.x_api_key
        with Client(
            base_url=self.base_url, headers=headers, timeout=timeout, **httpx_kws
        ) as client:
            try:
                response = client.post(uri, json=body)
                response.raise_for_status()
                return response.json()
            except HTTPError as e:
                return {"error": True, "detail": f"There was an HTTPError: {e}"}

    async def aget_serp(
        self,
        search_query: str,
        search_engine: Literal["google", "bing"] = "google",
        exclude_hosts: list[str] = [],
        max_results: int = DEFAULT_MAX_RESULTS,
        timeout: float = DEFAULT_TIMEOUT,
        **httpx_kws,
    ) -> dict:
        payload = {
            "search_query": search_query,
            "search_engine": search_engine,
            "max_results": max_results,
            "exclude_hosts": exclude_hosts,
            "timeout": timeout,
        }
        return await self._apost(self._get_serp_uri(), payload, **httpx_kws)

    def get_serp(
        self,
        search_query: str,
        search_engine: Literal["google", "bing"] = "google",
        exclude_hosts: list[str] = [],
        max_results: int = DEFAULT_MAX_RESULTS,
        timeout: float = DEFAULT_TIMEOUT,
        **httpx_kws,
    ) -> dict:
        payload = {
            "search_query": search_query,
            "search_engine": search_engine,
            "max_results": max_results,
            "exclude_hosts": exclude_hosts,
            "timeout": timeout,
        }
        return self._post(self._get_serp_uri(), payload, **httpx_kws)

    async def aget_page(
        self, target_url: str, timeout: float = DEFAULT_TIMEOUT, **httpx_kws
    ) -> dict:
        payload = {"url": target_url, "timeout": timeout}
        return await self._apost(self._get_view_uri(), payload, **httpx_kws)

    def get_page(
        self, target_url: str, timeout: float = DEFAULT_TIMEOUT, **httpx_kws
    ) -> dict:
        payload = {"url": target_url, "timeout": timeout}
        return self._post(self._get_view_uri(), payload, **httpx_kws)
