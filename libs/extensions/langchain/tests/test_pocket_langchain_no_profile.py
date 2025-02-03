import ast
import os
from unittest.async_case import IsolatedAsyncioTestCase

from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from hyperpocket.config import config
from hyperpocket_langchain.pocket_langchain import PocketLangchain


class TestPocketLangchainNoProfile(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        config.public_server_port = "https"
        config.public_hostname = "localhost"
        config.public_server_port = 8001
        config.internal_server_port = 8000
        config.enable_local_callback_proxy = True

        self.pocket = PocketLangchain(
            tools=[
                "https://github.com/vessl-ai/hyperpocket/main/tree/tools/none/simple-echo-tool",
                self.add,
                self.sub_pydantic_args,
            ],
        )

        self.llm_no_profile = ChatOpenAI(
            model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY")
        ).bind_tools(tools=self.pocket.get_tools(use_profile=False))

    async def asyncTearDown(self):
        self.pocket._teardown_server()

    async def test_function_tool_no_profile(self):
        # when
        response = await self.llm_no_profile.ainvoke(
            [{"role": "user", "content": "add 1, 2"}]
        )

        kwargs = response.tool_calls[0]["args"]
        thread_id = kwargs.pop("thread_id", "default")
        profile = kwargs.pop("profile", "default")
        body = kwargs

        result = await self.pocket.ainvoke(
            tool_name=response.tool_calls[0]["name"],
            body=body,
            thread_id=thread_id,
            profile=profile,
        )

        # then
        self.assertEqual(response.tool_calls[0]["name"], "add")
        self.assertEqual(response.tool_calls[0]["args"]["a"], 1)
        self.assertEqual(response.tool_calls[0]["args"]["b"], 2)
        self.assertEqual(result, "3")

    async def test_pydantic_function_tool_no_profile(self):
        # when
        response = await self.llm_no_profile.ainvoke(
            [{"role": "user", "content": "sub 1, 2"}]
        )

        kwargs = response.tool_calls[0]["args"]
        thread_id = kwargs.pop("thread_id", "default")
        profile = kwargs.pop("profile", "default")
        body = kwargs

        result = await self.pocket.ainvoke(
            tool_name=response.tool_calls[0]["name"],
            body=body,
            thread_id=thread_id,
            profile=profile,
        )

        # then
        self.assertEqual(response.tool_calls[0]["name"], "sub_pydantic_args")
        self.assertEqual(response.tool_calls[0]["args"]["a"]["first"], 1)
        self.assertEqual(response.tool_calls[0]["args"]["b"]["second"], 2)
        self.assertEqual(result, "-1")

    async def test_wasm_tool_no_profile(self):
        # when
        response = await self.llm_no_profile.ainvoke(
            [{"role": "user", "content": "echo 'hello world'"}]
        )

        kwargs = response.tool_calls[0]["args"]
        thread_id = kwargs.pop("thread_id", "default")
        profile = kwargs.pop("profile", "default")
        body = kwargs

        result = await self.pocket.ainvoke(
            tool_name=response.tool_calls[0]["name"],
            body=body,
            thread_id=thread_id,
            profile=profile,
        )
        output = ast.literal_eval(result)

        # then
        self.assertEqual(response.tool_calls[0]["name"], "simple_echo_text")
        self.assertEqual(response.tool_calls[0]["args"]["text"], "hello world")
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
