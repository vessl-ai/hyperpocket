import pathlib
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Optional

from hyperpocket.tool.dock import Dock
from hyperpocket.tool.function import FunctionTool

from hyperdock_container.runtime import ContainerRuntime
from hyperdock_container.tool import ContainerToolRequest
from hyperdock_container.tool_reference import ContainerLocalToolReference, ContainerGitToolReference, \
    ContainerToolReference


class ContainerDock(Dock):
    unique_tool_references: dict[tuple[str, ...], ContainerToolReference]
    _tool_requests: list[ContainerToolRequest]
    runtime: ContainerRuntime

    def __init__(self, *args, dock_vars: dict[str, str] = None, **kwargs):
        super().__init__(dock_vars=dock_vars)
        self.unique_tool_references = dict()
        self.runtime = ContainerRuntime.get_runtime_from_settings()
        self._tool_requests = []

    def try_parse(self, req_like: str, inline_tool_vars: Optional[dict] = None) -> ContainerToolRequest:
        if inline_tool_vars is None:
            inline_tool_vars = dict()
        if pathlib.Path(req_like).expanduser().exists():
            tool_ref = ContainerLocalToolReference(tool_path=req_like)
            return ContainerToolRequest(tool_ref=tool_ref, rel_path="", tool_vars=self._dock_vars | inline_tool_vars)
        elif req_like.startswith("https://github.com"):
            base_repo_url, git_ref, rel_path = ContainerGitToolReference.parse_repo_url(req_like)
            tool_ref = ContainerGitToolReference(repository_url=base_repo_url, git_ref=git_ref)
            return ContainerToolRequest(tool_ref=tool_ref, rel_path=rel_path, tool_vars=self._dock_vars | inline_tool_vars)
        raise ValueError(f"Could not parse as a ContainerToolRequest: {req_like}")

    def plug(self, req_like: Any, **kwargs):
        if isinstance(req_like, str):
            req = self.try_parse(req_like)
            req.overridden_tool_vars = self._dock_vars
            self.unique_tool_references[req.tool_ref.key()] = req.tool_ref
            self._tool_requests.append(req)
        elif isinstance(req_like, tuple):
            req, vars = req_like
            if not isinstance(req, str) or not isinstance(vars, dict):
                raise ValueError(f"Could not parse as a ContainerToolRequest: {req_like}")
            req = self.try_parse(req, inline_tool_vars=vars)
            self.unique_tool_references[req.tool_ref.key()] = req.tool_ref
            self._tool_requests.append(req)
        elif isinstance(req_like, ContainerToolRequest):
            if not hasattr(req_like, "overridden_tool_vars"):
                req_like.overridden_tool_vars = dict()
            req_like.overridden_tool_vars = self._dock_vars | req_like.overridden_tool_vars
            self.unique_tool_references[req_like.tool_ref.key()] = req_like.tool_ref
        else:
            raise ValueError(f"Could not parse as a ContainerToolRequest: {req_like}")

    async def teardown(self):
        pass

    def tools(self) -> list[FunctionTool]:
        with ThreadPoolExecutor(
                max_workers=min(len(self.unique_tool_references) + 1, 100), thread_name_prefix="repository_loader"
        ) as executor:
            executor.map(lambda k: k.sync(), self.unique_tool_references.values())
        
        for tool_req in self._tool_requests:
            tool_req.tool_ref = self.unique_tool_references[tool_req.tool_ref.key()]
            
        base_images = set([tool_req.base_image for tool_req in self._tool_requests])
        with ThreadPoolExecutor(
                max_workers=min(len(base_images) + 1, 100), thread_name_prefix="base_image_loader"
        ) as executor:
            executor.map(lambda base_image: self.runtime.pull(base_image), base_images)

        with ThreadPoolExecutor(
                max_workers=min(len(self._tool_requests) + 1, 100), thread_name_prefix="tool_loader"
        ) as executor:
            tool_collections = executor.map(lambda tool_req: self.runtime.from_tool_request(tool_req),
                                            self._tool_requests)

        return [tool for tool_collection in tool_collections for tool in tool_collection]
