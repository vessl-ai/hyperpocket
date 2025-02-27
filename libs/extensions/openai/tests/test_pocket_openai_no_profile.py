import ast
import json
import os
from unittest.async_case import IsolatedAsyncioTestCase

from openai import OpenAI
from pydantic import BaseModel

from hyperpocket.config import config
from hyperpocket_openai import PocketOpenAI


class TestPocketOpenAINoProfile(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        config.public_server_port = "https"
        config.public_hostname = "localhost"
        config.public_server_port = 8001
        config.internal_server_port = 8000
        config.enable_local_callback_proxy = True

        self.pocket = PocketOpenAI(
            tools=[
                "https://github.com/vessl-ai/hyperpocket/main/tree/tools/slack/get-messages",
                "https://github.com/vessl-ai/hyperpocket/main/tree/tools/slack/post-message",
                "https://github.com/vessl-ai/hyperpocket/main/tree/tools/none/simple-echo-tool",
                self.add,
                self.sub_pydantic_args,
            ],
            use_profile=False,
        )
        self.tool_specs = self.pocket.get_open_ai_tool_specs()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def asyncTearDown(self):
        self.pocket._teardown_server()

    def test_get_tools_from_pocket_no_profile(self):
        # when
        specs = self.pocket.get_open_ai_tool_specs()
        get_tool, send_tool = specs[0], specs[1]

        # then
        self.assertIsInstance(get_tool, dict)
        self.assertEqual(get_tool["function"]["name"], "slack_get_messages")
        self.assertTrue("channel" in get_tool["function"]["parameters"]["properties"])
        self.assertTrue("limit" in get_tool["function"]["parameters"]["properties"])

        self.assertIsInstance(send_tool, dict)
        self.assertEqual(send_tool["function"]["name"], "slack_send_messages")
        self.assertTrue("channel" in send_tool["function"]["parameters"]["properties"])
        self.assertTrue("text" in send_tool["function"]["parameters"]["properties"])

    async def test_function_tool_no_profile(self):
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "add 1, 2"}],
            tools=self.tool_specs,
        )

        choice = response.choices[0]
        tool_call = choice.message.tool_calls[0]
        name = tool_call.function.name
        args = tool_call.function.arguments
        args = json.loads(args)
        result = await self.pocket.ainvoke(tool_call)

        # then
        self.assertEqual(choice.finish_reason, "tool_calls")
        self.assertEqual(name, "add")
        self.assertEqual(args, {"a": 1, "b": 2})
        self.assertEqual(result["content"], "3")

    async def test_pydantic_function_tool_no_profile(self):
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "sub 1, 2"}],
            tools=self.tool_specs,
        )

        choice = response.choices[0]
        tool_call = choice.message.tool_calls[0]
        name = tool_call.function.name
        args = tool_call.function.arguments
        args = json.loads(args)
        result = await self.pocket.ainvoke(tool_call)

        # then
        self.assertEqual(choice.finish_reason, "tool_calls")
        self.assertEqual(name, "sub_pydantic_args")
        self.assertEqual(args, {"a": {"first": 1}, "b": {"second": 2}})
        self.assertEqual(result["content"], "-1")

    async def test_wasm_tool_no_profile(self):
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "echo 'hello world'"}],
            tools=self.tool_specs,
        )

        choice = response.choices[0]
        tool_call = choice.message.tool_calls[0]
        name = tool_call.function.name
        args = tool_call.function.arguments
        args = json.loads(args)
        result = await self.pocket.ainvoke(tool_call)
        output = ast.literal_eval(result["content"])

        # then
        self.assertEqual(choice.finish_reason, "tool_calls")
        self.assertEqual(name, "simple_echo_text")
        self.assertEqual(args, {"text": "hello world"})
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
