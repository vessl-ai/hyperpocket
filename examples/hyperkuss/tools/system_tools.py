from typing import Dict, List
from hyperpocket.tool import function_tool
from .. import tools
import inspect

@function_tool()
def list_tools() -> Dict:
    """
    List all available tools and their descriptions.
    Returns:
        Dictionary containing tool categories and their tools
    """
    try:
        tool_info = {}
        
        # Get info from tool categories
        for category_id, category in tools.TOOL_CATEGORIES.items():
            tool_list = []
            for tool in category["tools"]:
                # Get the original function from the FunctionTool
                original_func = tool.func if hasattr(tool, 'func') else tool
                
                tool_list.append({
                    "name": original_func.__name__,
                    "description": original_func.__doc__.strip() if original_func.__doc__ else "No description available",
                    "category": category["name"],
                    "parameters": inspect.signature(original_func).parameters if inspect.signature(original_func).parameters else {}
                })
            
            tool_info[category_id] = {
                "name": category["name"],
                "description": category["description"],
                "tools": tool_list
            }
        
        return {
            "categories": tool_info,
            "message": "Successfully retrieved tool information"
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": f"Failed to list tools: {str(e)}"
        } 