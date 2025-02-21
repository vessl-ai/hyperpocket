import inspect
from typing import Callable, List, Optional

from hyperpocket.auth import AuthProvider
from hyperpocket.tool.function.tool import FunctionTool
from hyperpocket.tool.tool import ToolAuth


def function_tool(
    func: Optional[Callable] = None,
    *,
    auth_provider: AuthProvider = None,
    scopes: List[str] = None,
    auth_handler: str = None,
    tool_vars: dict[str, str] = None,
):
    def decorator(inner_func: Callable):
        if not callable(inner_func):
            raise ValueError("FunctionTool can only be created from a callable")
        auth = None
        if auth_provider is not None:
            auth = ToolAuth(
                auth_provider=auth_provider,
                scopes=scopes if scopes else [],
                auth_handler=auth_handler,
            )

        if inspect.iscoroutinefunction(inner_func):
            return FunctionTool.from_func(func=inner_func, afunc=inner_func, auth=auth, tool_vars=tool_vars)

        return FunctionTool.from_func(func=inner_func, auth=auth, tool_vars=tool_vars)

    if func is not None:
        return decorator(func)

    # return FunctionTool
    return decorator
