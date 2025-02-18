from typing import Callable, Union

from hyperpocket.tool import Tool, ToolRequest
from hyperpocket.tool.dock import Dock

ToolLike = Union[Tool, str, tuple, Callable, ToolRequest, Dock]
