import asyncio
import json
from typing import List, Optional

from google.genai import types
from google.genai.types import FunctionCall, Tool as GeminiTool
from hyperpocket_gemini.util.tool_to_gemini_spec import tool_to_gemini_spec

from hyperpocket import Pocket
from hyperpocket.tool import Tool


class PocketGemini(Pocket):
    def invoke(self, tool_call: FunctionCall, **kwargs):
        loop = asyncio.get_running_loop()
        result = loop.run_until_complete(self.ainvoke(tool_call, **kwargs))
        return result

    async def ainvoke(self, tool_call: FunctionCall, **kwargs):
        if isinstance(tool_call.args, str):
            arg_json = json.loads(tool_call.args)
        else:
            arg_json = tool_call.args

        if self.use_profile:
            body = arg_json["body"]
            thread_id = arg_json.pop("thread_id", "default")
            profile = arg_json.pop("profile", "default")
        else:
            body = arg_json
            thread_id = "default"
            profile = "default"

        if isinstance(body, str):
            body = json.loads(body)

        try:
            response = {'result': await super().ainvoke(
                tool_call.name,
                body=body,
                thread_id=thread_id,
                profile=profile,
                **kwargs,
            )}
        except Exception as e:  # pylint: disable=broad-except
            response = {'error': str(e)}

        return types.Part.from_function_response(
            name=tool_call.name,
            response=response
        )

    def get_gemini_tool_specs(
        self, use_profile: Optional[bool] = None
    ) -> List[GeminiTool]:
        if use_profile is not None:
            self.use_profile = use_profile

        specs = []
        for tool in self.tools.values():
            spec = self.get_gemini_tool_spec(tool)
            specs.append(spec)
        return specs

    def get_gemini_tool_spec(self, tool: Tool) -> GeminiTool:
        spec = tool_to_gemini_spec(tool, use_profile=self.use_profile)
        return spec
