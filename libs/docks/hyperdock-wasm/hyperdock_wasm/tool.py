from typing import Optional

from hyperpocket.tool import ToolRequest
from hyperpocket.tool.function import FunctionTool

from hyperdock_wasm.lock import WasmLock, GitWasmLock, LocalWasmLock
from hyperdock_wasm.runtime import browser as browser_runtime


class WasmToolRequest(ToolRequest):
    lock: WasmLock
    rel_path: str
    overridden_tool_vars: dict[str, str]
    
    def __init__(self, lock: WasmLock, rel_path: str, tool_vars: dict[str, str] = None):
        self.lock = lock
        self.rel_path = rel_path
        self.overridden_tool_vars = tool_vars if tool_vars is not None else dict()
        
    def __str__(self):
        return f"ToolRequest(lock={self.lock}, rel_path={self.rel_path})"

def from_git(
    repository: str, ref: str, rel_path: str, tool_vars: Optional[dict[str, str]] = None
) -> WasmToolRequest:
    if not tool_vars:
        tool_vars = dict()
    return WasmToolRequest(
        GitWasmLock(repository_url=repository, git_ref=ref), rel_path, tool_vars)

def from_local(
    path: str, rel_path: str, tool_vars: Optional[dict[str, str]] = None
) -> WasmToolRequest:
    if not tool_vars:
        tool_vars = dict()
    return WasmToolRequest(
        LocalWasmLock(path), rel_path, tool_vars)

def from_tool_request(tool_request: ToolRequest) -> FunctionTool:
    if not isinstance(tool_request, WasmToolRequest):
        raise ValueError(f"Expected a WasmToolRequest, got {tool_request}")
    return browser_runtime.from_wasm_tool_request(tool_request)
