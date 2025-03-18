import os
import inspect
import traceback
import multiprocess
from functools import wraps
from typing import Any, Callable, Optional, Tuple, Type, Union, List
from types import MethodType
from hyperpocket.tool.function.tool import FunctionTool as PocketFunctionTool
from hyperpocket.tool.tool import ToolAuth
from llama_index.core.tools.function_tool import FunctionTool
from hyperpocket.util.flatten_json_schema import flatten_json_schema
from hyperpocket.util.function_to_model import function_to_model
from hyperpocket.tool.dock import Dock
from hyperpocket.config import pocket_logger
class LlamaIndexDock(Dock):
    @staticmethod
    def _run(
        tool_func: FunctionTool,
        envs: dict[str, str],
        llamaindex_tool_args: dict[str, Any],
        pipe: multiprocess.Pipe,
        **kwargs,
    ) -> None:
        for key, value in envs.items():
            os.environ[key] = value
            
        merged_args = kwargs.copy()
        for key in kwargs:
            if key in llamaindex_tool_args:
                merged_args[key] = llamaindex_tool_args[key]
        pocket_logger.info(f"Argument overried: {merged_args}")

        result = tool_func(**merged_args)
        _, conn = pipe
        conn.send(result)
    
    @classmethod
    def dock_list(
        cls,
        tool_func: List[FunctionTool],
        auth: Optional[dict[str, str]] = None,
        tool_vars: Optional[dict[str, str]] = None,
        llamaindex_tool_args: Optional[dict[str, str]] = None
    ) -> List[PocketFunctionTool]:
        return [
            cls.dock(
                tool, auth, tool_vars, llamaindex_tool_args
            )
            for tool in tool_func
        ]
    
    @classmethod
    def dock(
        cls,
        tool_func: FunctionTool,
        auth: Optional[dict[str, str]] = None,
        tool_vars: Optional[dict[str, str]] = None,
        llamaindex_tool_args: Optional[dict[str, str]] = None
    ) -> PocketFunctionTool:
        if isinstance(tool_func, list):
            if isinstance(tool_func[0], list):
                raise ValueError("Nested list is not supported")
            return cls.dock_list(
                tool_func, auth, tool_vars, llamaindex_tool_args
            )
            
        if inspect.ismethod(tool_func):
            original_func = tool_func.__func__
        else:
            original_func = tool_func._fn.__func__
        
        @wraps(original_func)
        async def wrapper(*args, **kwargs) -> str:
            try:
                child_env = os.environ.copy()
                pipe = multiprocess.Pipe()
                process = multiprocess.Process(
                    target=LlamaIndexDock._run,
                    args=(tool_func, child_env, llamaindex_tool_args, pipe),
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
        
        schema = function_to_model(original_func).model_json_schema()                 
        argument_json_schema = flatten_json_schema(schema)
        return PocketFunctionTool(
            func=wrapper,
            afunc=wrapper,
            name=original_func.__name__,
            description=original_func.__doc__,
            argument_json_schema=argument_json_schema,
            auth=ToolAuth(**auth) if auth else None,
            tool_vars=tool_vars,
        )
