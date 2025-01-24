from typing import Optional

from pydantic import BaseModel, Field

from hyperpocket.tool.wasm.script import ScriptFileNode


class Script(BaseModel):
    id: str = Field(alias="id")
    tool_id: str = Field(alias="tool_id")


class ScriptResult(BaseModel):
    stdout: Optional[str] = Field(alias="stdout", default=None)
    stderr: Optional[str] = Field(alias="stderr", default=None)
    error: Optional[str] = Field(alias="error", default=None)


class ScriptFileTree(BaseModel):
    tree: dict[str, ScriptFileNode] = Field(alias="tree")


class ScriptEntrypoint(BaseModel):
    package_name: Optional[str] = Field(alias="package_name")
    entrypoint: str = Field(alias="entrypoint")


class ScriptEncodedFile(BaseModel):
    encoded_file: str = Field(alias="encoded_file")


class ScriptFileRequest(BaseModel):
    path: str = Field(alias="path")
