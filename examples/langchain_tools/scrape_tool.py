from typing import Optional, Type

from bs4 import BeautifulSoup
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool
from tourist.core import TouristScraper


# HTML pages are huge, so we want to avoid sending too much input to the model.
# This helper function is specific to this example, but most scraper scripts will need
# something like this when parsing HTML in the "Wild".
def trim_content(html: str):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(True):
        if tag.name in ("style", "script", "svg"):
            # keep the meaning of the tag, but remove its contents to save space
            tag.string = ""
    return str(soup)


class TouristScraperInput(BaseModel):
    url: str = Field(description="Should be a valid URL.")


class TouristScraperTool(BaseTool):
    name = "tourist_scrape"
    description = (
        "A web scraper. "
        "Useful for when you need to answer questions related the contents of a website or URL. "
        "Input should be a URL."
    )
    args_schema: Type[BaseModel] = TouristScraperInput
    scraper: TouristScraper
    error_message = "Could not scrape that URL. Try again."

    def _run(
        self, url: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        if source_html := self.scraper.get_page(url).get("source_html"):
            return trim_content(source_html)
        else:
            return self.error_message

    async def _arun(
        self, url: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        if source_html := await self.scraper.aio_get_page(url).get("source_html"):
            return trim_content(source_html)
        else:
            return self.error_message
