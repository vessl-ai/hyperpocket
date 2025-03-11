import copy
import json
from typing import Optional

from langchain_core.runnables import RunnableConfig
from langgraph.errors import NodeInterrupt

from hyperpocket.config import pocket_logger

try:
    from langchain_core.messages import ToolMessage
    from langchain_core.tools import BaseTool, StructuredTool
except ImportError:
    raise ImportError("You need to install langchain to use pocket langgraph.")

try:
    from langgraph.graph import MessagesState
except ImportError:
    raise ImportError("You need to install langgraph to use pocket langgraph")

from hyperpocket import Pocket
from hyperpocket.tool import Tool as PocketTool


class PocketLanggraphBaseState(MessagesState):
    pass


class PocketLanggraph(Pocket):
    def get_tools(self, use_profile: Optional[bool] = None):
        if use_profile is not None:
            self.use_profile = use_profile
        return [
            self._get_langgraph_tool(tool_impl)
            for tool_impl in self.tools.values()
        ]

    def get_tool_node(
        self, should_interrupt: bool = False, use_profile: Optional[bool] = None
    ):
        if use_profile is not None:
            self.use_profile = use_profile

        async def _tool_node(
            state: PocketLanggraphBaseState, config: RunnableConfig
        ) -> dict:
            thread_id = config.get("configurable", {}).get("thread_id", "default")
            last_message = state["messages"][-1]
            tool_calls = last_message.tool_calls

            # 01. prepare
            prepare_list = []
            prepare_done_list = []
            need_prepare = False
            for tool_call in tool_calls:
                pocket_logger.debug(f"prepare tool {tool_call}")
                _tool_call = copy.deepcopy(tool_call)

                tool_call_id = _tool_call["id"]
                tool_name = _tool_call["name"]
                tool_args = _tool_call["args"]

                if self.use_profile:
                    body = tool_args.pop("body")
                    profile = tool_args.pop("profile", "default")
                else:
                    body = tool_args
                    profile = "default"

                prepare = await self.prepare_auth(
                    tool_name, body=body, thread_id=thread_id, profile=profile
                )
                need_prepare |= True if prepare else False

                if prepare is None:
                    prepare_done_list.append(
                        ToolMessage(content="prepare done", tool_call_id=tool_call_id)
                    )
                else:
                    prepare_list.append(
                        ToolMessage(content=prepare, tool_call_id=tool_call_id)
                    )

            if need_prepare:
                pocket_logger.debug(f"need prepare : {prepare_list}")
                if should_interrupt:  # interrupt
                    pocket_logger.debug(
                        f"{last_message.name}({last_message.id}) is interrupt."
                    )
                    result = "\n\t" + "\n\t".join(
                        set(msg.content for msg in prepare_list)
                    )
                    raise NodeInterrupt(
                        f"{result}\n\nThe tool execution interrupted. Please talk to me to resume."
                    )

                else:  # multi turn
                    pocket_logger.debug(
                        f"{last_message.name}({last_message.id}) is multi-turn"
                    )
                    return {"messages": prepare_done_list + prepare_list}

            pocket_logger.debug(
                f"no need prepare {last_message.name}({last_message.id})"
            )

            # 02. authenticate and tool call
            tool_messages = []
            for tool_call in tool_calls:
                pocket_logger.debug(f"authenticate and call {tool_call}")
                _tool_call = copy.deepcopy(tool_call)

                tool_call_id = _tool_call["id"]
                tool_name = _tool_call["name"]
                tool_args = _tool_call["args"]
                if self.use_profile:
                    body = tool_args.pop("body")
                    profile = tool_args.pop("profile", "default")
                else:
                    body = tool_args
                    profile = "default"

                if isinstance(body, str):
                    body = json.loads(body)

                try:
                    auth = await self.authenticate(
                        tool_name, body=body, thread_id=thread_id, profile=profile
                    )
                except Exception as e:
                    pocket_logger.error(
                        f"occur exception during authenticate. error : {e}"
                    )
                    tool_messages.append(
                        ToolMessage(
                            content=f"occur exception during authenticate. error : {e}",
                            tool_name=tool_name,
                            tool_call_id=tool_call_id,
                        )
                    )
                    continue

                try:
                    result = await self.tool_call(
                        tool_name,
                        body=body,
                        envs=auth,
                        thread_id=thread_id,
                        profile=tool_args.get("profile", "default"),
                    )
                except Exception as e:
                    pocket_logger.error(
                        f"occur exception during tool calling. error : {e}"
                    )
                    tool_messages.append(
                        ToolMessage(
                            content=f"occur exception during tool calling. error : {e}",
                            tool_name=tool_name,
                            tool_call_id=tool_call_id,
                        )
                    )
                    continue

                pocket_logger.debug(f"{tool_name} tool result : {result}")
                tool_messages.append(
                    ToolMessage(
                        content=result, tool_name=tool_name, tool_call_id=tool_call_id
                    )
                )

            return {"messages": tool_messages}

        return _tool_node

    def _get_langgraph_tool(self, pocket_tool: PocketTool) -> BaseTool:
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
                pocket_tool.name, body, thread_id, profile, **kwargs
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
                pocket_tool.name, body, thread_id, profile, **kwargs
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
