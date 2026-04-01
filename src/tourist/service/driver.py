import asyncio
import json
import logging
import random
import shutil
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path
from tempfile import mkdtemp
from typing import Literal
from urllib.parse import quote_plus

from html_to_markdown import ConversionOptions, convert
from patchright.async_api import (
    TimeoutError as PlaywrightTimeoutError,
    async_playwright,
)

from .utils import get_links_from_serp

logger = logging.getLogger("uvicorn.error")


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
                    "--renderer-process-limit=2",
                    f"--data-path={data_path}",
                    f"--disk-cache-dir={disk_cache_dir}",
                    "--ignore-certificate-errors",
                    "--remote-debugging-port=9222",
                ],
            )
            yield context
            await context.close()


# CREDIT: https://github.com/dumkydewilde/consentcrawl/blob/main/consentcrawl/crawl.py
async def handle_cookie_preferences(page) -> None:
    current_dir = Path(__file__).parent.resolve()
    with open(current_dir / "assets/cookie-managers.json", "r") as f:
        cookie_managers = json.load(f)

    for manager in cookie_managers:
        parent_locator = page
        locator: "Locator" = None

        actions = manager.get("actions", [])
        for action in actions:
            if action["type"] == "iframe":
                if await parent_locator.locator(action["value"]).count() > 0:
                    parent_locator = parent_locator.frame_locator(action["value"]).first
                else:
                    continue
            elif action["type"] == "css-selector":
                if await parent_locator.locator(action["value"]).first.is_visible():
                    locator = parent_locator.locator(action["value"])
                    break
            elif action["type"] == "css-selector-list":
                for selector in action["value"]:
                    if await parent_locator.locator(selector).first.is_visible():
                        locator = parent_locator.locator(selector)
                        # manager["selector-list-item"] = selector
                        break

        if locator is not None:
            try:
                # explicit wait for navigation as some pages will reload after accepting cookies
                # async with page.expect_navigation(wait_until="networkidle", timeout=15000):
                await locator.first.click(delay=10)
                logger.info(f"Accepted cookie preferences: {manager['name']}")
                return

            except (PlaywrightTimeoutError, Exception):
                logger.exception(
                    f"Could not handle cookie preferences: {manager['name']}"
                )
                continue


async def scrape(url: str, ctx: "BrowserContext") -> dict[str, str]:
    page = None
    try:
        page = await ctx.new_page()
        await page.route(
            "**/*",
            lambda route: route.abort()
            if route.request.resource_type == "image"
            else route.continue_(),
        )
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await page.mouse.move(333, 888)
        await page.mouse.wheel(0, -111)
        await handle_cookie_preferences(page)
        await page.wait_for_timeout(random.randint(1000, 2500))
        scraped_page = {
            "title": await page.title(),
            "html": await page.content(),
            "current_url": page.url,
            "requested_url": url,
        }
        return scraped_page
    except PlaywrightTimeoutError as e:
        raise e
    finally:
        if page is not None:
            await page.close()


async def get_serp_results(
    search_query: str,
    search_engine: Literal["brave", "duckduckgo"],
    exclude_hosts: list[str],
    max_results: int = 5,
    **chrome_kws,
) -> list[dict[str, str]]:
    serp_results: list[dict[str, str]] = []
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
                result["contents"] = convert(
                    html, ConversionOptions(skip_images=True)
                ).get("content")
                serp_results.append(result)
            except:
                logger.exception("Could not individual extract page:")
    return serp_results


async def get_page(url: str, **chrome_kws) -> dict[str, str]:
    async with chrome(**chrome_kws) as ctx:
        result = await scrape(url, ctx)
        html = result.pop("html")
        options = ConversionOptions(skip_images=True)
        result["contents"] = convert(html, options).get("content")
        return result
