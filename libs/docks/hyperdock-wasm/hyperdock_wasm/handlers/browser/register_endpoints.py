from fastapi.responses import HTMLResponse, FileResponse
from fastapi.routing import APIRouter
from hyperdock_wasm.handlers.browser import handlers


def register_hyperdock_wasm_endpoints(app):
    hyperdock_router = APIRouter()

    # Register hyperdock endpoints
    hyperdock_router.add_api_route(
        "/scripts/{script_id}/browse", handlers.browse_script_page,
        methods=["GET"],
        response_class=HTMLResponse,
    )
    hyperdock_router.add_api_route(
        "/scripts/{script_id}/done", handlers.done_script_page, methods=["POST"]
    )
    hyperdock_router.add_api_route(
        "/scripts/{script_id}/file_tree", handlers.get_file_tree, methods=["GET"]
    )
    hyperdock_router.add_api_route(
        "/scripts/{script_id}/entrypoint", handlers.get_entrypoint, methods=["GET"]
    )
    hyperdock_router.add_api_route(
        "/scripts/{script_id}/file/{file_name}", handlers.get_dist_file, methods=["GET"], response_class=FileResponse
    )

    app.include_router(hyperdock_router)
