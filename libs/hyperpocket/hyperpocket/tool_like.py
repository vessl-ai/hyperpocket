from typing import Callable, Union

from hyperpocket.tool import Tool

ToolLike = Union[Tool, str, tuple, Callable]
