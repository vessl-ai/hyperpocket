import os

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from hyperpocket_langchain import PocketLangchain


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
    with PocketLangchain(
            tools=[
                (
                        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/weaviate/query_near_text",
                        {
                            "WCD_URL": os.getenv("WCD_URL"),
                            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
                        },
                ),
                (
                        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/weaviate/create_collection",
                        {
                            "WCD_URL": os.getenv("WCD_URL"),
                        },
                ),
                (
                        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/weaviate/import_data",
                        {
                            "WCD_URL": os.getenv("WCD_URL"),
                            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
                        },
                ),
                (
                        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/weaviate/read_all_objects",
                        {
                            "WCD_URL": os.getenv("WCD_URL"),
                        },
                ),
                (
                        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/weaviate/read_object_by_id",
                        {
                            "WCD_URL": os.getenv("WCD_URL"),
                        },
                ),
            ],
    ) as pocket:
        agent(pocket)
