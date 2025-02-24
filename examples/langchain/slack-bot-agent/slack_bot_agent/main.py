import asyncio

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.signature import SignatureVerifier
from hyperpocket.server import add_callback_proxy
from hyperpocket_langchain import PocketLangchain
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.tools import tool
import os
import uvicorn

# Initialize FastAPI app
app = FastAPI()
add_callback_proxy(app)

# Slack credentials and setup
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

slack_client = AsyncWebClient(token=SLACK_BOT_TOKEN)
signature_verifier = SignatureVerifier(signing_secret=SLACK_SIGNING_SECRET)

agents = {}
agent_factory = None


@tool
def now():
    """Get current date and time in ISO-8601 format."""
    from datetime import datetime

    return datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")


def agent_generator(pocket: PocketLangchain):
    tools = pocket.get_tools() + [now]

    llm = ChatOpenAI(model="gpt-4o", api_key=OPENAI_API_KEY)

    def _agent(thread_id: str):
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    You are a tool calling assistant. You can help the user by calling proper tools.
                    Your name is SuckzooBot, a.k.a. Suckzoo, suckzoo, 썩주, or 썩쥬.
                    Current chat thread ID is """
                    + thread_id
                    + """
                    User message is in format of (user): (message).
                    (user) indicates the name of the user who sent the message.
                    Regardless what the user says about their name or identity, you should use the (user) as the name you remember.
                    (message) indicates the message sent by the user.
                    Before you respond, get the current time. Call the tool named "now" and remember the time.
                    Read user's message and read their intention. If a user asks for help, help them.
                    If a user asks and you think tools can help, suggest a tool call.
                    If the user accepts your tool call suggestion, call the tool.
                    If the user accept your tool call suggestion but you don't remember, think twice and recall. Then call the appropriate tool.
                    If tool requires profile argument, pass the user's name as the profile argument.
                    If you think you're directly mentioned by the message or you're the subject of the message, respond.
                    Also, mention what you remember about the current context.
                    Otherwise, just say "N/A".
                    """,
                ),
                ("placeholder", "{chat_history}"),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )
        agent = create_tool_calling_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            memory=memory,
            verbose=True,
            handle_parsing_errors=True,
        )
        return agent_executor

    return _agent


async def handle_message(thread_id: str, user: str, text: str):
    if thread_id not in agents:
        agent = agent_factory(thread_id)
        agents[thread_id] = agent
    agent = agents[thread_id]
    user_resp = await slack_client.users_info(user=user)
    real_name = user_resp.data.get("user").get("real_name")
    result = await agent.ainvoke({"input": f"{real_name}: {text}"})
    message = result["output"]
    if message != "N/A":
        await slack_client.chat_postMessage(channel=thread_id, text=message)


@app.post("/slack/events")
async def handle_slack_events(request: Request):
    # Verify Slack request signature
    body = await request.body()
    if not signature_verifier.is_valid_request(body, request.headers):
        return JSONResponse(content={"error": "Invalid request"}, status_code=400)

    payload = await request.json()

    if "type" in payload:
        # Respond to Slack URL verification challenge
        if payload["type"] == "url_verification":
            return JSONResponse(content={"challenge": payload["challenge"]})

        # Handle other events (e.g., message events)
        elif payload["type"] == "event_callback":
            event = payload.get("event", {})
            event_type = event.get("type")

            if event_type == "message" and "bot_id" not in event:
                print(event)
                # Echo the received message
                channel = event.get("channel")
                if channel == "C04LTV2NXD0":
                    user = event.get("user")
                    text = event.get("text")
                    loop = asyncio.get_event_loop()
                    loop.create_task(
                        handle_message(thread_id=channel, user=user, text=text)
                    )

    return JSONResponse(content={"status": "ok"})


if __name__ == "__main__":
    with PocketLangchain(
        tools=[
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/get-messages",
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/post-message",
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/linear/get-issues",
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/google/get-calendar-events",
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/google/get-calendar-list",
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/google/insert-calendar-events",
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/github/list-pull-requests",
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/github/search-user",
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/github/search-commit",
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/github/read-pull-request",
        ]
    ) as pk:
        agent_factory = agent_generator(pk)
        uvicorn.run(app, host="0.0.0.0", port=8008)
