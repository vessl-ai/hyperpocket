from logging import getLogger

import asyncio
from typing import List

from llama_index.core.llms import ChatMessage
from llama_index.core.memory import ChatMemoryBuffer
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
from llama_index.tools.yahoo_finance import YahooFinanceToolSpec
from hyperpocket.tool import from_dock, from_func
from hyperpocket_llamaindex import PocketLlamaindex
from hyperpocket.server.server import PocketServer
from .workflow_duckduckgo import DuckDuckGoWorkflow


logger = getLogger(__name__)

class ChatEvent(Event):
    chat_history: List[ChatMessage]

class YahooFinanceWorkflow(Workflow):
    llm: OpenAI = OpenAI(model="gpt-4o")
    
    @step
    async def prepare_chat_history(self, ctx: Context, ev: StartEvent) -> ChatEvent:
        logger.info(f"Preparing chat history: {ev}")

        current_chat_history = await ctx.get("chat_history", [])

        newest_msg = ev.get("message")
        if not newest_msg:
            raise ValueError("No `message` input provided!")

        current_chat_history.append({"role": "user", "content": newest_msg})
        await ctx.set("chat_history", current_chat_history)

        memory = ChatMemoryBuffer.from_defaults(
            chat_history=[ChatMessage(**x) for x in current_chat_history],
            llm=OpenAI(model="gpt-4o-mini"),
        )

        processed_chat_history = memory.get()

        return ChatEvent(chat_history=processed_chat_history)
    
    @step
    async def yahoo_chat(
        self, ctx: Context, ev: ChatEvent, duckduckgo_workflow: DuckDuckGoWorkflow
    ) -> StopEvent:
        chat_history = ev.chat_history

        async def run_query(message: str) -> str:
            """
            Query DuckDuckGo for the user's message.
            """
            
            response = await duckduckgo_workflow.run(message=message)
            return str(response)
        
        async def return_response(response: str) -> str:
            """Useful for returning a direct response to the user."""
            return response

        dock = llamaindex_dock(
            LlamaIndexToolRequest(
                tool_func=YahooFinanceToolSpec().stock_basic_info,
            )
        )
        
        pocket = PocketLlamaindex(
            tools=[
                *from_dock(dock),
                from_func(func=run_query, afunc=run_query),
                from_func(func=return_response, afunc=return_response),
            ],
            server=PocketServer(
                internal_server_port=8006,
                proxy_port=8005
            )
        )
        tools = pocket.get_tools()
        

        # responds using the tool or the LLM directly
        response = await self.llm.apredict_and_call(
            tools=tools,
            chat_history=chat_history,
            error_on_no_tool_call=False,
        )

        # update the chat history in the context
        current_chat_history = await ctx.get("chat_history", [])
        current_chat_history.append({"role": "assistant", "content": response.response})
        await ctx.set("chat_history", current_chat_history)

        return StopEvent(result=response.response)

def build_yahoo_finance_workflow() -> YahooFinanceWorkflow:
    return YahooFinanceWorkflow(timeout=120.0)
    
def build_agentic_workflow(duckduckgo_workflow: DuckDuckGoWorkflow) -> YahooFinanceWorkflow:
    yahoo_finance_workflow = YahooFinanceWorkflow(timeout=120.0)

    # add the rag workflow as a subworkflow
    yahoo_finance_workflow.add_workflows(duckduckgo_workflow=duckduckgo_workflow)

    return yahoo_finance_workflow