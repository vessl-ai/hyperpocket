import json
import pathlib
from typing import Optional

from hyperpocket.tool import ToolRequest

from hyperdock_container.tool_reference import ContainerToolReference


class ContainerToolRequest(ToolRequest):
    tool_ref: ContainerToolReference
    rel_path: str
    overridden_tool_vars: dict[str, str]
    runtime_arguments: dict
    _base_image: Optional[str]

    def __init__(
            self,
            tool_ref: ContainerToolReference,
            rel_path: str,
            tool_vars: dict[str, str] = None,
            runtime_arguments: dict = None):
        self.tool_ref = tool_ref
        self.rel_path = rel_path
        self.overridden_tool_vars = tool_vars if tool_vars is not None else dict()
        self.runtime_arguments = runtime_arguments if runtime_arguments is not None else dict()
        self._base_image = None

    def __str__(self):
        return f"ToolRequest(lock={self.tool_ref}, rel_path={self.rel_path})"
    
    @property
    def base_image(self) -> str:
        if self._base_image is not None:
            return self._base_image
        toolpkg_path = self.tool_ref.toolpkg_path()
        rel_path = self.rel_path
        rootpath = pathlib.Path(toolpkg_path) / rel_path
        pocket_tool_config_path = rootpath / "pocket.json"
        with pocket_tool_config_path.open("r") as f:
            pocket_tool_config = json.load(f)
            if (base_image := pocket_tool_config.get("baseImage")) is not None:
                self._base_image = base_image
                return base_image
            if (language := pocket_tool_config.get("language")) is not None:
                if lang := language.lower():
                    if lang == "python":
                        self._base_image = "python:3.11-slim"
                        return "python:3.11-slim"
                    if lang == "node":
                        self._base_image = "node"
                        return "node"
            raise ValueError("failed to determine base image")
