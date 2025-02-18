import os
import pathlib
import shutil
from typing import Callable
from unittest import IsolatedAsyncioTestCase

from hyperpocket.pocket_core import PocketCore
from hyperpocket.repository.tool_reference import LocalLock, GitLock
from hyperpocket.tool import from_func, Tool
from hyperpocket.tool.wasm.tool import WasmToolRequest


class TestPocketCore(IsolatedAsyncioTestCase):
    def test_parse_local_path_tool_like(self):
        # given
        test_local_path = pathlib.Path(os.getcwd()) / "test_local_path"
        if not test_local_path.exists():
            test_local_path.mkdir()

        try:
            # when
            parsed_tool_like = PocketCore._parse_str_tool_like(str(test_local_path))

            # then
            self.assertIsInstance(parsed_tool_like, WasmToolRequest)
            self.assertIsInstance(parsed_tool_like.lock, LocalLock)
            self.assertEqual(parsed_tool_like.lock.tool_path, str(test_local_path))

        finally:
            shutil.rmtree(test_local_path)

    def test_parse_main_github_url_tool_like(self):
        # given
        test_github_url = "https://github.com/vessl-ai/hyperpocket"

        # when
        parsed_tool_like = PocketCore._parse_str_tool_like(test_github_url)

        # then
        self.assertIsInstance(parsed_tool_like, WasmToolRequest)
        self.assertEqual(parsed_tool_like.rel_path, "")
        self.assertIsInstance(parsed_tool_like.lock, GitLock)
        self.assertEqual(
            parsed_tool_like.lock.repository_url,
            "https://github.com/vessl-ai/hyperpocket",
        )
        self.assertEqual(parsed_tool_like.lock.git_ref, "HEAD")

    def test_parse_specific_github_url_tool_like(self):
        # given
        test_github_url = (
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/get-message"
        )

        # when
        parsed_tool_like = PocketCore._parse_str_tool_like(test_github_url)

        # then
        self.assertIsInstance(parsed_tool_like, WasmToolRequest)
        self.assertEqual(parsed_tool_like.rel_path, "tools/slack/get-message")
        self.assertIsInstance(parsed_tool_like.lock, GitLock)
        self.assertEqual(
            parsed_tool_like.lock.repository_url,
            "https://github.com/vessl-ai/hyperpocket",
        )
        self.assertEqual(parsed_tool_like.lock.git_ref, "main")

    def test_parse_wasm_tool_like(self):
        # given
        local_path = pathlib.Path(os.getcwd()) / "test_local_path"
        tool_request = WasmToolRequest(
            LocalLock(str(local_path)), rel_path="/rel/path", tool_vars={}
        )

        # when
        parsed_tool_like = PocketCore._parse_tool_like(tool_request)

        # then
        self.assertIsInstance(parsed_tool_like, WasmToolRequest)
        self.assertEqual(parsed_tool_like.rel_path, "/rel/path")
        self.assertIsInstance(parsed_tool_like.lock, LocalLock)
        self.assertEqual(parsed_tool_like.lock.tool_path, str(local_path))

    def test_parse_callable_tool_like(self):
        # given
        def call():
            pass

        # when
        parsed_tool_like = PocketCore._parse_tool_like(call)

        # then
        self.assertIsInstance(parsed_tool_like, Callable)

    def test_parse_tool(self):
        # given
        def call():
            pass

        tool = from_func(call)

        # when
        parsed_tool_like = PocketCore._parse_tool_like(tool)

        # then
        self.assertIsInstance(parsed_tool_like, Tool)
