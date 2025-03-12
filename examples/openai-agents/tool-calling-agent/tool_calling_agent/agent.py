from agents import Agent, Runner, WebSearchTool, trace, FunctionTool

import os

from openai import OpenAI
from hyperpocket_openai import PocketOpenAI
import asyncio
from util import convert_to_openai_agent_tool

def agent():
    pocket = PocketOpenAI(
        tools=[
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/post-message",
        ]
    )
    tool_specs = pocket.get_open_ai_tool_specs()
    
    loop = asyncio.new_event_loop()

    prepare_url = loop.run_until_complete(pocket.initialize_tool_auth())

    for provider, url in prepare_url.items():
        print(f"[{provider}]\n\t{url}")

    loop.run_until_complete(pocket.wait_tool_auth())
    
    tool_specs = [convert_to_openai_agent_tool(spec) for spec in tool_specs]
    
    agent = Agent(
        name="Web searcher",
        instructions="You are a helpful agent.",
        tools=[
            WebSearchTool(user_location={"type": "approximate", "city": "New York"}),
            *tool_specs,],
    )
    
    with trace("Web search example"):
        result = Runner.run_sync(
            agent, "search about the latest news of LLM and send summary to the slack channel engr-test with Title 'LLM News with OpenAI agents'",
        )
        print(result.final_output)

if __name__ == "__main__":
    agent()
