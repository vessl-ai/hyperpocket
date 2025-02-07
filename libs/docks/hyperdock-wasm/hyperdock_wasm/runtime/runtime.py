import abc

from hyperpocket.tool import ToolRequest
from hyperpocket.tool.function import FunctionTool


class ToolRuntime(abc.ABC):
    @abc.abstractmethod
    def from_tool_request(self, tool_request: ToolRequest) -> FunctionTool:
        raise NotImplementedError
    
    @abc.abstractmethod
    async def teardown(self):
        raise NotImplementedError