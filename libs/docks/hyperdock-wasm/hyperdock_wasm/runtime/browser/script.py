import base64
import enum
import pathlib
from typing import Optional

import toml
from pydantic import BaseModel

from hyperpocket.config import pocket_logger


class ScriptRuntime(enum.Enum):
    Node = "node"
    Python = "python"
    Wasm = "wasm"


_RuntimePackageFiles = {
    ScriptRuntime.Node: ["dist/index.js"],
    ScriptRuntime.Python: ["main.py", "requirements.txt"],
    ScriptRuntime.Wasm: ["dist/index.wasm"],
}


class ScriptFileNodeContent(BaseModel):
    contents: str


class ScriptFileNode(BaseModel):
    directory: Optional[dict[str, "ScriptFileNode"]] = None
    file: Optional[ScriptFileNodeContent] = None

    @classmethod
    def create_file_tree(cls, path: str, contents: str) -> dict[str, "ScriptFileNode"]:
        path_split = path.split("/")
        if len(path_split) == 1:
            return {
                path_split[0]: ScriptFileNode(
                    file=ScriptFileNodeContent(contents=contents)
                )
            }
        node = cls.create_file_tree("/".join(path_split[1:]), contents)
        return {path_split[0]: ScriptFileNode(directory=node)}

    @staticmethod
    def merge(
        a: dict[str, "ScriptFileNode"], b: [str, "ScriptFileNode"]
    ) -> dict[str, "ScriptFileNode"]:
        for k, v in b.items():
            if k in a:
                if a[k].directory and v.directory:
                    a[k].directory = ScriptFileNode.merge(a[k].directory, v.directory)
                elif a[k].file and v.file:
                    a[k].file = v.file
            else:
                a[k] = v
        return a


class Script(BaseModel):
    id: str
    tool_path: str
    rendered_html: str
    runtime: ScriptRuntime

    def load_file_tree(self) -> dict[str, ScriptFileNode]:
        relpaths = _RuntimePackageFiles[self.runtime]
        file_tree = dict()
        for p in relpaths:
            filepath = pathlib.Path(self.tool_path) / p
            with filepath.open("r") as f:
                contents = f.read().encode("utf-8")
                encoded_bytes = base64.b64encode(contents)
                encoded_str = encoded_bytes.decode()
                file_tree = ScriptFileNode.merge(
                    file_tree, ScriptFileNode.create_file_tree(p, encoded_str)
                )
        return file_tree

    @property
    def package_name(self) -> Optional[str]:
        if self.runtime != ScriptRuntime.Python:
            return
        pyproject = toml.load(pathlib.Path(self.tool_path) / "pyproject.toml")
        if "project" in pyproject:
            name = pyproject["project"]["name"]
        if "tool" in pyproject and "poetry" in pyproject["tool"]:
            name = pyproject["tool"]["poetry"]["name"]
        if not name:
            raise ValueError("Could not find package name")
        return name.replace("-", "_")

    @property
    def entrypoint(self) -> str:
        pocket_logger.info(self.tool_path)
        if self.runtime == ScriptRuntime.Node:
            return "dist/index.js"
        elif self.runtime == ScriptRuntime.Wasm:
            return "dist/main.wasm"
        pyproject = toml.load(pathlib.Path(self.tool_path) / "pyproject.toml")
        version = None
        if "project" in pyproject:
            version = pyproject["project"]["version"]
        elif "tool" in pyproject and "poetry" in pyproject["tool"]:
            version = pyproject["tool"]["poetry"]["version"]
        else:
            raise ValueError("Could not find package version")
        wheel_name = f"{self.package_name}-{version}-py3-none-any.whl"
        wheel_path = pathlib.Path(self.tool_path) / "dist" / wheel_name
        if not wheel_path.exists():
            raise ValueError(f"Wheel file {wheel_path} does not exist")
        return wheel_name

    def dist_file_path(self, file_name: str) -> str:
        return str(pathlib.Path(self.tool_path) / "dist" / file_name)


class _ScriptStore(object):
    scripts: dict[str, Script] = {}

    def __init__(self):
        self.rendered_html = {}

    def add_script(self, script: Script):
        if script.id in self.scripts:
            raise ValueError("Script id already exists")
        self.scripts[script.id] = script

    def get_script(self, script_id: str) -> Script:
        # ValueError exception is intentional
        return self.scripts[script_id]


ScriptStore = _ScriptStore()
