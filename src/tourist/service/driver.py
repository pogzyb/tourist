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

import stamina
from patchright.async_api import (
    async_playwright,
    Playwright,
    TimeoutError as PlaywrightTimeoutError,
    Error,
)
from html_to_markdown import (
    ConversionOptions,
    convert_with_handle,
    create_options_handle,
    convert,
)

from .utils import get_links_from_serp

logger = logging.getLogger("uvicorn.error")

DEFAULT_WAIT_MS = 1500


@contextmanager
def temp_dirs():
    dirs = [mkdtemp(prefix="chrome-") for _ in range(3)]
    try:
        yield dirs
    finally:
        for d in dirs:
            shutil.rmtree(d)


@asynccontextmanager
async def chrome(**kws):
    with temp_dirs() as dirs:
        user_data_dir, data_path, disk_cache_dir = dirs
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
            return


async def scrape(url: str, ctx: "BrowserContext") -> dict[str, str]:
    page = await ctx.new_page()
    await page.goto(url, wait_until="load")
    await page.wait_for_timeout(DEFAULT_WAIT_MS)
    await handle_cookie_preferences(page)
    await page.keyboard.down("PageDown")
    scraped_page = {
        "title": await page.title(),
        "html": await page.content(),
        "current_url": page.url,
        "requested_url": url,
    }
    return scraped_page


@stamina.retry(on=Error, attempts=2, wait_initial=2)
async def get_serp_results(
    search_query: str,
    search_engine: Literal["brave", "duckduckgo"],
    exclude_hosts: list[str],
    max_results: int = 5,
    **chrome_kws,
) -> list[dict[str, str]]:

    serp_results: list[dict[str, str]] = []

    md_handler = create_options_handle(
        ConversionOptions(
            hocr_spatial_tables=False,
            skip_images=True,
        )
    )

    if search_engine == "brave":
        base_se = "search.brave.com"
        path_se = "search"
    elif search_engine == "duckduckgo":
        base_se = "duckduckgo.com"
        path_se = ""
    else:
        logger.error(f"invalid search_engine: {search_engine}")
        return []

    async with chrome(**chrome_kws) as ctx:

        serp_url = f"https://{base_se}/{path_se}?q={quote_plus(search_query)}"
        serp = await scrape(serp_url, ctx)

        links = get_links_from_serp(serp["html"], search_engine, exclude_hosts)
        if not links:
            logger.warning(f"No links were extracted from {serp_url}")

        tasks = [scrape(link, ctx) for link in links[:max_results]]

        for task in asyncio.as_completed(tasks):
            try:
                result = await task
                html = result.pop("html")
                result["contents"] = convert_with_handle(html, md_handler)
                serp_results.append(result)
            except:
                # handle individual scrape exceptions, but @stamina.retry outer exceptions
                logger.exception("Could not individual extract page:")

    return serp_results


@stamina.retry(on=Error, attempts=2)
async def get_page(url: str, **chrome_kws) -> dict[str, str]:
    async with chrome(**chrome_kws) as ctx:
        result = await scrape(url, ctx)
        html = result.pop("html")
        options = ConversionOptions(skip_images=True, hocr_spatial_tables=False)
        result["contents"] = convert(html, options)
        return result
