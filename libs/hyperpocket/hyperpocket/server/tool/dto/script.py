from pydantic import BaseModel, Field

from hyperpocket.tool.wasm.script import ScriptFileNode


class Script(BaseModel):
    id: str = Field(alias='id')
    tool_id: str = Field(alias='tool_id')


class ScriptStdout(BaseModel):
    stdout: str = Field(alias='stdout')

class ScriptFileTree(BaseModel):
    tree: dict[str, ScriptFileNode] = Field(alias='tree')
