import unittest

import pytest
from pydantic import BaseModel

from hyperdock_llamaindex import LlamaIndexDock
from llama_index.tools.duckduckgo import DuckDuckGoSearchToolSpec
from hyperpocket_llamaindex import PocketLlamaindex
from hyperpocket.tool.function.tool import FunctionTool


class TestHyperdockLlamaindex(unittest.IsolatedAsyncioTestCase):
    tool_spec = DuckDuckGoSearchToolSpec()
    
    def test_hyperdock_llamaindex_method(self):
        dock = LlamaIndexDock.dock(
            tool_func=self.tool_spec.duckduckgo_full_search,
            llamaindex_tool_args={
                "max_results": 5,
            },
        )
        pocket = PocketLlamaindex(
            tools=[
                dock,
            ]
        )
        tools = pocket.get_tools()

        # then
        self.assertTrue(isinstance(dock, FunctionTool), True)
    
    def test_hyperdock_llamaindex_function_tools(self):
        dock = LlamaIndexDock.dock(
            tool_func=self.tool_spec.to_tool_list(
                spec_functions=["duckduckgo_instant_search", "duckduckgo_full_search"]
            ),
            llamaindex_tool_args={
                "max_results": 5,
            },
        )
        pocket = PocketLlamaindex(
            tools=[
                *dock,
            ]
        )
        tools = pocket.get_tools()

        # then
        self.assertTrue(len(dock) == 2)
        self.assertTrue(isinstance(dock[0], FunctionTool), True)
    
    def test_hyperdock_llamaindex_function_tools_dock_list(self):
        dock = LlamaIndexDock.dock_list(
                tool_func=self.tool_spec.to_tool_list(
                    spec_functions=["duckduckgo_instant_search", "duckduckgo_full_search"]
                ),
                llamaindex_tool_args={
                    "max_results": 5,
                },
            )
        pocket = PocketLlamaindex(
            tools=[
                *dock,
            ]
        )
        tools = pocket.get_tools()
        
        # then
        self.assertTrue(len(dock) == 2)
        self.assertTrue(isinstance(dock[0], FunctionTool), True)
