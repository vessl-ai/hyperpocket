import json
from typing import List, Optional

try:
    from anthropic.types import ToolResultBlockParam, ToolUseBlock
except ImportError:
    raise ImportError("You need to install anthropic to use pocket anthropic.")

from hyperpocket import Pocket
from hyperpocket.tool import Tool

from hyperpocket_anthropic.util import tool_to_anthropic_spec


class PocketAnthropic(Pocket):
    def invoke(self, tool_use_block: ToolUseBlock, **kwargs) -> ToolResultBlockParam:
        if isinstance(tool_use_block.input, str):
            arg = json.loads(tool_use_block.input)
        else:
            arg = tool_use_block.input

        if self.use_profile:
            body = arg.pop("body")
            thread_id = arg.pop("thread_id", "default")
            profile = arg.pop("profile", "default")
        else:
            body = arg
            thread_id = "default"
            profile = "default"

        if isinstance(body, str):
            body = json.loads(body)

        result, interrupted = self.invoke_with_state(
            tool_use_block.name,
            body=body,
            thread_id=thread_id,
            profile=profile,
            **kwargs,
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
        if isinstance(tool_use_block.input, str):
            arg = json.loads(tool_use_block.input)
        else:
            arg = tool_use_block.input

        if self.use_profile:
            body = arg.pop("body")
            thread_id = arg.pop("thread_id", "default")
            profile = arg.pop("profile", "default")
        else:
            body = arg
            thread_id = "default"
            profile = "default"

        if isinstance(body, str):
            body = json.loads(body)

        result, interrupted = await self.ainvoke_with_state(
            tool_use_block.name,
            body=body,
            thread_id=thread_id,
            profile=profile,
            **kwargs,
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

    def get_anthropic_tool_specs(
        self, use_profile: Optional[bool] = None
    ) -> List[dict]:
        if use_profile is not None:
            self.use_profile = use_profile

        specs = []
        for tool in self.tools.values():
            spec = self.get_anthropic_tool_spec(tool)
            specs.append(spec)
        return specs

    def get_anthropic_tool_spec(self, tool: Tool) -> dict:
        spec = tool_to_anthropic_spec(tool, use_profile=self.use_profile)
        return spec
