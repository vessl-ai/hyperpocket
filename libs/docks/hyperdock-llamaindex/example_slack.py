import os
import ssl

from llama_index.core.agent import AgentRunner, FunctionCallingAgent
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.openai import OpenAI
from hyperdock_llamaindex import LlamaIndexToolRequest, dock as llamaindex_dock
from llama_index.tools.slack import SlackToolSpec
from hyperpocket.tool import from_dock, from_local
from hyperpocket_llamaindex import PocketLlamaindex

def build():
    llm = OpenAI(model="gpt-4o")
    dock = llamaindex_dock(
        LlamaIndexToolRequest(
            tool_func=SlackToolSpec.send_message,
        )
    )

    pocket = PocketLlamaindex(
        tools=[
            *from_dock(dock),
        ],
        auth={
            "auth_provider": "slack",
            "auth_handler": "slack-token",
        }
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
