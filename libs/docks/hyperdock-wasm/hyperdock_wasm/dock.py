import pathlib

from fastapi.responses import HTMLResponse, FileResponse
from hyperpocket.repository import Lock
from hyperpocket.tool.dock import Dock
from hyperpocket.tool.function import FunctionTool

from hyperdock_wasm.handlers import browse_script_page, done_script_page, get_file_tree, get_entrypoint, get_dist_file
from hyperdock_wasm.lock.git import GitWasmLock
from hyperdock_wasm.lock.local import LocalWasmLock
from hyperdock_wasm.runtime.browser.invoker_browser import InvokerBrowser
from hyperdock_wasm.tool import WasmToolRequest
from hyperdock_wasm.tool import from_tool_request

IDENTIFIER="wasm"

class WasmDock(Dock):
    def __init__(self, *args, dock_vars: dict[str, str] = None, **kwargs):
        super().__init__(identifier=IDENTIFIER, dock_vars=dock_vars)
        for req_like in args:
            self.plug(req_like)
        self._register_callbacks()
    
    def _register_callbacks(self):
        self._dock_http_router.get("/scripts/{script_id}/browse", response_class=HTMLResponse)(browse_script_page)
        self._dock_http_router.post("/scripts/{script_id}/done")(done_script_page)
        self._dock_http_router.get("/scripts/{script_id}/file_tree")(get_file_tree)
        self._dock_http_router.get("/scripts/{script_id}/entrypoint")(get_entrypoint)
        self._dock_http_router.get("/scripts/{script_id}/file/{file_name}", response_class=FileResponse)(get_dist_file)
    
    @staticmethod
    def try_parse(req_like: str) -> WasmToolRequest:
        if pathlib.Path(req_like).exists():
            lock = LocalWasmLock(tool_path=req_like)
            return WasmToolRequest(lock=lock, rel_path="", tool_vars=dict())
        elif req_like.startswith("https://github.com"):
            base_repo_url, git_ref, rel_path = GitWasmLock.parse_repo_url(req_like)
            lock = GitWasmLock(repository_url=base_repo_url, git_ref=git_ref)
            return WasmToolRequest(lock=lock, rel_path=rel_path, tool_vars=dict())
        raise ValueError(f"Could not parse as a WasmToolRequest: {req_like}")
    
    def deserialize_lock(self, lock_key: str, serialized_lock: dict) -> Lock:
        if lock_key.startswith("git#"):
            return GitWasmLock(**serialized_lock)
        elif lock_key.startswith("local#"):
            return LocalWasmLock(**serialized_lock)
        raise ValueError(f"Unknown lock source: {lock_key}")
    
    def plug(self, req_like: str | WasmToolRequest, **kwargs):
        if isinstance(req_like, str):
            req = WasmDock.try_parse(req_like)
            self._locks[req.lock.key()] = req.lock
            self._tool_requests.append(req)
        elif isinstance(req_like, WasmToolRequest):
            self._locks[req_like.lock.key()] = req_like.lock
            self._tool_requests.append(req_like)
        else:
            raise ValueError(f"Could not parse as a WasmToolRequest: {req_like}")
    
    def tools(self) -> list[FunctionTool]:
        return [self.runtime.from_tool_request(req) for req in self._tool_requests]

    async def teardown(self):
        await self.runtime.teardown()