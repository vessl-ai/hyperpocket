import asyncio
import json
from typing import Any, Callable, List, Optional

from agents import FunctionTool, RunContextWrapper
from hyperpocket_openai.util import tool_to_open_ai_spec
from openai import OpenAI

try:
    from openai.types.chat import ChatCompletionMessageToolCall
except ImportError:
    raise ImportError("You need to install openai to use pocket PocketOpenAI.")

from hyperpocket import Pocket, PocketAuth
from hyperpocket.config import pocket_logger
from hyperpocket.tool import Tool, ToolLike


class PocketOpenAI(Pocket):
    client: OpenAI

    def __init__(self, client: OpenAI, tools: list[ToolLike] = None, auth: PocketAuth = None, use_profile: bool = False):
        tools.extend([self.find_tool, self.invoke_tool])
        super().__init__(tools=tools, auth=auth, use_profile=use_profile)
        self.client = client

    async def init_auth_async(self, thread_id="default", profile="default") -> None:
        prepare_url = await self.initialize_tool_auth(
            thread_id=thread_id, profile=profile
        )

        for provider, url in prepare_url.items():
            print(f"[{provider}]\n\t{url}")

        await self.wait_tool_auth(thread_id=thread_id, profile=profile)
    
    def find_tool(self, query: str) -> str:
        """
        Search the web to find a tool that can meet the user's request.
        Args:
            query (str): The role of the tool which is capable of doing the task the user wants to do.
        Returns:
            str: The name of the tool and the JSON schema of the tool arguments.
        """
        tool_lists = [
            (
                "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/get-messages",
                "Get messages from Slack",
            ),
            (
                "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/post-message",
                "Post a message to Slack",
            ),
            (
                "https://github.com/vessl-ai/hyperpocket/tree/main/tools/linear/get-issues",
                "Get issues from Linear",
            ),
            (
                "https://github.com/vessl-ai/hyperpocket/tree/main/tools/google/get-calendar-events",
                "Get calendar events from Google Calendar",
            ),
            (
                "https://github.com/vessl-ai/hyperpocket/tree/main/tools/google/get-calendar-list",
                "Get calendar list from Google Calendar",
            ),
            (
                "https://github.com/vessl-ai/hyperpocket/tree/main/tools/google/insert-calendar-events",
                "Insert calendar events to Google Calendar",
            ),
            (
                "https://github.com/vessl-ai/hyperpocket/tree/main/tools/github/list-pull-requests",
                "List pull requests from GitHub",
            ),
        ]
        system_prompt = f"""
These are the available tools you can use to help the user. Each tuple describes an url of the tool and the description of the tool:
{tool_lists}

You are a helpful assistant that can use the available tools to help the user.
Your mission is to say the URL of the tool that can meet the user's request.
You can only say the URL of the tool, not the description of the tool."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        print(response)
        choice = response.choices[0]
        tool = self.load_tools([choice.message.content])[0]
        return json.dumps({"name": tool.name, "argument_schema": tool.argument_json_schema})
    
    async def invoke_tool(self, tool_name: str, arguments: dict):
        """
        Invokes found tool.
        Args:
            tool_name (str): The name of the tool.
            arguments (dict): The arguments of the tool.
        Returns:
            str: The result of the tool.
        """
        tool = self._tool_instance(tool_name)

        if self.use_profile:
            body = arguments["body"]
            thread_id = arguments.pop("thread_id", "default")
            profile = arguments.pop("profile", "default")
        else:
            body = arguments
            thread_id = "default"
            profile = "default"

        if isinstance(body, str):
            body = json.loads(body)

        result = await super().ainvoke(
            tool_name=tool_name,
            body=body,
            thread_id=thread_id,
            profile=profile,
        )

        return result

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
        for tool in self.tools.values():
            spec = self.get_open_ai_tool_spec(tool)
            specs.append(spec)
        return specs

    def get_open_ai_tool_spec(self, tool: Tool) -> dict:
        open_ai_spec = tool_to_open_ai_spec(tool, use_profile=self.use_profile)
        return open_ai_spec

    def create_run_function(self, spec: dict) -> Callable:
        invoker = super().ainvoke

        async def run_function(ctx: RunContextWrapper[Any], args: str) -> Any:
            body = json.loads(args)
            result = await invoker(
                tool_name=spec["function"]["name"],
                body=body,
            )

            return result

        return run_function

    def get_openai_agents_tools(self) -> List[FunctionTool]:
        """wrapper for schema change"""

        def format_parameter(param: dict) -> dict:
            param["additionalProperties"] = False

            if "properties" in param:
                properties = param["properties"]
                param["required"] = list(properties.keys())
                for prop in properties.values():
                    if "default" in prop:
                        del prop["default"]
            return param

        tool_specs = self.get_open_ai_tool_specs()
        tools = []
        for spec in tool_specs:
            formatted_params = format_parameter(spec["function"]["parameters"])

            tools.append(
                FunctionTool(
                    name=spec["function"]["name"],
                    description=spec["function"]["description"],
                    params_json_schema=formatted_params,
                    on_invoke_tool=self.create_run_function(spec),
                )
            )

        return tools


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
