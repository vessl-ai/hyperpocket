from time import sleep
from llama_index.core.agent import AgentRunner, FunctionCallingAgent
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.openai import OpenAI
from hyperpocket.tool import from_git
from hyperpocket_llamaindex import PocketLlamaindex

from prettyprint import input_user, print_system


def build():
    llm = OpenAI()
    p = PocketLlamaindex(
        tools=[
            from_git(
                "https://github.com/vessl-ai/hyperawesometools",
                "main",
                "managed-tools/slack/get-message",
            ),
        ]
    )
    tools = p.get_tools()

    memory = ChatMemoryBuffer.from_defaults(chat_history=[], llm=llm)

    agent = FunctionCallingAgent.from_tools(
        tools=tools, llm=llm, memory=memory, verbose=True
    )

    return agent


def run(agent: AgentRunner):
    sleep(1)  ## wait for the tool to be ready

    while True:
        user_input = input_user()
        if user_input == "q":
            print_system("bye")
            break
        elif user_input == "":
            continue

        agent.chat(user_input)


if __name__ == "__main__":
    agent = build()
    run(agent)
