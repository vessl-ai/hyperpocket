import ast
from unittest.async_case import IsolatedAsyncioTestCase
from urllib.parse import parse_qs, unquote, urlparse

import pytest
from pydantic import BaseModel

from hyperpocket import Pocket
from hyperpocket.auth import AuthProvider
from hyperpocket.tool import function_tool


class FirstNumber(BaseModel):
    first: int


class SecondNumber(BaseModel):
    second: int


class TestPocket(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.profile = "test-profile"
        self.thread_id = "test_thread_id"
        self.pocket: Pocket = None

    async def asyncTearDown(self):
        if self.pocket:
            self.pocket._teardown_server()

    async def test_function_tool(self):
        # given
        def add(a: int, b: int) -> int:
            """
            Add two numbers

            Args:
                a(int): first number
                b(int): second number

            """

            return a + b

        self.pocket = Pocket(
            tools=[add],
        )

        tool_name = "add"

        # when
        result = await self.pocket.ainvoke(
            tool_name=tool_name,
            body={"a": 1, "b": 3},
            thread_id=self.thread_id,
            profile=self.profile,
        )

        # then
        self.assertEqual(result, "4")

    async def test_pydantic_arg_function_tool(self):
        # given
        def add_pydantic_args(a: FirstNumber, b: SecondNumber):
            """
            Add two numbers

            Args:
                a(FirstNumber): first number
                b(SecondNumber): second number
            """
            return a.first + b.second

        self.pocket = Pocket(
            tools=[add_pydantic_args],
        )
        tool_name = "add_pydantic_args"

        # when
        result = await self.pocket.ainvoke(
            tool_name=tool_name,
            body={"a": {"first": 1}, "b": {"second": 3}},
            thread_id=self.thread_id,
            profile=self.profile,
        )

        # then
        self.assertEqual(result, "4")

    @pytest.mark.skip(reason="after open repo")
    async def test_wasm_tool(self):
        # given
        tool_name = "simple_echo_text"
        self.pocket = Pocket(
            tools=[
                "https://github.com/vessl-ai/hyperpocket/tree/main/tools/none/simple-echo-tool"
            ]
        )

        # when
        result = await self.pocket.ainvoke(
            tool_name=tool_name,
            body={"text": "test"},
            thread_id=self.thread_id,
            profile=self.profile,
        )
        output = ast.literal_eval(result)

        # then
        self.assertTrue(output["stdout"].startswith("echo message : test"))

    @pytest.mark.skip("config error")
    async def test_initialize_tool_auth(self):
        # given
        @function_tool(auth_provider=AuthProvider.GOOGLE, scopes=["scope1", "scope2"])
        def google_function_a(**kwargs):
            """
            google function A
            """
            pass

        @function_tool(auth_provider=AuthProvider.GOOGLE, scopes=["scope2", "scope3"])
        def google_function_b(**kwargs):
            """
            google function B
            """
            pass

        @function_tool()
        def simple_function():
            """
            simple function
            """
            pass

        self.pocket = Pocket(
            tools=[google_function_a, google_function_b, simple_function],
        )
        # when
        prepare_url_dict = await self.pocket.initialize_tool_auth()
        google_auth_url = prepare_url_dict[AuthProvider.GOOGLE.name]
        google_scopes = self._extract_auth_scopes_from_url(
            google_auth_url, scope_field_name="scope"
        )

        # then
        self.assertEqual(len(prepare_url_dict), 1)
        self.assertIsNotNone(prepare_url_dict.get(AuthProvider.GOOGLE.name))
        self.assertEqual(len(google_scopes), 3)

    @staticmethod
    def _extract_auth_scopes_from_url(url, scope_field_name, delimiter=" "):
        url = unquote(url)
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        scopes = query_params.get(scope_field_name, [""])[0]
        scope_list = scopes.split(delimiter)
        stripped_scopes = [s.strip() for s in scope_list]
        return stripped_scopes
