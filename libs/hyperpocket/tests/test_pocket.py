import ast
from unittest.async_case import IsolatedAsyncioTestCase
from urllib.parse import parse_qs, unquote, urlparse

import pytest
from pydantic import BaseModel

from hyperpocket import Pocket
from hyperpocket.auth import AuthProvider
from hyperpocket.tool import function_tool, Tool


class FirstNumber(BaseModel):
    first: int


class SecondNumber(BaseModel):
    second: int


class TestPocket(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.profile = "test-profile"
        self.thread_id = "test_thread_id"

    @pytest.mark.asyncio
    async def test_load_tools_str(self):
        """
        Test Load tools in case str type
        """
        # when
        pocket = Pocket(
            tools=[
                "https://github.com/vessl-ai/hyperpocket/tree/main/tools/none/simple-echo-tool"
            ]
        )

        # then
        simple_echo_tool = pocket.tools["simple_echo_tool"]
        self.assertIsInstance(simple_echo_tool, Tool)
        self.assertEqual(simple_echo_tool.name, "simple_echo_tool")

    async def test_load_tools_tuple(self):
        """
        Test Load tools in case tuple type
        """
        # when
        pocket = Pocket(
            tools=[
                ("https://github.com/vessl-ai/hyperpocket/tree/main/tools/none/simple-echo-tool",
                 {"TEST_VAR": "TEST"})
            ]
        )

        # then
        simple_echo_tool = pocket.tools["simple_echo_tool"]
        self.assertEqual(simple_echo_tool.tool_vars["TEST_VAR"], "TEST")

    async def test_load_tools_tool(self):
        """
        Test Load tools in case tool type
        """
        # given
        pocket = Pocket()

        # when
        tool_before_load = pocket.tools.get("simple_echo_tool")
        pocket.load_tools(
            tools=[
                "https://github.com/vessl-ai/hyperpocket/tree/main/tools/none/simple-echo-tool"
            ]
        )
        tool_after_load = pocket.tools.get("simple_echo_tool")

        # then
        self.assertIsNone(tool_before_load)
        self.assertIsInstance(tool_after_load, Tool)

    async def test_remove_tool(self):
        """
        Test Load tools in case tuple type
        """
        # given
        pocket = Pocket(
            tools=[
                "https://github.com/vessl-ai/hyperpocket/tree/main/tools/none/simple-echo-tool"
            ])

        # when
        tool_before_remove = pocket.tools.get("simple_echo_tool")
        pocket.remove_tool("simple_echo_tool")
        tool_after_remove = pocket.tools.get("simple_echo_tool")

        # then
        self.assertIsInstance(tool_before_remove, Tool)
        self.assertIsNone(tool_after_remove)

    async def test_grouping_tool_by_auth_provider(self):
        """
        Test grouping tool by auth provider
        It should return dict which groups tools by auth provider.
        """
        # given
        pocket = Pocket(
            tools=[
                "https://github.com/vessl-ai/hyperpocket/tree/main/tools/none/simple-echo-tool",
                "https://github.com/vessl-ai/hyperpocket/tree/main/tools/google/create-spreadsheet",
                "https://github.com/vessl-ai/hyperpocket/tree/main/tools/google/list-gmail",
                "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/get-messages",
                "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/post-message",
            ])

        # when
        grouped = pocket.grouping_tool_by_auth_provider()

        # then
        self.assertEqual(len(grouped), 2)
        self.assertEqual(len(grouped["GOOGLE"]), 2)
        self.assertEqual(len(grouped["SLACK"]), 2)

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

    async def test_container_tool(self):
        # given
        tool_name = "simple_echo_tool"
        self.pocket = Pocket(
            tools=[
                "https://github.com/vessl-ai/hyperpocket/tree/main/tools/none/simple-echo-tool",
            ]
        )

        # when
        result = await self.pocket.ainvoke(
            tool_name=tool_name,
            body={"text": "test"},
            thread_id=self.thread_id,
            profile=self.profile,
        )

        # then
        self.assertTrue("echo message : test" in result)

    async def test_initialize_tool_auth(self):
        # given
        from hyperpocket.config.auth import GoogleAuthConfig
        from hyperpocket.config.settings import config

        config().auth.google = GoogleAuthConfig(
            client_id="test",
            client_secret="test",
        )

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
