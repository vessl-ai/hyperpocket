import os
import getpass

from hyperpocket_langchain import PocketLangchain
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI

from hyperpocket.tool import from_git

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google AI API key: ")

def agent(pocket: PocketLangchain):
    tools = pocket.get_tools()

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
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
        print("gumloop agent : ", response["output"])
        print()


if __name__ == "__main__":
    with PocketLangchain(
            tools=[
                "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/get-message",
                "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/post-message",
            ],
    ) as pocket:
        agent(pocket)
