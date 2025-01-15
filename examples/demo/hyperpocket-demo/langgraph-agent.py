import asyncio
from time import sleep
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import tools_condition

from hyperpocket.tool import from_git
from hyperpocket_langgraph import PocketLanggraph

from prettyprint import print_agent, input_user


async def agent():
    p = PocketLanggraph(
        tools=[
            from_git(
                "https://github.com/vessl-ai/hyperawesometools",
                "main",
                "managed-tools/slack/get-message",
            ),
        ]
    )

    llm = ChatOpenAI(model="gpt-4o")
    llm_with_tools = llm.bind_tools(p.get_tools())

    graph_builder = StateGraph(MessagesState)

    def agent(state) -> dict:
        print("---CALL AGENT---")
        messages = state["messages"]
        msg = [
            SystemMessage(
                content=f"""
You are a slack insight agent. You read the messages from a slack channel and provide summaries and return insights when asked by user.
    """
            )
        ]
        response = llm_with_tools.invoke(messages + msg)
        print(response)
        return {"messages": [response]}

    graph_builder.add_node("agent", agent)
    graph_builder.add_node("tools", p.get_tool_node())

    graph_builder.add_edge(START, "agent")
    graph_builder.add_conditional_edges(
        "agent",
        tools_condition,
        {
            "tools": "tools",
            END: END,
        },
    )
    graph_builder.add_edge("tools", "agent")

    memory = MemorySaver()

    workflow = graph_builder.compile(checkpointer=memory)

    sleep(1)  ## wait for the tool to be ready

    while True:
        user_input = input_user()
        if user_input == "q":
            print("Good bye!")
            break

        response = await workflow.ainvoke(
            {"messages": [user_input]}, {"configurable": {"thread_id": "123"}}
        )
        print_agent(response["messages"][-1].content)
        print()


if __name__ == "__main__":
    asyncio.run(agent())
