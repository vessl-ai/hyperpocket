import asyncio
from time import sleep
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from hyperpocket_langchain import PocketLangchain
from hyperpocket.tool import from_git

from prettyprint import input_user, print_agent, print_system


def simple_agent():
    p = PocketLangchain(
        tools=[
            from_git(
                "https://github.com/vessl-ai/hyperawesometools",
                "main",
                "managed-tools/slack/get-message",
            ),
        ],
    )

    tools = p.get_tools()
    llm = ChatOpenAI(model="gpt-4o")

    prompt = ChatPromptTemplate.from_messages(
        [
            ("placeholder", "{chat_history}"),
            (
                "system",
                "You are a slack insight agent. You read the messages from a slack channel and provide summaries and return insights when asked by user.",
            ),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    agent_executor = AgentExecutor(
        agent=create_tool_calling_agent(llm, tools, prompt),
        tools=tools,
        memory=ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        ),
    )

    sleep(1)  ## wait for the tool to be ready

    while True:
        user_input = input_user()
        if user_input == "q":
            print_system("Good bye!")
            break

        response = agent_executor.invoke({"input": user_input})
        print_agent(response["output"])
        print()


if __name__ == "__main__":
    simple_agent()
