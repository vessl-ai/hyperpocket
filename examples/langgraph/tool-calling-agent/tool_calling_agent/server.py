import traceback
import uuid
from typing import Optional

import uvicorn
from fastapi import FastAPI
from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import tools_condition
from langgraph.types import Command
from pydantic import BaseModel
from starlette.responses import StreamingResponse

from hyperpocket.config import secret
from hyperpocket.tool import from_git

from hyperpocket_langgraph import PocketLanggraph


def build():
    pocket = PocketLanggraph(tools=[
        from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/slack/get-message"),
        from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/slack/post-message"),
        from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/linear/get-issues"),
        from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/google/get-calendar-events"),
        from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/google/get-calendar-list"),
        from_git("https://github.com/vessl-ai/hyperawesometools", "main",
                 "managed-tools/google/insert-calendar-events"),
        from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/github/pr-list"),
    ])

    llm = ChatOpenAI(model="gpt-4o", api_key=secret["OPENAI_API_KEY"], streaming=True)
    llm_with_tools = llm.bind_tools(pocket.get_tools())

    graph_builder = StateGraph(MessagesState)

    def agent(state) -> dict:
        print('---CALL AGENT---')
        messages = state['messages']
        msg = [
            SystemMessage(
                content='''
If you think you're done with the user's request, just express appreciation and ask
if there is anything else you can help with.
'''
            )
        ]
        response = llm_with_tools.invoke(messages + msg)
        print(response)
        return {'messages': [response]}

    async def rewrite(state) -> dict:
        print('---TRANSFORM TOOL MESSAGE---')
        messages = state['messages']
        question = messages[0].content
        tool_resp = messages[-1].content
        msg = [
            SystemMessage(
                content=f'''
Look at the input and try to reason about the underlying semantic intent / meaning.
Here is the initial question:

---
{question}
---

By your understanding, you decided to invoke a tool and you got the following response:

---
{tool_resp}
---

Answer the user what you did with the tool. It is, you have to explain what you have done,
and what is the result of the tool invocation, in a more human-friendly way.
Think twice about the context and the user's needs.
                '''
            )
        ]
        response = await llm.ainvoke(messages + msg)
        return {'messages': [response]}

    graph_builder.add_node("agent", agent)
    graph_builder.add_node("tools", pocket.get_tool_node(should_interrupt=True))
    graph_builder.add_node("rewrite", rewrite)

    graph_builder.add_edge(START, "agent")
    graph_builder.add_conditional_edges(
        "agent",
        tools_condition,
        {
            "tools": "tools",
            END: END,
        }
    )
    graph_builder.add_edge("tools", "rewrite")
    graph_builder.add_edge("rewrite", "agent")

    memory = MemorySaver()
    return graph_builder.compile(checkpointer=memory)


def server_example(graph):
    app = FastAPI()

    class Body(BaseModel):
        message: str
        thread_id: Optional[str] = None

    class Response(BaseModel):
        content: str
        type: str

    conversation_paused = {}

    @app.post("/chat")
    async def chat(body: Body) -> StreamingResponse:
        async def generate(_cfg: RunnableConfig = None):
            try:
                if conversation_paused.get(_cfg['configurable']["thread_id"], False):
                    conversation_paused.pop(_cfg['configurable']["thread_id"])
                    async for _, chunk in graph.astream(Command(resume={'action': 'continue'}), config=_cfg,
                                                        stream_mode="updates", subgraphs=True):
                        if intr := chunk.get('__interrupt__'):
                            conversation_paused[_cfg['configurable']["thread_id"]] = True
                            result = Response(content=intr[0].value, type="system")
                            yield result.model_dump_json() + "\n"
                        else:
                            message = list(chunk.values())[0]['messages'][-1]
                            if message.type == "ai" and message.content is not None and message.content != "":
                                result = Response(content=message.content, type=message.type)
                                yield result.model_dump_json() + "\n"
                else:
                    async for _, chunk in graph.astream({"messages": [("user", body.message)]}, config=_cfg,
                                                        stream_mode="updates", subgraphs=True):
                        if intr := chunk.get('__interrupt__'):
                            conversation_paused[_cfg['configurable']["thread_id"]] = True
                            result = Response(content=intr[0].value, type="system")
                            yield result.model_dump_json() + "\n"
                        else:
                            message = list(chunk.values())[0]['messages'][-1]
                            if message.type == "ai" and message.content is not None and message.content != "":
                                result = Response(content=message.content, type=message.type)
                                yield result.model_dump_json() + "\n"
            except Exception as e:
                print(traceback.print_exc())
                yield {"error": str(e)}

        thread_id = body.thread_id if body.thread_id else str(uuid.uuid4())
        config = RunnableConfig(
            recursion_limit=30,
            configurable={"thread_id": thread_id},
        )
        return StreamingResponse(
            generate(config),
            media_type="text/event-stream",
            headers={"X-Pocket-Langgraph-Thread-Id": thread_id},
        )

    uvicorn.run(app, host="0.0.0.0", port=8008)


def main():
    server_example(build())


if __name__ == "__main__":
    main()
