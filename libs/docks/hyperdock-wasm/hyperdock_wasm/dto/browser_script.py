from typing import Optional

from pydantic import BaseModel, Field

from hyperdock_wasm.runtime.browser.script import ScriptFileNode


class BrowserScript(BaseModel):
    id: str = Field(alias="id")
    tool_id: str = Field(alias="tool_id")


class BrowserScriptResult(BaseModel):
    stdout: Optional[str] = Field(alias="stdout", default=None)
    stderr: Optional[str] = Field(alias="stderr", default=None)
    error: Optional[str] = Field(alias="error", default=None)


class BrowserScriptFileTree(BaseModel):
    tree: dict[str, ScriptFileNode] = Field(alias="tree")


class BrowserScriptEntrypoint(BaseModel):
    package_name: Optional[str] = Field(alias="package_name")
    entrypoint: str = Field(alias="entrypoint")


class BrowserScriptEncodedFile(BaseModel):
    encoded_file: str = Field(alias="encoded_file")


class BrowserScriptFileRequest(BaseModel):
    path: str = Field(alias="path")
