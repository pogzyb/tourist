from llama_index.core.agent import ReActAgent
from llama_index.llms.ollama import Ollama
from llama_index.core.tools import FunctionTool

from tourist.client import TouristScraper


tourist_scraper = TouristScraper(
    base_url="http://localhost:8000",
    secret="",
    concurrency=1,
)


def multiply(a: float, b: float) -> float:
    """Multiply two numbers and returns the product"""
    return a * b


multiply_tool = FunctionTool.from_defaults(fn=multiply)


def add(a: float, b: float) -> float:
    """Add two numbers and returns the sum"""
    return a + b


add_tool = FunctionTool.from_defaults(fn=add)


def search(query: str) -> str:
    """Search places, items, people, or current events online."""
    serp_result = tourist_scraper.get_serp(query, max_results=1)
    return " ".join([r["content"] for r in serp_result])


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

results = agent.chat("What is 8 + 8 doubled?")
print(results.response)
