import ast
import json
import os
from unittest.async_case import IsolatedAsyncioTestCase

from llama_index.agent.openai import OpenAIAgent
from llama_index.llms.openai import OpenAI
from pydantic import BaseModel

from hyperpocket.config import config
from hyperpocket_llamaindex import PocketLlamaindex


class TestPocketLlamaindexUseProfile(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        config.public_server_port = "https"
        config.public_hostname = "localhost"
        config.public_server_port = 8001
        config.internal_server_port = 8000
        config.enable_local_callback_proxy = True

        self.pocket = PocketLlamaindex(
            tools=[
                "https://github.com/vessl-ai/hyperpocket/main/tree/tools/none/simple-echo-tool",
                self.add,
                self.sub_pydantic_args,
            ],
            use_profile=True,
        )

        self.llm = OpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))

    async def asyncTearDown(self):
        self.pocket._teardown_server()

    async def test_agent_use_profile(self):
        # given
        agent = OpenAIAgent.from_tools(
            tools=self.pocket.get_tools(),
            llm=OpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY")),
            verbose=True,
        )

        # when
        agent.query("add 1, 2")
        agent.query("sub 1, 2")
        agent.query("echo 'hello world'")

    async def test_function_tool(self):
        # when
        response = self.llm.chat_with_tools(
            user_msg="add 1, 2", tools=self.pocket.get_tools(), verbose=True
        )
        message = response.message
        tool_calls = message.additional_kwargs["tool_calls"]

        tool_name = tool_calls[0].function.name
        args = tool_calls[0].function.arguments
        args = json.loads(args)

        result = await self.pocket.ainvoke(tool_name=tool_name, **args)

        # then
        self.assertEqual(tool_name, "add")
        self.assertEqual(
            args["body"],
            {
                "a": 1,
                "b": 2,
            },
        )
        self.assertEqual(result, "3")

    async def test_pydantic_function_tool(self):
        # when
        response = self.llm.chat_with_tools(
            user_msg="sub 1, 2", tools=self.pocket.get_tools(), verbose=True
        )
        tool_calls = response.message.additional_kwargs["tool_calls"]

        tool_name = tool_calls[0].function.name
        args = tool_calls[0].function.arguments
        args = json.loads(args)

        result = await self.pocket.ainvoke(tool_name=tool_name, **args)

        # then
        self.assertEqual(tool_name, "sub_pydantic_args")
        self.assertEqual(
            args["body"],
            {
                "a": {"first": 1},
                "b": {"second": 2},
            },
        )
        self.assertEqual(result, "-1")

    async def test_wasm_tool(self):
        # when
        response = self.llm.chat_with_tools(
            user_msg="echo 'hello world'", tools=self.pocket.get_tools(), verbose=True
        )
        tool_calls = response.message.additional_kwargs["tool_calls"]

        tool_name = tool_calls[0].function.name
        args = tool_calls[0].function.arguments
        args = json.loads(args)

        result = await self.pocket.ainvoke(tool_name=tool_name, **args)
        output = ast.literal_eval(result)

        # then
        self.assertEqual(tool_name, "simple_echo_text")
        self.assertEqual(args["body"], {"text": "hello world"})
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
