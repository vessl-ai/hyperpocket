import json
from typing import Optional

from hyperpocket import Pocket
from hyperpocket.tool import Tool as HyperpocketTool
from pydantic_ai.tools import Tool as PydanticAITool

from hyperpocket_pydanticai.utils import (
    create_signature,
    generate_annotations,
    generate_docstring,
)


class PocketPydanticAI(Pocket):
    def get_tool(self, pocket_tool: HyperpocketTool) -> PydanticAITool:
        def _invoke(**kwargs):
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

        json_schema = pocket_tool.argument_json_schema
        description = pocket_tool.get_description(use_profile=self.use_profile)

        # Generate docstring, annotations, and signature so that pydantic-ai perceives the tool as a proper python function
        docstring = generate_docstring(description, json_schema)
        _invoke.__doc__ = docstring
        annotations = generate_annotations(json_schema)
        _invoke.__annotations__ = annotations
        signature = create_signature(json_schema)
        _invoke.__signature__ = signature

        tool = PydanticAITool(
            function=_invoke,
            takes_ctx=False,
            name=pocket_tool.name,
            description=description,
        )
        return tool

    def get_tools(self, use_profile: Optional[bool] = False) -> list[PydanticAITool]:
        if use_profile is not None:
            self.use_profile = use_profile

        tools = [self.get_tool(pk) for pk in self.core.tools.values()]
        return tools
