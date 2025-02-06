import os
import inspect
import traceback
from types import MethodType
from typing import Any, Callable, Optional, Tuple, Type, Union, List

import multiprocess
from llama_index.core.tools.tool_spec.base import BaseToolSpec
from llama_index.core.tools.function_tool import FunctionTool

class LlamaIndexToolRequest(object):
    tool_func: FunctionTool
    tool_args: dict[str, Any]
    tool_spec_args: dict[str, Any]
    env_dict_extends: dict[str, str]
    auth: Optional[dict[str, Any]]
    tool_vars: dict[str, str]

    def __init__(
        self,
        tool_func: FunctionTool,
        tool_args: Optional[dict[str, Any]] = None,
        tool_spec_args: Optional[dict[str, Any]] = None,
        env_dict_extends: Optional[dict[str, str]] = None,
        auth: Optional[dict[str, Any]] = None,
        tool_vars: Optional[dict[str, str]] = None,
    ):
        self.tool_func = tool_func
        self.tool_args = {}
        if tool_args is not None:
            self.tool_args = tool_args
        self.tool_spec_args = {}
        if tool_spec_args is not None:
            self.tool_spec_args = tool_spec_args
        self.env_dict_extends = {}
        if env_dict_extends is not None:
            self.env_dict_extends = env_dict_extends
        self.auth = auth
        self.tool_vars = {}
        if tool_vars is not None:
            self.tool_vars = tool_vars


ToolType = FunctionTool | LlamaIndexToolRequest

def _run(
    tool_func: FunctionTool,
    tool_spec: Type[BaseToolSpec],
    envs: dict[str, str],
    tool_args: dict[str, Any],
    pipe: multiprocess.Pipe,
    **kwargs,
) -> None:
    # must be called in a child process
    for key, value in envs.items():
        os.environ[key] = value
    result = tool_func(tool_spec(), **tool_args)
    _, conn = pipe
    conn.send(result)


def connect(
    tool_type: ToolType,
) -> Callable[[...], str]:
    tool_req = tool_type
    tool_spec = inspect._findclass(tool_req.tool_func._fn)
    if isinstance(tool_type, type):
        tool_req = LlamaIndexToolRequest(tool_type)

    def wrapper(**kwargs) -> str:
        try:
            child_env = os.environ.copy()
            pipe = multiprocess.Pipe()
            process = multiprocess.Process(
                target=_run,
                args=(tool_req.tool_func, tool_spec, child_env, tool_req.tool_args, tool_req.tool_spec_args, pipe),
                kwargs=kwargs,
            )
            process.start()
            conn, _ = pipe
            while True:
                if conn.poll():
                    result = conn.recv()
                    break
            process.terminate()
            process.join()
            return result
        except Exception as e:
            return "\n".join(traceback.format_exception(e))
    wrapper = tool_req.tool_func._fn.__func__    
    wrapper.__auth__ = tool_req.auth
    wrapper.__vars__ = tool_req.tool_vars

    return MethodType(wrapper, tool_spec())
