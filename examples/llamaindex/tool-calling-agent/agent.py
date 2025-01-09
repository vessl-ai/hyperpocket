from llama_index.core.agent import AgentRunner, FunctionCallingAgent
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.openai import OpenAI
from hyperpocket.config import secret
from hyperpocket.tool import from_git

from hyperpocket_llamaindex import PocketLlamaindex


def build():
    llm = OpenAI(api_key=secret["OPENAI_API_KEY"])
    pocket = PocketLlamaindex(
        tools=[
            from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/slack/get-message"),
            from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/slack/post-message"),
            from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/linear/get-issues"),
            from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/google/get-calendar-events"),
            from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/google/get-calendar-list"),
            from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/google/insert-calendar-events"),
            from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/github/pr-list"),
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
