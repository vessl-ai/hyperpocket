from fastapi import APIRouter
from fastapi.responses import FileResponse, HTMLResponse

from hyperpocket.futures import FutureStore
from hyperpocket.server.tool.dto import script as scriptdto
from hyperpocket.tool.wasm.script import ScriptStore

wasm_tool_router = APIRouter(prefix="/wasm")


@wasm_tool_router.get("/scripts/{script_id}/browse", response_class=HTMLResponse)
async def browse_script_page(script_id: str):
    html = ScriptStore.get_script(script_id).rendered_html
    return HTMLResponse(content=html)


@wasm_tool_router.post("/scripts/{script_id}/done")
async def done_script_page(
    script_id: str, req: scriptdto.ScriptResult
) -> scriptdto.ScriptResult:
    FutureStore.resolve_future(
        script_id, {"stdout": req.stdout, "stderr": req.stderr, "error": req.error}
    )
    return req


@wasm_tool_router.get("/scripts/{script_id}/file_tree")
async def get_file_tree(script_id: str) -> scriptdto.ScriptFileTree:
    script = ScriptStore.get_script(script_id)
    return scriptdto.ScriptFileTree(tree=script.load_file_tree())


@wasm_tool_router.get("/scripts/{script_id}/entrypoint")
async def get_entrypoint(script_id: str) -> scriptdto.ScriptEntrypoint:
    script = ScriptStore.get_script(script_id)
    package_name = script.package_name
    entrypoint = f"/tools/wasm/scripts/{script_id}/file/{script.entrypoint}"
    return scriptdto.ScriptEntrypoint(package_name=package_name, entrypoint=entrypoint)


@wasm_tool_router.get(
    "/scripts/{script_id}/file/{file_name}", response_class=FileResponse
)
async def get_dist_file(script_id: str, file_name: str):
    script = ScriptStore.get_script(script_id)
    return FileResponse(script.dist_file_path(file_name))
