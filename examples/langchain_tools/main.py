from typing import Annotated

from dotenv import load_dotenv
from typing_extensions import TypedDict
from langchain_aws import ChatBedrock
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from tourist.core import TouristScraper

from scrape_tool import TouristScraperTool
from serp_tool import TouristSERPTool

# Put your credentials in .env if you're using an LLM service
load_dotenv()

# Assumes you're running locally, change this to your cloud endpoint if you've deployed.
scraper = TouristScraper("http://localhost:8000", "", concurrency=1)
search_tool = TouristSERPTool(scraper=scraper, max_results=3)
scrape_tool = TouristScraperTool(scraper=scraper)

# This example uses much of the same code from LangGraph's Quickstart tutorial:
# https://langchain-ai.github.io/langgraph/tutorials/introduction/

tools = [search_tool, scrape_tool]


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)

# IMPORTANT: please update the Chat model if you're using a different LLM.
# TODO/Contribution: Add ChatOllama once it's supported.
llm = ChatBedrock(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    model_kwargs=dict(temperature=0),
)
llm_with_tools = llm.bind_tools(tools)


def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


graph_builder.add_node("chatbot", chatbot)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)

graph_builder.add_edge("tools", "chatbot")
graph_builder.set_entry_point("chatbot")


if __name__ == "__main__":
    graph = graph_builder.compile()
    config = {"configurable": {"thread_id": "1"}}

    ##### SERP example
    serp_input = "What is the latest news around the 2024 Olympics in Paris?"
    for event in graph.stream(
        {"messages": ("user", serp_input)}, config, stream_mode="values"
    ):
        event["messages"][-1].pretty_print()

    #####
    # pause for user to review results...
    import time

    time.sleep(5)  # noqa

    ##### Scrape example
    scrape_input = (
        "Grab the table element from https://pypistats.org/top and "
        "tell me what the top 5 most downloaded python packages are."
    )
    for event in graph.stream(
        {"messages": ("user", scrape_input)}, config, stream_mode="values"
    ):
        event["messages"][-1].pretty_print()

    ### interactive mode:

    # while True:
    #     user_input = input("User: ")
    #     if user_input in ["quit", "stop", "exit", ""]:
    #         break
    #     for event in graph.stream(
    #         {"messages": ("user", user_input)}, config, stream_mode="values"
    #     ):
    #         event["messages"][-1].pretty_print()
