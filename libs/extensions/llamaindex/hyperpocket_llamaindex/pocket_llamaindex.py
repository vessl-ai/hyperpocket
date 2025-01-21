from typing import List, Any

try:
    from llama_index.core.tools import FunctionTool, BaseTool, ToolMetadata
except ImportError:
    raise ImportError(
        "You need to install llama-index to use pocket llamaindex"
    )

from hyperpocket import Pocket
from hyperpocket.tool import Tool


class PocketLlamaindex(Pocket):
    def get_tools(self) -> List[BaseTool]:
        tools = [self.get_tool(pk) for pk in self.core.tools.values()]
        return tools

    def get_tool(self, pocket_tool: Tool) -> BaseTool:
        def _invoke(body: Any, thread_id: str = 'default', profile: str = 'default', **kwargs) -> str:
            result, interrupted = self.invoke_with_state(pocket_tool.name, body=body, thread_id=thread_id,
                                                         profile=profile, **kwargs)
            say = result
            if interrupted:
                say = f'{say}\n\nThe tool execution interrupted. Please talk to me to resume.'
            return say

        async def _ainvoke(body: Any, thread_id: str = 'default', profile: str = 'default', **kwargs) -> str:
            result, interrupted = await self.ainvoke_with_state(pocket_tool.name, body=body,
                                                                thread_id=thread_id, profile=profile, **kwargs)
            say = result
            if interrupted:
                say = f'{say}\n\nThe tool execution interrupted. Please talk to me to resume.'
            return say

        return FunctionTool.from_defaults(
            fn=_invoke,
            async_fn=_ainvoke,
            tool_metadata=ToolMetadata(
                description=pocket_tool.description,
                name=pocket_tool.name,
                fn_schema=pocket_tool.schema_model(),
            )
        )
