import unittest

import pytest
from crewai import Agent, Task
from pydantic import BaseModel

from hyperpocket_crewai.pocket_crewai import PocketCrewAI


class TestPocketCrewAI(unittest.IsolatedAsyncioTestCase):
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

    @pytest.mark.skip("tbu")
    async def test_pocket_crewai(self):
        # given
        pocket = PocketCrewAI(
            tools=[
                self.add,
            ],
        )

        agent = Agent(
            role="add agent",
            goal="add two numbers",
            backstory="add agent",
            tools=pocket.get_tools(),
            verbose=True
        )

        task = Task(
            description="add two numbers",
            expected_output="summation of two numbers",
            agent=agent
        )
