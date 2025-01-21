import copy
from typing import List, Any

from langchain_core.runnables import RunnableConfig
from langgraph.errors import NodeInterrupt
from pydantic import BaseModel

from hyperpocket.config import pocket_logger
from hyperpocket.pocket_main import ToolLike
from hyperpocket.prompts import pocket_extended_tool_description

try:
    from langchain_core.messages import ToolMessage
    from langchain_core.tools import BaseTool, StructuredTool
except ImportError:
    raise ImportError(
        "You need to install langchain to use pocket langgraph."
    )

try:
    from langgraph.graph import MessagesState
except ImportError:
    raise ImportError(
        "You need to install langgraph to use pocket langgraph"
    )

from hyperpocket import Pocket, PocketAuth
from hyperpocket.tool import Tool as PocketTool


class PocketLanggraphBaseState(MessagesState):
    pass


class PocketLanggraph(Pocket):
    langgraph_tools: dict[str, BaseTool]

    def __init__(self,
                 tools: List[ToolLike],
                 auth: PocketAuth = None):
        super().__init__(tools, auth)
        self.langgraph_tools = {}
        for tool_name, tool_impl in self.core.tools.items():
            self.langgraph_tools[tool_name] = self._get_langgraph_tool(tool_impl)

    def get_tools(self):
        return [v for v in self.langgraph_tools.values()]

    def get_tool_node(self, should_interrupt: bool = False):
        async def _tool_node(state: PocketLanggraphBaseState, config: RunnableConfig) -> dict:
            thread_id = config.get("configurable", {}).get("thread_id", "default")
            last_message = state['messages'][-1]
            tool_calls = last_message.tool_calls

            # 01. prepare
            prepare_list = []
            prepare_done_list = []
            need_prepare = False
            for tool_call in tool_calls:
                pocket_logger.debug(f"prepare tool {tool_call}")
                _tool_call = copy.deepcopy(tool_call)

                tool_call_id = _tool_call['id']
                tool_name = _tool_call['name']
                tool_args = _tool_call['args']
                body = tool_args.pop('body')
                if isinstance(body, BaseModel):
                    body = body.model_dump()

                prepare = await self.prepare_in_subprocess(tool_name, body=body, thread_id=thread_id,
                                                           profile=tool_args.get("profile", "default"))
                need_prepare |= True if prepare else False

                if prepare is None:
                    prepare_done_list.append(ToolMessage(content="prepare done", tool_call_id=tool_call_id))
                else:
                    prepare_list.append(ToolMessage(content=prepare, tool_call_id=tool_call_id))

            if need_prepare:
                pocket_logger.debug(f"need prepare : {prepare_list}")
                if should_interrupt:  # interrupt
                    pocket_logger.debug(f"{last_message.name}({last_message.id}) is interrupt.")
                    result = "\n\t" + "\n\t".join(set(msg.content for msg in prepare_list))
                    raise NodeInterrupt(f'{result}\n\nThe tool execution interrupted. Please talk to me to resume.')

                else:  # multi turn
                    pocket_logger.debug(f"{last_message.name}({last_message.id}) is multi-turn")
                    return {"messages": prepare_done_list + prepare_list}

            pocket_logger.debug(f"no need prepare {last_message.name}({last_message.id})")

            # 02. authenticate and tool call
            tool_messages = []
            for tool_call in tool_calls:
                pocket_logger.debug(f"authenticate and call {tool_call}")
                _tool_call = copy.deepcopy(tool_call)

                tool_call_id = _tool_call['id']
                tool_name = _tool_call['name']
                tool_args = _tool_call['args']
                body = tool_args.pop('body')
                if isinstance(body, BaseModel):
                    body = body.model_dump()

                try:
                    auth = await self.authenticate_in_subprocess(
                        tool_name, body=body, thread_id=thread_id, profile=tool_args.get("profile", "default"))
                except Exception as e:
                    pocket_logger.error(f"occur exception during authenticate. error : {e}")
                    tool_messages.append(
                        ToolMessage(content=f"occur exception during authenticate. error : {e}", tool_name=tool_name,
                                    tool_call_id=tool_call_id))
                    continue

                try:
                    result = await self.tool_call_in_subprocess(
                        tool_name, body=body, envs=auth, thread_id=thread_id,
                        profile=tool_args.get("profile", "default"))
                except Exception as e:
                    pocket_logger.error(f"occur exception during tool calling. error : {e}")
                    tool_messages.append(
                        ToolMessage(content=f"occur exception during tool calling. error : {e}", tool_name=tool_name,
                                    tool_call_id=tool_call_id))
                    continue

                pocket_logger.debug(f"{tool_name} tool result : {result}")
                tool_messages.append(ToolMessage(content=result, tool_name=tool_name, tool_call_id=tool_call_id))

            return {"messages": tool_messages}

        return _tool_node

    def _get_langgraph_tool(self, pocket_tool: PocketTool) -> BaseTool:
        def _invoke(body: Any, thread_id: str = 'default', profile: str = 'default', **kwargs) -> str:
            if isinstance(body, BaseModel):
                body = body.model_dump()
            result, interrupted = self.invoke_with_state(pocket_tool.name, body, thread_id, profile, **kwargs)
            say = result
            if interrupted:
                say = f'{say}\n\nThe tool execution interrupted. Please talk to me to resume.'
            return say

        async def _ainvoke(body: Any, thread_id: str = 'default', profile: str = 'default', **kwargs) -> str:
            if isinstance(body, BaseModel):
                body = body.model_dump()
            result, interrupted = await self.ainvoke_with_state(pocket_tool.name, body, thread_id, profile, **kwargs)
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
