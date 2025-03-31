import json
from typing import List, Optional

from langchain_core.tools import BaseTool, StructuredTool

from hyperpocket import Pocket
from hyperpocket.tool import Tool
from hyperpocket.util.convert_pydantic_to_dict import convert_pydantic_to_dict


class PocketLangchain(Pocket):
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
            body = convert_pydantic_to_dict(body)

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
            body = convert_pydantic_to_dict(body)

            result, interrupted = await self.ainvoke_with_state(
                pocket_tool.name, body=body, thread_id=thread_id, profile=profile
            )
            say = result
            if interrupted:
                say = f"{say}\n\nThe tool execution interrupted. Please talk to me to resume."
            return say

        return StructuredTool.from_function(
            func=_invoke,
            coroutine=_ainvoke,
            name=pocket_tool.name,
            description=pocket_tool.get_description(use_profile=self.use_profile),
            args_schema=pocket_tool.schema_model(use_profile=self.use_profile),
        )
