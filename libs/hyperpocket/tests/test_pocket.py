from unittest.async_case import IsolatedAsyncioTestCase

from pydantic import BaseModel

from hyperpocket import Pocket
from hyperpocket.config import config
from hyperpocket.tool import from_git


class TestPocket(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.profile = "test-profile"
        self.thread_id = "test_thread_id"

        config.public_server_port = "https"
        config.public_hostname = "localhost"
        config.public_server_port = 8001
        config.internal_server_port = 8000
        config.enable_local_callback_proxy = True

        self.pocket = Pocket(
            tools=[
                from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/simple-echo-tool"),
                self.add,
                self.add_pydantic_args
            ],
        )

    async def test_function_tool(self):
        # given
        tool_name = "add"

        # when
        result = await self.pocket.ainvoke(
            tool_name=tool_name,
            body={
                "a": 1,
                "b": 3
            },
            thread_id=self.thread_id,
            profile=self.profile,
        )

        # then
        self.assertEqual(result, "4")

    async def test_pydantic_arg_function_tool(self):
        # given
        tool_name = "add_pydantic_args"

        # when
        result = await self.pocket.ainvoke(
            tool_name=tool_name,
            body={
                "a": {
                    "first": 1
                },
                "b": {
                    "second": 3
                }
            },
            thread_id=self.thread_id,
            profile=self.profile,
        )

        # then
        self.assertEqual(result, "4")

    async def test_wasm_tool(self):
        # given
        tool_name = "simple_echo_text"

        # when
        result = await self.pocket.ainvoke(
            tool_name=tool_name,
            body={
                "text": "test"
            },
            thread_id=self.thread_id,
            profile=self.profile,
        )

        # then
        self.assertTrue(result.startswith("echo message : test"))

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
    def add_pydantic_args(a: FirstNumber, b: SecondNumber):
        """
        Add two numbers

        Args:
            a(FirstNumber): first number
            b(SecondNumber): second number
        """
        return a.first + b.second
