from logging import getLogger

from typing import List

from llama_index.core.llms import ChatMessage
from hyperpocket_llamaindex import PocketLlamaindex
from llama_index.core.workflow import (
    Context,
    Event,
    StartEvent,
    StopEvent,
    Workflow,
    step,
)
from llama_index.llms.openai import OpenAI

from hyperdock_llamaindex import LlamaIndexToolRequest, dock as llamaindex_dock
from llama_index.tools.duckduckgo import DuckDuckGoSearchToolSpec
from hyperpocket.tool import from_dock
from hyperpocket.config import config
from hyperpocket.server.server import PocketServer
from hyperpocket_llamaindex import PocketLlamaindex


logger = getLogger(__name__)

class DuckDuckGoWorkflow(Workflow):
    llm: OpenAI = OpenAI(model="gpt-4o")

    @step
    async def duckduckgo_chat(
        self, ctx: Context, ev: StartEvent, 
    ) -> StopEvent:
        message = ChatMessage(str(ev.get("message", "")))
        
        dock = llamaindex_dock(
            LlamaIndexToolRequest(
                tool_func=DuckDuckGoSearchToolSpec().duckduckgo_full_search,
                tool_args={
                    "max_results": 10,
                },
            )
        )
        
        pocket = PocketLlamaindex(
            tools=[
                *from_dock(dock),
            ],
            server=PocketServer(
                internal_server_port=8004,
                proxy_port=8003
            )
        )
        tools = pocket.get_tools()

        # responds using the tool or the LLM directly
        response = await self.llm.apredict_and_call(
            tools=tools,
            user_msg=message,
            error_on_no_tool_call=False,
        )

        # update the chat history in the context
        current_chat_history = await ctx.get("chat_history", [])
        current_chat_history.append({"role": "assistant", "content": response.response})
        await ctx.set("chat_history", current_chat_history)

        return StopEvent(result=str(response.response))


def build_duckduckgo_workflow() -> DuckDuckGoWorkflow:
    return DuckDuckGoWorkflow(timeout=120.0)