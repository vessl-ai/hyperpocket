from unittest.async_case import IsolatedAsyncioTestCase

from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from hyperpocket.config import config, secret
from hyperpocket.tool import from_git
from hyperpocket_langchain.pocket_langchain import PocketLangchain


class TestPocketLangchain(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        config.public_server_port = "https"
        config.public_hostname = "localhost"
        config.public_server_port = 8001
        config.internal_server_port = 8000
        config.enable_local_callback_proxy = True

        self.pocket = PocketLangchain(
            tools=[
                from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/simple-echo-tool"),
                self.add,
                self.sub_pydantic_args
            ],
        )
        tools = self.pocket.get_tools()
        self.llm = ChatOpenAI(model="gpt-4o", api_key=secret["OPENAI_API_KEY"]).bind_tools(tools=tools)

    async def test_function_tool(self):
        # when
        response = await self.llm.ainvoke([{
            "role": "user",
            "content": "add 1, 2"
        }])

        result = await self.pocket.ainvoke(
            tool_name=response.tool_calls[0]["name"],
            body=response.tool_calls[0]["args"]["body"]
        )

        # then
        self.assertEqual(response.tool_calls[0]["name"], "add")
        self.assertEqual(response.tool_calls[0]["args"]["body"]["a"], 1)
        self.assertEqual(response.tool_calls[0]["args"]["body"]["b"], 2)
        self.assertEqual(result, "3")

    async def test_pydantic_function_tool(self):
        # when
        response = await self.llm.ainvoke([{
            "role": "user",
            "content": "sub 1, 2"
        }])

        result = await self.pocket.ainvoke(
            tool_name=response.tool_calls[0]["name"],
            body=response.tool_calls[0]["args"]["body"]
        )

        # then
        self.assertEqual(response.tool_calls[0]["name"], "sub_pydantic_args")
        self.assertEqual(response.tool_calls[0]["args"]["body"]["a"]["first"], 1)
        self.assertEqual(response.tool_calls[0]["args"]["body"]["b"]["second"], 2)
        self.assertEqual(result, "-1")

    async def test_wasm_tool(self):
        # when
        response = await self.llm.ainvoke([{
            "role": "user",
            "content": "echo 'hello world'"
        }])

        result = await self.pocket.ainvoke(
            tool_name=response.tool_calls[0]["name"],
            body=response.tool_calls[0]["args"]["body"]
        )

        # then
        self.assertEqual(response.tool_calls[0]["name"], "simple_echo_text")
        self.assertEqual(response.tool_calls[0]["args"]["body"]["text"], "hello world")
        self.assertTrue(result.startswith("echo message : hello world"))

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
