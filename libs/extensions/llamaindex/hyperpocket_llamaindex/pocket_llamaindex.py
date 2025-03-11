import json
from typing import List, Optional

try:
    from llama_index.core.tools import BaseTool, FunctionTool, ToolMetadata
except ImportError:
    raise ImportError("You need to install llama-index to use pocket llamaindex")

from hyperpocket import Pocket
from hyperpocket.tool import Tool


class PocketLlamaindex(Pocket):
    def get_tools(self, use_profile: Optional[bool] = None) -> List[BaseTool]:
        if use_profile is not None:
            self.use_profile = use_profile

        tools = [self.get_tool(pk) for pk in self.tools.values()]
        return tools

    def get_tool(self, pocket_tool: Tool) -> BaseTool:
        def _invoke(**kwargs) -> str:
            if self.use_profile:
                body = kwargs["body"]
                thread_id = kwargs.pop("thread_id", "default")
                profile = kwargs.pop("profile", "default")
            else:
                body = kwargs
                thread_id = "default"
                profile = "default"

            if isinstance(body, str):
                body = json.loads(body)

            result, interrupted = self.invoke_with_state(
                pocket_tool.name,
                body=body,
                thread_id=thread_id,
                profile=profile,
                **kwargs,
            )
            say = result
            if interrupted:
                say = f"{say}\n\nThe tool execution interrupted. Please talk to me to resume."
            return say

        async def _ainvoke(**kwargs) -> str:
            if self.use_profile:
                body = kwargs["body"]
                thread_id = kwargs.pop("thread_id", "default")
                profile = kwargs.pop("profile", "default")
            else:
                body = kwargs
                thread_id = "default"
                profile = "default"

            if isinstance(body, str):
                body = json.loads(body)

            result, interrupted = await self.ainvoke_with_state(
                pocket_tool.name,
                body=body,
                thread_id=thread_id,
                profile=profile,
                **kwargs,
            )
            say = result
            if interrupted:
                say = f"{say}\n\nThe tool execution interrupted. Please talk to me to resume."
            return say

        return FunctionTool.from_defaults(
            fn=_invoke,
            async_fn=_ainvoke,
            tool_metadata=ToolMetadata(
                name=pocket_tool.name,
                description=pocket_tool.get_description(use_profile=self.use_profile),
                fn_schema=pocket_tool.schema_model(use_profile=self.use_profile),
            ),
        )
