import base64
import enum
import pathlib
from typing import Optional

from pydantic import BaseModel


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
    directory: Optional[dict[str, 'ScriptFileNode']] = None
    file: Optional[ScriptFileNodeContent] = None
    
    @classmethod
    def create_file_tree(cls, path: str, contents: str) -> dict[str, 'ScriptFileNode']:
        path_split = path.split("/")
        if len(path_split) == 1:
            return {path_split[0]: ScriptFileNode(file=ScriptFileNodeContent(contents=contents))}
        node = cls.create_file_tree('/'.join(path_split[1:]), contents)
        return {path_split[0]: ScriptFileNode(directory=node)}
    
    @staticmethod
    def merge(a: dict[str, 'ScriptFileNode'], b: [str, 'ScriptFileNode']) -> dict[str, 'ScriptFileNode']:
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
                contents = f.read().encode('utf-8')
                encoded_bytes = base64.b64encode(contents)
                encoded_str = encoded_bytes.decode()
                file_tree = ScriptFileNode.merge(file_tree, ScriptFileNode.create_file_tree(p, encoded_str))
        return file_tree
                

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
