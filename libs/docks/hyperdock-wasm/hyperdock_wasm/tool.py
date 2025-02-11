from hyperpocket.tool import ToolRequest

from hyperdock_wasm.tool_reference import WasmToolReference


class WasmToolRequest(ToolRequest):
    tool_ref: WasmToolReference
    rel_path: str
    overridden_tool_vars: dict[str, str]
    
    def __init__(self, tool_ref: WasmToolReference, rel_path: str, tool_vars: dict[str, str] = None):
        self.tool_ref = tool_ref
        self.rel_path = rel_path
        self.overridden_tool_vars = tool_vars if tool_vars is not None else dict()
        
    def __str__(self):
        return f"ToolRequest(lock={self.tool_ref}, rel_path={self.rel_path})"
