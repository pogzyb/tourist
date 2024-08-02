from typing import Optional, Type

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool
from tourist.core import TouristScraper


class TouristSERPInput(BaseModel):
    query: str = Field(description="Should be a search term.")


class TouristSERPTool(BaseTool):
    name = "tourist_serp"
    description: str = (
        "A search tool. "
        "Useful for when you need to answer questions about current events, people, places, or things. "
        "Input should be a search query."
    )
    args_schema: Type[BaseModel] = TouristSERPInput
    scraper: TouristScraper
    error_message = "Could not retrieve information. Try again."
    max_results: int = 5

    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        if results := self.scraper.get_serp(query, self.max_results):
            return " ".join([r["content"] for r in results])
        else:
            return self.error_message

    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        if results := await self.scraper.aget_serp(query, self.max_results):
            return " ".join([r["content"] for r in results])
        else:
            return self.error_message
