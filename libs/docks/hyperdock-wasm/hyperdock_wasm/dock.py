import asyncio
import pathlib
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from hyperdock_wasm.runtime import ToolRuntime
from hyperdock_wasm.runtime.browser.runtime import BrowserScriptRuntime
from hyperdock_wasm.tool import WasmToolRequest
from hyperdock_wasm.tool_reference import WasmGitToolReference, WasmLocalToolReference, WasmToolReference
from hyperpocket.tool.dock import Dock
from hyperpocket.tool.function import FunctionTool


class WasmDock(Dock):
    unique_tool_references: dict[tuple[str, ...], WasmToolReference]
    runtime: ToolRuntime

    def __init__(self, *args, dock_vars: dict[str, str] = None, **kwargs):
        super().__init__(dock_vars=dock_vars)
        self.unique_tool_references = dict()
        self.runtime = BrowserScriptRuntime()
        for req_like in args:
            self.plug(req_like)

    def __del__(self):
        try:
            loop = asyncio.get_running_loop()
            loop.run_until_complete(self.teardown())
        except RuntimeError:
            asyncio.run(self.teardown())

    def try_parse(self, req_like: str) -> WasmToolRequest:
        if pathlib.Path(req_like).expanduser().exists():
            tool_ref = WasmLocalToolReference(tool_path=req_like)
            return WasmToolRequest(tool_ref=tool_ref, rel_path="", tool_vars=self._dock_vars)
        elif req_like.startswith("https://github.com"):
            base_repo_url, git_ref, rel_path = WasmGitToolReference.parse_repo_url(req_like)
            tool_ref = WasmGitToolReference(repository_url=base_repo_url, git_ref=git_ref)
            return WasmToolRequest(tool_ref=tool_ref, rel_path=rel_path, tool_vars=self._dock_vars)
        raise ValueError(f"Could not parse as a WasmToolRequest: {req_like}")

    def plug(self, req_like: Any, **kwargs):
        if isinstance(req_like, str):
            req = self.try_parse(req_like)
            self.unique_tool_references[req.tool_ref.key()] = req.tool_ref
            self._tool_requests.append(req)
        elif isinstance(req_like, WasmToolRequest):
            if not hasattr(req_like, "overridden_tool_vars"):
                req_like.overridden_tool_vars = dict()
            req_like.overridden_tool_vars = self._dock_vars | req_like.overridden_tool_vars
            self.unique_tool_references[req_like.tool_ref.key()] = req_like.tool_ref
            self._tool_requests.append(req_like)
        else:
            raise ValueError(f"Could not parse as a WasmToolRequest: {req_like}")

    def _sync_ref(self, k, **kwargs):
        tool_ref = self.unique_tool_references[k]
        tool_ref.sync(**kwargs)

    def tools(self) -> list[FunctionTool]:
        with ThreadPoolExecutor(
                max_workers=min(len(self.unique_tool_references) + 1, 100), thread_name_prefix="repository_loader"
        ) as executor:
            executor.map(lambda k: self._sync_ref(k), self.unique_tool_references.keys())

        for tool_req in self._tool_requests:
            tool_req.tool_ref = self.unique_tool_references[tool_req.tool_ref.key()]

        return [self.runtime.from_tool_request(req) for req in self._tool_requests]

    async def teardown(self):
        await self.runtime.teardown()
