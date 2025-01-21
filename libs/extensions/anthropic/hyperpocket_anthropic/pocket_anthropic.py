import json
from typing import List

try:
    from anthropic.types import ToolResultBlockParam, ToolUseBlock
except ImportError:
    raise ImportError("You need to install anthropic to use pocket anthropic.")

from hyperpocket import Pocket
from hyperpocket.tool import Tool

from hyperpocket_anthropic.util import tool_to_anthropic_spec


class PocketAnthropic(Pocket):
    def invoke(self, tool_use_block: ToolUseBlock, **kwargs) -> ToolResultBlockParam:
        body = self.parse_input(tool_use_block)
        result, interrupted = self.invoke_with_state(
            tool_use_block.name, body=body, **kwargs
        )
        say = result
        if interrupted:
            say = (
                f"{say}\n\nThe tool execution interrupted. Please talk to me to resume."
            )

        tool_result_block = ToolResultBlockParam(
            tool_use_id=tool_use_block.id, type="tool_result", content=say
        )

        return tool_result_block

    async def ainvoke(
            self, tool_use_block: ToolUseBlock, **kwargs
    ) -> ToolResultBlockParam:
        body = self.parse_input(tool_use_block)
        result, interrupted = await self.ainvoke_with_state(
            tool_use_block.name, body=body, **kwargs
        )
        say = result

        if interrupted:
            say = (
                f"{say}\n\nThe tool execution interrupted. Please talk to me to resume."
            )

        tool_result_block = ToolResultBlockParam(
            tool_use_id=tool_use_block.id, type="tool_result", content=say
        )

        return tool_result_block

    @staticmethod
    def parse_input(tool_use_block):
        if isinstance(tool_use_block.input, str):
            arg = json.loads(tool_use_block.input)
            body = arg["body"]
        else:
            arg = tool_use_block.input
            body = arg["body"]

        if isinstance(body, str):
            body = json.loads(body)

        return body

    def get_anthropic_tool_specs(self) -> List[dict]:
        specs = []
        for tool in self.core.tools.values():
            spec = self.get_anthropic_tool_spec(tool)
            specs.append(spec)
        return specs

    @staticmethod
    def get_anthropic_tool_spec(tool: Tool) -> dict:
        spec = tool_to_anthropic_spec(tool)
        return spec
