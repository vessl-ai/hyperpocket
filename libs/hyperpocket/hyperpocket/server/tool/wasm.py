from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from hyperpocket.futures import FutureStore
from hyperpocket.server.tool.dto import script as scriptdto
from hyperpocket.tool.wasm.script import ScriptStore

wasm_tool_router = APIRouter(
    prefix="/wasm"
)


@wasm_tool_router.get("/scripts/{script_id}/browse", response_class=HTMLResponse)
async def browse_script_page(script_id: str):
    html = ScriptStore.get_script(script_id).rendered_html
    return HTMLResponse(content=html)


@wasm_tool_router.post("/scripts/{script_id}/done")
async def done_script_page(script_id: str, req: scriptdto.ScriptStdout) -> scriptdto.ScriptStdout:
    FutureStore.resolve_future(script_id, req.stdout)
    return scriptdto.ScriptStdout(stdout=req.stdout)

@wasm_tool_router.post("/scripts/{script_id}/fail")
async def fail_script_page(script_id: str, req: scriptdto.ScriptStdout) -> scriptdto.ScriptStdout:
    pass

@wasm_tool_router.get("/scripts/{script_id}/file_tree")
async def get_file_tree(script_id: str) -> scriptdto.ScriptFileTree:
    script = ScriptStore.get_script(script_id)
    return scriptdto.ScriptFileTree(tree=script.load_file_tree())
