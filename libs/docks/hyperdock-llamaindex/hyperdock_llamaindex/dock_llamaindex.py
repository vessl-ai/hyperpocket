import copy
import functools
from typing import Optional, Dict

from llama_index.core.tools import FunctionTool

from hyperdock_llamaindex import converter
from hyperdock_llamaindex.converter import CONVERTER_TYPE
from hyperpocket.runtime import Runtime, LocalRuntime
from hyperpocket.tool import ToolAuth
from hyperpocket.tool.function import FunctionTool as PocketFunctionTool


class DockLlamaindex:
    env_map: dict[str, CONVERTER_TYPE] = {
        "SLACK_BOT_TOKEN": converter.slack_bot_token,
        "GOOGLE_TOKEN": converter.google_application_credentials
    }
    runtime: Runtime = LocalRuntime()

    @classmethod
    def to_pocket_function_tool(cls, tool: FunctionTool, auth: Optional[ToolAuth] = None,
                                tool_vars: dict = None) -> PocketFunctionTool:
        if tool_vars is None:
            tool_vars = {}

        return PocketFunctionTool(
            func=functools.partial(cls.wrapped, tool.fn),
            afunc=functools.partial(cls.async_wrapped, tool.async_fn),
            name=tool.metadata.name,
            description=tool.metadata.description,
            argument_json_schema=tool.metadata.fn_schema.model_json_schema(),
            auth=auth,
            default_tool_vars=tool_vars
        )

    @classmethod
    def wrapped(cls, func, **kwargs):
        modified_env = cls.modify_environment(kwargs)
        return cls.runtime.run(func, kwargs, modified_env)

    @classmethod
    async def async_wrapped(cls, func, **kwargs):
        modified_env = cls.modify_environment(kwargs)
        return cls.runtime.run(func, kwargs, modified_env)

    @classmethod
    def modify_environment(
            cls,
            kwargs: dict,
            env_dict_extends: Optional[dict[str, CONVERTER_TYPE]] = None,
    ) -> Dict[str, str]:
        if env_dict_extends is None:
            env_dict_extends = {}

        _kwargs = copy.deepcopy(kwargs)
        modified = {}
        for key, value in _kwargs.items():
            # first off, check extended converter
            if key in env_dict_extends:
                env_converter = env_dict_extends[key]
                modified_key, modified_value = env_converter(key, value)
                modified[modified_key] = modified_value

                # converted environment is deleted from kwargs. because it will be injected to os env.
                del kwargs[key]

            # and then, check default converter
            elif key in cls.env_map:
                env_converter = cls.env_map[key]
                modified_key, modified_value = env_converter(key, value)
                modified[modified_key] = modified_value

                # converted environment is deleted from kwargs. because it will be injected to os env.
                del kwargs[key]

        return modified
