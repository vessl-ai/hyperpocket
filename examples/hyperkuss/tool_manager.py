import logging
from typing import Dict, List, Optional
from hyperpocket.tool.function import FunctionTool

logger = logging.getLogger(__name__)

class ToolManager:
    def __init__(self):
        self.tools: Dict[str, FunctionTool] = {}
        self.tool_specs = None

    def register_tool(self, tool: FunctionTool) -> None:
        """Register a new tool"""
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")

    def register_tools(self, tools: List[FunctionTool]) -> None:
        """Register multiple tools at once"""
        for tool in tools:
            self.register_tool(tool)

    def get_all_tools(self) -> List[FunctionTool]:
        """Get all registered tools"""
        return list(self.tools.values())

    def get_tool(self, name: str) -> Optional[FunctionTool]:
        """Get a specific tool by name"""
        return self.tools.get(name)

    def remove_tool(self, name: str) -> bool:
        """Remove a tool by name"""
        if name in self.tools:
            del self.tools[name]
            logger.info(f"Removed tool: {name}")
            return True
        return False

    def update_tool_specs(self, pocket) -> None:
        """Update tool specifications using Hyperpocket"""
        self.tool_specs = pocket.get_open_ai_tool_specs() 