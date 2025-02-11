from typing import Callable, Union

from hyperpocket.tool import Tool, ToolRequest
from hyperpocket.tool.dock import Dock

ToolLike = Union[Tool, str, Callable, ToolRequest, Dock]
