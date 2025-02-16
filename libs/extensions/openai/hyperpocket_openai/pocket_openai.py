import asyncio
import json
from typing import List, Optional

from hyperpocket_openai.util import tool_to_open_ai_spec
from openai import OpenAI

try:
    from openai.types.chat import ChatCompletionMessageToolCall
except ImportError:
    raise ImportError("You need to install openai to use pocket PocketOpenAI.")

from hyperpocket import Pocket
from hyperpocket.config import pocket_logger
from hyperpocket.tool import Tool


class PocketOpenAI(Pocket):
    def invoke(self, tool_call: ChatCompletionMessageToolCall, **kwargs):
        loop = asyncio.get_running_loop()
        result = loop.run_until_complete(self.ainvoke(tool_call, **kwargs))
        return result

    async def ainvoke(self, tool_call: ChatCompletionMessageToolCall, **kwargs):
        arg_json = json.loads(tool_call.function.arguments)

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

        result = await super().ainvoke(
            tool_call.function.name,
            body=body,
            thread_id=thread_id,
            profile=profile,
            **kwargs,
        )
        tool_message = {"role": "tool", "content": result, "tool_call_id": tool_call.id}

        return tool_message

    def get_open_ai_tool_specs(self, use_profile: Optional[bool] = None) -> List[dict]:
        if use_profile is not None:
            self.use_profile = use_profile
        specs = []
        for tool in self.core.tools.values():
            spec = self.get_open_ai_tool_spec(tool)
            specs.append(spec)
        return specs

    def get_open_ai_tool_spec(self, tool: Tool) -> dict:
        open_ai_spec = tool_to_open_ai_spec(tool, use_profile=self.use_profile)
        return open_ai_spec


async def handle_tool_call_async(
    llm: OpenAI,
    pocket: PocketOpenAI,
    model: str,
    tool_specs: List[dict],
    messages: List[dict],
):
    while True:
        response = llm.chat.completions.create(
            model=model,
            messages=messages,
            tools=tool_specs,
        )
        choice = response.choices[0]
        messages.append(choice.message)
        if choice.finish_reason == "stop":
            break

        elif choice.finish_reason == "tool_calls":
            tool_calls = choice.message.tool_calls
            for tool_call in tool_calls:
                pocket_logger.debug(f"[TOOL CALL] {tool_call}")
                tool_message = await pocket.ainvoke(tool_call)
                messages.append(tool_message)

    return messages[-1].content


def handle_tool_call(
    llm: OpenAI,
    pocket: PocketOpenAI,
    model: str,
    tool_specs: List[dict],
    messages: List[dict],
):
    while True:
        response = llm.chat.completions.create(
            model=model,
            messages=messages,
            tools=tool_specs,
        )
        choice = response.choices[0]
        messages.append(choice.message)
        if choice.finish_reason == "stop":
            break

        elif choice.finish_reason == "tool_calls":
            tool_calls = choice.message.tool_calls
            for tool_call in tool_calls:
                pocket_logger.debug("[TOOL CALL] ", tool_call)
                tool_message = pocket.invoke(tool_call)
                messages.append(tool_message)

    return messages[-1].content
