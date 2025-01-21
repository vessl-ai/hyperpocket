from typing import Union, Callable

from hyperpocket.tool import ToolRequest, Tool

ToolLike = Union[Tool, str, Callable, ToolRequest]