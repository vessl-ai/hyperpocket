import copy
import functools
from typing import Optional, Dict

from llama_index.core.tools import FunctionTool

from hyperdock_llamaindex import converter
from hyperdock_llamaindex.converter import CONVERTER_TYPE
from hyperpocket.runtime import Runtime, LocalRuntime
from hyperpocket.runtime.container.container_runtime import ContainerRuntime
from hyperpocket.tool import ToolAuth
from hyperpocket.tool.function import FunctionTool as PocketFunctionTool


class DockLlamaindex:
    env_converters: dict[str, CONVERTER_TYPE] = {
        "SLACK_BOT_TOKEN": converter.slack_bot_token,
        "GOOGLE_TOKEN": converter.google_application_credentials
    }
    extended_env_converters: dict[str, CONVERTER_TYPE] = {}
    runtime: Runtime = LocalRuntime()

    def __init__(self, runtime: Runtime = None, extended_env_converters: dict[str, CONVERTER_TYPE] = None):
        if runtime:
            self.runtime = runtime
        if extended_env_converters:
            self.extended_env_converters = extended_env_converters

    def dock(self, tool: FunctionTool, auth: Optional[ToolAuth] = None, tool_vars: dict = None) -> PocketFunctionTool:
        if tool_vars is None:
            tool_vars = {}

        if isinstance(self.runtime, LocalRuntime):
            func = functools.partial(self.wrapped, tool.fn)
            afunc = functools.partial(self.async_wrapped, tool.async_fn)
        elif isinstance(self.runtime, ContainerRuntime):
            # @moon just a pseudocode
            func = functools.partial(
                self.wrapped,
                "hyperdock-llamaindex-container-image:latest",
                tool.metadata.name,
            )

            afunc = functools.partial(
                self.async_wrapped,
                "hyperdock-llamaindex-container-image:latest",
                tool.metadata.name,
            )

        return PocketFunctionTool(
            func=func,
            afunc=afunc,
            name=tool.metadata.name,
            description=tool.metadata.description,
            argument_json_schema=tool.metadata.fn_schema.model_json_schema(),
            auth=auth,
            default_tool_vars=tool_vars
        )

    def wrapped(self, run_arg, **tool_args):
        modified_env = self.modify_environment(tool_args)
        return self.runtime.run(run_arg, tool_args, modified_env)

    async def async_wrapped(self, run_arg, **tool_args):
        modified_env = self.modify_environment(tool_args)
        return self.runtime.run(run_arg, tool_args, modified_env)

    def modify_environment(self, kwargs: dict) -> Dict[str, str]:
        _kwargs = copy.deepcopy(kwargs)
        modified = {}
        for key, value in _kwargs.items():
            # first off, check extended converter
            if key in self.extended_env_converters:
                env_converter = self.extended_env_converters[key]
                modified_key, modified_value = env_converter(key, value)
                modified[modified_key] = modified_value

                # converted environment is deleted from kwargs. because it will be injected to os env.
                del kwargs[key]

            # and then, check default converter
            elif key in self.env_converters:
                env_converter = self.env_converters[key]
                modified_key, modified_value = env_converter(key, value)
                modified[modified_key] = modified_value

                # converted environment is deleted from kwargs. because it will be injected to os env.
                del kwargs[key]

        return modified
