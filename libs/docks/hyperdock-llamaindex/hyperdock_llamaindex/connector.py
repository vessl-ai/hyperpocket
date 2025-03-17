import os
import inspect
import traceback
import multiprocess
from typing import Any, Callable, Optional, Tuple, Type, Union, List
from types import MethodType
from llama_index.core.tools.function_tool import FunctionTool
from llama_index.core.tools.tool_spec.base import BaseToolSpec
from hyperpocket.tool_like import ToolLike
from hyperpocket.tool.dock import Dock

def _run(
    tool_func: FunctionTool,
    tool_spec: Type[BaseToolSpec],
    envs: dict[str, str],
    llamaindex_tool_args: dict[str, Any],
    pipe: multiprocess.Pipe,
    **kwargs,
) -> None:
    for key, value in envs.items():
        os.environ[key] = value
    result = tool_func(tool_spec(), **llamaindex_tool_args)
    _, conn = pipe
    conn.send(result)

def llamaindex_dock(
    tool_func: List[FunctionTool],
    auth: Optional[dict[str, str]] = None,
    tool_vars: Optional[dict[str, str]] = None,
    llamaindex_tool_args: Optional[dict[str, str]] = None
) -> list[ToolLike]:
    result = []
    for tool in tool_func:
        tool_spec = inspect._findclass(tool._fn)
        
        def wrapper(**kwargs) -> str:
            try:
                child_env = os.environ.copy()
                pipe = multiprocess.Pipe()
                process = multiprocess.Process(
                    target=_run,
                    args=(tool_func, tool_spec, child_env, llamaindex_tool_args, pipe),
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
        
        wrapper = tool._fn.__func__
        wrapper.__auth__ = auth
        wrapper.__vars__ = tool_vars
        wrapper.__name__ = tool._metadata.name
        
        result.append(MethodType(wrapper, tool_spec()))
    return result
