import os

from llama_index.core.agent import AgentRunner, FunctionCallingAgent
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.openai import OpenAI
from hyperdock_llamaindex import LlamaIndexDock
from llama_index.tools.duckduckgo import DuckDuckGoSearchToolSpec
from hyperpocket_llamaindex import PocketLlamaindex


def build():
    llm = OpenAI(model="gpt-4o")
    tool_spec = DuckDuckGoSearchToolSpec()    
    dock = LlamaIndexDock.dock(
        tool_func=tool_spec.to_tool_list(
            spec_functions=["duckduckgo_instant_search", "duckduckgo_full_search"]
        ),
        llamaindex_tool_args={
            "max_results": 5,
        },
    )
    pocket = PocketLlamaindex(
        tools=[
            *dock,
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
