import asyncio
import json
from typing import List

from hyperpocket_openai.util import tool_to_open_ai_spec

try:
    from openai.types.chat import ChatCompletionMessageToolCall
except ImportError:
    raise ImportError(
        "You need to install openai to use pocket PocketOpenAI."
    )

from hyperpocket import Pocket
from hyperpocket.tool import Tool


class PocketOpenAI(Pocket):
    def invoke(self, tool_call: ChatCompletionMessageToolCall, *kwargs):
        loop = asyncio.get_running_loop()
        result = loop.run_until_complete(self.ainvoke(tool_call, **kwargs))
        return result

    async def ainvoke(self, tool_call: ChatCompletionMessageToolCall, **kwargs):
        arg_json = json.loads(tool_call.function.arguments)
        result = await super().ainvoke(tool_call.function.name, **arg_json, **kwargs)
        tool_message = {
            "role": "tool",
            "content": result,
            "tool_call_id": tool_call.id
        }

        return tool_message

    def get_open_ai_tool_specs(self) -> List[dict]:
        specs = []
        for tool in self.core.tools.values():
            spec = self.get_open_ai_tool_spec(tool)
            specs.append(spec)
        return specs

    @staticmethod
    def get_open_ai_tool_spec(tool: Tool) -> dict:
        open_ai_spec = tool_to_open_ai_spec(tool)
        return open_ai_spec
