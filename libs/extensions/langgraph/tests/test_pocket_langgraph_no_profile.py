import ast
import os
from unittest.async_case import IsolatedAsyncioTestCase

from langchain_openai import ChatOpenAI
from langgraph.constants import END, START
from langgraph.graph import MessagesState, StateGraph
from langgraph.prebuilt import tools_condition
from pydantic import BaseModel

from hyperpocket.config import config
from hyperpocket_langgraph import PocketLanggraph


class TestPocketLanggraphNoProfile(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        config.public_server_port = "https"
        config.public_hostname = "localhost"
        config.public_server_port = 8001
        config.internal_server_port = 8000
        config.enable_local_callback_proxy = True

        self.pocket = PocketLanggraph(
            tools=[
                "https://github.com/vessl-ai/hyperpocket/main/tree/tools/none/simple-echo-tool",
                self.add,
                self.sub_pydantic_args,
            ],
            use_profile=False,
        )
        tools = self.pocket.get_tools()
        tool_node = self.pocket.get_tool_node()
        self.llm = ChatOpenAI(
            model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY")
        ).bind_tools(tools=tools)

        def chatbot(state: MessagesState):
            return {"messages": [self.llm.invoke(state["messages"])]}

        graph_builder = StateGraph(MessagesState)

        graph_builder.add_node("chat", chatbot)
        graph_builder.add_node("tools", tool_node)
        graph_builder.add_conditional_edges("chat", tools_condition)

        graph_builder.add_edge("tools", "chat")
        graph_builder.add_edge(START, "chat")
        graph_builder.add_edge("chat", END)

        self.graph = graph_builder.compile()

    async def asyncTearDown(self):
        self.pocket._teardown_server()

    async def test_function_tool_no_profile(self):
        # when
        response = await self.graph.ainvoke({"messages": [("user", "add 1, 2")]})

        tool_call = response["messages"][1]
        tool_result = response["messages"][2]

        # then
        self.assertEqual(tool_call.tool_calls[0]["name"], "add")
        self.assertEqual(tool_call.tool_calls[0]["args"], {"a": 1, "b": 2})
        self.assertEqual(tool_result.content, "3")

    async def test_pydantic_function_tool_no_profile(self):
        # when
        response = await self.graph.ainvoke({"messages": [("user", "sub 1, 2")]})

        tool_call = response["messages"][1]
        tool_result = response["messages"][2]

        # then
        self.assertEqual(tool_call.tool_calls[0]["name"], "sub_pydantic_args")
        self.assertEqual(
            tool_call.tool_calls[0]["args"], {"a": {"first": 1}, "b": {"second": 2}}
        )
        self.assertEqual(tool_result.content, "-1")

    async def test_wasm_tool_no_profile(self):
        # when
        response = await self.graph.ainvoke(
            {"messages": [("user", "echo 'hello world'")]}
        )

        tool_call = response["messages"][1]
        tool_result = response["messages"][2]

        output = ast.literal_eval(tool_result.content)

        # then
        self.assertEqual(tool_call.tool_calls[0]["name"], "simple_echo_text")
        self.assertEqual(tool_call.tool_calls[0]["args"], {"text": "hello world"})
        self.assertTrue(output["stdout"].startswith("echo message : hello world"))

    @staticmethod
    def add(a: int, b: int) -> int:
        """
        Add two numbers

        Args:
            a(int): first number
            b(int): second number

        """

        return a + b

    class FirstNumber(BaseModel):
        first: int

    class SecondNumber(BaseModel):
        second: int

    @staticmethod
    def sub_pydantic_args(a: FirstNumber, b: SecondNumber):
        """
        sub two numbers

        Args:
            a(FirstNumber): first number
            b(SecondNumber): second number
        """
        return a.first - b.second
