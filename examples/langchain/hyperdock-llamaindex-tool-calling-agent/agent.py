import os

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from hyperdock_llamaindex.dock_llamaindex import DockLlamaindex
from hyperpocket.auth import AuthProvider
from hyperpocket.tool import ToolAuth
from hyperpocket_langchain import PocketLangchain

from llama_index.tools.yahoo_finance import YahooFinanceToolSpec
from llama_index.tools.duckduckgo import DuckDuckGoSearchToolSpec


def agent(pocket: PocketLangchain):
    tools = pocket.get_tools()

    llm = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))

    prompt = ChatPromptTemplate.from_messages(
        [
            ("placeholder", "{chat_history}"),
            (
                "system",
                "You are a tool calling assistant. You can help the user by calling proper tools",
            ),
            ("placeholder", "{chat_history}"),
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
    llama_yahoo_finance_tools = [
        DockLlamaindex.to_pocket_function_tool(
            tool, auth=ToolAuth(auth_provider=AuthProvider.SLACK)) for tool in YahooFinanceToolSpec().to_tool_list()]

    llama_duckduckgo_tools = [
        DockLlamaindex.to_pocket_function_tool(tool) for tool in DuckDuckGoSearchToolSpec().to_tool_list()]

    with PocketLangchain(
            tools=[
                *llama_yahoo_finance_tools,
                *llama_duckduckgo_tools
            ],
    ) as pocket:
        agent(pocket)
