import unittest

import pytest
from crewai import Agent, Task
from pydantic import BaseModel

from hyperpocket_crewai.pocket_crewai import PocketCrewAI


class TestPocketCrewAI(unittest.IsolatedAsyncioTestCase):
    def test_function_tool(self):
        def _secret_operator(a: int, b: int) -> int:
            """
            secret operator of two numbers

            Args:
                a(int): first number
                b(int): second number

            """

            return a + b

        with PocketCrewAI(tools=[_secret_operator]) as pocket:
            # given
            agent = Agent(
                role="secret operating agent",
                goal="apply secret operating to 2, 5",
                backstory="secret operating agent",
                tools=pocket.get_tools(),
                verbose=True,
                max_iter=5,
                max_retry_limit=1,
            )

            task = Task(
                description="do secret operating two numbers",
                expected_output="result of two numbers",
                agent=agent,
            )

            # when
            output = agent.execute_task(task=task, tools=pocket.get_tools())

            # then
            self.assertEqual(output, "7")

    def test_wasm_tool(self):
        with PocketCrewAI(tools=[
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/none/simple-echo-tool"
        ]) as pocket:
            # given
            agent = Agent(
                role="echo agent",
                goal="echo",
                backstory="echo agent",
                tools=pocket.get_tools(),
                verbose=True,
                max_iter=5,
                max_retry_limit=1,
            )

            task = Task(
                description="echo 'hello world'",
                expected_output="echo 'hello world'",
                agent=agent,
            )

            # when
            output = agent.execute_task(task=task, tools=pocket.get_tools()).strip()

            # then
            self.assertTrue("hello world" in output)

    @pytest.mark.skip(reason="crewai don't support nested pydantic arguments.")
    def test_pydantic_function_tool(self):
        def _secret_operator(a: FirstNumber, b: SecondNumber):
            """
            secret operator

            Args:
                a(FirstNumber): first number
                b(SecondNumber): second number
            """
            return a.first - b.second

        with PocketCrewAI(tools=[_secret_operator]) as pocket:
            # given
            agent = Agent(
                role="secret operating agent",
                goal="apply secret operating to 2, 5",
                backstory="secret operating agent",
                tools=pocket.get_tools(),
                verbose=True,
                max_iter=5,
                max_retry_limit=1,
            )

            task = Task(
                description="do secret operating two numbers",
                expected_output="result of two numbers",
                agent=agent,
            )

            # when
            output = agent.execute_task(task=task, tools=pocket.get_tools())

            # then
            self.assertEqual(output, "-3")


class FirstNumber(BaseModel):
    first: int


class SecondNumber(BaseModel):
    second: int
