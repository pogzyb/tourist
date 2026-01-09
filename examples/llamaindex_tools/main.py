import asyncio

from llama_index.llms.ollama import Ollama
from llama_index.core.agent.workflow import FunctionAgent
from tourist.client import TouristScraper


tourist_scraper = TouristScraper(
    func_urls="http://localhost:8000",
    x_api_key="whatever",
)


async def search(query: str):
    """Search places, items, people, or current events online."""
    serp_result = await tourist_scraper.aget_serp(query, search_engine="bing", max_results=2)
    return serp_result
 

async def main():
    llm = Ollama(model="ministral-3:3b", request_timeout=120.0)

    agent = FunctionAgent(
        tools=[search],
        llm=llm,
        system_prompt="You are a helpful assistant that can search the web for information.",
        verbose=True,
    )

    response = await agent.run(user_msg="What's going on with the College Football Playoff?")
    print(str(response))


if __name__ == "__main__":
    asyncio.run(main())
