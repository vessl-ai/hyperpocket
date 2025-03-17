import asyncio
from llama_index.core.agent import AgentRunner, FunctionCallingAgent
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.openai import OpenAI
from hyperdock_llamaindex import LlamaIndexDock
from llama_index.tools.google import GmailToolSpec
from hyperpocket_llamaindex import PocketLlamaindex

async def _build():
    llm = OpenAI(model="gpt-4o")
    tool_spec = GmailToolSpec()
    
    # Case 1: with llamaindex auth
    dock = LlamaIndexDock.dock(
        tool_func=tool_spec.to_tool_list(
            spec_functions=["search_messages"]
        ),
        llamaindex_tool_args={
            "max_results": 10,
        },      
    )
    pocket = PocketLlamaindex(
        tools=[
            dock,
        ],
    )
    tools = pocket.get_tools()
    
    # authenticate with llamaindex tool oauth process
    print("Case 1: with llamaindex auth")
    prepare_url = await pocket.initialize_tool_auth()

    for provider, url in prepare_url.items():
        print(f"[{provider}]\n\t{url}")

    await pocket.wait_tool_auth()
    
    # @TODO Case 2: with pocket auth

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
    agent = asyncio.run(_build())
    run(agent)
