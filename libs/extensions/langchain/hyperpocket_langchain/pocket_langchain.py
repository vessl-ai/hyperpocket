from typing import List, Any

from hyperpocket import Pocket
from hyperpocket.prompts import pocket_extended_tool_description
from hyperpocket.tool import Tool
from langchain_core.tools import BaseTool, StructuredTool
from pydantic import BaseModel


class PocketLangchain(Pocket):
    def get_tools(self) -> List[BaseTool]:
        tools = [self.get_tool(pk) for pk in self.core.tools.values()]
        return tools

    def get_tool(self, pocket_tool: Tool) -> BaseTool:
        def _invoke(body: Any, thread_id: str = 'default', profile: str = 'default', **kwargs) -> str:
            if isinstance(body, BaseModel):
                body = body.model_dump()

            result, interrupted = self.invoke_with_state(pocket_tool.name, body=body, thread_id=thread_id,
                                                         profile=profile, **kwargs)
            say = result
            if interrupted:
                say = f'{say}\n\nThe tool execution interrupted. Please talk to me to resume.'
            return say

        async def _ainvoke(body: Any, thread_id: str = 'default', profile: str = 'default', **kwargs) -> str:
            if isinstance(body, BaseModel):
                body = body.model_dump()

            result, interrupted = await self.ainvoke_with_state(pocket_tool.name, body=body,
                                                                thread_id=thread_id, profile=profile, **kwargs)
            say = result
            if interrupted:
                say = f'{say}\n\nThe tool execution interrupted. Please talk to me to resume.'
            return say

        return StructuredTool.from_function(
            func=_invoke,
            coroutine=_ainvoke,
            name=pocket_tool.name,
            description=pocket_extended_tool_description(pocket_tool.description),
            args_schema=pocket_tool.schema_model(),
        )
