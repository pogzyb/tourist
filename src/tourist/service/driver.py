from contextlib import asynccontextmanager
from urllib.parse import quote_plus
from typing import LiteralString

from patchright.async_api import async_playwright, Playwright
from html_to_markdown import (
    ConversionOptions,
    convert_with_handle,
    create_options_handle,
)

from service.utils import get_links_from_serp


@asynccontextmanager
async def chrome(**kws):
    async with async_playwright(**kws) as playwright:
        browser = playwright.chrome
        context = await browser.new_context()
        yield context
        await context.close()
        await browser.close()


async def scrape(url, ctx) -> dict[str, str]:
    page = await ctx.new_page()
    await page.goto(url)
    return {
        "title": page.title(),
        "html": await page.content(),
        "current_url": page.url(),
        "requested_url": url,
    }


async def get_page(url: str, **chrome_kws) -> dict[str, str]:
    async with chrome(**chrome_kws) as ctx:
        result = await scrape(url, ctx)
        html = result.pop("html")
        result["contents"] = convert(html)
        return result


async def get_serp_results(
    query: str,
    engine: LiteralString["google", "bing"],
    exclude_hosts: list[str],
    max_results: int = 5,
    **chrome_kws,
) -> list[dict[str, str]]:
    serp_results = []
    handle = create_options_handle(ConversionOptions(hocr_spatial_tables=False))
    async with chrome(**chrome_kws) as ctx:
        serp = await get_page(f"https://google.com/search?q={quote_plus(query)}", ctx)
        links = get_links_from_serp(serp["html"], engine, exclude_hosts)[:max_results]
        for task in asyncio.as_completed([scrape(link, ctx) for link in links]):
            result = await task
            html = result.pop("html")
            result["contents"] = convert_with_handle(html, handle)
            serp_results.append(result)
    return serp_results
