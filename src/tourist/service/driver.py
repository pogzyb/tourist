import asyncio
import json
import logging
import shutil
from pathlib import Path
from tempfile import mkdtemp
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path
from urllib.parse import quote_plus
from typing import Literal

from patchright.async_api import (
    async_playwright,
    Playwright,
    TimeoutError as PlaywrightTimeoutError,
)
from html_to_markdown import (
    ConversionOptions,
    convert_with_handle,
    create_options_handle,
    convert,
)

from .utils import get_links_from_serp

logger = logging.getLogger("uvicorn.error")

DEFAULT_WAIT_MS = 1000


@contextmanager
def temp_dirs():
    user_data_dir = mkdtemp(prefix="chrome-")
    data_path = mkdtemp(prefix="chrome-")
    disk_cache_dir = mkdtemp(prefix="chrome-")
    yield (user_data_dir, data_path, disk_cache_dir)
    if Path(user_data_dir).is_dir():
        shutil.rmtree(user_data_dir)
    if Path(data_path).is_dir():
        shutil.rmtree(data_path)
    if Path(disk_cache_dir).is_dir():
        shutil.rmtree(disk_cache_dir)


@asynccontextmanager
async def chrome(**kws):
    with temp_dirs() as tmp:
        user_data_dir, data_path, disk_cache_dir = tmp
        async with async_playwright() as playwright:
            context = await playwright.chromium.launch_persistent_context(
                user_data_dir,
                channel="chrome",
                headless=False,
                args=[
                    "--no-sandbox",
                    "--disable-gpu",
                    "--disable-dev-shm-usage",
                    "--disable-dev-tools",
                    "--deny-permission-prompts",
                    "--no-zygote",
                    f"--data-path={data_path}",
                    f"--disk-cache-dir={disk_cache_dir}",
                    "--ignore-certificate-errors",
                    "--remote-debugging-port=9222",
                ],
            )
            yield context
            await context.close()


async def handle_cookie_preferences(page) -> None:
    current_dir = Path(__file__).parent.resolve()
    with open(current_dir / "assets/cookie-managers.json", "r") as f:
        cookie_managers = json.load(f)
    locator = None
    for manager in cookie_managers:
        try:
            actions = manager.get("actions", [])
            for action in actions:
                if action["type"] == "iframe":
                    if await page.locator(action["value"]).count() > 0:
                        locator = page.frame_locator(action["value"]).first
                    else:
                        continue
                elif action["type"] == "css-selector":
                    if await page.locator(action["value"]).first.is_visible():
                        locator = page.locator(action["value"])
                        break
                elif action["type"] == "css-selector-list":
                    for selector in action["value"]:
                        if await page.locator(selector).first.is_visible():
                            locator = page.locator(selector)
                            break
        except:
            continue
    if locator is not None:
        try:
            async with page.expect_navigation(wait_until="networkidle", timeout=10000):
                await locator.first.click(delay=10)
        except (PlaywrightTimeoutError, Exception):
            # just return, do not stop the serping
            ...


async def scrape(url, ctx) -> dict[str, str]:
    page = await ctx.new_page()
    await page.goto(url, wait_until="domcontentloaded")
    await page.wait_for_timeout(DEFAULT_WAIT_MS)
    await handle_cookie_preferences(page)
    return {
        "title": await page.title(),
        "html": await page.content(),
        "current_url": page.url,
        "requested_url": url,
    }


async def get_serp_results(
    search_query: str,
    search_engine: Literal["google", "bing"],
    exclude_hosts: list[str],
    max_results: int = 5,
    **chrome_kws,
) -> list[dict[str, str]]:
    try:
        serp_results = []
        handle = create_options_handle(ConversionOptions(hocr_spatial_tables=False))
        async with chrome(**chrome_kws) as ctx:
            serp = await scrape(
                f"https://{search_engine}.com/search?q={quote_plus(search_query)}", ctx
            )
            links = get_links_from_serp(serp["html"], search_engine, exclude_hosts)[
                :max_results
            ]
            for task in asyncio.as_completed([scrape(link, ctx) for link in links]):
                result = await task
                html = result.pop("html")
                result["contents"] = convert_with_handle(html, handle)
                serp_results.append(result)
        return serp_results
    except:
        logger.exception("Could not get serp results:")
        return None


async def get_page(url: str, **chrome_kws) -> dict[str, str]:
    async with chrome(**chrome_kws) as ctx:
        result = await scrape(url, ctx)
        html = result.pop("html")
        result["contents"] = convert(html)
        return result
