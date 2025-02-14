from fastapi.responses import FileResponse, HTMLResponse

import hyperdock_wasm.dto as scriptdto
from hyperdock_wasm.runtime.browser.script import ScriptStore
from hyperpocket.futures import FutureStore


async def browse_script_page(script_id: str):
    html = ScriptStore.get_script(script_id).rendered_html
    return HTMLResponse(content=html)

async def done_script_page(
        script_id: str, req: scriptdto.BrowserScriptResult
) -> scriptdto.BrowserScriptResult:
    FutureStore.resolve_future(
        script_id, {"stdout": req.stdout, "stderr": req.stderr, "error": req.error}
    )
    return req

async def get_file_tree(script_id: str) -> scriptdto.BrowserScriptFileTree:
    script = ScriptStore.get_script(script_id)
    return scriptdto.BrowserScriptFileTree(tree=script.load_file_tree())

async def get_entrypoint(script_id: str) -> scriptdto.BrowserScriptEntrypoint:
    script = ScriptStore.get_script(script_id)
    package_name = script.package_name
    entrypoint = f"/scripts/{script_id}/file/{script.entrypoint}"
    return scriptdto.BrowserScriptEntrypoint(package_name=package_name, entrypoint=entrypoint)

async def get_dist_file(script_id: str, file_name: str):
    script = ScriptStore.get_script(script_id)
    return FileResponse(script.dist_file_path(file_name))
