import asyncio
from datetime import datetime

import pytz
import uvicorn
from fastapi import FastAPI, Request
from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import tools_condition
from langgraph.types import Command
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.signature import SignatureVerifier
from starlette.responses import JSONResponse

from hyperpocket.config import secret
from hyperpocket.server import add_callback_proxy
from hyperpocket_langgraph import PocketLanggraph
from .local_tools import fetch_user_prs_from_organization, get_user_slack_threads

slack_client = WebClient(secret["SLACK_BOT_TOKEN"])
verifier = SignatureVerifier(signing_secret=secret["SLACK_SIGNING_SECRET"])


def send_slack_message(channel, text):
    try:
        response = slack_client.chat_postMessage(channel=channel, text=text)
        return response
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")


def update_slack_message(channel, ts, text):
    try:
        slack_client.chat_update(channel=channel, text=text, ts=ts)
    except SlackApiError as e:
        print(f"Error update message: {e.response['error']}")


def get_current_utc_time() -> str:
    return datetime.now(tz=pytz.utc).strftime("%Y-%m-%dT%H:%M:%S")


def build():
    pocket = PocketLanggraph(tools=[
        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/get-message",
        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/post-message",
        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/linear/get-issues",
        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/google/get-calendar-events",
        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/google/get-calendar-list",
        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/google/insert-calendar-events",
        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/github/read-pull-requests",
        get_user_slack_threads,
        fetch_user_prs_from_organization
    ])

    llm = ChatOpenAI(model="gpt-4o", api_key=secret["OPENAI_API_KEY"], streaming=True)
    llm_with_tools = llm.bind_tools(pocket.get_tools())

    graph_builder = StateGraph(MessagesState)

    async def agent(state: MessagesState, config: RunnableConfig) -> dict:
        print('---CALL AGENT---')
        messages = state['messages']
        msg = [
            SystemMessage(
                content=f'''
[current utc time] : {config["configurable"].get("current_utc_time")}
You are an intelligent scheduling assistant. When the user asks about their schedule, your job is to fetch and organize relevant information from the following data sources:
	1.	Ongoing github pull requests (PRs).
	2.	Linear issues marked as ‘In Progress’ or ‘To Do.’
	3.	Today’s Google Calendar meeting schedule.
	4.	Slack threads authored by the user in the past week.

Before you call tools and process user asks about their schedule, you should first think what data do you know and what data is needed.
Make sure to consider the above process carefully before proceeding to the next step.

When interacting with tools:
	- Always use accurate and relevant inputs based on the data you already know.
	- If the necessary data is still unavailable to call tools, must ask the user directly for the missing information, specifying exactly what is needed.
	- Do not assume that fields with the same name (e.g., name) across different tools represent the same value or meaning. Each tool has its own data structure, and field values must be verified before use.
	- Never use placeholder or generic values such as your-name, your-name@google.com or your-organization. 
	- NEVER ATTEMPT TO FILL OR INFERENCE ANY UNSURE USER INFORMATION OR DATA NEEDED TO CALL TOOLS.

Based on the complete and accurate data:
	- Summarize their tasks and meetings for today.
	- Highlight urgent or high-priority items.
	- Provide a concise overview of upcoming tasks or issues requiring attention.
	- Schedule their tasks by proper order based on their tasks and urgency

Always ensure your response is clear, actionable, and structured, making it easy for the user to understand their current commitments and next steps.
'''
            )
        ]

        try:
            response = await llm_with_tools.ainvoke(msg + messages, config=config)
        except Exception as e:
            print("error occur : ", e)
            response = await llm_with_tools.ainvoke([messages[-1], SystemMessage(
                content=f"currently failed to calling first analyze the reason, and notify this reason to user. [reason : {e}]")])

        print(response)
        return {'messages': [response]}

    graph_builder.add_node("agent", agent)
    graph_builder.add_node("tools", pocket.get_tool_node())

    graph_builder.add_edge(START, "agent")
    graph_builder.add_conditional_edges(
        "agent",
        tools_condition,
        {
            "tools": "tools",
            END: END,
        }
    )
    graph_builder.add_edge("tools", "agent")

    memory = MemorySaver()
    return graph_builder.compile(checkpointer=memory)


def server_example(graph):
    app = FastAPI()

    conversation_paused = {}

    @app.post("/slack/events")
    async def slack_events(request: Request):
        try:
            body = await request.body()
            timestamp = request.headers.get("X-Slack-Request-Timestamp")
            signature = request.headers.get("X-Slack-Signature")

            if not verifier.is_valid_request(body,
                                             {"x-slack-signature": signature, "x-slack-request-timestamp": timestamp}):
                return JSONResponse(status_code=403, content={"detail": "Invalid request signature"})

        except Exception as e:
            return JSONResponse(status_code=400, content={"detail": f"Invalid request: {str(e)}"})

        payload = await request.json()

        # URL 검증 처리
        if "challenge" in payload:
            return {"challenge": payload["challenge"]}

        # 이벤트 처리
        if "event" in payload:
            event = payload["event"]
            print("event : ", event)
            if event.get("type") == "message" and event.get("bot_id") is None and event.get("app_id") is None:
                thread_id = event.get("user")
                if thread_id is not None:
                    text = event.get("text", "")
                    channel = event.get("channel", "")
                    response = send_slack_message(channel, "답변을 생성 중입니다..")
                    asyncio.create_task(chat(msg=text, channel=channel, ts=response.get("ts"), thread_id=thread_id))

        return {"status": "ok"}

    async def chat(msg: str, channel: str, ts: str, thread_id: str):
        config = RunnableConfig(
            recursion_limit=30,
            configurable={
                "thread_id": thread_id,
                "current_utc_time": get_current_utc_time()
            },
        )

        if conversation_paused.get(config['configurable']["thread_id"], False):
            conversation_paused.pop(config['configurable']["thread_id"])
            async for _, chunk in graph.astream(Command(resume={'action': 'continue'}), config=config,
                                                stream_mode="updates", subgraphs=True):
                if intr := chunk.get('__interrupt__'):
                    conversation_paused[config['configurable']["thread_id"]] = True
                    update_slack_message(channel=channel, text=intr[0].value, ts=ts)
                else:
                    message = list(chunk.values())[0]['messages'][-1]
                    if message.type == "ai" and message.content is not None and message.content != "":
                        update_slack_message(channel=channel, text=message.content, ts=ts)
        else:
            async for _, chunk in graph.astream({"messages": [("user", msg)]}, config=config,
                                                stream_mode="updates", subgraphs=True):
                if intr := chunk.get('__interrupt__'):
                    conversation_paused[config['configurable']["thread_id"]] = True
                    update_slack_message(channel=channel, text=intr[0].value, ts=ts)
                else:
                    message = list(chunk.values())[0]['messages'][-1]
                    if message.type == "ai" and message.content is not None and message.content != "":
                        update_slack_message(channel=channel, text=message.content, ts=ts)

    add_callback_proxy(app)
    uvicorn.run(app, host="0.0.0.0", port=8008)


if __name__ == "__main__":
    server_example(build())
