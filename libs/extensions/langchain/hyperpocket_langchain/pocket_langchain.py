import json
from typing import List, Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool, StructuredTool

from hyperpocket import Pocket, PocketAuth
from hyperpocket.tool import Tool, ToolLike


class PocketLangchain(Pocket):
    def __init__(self, llm, tools: list[ToolLike] = None, auth: PocketAuth = None, use_profile: bool = False):
        if tools is None:
            tools = []
        tools.extend([self.find_tool, self.invoke_tool])
        super().__init__(tools=tools, auth=auth, use_profile=use_profile)
        self.llm = llm

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
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "{query}"),
        ])
        chain = prompt_template | self.llm
        response = chain.invoke({"query": query})
        tool_url = response.content
        tool = self.load_or_get_tool(tool_url)
        return json.dumps({"name": tool.name, "argument_schema": tool.argument_json_schema})
    
    async def invoke_tool(self, tool_name_to_invoke: str, arguments_str: str):
        """
        Invokes found tool.
        Args:
            tool_name_to_invoke (str): The name of the tool to invoke.
            arguments_str (str): The arguments of the tool to pass. This is JSON-encoded string.
        Returns:
            str: The result of the tool.
        """
        arguments = json.loads(arguments_str)

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
        

        result, interrupted = await self.ainvoke_with_state(
            tool_name=tool_name_to_invoke,
            body=body,
            thread_id=thread_id,
            profile=profile,
        )
        say = result
        if interrupted:
            say = f"{say}\n\nThe tool execution interrupted. Please talk to me to resume."
        return say

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
