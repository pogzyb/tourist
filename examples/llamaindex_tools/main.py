from llama_index.core.agent import ReActAgent
from llama_index.llms.ollama import Ollama
from llama_index.core.tools import FunctionTool

from tourist.client import TouristScraper


tourist_scraper = TouristScraper(
    base_url="http://localhost:8000",
    x_api_key="supersecret",
)


def search(query: str) -> str:
    """Search places, items, people, or current events online."""
    serp_result = tourist_scraper.get_serp(query, max_results=2)
    return "\n\n".join([r["contents"] for r in serp_result])


search_tool = FunctionTool.from_defaults(fn=search)

llm = Ollama(
    base_url="http://localhost:11434",
    model="llama3.1:8b",
    request_timeout=120.0,
)

agent = ReActAgent.from_tools(
    [multiply_tool, add_tool, search_tool], llm=llm, verbose=True
)

results = agent.chat("Give me a summary of the latest news on this NFL season.")
print(results.response)
