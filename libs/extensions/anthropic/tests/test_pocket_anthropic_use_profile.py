import ast
import os
from unittest.async_case import IsolatedAsyncioTestCase

from anthropic import Anthropic
from pydantic import BaseModel

from hyperpocket.config import config
from hyperpocket_anthropic import PocketAnthropic


class TestPocketAnthropicUseProfile(IsolatedAsyncioTestCase):
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

    async def asyncSetUp(self):
        config.public_server_port = "https"
        config.public_hostname = "localhost"
        config.public_server_port = 8001
        config.internal_server_port = 8000
        config.enable_local_callback_proxy = True

        self.pocket = PocketAnthropic(
            tools=[
                "https://github.com/vessl-ai/hyperpocket/main/tree/tools/none/simple-echo-tool",
                self.add,
                self.sub_pydantic_args,
            ],
        )
        self.tool_specs_use_profile = self.pocket.get_anthropic_tool_specs(
            use_profile=True
        )
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    async def asyncTearDown(self):
        self.pocket._teardown_server()

    def test_get_tools_from_pocket_use_profile(self):
        # given
        pocket = PocketAnthropic(
            tools=[
                "https://github.com/vessl-ai/hyperpocket/main/tree/tools/slack/get-messages",
                "https://github.com/vessl-ai/hyperpocket/main/tree/tools/slack/post-message",
            ]
        )

        # when
        specs = pocket.get_anthropic_tool_specs(use_profile=True)
        get_tool, send_tool = specs[0], specs[1]

        # then
        self.assertIsInstance(get_tool, dict)
        self.assertEqual(get_tool["name"], "slack_get_messages")
        self.assertTrue("body" in get_tool["input_schema"]["properties"])
        self.assertTrue(
            "channel" in get_tool["input_schema"]["properties"]["body"]["properties"]
        )
        self.assertTrue(
            "limit" in get_tool["input_schema"]["properties"]["body"]["properties"]
        )

        self.assertIsInstance(send_tool, dict)
        self.assertEqual(send_tool["name"], "slack_send_messages")
        self.assertTrue("body" in send_tool["input_schema"]["properties"])
        self.assertTrue(
            "channel" in send_tool["input_schema"]["properties"]["body"]["properties"]
        )
        self.assertTrue(
            "text" in send_tool["input_schema"]["properties"]["body"]["properties"]
        )

    async def test_function_tool_use_profile(self):
        response = self.client.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=500,
            messages=[{"role": "user", "content": "add 1, 2"}],
            tools=self.tool_specs_use_profile,
        )

        tool_result_block = None
        for block in response.content:
            if block.type == "tool_use":
                tool_result_block = await self.pocket.ainvoke(block)

        # then
        self.assertEqual(response.stop_reason, "tool_use")
        self.assertIsNotNone(tool_result_block)
        self.assertEqual(tool_result_block["content"], "3")

    async def test_pydantic_function_tool_use_profile(self):
        response = self.client.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=500,
            messages=[{"role": "user", "content": "sub 1, 2"}],
            tools=self.tool_specs_use_profile,
        )

        tool_result_block = None
        for block in response.content:
            if block.type == "tool_use":
                tool_result_block = await self.pocket.ainvoke(block)

        # then
        self.assertEqual(response.stop_reason, "tool_use")
        self.assertIsNotNone(tool_result_block)
        self.assertEqual(tool_result_block["content"], "-1")

    async def test_wasm_tool_use_profile(self):
        response = self.client.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=500,
            messages=[{"role": "user", "content": "echo 'hello world'"}],
            tools=self.tool_specs_use_profile,
        )

        tool_result_block = None
        for block in response.content:
            if block.type == "tool_use":
                tool_result_block = await self.pocket.ainvoke(block)
        output = ast.literal_eval(tool_result_block["content"])

        # then
        self.assertEqual(response.stop_reason, "tool_use")
        self.assertIsNotNone(tool_result_block)
        self.assertTrue(output["stdout"].startswith("echo message : hello world"))
