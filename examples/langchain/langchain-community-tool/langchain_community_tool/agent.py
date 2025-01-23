from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_community.tools import SlackGetMessage, DuckDuckGoSearchRun

from hyperdock_langchain import dock as langchain_dock, LangchainToolRequest
from hyperpocket.config import secret
from hyperpocket.tool import from_dock
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
            *from_dock(
                langchain_dock(
                    LangchainToolRequest(SlackGetMessage, auth={"auth_provider": "slack"}),
                    LangchainToolRequest(DuckDuckGoSearchRun),
                )
            )
        ],
    ) as pocket:
        agent(pocket)