from typing import Callable, Union

from hyperpocket.tool import Tool, ToolRequest

ToolLike = Union[Tool, str, Callable, ToolRequest]
