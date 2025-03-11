import asyncio
import json
from typing import List, Optional

from crewai.tools import BaseTool
from crewai.tools.base_tool import Tool

from hyperpocket import Pocket
from hyperpocket.tool import Tool as HyperpocketTool


class PocketCrewAI(Pocket):
    def init(self, thread_id="default", profile="default") -> None:
        loop = asyncio.new_event_loop()

        prepare_url = loop.run_until_complete(self.initialize_tool_auth(
            thread_id=thread_id,
            profile=profile
        ))

        for provider, url in prepare_url.items():
            print(f"[{provider}]\n\t{url}")

        loop.run_until_complete(self.wait_tool_auth(
            thread_id=thread_id,
            profile=profile
        ))

    def get_tools(self, use_profile: Optional[bool] = None) -> List[BaseTool]:
        if use_profile is not None:
            self.use_profile = use_profile

        tools = [self.get_tool(pk) for pk in self.tools.values() if not pk.name.startswith("__")]
        return tools

    def get_tool(self, pocket_tool: HyperpocketTool) -> BaseTool:
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

            result, interrupted = self.invoke_with_state(pocket_tool.name, body=body, thread_id=thread_id,
                                                         profile=profile)
            say = result
            if interrupted:
                say = f'{say}\n\nThe tool execution interrupted. Please talk to me to resume.'
            return say

        args_schema = pocket_tool.schema_model(use_profile=self.use_profile)
        description = pocket_tool.get_description(use_profile=self.use_profile)

        return Tool(
            name=pocket_tool.name,
            description=description,
            func=_invoke,
            args_schema=args_schema
        )
