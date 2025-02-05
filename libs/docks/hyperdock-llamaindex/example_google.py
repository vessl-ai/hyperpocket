import os

from llama_index.core.agent import AgentRunner, FunctionCallingAgent
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.openai import OpenAI
from hyperdock_llamaindex import LlamaIndexToolRequest, dock as llamaindex_dock
from llama_index.tools.google import GmailToolSpec
from hyperpocket.tool import from_dock
from hyperpocket_llamaindex import PocketLlamaindex

def build():
    llm = OpenAI(model="gpt-4o")
    dock = llamaindex_dock(
        LlamaIndexToolRequest(
            tool_func=GmailToolSpec.search_messages,
            tool_args={
                "max_results": 10,
            },
                auth={
                "auth_provider": "google",
                "scopes": [
                    'https://www.googleapis.com/auth/gmail.readonly',
                    'https://www.googleapis.com/auth/gmail.compose',
                    ],
            }
        )
    )

    pocket = PocketLlamaindex(
        tools=[
            *from_dock(dock),
        ]
    )
    tools = pocket.get_tools()

    memory = ChatMemoryBuffer.from_defaults(chat_history=[], llm=llm)

    agent = FunctionCallingAgent.from_tools(
        tools=tools, llm=llm, memory=memory, verbose=True
    )

    return agent


def run(agent: AgentRunner):
    while True:
        print("user(q to quit) : ", end="")
        user_input = input()
        if user_input == "q":
            print("bye")
            break
        elif user_input == "":
            continue

        agent.chat(user_input)


if __name__ == "__main__":
    agent = build()
    run(agent)
