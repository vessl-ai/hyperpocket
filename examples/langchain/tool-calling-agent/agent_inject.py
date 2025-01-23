from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from hyperpocket.config import secret
from hyperpocket.tool import from_git
from hyperpocket_langchain import PocketLangchain


def agent(pocket: PocketLangchain):
    tools = pocket.get_tools()

    llm = ChatOpenAI(model="gpt-4o", api_key=secret["OPENAI_API_KEY"])

    prompt = ChatPromptTemplate.from_messages(
        [
            ("placeholder", "{chat_history}"),
            (
                "system",
                "You are a tool calling assistant. You can help the user by calling proper tools",
            ),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
    )

    print("\n\n\n")
    print("Hello, this is langchain slack agent.")
    while True:
        print("user(q to quit) : ", end="")
        user_input = input()
        if user_input == "q":
            print("Good bye!")
            break

        response = agent_executor.invoke({"input": user_input})
        print("slack agent : ", response["output"])
        print()


if __name__ == "__main__":
    with PocketLangchain(
            tools=[
                from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/slack/get-message"),
                from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/slack/post-message"),
                from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/linear/get-issues"),
                from_git("https://github.com/vessl-ai/hyperawesometools", "main",
                         "managed-tools/google/get-calendar-events"),
                from_git("https://github.com/vessl-ai/hyperawesometools", "main",
                         "managed-tools/google/get-calendar-list"),
                from_git("https://github.com/vessl-ai/hyperawesometools", "main",
                         "managed-tools/google/insert-calendar-events"),
                from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/github/pr-list"),
                from_git("https://github.com/vessl-ai/hyperawesometools", "main",
                         "managed-tools/github/read-pull-request"),

            ],
            # force_update=True,
    ) as pocket:
        agent(pocket)
